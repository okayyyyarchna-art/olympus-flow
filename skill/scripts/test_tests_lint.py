import contextlib
import importlib.util
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("tests_lint", Path(__file__).parents[1] / "tools/tests_lint.py")
tests_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests_lint)

GO_REPO = {
    "go.mod": "module example.org/m\n\ngo 1.24.0\n",
    "internal/engine/engine.go": 'package engine\n\nimport "example.org/m/internal/state"\n\nvar _ = state.X\n',
    "internal/engine/engine_test.go": ('package engine\n\nimport (\n\t"testing"\n\t"time"\n\n\t"example.org/m/internal/testhelp"\n)\n\n'
                                       'func TestFast(t *testing.T) {\n\tstart := time.Now()\n\ttesthelp.Use()\n'
                                       '\tif time.Since(start) > 2*time.Second {\n\t\tt.Fatal("slow")\n\t}\n}\n'),
    "internal/state/state.go": "package state\n\nvar X = 1\n",
    "internal/state/state_test.go": ('package state\n\nimport (\n\t"os"\n\t"testing"\n)\n\n'
                                     'func TestRoot(t *testing.T) {\n\tif os.Geteuid() == 0 {\n\t\tt.Skip("root")\n\t}\n}\n'),
    "internal/testhelp/helper.go": "package testhelp\n\nfunc Use() {}\n",
    "internal/cli/cli.go": 'package cli\n\nimport "example.org/m/internal/engine"\n\nvar _ = engine.Run\n',
    "internal/cli/cli_test.go": 'package cli\n\nimport "testing"\n\nfunc TestCLI(t *testing.T) {}\n',
    "internal/other/other.go": 'package other\n\nimport "example.org/m/internal/engine"\n\nvar _ = engine.Run\n',
    "internal/engine/testdata/ignored.go": 'package ignored\n\nimport "example.org/m/internal/cli"\n',
}
SOLUTION = ("diff --git a/internal/engine/engine.go b/internal/engine/engine.go\n--- a/internal/engine/engine.go\n"
            "+++ b/internal/engine/engine.go\n@@ -1,3 +1,4 @@\n+// changed\n")


def patch_with_test_sh(body):
    lines = "".join("+" + ln + "\n" for ln in body.splitlines())
    return ("diff --git a/test.sh b/test.sh\nnew file mode 100755\n--- /dev/null\n+++ b/test.sh\n@@ -0,0 +1,9 @@\n" + lines)


BASH_RUNNER = """#!/usr/bin/env bash
MODE="${1:-base}"
PINNED='(_test[.]go)$'
case "$MODE" in
  base)
    BASE_PKGS=(internal/engine internal/state)
    go test -v "${BASE_PKGS[@]/#/./}"
    ;;
  new) go test -v ./internal/engine -run '^TestNew' ;;
esac
"""
BASH_RUNNER_FIXED = BASH_RUNNER.replace("PINNED='(_test[.]go)$'",
                                        "PINNED='(_test[.]go|internal/testhelp/[^/]*[.]go)$'\nrestore_tests \"$PINNED\" internal/testhelp internal/engine\n"
                                        "# base skip: internal/cli its only test needs a network listener the image has no permission for")
ADAPTER_RUNNER = """#!/usr/bin/env bash
exec python - "$@" <<'ADAPTER_PY'
import json
PROFILE = json.loads(r'''
{
  "selectors": {"base": ["./internal/engine", "./internal/state"], "new": ["./internal/engine"]},
  "restore_paths": ["internal/engine/engine_test.go", "internal/state/state_test.go", "internal/testhelp/helper.go"],
  "helpers": ["internal/testhelp/helper.go"]
}
''')
print(PROFILE)
ADAPTER_PY
"""


class GoChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "base"
        for name, body in GO_REPO.items():
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        self.pkg = self.root / "pkg"
        self.pkg.mkdir()
        (self.pkg / "description.md").write_text("Engine runs.\n")
        (self.pkg / "solution.patch").write_text(SOLUTION)

    def run_lint(self, test_sh):
        (self.pkg / "test.patch").write_text(patch_with_test_sh(test_sh))
        output = io.StringIO()
        tests_lint.out.clear()
        with patch.object(tests_lint.shutil, "which", lambda *_: None), \
                patch.object(sys, "argv", ["tests_lint", str(self.pkg), str(self.repo)]), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as exc:
                tests_lint.main()
        return exc.exception.code, output.getvalue().splitlines()

    def test_regex_graph_resolves_module_imports_and_skips_testdata(self):
        pkgs = tests_lint.go_scan(self.repo)
        self.assertEqual(pkgs["internal/engine"]["imports"], {"internal/state"})
        self.assertEqual(pkgs["internal/engine"]["test_imports"], {"internal/testhelp"})
        self.assertEqual(pkgs["internal/cli"]["imports"], {"internal/engine"})
        self.assertNotIn("internal/engine/testdata", pkgs)

    def test_bash_runner_unpinned_helper_missing_importer_and_candidates(self):
        code, lines = self.run_lint(BASH_RUNNER)
        self.assertEqual(code, 1)
        self.assertTrue(any("NOTE" in l and "regex parse" in l for l in lines), lines)
        self.assertTrue(any(l.startswith("FAIL") and "G1" in l and "internal/testhelp" in l for l in lines), lines)
        self.assertTrue(any(l.startswith("FAIL") and "G2" in l and "internal/cli" in l for l in lines), lines)
        # internal/other imports the changed package but has no tests: nothing to run
        self.assertFalse(any("internal/other" in l for l in lines), lines)
        self.assertTrue(any("W1" in l and "engine_test.go:13 TestFast: elapsed-time comparison" in l for l in lines), lines)
        self.assertTrue(any("W1" in l and "state_test.go:9 TestRoot: skips as root" in l for l in lines), lines)

    def test_pinned_helper_and_reasoned_skip_pass(self):
        code, lines = self.run_lint(BASH_RUNNER_FIXED)
        self.assertEqual(code, 0, lines)
        self.assertTrue(any(l.startswith("PASS") and "G1" in l and "internal/testhelp" in l for l in lines), lines)
        self.assertTrue(any(l.startswith("REVIEW") and "G2" in l and "internal/cli: its only test" in l for l in lines), lines)

    def test_adapter_profile_selection_and_restore_paths(self):
        code, lines = self.run_lint(ADAPTER_RUNNER)
        self.assertTrue(any("2 from selectors.base of the embedded profile" in l for l in lines), lines)
        self.assertTrue(any(l.startswith("PASS") and "G1" in l and "restore_paths/helpers" in l for l in lines), lines)
        self.assertTrue(any(l.startswith("FAIL") and "G2" in l and "internal/cli" in l for l in lines), lines)
        self.assertEqual(code, 1)

    def test_embedded_profile_reads_both_raw_string_forms(self):
        for quotes in ("'''", '"""'):
            with self.subTest(quotes=quotes):
                sh = "PROFILE = json.loads(r" + quotes + '\n{"selectors": {"base": ["./internal/engine"]}, "note": "it\'s \\"q\\""}\n' + quotes + ")\n"
                self.assertEqual(tests_lint.embedded_profile(sh)["selectors"]["base"], ["./internal/engine"])

    def test_no_base_selection_is_reported_not_guessed(self):
        code, lines = self.run_lint("#!/usr/bin/env bash\ngo test ./...\n")
        self.assertTrue(any(l.startswith("REVIEW") and "G0" in l for l in lines), lines)
        self.assertFalse(any(re.match(r"\w+\s+(G1|G2|W1)\b", l) for l in lines), lines)


if __name__ == "__main__":
    unittest.main()
