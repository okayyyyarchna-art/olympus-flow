import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools/summarize.py"
spec = importlib.util.spec_from_file_location("summarize", SCRIPT)
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


def clean_reports(tag="r1"):
    score = {"score": 3, "max_score": 3, "level": "Fully Met", "reasoning": "all promises traced"}
    sq = {"verdict": "PASS", "solution_comprehensiveness": copy.deepcopy(score),
          "code_quality": copy.deepcopy(score), "issues": [], "promises": ["handle input"],
          "branchInventory": [], "exitAfterMutation": [],
          "modeFailureMatrix": [{k: "trace" for k in ("mode", "success", "errorBeforeHandle", "errorAfter", "timeout", "cancel")}],
          "breakAttempts": [{k: "trace" for k in ("promise", "scenario", "trace", "result", "why")}],
          "summary": "clean", "overall_feedback": "clean"}
    return {
        f"fairness-{tag}.json": {"verdict": "PASS", "taskSummary": "handle input", "overall": "clean", "requirements": [
            {"requirement": "handles input", "sourceQuote": "handle input", "covered": "yes", "coveringTests": ["test"]}],
            "tests": [{"name": "test", "verifies": "handles input", "fairness": "Prompt-stated", "concerns": [], "evidence": "handle input"}],
            "coverageSuggestions": [], "unfairTestCount": 0},
        f"sq-{tag}a.json": copy.deepcopy(sq), f"sq-{tag}b.json": copy.deepcopy(sq),
        f"dq-{tag}.json": {"verdict": "PASS", "comments": [], "requirementCount": {"count": 1, "blocking": False},
            "requirements": ["handle input"], "verdictBasis": {"majors": 0, "minors": 0}, "summary": "clean",
            "taskCriteria": [{"id": f"{i:02}", "verdict": "PASS", "note": "checked"} for i in range(1, 9)],
            "prechecks": {"ascii": True, "noUrls": True, "words": 20, "categorySuggested": "bugfix"}},
        f"ar-{tag}.json": {"description": {"band": 3, "confidence": "high", "reasoning": "clean"},
                          "tests": {"band": 3, "confidence": "high", "reasoning": "clean"},
                          "solution": {"band": 3, "confidence": "high", "reasoning": "clean"},
                          "outcome": "approved", "issues": [], "summary": "clean", "authorGuidance": "clean"},
        f"verify-{tag}.json": {"kept": {k: 0 for k in summary.KEPT}, "verdicts": [],
                              "bandsAfterVerification": {"description": 3, "tests": 3, "solution": 3}, "summary": "clean"},
    }


def issue(title, severity="medium"):
    return {"title": title, "severity": severity, "criterion": "comprehensiveness",
            "evidence": "handle input", "failingCase": "input is lost", "detail": "input lost", "disproofTried": "trace checked"}


class Checkpoints(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.reports = clean_reports()
        self.manifest = summary.declaration("r1")
        self.write()

    def write(self):
        for name, value in self.reports.items():
            (self.folder / name).write_text(json.dumps(value), encoding="utf-8")

    def test_complete_clean_checkpoint_passes(self):
        self.assertEqual(summary.gate(self.folder, self.manifest), ([], []))

    def test_each_required_report_missing_empty_malformed_or_incomplete_fails(self):
        for name in self.reports:
            path = self.folder / name
            for value in (None, "", "not json", "{}", "[]", '{"verdict":"PASS"}',
                          '{"verdict":"FAIL","verdict":"PASS"}'):
                with self.subTest(report=name, value=value):
                    self.write()
                    if value is None:
                        path.unlink()
                    else:
                        path.write_text(value)
                    with self.assertRaises((ValueError, OSError)):
                        summary.gate(self.folder, self.manifest)

    def test_declared_checkpoint_cannot_omit_a_required_check_or_reuse_a_sample(self):
        partial = {"checkpoint": "r1", "reports": [r for r in self.manifest["reports"] if r["kind"] == "dq"]}
        with self.assertRaises(ValueError):
            summary.gate(self.folder, partial)
        same = copy.deepcopy(self.manifest)
        same["reports"][2]["file"] = same["reports"][1]["file"]
        with self.assertRaises(ValueError):
            summary.gate(self.folder, same)

    def test_all_severities_require_source_specific_dispositions(self):
        for severity in ("high", "medium", "low"):
            self.reports = clean_reports()
            self.reports["sq-r1a.json"]["issues"] = [issue("lost input", severity)]
            self.write()
            problems, union = summary.gate(self.folder, self.manifest)
            self.assertIn(("sq-r1a", "lost input"), union)
            self.assertTrue(any("unresolved" in p for p in problems))
            self.reports["verify-r1.json"]["verdicts"] = [{
                "source": "sq-r1a", "id": "lost input", "severity": severity, "decision": "KEEP", "evidence": "trace"}]
            self.write()
            self.assertTrue(summary.gate(self.folder, self.manifest)[0])
            self.reports["verify-r1.json"]["verdicts"][0].update(decision="DROP", dropReason="code", evidence="line 20 handles it")
            self.write()
            self.assertFalse(summary.gate(self.folder, self.manifest)[0])

    def test_kept_medium_or_unknown_or_duplicate_dispositions_block(self):
        self.reports["verify-r1.json"]["kept"]["solution_medium"] = 1
        self.write()
        self.assertTrue(summary.gate(self.folder, self.manifest)[0])
        self.reports = clean_reports()
        self.reports["verify-r1.json"]["verdicts"] = [{
            "source": "sq-r1a", "id": "unknown", "severity": "medium", "decision": "DROP", "dropReason": "scope", "evidence": "quote"}]
        self.write()
        with self.assertRaises(ValueError):
            summary.gate(self.folder, self.manifest)

    def test_sq_union_preserves_findings_and_all_source_ids(self):
        self.reports["sq-r1a.json"]["issues"] = [issue("first"), issue("shared")]
        self.reports["sq-r1b.json"]["issues"] = [issue("second"), issue("shared")]
        self.write()
        merged = summary.merge_sq(self.folder, "r1")
        self.assertEqual({i["title"] for i in merged["issues"]}, {"first", "second", "shared"})
        shared = next(i for i in merged["issues"] if i["title"] == "shared")
        self.assertEqual({s["source"] for s in shared["sources"]}, {"sq-r1a", "sq-r1b"})
        self.assertEqual([s["id"] for s in shared["sources"]], ["shared", "shared"])
        self.assertEqual(len(merged["sourceReports"]), 2)

    def test_partial_dq_only_exits_nonzero(self):
        for name in self.reports:
            if not name.startswith("dq-"):
                (self.folder / name).unlink()
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.folder), "r1"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("GATE FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
