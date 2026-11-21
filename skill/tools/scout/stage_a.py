#!/usr/bin/env python3
"""stage_a.py <trajectory.json or run folder>...: harness fingerprint of hosted runs, from their ATIF trajectories.

Per run: date, run label, first-request input tokens, visible prompt tokens (every non-agent message: system,
AGENTS.md, task description), the hidden part (first request minus visible: the harness's own instructions and tool
schemas), requests, sequence length, output and reasoning tokens per request, reasoning share, minutes, and the
windows with their peaks. Then the tool set per run, the distinct argument-name sets per tool, the tool-output
header, the system message head and the number of skills the harness listed.

When to run it: before any local stand-in solve, to compare the local harness (scout/local_sessions.py) with the
hosted one; after every rollout, to record the hidden-part size and the reasoning per request, so a platform change
(new harness build, model or effort) shows at once. Tokens: tiktoken o200k_base when installed, else an estimate of
4 characters per token (the first output line says which). Standard library otherwise; always exits 0.
"""
import collections
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import seqlen  # noqa: E402


def ts(x):
    return datetime.fromisoformat(str(x).replace("Z", "+00:00"))


def label(path):
    """zip/Orion_Orion_4 for .../zip/Orion_Orion_4 or .../zip/Orion_Orion_4/trajectory.json."""
    parts = [p for p in os.path.normpath(path).replace("\\", "/").split("/") if p]
    if parts and parts[-1].lower().endswith(".json"):
        parts = parts[:-1]
    return "/".join(parts[-2:])


def trajectory_path(path):
    return os.path.join(path, "trajectory.json") if os.path.isdir(path) else path


def fingerprint(path, count):
    info = seqlen.read_trajectory(trajectory_path(path))
    steps = info["trajectory"].get("steps") or []
    calls = info["calls"]
    visible = sum(count(s.get("message") if isinstance(s.get("message"), str) else json.dumps(s.get("message")))
                  for s in steps if s.get("source") != "agent")
    first = calls[0]["input"] if calls else None
    tools, argkeys, header = collections.Counter(), collections.defaultdict(set), ""
    for s in steps:
        if s.get("source") != "agent":
            continue
        for c in s.get("tool_calls") or []:
            name = c.get("function_name")
            tools[name] += 1
            a = c.get("arguments")
            if isinstance(a, dict):
                argkeys[name].update(a.keys())
        if not header:
            for r in (s.get("observation") or {}).get("results") or []:
                content = r.get("content")
                if isinstance(content, str) and content.startswith("Chunk ID"):
                    header = re.sub(r"[0-9a-f]{6}", "xxxxxx", content.split("Output:")[0]).replace("\n", " | ")[:160]
                    break
    peaks = seqlen.window_peaks(calls)
    out = info.get("output_total") or sum(c["output"] for c in calls)
    rea = info.get("reasoning_total") or sum(c.get("reasoning") or 0 for c in calls)
    n = len(calls)
    stamps = [s.get("timestamp") for s in steps if s.get("timestamp")]
    try:
        minutes = (ts(stamps[-1]) - ts(stamps[0])).total_seconds() / 60 if len(stamps) > 1 else 0
    except ValueError:
        minutes = 0
    system = next((s.get("message") for s in steps
                   if s.get("source") == "system" and isinstance(s.get("message"), str)), "") or ""
    return {"run": label(path), "date": str(stamps[0])[:16] if stamps else "?", "first": first, "visible": visible,
            "hidden": (first - visible) if first else None, "requests": n, "windows": peaks,
            "seqlen": sum(peaks) or seqlen.as_int(info.get("platform_seqlen")) or 0,
            "out_req": out / n if n else 0, "rea_req": rea / n if n else 0, "rea_pct": 100 * rea / max(out, 1),
            "minutes": minutes, "tools": dict(tools), "argkeys": {k: sorted(v) for k, v in argkeys.items()},
            "header": header, "system_head": system[:220].replace("\n", " | "),
            "skills": len(re.findall(r"^- [\w.-]+:", system, flags=re.M))}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else argv
    paths = seqlen.expand([a for a in argv if not a.startswith("-")])
    if not paths or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    count, note = seqlen.token_counter()
    rows, errors = [], []
    for path in paths:
        try:
            rows.append(fingerprint(path, count))
        except Exception as e:  # one bad input must not stop the batch
            errors.append(f"{label(path)}: {type(e).__name__}: {e}")
    rows.sort(key=lambda r: r["date"])
    print(note)
    print(f"{'date':16} {'run':38} {'first':>6} {'visible':>7} {'hidden':>6} {'reqs':>4} {'seqlen':>7} {'out/req':>7} "
          f"{'rea/req':>7} {'rea%':>4} {'min':>4} windows")
    for r in rows:
        print(f"{r['date']:16} {r['run'][-38:]:38} {str(r['first']):>6} {r['visible']:>7} {str(r['hidden']):>6} "
              f"{r['requests']:>4} {r['seqlen']:>7} {r['out_req']:>7.0f} {r['rea_req']:>7.0f} {r['rea_pct']:>4.0f} "
              f"{r['minutes']:>4.0f} {r['windows']}")
    for e in errors:
        print(f"error: {e}")
    if not rows:
        return 0
    print()
    print("tool sets per run:")
    for r in rows:
        print(f"  {r['run']}: {r['tools']}")
    print()
    seen = {}
    for r in rows:
        seen.setdefault(json.dumps(r["argkeys"], sort_keys=True), []).append(r["run"])
    print("argument names per tool (distinct sets):")
    for key, runs in seen.items():
        print(f"  {key}  <- {', '.join(runs)}")
    print()
    print("tool output header (first seen):", rows[0]["header"] or "-")
    print("distinct headers:", len({r["header"] for r in rows}))
    print("system message head:", rows[0]["system_head"] or "-")
    print("skills listed per run:", [r["skills"] for r in rows])
    print("hidden part per run:", [r["hidden"] for r in rows], "(one value across runs = same harness build)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
