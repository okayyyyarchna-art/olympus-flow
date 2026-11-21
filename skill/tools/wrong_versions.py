#!/usr/bin/env python3
"""Run the kept wrong versions of a task against the current hidden tests (tq-once.md section 2).

usage: wrong_versions.py <kept-dir> <tree> [--cmd COMMAND] [--tests NAME,...] [--only NAME,...]

<kept-dir> holds one Python script per kept version (eval/wrong/kept/<name>.py) that defines
  EDITS = [(path, old, new), ...]  exact-text edits of the repository, each matching once (LF kept)
  KIND = 'wrong' | 'control' | 'held'
  EXPECT = 'TestName' or 'TestName/leaf' (a leaf name or a prefix of it), or a list: the cells that must catch it
Each script's edits are applied to one copy of <tree>, COMMAND runs in that copy, then the edited files are restored.
COMMAND (default: ./test.sh new --output_path {junit}) runs through the shell in the copy. `{junit}` is replaced by
a report path that is read afterwards; `{tests}` by a quoted regex of the top-level test names of EXPECT (or of
--tests), empty for a control, so a repository command can run only them, for example
  --cmd "go test -count=1 -run {tests} ./internal/engine/"
Without {junit} the failing names are read from Go test output (--- FAIL: lines).
Verdicts: wrong -> every EXPECT entry is matched by a failing leaf (other failing leaves are listed as "also fails");
control -> everything passes (exit 0); held ->
reported only. An edit that no longer matches once fails its step. One summary table; exit 1 on any mismatch.
Re-running only the versions a test edit can affect (BACKLOG #179) is not built: every script runs each time.
"""
import argparse
import os
import re
import runpy
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_CMD = "./test.sh new --output_path {junit}"
KINDS = ("wrong", "control", "held")
TIMEOUT = 1200


def load(script):
    """(kind, edits, leaves) of one kept script; ValueError when it lacks KIND or EDITS."""
    namespace = runpy.run_path(str(script), run_name="kept")
    kind, edits, expect = namespace.get("KIND"), namespace.get("EDITS"), namespace.get("EXPECT", "")
    if kind not in KINDS or not isinstance(edits, list):
        raise ValueError(f"{script.name}: needs KIND in {KINDS} and EDITS = [(path, old, new), ...]")
    leaves = [expect] if isinstance(expect, str) else list(expect)
    return kind, edits, [leaf for leaf in leaves if leaf]


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def apply(root, edits):
    """Apply the edits under root; return {path: original text}. ValueError when one does not match exactly once."""
    originals = {}
    for path, old, new in edits:
        target = Path(root) / path
        src = read(target) if target.is_file() else None
        if src is None or src.count(old) != 1:
            restore(root, originals)
            found = "missing file" if src is None else f"{src.count(old)} matches"
            raise ValueError(f"edit does not apply: {path} ({found})")
        originals.setdefault(path, src)
        write(target, src.replace(old, new, 1))
    return originals


def restore(root, originals):
    for path, src in originals.items():
        write(Path(root) / path, src)


def remove_tree(path):
    # Windows marks .git pack files read-only, which stops rmtree; make the entry writable and retry.
    shutil.rmtree(path, onerror=lambda func, name, exc: (os.chmod(name, stat.S_IWRITE), func(name)))


def tests_regex(leaves):
    names = sorted({leaf.split("/")[0] for leaf in leaves})
    return f"^({'|'.join(names)})$" if names else ""


def junit_failures(path):
    return {case.get("name", "") for case in ET.parse(path).getroot().iter("testcase")
            if case.find("failure") is not None or case.find("error") is not None}


def text_failures(out):
    failing = set(re.findall(r"^\s*--- FAIL: (\S+)", out, re.M))
    if "[build failed]" in out or "[setup failed]" in out or "build failed" in out:
        failing.add("build failed")
    return failing


def quote(value):
    # The shell is bash in the task image and cmd.exe on a Windows host (unit tests); cmd.exe keeps ^ ( | $ literal
    # only inside double quotes.
    return '"' + value.replace('"', '\\"') + '"' if os.name == "nt" else shlex.quote(value)


def run(command, cwd, leaves):
    """(exit, failing names or None when the report is missing, seconds) of COMMAND in cwd."""
    junit = Path(cwd).parent / "report.xml"
    junit.unlink(missing_ok=True)
    shell = command.replace("{junit}", quote(str(junit))).replace("{tests}", quote(tests_regex(leaves)))
    t0 = time.monotonic()
    try:
        proc = subprocess.run(shell, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=TIMEOUT)
        code, out = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        code, out = 124, ""
    if "{junit}" in command:
        failing = junit_failures(junit) if junit.is_file() else None
    else:
        failing = text_failures(out)
    return code, failing, time.monotonic() - t0


def verdict(kind, leaves, code, failing):
    """(ok | BAD | held, detail) from the leaves a run failed; a parent counts for its leaves and a leaf for its parent."""
    if code == 124:
        return "BAD", f"timeout after {TIMEOUT}s"
    if failing is None:
        return "BAD", "no report written"
    if kind == "control":
        return ("ok", "") if code == 0 and not failing else ("BAD", "a control fails")
    # An EXPECT entry names a leaf exactly or by a prefix of its name (subtest names are long): it is caught when a
    # failing leaf equals it, sits below it, or starts with it. Other failing leaves are reported, not a mismatch:
    # a wrong version may break several cells, and the gate is that its own cell catches it.
    def hit(leaf, f):
        return f == leaf or f.startswith(leaf) or leaf.startswith(f + "/")
    missing = [leaf for leaf in leaves if not any(hit(leaf, f) for f in failing)]
    extra = sorted(f for f in failing if not any(hit(leaf, f) for leaf in leaves))
    if kind == "held":
        return "held", ("not caught: " + ", ".join(missing)) if missing else "caught"
    if missing:
        return "BAD", "not caught: " + ", ".join(missing)
    if code == 0:
        return "BAD", "exit 0 although the leaves fail"
    return "ok", ("also fails: " + ", ".join(extra[:3]) + (" ..." if len(extra) > 3 else "")) if extra else ""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kept", type=Path)
    parser.add_argument("tree", type=Path)
    parser.add_argument("--cmd", default=DEFAULT_CMD)
    parser.add_argument("--tests", help="top-level test names for {tests}, comma-separated (default: EXPECT)")
    parser.add_argument("--only", help="kept script names to run, comma-separated (default: all)")
    args = parser.parse_args(argv)
    scripts = sorted(args.kept.glob("*.py"))
    if args.only:
        wanted = set(args.only.split(","))
        scripts = [s for s in scripts if s.stem in wanted]
    if not scripts:
        print(f"no kept scripts in {args.kept}")
        return 2
    work = Path(tempfile.mkdtemp(prefix="wrong-"))
    copy = work / "tree"
    print(f"copying {args.tree} -> {copy}", flush=True)
    shutil.copytree(args.tree, copy, symlinks=True)
    rows, bad = [], False
    try:
        for script in scripts:
            try:
                kind, edits, leaves = load(script)
                originals = apply(copy, edits)
            except ValueError as exc:
                rows.append((script.stem, "?", "BAD", 0.0, str(exc)))
                print(f"kept {script.stem}: BAD: {exc}", flush=True)
                continue
            try:
                selected = args.tests.split(",") if args.tests else leaves
                code, failing, seconds = run(args.cmd, copy, selected)
            finally:
                restore(copy, originals)
            result, detail = verdict(kind, leaves, code, failing)
            failing_text = ", ".join(sorted(failing))[:160] if failing else ""
            rows.append((script.stem, kind, result, seconds, detail or failing_text))
            print(f"kept {script.stem} ({kind}): {result} in {seconds:.0f}s; exit {code}; failing: {failing_text}",
                  flush=True)
    finally:
        remove_tree(work)
    bad = any(row[2] == "BAD" for row in rows)
    width = max(len(row[0]) for row in rows)
    print(f"\n{'kept version':<{width}}  kind     verdict  time  detail")
    for name, kind, result, seconds, detail in rows:
        print(f"{name:<{width}}  {kind:<7}  {result:<7}  {seconds:4.0f}  {detail}")
    print("note: every kept version runs each time; re-running only the versions a test edit can affect is open (#179)")
    print(f"WRONG VERSIONS {'FAIL' if bad else 'PASS'}: {len(rows)} kept scripts, "
          f"{sum(r[2] == 'BAD' for r in rows)} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
