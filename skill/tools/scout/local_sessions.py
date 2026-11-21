#!/usr/bin/env python3
"""local_sessions.py [--marker TEXT] <sessions dir or rollout-*.jsonl>...: the work fingerprint of local Codex
solves from their session logs (rollout-*.jsonl, usually under ~/.codex/sessions), where model and effort are known.

Per session: start, model, effort, requests, sequence length, output and reasoning tokens per request, reasoning
share, minutes, peak context and the model's context window, the tool counts and the windows with their peaks.
With --marker TEXT only sessions whose working folder contains TEXT are read (the solve clones of one task);
sessions without token counts are skipped. Compare the rows with scout/stage_a.py (hosted runs) before trusting a
local stand-in, and read the seqlen column against the 300K design target. Standard library only; always exits 0.
"""
import glob
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import seqlen  # noqa: E402


def ts(x):
    return datetime.fromisoformat(str(x).replace("Z", "+00:00"))


def session_files(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob.glob(os.path.join(p, "**", "rollout-*.jsonl"), recursive=True)
        else:
            files.append(p)
    return sorted(set(files))


def row(path, marker):
    """A fingerprint row or None when the session is not of the marked task or has no token counts."""
    info = seqlen.read_codex_jsonl(path)
    if marker and marker not in info["cwd"].replace("\\", "/"):
        return None
    calls = info["calls"]
    if not calls:
        return None
    peaks = seqlen.window_peaks(calls)
    out = sum(c["output"] for c in calls)
    rea = sum(c.get("reasoning") or 0 for c in calls)
    n = len(calls)
    try:
        minutes = (ts(info["ended"]) - ts(info["started"])).total_seconds() / 60 if info["started"] else 0
    except ValueError:
        minutes = 0
    return {"started": str(info["started"] or "?")[:16], "model": info["model"] or "?", "effort": info["effort"] or "?",
            "requests": n, "seqlen": sum(peaks), "out_req": out / n, "rea_req": rea / n,
            "rea_pct": 100 * rea / max(out, 1), "minutes": minutes, "peak": max(c["input"] for c in calls),
            "context_window": info["context_window"], "tools": info["tools"], "windows": peaks,
            "file": os.path.basename(path)}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else list(argv)
    marker = None
    if "--marker" in argv:
        i = argv.index("--marker")
        marker = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    paths = seqlen.expand([a for a in argv if not a.startswith("-")])
    if not paths or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    files = session_files(paths)
    print(f"{len(files)} session logs" + (f", marker {marker!r} in the working folder" if marker else ""))
    print(f"{'started':16} {'model':16} {'effort':7} {'reqs':>4} {'seqlen':>7} {'out/req':>7} {'rea/req':>7} "
          f"{'rea%':>4} {'min':>4} {'peak':>7} {'ctx':>7} tools / windows")
    shown = []
    for path in files:
        try:
            r = row(path, marker)
        except Exception as e:  # one bad log must not stop the batch
            print(f"error: {os.path.basename(path)}: {type(e).__name__}: {e}")
            continue
        if r:
            shown.append(r)
            print(f"{r['started']:16} {r['model'][:16]:16} {str(r['effort'])[:7]:7} {r['requests']:>4} {r['seqlen']:>7} "
                  f"{r['out_req']:>7.0f} {r['rea_req']:>7.0f} {r['rea_pct']:>4.0f} {r['minutes']:>4.0f} {r['peak']:>7} "
                  f"{str(r['context_window'] or '-'):>7} {r['tools']} {r['windows']}")
    if shown:
        mean = sum(r["seqlen"] for r in shown) / len(shown)
        print(f"{len(shown)} sessions shown; mean seqlen {mean:,.0f}: {seqlen.judge(mean)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
