import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")


class Launchers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "skill"
        shutil.copytree(ROOT / "tools", self.skill / "tools", ignore=shutil.ignore_patterns("__pycache__", ".docker.lock"))
        shutil.copytree(ROOT / "replicas", self.skill / "replicas")
        self.task = self.root / "task"
        self.task.mkdir()
        (self.skill / "tools/machine.sh").write_text('''OLYMPUS_TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLYMPUS_LIB="$OLYMPUS_TOOLS/lib"
PY=python
OLYMPUS_WORK_ROOT="$OLYMPUS_TOOLS/work"
OLYMPUS_REVIEW_LANES=2
OLYMPUS_SEAMS_ROOT="$OLYMPUS_TOOLS/seams"
''', encoding="utf-8")
        self.marker = self.root / "model-called"
        for name in ("codex_job.sh", "claude2_run.sh"):
            (self.skill / "tools/lib" / name).write_text(f'touch "{self.marker.as_posix()}"\nexit 91\n')

    def run_tool(self, name, *args, **env):
        # Git Bash accepts forward-slash Windows paths as arguments.
        return subprocess.run([BASH, str(self.skill / "tools" / name), *map(str, args)],
                              capture_output=True, text=True, env={**os.environ, **env}, timeout=15)

    def test_every_replica_prompt_and_catalog_is_validated_before_launch(self):
        for check, kb in (("sq", "solution"), ("fairness", "tests"), ("dq", "description"),
                          ("ar", "solution"), ("verify", "tests"), ("ref-audit", "solution"),
                          ("fp-audit", "tests")):
            for resource in ("common.md", f"{check}.md", f"knowledge/{kb}.md"):
                with self.subTest(check=check, resource=resource):
                    path = self.skill / "replicas" / resource
                    saved = path.read_bytes()
                    path.unlink()
                    result = self.run_tool("replica.sh", self.task, check, "r1")
                    path.write_bytes(saved)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn(resource, result.stderr)
                    self.assertFalse(self.marker.exists())

    def test_aggregate_preflight_does_not_start_partial_jobs(self):
        for tool, resource, args in (("round.sh", "knowledge/description.md", ("r1",)),
                                     ("sweep.sh", "sweep-brief.md", ("s1",))):
            path = self.skill / "replicas" / resource
            saved = path.read_bytes()
            path.write_text("")
            result = self.run_tool(tool, self.task, *args)
            path.write_bytes(saved)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn(resource, result.stderr)
            self.assertFalse(self.marker.exists())

    def mock_lanes(self):
        (self.skill / "tools/lib/check_codex_brief.sh").write_text("exit 0\n")
        (self.skill / "tools/replica.sh").write_text('''[ "${4:-}" != --validate-only ] || exit 0
mkdir -p "$1/eval/replica"
echo "$2-$3" >> "$1/calls"
sleep 0.05
[ "${MOCK_NO_REPORT:-}" != "$2-$3" ] || exit 0
echo '{}' > "$1/eval/replica/$2-$3.json"
[ "${MOCK_FAIL:-}" != "$2-$3" ] || exit 7
''')
        (self.skill / "tools/lib/claude2_run.sh").write_text('''mkdir -p "$2/eval/claude2"
echo "$1" >> "$2/calls"
sleep 0.05
[ "${MOCK_NO_REPORT:-}" != "$1" ] || exit 0
echo 'Verdict: PASS' > "$2/eval/claude2/$3-$1-$C2_SUFFIX.md"
[ "${MOCK_FAIL:-}" != "$1" ] || exit 7
''')
        (self.skill / "tools/summarize.py").write_text("print('GATE PASS')\n")

    def test_single_lane_blocks_and_writes_only_its_report(self):
        self.mock_lanes()
        result = self.run_tool("sweep.sh", self.task, "s1", "--lane", "ref-a")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.task / "calls").read_text().splitlines(), ["ref-audit-sws1a"])
        self.assertTrue((self.task / "eval/replica/ref-audit-sws1a.json").is_file())
        result = self.run_tool("round.sh", self.task, "r1", "--check", "sq-b")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.task / "eval/replica/sq-r1b.json").is_file())

    def test_aggregate_waits_for_every_lane_and_propagates_errors(self):
        self.mock_lanes()
        for tool, args, expected in (
            ("sweep.sh", ("s1",), ["ar", "sq", "ref-audit-sws1a", "ref-audit-sws1b"]),
            ("round.sh", ("r1",), ["fairness-r1", "sq-r1a", "sq-r1b", "dq-r1", "ar-r1", "verify-r1"]),
        ):
            for kind in ("MOCK_FAIL", "MOCK_NO_REPORT"):
                with self.subTest(tool=tool, kind=kind):
                    (self.task / "calls").unlink(missing_ok=True)
                    result = self.run_tool(tool, self.task, *args, **{kind: expected[0]})
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual((self.task / "calls").read_text().splitlines(), expected)

    def test_no_unwaited_background_launches(self):
        for name in ("sweep.sh", "round.sh", "hunt.sh"):
            source = (ROOT / "tools" / name).read_text()
            self.assertNotRegex(source, r"(?m)&\s*\)?\s*$", name)


if __name__ == "__main__":
    unittest.main()
