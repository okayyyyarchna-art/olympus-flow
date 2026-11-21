import json
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

from test_capacity import load_proof


class Proof(unittest.TestCase):
    def setUp(self):
        self.proof = load_proof()
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def cell(self, xml, exit_code=0, mode="new", solution=True, ids=None):
        calls = []
        def docker(*args, **kwargs):
            calls.append(args)
            if len(calls) == 1:
                return subprocess.CompletedProcess(args, 0, "prepared", "")
            return subprocess.CompletedProcess(args, exit_code,
                                               "test log\n" + self.proof.MARK + "\n" + xml, "stderr")
        with patch.object(self.proof, "docker", side_effect=docker):
            result = self.proof.run("image", self.root, self.root / "out", mode, solution,
                                    expected_ids=ids or ["C::one"])
        return result, calls

    def test_strict_reconciliation_rejects_all_integrity_failures(self):
        good = '<testcase classname="C" name="one"/>'
        failures = [
            (f"<testsuite>{good}{good}</testsuite>", 0),
            ("<testsuite/>", 0),
            ('<testsuite><testcase name="other"/></testsuite>', 0),
            (f'<testsuite>{good}<testcase name="extra"/></testsuite>', 0),
            ('<testsuite><testcase classname="C" name="one"><skipped/></testcase></testsuite>', 0),
            (f"<testsuite>{good}</testsuite>", 17),
            ('<testsuite><testcase classname="C" name="one"><failure message="broken"/></testcase></testsuite>', 0),
            ("", 0), ("not xml", 0),
        ]
        for xml, code in failures:
            with self.subTest(xml=xml, exit=code), tempfile.TemporaryDirectory(dir=self.root) as tmp:
                original = self.root
                self.root = Path(tmp)
                try:
                    with self.assertRaises(ValueError):
                        self.cell(xml, code)
                finally:
                    self.root = original

    def test_h4_mount_environment_status_and_logs(self):
        xml = '<testsuite><testcase classname="C" name="one"/></testsuite>'
        (results, _), calls = self.cell(xml)
        self.assertEqual(results, {"C::one": "pass"})
        args = calls[1]
        self.assertEqual(args[args.index("--workdir") + 1], "/")
        self.assertEqual(args[args.index("--user") + 1], "12345:12345")
        self.assertIn(f"{self.root / 'out/source'}:/app:ro", args)
        self.assertIn("/out:rw,mode=1777", args)
        self.assertEqual(args[args.index("--network") + 1], "none")
        self.assertEqual(args[args.index("-i") + 1], "PATH=/usr/local/bin:/usr/bin:/bin")
        self.assertNotIn("HOME=", " ".join(args))
        self.assertIn('exit "$status"', args[-1])
        self.assertIn("grep -qx '12345'", calls[0][-1])
        self.assertEqual(json.loads((self.root / "out/new-exit.json").read_text())["exit_code"], 0)
        self.assertIn("stderr", (self.root / "out/new.log").read_text())

    def test_unsolved_requires_every_id_to_fail_and_nonzero_exit(self):
        xml = '<testsuite><testcase classname="C" name="one"><failure>missing feature</failure></testcase></testsuite>'
        (results, _), _ = self.cell(xml, 1, solution=False)
        self.assertEqual(results, {"C::one": "failure"})

    def test_image_identity_changes_with_every_environment_input(self):
        baseline = (b"FROM base", "commit", "tree", [{"digest": "sha256:one"}], "linux/amd64")
        key, _ = self.proof.image_key(*baseline)
        for index, value in enumerate((b"FROM other", "other-commit", "other-tree",
                                       [{"digest": "sha256:two"}], "linux/arm64")):
            changed = list(baseline)
            changed[index] = value
            self.assertNotEqual(key, self.proof.image_key(*changed)[0])

    def test_resolution_pins_actual_build_to_digest_and_platform(self):
        digest = "base@sha256:" + "a" * 64
        def docker(*args, **kwargs):
            output = json.dumps([digest]) if args[0] == "image" else ""
            return subprocess.CompletedProcess(args, 0, output, "")
        with patch.object(self.proof, "docker", side_effect=docker) as mocked:
            resolved, bases = self.proof.resolve_dockerfile(b"ARG BASE=base:latest\nFROM ${BASE} AS build\nFROM build\n", "linux/amd64")
        self.assertIn(digest.encode(), resolved)
        self.assertEqual(len(bases), 1)
        self.assertEqual(bases[0]["platform"], "linux/amd64")
        self.assertEqual(mocked.call_args_list[0].args[:3], ("pull", "--platform", "linux/amd64"))
        self.assertEqual(self.proof.repository_id("docker.io/library/base:latest"),
                         self.proof.repository_id(digest))

    def test_ids_must_be_nonempty_unique_files(self):
        path = self.root / "ids.json"
        for value in ([], ["one", "one"], [""]):
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                self.proof.read_ids(path)

    def test_base_skips_need_allowlist_and_new_skips_never_pass(self):
        xml = '<testsuite><testcase classname="C" name="one"><skipped/></testcase></testsuite>'
        def docker(*args, **kwargs):
            return subprocess.CompletedProcess(args, 0, "\n" + self.proof.MARK + "\n" + xml, "")
        with patch.object(self.proof, "docker", side_effect=docker):
            cases, _ = self.proof.run("image", self.root, self.root / "base", "base", True,
                                     expected_ids=["C::one"], allowed_skips=["C::one"])
            self.assertEqual(cases, {"C::one": "skipped"})
            with self.assertRaises(ValueError):
                self.proof.run("image", self.root, self.root / "new", "new", True,
                               expected_ids=["C::one"], allowed_skips=["C::one"])

    def test_every_main_cell_receives_expected_ids_and_failed_cell_fails_proof(self):
        for name, data in (("base.json", ["baseline"]), ("new.json", ["feature"])):
            (self.root / name).write_text(json.dumps(data))
        (self.root / "Dockerfile").write_text("FROM base")
        for name in ("test.patch", "solution.patch"):
            (self.root / name).write_text("patch")
        argv = ["proof", str(self.root), str(self.root), "--base-ids", str(self.root / "base.json"),
                "--new-ids", str(self.root / "new.json"), "--work-root", str(self.root), "--stability"]
        calls = []
        def run(image, patches, out, mode, solution, **kwargs):
            self.assertEqual(kwargs["expected_ids"], ["baseline"] if mode == "base" else ["feature"])
            calls.append((mode, solution))
            return {kwargs["expected_ids"][0]: "pass" if solution or mode == "base" else "failure"}, 1
        with patch.object(sys, "argv", argv), \
             patch.object(self.proof, "resolve_dockerfile", return_value=(b"FROM base", [])), \
             patch.object(self.proof, "docker", return_value=subprocess.CompletedProcess([], 0, "", "")), \
             patch.object(self.proof.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "commit", "")), \
             patch.object(self.proof, "run", side_effect=run) as cell, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.proof.main(), 0)
            self.assertEqual(len(calls), 19)
            cell.side_effect = ValueError("inconsistent report")
            self.assertEqual(self.proof.main(), 1)

    def test_base_only_builds_then_runs_only_the_base_cell_through_the_run_hook(self):
        # repo_check hooks proof.run for native discovery; --base-only must reach it after the image step (BACKLOG 140/164).
        (self.root / "base.json").write_text(json.dumps(["baseline"]))
        (self.root / "Dockerfile").write_text("FROM base")
        for name in ("test.patch", "solution.patch"):
            (self.root / name).write_text("patch")
        argv = ["proof", str(self.root), str(self.root), "--base-ids", str(self.root / "base.json"),
                "--work-root", str(self.root), "--base-only", "--final"]
        calls = []
        def run(image, patches, out, mode, solution, **kwargs):
            calls.append((mode, solution, kwargs["expected_ids"], out.name))
            return {"baseline": "pass"}, 1
        with patch.object(sys, "argv", argv), \
             patch.object(self.proof, "resolve_dockerfile", return_value=(b"FROM base", [])), \
             patch.object(self.proof, "docker", return_value=subprocess.CompletedProcess([], 0, "", "")), \
             patch.object(self.proof.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "commit", "")), \
             patch.object(self.proof, "run", side_effect=run) as cell, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.proof.main(), 0)
            self.assertEqual(calls, [("base", False, ["baseline"], "base-base")])
            cell.side_effect = ValueError("inconsistent report")
            self.assertEqual(self.proof.main(), 1)
        with patch.object(sys, "argv", argv[:-2] + ["--final"]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.proof.main()  # without --base-only, --new-ids is still required


BASE_XML = '<testsuite><testcase classname="C" name="old"/></testsuite>'
NEW_XML = '<testsuite><testcase classname="C" name="feature"/></testsuite>'
EXTRA_XML = '<testsuite><testcase classname="C" name="old"/><testcase classname="C" name="script"/></testsuite>'
FAILED_XML = '<testsuite><testcase classname="C" name="old"><failure message="x">bad</failure></testcase></testsuite>'


class PlatformCells(unittest.TestCase):
    """The platform-identity cells: --root-base, --two-user, --plain-new (BACKLOG #155, #158, #172, #174)."""

    def setUp(self):
        self.proof = load_proof()
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ids = {"base": ["C::old"], "new": ["C::feature"]}

    def stdout(self, exits, files):
        head = "".join(f"STEP {step} exit {code}\n" for step, code in exits.items())
        return head + "".join(f"\n{self.proof.MARK} {name}\n{text}" for name, text in files.items())

    def cell(self, steps, exits, files, code=0):
        calls = []
        def docker(*args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, code, self.stdout(exits, files), "stderr text")
        with patch.object(self.proof, "docker", side_effect=docker):
            got = self.proof.platform_cell("image", self.root, self.root / "cell", steps)
        return got, calls[0]

    def test_two_user_cell_runs_as_root_in_the_image_and_returns_each_step(self):
        got, args = self.cell(("baseline", "new", "after"), {"baseline": 0, "apply": 0, "new": 0, "after": 1},
                              {"baseline.xml": BASE_XML, "new.xml": NEW_XML, "after.xml": BASE_XML, "apply.log": "ok"})
        self.assertEqual(args[0], "run")
        self.assertEqual(args[args.index("--user") + 1], "0:0")
        self.assertEqual(args[args.index("--workdir") + 1], "/app")
        self.assertEqual(args[args.index("--network") + 1], "none")
        self.assertIn(f"{self.root}:/patches:ro", args)
        self.assertNotIn(":/app:ro", " ".join(args))  # the image's own /app, as on the platform
        script = args[-1]
        for text in ("groupadd -g 1000 model", "useradd -m -u 1000 -g 1000", "chmod -R a+rwX /app", "chmod +x test.sh",
                     "git apply --whitespace=nowarn /patches/test.patch",
                     "./test.sh base --output_path /out/baseline.xml",
                     "as 'git -c safe.directory=/app apply --whitespace=nowarn /patches/solution.patch'",
                     "as './test.sh new --output_path /out/new.xml'", "as './test.sh base --output_path /out/after.xml'"):
            self.assertIn(text, script)
        self.assertLess(script.index("chmod -R a+rwX /app"), script.index("/patches/test.patch"))
        self.assertLess(script.index("STEP baseline"), script.index("/patches/solution.patch"))
        self.assertEqual(got, {"baseline": (0, BASE_XML), "apply": (0, "ok"), "new": (0, NEW_XML), "after": (1, BASE_XML)})
        self.assertEqual((self.root / "cell/new.xml").read_text(), NEW_XML)
        self.assertIn("stderr text", (self.root / "cell/cell.log").read_text())

    def test_root_base_cell_has_no_model_steps_and_plain_cell_calls_test_sh_new_bare(self):
        got, args = self.cell(("baseline",), {"baseline": 0}, {"baseline.xml": BASE_XML})
        self.assertNotIn("solution.patch", args[-1])
        self.assertEqual(got, {"baseline": (0, BASE_XML)})
        got, args = self.cell(("plain",), {"apply": 0, "plain": 0}, {"apply.log": "", "plain.log": "ok  1 test"})
        self.assertIn("as './test.sh new' >", args[-1])
        self.assertNotIn("--output_path", args[-1].split("STEP apply")[1])
        self.assertNotIn("test.sh base", args[-1])
        self.assertEqual(got["plain"], (0, "ok  1 test"))

    def test_failed_container_or_missing_step_raises(self):
        with self.assertRaises(ValueError):
            self.cell(("baseline",), {}, {}, code=97)
        with self.assertRaises(ValueError) as caught:
            self.cell(("baseline", "new", "after"), {"baseline": 0}, {"baseline.xml": BASE_XML})
        self.assertIn("steps run ['baseline']", str(caught.exception))

    def fake_cells(self, files, exits=()):
        exits = dict(exits)
        calls = []
        def platform_cell(image, patches, out, steps, platform=None, timeout=600):
            calls.append(steps)
            out.mkdir(parents=True, exist_ok=True)
            result = {}
            for step in steps + (("apply",) if set(steps) & {"new", "after", "plain"} else ()):
                text = files.get(step, "")
                (out / f"{step}.xml").write_text(text)
                result[step] = (exits.get(step, 0), text)
            return result
        return platform_cell, calls

    def verdicts(self, files, exits=(), **flags):
        from types import SimpleNamespace
        args = SimpleNamespace(**{"root_base": False, "two_user": False, "plain_new": False, "timeout": 600, **flags})
        fake, _ = self.fake_cells(files, exits)
        self.proof.ok = True
        out = io.StringIO()
        with patch.object(self.proof, "platform_cell", side_effect=fake), contextlib.redirect_stdout(out):
            self.proof.platform_cells(args, "image", self.root, self.root, self.ids, [], "linux/amd64")
        return self.proof.ok, out.getvalue()

    def test_verdicts_follow_the_platform_rules(self):
        clean = {"baseline": BASE_XML, "new": NEW_XML, "after": BASE_XML, "plain": "ok"}
        good, out = self.verdicts(clean, root_base=True, two_user=True, plain_new=True)
        self.assertTrue(good, out)
        self.assertEqual(out.count("PASS  "), 7)  # root base; apply, baseline, new, sets; apply, plain
        self.assertIn("two-user: uid 1000 applies solution.patch in /app after root's run (exit 0)", out)
        self.assertIn("two-user: verifySolution sets baseline failures 0", out)
        self.assertIn("plain-new: test.sh new with no --output_path exits 0", out)
        good, out = self.verdicts({**clean, "after": EXTRA_XML}, two_user=True)
        self.assertFalse(good)
        self.assertIn("FAIL  two-user: verifySolution sets", out)
        self.assertIn("after extras (not a baseline pass, not a new case, not skipped): C::script", out)
        good, out = self.verdicts({**clean, "baseline": FAILED_XML}, exits={"baseline": 1}, root_base=True)
        self.assertFalse(good)
        self.assertIn("FAIL  root-base: base mode as root:", out)
        good, out = self.verdicts(clean, exits={"apply": 1}, two_user=True)
        self.assertFalse(good)
        self.assertIn("FAIL  two-user: uid 1000 applies solution.patch", out)
        good, out = self.verdicts(clean, exits={"plain": 2}, plain_new=True)
        self.assertFalse(good)
        self.assertIn("FAIL  plain-new: test.sh new with no --output_path exits 2", out)
        self.proof.ok = True
        with patch.object(self.proof, "platform_cell", side_effect=ValueError("no steps")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            from types import SimpleNamespace
            self.proof.platform_cells(SimpleNamespace(root_base=True, two_user=False, plain_new=False, timeout=600),
                                      "image", self.root, self.root, self.ids, [], None)
        self.assertFalse(self.proof.ok)
        self.assertIn("FAIL  root-base: no steps", out.getvalue())

    def test_main_runs_the_platform_cells_only_with_their_flags(self):
        for name, data in (("base.json", ["C::old"]), ("new.json", ["C::feature"])):
            (self.root / name).write_text(json.dumps(data))
        (self.root / "Dockerfile").write_text("FROM base")
        for name in ("test.patch", "solution.patch"):
            (self.root / name).write_text("patch")
        argv = ["proof", str(self.root), str(self.root), "--base-ids", str(self.root / "base.json"),
                "--new-ids", str(self.root / "new.json"), "--work-root", str(self.root)]
        fake, calls = self.fake_cells({"baseline": BASE_XML, "new": NEW_XML, "after": BASE_XML, "plain": "ok"})
        def run(image, patches, out, mode, solution, **kwargs):
            return {kwargs["expected_ids"][0]: "pass" if solution or mode == "base" else "failure"}, 1
        with patch.object(self.proof, "resolve_dockerfile", return_value=(b"FROM base", [])), \
             patch.object(self.proof, "docker", return_value=subprocess.CompletedProcess([], 0, "", "")), \
             patch.object(self.proof.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "commit", "")), \
             patch.object(self.proof, "run", side_effect=run), \
             patch.object(self.proof, "platform_cell", side_effect=fake), contextlib.redirect_stdout(io.StringIO()):
            with patch.object(sys, "argv", argv):
                self.assertEqual(self.proof.main(), 0)
            self.assertEqual(calls, [])
            with patch.object(sys, "argv", argv + ["--root-base", "--two-user", "--plain-new"]):
                self.assertEqual(self.proof.main(), 0)
            self.assertEqual(calls, [("baseline",), ("baseline", "new", "after"), ("plain",)])
            with patch.object(sys, "argv", argv + ["--two-user", "--base-only"]):
                self.assertEqual(self.proof.main(), 0)
            self.assertEqual(len(calls), 3)  # --base-only returns before the platform cells


if __name__ == "__main__":
    unittest.main()
