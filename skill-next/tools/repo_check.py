#!/usr/bin/env python3
"""Qualify a generated adapter offline. Every Docker call uses the shared lock.

repo_check.py TASK [--timeout SECONDS]
Evidence lives in TASK/check. Does not mutate TASK/base or run Docker cleanup.
"""
import argparse
import contextlib
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from xml.etree import ElementTree as ET

from machine import load
from repo_init import git, save

MARK = "=====REPO-CHECK-XML====="
STEPS = ("native-discovery", "build-and-offline-base", "single-id-and-relative-spaced-output",
         "listed-ids-match-junit", "production-error-named-diagnostics", "test-skip-restored",
         "production-not-restored", "uid-env-cwd-readonly-offline", "test-build-after-restore",
         "zero-selection", "watchdog-timeout", "absent-report", "empty-report", "malformed-report",
         "converter-failure", "collection-failure")


def choose_production(profile, source, one):
    language = profile["language"]
    suffixes = {"go": (".go",), "python": (".py", ".pyx"), "typescript": (".ts", ".tsx", ".js", ".jsx")}
    candidates = [name for name in profile["production"] if name.endswith(suffixes[language])]
    explicit = profile.get("production_probe")
    if explicit:
        if explicit not in candidates:
            raise ValueError("production_probe must name an inventoried production source")
        return explicit
    if language == "python":
        modules = [name.split('.')[0] for name in profile["setup_imports"]]
        node = profile["native_ids"][one].split("::")[0]
        modules += re.findall(r"^(?:from|import)\s+([\w.]+)", (source / node).read_text(), re.M)
        for module in modules:
            stem = module.replace('.', '/')
            paths = [stem + '/__init__.py', stem + '.py', stem + '.pyx', 'src/' + stem + '/__init__.py', 'src/' + stem + '.py']
            match = next((name for name in paths if name in candidates), None)
            if match:
                return match
        raise ValueError("cannot ground a Python import probe; set production_probe explicitly")
    selectors = [name.removeprefix('./') for name in profile["selectors"]["base"]]
    if language == "typescript":
        twins = {re.sub(r"\.(test|spec)(\.[jt]sx?)$", r"\2", name) for name in selectors}
        match = next((name for name in candidates if name in twins), None)
    else:
        match = next((name for name in candidates if any(name.startswith(s.rstrip('/') + '/') for s in selectors)), None)
    if not match:
        raise ValueError("no covered production file found; set production_probe explicitly")
    return match


def patch_runner(task):
    body = (task / "init/test.sh").read_text(encoding="utf-8")
    existing = git(task / "base", "ls-tree", "HEAD", "--", "test.sh")
    if existing:
        original = subprocess.check_output(["git", "-C", str(task / "base"), "show", "HEAD:test.sh"]).decode("utf-8")
        mode = existing.split()[0]
        patch = "diff --git a/test.sh b/test.sh\n"
        if mode != "100755":
            patch += f"old mode {mode}\nnew mode 100755\n"
        lines = difflib.unified_diff(original.splitlines(keepends=True), body.splitlines(keepends=True),
                                    fromfile="a/test.sh", tofile="b/test.sh")
        patch += "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines)
    else:
        patch = ("diff --git a/test.sh b/test.sh\nnew file mode 100755\n--- /dev/null\n+++ b/test.sh\n"
                 + f"@@ -0,0 +1,{len(body.splitlines())} @@\n"
                 + "".join("+" + line + "\n" for line in body.splitlines()))
    (task / "init/test.patch").write_text(patch, encoding="utf-8", newline="\n")
    (task / "init/solution.patch").write_text("", encoding="utf-8")


class Check:
    def __init__(self, task, timeout):
        self.task = task
        self.profile = json.loads((task / "profile.json").read_text(encoding="utf-8"))
        self.machine = load()
        self.timeout = timeout
        self.out = task / "check"
        self.out.mkdir(exist_ok=True)
        self.results = []
        self.checked_runner_sha = None
        self.image = None
        self.env = dict(os.environ, DOCKRUN_SLOTS="1", PYTHONDONTWRITEBYTECODE="1")
        if self.machine["os"] == "windows":
            self.env["MSYS_NO_PATHCONV"] = "1"
        self.lock = Path(__file__).resolve().parent / "lib/dockrun.py"
        self.counter = 0

    def record(self, name, good, detail):
        row = {"step": name, "result": "PASS" if good else "FAIL", "detail": detail}
        self.results.append(row)
        print(f"{row['result']} {name}: {detail}", flush=True)
        (self.out / "results.json").write_text(json.dumps(self.results, indent=2) + "\n", encoding="utf-8")

    def docker(self, *args, timeout=None):
        if args[0] == "run":
            args = ("run", "--memory", str(self.machine["docker"]["memory_gb"]) + "g", *args[1:])
        argv = [self.machine["python"], str(self.lock), *args]
        duration = timeout or (3600 if args[0] == "build" else self.timeout)
        if args[0] == "build":
            log = self.out / "docker-build.log"
            with log.open("w", encoding="utf-8") as stream:
                proc = self.supervise(argv, duration, stdout=stream, stderr=subprocess.STDOUT)
            return subprocess.CompletedProcess(argv, proc.returncode, log.read_text(encoding="utf-8", errors="replace"), "")
        return self.supervise(argv, duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, encoding="utf-8", errors="replace")

    def supervise(self, argv, duration, **kwargs):
        extra = {"start_new_session": True} if os.name != "nt" else {}
        proc = subprocess.Popen(argv, env=self.env, **kwargs, **extra)
        try:
            stdout, stderr = proc.communicate(timeout=duration)
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
            else:
                import signal
                os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate()
            raise RuntimeError(f"Docker watchdog expired after {duration}s; tracked process tree stopped")
        return subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)

    def source(self, label):
        path = Path(tempfile.mkdtemp(prefix=f"source-{label}-", dir=self.out)) / "repo"
        subprocess.run(["git", "clone", "-q", "--no-local", str(self.task / "base"), str(path)], check=True)
        shutil.copyfile(self.task / "init/test.sh", path / "test.sh")
        (path / "test.sh").chmod(0o755)
        return path

    def invoke(self, source, label, extra=(), discover=False, relative=False):
        output = "relative report.xml" if relative else "/out/report with spaces.xml"
        listing = "--list" in extra
        args = ["/app/test.sh", "base", *(list(extra)), *( ["--discover"] if discover else ([] if listing else ["--output_path", output]))]
        import shlex
        cmd = " ".join(shlex.quote(a) for a in args)
        if relative:
            # Invoke from /; the root filesystem is writable for the probe uid via /out.
            cmd = "cd /out && " + cmd
        cmd = ("if cut -d: -f3 /etc/passwd | grep -qx 12345; then exit 97; fi; " + cmd +
               "; status=$?; printf '\\n" + MARK + "\\n'; " +
               (":" if discover or listing else "cat " + shlex.quote("/out/" + output if relative else output)) +
               "; exit \"$status\"")
        t0 = time.monotonic()
        proc = self.docker("run", "--rm", "--platform", self.profile["environment"]["platform"],
                           "--network", "none", "--user", "12345:12345", "--workdir", "/",
                           "--tmpfs", "/tmp:rw,mode=1777", "--tmpfs", "/out:rw,mode=1777",
                           "-v", f"{source}:/app:ro", "--entrypoint", "/usr/bin/env", self.image,
                           "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "/bin/bash", "-c", cmd)
        log, marker, xml = proc.stdout.partition("\n" + MARK + "\n")
        (self.out / f"{label}.log").write_text(log + proc.stderr, encoding="utf-8")
        (self.out / f"{label}.xml").write_text(xml, encoding="utf-8")
        (self.out / f"{label}.json").write_text(json.dumps({"exit": proc.returncode,
              "seconds": time.monotonic() - t0, "marker": bool(marker),
              "runner_sha256": hashlib.sha256((source / 'test.sh').read_bytes()).hexdigest()}, indent=2), encoding="utf-8")
        return proc.returncode, xml, log + proc.stderr

    def vectors(self, xml, expected):
        root = ET.fromstring(xml)
        values = {}
        for case in root.iter("testcase"):
            key = (case.get("classname") + "::" if case.get("classname") else "") + case.get("name", "")
            if key in values:
                raise ValueError("duplicate ID: " + key)
            values[key] = next((tag for tag in ("error", "failure", "skipped") if case.find(tag) is not None), "pass")
        if set(values) != set(expected) or not values:
            raise ValueError("JUnit IDs differ from expected inventory")
        return values

    def build(self):
        import proof
        if re.search(r"\{\{|NOT_VERIFIED", (self.task / "init/Dockerfile").read_text()):
            raise ValueError("Dockerfile has unresolved build inputs; resolve profile.open first")
        provisional = self.profile["expected"]["base"]
        if not provisional:
            raise ValueError("no provisional IDs: configure expected.base or qualify an unsupported adapter first")
        old_cleanup, old_run, old_docker = proof.cleanup_build_cache, proof.run, proof.docker
        old_args = sys.argv
        old_env = os.environ.get("DOCKRUN_SLOTS")
        os.environ["DOCKRUN_SLOTS"] = "1"
        # proof --build-only also executes base/base. Qualify IDs after its build,
        # before that execution. Disable its otherwise automatic builder prune.
        proof.cleanup_build_cache = lambda: None
        proof.docker = self.docker

        def qualify(image, patches, out, mode, solution, **kwargs):
            self.image = image
            source = self.source("discovery")
            code, _, log = self.invoke(source, "discovery", discover=True)
            marker = "=====ADAPTER-IDS=====\n"
            if code or marker not in log:
                raise ValueError("native ID discovery failed; see check/discovery.log")
            ids = json.loads(log.split(marker, 1)[1].splitlines()[0])
            if not ids:
                raise ValueError("zero IDs discovered")
            self.profile["expected"]["base"] = sorted(ids)
            self.profile["native_ids"] = ids
            self.profile["ids_qualified"] = True
            self.profile["open"] = [row for row in self.profile["open"] if row["field"] not in ("go_build_constraints",)]
            save(self.task, self.profile)
            patch_runner(self.task)
            shutil.copyfile(self.task / "init/test.patch", patches / "test.patch")
            kwargs["expected_ids"] = sorted(ids)
            self.record("native-discovery", True, f"{len(ids)} named IDs; discovery.log")
            return old_run(image, patches, out, mode, solution, **kwargs)

        proof.run = qualify
        patch_runner(self.task)
        # proof validates both files before build-only. New-feature inventory is
        # deliberately OPEN: this invocation executes only the base mode.
        bootstrap_ids = self.out / "build-only-unused-new-ids.json"
        bootstrap_ids.write_text(json.dumps(provisional), encoding="utf-8")
        skips = self.out / "base-skips.json"
        skips.write_text(json.dumps(list(self.profile["skip_allowlist"])), encoding="utf-8")
        sys.argv = [str(Path(proof.__file__)), str(self.task / "base"), str(self.task / "init"),
                    "--base-ids", str(self.task / "init/base-ids.json"),
                    "--new-ids", str(bootstrap_ids), "--build-only", "--final",
                    "--base-skips", str(skips),
                    "--work-root", str(self.out), "--timeout", str(self.timeout)]
        captured = io.StringIO()
        try:
            with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
                code = proof.main()
        finally:
            sys.argv = old_args
            proof.cleanup_build_cache, proof.run, proof.docker = old_cleanup, old_run, old_docker
            if old_env is None:
                os.environ.pop("DOCKRUN_SLOTS", None)
            else:
                os.environ["DOCKRUN_SLOTS"] = old_env
            (self.out / "build-proof.log").write_text(captured.getvalue(), encoding="utf-8")
            print(captured.getvalue(), end="", flush=True)
        self.record("build-and-offline-base", code == 0, "proof.py --build-only, cleanup disabled; build-proof.log")
        if self.image:
            (self.out / "image.txt").write_text(self.image + "\n", encoding="utf-8")
            image_id = self.docker("image", "inspect", "--format", "{{.Id}}", self.image)
            self.profile["identity"]["image_id"] = image_id.stdout.strip() if image_id.returncode == 0 else "NOT VERIFIED"
            identities = sorted((self.out / "proof-work").glob("proof-*/identity.json"), key=lambda p: p.stat().st_mtime)
            if identities:
                self.profile["identity"]["environment_identity"] = json.loads(identities[-1].read_text())
            save(self.task, self.profile)
        return code == 0

    def probes(self):
        expected = self.profile["expected"]["base"]
        one = next((key for key in expected if "::Test" in key), expected[0])
        source = self.source("probes")
        self.checked_runner_sha = hashlib.sha256((source / "test.sh").read_bytes()).hexdigest()
        code, xml, _ = self.invoke(source, "single-id", ["--one", one], relative=True)
        vector = self.vectors(xml, [one])
        self.record("single-id-and-relative-spaced-output", code == 0 and vector[one] == "pass", one)
        code, _, log = self.invoke(source, "listed", ["--list"], discover=False)
        # --list has no XML, intentionally; only the JSON inventory is authoritative.
        listed = json.loads(next(line for line in log.splitlines() if line.startswith("[")))
        self.record("listed-ids-match-junit", code == 0 and listed == expected,
                    f"{len(listed)} qualified IDs; build-only base/base reconciles those exact IDs")

        language = self.profile["language"]
        production = choose_production(self.profile, source, one)
        target = source / production
        original = target.read_bytes()
        token = "REPO_CHECK_PRODUCTION_SENTINEL"
        broken = {"go": "\nvar _ = " + token + "\n", "python": "\nraise RuntimeError('" + token + "')\n",
                  "typescript": "\nconst " + token + " = ;\n"}[language]
        target.write_bytes(original + broken.encode())
        code, xml, log = self.invoke(source, "production-error")
        values = self.vectors(xml, expected)
        self.record("production-error-named-diagnostics", code != 0 and "error" in values.values() and token in xml,
                    f"effective candidate {production}; {sum(v == 'error' for v in values.values())} named errors; production-error.xml")
        target.write_bytes(original)

        # A sentinel production failure remains while candidate tests try to skip
        # themselves. Restoring the tests must expose the production failure.
        native = self.profile["native_ids"][one]
        if language == "go":
            if "::Test" not in one:
                raise ValueError("a repository-native skip probe is needed for a Go suite without testing.T cases")
            pkg = native[0].removeprefix(self.profile["toolchain"]["module"]).lstrip('/')
            test_file = next(n for n in self.profile["tests"] if str(Path(n).parent).replace('\\', '/') == pkg and native[1] in (source / n).read_text(errors="replace"))
            test_text = (source / test_file).read_text()
            skip_text = re.sub(r"(func " + re.escape(native[1]) + r"\([^)]*\)\s*\{)", r'\1 t.Skip("REPO_CHECK_SKIP_SENTINEL");', test_text, count=1)
            if skip_text == test_text:
                raise ValueError("could not inject skip into selected Go test")
        elif language == "python":
            test_file = native.split("::")[0]
            test_text = (source / test_file).read_text()
            skip_text = test_text + '\nimport pytest\npytestmark = pytest.mark.skip(reason="REPO_CHECK_SKIP_SENTINEL")\n'
        else:
            test_file = next((name for name in self.profile["config"] if re.search(r"(^|/)vitest\.config\.[jt]s$", name)), "vitest.config.ts")
            test_text = (source / test_file).read_text() if (source / test_file).is_file() else None
            skip_text = "export default {test: {exclude: ['**/*']}}; // REPO_CHECK_SKIP_SENTINEL\n"
        (source / test_file).write_text(skip_text, encoding="utf-8", newline="\n")
        code, xml, log = self.invoke(source, "test-tamper", ["--one", one])
        values = self.vectors(xml, [one])
        self.record("test-skip-restored", code == 0 and values[one] == "pass" and "REPO_CHECK_SKIP_SENTINEL" not in xml,
                    f"candidate skip in {test_file} undone; original assertion executes")
        # The same tampered test with broken production must still fail by name.
        target.write_bytes(original + broken.encode())
        code, xml, _ = self.invoke(source, "tamper-with-production", ["--one", one])
        values = self.vectors(xml, [one])
        self.record("production-not-restored", code != 0 and values[one] == "error" and token in xml,
                    "test restoration preserves the production sentinel; tamper-with-production.xml")
        target.write_bytes(original)
        if test_text is None:
            (source / test_file).unlink()
        else:
            (source / test_file).write_text(test_text, encoding="utf-8", newline="\n")
        code, xml, _ = self.invoke(source, "unknown-uid-cleared-env")
        values = self.vectors(xml, expected)
        allowed = self.profile["skip_allowlist"]
        self.record("uid-env-cwd-readonly-offline", code == 0 and all(v == "pass" or (v == "skipped" and k in allowed) for k, v in values.items()),
                    "uid/gid 12345 absent from passwd; env -i PATH=/usr/local/bin:/usr/bin:/bin; cwd /; /app:ro; network none")
        self.failure_probes(source, one, test_file)

    def failure_probes(self, source, one, test_file):
        runner = source / "test.sh"
        original = runner.read_text(encoding="utf-8")

        def probe(label, body, token):
            if body == original:
                raise ValueError("fault injection did not change runner: " + label)
            (self.out / (label + "-test.sh")).write_text(body, encoding="utf-8", newline="\n")
            runner.write_text(body, encoding="utf-8", newline="\n")
            try:
                code, xml, _ = self.invoke(source, label, ["--one", one])
                values = self.vectors(xml, [one])
                self.record(label, code != 0 and values[one] in ("error", "failure") and token in xml,
                            f"one named failing case carries {token}; {label}.xml")
            finally:
                runner.write_text(original, encoding="utf-8", newline="\n")

        anchor = "        work = prepare(Path(sys.argv[1]), scratch, env, args.mode)"
        suffix = {"go": "\nvar _ = REPO_CHECK_TEST_BUILD_SENTINEL\n",
                  "python": "\ndef REPO_CHECK_TEST_BUILD_SENTINEL(:\n",
                  "typescript": "\nconst REPO_CHECK_TEST_BUILD_SENTINEL = ;\n"}[self.profile["language"]]
        injection = (anchor + "\n        with (work / " + repr(test_file) + ").open('a') as injected:\n"
                     "            injected.write(" + repr(suffix) + ")")
        probe("test-build-after-restore", original.replace(anchor, injection), "REPO_CHECK_TEST_BUILD_SENTINEL")
        injection = anchor + "\n        PROFILE['selectors']['base'] = []"
        probe("zero-selection", original.replace(anchor, injection), "zero selection")
        injection = anchor + "\n        PROFILE['timeout'] = 1\n        PROFILE['setup_commands'] = [[sys.executable, '-c', 'import time; time.sleep(10)']]"
        probe("watchdog-timeout", original.replace(anchor, injection), "timeout: 1 seconds")
        # Simulate failures at the report boundary after a real native execution.
        boundary = "    return status, cases, '\\n'.join(diagnostics)"
        if self.profile["language"] == "python":
            native = "        try:\n            cases = list(ET.parse(report).iter('testcase'))"
            for label, statement in (("absent-report", "report.unlink()"), ("empty-report", "report.write_text('')"),
                                     ("malformed-report", "report.write_text('not XML')")):
                probe(label, original.replace(native, "        " + statement + "\n" + native), "absent/empty/malformed native report")
        else:
            for label, replacement, token in (
                ("absent-report", "    cases = []\n    diagnostics.append('REPO_CHECK_ABSENT_REPORT')", "REPO_CHECK_ABSENT_REPORT"),
                ("empty-report", "    cases = []\n    diagnostics.append('REPO_CHECK_EMPTY_REPORT')", "REPO_CHECK_EMPTY_REPORT"),
                ("malformed-report", "    ET.fromstring('REPO_CHECK_MALFORMED_REPORT')", "syntax error"),
            ):
                probe(label, original.replace(boundary, replacement + "\n" + boundary), token)
        # A converter crash must still emit an independently escaped named report.
        converter = "    try:\n        return write_report(output, expected, cases, diagnostic, status, args.mode)"
        replacement = "    try:\n        raise RuntimeError('REPO_CHECK_CONVERTER_SENTINEL')\n        return write_report(output, expected, cases, diagnostic, status, args.mode)"
        probe("converter-failure", original.replace(converter, replacement), "REPO_CHECK_CONVERTER_SENTINEL")
        collection = "        ids = collect(work, scratch, env, args.mode)"
        probe("collection-failure", original.replace(collection, "        raise RuntimeError('REPO_CHECK_COLLECTION_SENTINEL')\n" + collection),
              "REPO_CHECK_COLLECTION_SENTINEL")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("--timeout", type=int, default=660)
    args = parser.parse_args()
    check = None
    try:
        if not 0 < args.timeout < 688:
            raise ValueError("timeout must be positive and below the platform bound")
        check = Check(args.task.resolve(), args.timeout)
        if git(check.task / "base", "status", "--porcelain"):
            raise ValueError("base checkout is dirty")
        if (git(check.task / "base", "rev-parse", "HEAD") != check.profile["identity"]["commit"] or
                git(check.task / "base", "rev-parse", "HEAD^{tree}") != check.profile["identity"]["tree"]):
            raise ValueError("base checkout does not match the pinned profile identity")
        if check.build():
            check.probes()
    except Exception as exc:
        if check:
            check.record("self-check", False, f"{type(exc).__name__}: {exc}")
        else:
            print(f"FAIL self-check: {exc}", file=sys.stderr)
            return 1
    completed = {row["step"] for row in check.results}
    for name in STEPS:
        if name not in completed:
            check.record(name, False, "NOT EXECUTED: blocked by a preceding failure")
    passed = bool(check.results) and all(row["result"] == "PASS" for row in check.results)
    check.profile["base_adapter_qualified"] = passed
    check.profile["qualified"] = False
    save(check.task, check.profile)
    if check.checked_runner_sha:
        final_sha = hashlib.sha256((check.task / "init/test.sh").read_bytes()).hexdigest()
        same = final_sha == check.checked_runner_sha
        check.record("runner-identity-unchanged", same,
                     "final runner matches executed probes" if same else "runner changed during qualification; rerun required")
        if not same:
            check.profile["base_adapter_qualified"] = False
            save(check.task, check.profile)
        passed = passed and same
    print("New-feature four-cell proof and human platform build remain OPEN.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
