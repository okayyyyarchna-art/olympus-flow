import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("junit_sets", Path(__file__).parents[1] / "tools/junit_sets.py")
junit_sets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(junit_sets)


def xml(*cases):
    body = ""
    for name, status in cases:
        child = {"pass": "", "fail": "<failure>broken</failure>", "skip": "<skipped/>"}[status]
        body += f'<testcase classname="pkg" name="{name}">{child}</testcase>'
    return f"<testsuites><testsuite>{body}</testsuite></testsuites>"


BASE = xml(("Old1", "pass"), ("Old2", "pass"), ("Platform", "skip"))
NEW = xml(("Feature1", "pass"), ("Feature2", "pass"))
AFTER = xml(("Old1", "pass"), ("Old2", "pass"), ("Platform", "skip"))


class Sets(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def files(self, base=BASE, new=NEW, after=AFTER):
        paths = []
        for name, data in (("base", base), ("new", new), ("after", after)):
            path = self.root / f"{name}.xml"
            path.write_text(data, encoding="utf-8")
            paths.append(str(path))
        return paths

    def run_main(self, *paths):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = junit_sets.main(list(paths))
        return code, out.getvalue()

    def test_cases_use_kit_ids_and_three_statuses(self):
        base = junit_sets.cases(self.files()[0])
        self.assertEqual(base, {"pkg::Old1": "pass", "pkg::Old2": "pass", "pkg::Platform": "skip"})

    def test_clean_triple_passes_with_every_set_empty(self):
        code, out = self.run_main(*self.files())
        self.assertEqual(code, 0)
        self.assertIn("VERDICT PASS", out)
        self.assertIn("baseline 3 cases: pass 2 skip 1; new 2 cases; after 3 cases", out)
        sets = junit_sets.check(junit_sets.cases(self.files()[0]), {}, junit_sets.cases(self.files()[2]))
        self.assertFalse(any(sets.values()))

    def test_each_rejected_set_fails_alone(self):
        rejected = {
            "baseline failures": dict(base=xml(("Old1", "fail"), ("Old2", "pass")),
                                      after=xml(("Old2", "pass"), ("Platform", "skip"))),
            "new cases not passing": dict(new=xml(("Feature1", "pass"), ("Feature2", "skip"))),
            "new cases that the baseline also has": dict(new=xml(("Old1", "pass"), ("Feature2", "pass"))),
            "after extras (not a baseline pass, not a new case, not skipped)":
                dict(after=xml(("Old1", "pass"), ("Old2", "pass"), ("Platform", "skip"), ("Script", "pass"))),
            "baseline passes not passing in the after run": dict(after=xml(("Old1", "pass"), ("Old2", "fail"))),
        }
        for title, change in rejected.items():
            with self.subTest(title=title):
                code, out = self.run_main(*self.files(**change))
                self.assertEqual(code, 1)
                self.assertIn("VERDICT FAIL", out)
                self.assertIn(f"{title}: 1\n", out)
                others = [line for line in out.splitlines() if line.endswith(": 1") and not line.startswith(title)]
                self.assertEqual(others, [])

    def test_skipped_after_extra_and_missing_after_case_are_judged_as_the_platform_does(self):
        skipped_extra = xml(("Old1", "pass"), ("Old2", "pass"), ("Platform", "skip"), ("Script", "skip"))
        self.assertEqual(self.run_main(*self.files(after=skipped_extra))[0], 0)
        missing = xml(("Old1", "pass"))
        code, out = self.run_main(*self.files(after=missing))
        self.assertEqual(code, 1)
        self.assertIn("  - pkg::Old2", out)

    def test_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err, patch.object(sys, "argv", ["junit_sets.py", "one"]):
            self.assertEqual(junit_sets.main(sys.argv[1:]), 2)
        self.assertIn("usage: junit_sets.py", err.getvalue())


if __name__ == "__main__":
    unittest.main()
