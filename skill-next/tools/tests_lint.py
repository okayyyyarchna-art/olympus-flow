#!/usr/bin/env python3
"""Deterministic checks for test findings the platform raises again and again (no model, seconds).

usage: python tests_lint.py <pkg-dir> <repo-dir>
pkg-dir: description.md (or task.md), test.patch, solution.patch. repo-dir: the repository (any state) to look up
existing test files. Prints FAIL / REVIEW / PASS lines. FAIL = fix it. REVIEW = look at it; fix it or write one line in
eval/gates.md saying why it is fine. Exit 1 when any FAIL.

Each rule is a platform finding seen on 2+ packages (MAP.md section 11, replicas/knowledge/tests.md):
L1 vacuous all()/any() (window AR T3 High, `all([])`); L2 private-state asserts (elio PDF path, task 7 fields, T5);
L3 mock-call pins (T5, internal coupling); L4 wall-clock waits deciding outcomes (goka 5 s, task 8 15 s: T2);
L5 base mode misses tests of edited files (window T1 High, swift T1); L6 deselect without a reason comment (T1);
L7 log/output pins (producer flush TQ unfair, T7); L8 exact error-message pins (T7); L9 a test replaces a framework
method (SetTable AR tests band 1, dead letter T5); L10 lifecycle started but not ended (dead letter T5 High).
"""
import re
import sys
from pathlib import Path

out = []


def emit(level, rule, msg):
    out.append(level)
    print(f"{level:6} {rule}: {msg}")


def added_by_file(patch):
    files, cur = {}, None
    for line in patch.splitlines():
        m = re.match(r"^\+\+\+ b/(.+)$", line)
        if m:
            cur = m.group(1)
            files[cur] = []
            continue
        if cur and line.startswith("+") and not line.startswith("+++"):
            files[cur].append(line[1:])
    return files


def functions(lines, lang):
    """Split added lines into (name, body lines) per test/helper function."""
    pat = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\(") if lang == "py" else re.compile(r"^func\s+(?:\([^)]*\)\s*)?(\w+)\(")
    funcs, name, body = [], None, []
    for ln in lines:
        m = pat.match(ln)
        if m:
            if name:
                funcs.append((name, body))
            name, body = m.group(1), []
        elif name:
            body.append(ln)
    if name:
        funcs.append((name, body))
    return funcs


def main():
    pkg, repo = Path(sys.argv[1]), Path(sys.argv[2])
    desc = (pkg / "description.md") if (pkg / "description.md").exists() else (pkg / "task.md")
    desc = desc.read_text(encoding="utf-8", errors="replace")
    tp = (pkg / "test.patch").read_text(encoding="utf-8", errors="replace")
    sp = (pkg / "solution.patch").read_text(encoding="utf-8", errors="replace")
    tfiles = added_by_file(tp)
    sfiles = added_by_file(sp)
    test_sh = "\n".join(tfiles.get("test.sh", []))
    hits = 0
    for path, lines in tfiles.items():
        if path == "test.sh":
            continue
        lang = "py" if path.endswith(".py") else "go" if path.endswith(".go") else None
        if not lang:
            continue
        helper_repl = set()
        for name, body in functions(lines, lang):
            text = "\n".join(body)
            where = f"{path}::{name}"
            is_test = name.startswith(("test_", "Test"))
            # L1 vacuous all/any without a non-empty guard in the same function
            for m in re.finditer(r"assert\s+(all|any)\((.+?)\s+for\s+\w+\s+in\s+([A-Za-z_]\w*)\s*\)", text):
                seq = m.group(3)
                if not re.search(rf"assert\s+(len\()?{re.escape(seq)}|assert\s+{re.escape(seq)}\b|{re.escape(seq)}\s*==\s*\[", text):
                    emit("REVIEW", "L1 vacuous all()/any()", f"{where}: `{m.group(0)[:70]}` passes on an empty {seq}; add `assert {seq}` or an exact expected list")
                    hits += 1
            # L2 private-state asserts
            for m in re.finditer(r"^\s*assert\b.*?\b\w+\._(?!_)\w+", text, re.M):
                emit("REVIEW", "L2 private state asserted", f"{where}: `{m.group(0).strip()[:90]}`; assert an observable outcome unless the description names it")
                hits += 1
            # L3 mock call pins
            for m in re.finditer(r"\.(assert_called\w*|assert_awaited\w*)\b|^\s*assert\b.*\.(call_args\w*|call_count|mock_calls)\b", text if is_test else "", re.M):
                emit("REVIEW", "L3 mock call pinned", f"{where}: `{m.group(0).strip()[:60]}`; a valid design calling things differently fails")
                hits += 1
                break
            # L4 wall-clock waits
            for m in re.finditer(r"(asyncio\.sleep|time\.sleep|time\.Sleep|time\.After)\(\s*([0-9.]+)?\s*(\*\s*time\.\w+)?", text):
                val = m.group(2)
                big = (val is not None and float(val) >= 0.5) or bool(m.group(3) and re.search(r"Second|Minute", m.group(3)))
                if big:
                    emit("REVIEW", "L4 wall-clock wait", f"{where}: `{m.group(0)}` may decide an ordering or hide a slow design; use an event/handshake")
                    hits += 1
                    break
            # L7 log / output pins
            if re.search(r"\bcaplog\b|\bcapsys\b|assertLogs|capfd", text):
                emit("REVIEW", "L7 log/output pinned", f"{where}: logs are pinned; allowed only when the description names the message")
                hits += 1
            # L8 exact error message pins
            for m in re.finditer(r"(?:pytest\.raises\([^)]*match\s*=\s*|str\(\w+\)\s*==\s*|\.Error\(\)\s*!=\s*)[rbf]?['\"]([^'\"]{6,})['\"]", text):
                if m.group(1).lower() not in desc.lower():
                    emit("REVIEW", "L8 exact message pinned", f"{where}: `{m.group(1)[:60]}` not in the description")
                    hits += 1
            # L9 a framework method replaced inside a test
            edge = r"create_conn|connect|time|sleep|monotonic|now|urlopen|request|socket|getaddrinfo"
            for m in re.finditer(r"monkeypatch\.setattr\(\s*[\w.]+\s*,\s*['\"](_?\w+)['\"]|^\s*[\w.]+\.(send_soon|send|publish\w*|_on_\w+|on_\w+)\s*=\s*(?!None)", text if is_test else "", re.M):
                if re.fullmatch(edge, (m.group(1) or m.group(2) or "")):
                    continue
                emit("REVIEW", "L9 framework method replaced", f"{where}: `{m.group(0).strip()[:80]}`; a stated mode must still run its real code path")
                hits += 1
                break
            if not is_test:
                for m in re.finditer(r"^\s*[\w.]+\.(send_soon|send|publish\w*|_on_\w+|on_\w+)\s*=\s*(?!None)", text, re.M):
                    helper_repl.add(m.group(1))
            # L10 lifecycle started but not ended
            for m in re.finditer(r"\bon_(\w+?)_start\(", text if is_test else ""):
                if not re.search(rf"\bon_{m.group(1)}_end\(", text):
                    emit("REVIEW", "L10 lifecycle not completed", f"{where}: on_{m.group(1)}_start() without on_{m.group(1)}_end()")
                    hits += 1
        if helper_repl:
            emit("REVIEW", "L9 harness replaces framework methods", f"{path}: helpers replace {', '.join(sorted(helper_repl))}; every mode the description states must still run its real code path (e.g. threaded producer)")
            hits += 1
    # L5 base mode covers the existing tests of every edited production file
    prod = [p for p in sfiles if not re.search(r"(^|/)(tests?|docs?)/|_test\.go$|\.md$|CHANGELOG", p)]
    for p in prod:
        stem = Path(p).stem
        cands = [c for c in repo.rglob(f"test_{stem}.py")] + [c for c in repo.rglob(f"{stem}_test.go")]
        parent = Path(p).parent.name
        cands = [c for c in cands if "site-packages" not in str(c)
                 and parent in c.relative_to(repo).parts
                 and not set(c.relative_to(repo).parts) & {"integration", "probe", "e2e", "functional"}]
        for c in cands[:3]:
            rel = c.relative_to(repo).as_posix()
            toks = set(re.findall(r"[\w./-]*tests?/[\w./-]+", test_sh))
            covered = any(rel == t.rstrip("/") or rel.startswith(t.rstrip("/") + "/") for t in toks)
            if not covered and rel.endswith("_test.go"):
                # Go runs every test file of a package: covered when test.sh runs the package directory
                # (vet 2026-11-06: run_pkg internal/policy was flagged as missing finalize_test.go)
                pkg_dir = Path(rel).parent.as_posix()
                covered = re.search(rf"(^|[\s'\"./]){re.escape(pkg_dir)}(/\.\.\.)?([\s'\"]|$)", test_sh, re.M) is not None
            if not covered and test_sh:
                emit("FAIL", "L5 base mode misses a test of an edited file", f"{p} is edited; base selection in test.sh does not run {rel}")
                hits += 1
    # L6 every deselect has a reason comment just above it
    sh = test_sh.splitlines()
    for i, ln in enumerate(sh):
        if re.search(r"--deselect|::Test\w*::\w+\"|::test_\w+\"", ln) and "::" in ln:
            above = " ".join(sh[max(0, i - 12):i])
            if "#" not in above:
                emit("REVIEW", "L6 deselect without reason", f"`{ln.strip()[:90]}` has no comment above it")
                hits += 1
    if not hits:
        emit("PASS", "tests lint", "no recurring platform pattern found")
    print(f"\n{out.count('FAIL')} FAIL, {out.count('REVIEW')} REVIEW")
    sys.exit(1 if "FAIL" in out else 0)


if __name__ == "__main__":
    main()
