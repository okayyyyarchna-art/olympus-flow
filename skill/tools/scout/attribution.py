#!/usr/bin/env python3
"""attribution.py [--areas areas.json] <run folder or trajectory.json>...: how much of each run's context (sequence
length) goes to each requirement area.

Each tool call (its arguments plus the output the agent read) is counted in tokens and given to the areas whose
regex matches the lowered call text (a call naming several areas is split evenly). Test and build runs, planning
(update_plan) and orientation (docs, git status, listing) are their own groups; what is left of the sequence length
after the tool calls is the fixed prompt (first-request input: harness, AGENTS.md, description) and the model's own
reasoning and messages, which the context also carries. areas.json is {"area name": "regex", ...}; the reserved keys
"_build" and "_orient" replace the built-in test/build and orientation regexes. Without --areas there is one area,
"all". Run it before adding a requirement for length (measured on vet task 6: about 20K of context per requirement
that needs a code change, 3-7K for one the reference already meets, tests and builds about 18%, reasoning about
15%). Tokens: tiktoken o200k_base when installed, else 4 characters per token. Standard library otherwise.
"""
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import seqlen  # noqa: E402

BUILD = (r"\bgo (test|vet|build)\b|gofmt|golangci|\bmake\b|\bcargo (test|build|check|clippy)\b|\bpytest\b|"
         r"python3? -m (pytest|unittest)|\bnpm (test|run)\b|\bpnpm (test|run)\b|\byarn (test|run)\b|\bjest\b|"
         r"\bmvn\b|\bgradle\b|dotnet test|\btsc\b")
ORIENT = r"agents\.md|readme|contributing|docs/|git (status|log|diff|show)|\bls\b|rg --files|find \."
GROUP_PLAN = "planning"
GROUP_BUILD = "running tests and builds"
GROUP_ORIENT = "orientation (docs, git, listing)"
GROUP_OTHER = "other reading"
GROUP_PROMPT = "fixed prompt (harness, AGENTS.md, description)"
GROUP_REST = "model reasoning and messages, rest"


def load_areas(path):
    """[(name, compiled regex)], build regex, orient regex from a JSON file; one area "all" without a file."""
    build, orient = BUILD, ORIENT
    if not path:
        return [("all", re.compile("."))], re.compile(build), re.compile(orient)
    spec = seqlen.load_json(path)
    if not isinstance(spec, dict) or not spec:
        raise ValueError("areas.json must be a non-empty object {\"area name\": \"regex\"}")
    build = spec.get("_build", build)
    orient = spec.get("_orient", orient)
    areas = [(name, re.compile(rx)) for name, rx in spec.items() if not name.startswith("_")]
    if not areas:
        raise ValueError("areas.json names no area")
    return areas, re.compile(build), re.compile(orient)


def text(x):
    return x if isinstance(x, str) else json.dumps(x)


def attribute(path, areas, build, orient, count):
    """(sequence length, Counter of tokens per group) of one run."""
    tp = os.path.join(path, "trajectory.json") if os.path.isdir(path) else path
    info = seqlen.read_trajectory(tp)
    calls = info["calls"]
    peaks = seqlen.window_peaks(calls)
    seq = sum(peaks) or seqlen.as_int(info.get("platform_seqlen")) or 0
    first = calls[0]["input"] if calls else 0
    got = collections.Counter()
    for s in info["trajectory"].get("steps") or []:
        if s.get("source") != "agent":
            continue
        res = {r.get("source_call_id") or r.get("tool_call_id"): r.get("content")
               for r in (s.get("observation") or {}).get("results") or []}
        for c in s.get("tool_calls") or []:
            a = text(c.get("arguments"))
            n = count(a) + count(text(res.get(c.get("tool_call_id")) or ""))
            low = a.lower()
            if c.get("function_name") == "update_plan":
                got[GROUP_PLAN] += n
                continue
            if c.get("function_name") == "write_stdin" or (build.search(low) and "begin patch" not in low):
                got[GROUP_BUILD] += n
                continue
            hits = [name for name, rx in areas if rx.search(low)]
            if not hits and orient.search(low):
                got[GROUP_ORIENT] += n
                continue
            if not hits:
                got[GROUP_OTHER] += n
                continue
            for h in hits:
                got[h] += n / len(hits)
    tools = sum(got.values())
    got[GROUP_PROMPT] = first
    got[GROUP_REST] = max(seq - first - tools, 0)
    return seq, got


def label(path):
    parts = [p for p in os.path.normpath(path).replace("\\", "/").split("/") if p]
    if parts and parts[-1].lower().endswith(".json"):
        parts = parts[:-1]
    return "/".join(parts[-3:])


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else list(argv)
    areas_path = None
    if "--areas" in argv:
        i = argv.index("--areas")
        areas_path = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    paths = seqlen.expand([a for a in argv if not a.startswith("-")])
    if not paths or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    try:
        areas, build, orient = load_areas(areas_path)
    except (OSError, ValueError) as e:
        print(f"areas: {type(e).__name__}: {e}")
        return 0
    count, note = seqlen.token_counter()
    print(f"{note}; areas: {', '.join(name for name, _ in areas)}")
    total, nruns = collections.Counter(), 0
    for path in paths:
        try:
            seq, got = attribute(path, areas, build, orient, count)
        except Exception as e:  # one bad input must not stop the batch
            print(f"== {label(path)}: error: {type(e).__name__}: {e}")
            continue
        nruns += 1
        print(f"== {label(path)}: sequence length {seq:,}")
        for k, v in got.most_common():
            print(f"   {v:>8.0f}  {100 * v / seq if seq else 0:5.1f}%  {k}")
        for k, v in got.items():
            total[k] += v / seq if seq else 0
    if nruns:
        print()
        print(f"== average share of sequence length over {nruns} runs")
        for k, v in sorted(total.items(), key=lambda kv: -kv[1]):
            print(f"   {100 * v / nruns:5.1f}%  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
