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


if __name__ == "__main__":
    unittest.main()
