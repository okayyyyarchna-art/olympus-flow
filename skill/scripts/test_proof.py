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


if __name__ == "__main__":
    unittest.main()
