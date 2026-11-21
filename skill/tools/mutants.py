#!/usr/bin/env python3
"""Wrong-solution sweep over the lines a patch adds (Go only: go.mod, go test and Go syntax; BACKLOG #178, #181).

usage: mutants.py gen <patch> <tree> <out.json> [--cover profile.out]
       mutants.py run <mutants.json> <tree> <tests.patch> <out.jsonl> --run REGEX [--shard K/N] [--timeout SECONDS]

gen: the module path comes from <tree>/go.mod; the files and lines from what <patch> adds to non-test Go files (the
tree must hold the patch applied). One mutant per operator that fits a line:
  neg          an if / else if / case condition negated     true, false  the condition replaced by true, by false
  drop         one operand of a top-level || or && removed (and one level down)
  del          an assignment, call, continue, break or ++ line deleted
  flip         return true <-> return false
  swap         in a return or an assignment, one field replaced by a sibling field of the same type in the same
               struct (from the tree's struct declarations): the "package change instead of entry change" class
With --cover (a Go cover profile of the hidden tests) each mutant says whether a test ran its line (covered true or
false), so one list serves both passes: lines the tests run, and branches no test runs. Prints counts per operator.
run: applies one mutant at a time to a copy of <tree>, runs `go test -count=1 -failfast -run REGEX` over the packages
of the *_test.go files of <tests.patch>, and classes it killed (a test fails), survived (every test passes), invalid
(does not build), timeout, or stale (the tree no longer has the line). Shard K of N takes the mutants with
id % N == K (default 0/1). One JSON line per mutant in <out.jsonl>, the survivors in <out>-survivors.txt.
"""
import argparse
import collections
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKIP = ("//", "}", "{", "case ", "default", "return", "if ", "for ", "switch", "func ", "var ", "const ", "type ",
        "else", "go ", "defer ", "select", "package ", "import")
ASSIGN = re.compile(r"(^|[^=!<>:])=([^=]|$)")
SELECTOR = re.compile(r"\.([A-Za-z_]\w*)\b(?!\()")
FIELD = re.compile(r"^\s*([A-Za-z_]\w*(?:, [A-Za-z_]\w*)*)\s+([^\s`/][^`]*?)\s*(?:`[^`]*`)?\s*(?://.*)?$")


def read(path):
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def remove_tree(path):
    # Windows marks .git pack files read-only, which stops rmtree; make the entry writable and retry.
    shutil.rmtree(path, onerror=lambda func, name, exc: (os.chmod(name, stat.S_IWRITE), func(name)))


def module_path(tree):
    for line in read(Path(tree) / "go.mod").splitlines():
        if line.startswith("module "):
            return line.split()[1]
    raise ValueError(f"no module line in {tree}/go.mod")


def added_lines(patch):
    """{file: {line numbers}} that the patch adds to non-test Go files."""
    added = collections.defaultdict(set)
    current, n = None, 0
    for line in read(patch).splitlines(keepends=True):
        if line.startswith("+++ "):
            name = line[4:].strip()
            current = name[2:] if name.startswith("b/") else None
            if current and (not current.endswith(".go") or current.endswith("_test.go")):
                current = None
            continue
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            n = int(hunk.group(1))
            continue
        if current is None:
            continue
        if line.startswith("+"):
            added[current].add(n)
            n += 1
        elif line.startswith(" ") or line.strip() == "":
            n += 1
    return added


def covered_lines(profile, module):
    """{file: {line numbers}} with a count above zero in a Go cover profile."""
    ran = collections.defaultdict(set)
    for line in read(profile).splitlines():
        m = re.match(r"(.+):(\d+)\.(\d+),(\d+)\.(\d+) (\d+) (\d+)$", line.strip())
        if m and m.group(1).startswith(module + "/") and int(m.group(7)) > 0:
            ran[m.group(1)[len(module) + 1:]].update(range(int(m.group(2)), int(m.group(4)) + 1))
    return ran


def split_top(expr, sep):
    """Split expr at top-level sep, outside brackets and string literals."""
    parts, depth, i, start, quote = [], 0, 0, 0, None
    while i < len(expr):
        c = expr[i]
        if quote:
            if c == "\\" and quote != "`":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth == 0 and expr.startswith(sep, i):
            parts.append(expr[start:i].strip())
            i += len(sep)
            start = i
            continue
        i += 1
    parts.append(expr[start:].strip())
    return parts


def drops(cond):
    """Conditions with one operand removed: top-level || (or &&), then one level into each operand."""
    out = []
    for sep in (" || ", " && "):
        parts = split_top(cond, sep)
        if len(parts) > 1:
            for k in range(len(parts)):
                out.append(sep.join(parts[:k] + parts[k + 1:]))
            if sep == " || ":
                for k, part in enumerate(parts):
                    sub = split_top(part, " && ")
                    if len(sub) > 1:
                        for j in range(len(sub)):
                            out.append(sep.join(parts[:k] + [" && ".join(sub[:j] + sub[j + 1:])] + parts[k + 1:]))
            break
    return out


def named(typ):
    """A named type or a pointer to one (model.Change, *Manifest, time.Time): two fields of such a type are the same
    kind of thing. string, bool, numbers, slices, maps and funcs are left out, where a swap is only noise."""
    return re.match(r"^(\w+\.)?[A-Z]\w*$", typ.lstrip("*")) is not None


def struct_siblings(tree):
    """{field: {fields of the same named type in the same struct}} over the tree's non-test Go files."""
    siblings = collections.defaultdict(set)
    for path in Path(tree).rglob("*.go"):
        if path.name.endswith("_test.go") or ".git" in path.parts or "vendor" in path.parts:
            continue
        for block in re.findall(r"(?ms)^type \w+ struct \{\n(.*?)^\}", read(path)):
            by_type = collections.defaultdict(list)
            for line in block.split("\n"):
                m = FIELD.match(line)
                if m and not line.lstrip().startswith("//") and named(m.group(2)):
                    for name in m.group(1).split(", "):
                        by_type[m.group(2)].append(name)
            for names in by_type.values():
                for name in names:
                    siblings[name].update(other for other in names if other != name)
    return siblings


def mutate(line, siblings):
    """[(operator, new line)] for one source line."""
    indent = line[: len(line) - len(line.lstrip())]
    body = line.strip()
    news = []
    m = re.match(r"^(\} else )?if (.+) \{$", body)
    if m:
        head, cond, init = m.group(1) or "", m.group(2), ""
        semi = split_top(cond, "; ")
        if len(semi) == 2:
            init, cond = semi[0] + "; ", semi[1]
        news.append(("neg", f"{indent}{head}if {init}!({cond}) {{"))
        news += [("drop", f"{indent}{head}if {init}{c} {{") for c in drops(cond)]
        news += [("true", f"{indent}{head}if {init}true {{"), ("false", f"{indent}{head}if {init}false {{")]
    m = re.match(r"^case (.+):$", body)
    if m and len(split_top(m.group(1), ", ")) == 1:
        cond = m.group(1)
        news.append(("neg", f"{indent}case !({cond}):"))
        news += [("drop", f"{indent}case {c}:") for c in drops(cond)]
        news += [("true", f"{indent}case true:"), ("false", f"{indent}case false:")]
    if body in ("return true", "return false"):
        news.append(("flip", indent + ("return false" if body == "return true" else "return true")))
    if (body and not body.startswith(SKIP) and ":=" not in body
            and not body.endswith(("{", "(", ",", "+", "||", "&&"))
            and (ASSIGN.search(body) or body.endswith(")") or body in ("continue", "break")
                 or body.endswith(("++", "--")))):
        news.append(("del", indent + "// mutant: line deleted"))
    if body.startswith("return ") or ((ASSIGN.search(body) or ":=" in body)
                                      and not body.startswith(("if ", "for ", "case ", "switch ", "} else if "))):
        for m in SELECTOR.finditer(body):
            for other in sorted(siblings.get(m.group(1), ())):
                news.append(("swap", indent + body[:m.start(1)] + other + body[m.end(1):]))
    return news


def gen(args):
    module = module_path(args.tree)
    added = added_lines(args.patch)
    ran = covered_lines(args.cover, module) if args.cover else None
    siblings = struct_siblings(args.tree)
    mutants = []
    for name in sorted(added):
        path = Path(args.tree) / name
        if not path.is_file():
            print(f"missing in the tree (is the patch applied?): {name}", file=sys.stderr)
            continue
        src = read(path).split("\n")
        for ln in sorted(added[name]):
            if ln > len(src):
                continue
            for op, new in mutate(src[ln - 1], siblings):
                mutants.append({"id": len(mutants), "file": name, "line": ln, "op": op, "orig": src[ln - 1],
                                "new": new, "covered": None if ran is None else ln in ran[name]})
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(mutants, f, indent=0)
    ops = collections.Counter(m["op"] for m in mutants)
    print(f"mutants: {len(mutants)} from {sum(map(len, added.values()))} added lines in {len(added)} files; "
          + ", ".join(f"{op} {n}" for op, n in sorted(ops.items())))
    if ran is not None:
        print(f"covered (a test ran the line): {sum(m['covered'] for m in mutants)}; "
              f"not run: {sum(not m['covered'] for m in mutants)}")
    return 0


def packages(tests_patch):
    dirs = set()
    for line in read(tests_patch).splitlines():
        if line.startswith("+++ b/") and line.strip().endswith("_test.go"):
            dirs.add("./" + line[6:].strip().rsplit("/", 1)[0] + "/")
    return sorted(dirs)


def run_one(copy, mutant, regex, pkgs, timeout):
    """(result, failed tests, seconds) of one mutant applied in the copy and restored afterwards."""
    path = copy / mutant["file"]
    src = read(path)
    lines = src.split("\n")
    if mutant["line"] > len(lines) or lines[mutant["line"] - 1] != mutant["orig"]:
        return "stale", [], 0.0
    lines[mutant["line"] - 1] = mutant["new"]
    write(path, "\n".join(lines))
    t0 = time.monotonic()
    try:
        proc = subprocess.run(["go", "test", "-count=1", "-failfast", "-timeout", f"{timeout}s", "-run", regex] + pkgs,
                              cwd=copy, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout + 120)
        text = proc.stdout + proc.stderr
        if "[build failed]" in text or "[setup failed]" in text or "build failed" in text:
            result = "invalid"
        else:
            result = "survived" if proc.returncode == 0 else "killed"
        failed = sorted({l.split()[2] for l in text.splitlines() if l.strip().startswith("--- FAIL:")})[:3]
    except subprocess.TimeoutExpired:
        result, failed = "timeout", []
    finally:
        write(path, src)
    return result, failed, time.monotonic() - t0


def run(args):
    with open(args.mutants, encoding="utf-8") as f:
        mutants = json.load(f)
    shard, shards = (int(x) for x in args.shard.split("/"))
    pkgs = packages(args.tests)
    if not pkgs:
        raise ValueError(f"no *_test.go files in {args.tests}")
    work = Path(tempfile.mkdtemp(prefix="mutants-"))
    copy = work / "tree"
    print(f"copying {args.tree} -> {copy}; packages {' '.join(pkgs)}; shard {shard}/{shards}", flush=True)
    shutil.copytree(args.tree, copy, symlinks=True)
    rows = []
    try:
        with open(args.out, "w", encoding="utf-8") as out:
            for mutant in mutants:
                if mutant["id"] % shards != shard:
                    continue
                result, failed, seconds = run_one(copy, mutant, args.run, pkgs, args.timeout)
                rows.append({**mutant, "result": result, "failed": failed, "seconds": round(seconds)})
                out.write(json.dumps(rows[-1]) + "\n")
                out.flush()
                print(f"{mutant['id']:4} {result:8} {mutant['file']}:{mutant['line']} {mutant['op']} ({seconds:.0f}s)",
                      flush=True)
    finally:
        remove_tree(work)
    survivors = Path(args.out).with_name(Path(args.out).stem + "-survivors.txt")
    survivors.write_text("".join(f"{r['id']}\t{r['file']}:{r['line']}\t{r['op']}\tcovered={r.get('covered')}\t"
                                 f"{r['new'].strip()}\n" for r in rows if r["result"] == "survived"), encoding="utf-8")
    counts = collections.Counter(r["result"] for r in rows)
    print(f"shard {shard}/{shards}: {len(rows)} mutants; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
          + f"; survivors in {survivors}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("gen")
    g.add_argument("patch", type=Path)
    g.add_argument("tree", type=Path)
    g.add_argument("out", type=Path)
    g.add_argument("--cover", type=Path)
    r = sub.add_parser("run")
    r.add_argument("mutants", type=Path)
    r.add_argument("tree", type=Path)
    r.add_argument("tests", type=Path)
    r.add_argument("out", type=Path)
    r.add_argument("--run", required=True, help="go test -run regex of the tests to run")
    r.add_argument("--shard", default="0/1")
    r.add_argument("--timeout", type=int, default=600, help="go test -timeout per mutant (seconds)")
    args = parser.parse_args(argv)
    return gen(args) if args.command == "gen" else run(args)


if __name__ == "__main__":
    sys.exit(main())
