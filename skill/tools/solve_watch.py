#!/usr/bin/env python3
"""Solver watcher (user rule 2026-11-06): a local solve may use only its own clone, the task text and the repo.

usage: python solve_watch.py <task-dir>
Reads every solves/s<n>/meta.txt, finds the solver's own transcript (Claude Code: ~/.claude/projects and the claude2
config dir, keyed by the clone path; Codex: ~/.codex/sessions rollouts whose cwd is the clone) and checks every tool
call. A call that names the task folder, the hidden tests or reference, memory, the olympus skills, the agents, the
shipd/claude-code workspaces or another solver's clone makes the solve SUSPICIOUS. Prints one verdict per solve and
writes <task-dir>/solves/watch.md. Grade and calibrate only CLEAN solves.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
CLAUDE_DIRS = [HOME / ".claude" / "projects", HOME / ".claude-cli" / "projects"]
CODEX_SESSIONS = HOME / ".codex" / "sessions"


def norm(s):
    return s.replace("\\\\", "\\").replace("/", "\\").lower()


def forbidden_patterns(task_dir):
    t = norm(str(task_dir))
    return [t, r"oss\claude-code", r"oss\shipd", r".claude\projects", r".claude\skills\olympus",
            r".claude\agents", r".claude-cli\projects", r".codex\skills", r".codex\memories", r".codex\olympus"]


def claude_transcripts(clone):
    key = re.sub(r"[:\\/]", "-", str(Path(clone)))
    out = []
    for d in CLAUDE_DIRS:
        for cand in (key, key.replace("c--", "C--", 1)):
            out += glob.glob(str(d / cand / "*.jsonl"))
    return sorted(set(out))


def claude_calls(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        content = (d.get("message") or {}).get("content")
        if isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_use":
                    yield c.get("name", "?"), json.dumps(c.get("input", {}))


def codex_rollouts(clone):
    want = norm(str(Path(clone)))
    out = []
    for f in glob.glob(str(CODEX_SESSIONS / "**" / "rollout-*.jsonl"), recursive=True):
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                first = json.loads(fh.readline())
        except (ValueError, OSError):
            continue
        cwd = norm((first.get("payload") or {}).get("cwd", ""))
        if cwd and cwd.rstrip("\\") == want.rstrip("\\"):
            out.append(f)
    return out


def codex_calls(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        p = d.get("payload") or {}
        if p.get("type") in ("function_call", "custom_tool_call", "local_shell_call"):
            yield p.get("name", p.get("type")), json.dumps(p.get("arguments") or p.get("input") or p.get("action") or {})


def main():
    task = Path(sys.argv[1]).resolve()
    bad = forbidden_patterns(task)
    lines = ["# Solver watch", "", "| solve | transcripts | tool calls | verdict | first hits |", "|---|---|---|---|---|"]
    for meta in sorted(glob.glob(str(task / "solves" / "s*" / "meta.txt"))):
        m = re.search(r"clone=(\S+)", Path(meta).read_text(encoding="utf-8", errors="replace"))
        if not m:
            continue
        clone = m.group(1)
        if clone.startswith("/") and len(clone) > 2 and clone[2] == "/":  # /c/Users -> C:\Users
            clone = clone[1].upper() + ":" + clone[2:]
        clone_n = norm(clone)
        own_top = norm(str(Path(clone).parent))
        others = [norm(c) + "\\" for c in glob.glob(str(HOME / "vp-*")) if norm(c) != own_top]
        files = claude_transcripts(clone) + codex_rollouts(clone)
        calls, hits = 0, []
        for f in files:
            gen = claude_calls(f) if f.endswith(".jsonl") and "projects" in f else codex_calls(f)
            for name, inp in gen:
                calls += 1
                s = norm(inp)
                if any(b in s for b in bad) or any(o in s for o in others):
                    hits.append(f"{name}: {inp[:140]}")
        verdict = "NO TRANSCRIPT" if not files else ("SUSPICIOUS" if hits else "CLEAN")
        solve = Path(meta).parent.name
        lines.append(f"| {solve} | {len(files)} | {calls} | {verdict} | {' / '.join(h.replace('|', '/') for h in hits[:2])} |")
        print(f"{solve}: {verdict} ({len(files)} transcripts, {calls} tool calls, {len(hits)} hits)")
        for h in hits[:5]:
            print("   ", h)
    (task / "solves" / "watch.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
