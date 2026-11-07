import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import repo_init


class Discovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def files(self, files):
        for name, body in files.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "fixture"], check=True)

    def test_go_toolchain_commands_inventory_and_production_authority(self):
        self.files({"go.mod": "module example.org/project\n\ngo 1.24.0\ntoolchain go1.24.3\n",
                    "go.sum": "", "internal/config.go": "package internal\n",
                    "internal/p_test.go": "package internal\nfunc TestOne(t *testing.T) {}\n",
                    "internal/testdata/a.txt": "fixture", "Makefile": "test:\n\tgo test ./...\nfmt:\n\tgofmt -w .\n"})
        p = repo_init.discover(self.repo)
        self.assertEqual(p["toolchain"]["version"], "1.24.3")
        self.assertIn("go.sum", p["locks"])
        self.assertIn("internal/config.go", p["production"])
        self.assertNotIn("internal/config.go", p["config"])
        self.assertIn("internal/testdata/a.txt", p["fixtures"])
        self.assertEqual(p["expected"]["base"], ["example.org/project/internal::TestOne"])
        self.assertTrue(any(e["location"] == "go.mod:4" for e in p["evidence"]["toolchain"]))
        self.assertIn("go test -list", p["commands"]["enumerate"])

    def test_python_constraints_are_not_silently_exact_pins(self):
        self.files({"pyproject.toml": '[project]\nrequires-python = ">=3.10"\n[tool.pytest.ini_options]\n',
                    "p/__init__.py": "", "p/core.py": "x = 1\n", "tests/conftest.py": "",
                    "tests/test_a.py": "class TestA:\n def test_ok(self): pass\n",
                    ".github/workflows/ci.yml": "run: python -m pytest\nrun: black --check .\n"})
        p = repo_init.discover(self.repo)
        self.assertEqual(p["language"], "python")
        self.assertIn("p/core.py", p["production"])
        self.assertEqual(p["expected"]["base"], ["tests.test_a.TestA::test_ok"])
        self.assertTrue(any(r["field"] == "toolchain.version" for r in p["open"]))
        self.assertTrue(p["evidence"]["ci"])
        self.assertTrue(p["evidence"]["validation"])

    def test_typescript_lock_framework_and_package_manager(self):
        self.files({"package.json": json.dumps({"packageManager": "pnpm@10.1.0", "engines": {"node": ">=22"},
                    "devDependencies": {"vitest": "3.0.0"}, "scripts": {"test": "vitest run", "lint": "eslint ."}}),
                    ".nvmrc": "v22.13.0\n", "pnpm-lock.yaml": "lockfileVersion: '9.0'\n",
                    "src/index.ts": "export const x = 1;", "src/index.test.ts": "test('x', () => {});"})
        p = repo_init.discover(self.repo)
        self.assertEqual(p["language"], "typescript")
        self.assertEqual(p["toolchain"]["version"], "22.13.0")
        self.assertEqual(p["frameworks"], ["vitest"])
        self.assertEqual(p["commands"]["fetch"], "pnpm install --frozen-lockfile")
        self.assertIn("src/index.ts", p["production"])
        self.assertIn("src/index.test.ts", p["tests"])
        self.assertTrue(any("UNPROVEN" in r["reason"] for r in p["open"]))

    def test_rust_is_discovered_but_never_claimed_qualified(self):
        self.files({"Cargo.toml": '[package]\nname = "demo"\nversion = "0.1.0"',
                    "Cargo.lock": "", "rust-toolchain.toml": '[toolchain]\nchannel = "1.85.0"', "src/lib.rs": "pub fn f() {}"})
        p = repo_init.discover(self.repo)
        self.assertIn("rust", p["languages"])
        self.assertEqual(p["language"], "unsupported")
        self.assertTrue(any(e["location"] == "rust-toolchain.toml:2" for e in p["evidence"]["toolchain"]))

    def test_settings_cannot_smuggle_an_unrecognized_runtime_hook(self):
        with self.assertRaises(ValueError):
            repo_init.apply_settings({}, {"shell_hook": "unsafe"})

    def test_cli_fresh_clone_is_clean_and_all_template_markers_render(self):
        self.files({"go.mod": "module example.org/x\n\ngo 1.24.3\n", "x.go": "package x\n",
                    "x_test.go": "package x\nfunc TestX(t *testing.T) {}\n"})
        commit = repo_init.git(self.repo, "rev-parse", "HEAD")
        task = self.repo / "task"
        machine = TOOLS.parents[1] / "machine/windows-asus.json"
        env = dict(os.environ, OLYMPUS_MACHINE=str(machine))
        proc = subprocess.run([sys.executable, "-B", str(TOOLS / "repo_init.py"), str(self.repo), commit, str(task)],
                              env=env, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(repo_init.git(task / "base", "status", "--porcelain"), "")
        dockerfile = (task / "init/Dockerfile").read_text()
        self.assertNotIn("{{", dockerfile)
        self.assertIn("NOT_VERIFIED", dockerfile)
        self.assertIn("go1.24.3.linux-amd64.tar.gz", dockerfile)

    def test_restore_neutralizes_test_edits_and_retains_candidate_production(self):
        self.files({"p.py": "value = 1\n", "tests/test_p.py": "assert True\n", "tests/helper.py": "value = 2\n"})
        commit = repo_init.git(self.repo, "rev-parse", "HEAD")
        (self.repo / "p.py").write_text("value = 99\n")
        (self.repo / "tests/test_p.py").write_text("skip_all = True\n")
        (self.repo / "tests/rogue.py").write_text("shadow = True\n")
        (self.repo / "tests/feature.py").write_text("feature = True\n")
        # Scratch must be outside the candidate tree to avoid recursive copying.
        with tempfile.TemporaryDirectory() as folder:
            ns = runtime()
            ns["PROFILE"].update({"identity": {"commit": commit}, "language": "python",
                                  "restore_paths": ["tests/test_p.py", "tests/helper.py"],
                                  "tests": ["tests/test_p.py", "tests/helper.py"],
                                  "hidden_paths": ["tests/feature.py"]})
            effective = ns["prepare"](self.repo, Path(folder), dict(os.environ))
            self.assertEqual((effective / "p.py").read_text(), "value = 99\n")
            self.assertEqual((effective / "tests/test_p.py").read_text(), "assert True\n")
            self.assertEqual((effective / "tests/helper.py").read_text(), "value = 2\n")
            self.assertFalse((effective / "tests/rogue.py").exists())
            self.assertEqual((effective / "tests/feature.py").read_text(), "feature = True\n")
            ns["PROFILE"]["identity"]["commit"] = "f" * 40
            with self.assertRaisesRegex(RuntimeError, "pristine base commit unavailable"):
                ns["prepare"](self.repo, Path(folder), dict(os.environ))


def runtime():
    body = (repo_init.TEMPLATES / "python/test.sh").read_text().split("<<'ADAPTER_PY'\n", 1)[1].rsplit("\nADAPTER_PY", 1)[0]
    body = body.replace("PROFILE = json.loads(base64.b64decode('{{profile_b64}}'))", "PROFILE = {'skip_allowlist': {}}")
    body = body.rsplit("sys.exit(main())", 1)[0]
    namespace = {}
    exec(compile(body, "adapter-runtime", "exec"), namespace)
    return namespace


class Reporting(unittest.TestCase):
    def setUp(self):
        self.runtime = runtime()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / "a report.xml"

    def report(self, cases, code=0, mode="base", expected=("A::one", "A::two")):
        with contextlib.redirect_stderr(io.StringIO()):
            status = self.runtime["write_report"](self.output, expected, cases, "REAL <compiler> & diagnostic", code, mode)
        return status, list(ET.parse(self.output).iter("testcase"))

    def test_all_missing_ids_get_real_diagnostic_and_infrastructure_errors(self):
        code, cases = self.report([], 1)
        self.assertEqual(code, 1)
        self.assertEqual(len(cases), 2)
        self.assertTrue(all("REAL <compiler> & diagnostic" in c.find("error").text for c in cases))

    def test_partial_timeout_retains_completed_cases_and_names_missing(self):
        one = ET.Element("testcase", classname="A", name="one")
        code, cases = self.report([one], 124)
        self.assertEqual(code, 1)
        self.assertIsNone(cases[0].find("error"))
        self.assertIsNotNone(cases[1].find("error"))

    def test_reporter_success_does_not_hide_failed_process(self):
        cases = [ET.Element("testcase", classname="A", name=n) for n in ("one", "two")]
        code, result = self.report(cases, 17)
        self.assertEqual(code, 1)
        self.assertIsNotNone(result[0].find("error"))

    def test_duplicate_unexpected_empty_and_missing_reports_fail(self):
        one = ET.Element("testcase", classname="A", name="one")
        other = ET.Element("testcase", name="surprise")
        for cases in ([], [one], [one, one], [one, other]):
            with self.subTest(cases=cases):
                self.assertEqual(self.report(cases)[0], 1)

    def test_base_skips_need_exact_reasons_and_new_never_allows_skips(self):
        def cases():
            c = ET.Element("testcase", classname="A", name="one")
            ET.SubElement(c, "skipped")
            return [c]
        self.assertEqual(self.report(cases(), expected=["A::one"])[0], 1)
        self.runtime["PROFILE"]["skip_allowlist"] = {"A::one": "optional backend not selected; exact source evidence required"}
        self.assertEqual(self.report(cases(), expected=["A::one"])[0], 0)
        self.assertEqual(self.report(cases(), mode="new", expected=["A::one"])[0], 1)

    def test_zero_inventory_is_not_a_successful_empty_suite(self):
        with self.assertRaises(RuntimeError):
            self.report([], expected=[])

    def test_diagnostics_with_control_bytes_still_produce_valid_xml(self):
        self.assertEqual(self.runtime["write_report"](self.output, ["one"], [], "bad\x00\x1boutput", 1, "base"), 1)
        self.assertIn("bad\\x00\\x1boutput", ET.parse(self.output).find(".//error").text)

    def test_templates_share_the_same_qualified_runtime(self):
        values = [(repo_init.TEMPLATES / lang / "test.sh").read_text() for lang in ("go", "python", "typescript")]
        self.assertEqual(values[0], values[1])
        self.assertEqual(values[1], values[2])


if __name__ == "__main__":
    unittest.main()
