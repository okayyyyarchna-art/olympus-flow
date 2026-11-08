#!/usr/bin/env python3
"""Four-cell offline proof with strict JUnit reconciliation.

usage: proof.py <base-repo> <pkg-dir> --base-ids ids.json --new-ids ids.json
       [--base-skips ids.json] [--stability] [--final] [--rebuild] [--build-only]
       [--work-root DIR] [--timeout SECONDS] [--build-timeout SECONDS]
Expected-ID files are nonempty canonical-ID JSON arrays. Baseline skips must be
predeclared; new-mode skips always fail. All cells use the literal H4 environment.
Image reuse includes Dockerfile, committed context, resolved FROM digests and platform.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import string
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I drops the script folder
from machine import load

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from certify import id_set, inspect_junit

MACHINE = load()
DOCKRUN = [MACHINE["python"], str(Path(__file__).resolve().parent / "lib/dockrun.py")]
ENV = dict(os.environ)
if MACHINE["os"] == "windows":
    ENV["MSYS_NO_PATHCONV"] = "1"
MARK = "=====PROOF-JUNIT====="
MINIMAL_PATH = "/usr/local/bin:/usr/bin:/bin"
SLOT_WAIT = 3600
ok = True


def say(good, message):
    global ok
    ok = ok and good
    print(f"{'PASS' if good else 'FAIL'}  {message}", flush=True)


def docker(*args, timeout=600):
    # The limit covers the command itself: dockrun applies it once a Docker slot is free.
    return subprocess.run(DOCKRUN + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace",
                          env={**ENV, "DOCKRUN_TIMEOUT": str(timeout)}, timeout=timeout + SLOT_WAIT)


def cleanup_build_cache():
    if MACHINE["docker"]["cleanup_allowed"] is True:
        docker("builder", "prune", "-af")


def read_ids(path, allow_empty=False):
    values = json.loads(Path(path).read_text(encoding="utf-8"))
    id_set(values, "IDs", allow_empty=allow_empty)
    return values


def repository_id(reference):
    repository = reference.split("@")[0]
    if ":" in repository.rsplit("/", 1)[-1]:
        repository = repository.rsplit(":", 1)[0]
    parts = repository.split("/")
    if len(parts) == 1 or ("." not in parts[0] and ":" not in parts[0] and parts[0] != "localhost"):
        parts.insert(0, "docker.io")
    if parts[0] == "index.docker.io":
        parts[0] = "docker.io"
    if parts[0] == "docker.io" and len(parts) == 2:
        parts.insert(1, "library")
    return "/".join(parts)


def resolve_dockerfile(data, platform):
    """Resolve mutable FROM references and build the exact resolved bytes."""
    variables = {"TARGETPLATFORM": platform, "BUILDPLATFORM": MACHINE["docker"]["native_platform"]}
    stages = set()
    bases = []
    lines = []
    for line in data.decode("utf-8").splitlines():
        match = re.match(r"\s*ARG\s+(\w+)=(.*)$", line, re.I)
        if match:
            variables[match[1]] = string.Template(match[2]).safe_substitute(variables)
        match = re.match(r"(\s*FROM\s+)(.*)$", line, re.I)
        if match:
            parts = shlex.split(match[2])
            stage_platform = platform
            options = []
            while parts and parts[0].startswith("--"):
                option = string.Template(parts.pop(0)).safe_substitute(variables)
                if not option.startswith("--platform="):
                    raise ValueError(f"unsupported FROM option: {option}")
                stage_platform = option.split("=", 1)[1]
                if "$" in stage_platform:
                    raise ValueError("unresolved FROM platform")
                options.append(option)
            if not parts:
                raise ValueError("empty FROM")
            ref = string.Template(parts[0]).safe_substitute(variables)
            if "$" in ref:
                raise ValueError(f"unresolved FROM: {ref}")
            if ref.lower() not in stages and ref.lower() != "scratch":
                pulled = docker("pull", "--platform", stage_platform, ref)
                if pulled.returncode:
                    raise ValueError("base image resolution failed: " + pulled.stderr)
                inspected = docker("image", "inspect", "--format", "{{json .RepoDigests}}", ref)
                if inspected.returncode:
                    raise ValueError("base image inspect failed: " + inspected.stderr)
                digests = json.loads(inspected.stdout)
                matches = [d for d in digests or [] if repository_id(d) == repository_id(ref)]
                if not matches or not re.search(r"@sha256:[0-9a-f]{64}$", matches[0]):
                    raise ValueError(f"no resolved repository digest for {ref}")
                ref = matches[0]
                bases.append({"reference": parts[0], "digest": ref, "platform": stage_platform})
            if len(parts) > 1:
                if len(parts) != 3 or parts[1].lower() != "as":
                    raise ValueError("unsupported FROM syntax")
                stages.add(parts[2].lower())
            parts[0] = ref
            line = match[1] + " ".join(options + parts)
        lines.append(line)
    if not any(re.match(r"\s*FROM\s", line, re.I) for line in lines):
        raise ValueError("Dockerfile has no FROM")
    return ("\n".join(lines) + "\n").encode(), bases


def image_key(dockerfile, head, tree, bases, platform):
    identity = {"dockerfile_sha256": hashlib.sha256(dockerfile).hexdigest(),
                "base_commit": head, "context_tree": tree, "resolved_bases": bases, "platform": platform}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return key, identity


def run(image, patches, out, mode, solution, as_user=12345, platform=None,
        *, expected_ids, allowed_skips=(), timeout=600):
    out.mkdir(parents=True, exist_ok=True)
    prepared = out / "source"
    prepared.mkdir()
    platform = platform or MACHINE["docker"]["native_platform"]
    # Populate from the built image before exposing the patched tree read-only.
    apply = (f"if [ -f /etc/passwd ] && cut -d: -f3 /etc/passwd | grep -qx '{as_user}'; "
             "then echo 'probe uid is present in passwd' >&2; exit 1; fi; "
             "cp -a /app/. /prepared/ && cd /prepared && "
             "git -c safe.directory=/prepared apply --whitespace=nowarn /patches/test.patch")
    if solution:
        apply += " && git -c safe.directory=/prepared apply --whitespace=nowarn /patches/solution.patch"
    apply += " && chmod -R a+rX /prepared"
    prep = docker("run", "--rm", "--platform", platform, "--network", "none",
                  "--user", "0:0", "--entrypoint", "/bin/bash",
                  "-v", f"{patches}:/patches:ro", "-v", f"{prepared}:/prepared:rw",
                  image, "-c", apply, timeout=timeout)
    (out / f"{mode}-prepare.log").write_text(prep.stdout + prep.stderr, encoding="utf-8")
    if prep.returncode:
        raise ValueError(f"patch preparation exit {prep.returncode}: {out}")
    command = (f"/app/test.sh --output_path /out/{mode}.xml {mode}; status=$?; "
               f"printf '\\n{MARK}\\n'; cat /out/{mode}.xml; exit \"$status\"")
    t0 = time.monotonic()
    proc = docker("run", "--rm", "--platform", platform, "--network", "none",
                  "--user", f"{as_user}:{as_user}", "--workdir", "/",
                  # /tmp stays the container's own writable /tmp: the image keeps its warm build cache there, as
                  # on the platform. A tmpfs over it hid that cache, and a cold vet build filled the size-capped,
                  # noexec tmpfs (vet task 2: "fork/exec ... permission denied", "no space left on device").
                  "--tmpfs", "/out:rw,mode=1777",
                  "-v", f"{prepared}:/app:ro", "--entrypoint", "/usr/bin/env", image,
                  "-i", f"PATH={MINIMAL_PATH}", "/bin/bash", "-c", command, timeout=timeout)
    log, marker, xml = proc.stdout.partition("\n" + MARK + "\n")
    (out / f"{mode}.log").write_text(log + proc.stderr, encoding="utf-8")
    (out / f"{mode}.xml").write_text(xml, encoding="utf-8")
    (out / f"{mode}-exit.json").write_text(json.dumps({"exit_code": proc.returncode}), encoding="utf-8")
    if not marker:
        raise ValueError(f"missing JUnit marker (exit {proc.returncode}): {out}")
    expect = "fail" if mode == "new" and not solution else "pass"
    evidence = inspect_junit(xml.encode(), expected_ids, expect, proc.returncode,
                             allowed_skips if mode == "base" else ())
    return evidence["results"], time.monotonic() - t0


def main():
    global ok
    ok = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("pkg", type=Path)
    parser.add_argument("--base-ids", required=True, type=Path)
    parser.add_argument("--new-ids", required=True, type=Path)
    parser.add_argument("--base-skips", type=Path)
    for option in ("stability", "final", "rebuild", "build-only"):
        parser.add_argument("--" + option, action="store_true")
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--build-timeout", type=int, default=3600)
    args = parser.parse_args()
    if not 0 < args.timeout < 688:
        parser.error("timeout must be positive and below the 688-second platform watchdog")
    image = "(unresolved)"
    work = None
    try:
        ids = {mode: read_ids(path) for mode, path in (("base", args.base_ids), ("new", args.new_ids))}
        skips = read_ids(args.base_skips, allow_empty=True) if args.base_skips else []
        if not set(skips) <= set(ids["base"]):
            raise ValueError("base skip allowlist contains unexpected IDs")
        repo, pkg = args.repo.resolve(), args.pkg.resolve()
        platform = MACHINE["docker"]["final_platform" if args.final or args.stability else "native_platform"]
        def git(*argv):
            return subprocess.run(["git", "-C", str(repo), *argv], capture_output=True,
                                  text=True, check=True).stdout.strip()
        head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
        data = (pkg / "Dockerfile").read_bytes()
        resolved, bases = resolve_dockerfile(data, platform)
        key, identity = image_key(data, head, tree, bases, platform)
        image = f"olympus-proof:{key}"
        root = (args.work_root or Path(MACHINE["paths"]["work_root"])).resolve() / "proof-work"
        root.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix="proof-", dir=root))
        (work / "identity.json").write_text(json.dumps(identity, indent=2), encoding="utf-8")
        if args.rebuild or docker("image", "inspect", image).returncode:
            ctx = work / "context"
            subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", str(repo), str(ctx)], check=True)
            subprocess.run(["git", "-C", str(ctx), "checkout", "-q", "--detach", head], check=True)
            dockerfile = work / "Dockerfile.resolved"
            dockerfile.write_bytes(resolved)
            built = docker("build", "--platform", platform, "-f", str(dockerfile), "-t", image, str(ctx),
                           timeout=args.build_timeout)
            if built.returncode:
                raise ValueError("image build failed: " + built.stdout + built.stderr)
            cleanup_build_cache()
        say(True, f"image builds/reuses complete environment identity {key}")
        patches = work / "patches"
        patches.mkdir()
        for name in ("test.patch", "solution.patch"):
            shutil.copy(pkg / name, patches / name)

        def cell(label, mode, solution):
            results, elapsed = run(image, patches, work / label, mode, solution, platform=platform,
                                   expected_ids=ids[mode], allowed_skips=skips, timeout=args.timeout)
            say(True, f"{label}: exit/report/IDs reconcile {results}")
            return results, elapsed

        cell("base-base", "base", False)
        if args.build_only:
            return 0
        _, elapsed = cell("new-base", "new", False)
        say(elapsed < 300, f"new/base duration {elapsed:.1f}s (<300s)")
        previous = None
        for i in range(2):
            result = (cell(f"base-reference-{i}", "base", True)[0],
                      cell(f"new-reference-{i}", "new", True)[0])
            if previous is not None:
                say(result == previous, "reference per-ID vectors repeat")
            previous = result
        # All preceding cells already use H4; retain a separately named unknown-uid probe.
        cell("unknown-uid", "new", True)
        if args.stability:
            for label, solution in (("base", False), ("reference", True)):
                def repeat(i):
                    return cell(f"stability-{label}-{i}", "new", solution)[0]
                if MACHINE["parallel"]["stability_parallel"]:
                    with ThreadPoolExecutor(max_workers=MACHINE["docker"]["slots"]) as pool:
                        vectors = list(pool.map(repeat, range(6)))
                else:
                    vectors = [repeat(i) for i in range(6)]
                say(all(v == vectors[0] for v in vectors), f"six {label} per-ID vectors repeat")
    except Exception as exc:
        say(False, f"proof crashed: {type(exc).__name__}: {exc}")
    finally:
        print(f"image: {image}\nartifacts: {work}\nPROOF {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
