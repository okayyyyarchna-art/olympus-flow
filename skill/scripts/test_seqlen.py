"""Unit tests for tools/seqlen.py and tools/rollout_report.py on tiny synthetic inputs."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import rollout_report  # noqa: E402
import seqlen  # noqa: E402

STAMP = "2026-11-21T00:00:00.000Z"
# (input, output) per request: three windows, each started by a drop of the input below half of the previous one
THREE_WINDOWS = [(10000, 100), (120000, 500), (200000, 400),   # peak 200,400
                 (14000, 100), (90000, 300),                   # peak 90,300
                 (13000, 50), (40000, 200), (60000, 100)]      # peak 60,100
PEAKS = [200400, 90300, 60100]


def codex_log(requests, model="gpt-test", effort="xhigh", window=272000, cwd="/tmp/vp-task-1/work"):
    lines = [json.dumps({"timestamp": STAMP, "type": "session_meta", "payload": {"cwd": cwd}}),
             json.dumps({"timestamp": STAMP, "type": "turn_context", "payload": {"model": model, "effort": effort,
                                                                                 "cwd": cwd}}),
             "not json at all"]
    for inp, out in requests:
        lines.append(json.dumps({"timestamp": STAMP, "type": "event_msg", "payload": {
            "type": "token_count", "info": {"last_token_usage": {"input_tokens": inp, "output_tokens": out,
                                                                 "reasoning_output_tokens": 0},
                                            "model_context_window": window}}}))
        lines.append(json.dumps({"type": "response_item", "payload": {"type": "function_call", "name": "exec_command"}}))
    lines.append(json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": None}}))
    return "\n".join(lines) + "\n"


def trajectory(usage, extra=None, prompt="Task: fix the scan, even if the lockfile is empty"):
    """usage: (window, input, output) per request."""
    per = [{"input_tokens": i, "output_tokens": o, "cached_input_tokens": 0, "window": w} for w, i, o in usage]
    ex = {"per_request_usage": per}
    ex.update(extra or {})
    return {"schema_version": "ATIF-v1", "agent": {"model_name": "<model>"}, "steps": [
        {"step_id": 1, "timestamp": "2026-11-21T00:00:00Z", "source": "system", "message": "<permissions>"},
        {"step_id": 2, "timestamp": "2026-11-21T00:00:01Z", "source": "user", "message": prompt},
        {"step_id": 3, "timestamp": "2026-11-21T00:20:00Z", "source": "agent", "model_name": "gpt-x",
         "message": "done", "reasoning_content": "look first",
         "tool_calls": [{"tool_call_id": "c1", "function_name": "exec_command", "arguments": {"cmd": "go test ./..."}}],
         "observation": {"results": [{"source_call_id": "c1", "content": "ok"}]}}],
        "final_metrics": {"total_completion_tokens": sum(o for _, _, o in usage), "extra": ex}}


def junit(cases):
    """cases: (name, failed) pairs."""
    body = "".join(f'<testcase name="{n}" classname="pkg">{"<failure>x</failure>" if bad else ""}</testcase>'
                   for n, bad in cases)
    return f'<?xml version="1.0"?><testsuites><testsuite name="new">{body}</testsuite></testsuites>'


def write(folder, name, content):
    os.makedirs(folder, exist_ok=True)
    p = os.path.join(folder, name)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(content if isinstance(content, str) else json.dumps(content))
    return p


def zip_run(root, name, usage, verdict, label=None, cases=(), prompt=None):
    d = os.path.join(root, name)
    t = trajectory(usage, **({"prompt": prompt} if prompt else {}))
    write(d, "trajectory.json", t)
    write(d, "eval-result.json", {"verdict": verdict})
    write(d, "run.txt", f"Run: {label}\nRun ID: x\n" if label else "Run ID: x\n")
    if cases:
        write(d, "junit-new.xml", junit(cases))
    return d


class WindowPeaks(unittest.TestCase):
    def test_drop_heuristic_splits_at_half(self):
        self.assertEqual(seqlen.window_peaks([]), [])
        self.assertEqual(seqlen.window_peaks([{"input": 100, "output": 1}, {"input": 51, "output": 0}]), [101])
        self.assertEqual(seqlen.window_peaks([{"input": 100, "output": 1}, {"input": 49, "output": 2}]), [101, 51])

    def test_window_ids_win_over_the_heuristic(self):
        calls = [{"window": 0, "input": 100, "output": 0}, {"window": 0, "input": 20, "output": 0},
                 {"window": 1, "input": 90, "output": 5}]
        self.assertEqual(seqlen.window_peaks(calls), [100, 95])


class CodexLog(unittest.TestCase):
    def test_three_window_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "rollout-2026-11-21T00-00-00-abc.jsonl", codex_log(THREE_WINDOWS))
            r = seqlen.measure(p)
        self.assertIsNone(r["error"])
        self.assertEqual(r["kind"], "codex")
        self.assertEqual(r["requests"], 8)
        self.assertEqual(r["peaks"], PEAKS)
        self.assertEqual(r["seqlen"], sum(PEAKS))
        self.assertTrue(r["compacted"])
        self.assertEqual((r["model"], r["effort"], r["context_window"]), ("gpt-test", "xhigh", 272000))
        line = seqlen.format_record(r)
        self.assertIn("windows 3 [200,400, 90,300, 60,100]", line)
        self.assertIn("seqlen 350,800 (351K)", line)
        self.assertIn("compacted yes", line)
        self.assertIn("context window 272,000 (peak 74%)", line)

    def test_single_window_session_is_not_compacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "rollout-x.jsonl", codex_log([(10000, 10), (150000, 20), (230000, 30)]))
            r = seqlen.measure(p)
        self.assertEqual((r["peaks"], r["seqlen"], r["compacted"]), ([230030], 230030, False))


class Trajectory(unittest.TestCase):
    def test_windows_from_ids_and_platform_agreement(self):
        usage = [(0, 10000, 100), (0, 240000, 500), (1, 12000, 50), (1, 90000, 467)]
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "trajectory.json", trajectory(usage, {"sequence_length": 330967, "compacted": True}))
            r = seqlen.measure(p)
        self.assertEqual(r["kind"], "trajectory")
        self.assertEqual(r["peaks"], [240500, 90467])
        self.assertEqual(r["seqlen"], 330967)
        self.assertTrue(r["compacted"])
        self.assertEqual(r["model"], "gpt-x")  # agent.model_name is the "<model>" placeholder
        line = seqlen.format_record(r)
        self.assertIn("platform 330,967", line)
        self.assertNotIn("differs", line)

    def test_no_per_request_usage_falls_back_to_the_platform_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "trajectory.json", trajectory([], {"sequence_length": 414478}))
            r = seqlen.measure(p)
        self.assertEqual((r["requests"], r["seqlen"], r["compacted"], r["from_platform"]), (0, 414478, None, True))
        self.assertIn("requests 0 (no per-request usage; platform value)", seqlen.format_record(r))

    def test_one_window_and_a_differing_platform_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "trajectory.json", trajectory([(0, 10000, 100), (0, 220000, 200)], {"sequence_length": 220000}))
            r = seqlen.measure(p)
        self.assertEqual((r["peaks"], r["compacted"]), ([220200], False))
        self.assertIn("platform 220,000 (differs)", seqlen.format_record(r))


class RunFolders(unittest.TestCase):
    def test_zip_and_pulled_folders_and_the_passing_mean(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = zip_run(tmp, "Orion_Orion_1", [(0, 10000, 100), (0, 240000, 500), (1, 12000, 50), (1, 90000, 467)],
                        "PASS", label="Orion #3")
            b = zip_run(tmp, "Orion_Orion_2", [(0, 10000, 100), (0, 215000, 300)], "FAIL_MISSED_REQUIREMENT",
                        label="Orion #4")
            c = os.path.join(tmp, "rd7pulledrunid")
            write(c, "output.json", {"sequenceLength": "275000", "compacted": "False", "verdict": "PASS"})
            write(c, "evalResult.json", {"verdict": "PASS_WITH_CAVEATS"})
            write(c, "verdict.txt", "Vega PASS_WITH_CAVEATS\nlabel: Vega #1\n")
            d = zip_run(tmp, "Nova_Nova_1", [(0, 10000, 100), (0, 150000, 300)], "FAIL_REGRESSION")
            records = [seqlen.measure(x) for x in (a, b, c, d)]
        ra, rb, rc, rd = records
        self.assertEqual([r["family"] for r in records], ["Orion", "Orion", "Vega", "Nova"])
        self.assertEqual([r["verdict"] for r in records], ["PASS", "FAIL_MISSED_REQUIREMENT", "PASS_WITH_CAVEATS",
                                                           "FAIL_REGRESSION"])
        self.assertEqual((ra["kind"], ra["seqlen"], ra["compacted"]), ("run", 330967, True))
        self.assertEqual((rb["seqlen"], rb["compacted"]), (215300, False))
        self.assertEqual((rc["kind"], rc["seqlen"], rc["compacted"], rc["from_platform"]), ("pulled", 275000, False, True))
        self.assertIn("requests - (platform values, no trajectory)", seqlen.format_record(rc))
        line = seqlen.summary(records)
        self.assertIn("2 passing of 4 with a verdict", line)
        self.assertIn(f"passing mean {(330967 + 275000) / 2:,.0f}", line)
        self.assertIn("256K bar met, 300K target met", line)
        self.assertIn("256K bar not met", seqlen.summary([rb, rd]))
        self.assertIn("no verdicts; mean over all 1 inputs", seqlen.summary([dict(rb, verdict=None)]))

    def test_bad_inputs_are_lines_not_crashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = os.path.join(tmp, "empty")
            os.makedirs(empty)
            txt = write(tmp, "notes.txt", "x")
            for path in (os.path.join(tmp, "missing"), empty, txt):
                r = seqlen.measure(path)
                self.assertIsNotNone(r["error"], path)
                self.assertIn("error:", seqlen.format_record(r))
            self.assertEqual(seqlen.main([os.path.join(tmp, "missing")]), 0)
        self.assertEqual(seqlen.summary([r]), "summary: no sequence length measured")


class RolloutReport(unittest.TestCase):
    def test_table_shared_failures_and_gate(self):
        cases_ok = [("TestA", False), ("TestShared", False), ("TestC", False)]
        cases_bad = [("TestA", False), ("TestShared", True), ("TestC", True)]
        with tempfile.TemporaryDirectory() as tmp:
            folders = [
                zip_run(tmp, "Orion_Orion_1", [(0, 10000, 100), (0, 240000, 500), (1, 12000, 50), (1, 90000, 467)],
                        "PASS", label="Orion #1", cases=cases_ok),
                zip_run(tmp, "Orion_Orion_2", [(0, 10000, 100), (0, 200000, 300)], "FAIL_MISSED_REQUIREMENT",
                        label="Orion #2", cases=cases_bad),
                zip_run(tmp, "Orion_Orion_3", [(0, 10000, 100), (0, 210000, 300)], "FAIL_MISSED_REQUIREMENT",
                        label="Orion #3", cases=cases_bad, prompt="Task without the sentence"),
                zip_run(tmp, "Orion_Orion_4", [(0, 10000, 100), (0, 190000, 300)], "FAIL_REGRESSION",
                        label="Orion #4", cases=[("TestA", True), ("TestShared", False), ("TestC", False)]),
            ]
            text = "\n".join(rollout_report.report(folders, marker="even if the lockfile is empty"))
        self.assertIn("platform junit", text.splitlines()[0])
        rows = {line.split()[0].split("/")[-1]: line for line in text.splitlines() if "Orion_Orion_" in line}
        self.assertIn(" 0/3 ", rows["Orion_Orion_1"])
        self.assertIn(" 2/3 ", rows["Orion_Orion_2"])
        self.assertIn("330,967", rows["Orion_Orion_1"])
        self.assertTrue(rows["Orion_Orion_1"].rstrip().endswith("yes"))  # marker seen
        self.assertTrue(rows["Orion_Orion_3"].rstrip().endswith("no"))
        self.assertIn("  2  TestShared", text)
        self.assertIn("  2  TestC", text)
        self.assertNotIn("  1  TestA", text)
        self.assertIn("Orion: 4 completed, 1 pass (25%), passing mean seqlen 330,967", text)
        self.assertIn("Orion solves >=1 run and <=25%: met (1 of 4 pass = 25%)", text)
        self.assertIn("Orion passing runs average >=256K: met (mean 330,967 over 1 passing)", text)
        self.assertIn("Nova 0%: not enough runs (0 of 4; 0 of 0 pass so far)", text)
        self.assertIn("Vega <=25%: not enough runs (0 of 4", text)
        self.assertIn(">=4 completed runs per family: Orion met (4), Nova not met (0), Vega not met (0)", text)

    def test_gate_not_met_cases_and_testlog_misses(self):
        with tempfile.TemporaryDirectory() as tmp:
            folders = [zip_run(tmp, f"Orion_Orion_{i}", [(0, 10000, 100), (0, 100000 + i, 100)], "PASS",
                               label=f"Orion #{i}", cases=[("TestA", False)]) for i in range(1, 5)]
            pulled = os.path.join(tmp, "rd7pulled")
            write(pulled, "output.json", {"sequenceLength": 300000, "compacted": True, "verdict": "FAIL_REGRESSION"})
            write(pulled, "verdict.txt", "Nova FAIL_REGRESSION\n")
            write(pulled, "testlog.txt", "--- FAIL: TestX (0.1s)\n    --- FAIL: TestX/sub (0.1s)\nFAILED tests/t.py::test_y - boom\n")
            text = "\n".join(rollout_report.report(folders + [pulled]))
        self.assertIn("Orion solves >=1 run and <=25%: not met (4 of 4 pass = 100% > 25%)", text)
        self.assertIn("Orion passing runs average >=256K: not met (mean 100,", text)
        self.assertIn("junit / testlog", text.splitlines()[0])
        row = next(line for line in text.splitlines() if "rd7pulled" in line)
        self.assertIn(" Nova ", row)
        self.assertIn(" 2 ", row)  # TestX and test_y, subtests not counted twice
        self.assertIn("300,000", row)


if __name__ == "__main__":
    unittest.main()
