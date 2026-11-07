#!/usr/bin/env python3
"""S4 in one command: every Docker proof the platform's verify checks run, through our Docker slot lock.

usage: python proof.py <base-repo> <pkg-dir> [--stability] [--final] [--rebuild] [--build-only] [--work-root DIR]
  --build-only: the Dockerfile gate (build or reuse the image, run base mode once), before the user's platform build.
  The image is built once per Dockerfile + base commit and reused after that (--rebuild forces a build).
  base-repo: pristine checkout at the pinned commit (with .git). pkg-dir: Dockerfile, test.patch, solution.patch.
Checks (each a recorded platform failure when missing):
  1. image builds from the checked-out repo (verifyBuild)
  2. without solution: base passes, every new test fails; clean `new` run under 300 s (verifyTests, 688 s kill on T11)
  3. with solution, twice: base + new pass with identical counts (verifySolution)
  4. with solution as a uid with no passwd entry and an empty environment (`env -i`): new passes
     (offlineUidPassed; turso T6: test.sh must set its own env)
  5. --stability (once before the first paste): 6 runs without and 6 with the solution, identical results per test id
     (verifyFlakiness method)
Prints PASS/FAIL per check and one final line. Exit 1 on any FAIL.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from machine import load

try:
    MACHINE = load()
except ValueError as exc:
    sys.exit(f"machine: {exc}")
DOCKRUN = [MACHINE["python"], str(Path(__file__).resolve().parent / "lib" / "dockrun.py")]
ENV = dict(os.environ)
if MACHINE["os"] == "windows":
    ENV["MSYS_NO_PATHCONV"] = "1"
ok = True
MARK = "=====PROOF-JUNIT====="


def say(good, msg):
    global ok
    ok = ok and good
    print(f"{'PASS' if good else 'FAIL'}  {msg}", flush=True)


def docker(*args):
    return subprocess.run(DOCKRUN + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)


def junit(path):
    if not path.exists() or path.stat().st_size == 0:
        return None
    cases = {}
    for c in ET.parse(path).getroot().iter("testcase"):
        key = f"{c.get('classname')}::{c.get('name')}"
        cases[key] = "fail" if (c.find("failure") is not None or c.find("error") is not None) else \
            "skip" if c.find("skipped") is not None else "pass"
    return cases


def run(image, patches, out, mode, solution, as_user=None, platform=None):
    """Apply patches as root (as the platform does), then run test.sh as root or as a uid with an empty env."""
    out.mkdir(parents=True, exist_ok=True)
    apply = "mkdir -p /out && cd /app && git apply --whitespace=nowarn /patches/test.patch"
    if solution:
        apply += " && git apply --whitespace=nowarn /patches/solution.patch"
    cmd = f"./test.sh --output_path /out/{mode}.xml {mode}"
    if as_user:
        apply += f" && chown -R {as_user}:{as_user} /out"
        cmd = (f"setpriv --reuid={as_user} --regid={as_user} --clear-groups "
               f"env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=/tmp bash -c 'cd /app && {cmd}'")
    t0 = time.time()
    # /out stays inside the container and the JUnit comes back on stdout after a marker: files that Docker writes
    # through a bind mount can carry an ACL without this user (vet 2026-11-06, twice: %TEMP% and then ~/OSS after a
    # Docker restart), and the proof then crashed with PermissionError before any check ran
    p = docker("run", "--rm", "--platform", platform or MACHINE["docker"]["native_platform"], "--network", "none", "-v", f"{patches}:/patches:ro",
               image, "bash", "-c", f"{{ {apply}; }} >/tmp/apply.log 2>&1 && {cmd}; echo '{MARK}'; cat /out/{mode}.xml 2>/dev/null")
    text, _, xml = p.stdout.partition(MARK + chr(10))
    (out / f"{mode}.log").write_text(text + p.stderr, encoding="utf-8", errors="replace")
    (out / f"{mode}.xml").write_text(xml, encoding="utf-8")
    return junit(out / f"{mode}.xml"), time.time() - t0


def counts(cases):
    vals = list(cases.values())
    return {k: vals.count(k) for k in ("pass", "fail", "skip")}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo")
    ap.add_argument("pkg")
    ap.add_argument("--stability", action="store_true")
    ap.add_argument("--final", action="store_true", help="run all cells on the final platform")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--work-root", help="scratch root for this invocation")
    args = ap.parse_args()
    stability = args.stability
    repo, pkg = Path(args.repo).resolve(), Path(args.pkg).resolve()
    platform = MACHINE["docker"]["final_platform" if stability or args.final else "native_platform"]
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    # Build once per task (user rule 2026-11-06): the image depends only on the Dockerfile and the base commit, so it
    # is tagged by both and reused until one of them changes. Patches are applied in each container, never baked in.
    # A fresh clone's .git defeats Docker's layer cache (COPY . .), so rebuilding "with cache" was a full ~10 min
    # build on every call. --rebuild forces a build.
    key = hashlib.sha256((pkg / "Dockerfile").read_bytes() + head.encode()).hexdigest()[:12]
    image = f"olympus-proof-{pkg.parent.name.lower()}:{key}"
    if platform != "linux/amd64":
        image += "-" + platform.split("/")[-1]
    # Not %TEMP%: its ACL grants only SYSTEM, Administrators and the file owner, and the JUnit files that Docker's
    # backend writes there became unreadable to this user after a Docker restart (vet 2026-11-06). ~/OSS grants the
    # user full control explicitly.
    work_root = Path(args.work_root or MACHINE["paths"]["work_root"]).resolve()
    proof_root = work_root / "proof-work"
    proof_root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="proof-", dir=proof_root))
    try:
        if not args.rebuild and docker("image", "inspect", image).returncode == 0:
            say(True, f"1 image builds (reused {image}: same Dockerfile and base commit)")
        else:
            # a clone gives a real .git with history (test.sh restores base tests from it) and works when base/ is a
            # git worktree; it holds exactly the committed HEAD, like the platform's checkout. One stable clone per
            # task (user 2026-11-06, local speed only): a fresh clone each time changed .git, so COPY . . and every
            # later layer were rebuilt; the Dockerfile stays outside the context for the same reason.
            ctx = work_root / "proof-ctx" / pkg.parent.name
            cur = subprocess.run(["git", "-C", str(ctx), "rev-parse", "HEAD"], capture_output=True, text=True)
            if cur.returncode != 0 or cur.stdout.strip() != head:
                shutil.rmtree(ctx, ignore_errors=True)
                ctx.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "clone", "-q", "--no-checkout", str(repo), str(ctx)], check=True)
                subprocess.run(["git", "-C", str(ctx), "checkout", "-q", head], check=True)
            shutil.copy(pkg / "Dockerfile", work / "Dockerfile.olympus")
            b = docker("build", "--platform", platform, "-f", str(work / "Dockerfile.olympus"), "-t", image, str(ctx))
            say(b.returncode == 0, "1 image builds" + ("" if b.returncode == 0 else ": " + (b.stdout + b.stderr)[-800:]))
            # the image is built once and reused, so its build cache is never needed again; it filled C: on vet
            # (37.75 GB, docker_data.vhdx 72.7 GB, engine down) - drop it after every build (user 2026-11-06)
            docker("builder", "prune", "-af")
            if b.returncode:
                return
        patches = work / "patches"
        patches.mkdir()
        for f in ("test.patch", "solution.patch"):
            shutil.copy(pkg / f, patches / f)

        base, _ = run(image, patches, work / "nosol", "base", False, platform=platform)
        say(bool(base) and counts(base)["fail"] == 0, f"2a without solution: base passes ({counts(base) if base else 'no JUnit'})")
        if args.build_only:
            # Dockerfile gate (user rule 2026-11-06): the image builds and base mode runs offline in it; the user then
            # builds the same Dockerfile on the platform before any other stage
            return
        new, secs = run(image, patches, work / "nosol", "new", False, platform=platform)
        say(bool(new) and counts(new)["pass"] == 0 and counts(new)["fail"] > 0,
            f"2b without solution: every new test fails ({counts(new) if new else 'no JUnit'})")
        say(secs < 300, f"2c clean new run {secs:.0f} s (< 300 s)")

        seen = None
        for i in (1, 2):
            sb, _ = run(image, patches, work / f"sol{i}", "base", True, platform=platform)
            sn, _ = run(image, patches, work / f"sol{i}", "new", True, platform=platform)
            good = bool(sb) and bool(sn) and counts(sb)["fail"] == 0 and counts(sn)["fail"] == 0
            say(good, f"3 with solution run {i}: base {counts(sb) if sb else '-'}, new {counts(sn) if sn else '-'}")
            now = (sb, sn)
            if seen is not None:
                say(now == seen, "3 identical results between the two solution runs")
            seen = now

        un, _ = run(image, patches, work / "uid", "new", True, as_user=12345, platform=platform)
        say(bool(un) and counts(un)["fail"] == 0, f"4 as uid 12345 with env -i: new {counts(un) if un else 'no JUnit'}")

        if stability:
            for label, sol in (("unsolved", False), ("solved", True)):
                first = None
                def cell(i):
                    return run(image, patches, work / f"stab-{label}-{i}", "new", sol, platform=platform)[0]
                results = map(cell, range(6))
                if MACHINE["parallel"]["stability_parallel"]:
                    with ThreadPoolExecutor(max_workers=MACHINE["docker"]["slots"]) as pool:
                        results = list(pool.map(cell, range(6)))
                for i, r in enumerate(results):
                    if first is None:
                        first = r
                    elif r != first:
                        say(False, f"5 {label} run {i + 1} differs from run 1 (flaky test ids)")
                        break
                else:
                    say(True, f"5 {label}: 6 runs identical")
    except Exception as e:  # noqa: BLE001  any crash is a FAIL, never a silent pass
        say(False, f"proof crashed: {type(e).__name__}: {e}")
    finally:
        # the image stays for the next proof of this task; task cleanup deletes it (memory: cleanup-keep-learning)
        print(f"\nimage: {image}")
        print(f"artifacts: {work}")
        print("PROOF PASS" if ok else "PROOF FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
