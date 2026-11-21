import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("mutants", Path(__file__).parents[1] / "tools/mutants.py")
mut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mut)

SOURCE = """package pkg

type Kind string

type Node struct{ N int }

type Pair struct {
\tHead        *Node
\tBase        *Node
\tName        string
\tVersion     string
\tChange      Kind
\tEntryChange Kind
}

func f(x, y int, p *Pair) bool {
\tif x > 1 && y > 2 || x == 0 {
\t\treturn true
\t}
\tp.Change = p.EntryChange
\tswitch {
\tcase x == 7:
\t\treturn p.Head.N > 0
\t}
\treturn false
}

func g(p *Pair) *Node {
\treturn p.Head
}
"""


def patch_adding(name, text):
    lines = text.split("\n")[:-1]
    return (f"diff --git a/{name} b/{name}\n--- /dev/null\n+++ b/{name}\n@@ -0,0 +1,{len(lines)} @@\n"
            + "".join("+" + line + "\n" for line in lines))


class Mutants(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tree = self.root / "tree"
        (self.tree / "pkg").mkdir(parents=True)
        (self.tree / "go.mod").write_text("module example.com/m\n\ngo 1.22\n")
        (self.tree / "pkg/a.go").write_bytes(SOURCE.encode())
        self.patch = self.root / "solution.patch"
        self.patch.write_text(patch_adding("pkg/a.go", SOURCE) + patch_adding("pkg/a_test.go", "package pkg\n")
                              + patch_adding("README.md", "notes\n"), newline="\n")
        self.tests = self.root / "test.patch"
        self.tests.write_text(patch_adding("pkg/a_test.go", "package pkg\n"), newline="\n")
        self.out = self.root / "mutants.json"

    def gen(self, *extra):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mut.main(["gen", str(self.patch), str(self.tree), str(self.out), *extra]), 0)
        return json.loads(self.out.read_text()), out.getvalue()

    def test_added_lines_module_and_operators(self):
        self.assertEqual(mut.added_lines(self.patch), {"pkg/a.go": set(range(1, 31))})
        self.assertEqual(mut.module_path(self.tree), "example.com/m")
        mutants, out = self.gen()
        self.assertIn("mutants: 17 from 30 added lines in 1 files; del 1, drop 4, false 2, flip 2, neg 2, swap 4, true 2", out)
        news = {(m["line"], m["op"], m["new"].strip()) for m in mutants}
        for expected in [(17, "neg", "if !(x > 1 && y > 2 || x == 0) {"), (17, "drop", "if x == 0 {"),
                         (17, "drop", "if x > 1 && y > 2 {"), (17, "drop", "if y > 2 || x == 0 {"),
                         (17, "drop", "if x > 1 || x == 0 {"), (17, "true", "if true {"), (17, "false", "if false {"),
                         (18, "flip", "return false"), (25, "flip", "return true"),
                         (20, "del", "// mutant: line deleted"), (20, "swap", "p.EntryChange = p.EntryChange"),
                         (20, "swap", "p.Change = p.Change"), (22, "neg", "case !(x == 7):"), (22, "true", "case true:"),
                         (22, "false", "case false:"), (23, "swap", "return p.Base.N > 0"), (29, "swap", "return p.Base")]:
            self.assertIn(expected, news)
        self.assertEqual([m["id"] for m in mutants], list(range(17)))
        self.assertTrue(all(m["covered"] is None for m in mutants))
        self.assertEqual(mutants[0]["orig"], "\tif x > 1 && y > 2 || x == 0 {")

    def test_cover_profile_marks_lines_a_test_ran(self):
        profile = self.root / "cover.out"
        profile.write_text("mode: set\nexample.com/m/pkg/a.go:17.2,19.3 2 1\nexample.com/m/pkg/a.go:20.2,25.14 3 0\n"
                           "other.org/x/y.go:17.1,18.2 1 1\n")
        mutants, out = self.gen("--cover", str(profile))
        covered = {m["line"] for m in mutants if m["covered"]}
        self.assertEqual(covered, {17, 18})
        self.assertIn("covered (a test ran the line): 8; not run: 9", out)

    def test_run_classes_each_mutant_restores_the_copy_and_shards(self):
        mutants, _ = self.gen()
        calls = []
        def fake(cmd, cwd, **kwargs):
            calls.append(cmd)
            text = (Path(cwd) / "pkg/a.go").read_text()
            self.assertEqual(text.count("\n"), SOURCE.count("\n"))
            if "if false {" in text:
                return subprocess.CompletedProcess(cmd, 0, "ok  \texample.com/m/pkg\t0.1s\n", "")
            if "if true {" in text:
                raise subprocess.TimeoutExpired(cmd, 1)
            if "p.Change = p.Change" in text:
                return subprocess.CompletedProcess(cmd, 1, "# example.com/m/pkg\npkg/a.go:20:2: x\nFAIL\tpkg [build failed]\n", "")
            return subprocess.CompletedProcess(cmd, 1, "=== RUN TestX\n--- FAIL: TestX (0.00s)\nFAIL\n", "")
        out_path = self.root / "shard.jsonl"
        with patch.object(mut.subprocess, "run", side_effect=fake), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(mut.main(["run", str(self.out), str(self.tree), str(self.tests), str(out_path),
                                       "--run", "Prs9$", "--timeout", "30"]), 0)
        rows = [json.loads(line) for line in out_path.read_text().splitlines()]
        self.assertEqual(len(rows), 17)
        results = {r["result"] for r in rows}
        self.assertEqual(results, {"killed", "survived", "invalid", "timeout"})
        self.assertEqual(sum(r["result"] == "killed" for r in rows), 14)
        self.assertEqual([r["failed"] for r in rows if r["result"] == "killed"][0], ["TestX"])
        self.assertEqual(calls[0][:6], ["go", "test", "-count=1", "-failfast", "-timeout", "30s"])
        self.assertEqual(calls[0][6:], ["-run", "Prs9$", "./pkg/"])
        survivors = (self.root / "shard-survivors.txt").read_text()
        self.assertIn("\tpkg/a.go:17\tfalse\tcovered=None\tif false {\n", survivors)
        self.assertIn("killed 14, survived 1, timeout 1", out.getvalue())
        self.assertEqual((self.tree / "pkg/a.go").read_bytes(), SOURCE.encode())  # the tree itself is untouched
        # a mutant whose line the tree no longer has is stale and runs nothing; shard 1/2 takes the odd ids
        mutants[3]["orig"] = "gone"
        self.out.write_text(json.dumps(mutants))
        calls.clear()
        with patch.object(mut.subprocess, "run", side_effect=fake), contextlib.redirect_stdout(io.StringIO()):
            mut.main(["run", str(self.out), str(self.tree), str(self.tests), str(out_path), "--run", "X", "--shard", "1/2"])
        rows = [json.loads(line) for line in out_path.read_text().splitlines()]
        self.assertEqual([r["id"] for r in rows], list(range(1, 17, 2)))
        self.assertEqual([r["result"] for r in rows if r["id"] == 3], ["stale"])
        self.assertEqual(len(calls), 7)

    def test_run_needs_test_files_in_the_tests_patch(self):
        self.gen()
        no_tests = self.root / "readme.patch"
        no_tests.write_text(patch_adding("README.md", "notes\n"), newline="\n")
        with self.assertRaises(ValueError):
            mut.main(["run", str(self.out), str(self.tree), str(no_tests), str(self.root / "x.jsonl"), "--run", "X"])


if __name__ == "__main__":
    unittest.main()
