#!/usr/bin/env python3
"""timeline.py <trajectory.json or run folder> [--limit N]: a compact timeline of one agent run.

Header: requests, the windows with their peaks, sequence length and whether the run compacted. Then every agent
step: step id and timestamp, the first 1500 characters of its reasoning, each tool call with a short form of its
arguments (a patch shows the files it touches) and the size and first line of its result, and the agent's own
message in full. --limit N caps the argument text at N characters (default 260). Standard library only.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import seqlen  # noqa: E402

PATCH_FILES = re.compile(r"\*\*\* (?:Update|Add|Delete) File: (\S+)")


def text(x):
    return x if isinstance(x, str) else json.dumps(x)


def lines_of(path, limit=260):
    tp = os.path.join(path, "trajectory.json") if os.path.isdir(path) else path
    info = seqlen.read_trajectory(tp)
    peaks = seqlen.window_peaks(info["calls"])
    out = [f"requests {len(info['calls'])} | windows {len(peaks)} {[f'{p:,}' for p in peaks]} | "
           f"sequence length {sum(peaks):,} | compacted {seqlen.yn(len(peaks) > 1 if peaks else None)}"
           + (f" | platform {seqlen.as_int(info.get('platform_seqlen')):,}"
              if seqlen.as_int(info.get("platform_seqlen")) is not None else "")]
    n = 0
    for s in info["trajectory"].get("steps") or []:
        if s.get("source") != "agent":
            continue
        out.append(f"{'=' * 30} STEP {s.get('step_id')} {s.get('timestamp')}")
        out.append("REASONING: " + (s.get("reasoning_content") or "")[:1500])
        results = {r.get("source_call_id") or r.get("tool_call_id"): r.get("content")
                   for r in (s.get("observation") or {}).get("results") or []}
        for c in s.get("tool_calls") or []:
            n += 1
            a = text(c.get("arguments"))
            files = PATCH_FILES.findall(a)
            short = (("PATCH " + ", ".join(files)) if files else a).replace("\n", " ; ")[:limit]
            res = results.get(c.get("tool_call_id"))
            res = text(res) if res is not None else ""
            out.append(f"[{n}] {c.get('function_name')}: {short}")
            out.append(f"      -> {len(res)} chars: {res[:140].replace(chr(10), ' ; ')}")
        out.append("MESSAGE: " + text(s.get("message") if s.get("message") is not None else ""))
    return out


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else list(argv)
    limit = 260
    if "--limit" in argv:
        i = argv.index("--limit")
        try:
            limit = int(argv[i + 1])
        except (IndexError, ValueError):
            limit = 260
        del argv[i:i + 2]
    paths = [a for a in argv if not a.startswith("-")]
    if not paths or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    for path in paths:
        try:
            for line in lines_of(path, limit):
                print(line)
        except Exception as e:  # a bad input is reported, not raised
            print(f"{path}: error: {type(e).__name__}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
