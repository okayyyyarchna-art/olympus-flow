#!/usr/bin/env python3
"""seqlen.py <path>...: sequence length of agent runs, counted as the platform counts it.

Sequence length = the sum over context windows of each window's peak, where a request's context is its input tokens
plus its output tokens (the platform's rule `window_peaks_2026_11b`; this tool matches the platform's own
`sequence_length` field on every trajectory checked). A window ends at a compaction: the trajectory's `window` id
changes, or (Codex session logs) the input context drops below half of the previous request. The hosted Codex
harness compacts at about 244K and restarts at 12-14K, so the platform's 256K bar means "the passing run compacted
once"; the design target is 300K.

Each path is one of
  a Codex rollout .jsonl      local Codex CLI session log (turn_context and token_count payloads)
  a platform trajectory.json  final_metrics.extra.per_request_usage[{window, input_tokens, output_tokens}]
  a run folder                zip download (trajectory.json, eval-result.json, run.txt) or tools/pull.sh
                              (output.json with sequenceLength and compacted, evalResult.json, verdict.txt)
One line per input: source, kind, family, model (and effort when known), requests, windows with each peak, sequence
length, compacted yes/no, the context window size and peak share for a Codex log, the verdict, and the platform's
own number when the trajectory carries one. Then one summary line: the mean sequence length of the passing runs
(verdict starting with PASS) against the 256K bar and the 300K target; without verdicts, the mean over all inputs.
Always exits 0; a bad input gets an error line instead of stopping the batch. Standard library only.
"""
import glob
import json
import os
import re
import sys

BAR = 256_000          # platform: Orion's passing runs must average at least this
TARGET = 300_000       # owner: design every new task for this from the start
DROP = 0.5             # a request whose input is below half of the previous one starts a new window
PLACEHOLDER = re.compile(r"^<.*>$")  # the zip trajectories redact the model as "<model>"


def window_peaks(calls):
    """Peak context (input + output tokens) of each window; calls are dicts with input, output and optional window id.

    When every call carries a window id the ids split the windows (platform trajectories); otherwise a drop of the
    input context below half of the previous request does (Codex logs)."""
    peaks, prev_in, prev_w = [], None, None
    tagged = bool(calls) and all(c.get("window") is not None for c in calls)
    for c in calls:
        inp, out = int(c.get("input") or 0), int(c.get("output") or 0)
        if tagged:
            new = not peaks or c["window"] != prev_w
        else:
            new = not peaks or (prev_in is not None and inp < prev_in * DROP)
        if new:
            peaks.append(0)
        peaks[-1] = max(peaks[-1], inp + out)
        prev_in, prev_w = inp, c.get("window")
    return peaks


def passes(verdict):
    """The platform's passing verdicts start with PASS (PASS, PASS_WITH_CAVEATS, ...)."""
    return str(verdict or "").strip().upper().startswith("PASS")


def as_int(v):
    """Platform JSON gives numbers as numbers or as strings ('475502'); None stays None."""
    if v is None or isinstance(v, bool):
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def as_bool(v):
    """Platform JSON gives flags as booleans or as strings ('True'); None and unknown text stay None."""
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no", ""):
        return False
    return None


def load_json(path):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return json.load(f)


def read_codex_jsonl(path):
    """Model, effort, context window, cwd, timestamps, tool counts and per-request usage of a Codex session log."""
    info = {"kind": "codex", "model": None, "effort": None, "context_window": None, "cwd": "", "started": None,
            "ended": None, "calls": [], "tools": {}}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            p = d.get("payload") if isinstance(d.get("payload"), dict) else {}
            if d.get("timestamp"):
                info["started"] = info["started"] or d["timestamp"]
                info["ended"] = d["timestamp"]
            kind = d.get("type")
            if kind == "session_meta":
                info["cwd"] = p.get("cwd") or info["cwd"]
            elif kind == "turn_context":
                info["model"] = p.get("model") or info["model"]
                settings = (p.get("collaboration_mode") or {}).get("settings") or {}
                info["effort"] = (p.get("effort") or p.get("reasoning_effort") or settings.get("reasoning_effort")
                                  or info["effort"])
                info["cwd"] = p.get("cwd") or info["cwd"]
            elif p.get("type") == "token_count" and isinstance(p.get("info"), dict):
                u = p["info"].get("last_token_usage") or {}
                info["calls"].append({"window": None, "input": u.get("input_tokens", 0),
                                      "output": u.get("output_tokens", 0),
                                      "reasoning": u.get("reasoning_output_tokens", 0)})
                info["context_window"] = p["info"].get("model_context_window") or info["context_window"]
            elif kind == "response_item" and p.get("type") in ("function_call", "custom_tool_call"):
                name = p.get("name") or "?"
                info["tools"][name] = info["tools"].get(name, 0) + 1
    return info


def read_trajectory(path):
    """Per-request usage, model and the platform's own sequence fields of an ATIF trajectory.json."""
    t = load_json(path)
    fm = t.get("final_metrics") or {}
    extra = fm.get("extra") or {}
    usage = extra.get("per_request_usage") or []
    calls = [{"window": u.get("window"), "input": u.get("input_tokens", 0), "output": u.get("output_tokens", 0),
              "reasoning": u.get("reasoning_output_tokens", 0)} for u in usage if isinstance(u, dict)]
    model = (t.get("agent") or {}).get("model_name")
    if not model or PLACEHOLDER.match(str(model)):
        model = next((s.get("model_name") for s in t.get("steps") or []
                      if s.get("source") == "agent" and s.get("model_name")
                      and not PLACEHOLDER.match(str(s["model_name"]))), None)
    return {"kind": "trajectory", "model": model, "effort": None, "calls": calls,
            "platform_seqlen": extra.get("sequence_length"), "platform_compacted": extra.get("compacted"),
            "reasoning_total": extra.get("reasoning_output_tokens"),
            "output_total": fm.get("total_completion_tokens"), "trajectory": t}


def read_verdict(folder):
    """Verdict of a run folder: eval-result.json (zip), evalResult.json or output.json, then verdict.txt (pull.sh)."""
    for name in ("eval-result.json", "evalResult.json", "output.json"):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            try:
                v = load_json(p).get("verdict")
            except (ValueError, OSError, AttributeError):
                v = None
            if v:
                return str(v)
    p = os.path.join(folder, "verdict.txt")
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            parts = f.readline().split()
        if len(parts) > 1:
            return parts[1]
    return None


def read_family(folder):
    """Solver family: run.txt "Run: Orion #3" (zip), verdict.txt "Orion PASS" (pull.sh), else the folder name."""
    p = os.path.join(folder, "run.txt")
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            m = re.match(r"\s*Run:\s*([^#\n]+?)\s*(#|$)", f.readline())
        if m and m.group(1):
            return m.group(1)
    p = os.path.join(folder, "verdict.txt")
    if os.path.isfile(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            parts = f.readline().split()
        if parts:
            return parts[0]
    base = os.path.basename(os.path.normpath(folder))
    return base.split("_")[0] if "_" in base else None


def read_run_folder(folder):
    """A zip download folder (trajectory.json) or a tools/pull.sh folder (output.json with the platform's numbers)."""
    tp, op = os.path.join(folder, "trajectory.json"), os.path.join(folder, "output.json")
    if os.path.isfile(tp):
        info = read_trajectory(tp)
        info["kind"] = "run"
    elif os.path.isfile(op):
        o = load_json(op)
        info = {"kind": "pulled", "model": None, "effort": None, "calls": [],
                "platform_seqlen": o.get("sequenceLength"), "platform_compacted": o.get("compacted")}
    else:
        raise FileNotFoundError("no trajectory.json or output.json in the folder")
    info["verdict"] = read_verdict(folder)
    info["family"] = read_family(folder)
    return info


def measure(path):
    """One record per input: source, kind, family, model, requests, peaks, seqlen, compacted, verdict, context window."""
    rec = {"source": path, "kind": None, "family": None, "model": None, "effort": None, "requests": 0, "peaks": [],
           "seqlen": None, "compacted": None, "verdict": None, "context_window": None, "platform_seqlen": None,
           "platform_compacted": None, "from_platform": False, "error": None}
    try:
        if os.path.isdir(path):
            info = read_run_folder(path)
        elif path.lower().endswith(".jsonl"):
            info = read_codex_jsonl(path)
        elif path.lower().endswith(".json"):
            info = read_trajectory(path)
        elif not os.path.exists(path):
            raise FileNotFoundError("no such file or folder")
        else:
            raise ValueError("not a .jsonl, a .json or a run folder")
    except Exception as e:  # one bad input must not stop the batch
        rec["error"] = f"{type(e).__name__}: {e}"
        return rec
    for k in ("kind", "family", "model", "effort", "verdict", "context_window"):
        rec[k] = info.get(k)
    rec["platform_seqlen"] = as_int(info.get("platform_seqlen"))
    rec["platform_compacted"] = as_bool(info.get("platform_compacted"))
    calls = info.get("calls") or []
    rec["requests"] = len(calls)
    if calls:
        rec["peaks"] = window_peaks(calls)
        rec["seqlen"] = sum(rec["peaks"])
        rec["compacted"] = len(rec["peaks"]) > 1
    elif rec["platform_seqlen"] is not None:
        rec["seqlen"], rec["compacted"], rec["from_platform"] = rec["platform_seqlen"], rec["platform_compacted"], True
    return rec


def short_name(path):
    """The last two path parts of a folder (zip/Orion_Orion_4), the file name of a file."""
    parts = [p for p in os.path.normpath(path).replace("\\", "/").split("/") if p]
    name = "/".join(parts[-2:]) if os.path.isdir(path) else (parts[-1] if parts else path)
    return name[-70:]


def yn(flag):
    return "-" if flag is None else ("yes" if flag else "no")


def fmt_k(n):
    return "-" if n is None else f"{n:,} ({n / 1000:.0f}K)"


def format_record(r):
    if r["error"]:
        return f"{short_name(r['source'])} | error: {r['error']}"
    parts = [short_name(r["source"]), r["kind"] or "-"]
    if r["family"]:
        parts.append(r["family"])
    parts.append("model " + (r["model"] or "-") + (f" {r['effort']}" if r["effort"] else ""))
    if r["from_platform"]:
        parts.append("requests - (platform values, no trajectory)" if r["kind"] == "pulled"
                     else "requests 0 (no per-request usage; platform value)")
    else:
        parts.append(f"requests {r['requests']}")
        parts.append(f"windows {len(r['peaks'])} [{', '.join(f'{p:,}' for p in r['peaks'])}]")
    parts.append(f"seqlen {fmt_k(r['seqlen'])}")
    parts.append(f"compacted {yn(r['compacted'])}")
    if r["context_window"]:
        peak = max(r["peaks"]) if r["peaks"] else 0
        parts.append(f"context window {r['context_window']:,} (peak {100 * peak / r['context_window']:.0f}%)")
    if r["verdict"]:
        parts.append(f"verdict {r['verdict']}")
    if r["platform_seqlen"] is not None and not r["from_platform"]:
        same = r["platform_seqlen"] == r["seqlen"]
        parts.append(f"platform {r['platform_seqlen']:,}" + ("" if same else " (differs)"))
    return " | ".join(parts)


def judge(mean):
    return (f"256K bar {'met' if mean >= BAR else 'not met'}, "
            f"300K target {'met' if mean >= TARGET else 'not met'}")


def summary(records):
    """Mean sequence length of the passing runs against the bar and the target; all inputs when no verdict exists."""
    ok = [r for r in records if r["seqlen"] is not None]
    if not ok:
        return "summary: no sequence length measured"
    mean_all = sum(r["seqlen"] for r in ok) / len(ok)
    with_verdict = [r for r in ok if r["verdict"]]
    passing = [r for r in with_verdict if passes(r["verdict"])]
    if passing:
        mean = sum(r["seqlen"] for r in passing) / len(passing)
        return (f"summary: {len(passing)} passing of {len(with_verdict)} with a verdict, "
                f"passing mean {mean:,.0f}: {judge(mean)}")
    if with_verdict:
        return (f"summary: 0 passing of {len(with_verdict)} with a verdict, no passing mean; "
                f"mean over all {len(ok)} runs {mean_all:,.0f} (design read: {judge(mean_all)})")
    return f"summary: no verdicts; mean over all {len(ok)} inputs {mean_all:,.0f}: {judge(mean_all)}"


def token_counter():
    """(count function, note): tiktoken o200k_base when it is installed, else 4 characters per token."""
    try:
        import tiktoken  # optional
        enc = tiktoken.get_encoding("o200k_base")
        return (lambda s: len(enc.encode(s, disallowed_special=()))), "tokens: tiktoken o200k_base"
    except Exception:
        return (lambda s: (len(s) + 3) // 4), "tokens: estimated at 4 characters per token (tiktoken not available)"


def expand(args):
    """Expand glob patterns that the shell left alone (PowerShell); keep everything else as given."""
    out = []
    for a in args:
        if any(ch in a for ch in "*?[") and not os.path.exists(a):
            out += sorted(glob.glob(a)) or [a]
        else:
            out.append(a)
    return out


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else argv
    paths = expand([a for a in argv if not a.startswith("-")])
    if not paths or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    records = [measure(p) for p in paths]
    for r in records:
        print(format_record(r))
    print(summary(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
