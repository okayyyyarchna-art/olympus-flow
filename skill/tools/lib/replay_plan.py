#!/usr/bin/env python3
"""Plan a delta replay: which platform runs need a replay after a test.patch change (rollout.md step 2).

usage: python replay_plan.py <old-test.patch> <new-test.patch> <runs-dir> [--stage <dir>] [--skip-lines]
  <runs-dir>  pull.sh --runs layout: <run>/verdict.txt, <run>/solution.patch, <run>/testlog.txt
  --stage     copy the solution.patch of every REPLAY run to <dir>/<run>.patch (input for replay_patches.sh)
  --skip-lines  treat LINE? as SKIP (only when no changed fixture is read at or before the failing line)

The build is the slow part of a replay, so the saving is in the runs that need none:
  SKIP     the run failed, and every failure location is in a test file the change did not touch: same result.
  LINE?    a failure is in a changed file, but the first changed line (comments ignored) comes after it: the runner
           stops at its first failing line, so the result holds unless a changed fixture is read earlier.
  REPLAY   the run passed, a failure is at or after a changed line, or no failure location was found.
"""
import re
import shutil
import sys
from pathlib import Path


def files(patch_text):
    """{path: (added lines, whole section)} per file of a unified diff."""
    out, cur, added, sect = {}, None, [], []
    for line in patch_text.splitlines():
        if line.startswith("diff --git "):
            if cur:
                out[cur] = (added, sect)
            cur, added, sect = line.split(" b/", 1)[-1], [], []
        if cur is None:
            continue
        sect.append(line)
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    if cur:
        out[cur] = (added, sect)
    return out


def comment(line):
    s = line.strip()
    return s == "" or s.startswith(("#", "//", "--", ";"))


def changes(old, new):
    """{path: first changed line of the OLD file (comment lines ignored), or None when unknown}.

    Run logs carry line numbers of the tests they were graded with (the old ones). Comment lines are dropped before
    the comparison, so an added header comment does not count; the result is mapped back to an old-file line number.
    """
    out = {}
    for path in old.keys() | new.keys():
        if path not in old or path not in new:
            out[path] = None
            continue
        (a, sa), (b, sb) = old[path], new[path]
        if sa == sb:
            continue
        if not any(l.startswith("new file mode") for l in sb):
            out[path] = None  # a modification hunk: line numbers of the whole file are unknown
            continue
        ka = [(i + 1, l) for i, l in enumerate(a) if not comment(l)]
        kb = [l for l in b if not comment(l)]
        k = next((j for j, (_, l) in enumerate(ka) if j >= len(kb) or kb[j] != l), len(ka))
        if k == len(ka) and len(kb) == len(ka):
            continue  # only comments changed
        out[path] = ka[k][0] if k < len(ka) else (ka[-1][0] + 1 if ka else 1)
    return out


LOC = re.compile(r"([\w./-]+\.[A-Za-z0-9]+):(\d+)")


def plan(changed, run_dir, test_paths):
    verdict = (run_dir / "verdict.txt").read_text(encoding="utf-8", errors="replace") if (run_dir / "verdict.txt").exists() else ""
    if "PASS" in verdict and "FAIL" not in verdict:
        return "REPLAY", "passed before; changed tests may fail it"
    log = run_dir / "testlog.txt"
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    locs = []
    for line in text.splitlines():
        if "FAIL" not in line and "Error" not in line and "error" not in line:
            continue
        for f, n in LOC.findall(line):
            match = [p for p in test_paths if p.endswith(f) or f.endswith(p) or Path(p).name == Path(f).name]
            if match:
                locs.append((match[0], int(n)))
    if not locs:
        return "REPLAY", "no failure location in testlog.txt"
    why = []
    state = "SKIP"
    for path, n in sorted(set(locs)):
        if path not in changed:
            why.append(f"{Path(path).name}:{n} unchanged file")
            continue
        first = changed[path]
        if first is None or first <= n:
            return "REPLAY", f"{Path(path).name}:{n} at/after a change (first changed line {first or '?'})"
        state = "LINE?"
        why.append(f"{Path(path).name}:{n} before first change at {first}")
    return state, "; ".join(why)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        sys.exit(__doc__)
    old = files(Path(args[0]).read_text(encoding="utf-8", errors="replace"))
    new = files(Path(args[1]).read_text(encoding="utf-8", errors="replace"))
    runs = Path(args[2])
    stage = None
    if "--stage" in sys.argv:
        stage = Path(sys.argv[sys.argv.index("--stage") + 1])
        stage.mkdir(parents=True, exist_ok=True)
    skip_lines = "--skip-lines" in sys.argv
    changed = changes(old, new)
    print("changed test files:", ", ".join(f"{Path(p).name}" + (f" (from old line {c})" if c else " (whole file)")
                                           for p, c in sorted(changed.items())) or "none")
    counts, failing_files = {}, set()
    dirs = sorted(p for p in runs.iterdir() if p.is_dir())
    for d in dirs:
        log = d / "testlog.txt"
        if log.exists():
            failing_files |= {Path(f).name for f, _ in LOC.findall(log.read_text(encoding="utf-8", errors="replace"))}
    shared = sorted(Path(p).name for p in changed if Path(p).name not in failing_files)
    if shared:
        # A run that keeps its failing line still fails, whatever else changed, unless one of these feeds that line.
        print("CHECK: changed files no run failed in:", ", ".join(shared),
              "- SKIP and LINE? hold unless one of them feeds a failing line (harness, shared fixture)")
    for d in dirs:
        state, why = plan(changed, d, list(new.keys() | old.keys()))
        if state == "LINE?" and skip_lines:
            state = "SKIP"
        counts[state] = counts.get(state, 0) + 1
        print(f"{state:7} {d.name}  {why}")
        if stage and state == "REPLAY" and (d / "solution.patch").exists():
            shutil.copy(d / "solution.patch", stage / f"{d.name}.patch")
    print("total:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
