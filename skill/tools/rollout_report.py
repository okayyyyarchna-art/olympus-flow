#!/usr/bin/env python3
"""rollout_report.py [--marker TEXT] <run folder>...: one table for a batch of platform runs, the tests failed by two
or more runs, and the platform rollout gate computed from the table.

Run folders are zip downloads (run.txt, junit-new.xml, eval-result.json, trajectory.json) or tools/pull.sh folders
(verdict.txt, output.json, evalResult.json, testlog.txt). Columns: run, family (run.txt "Run: Orion #3", verdict.txt
or the folder name), missed (failing test cases of the platform junit-new.xml, or the failing tests of the pulled
platform testlog; never a local replay), verdict, sequence length (tools/seqlen.py), compacted, requests, and
whether --marker TEXT appears in the task prompt of the trajectory (a description sentence the run saw).

Gate (platform rollout criteria, 2026-11-21): Orion solves at least one run and at most 25%; Orion's solving runs
average at least 256K of sequence length; Nova 0%; Vega at most 25%; at least 4 completed runs per family. A run
counts as completed when it has a verdict. Always exits 0. Standard library only.
"""
import collections
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seqlen  # noqa: E402

FAMILIES = ("Orion", "Nova", "Vega")
MIN_RUNS = 4
MAX_RATE = 0.25
GO_FAIL = re.compile(r"^--- FAIL: (\S+)", re.M)          # top-level Go tests (subtests are indented)
PYTEST_FAIL = re.compile(r"^FAILED (\S+?)(?: - .*)?$", re.M)


def junit_misses(path):
    """(failing test-case names, total test cases) of a JUnit file."""
    cases = list(ET.parse(path).getroot().iter("testcase"))
    bad = [c.get("name") or "?" for c in cases if c.find("failure") is not None or c.find("error") is not None]
    return bad, len(cases)


def testlog_misses(path):
    """(failing test names, None) from a pulled platform test log: Go `--- FAIL: Name` and pytest `FAILED name`."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    names = list(dict.fromkeys(GO_FAIL.findall(text) + PYTEST_FAIL.findall(text)))
    return names, None


def misses(folder):
    """(failing names, total or None, source name) from the platform's junit, else its test log, else nothing."""
    p = os.path.join(folder, "junit-new.xml")
    if os.path.isfile(p):
        bad, total = junit_misses(p)
        return bad, total, "junit"
    p = os.path.join(folder, "testlog.txt")
    if os.path.isfile(p):
        bad, total = testlog_misses(p)
        return bad, total, "testlog"
    return None, None, None


def prompt_has(folder, marker):
    """Whether the marker text appears in a non-agent message (the task prompt) of the folder's trajectory."""
    p = os.path.join(folder, "trajectory.json")
    if not marker or not os.path.isfile(p):
        return None
    try:
        steps = seqlen.load_json(p).get("steps") or []
    except (ValueError, OSError, AttributeError):
        return None
    return any(marker in s.get("message") for s in steps
               if s.get("source") != "agent" and isinstance(s.get("message"), str))


def canonical(family):
    """Platform codenames as the platform spells them; anything else as found."""
    if not family:
        return "?"
    return next((f for f in FAMILIES if f.lower() == family.strip().lower()), family.strip())


def row_for(folder, marker):
    rec = seqlen.measure(folder)
    rec["family"] = canonical(rec["family"])
    rec["name"] = seqlen.short_name(folder)
    try:
        rec["missed"], rec["total"], rec["miss_source"] = misses(folder)
    except (ET.ParseError, OSError) as e:
        rec["missed"], rec["total"], rec["miss_source"] = None, None, f"error: {e}"
    rec["marker"] = prompt_has(folder, marker)
    return rec


def rate_text(f):
    return f"{100 * f['passes'] / f['runs']:.0f}%" if f["runs"] else "-"


def gate_lines(rows):
    """Per family runs, passes, rate (and Orion's passing mean); then each platform criterion met / not met."""
    fam = {}
    for r in rows:
        if not r.get("verdict"):
            continue
        f = fam.setdefault(r["family"], {"runs": 0, "passes": 0, "pass_seqlen": []})
        f["runs"] += 1
        if seqlen.passes(r["verdict"]):
            f["passes"] += 1
            if r.get("seqlen") is not None:
                f["pass_seqlen"].append(r["seqlen"])
    empty = {"runs": 0, "passes": 0, "pass_seqlen": []}
    order = list(FAMILIES) + sorted(k for k in fam if k not in FAMILIES)
    lines = ["gate (platform criteria 2026-11-21; completed = has a verdict):"]
    for name in order:
        f = fam.get(name, empty)
        line = f"  {name}: {f['runs']} completed, {f['passes']} pass ({rate_text(f)})"
        if name == "Orion":
            mean = sum(f["pass_seqlen"]) / len(f["pass_seqlen"]) if f["pass_seqlen"] else None
            line += f", passing mean seqlen {mean:,.0f}" if mean is not None else ", passing mean seqlen -"
        lines.append(line)

    def enough(f):
        return f["runs"] >= MIN_RUNS

    def short(f):
        return f"{f['passes']} of {f['runs']}"

    o = fam.get("Orion", empty)
    if not enough(o):
        verdict = f"not enough runs ({o['runs']} of {MIN_RUNS}; {short(o)} pass so far)"
    elif o["passes"] < 1:
        verdict = f"not met (0 passes of {o['runs']})"
    elif o["passes"] > MAX_RATE * o["runs"]:
        verdict = f"not met ({short(o)} pass = {rate_text(o)} > 25%)"
    else:
        verdict = f"met ({short(o)} pass = {rate_text(o)})"
    lines.append(f"  Orion solves >=1 run and <=25%: {verdict}")

    if not o["passes"]:
        verdict = "not met (no passing run)" if enough(o) else f"not enough runs ({o['runs']} of {MIN_RUNS}; no passing run yet)"
    elif not o["pass_seqlen"]:
        verdict = "unknown (passing runs without a sequence length)"
    else:
        mean = sum(o["pass_seqlen"]) / len(o["pass_seqlen"])
        verdict = f"{'met' if mean >= seqlen.BAR else 'not met'} (mean {mean:,.0f} over {len(o['pass_seqlen'])} passing)"
        if not enough(o):
            verdict += f"; not enough runs ({o['runs']} of {MIN_RUNS})"
    lines.append(f"  Orion passing runs average >=256K: {verdict}")

    n = fam.get("Nova", empty)
    if not enough(n):
        verdict = f"not enough runs ({n['runs']} of {MIN_RUNS}; {short(n)} pass so far)"
    else:
        verdict = f"{'met' if n['passes'] == 0 else 'not met'} ({short(n)} pass)"
    lines.append(f"  Nova 0%: {verdict}")

    v = fam.get("Vega", empty)
    if not enough(v):
        verdict = f"not enough runs ({v['runs']} of {MIN_RUNS}; {short(v)} pass so far)"
    else:
        verdict = f"{'met' if v['passes'] <= MAX_RATE * v['runs'] else 'not met'} ({short(v)} pass = {rate_text(v)})"
    lines.append(f"  Vega <=25%: {verdict}")

    per = ", ".join(f"{name} {'met' if enough(fam.get(name, empty)) else 'not met'} ({fam.get(name, empty)['runs']})"
                    for name in FAMILIES)
    lines.append(f"  >=4 completed runs per family: {per}")
    return lines


def report(folders, marker=None):
    rows = [row_for(d, marker) for d in folders]
    width = max([len(r["name"]) for r in rows] + [3])
    sources = sorted({r["miss_source"] for r in rows if r["miss_source"] and not r["miss_source"].startswith("error")})
    lines = [f"misses = platform {' / '.join(sources) if sources else 'junit'} (never a local replay); "
             f"seqlen = sum of window peaks (input + output tokens)"
             + (f"; marker = {marker!r} seen in the task prompt" if marker else ""),
             f"{'run':{width}} {'family':7} {'missed':>8} {'verdict':26} {'seqlen':>8} {'compact':>7} {'reqs':>4} marker"]
    fails = collections.defaultdict(list)
    for r in rows:
        if r.get("error"):
            lines.append(f"{r['name']:{width}} error: {r['error']}")
            continue
        for b in r["missed"] or []:
            fails[b].append(r["name"])
        if r["missed"] is None:
            missed = "-"
        elif r["total"] is None:
            missed = str(len(r["missed"]))
        else:
            missed = f"{len(r['missed'])}/{r['total']}"
        reqs = "-" if r["from_platform"] else str(r["requests"])
        seq = "-" if r["seqlen"] is None else f"{r['seqlen']:,}"
        lines.append(f"{r['name']:{width}} {r['family']:7} {missed:>8} {str(r['verdict'] or '-'):26} {seq:>8} "
                     f"{seqlen.yn(r['compacted']):>7} {reqs:>4} {seqlen.yn(r['marker'])}")
    lines.append("")
    lines.append("tests failed by two or more runs:")
    shared = [(n, who) for n, who in fails.items() if len(who) >= 2]
    for n, who in sorted(shared, key=lambda kv: (-len(kv[1]), kv[0])):
        lines.append(f"  {len(who)}  {n[:140]}")
    if not shared:
        lines.append("  none")
    lines.append("")
    lines += gate_lines([r for r in rows if not r.get("error")])
    return lines


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:] if argv is None else list(argv)
    marker = None
    if "--marker" in argv:
        i = argv.index("--marker")
        marker = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    folders = [d for d in seqlen.expand(argv) if not d.startswith("-")]
    if not folders or "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    for line in report(folders, marker):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
