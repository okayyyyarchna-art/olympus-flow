import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

spec = importlib.util.spec_from_file_location("wrong_versions", Path(__file__).parents[1] / "tools/wrong_versions.py")
wv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wv)

KEPT = textwrap.dedent('''
    """{doc}"""
    KIND = {kind!r}
    EXPECT = {expect!r}
    EDITS = [("pkg/a.go", "\\tmark := original\\n", "\\tmark := {word}\\n")]


    def main():
        pass


    if __name__ == "__main__":
        main()
''')

# A stand-in for the test command: fails TestX/leaf when the tree holds the wrong edit; writes a JUnit report when
# asked, prints Go test lines otherwise; appends the {tests} argument it received to a log.
RUNNER = textwrap.dedent('''
    import pathlib, sys
    junit, tests, log = sys.argv[1:4]
    wrong = "WRONG" in pathlib.Path("pkg/a.go").read_text()
    with open(log, "a") as f:
        f.write(tests + "\\n")
    if junit != "-":
        bad = "<failure>bad</failure>" if wrong else ""
        pathlib.Path(junit).write_text('<testsuites><testsuite><testcase classname="pkg" name="TestX/leaf">' + bad
                                       + '</testcase><testcase classname="pkg" name="TestY"/></testsuite></testsuites>')
    else:
        print("--- FAIL: TestX\\n    --- FAIL: TestX/leaf" if wrong else "--- PASS: TestX\\nok")
    sys.exit(1 if wrong else 0)
''')


class WrongVersions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tree = self.root / "tree"
        (self.tree / "pkg").mkdir(parents=True)
        (self.tree / "pkg/a.go").write_bytes(b"package pkg\n\nfunc f() {\n\tmark := original\n}\n")
        self.kept = self.root / "kept"
        self.kept.mkdir()
        self.runner = self.root / "runner.py"
        self.runner.write_text(RUNNER, encoding="utf-8")
        self.log = self.root / "tests.log"

    def script(self, name, kind, expect, word):
        (self.kept / f"{name}.py").write_text(KEPT.format(doc=name, kind=kind, expect=expect, word=word),
                                              encoding="utf-8", newline="\n")

    def command(self, junit="{junit}"):
        return f'"{sys.executable}" "{self.runner}" {junit} {{tests}} "{self.log}"'

    def main(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = wv.main([str(self.kept), str(self.tree), "--cmd", self.command(), *extra])
        return code, out.getvalue()

    def test_apply_restores_bytes_and_a_stale_edit_fails_without_leaving_the_first_edit(self):
        originals = wv.apply(self.tree, [("pkg/a.go", "\tmark := original\n", "\tmark := WRONG\n")])
        self.assertIn(b"mark := WRONG\n", (self.tree / "pkg/a.go").read_bytes())
        wv.restore(self.tree, originals)
        self.assertEqual((self.tree / "pkg/a.go").read_bytes(), b"package pkg\n\nfunc f() {\n\tmark := original\n}\n")
        with self.assertRaises(ValueError) as caught:
            wv.apply(self.tree, [("pkg/a.go", "\tmark := original\n", "\tmark := WRONG\n"),
                                 ("pkg/a.go", "gone\n", "x\n")])
        self.assertIn("edit does not apply: pkg/a.go (0 matches)", str(caught.exception))
        self.assertIn(b"mark := original\n", (self.tree / "pkg/a.go").read_bytes())
        with self.assertRaises(ValueError):
            wv.apply(self.tree, [("pkg/missing.go", "a", "b")])

    def test_verdict_rules(self):
        leaf, parent = ["TestX/leaf"], ["TestX"]
        self.assertEqual(wv.verdict("wrong", leaf, 1, {"TestX", "TestX/leaf"}), ("ok", ""))
        self.assertEqual(wv.verdict("wrong", parent, 1, {"TestX/leaf"}), ("ok", ""))
        self.assertEqual(wv.verdict("wrong", leaf, 0, set()), ("BAD", "not caught: TestX/leaf"))
        self.assertEqual(wv.verdict("wrong", leaf, 1, {"TestX/leaf", "TestZ"}), ("ok", "also fails: TestZ"))
        self.assertEqual(wv.verdict("wrong", ["TestX/le"], 1, {"TestX/leaf_long_name"}), ("ok", ""))
        self.assertEqual(wv.verdict("wrong", leaf, 0, {"TestX/leaf"}), ("BAD", "exit 0 although the leaves fail"))
        self.assertEqual(wv.verdict("wrong", leaf, 1, None), ("BAD", "no report written"))
        self.assertEqual(wv.verdict("wrong", leaf, 124, set())[0], "BAD")
        self.assertEqual(wv.verdict("control", [], 0, set()), ("ok", ""))
        self.assertEqual(wv.verdict("control", [], 1, {"TestY"}), ("BAD", "a control fails"))
        self.assertEqual(wv.verdict("held", leaf, 0, set()), ("held", "not caught: TestX/leaf"))
        self.assertEqual(wv.verdict("held", leaf, 1, {"TestX/leaf"}), ("held", "caught"))
        self.assertEqual(wv.tests_regex(["TestB/x", "TestA", "TestB/y"]), "^(TestA|TestB)$")
        self.assertEqual(wv.tests_regex([]), "")

    def test_main_judges_each_kind_and_fails_on_a_stale_edit(self):
        self.script("wrong-one", "wrong", "TestX/leaf", "WRONG")
        self.script("control-one", "control", "", "CONTROL")
        self.script("held-one", "held", "TestX/leaf", "HELD")
        self.script("stale-one", "wrong", "TestX/leaf", "WRONG")
        stale = self.kept / "stale-one.py"
        stale.write_text(stale.read_text(encoding="utf-8").replace("mark := original", "gone"), encoding="utf-8")
        code, out = self.main()
        self.assertEqual(code, 1)
        self.assertIn("kept wrong-one (wrong): ok", out)
        self.assertIn("kept control-one (control): ok", out)
        self.assertIn("kept held-one (held): held", out)
        self.assertIn("not caught: TestX/leaf", out)
        self.assertIn("kept stale-one: BAD: edit does not apply: pkg/a.go (0 matches)", out)
        self.assertIn("WRONG VERSIONS FAIL: 4 kept scripts, 1 mismatches", out)
        self.assertIn("#179", out)
        # The tree itself is never edited, and {tests} carried the quoted regex of the top-level names (scripts run
        # in name order: control, held, stale (no run), wrong).
        self.assertIn(b"mark := original\n", (self.tree / "pkg/a.go").read_bytes())
        self.assertEqual(self.log.read_text().split("\n")[:3], ["", "^(TestX)$", "^(TestX)$"])
        code, out = self.main("--only", "wrong-one,control-one")
        self.assertEqual(code, 0)
        self.assertIn("WRONG VERSIONS PASS: 2 kept scripts, 0 mismatches", out)

    def test_go_text_output_route_and_tests_override(self):
        self.script("wrong-one", "wrong", "TestX/leaf", "WRONG")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = wv.main([str(self.kept), str(self.tree), "--cmd", self.command("-"), "--tests", "TestX,TestQ"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("failing: TestX, TestX/leaf", out.getvalue())
        self.assertEqual(self.log.read_text().strip(), "^(TestQ|TestX)$")

    def test_no_scripts_is_an_error(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wv.main([str(self.kept), str(self.tree)]), 2)


if __name__ == "__main__":
    unittest.main()
