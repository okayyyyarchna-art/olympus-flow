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

    def test_round_override_cannot_raise_profile_capacity(self):
        self.mock_lanes()
        capacity = self.root / "capacity"
        path = self.skill / "tools/machine.py"
        with path.open("a") as f:
            f.write(f'''\n_original_limit = slot_limit
def slot_limit(limit, override=None):
    value = _original_limit(limit, override)
    open({capacity.as_posix()!r}, 'w').write(str(value))
    return value
''')
        for override, expected in (("999", "2"), ("1", "1")):
            result = self.run_tool("round.sh", self.task, "r1", "--check", "sq-a", ROUND_SLOTS=override)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(capacity.read_text(), expected)
        result = self.run_tool("round.sh", self.task, "r1", "--check", "sq-a", ROUND_SLOTS="-1")
        self.assertEqual(result.returncode, 2)

    def test_round_gate_propagates_real_summary_failure(self):
        self.mock_lanes()
        shutil.copy(ROOT / "tools/summarize.py", self.skill / "tools/summarize.py")
        result = self.run_tool("round.sh", self.task, "r1", "--check", "gate")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("GATE FAIL", result.stdout)
        self.assertFalse((self.task / "calls").exists())

    def test_complete_round_passes_with_both_samples_and_union(self):
        from test_summarize import clean_reports
        import json
        fixture = self.root / "reports.json"
        fixture.write_text(json.dumps(clean_reports()))
        shutil.copy(ROOT / "tools/summarize.py", self.skill / "tools/summarize.py")
        (self.skill / "tools/replica.sh").write_text('''[ "${4:-}" != --validate-only ] || exit 0
mkdir -p "$1/eval/replica"
python -c 'import json,sys,pathlib; name=sys.argv[2]+"-"+sys.argv[3]+".json"; data=json.load(open(sys.argv[4])); pathlib.Path(sys.argv[1],"eval/replica",name).write_text(json.dumps(data[name]))' "$1" "$2" "$3" "$MOCK_REPORTS"
''')
        result = self.run_tool("round.sh", self.task, "r1", MOCK_REPORTS=fixture.as_posix())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GATE PASS", result.stdout)
        union = json.loads((self.task / "eval/replica/sq-r1.json").read_text())
        self.assertEqual({s["source"] for s in union["sourceReports"]}, {"sq-r1a", "sq-r1b"})

    def mock_round_reports(self, tags):
        from test_summarize import clean_reports
        import json
        fixture = self.root / "reports.json"
        merged = {}
        for tag in tags:
            merged.update(clean_reports(tag))
        fixture.write_text(json.dumps(merged))
        shutil.copy(ROOT / "tools/summarize.py", self.skill / "tools/summarize.py")
        (self.skill / "tools/replica.sh").write_text('''[ "${4:-}" != --validate-only ] || exit 0
mkdir -p "$1/eval/replica"
python -c 'import json,sys,pathlib; name=sys.argv[2]+"-"+sys.argv[3]+".json"; data=json.load(open(sys.argv[4])); pathlib.Path(sys.argv[1],"eval/replica",name).write_text(json.dumps(data[name]))' "$1" "$2" "$3" "$MOCK_REPORTS"
''')
        pkg = self.task / "pkg"
        pkg.mkdir(exist_ok=True)
        for name in ("description.md", "solution.patch", "test.patch"):
            (pkg / name).write_text(name + " v1\n")
        return fixture.as_posix(), pkg

    def test_test_only_round_reuses_sq_and_dq_of_the_same_bytes(self):
        fixture, pkg = self.mock_round_reports(["r1", "r2"])
        self.assertEqual(self.run_tool("round.sh", self.task, "r1", MOCK_REPORTS=fixture).returncode, 0)
        (pkg / "test.patch").write_text("test.patch v2\n")
        result = self.run_tool("round.sh", self.task, "r2", "fairness", "ar", MOCK_REPORTS=fixture)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("reusing sq reports of round r1", result.stdout)
        self.assertIn("reusing dq reports of round r1", result.stdout)
        self.assertIn("GATE PASS", result.stdout)

    def test_round_without_usable_reports_stops_before_running(self):
        fixture, pkg = self.mock_round_reports(["r1", "r2"])
        self.assertEqual(self.run_tool("round.sh", self.task, "r1", MOCK_REPORTS=fixture).returncode, 0)
        (pkg / "solution.patch").write_text("solution.patch v2\n")
        result = self.run_tool("round.sh", self.task, "r2", "fairness", "ar", MOCK_REPORTS=fixture)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("no reports to use for: sq dq", result.stderr)
        self.assertFalse((self.task / "eval/replica/fairness-r2.json").exists())

    def test_claude_child_exit_and_fresh_report_are_both_required(self):
        shutil.copy(ROOT / "tools/lib/claude2_run.sh", self.skill / "tools/lib/claude2_run.sh")
        config = self.skill / "tools/machine.sh"
        with config.open("a") as f:
            f.write('''OLYMPUS_OS=linux
OLYMPUS_CLAUDE2_CONFIG_DIR="$OLYMPUS_TOOLS/config"
OLYMPUS_CLAUDE_CONFIG_DIR="$OLYMPUS_TOOLS/config"
OLYMPUS_MEMORY_DIR="$OLYMPUS_TOOLS/memory"
OLYMPUS_COORDINATOR_ROOT="$OLYMPUS_TOOLS"
OLYMPUS_CLAUDE_BIN="$OLYMPUS_TOOLS/fake-model.sh"
machine_host() { printf '%s\\n' "$1"; }
machine_config() { printf '%s\\n' "$1"; }
''')
        model = self.skill / "tools/fake-model.sh"
        model.write_text('''#!/usr/bin/env bash
mkdir -p "$MOCK_TASK/eval/claude2"
[ "${MOCK_NO_REPORT:-}" = yes ] || echo result > "$MOCK_TASK/eval/claude2/pkg-ar.md"
exit "${MOCK_EXIT:-0}"
''')
        model.chmod(0o755)
        brief = self.task / "brief.md"
        brief.write_text("offline fixture")
        for code, missing, expected in (("0", "no", 0), ("7", "no", 1), ("0", "yes", 1)):
            result = self.run_tool("lib/claude2_run.sh", "ar", self.task, "pkg", brief, "high",
                                   MOCK_TASK=self.task.as_posix(), MOCK_EXIT=code, MOCK_NO_REPORT=missing)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
