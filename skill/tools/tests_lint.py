#!/usr/bin/env python3
"""Deterministic checks for test findings the platform raises again and again (no model, seconds).

usage: python tests_lint.py <pkg-dir> <repo-dir>
pkg-dir: description.md (or task.md), test.patch, solution.patch. repo-dir: the repository at the base commit (any state
works for L1-L10; the Go checks G1/G2/W1 read the base checkout). Prints FAIL / REVIEW / PASS lines. FAIL = fix it.
REVIEW = look at it; fix it or write one line in eval/gates.md saying why it is fine. Exit 1 when any FAIL.

Each rule is a platform finding seen on 2+ packages (replicas/knowledge/tests.md):
L1 vacuous all()/any() (window AR T3 High, `all([])`); L2 private-state asserts (elio PDF path, task 7 fields, T5);
L3 mock-call pins (T5, internal coupling); L4 wall-clock waits deciding outcomes (goka 5 s, task 8 15 s: T2);
L5 base mode misses tests of edited files (window T1 High, swift T1); L6 deselect without a reason comment (T1);
L7 log/output pins (producer flush TQ unfair, T7); L8 exact error-message pins (T7); L9 a test replaces a framework
method (SetTable AR tests band 1, dead letter T5); L10 lifecycle started but not ended (dead letter T5 High).

Go repositories (go.mod at the repo root), from the import graph of the base checkout (`go list` when a Go toolchain
is on PATH and runs, else a regex parse of the import lines, said in a NOTE line) and the base-mode package list of
test.sh (selectors.base of the embedded JSON profile, or the directories named in the `base)` arms of a bash runner):
G1 a package that only _test.go files import, used by a base-mode package, is not pinned by test.sh (vet 6 graphtest,
pmg cloudpolicytest: #222, #160); G2 a package with tests that is a changed package or imports one is neither in base
mode nor named in a `# base skip: <dir> <reason>` line (vet 6 fx25: #197); W1 a base-mode test with an upper wall-clock
bound, a root skip or a passwd lookup is a skip-allowlist candidate (vet 6 Verify Flakiness, pmg verifyTests: #213,
#155), printed for the builder to decide, never a failure by itself.
"""
import base64
import binascii
import json
import os
import re
import shutil
import subprocess
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


# ---- Go import graph of the base checkout ----
SKIP_DIRS = ("vendor", "testdata", "node_modules", ".git")
IMPORT_LINE = re.compile(r'^\s*(?:[\w.]+\s+)?"([^"]+)"', re.M)


def go_imports(text):
    """Import paths of one Go source file: single `import "x"` lines and import blocks."""
    found = set(re.findall(r'^import\s+(?:[\w.]+\s+)?"([^"]+)"', text, re.M))
    for block in re.findall(r"^import\s*\((.*?)^\)", text, re.M | re.S):
        found.update(IMPORT_LINE.findall(block))
    return found


def go_list(repo):
    """Packages from `go list` (None when no toolchain is on PATH or the command fails)."""
    if not shutil.which("go"):
        return None
    env = dict(os.environ, GOWORK="off", GOFLAGS="-mod=mod")
    try:
        proc = subprocess.run(["go", "list", "-e", "-json=ImportPath,Dir,GoFiles,TestGoFiles,XTestGoFiles,Imports,TestImports,XTestImports",
                               "./..."], cwd=repo, capture_output=True, text=True, env=env, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode or not proc.stdout.strip():
        return None
    root = Path(repo).resolve()
    decoder, text, objects = json.JSONDecoder(), proc.stdout, []
    try:
        while text.strip():
            item, end = decoder.raw_decode(text.lstrip())
            objects.append(item)
            text = text.lstrip()[end:]
    except ValueError:
        return None
    by_path, pkgs = {}, {}
    for item in objects:
        try:
            rel = Path(item["Dir"]).resolve().relative_to(root).as_posix()
        except (KeyError, ValueError):
            continue
        by_path[item["ImportPath"]] = rel
        pkgs[rel] = {"files": item.get("GoFiles") or [], "tests": (item.get("TestGoFiles") or []) + (item.get("XTestGoFiles") or []),
                     "raw": set(item.get("Imports") or []), "raw_test": set(item.get("TestImports") or []) | set(item.get("XTestImports") or [])}
    for pkg in pkgs.values():
        pkg["imports"] = {by_path[i] for i in pkg.pop("raw") if i in by_path}
        pkg["test_imports"] = {by_path[i] for i in pkg.pop("raw_test") if i in by_path}
    return pkgs


def go_files(repo):
    """(package dir, file name) of every .go file and go.mod under repo; vendor, testdata, .git and dot or underscore folders pruned."""
    for base, dirs, files in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith((".", "_")))
        rel = Path(base).relative_to(repo).as_posix()
        for name in sorted(files):
            if name.endswith(".go") or name == "go.mod":
                yield rel, name


def go_scan(repo):
    """Packages from a regex parse of the import lines (every go.mod in the tree names a module prefix)."""
    repo = Path(repo)
    modules, sources = {}, []
    for d, name in go_files(repo):
        if name == "go.mod":
            m = re.search(r"^module\s+(\S+)", (repo / d / name).read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                modules[d] = m.group(1)
        else:
            sources.append((d, name))
    pkgs = {}
    for d, name in sources:
        path = repo / d / name
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"^//go:build ignore\b|^// \+build ignore\b", text, re.M):
            continue
        pkg = pkgs.setdefault(d, {"files": [], "tests": [], "raw": set(), "raw_test": set()})
        if path.name.endswith("_test.go"):
            pkg["tests"].append(path.name)
            pkg["raw_test"] |= go_imports(text)
        else:
            pkg["files"].append(path.name)
            pkg["raw"] |= go_imports(text)
    ordered = sorted(modules.items(), key=lambda kv: -len(kv[1]))

    def resolve(ip):
        for mdir, mod in ordered:
            if ip == mod:
                return mdir
            if ip.startswith(mod + "/"):
                sub = ip[len(mod) + 1:]
                return sub if mdir == "." else mdir + "/" + sub
        return None
    for pkg in pkgs.values():
        pkg["imports"] = {r for r in map(resolve, pkg.pop("raw")) if r in pkgs}
        pkg["test_imports"] = {r for r in map(resolve, pkg.pop("raw_test")) if r in pkgs}
    return pkgs


def embedded_profile(test_sh):
    """The JSON profile of a generated adapter (readable JSON first, the older base64 form second), else None."""
    m = re.search(r"json\.loads\(r(\"\"\"|''')(.*?)\1\)", test_sh, re.S)
    if m:
        try:
            return json.loads(m.group(2))
        except ValueError:
            return None
    m = re.search(r"base64\.b64decode\('([A-Za-z0-9+/=]+)'\)", test_sh)
    if m:
        try:
            return json.loads(base64.b64decode(m.group(1)))
        except (ValueError, binascii.Error):
            return None
    return None


def expand_selector(sel, pkgs):
    sel = sel.strip().strip("'\"")
    if sel.startswith("./"):
        sel = sel[2:]
    if sel in (".", ""):
        return {"."} & set(pkgs)
    if sel == "...":
        return set(pkgs)
    if sel.endswith("/..."):
        prefix = sel[:-4]
        return {d for d in pkgs if d == prefix or d.startswith(prefix + "/")}
    return {sel.rstrip("/")} & set(pkgs)


def base_packages(test_sh, pkgs, profile):
    """(package dirs base mode runs, where they were read)."""
    if profile and isinstance(profile.get("selectors"), dict):
        dirs = set()
        for sel in profile["selectors"].get("base", []):
            dirs |= expand_selector(str(sel), pkgs)
        return dirs, "selectors.base of the embedded profile"
    region, on = [], False
    for ln in test_sh.splitlines():
        if re.match(r"^\s*base\)", ln):
            on = True
        if on and not re.match(r"^\s*#", ln):
            region.append(ln)
        if on and ";;" in ln:
            on = False
    dirs = set()
    for tok in re.findall(r"[\w./-]+", "\n".join(region)):
        dirs |= expand_selector(tok, pkgs)
    return dirs, "the base) arms of the runner" if region else "nowhere: no embedded profile and no base) arm"


def pinned_by(test_sh, profile, pkg_dir, files):
    """How test.sh pins the non-test files of pkg_dir (restore_paths/helpers of the profile, or a PIN* regex plus the
    directory named for restoring), or None."""
    rels = [f if pkg_dir == "." else pkg_dir + "/" + f for f in files]
    if profile:
        listed = set(profile.get("restore_paths") or []) | set(profile.get("helpers") or [])
        return "restore_paths/helpers" if all(r in listed for r in rels) else None
    named = re.search(rf"(^|[\s'\"]){re.escape(pkg_dir)}([\s'\"]|$)", test_sh, re.M) is not None
    for m in re.finditer(r"^\s*(\w*PIN\w*)=['\"](.+?)['\"]\s*$", test_sh, re.M):
        try:
            rx = re.compile(m.group(2))
        except re.error:
            continue
        if named and all(rx.search(r) for r in rels):
            return m.group(1) + " and the directory is restored"
    return None


def check_helpers(pkgs, base, test_sh, profile):
    """G1: every package that only tests import, used by a base-mode package, is pinned."""
    hits = 0
    for d, pkg in sorted(pkgs.items()):
        if not pkg["files"]:
            continue
        importers = [o for o, p in pkgs.items() if o != d and d in p["imports"]]
        test_importers = [o for o, p in pkgs.items() if o != d and d in p["test_imports"]]
        if importers or not test_importers:
            continue
        in_base = sorted(o for o in test_importers if o in base)
        if not in_base:
            continue
        how = pinned_by(test_sh, profile, d, pkg["files"])
        if how:
            emit("PASS", "G1 test-only helper pinned", f"{d} (tests of {', '.join(in_base[:3])}) via {how}")
        else:
            emit("FAIL", "G1 test-only helper not pinned", f"{d} is imported only by tests ({', '.join(in_base[:3])}) that base mode runs, and "
                 f"test.sh does not restore it: an edit to {d} weakens those tests (#222, #160)")
            hits += 1
    return hits


def check_importers(pkgs, base, changed, test_sh):
    """G2: a changed package and each direct importer of it, when it has tests, is in base mode or listed with a reason."""
    hits = 0
    skips = {k.lstrip("./").rstrip("/"): v.strip() for k, v in re.findall(r"^\s*#\s*base skip:\s*(\S+)\s+(.+)$", test_sh, re.M)}
    seen = set()
    for c in sorted(changed):
        if c not in pkgs:
            continue
        importers = {o for o, p in pkgs.items() if o != c and (c in p["imports"] or c in p["test_imports"])}
        for d in sorted({c} | importers):
            if d in seen or not pkgs[d]["tests"] or d in base:
                continue
            seen.add(d)
            reason = next((v for k, v in skips.items() if k == d or k.endswith("/" + d)), None)
            if reason:
                emit("REVIEW", "G2 importer left out with a reason", f"{d}: {reason}")
            else:
                via = "is changed" if d == c else f"imports {c} (changed)"
                emit("FAIL", "G2 base mode misses a package that uses changed code",
                     f"{d} has tests and {via}; add it to base mode or a `# base skip: {d} <reason>` line in test.sh (#197)")
            hits += 1
    return hits


WALL_CLOCK = (
    (re.compile(r"(?:assert|require)\.(?:Less|LessOrEqual|Greater|GreaterOrEqual|WithinDuration|InDelta|InEpsilon)\w*\([^\n]*time\.(?:Since|Now|Until|Duration)"),
     "upper wall-clock bound"),
    (re.compile(r"time\.Since\([^\n]*\)\s*(?:<|>|<=|>=)|(?:<|>|<=|>=)\s*time\.Since\("), "elapsed-time comparison"),
    (re.compile(r"\belapsed\b[^\n]*(?:<|>)[^\n]*time\.(?:Millisecond|Second|Minute)"), "elapsed-time comparison"),
    (re.compile(r"(?:context\.WithTimeout|time\.After|time\.NewTimer|time\.AfterFunc|SetDeadline)\([^\n]*\b\d{1,3}\s*\*\s*time\.Millisecond"),
     "sub-second timeout"),
)
ROOT_CHECK = re.compile(r"os\.Gete?uid\(\)\s*==\s*0|Gete?uid\(\)\s*==\s*0|==\s*\"root\"")


def check_candidates(repo, pkgs, base):
    """W1: base-mode tests with an upper wall-clock bound, a root skip or a passwd lookup; candidates, not failures."""
    hits = 0
    for d in sorted(base):
        for name in sorted(pkgs.get(d, {}).get("tests", [])):
            path = Path(repo) / d / name
            rel = name if d == "." else d + "/" + name
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            func = "?"
            for i, ln in enumerate(lines):
                m = re.match(r"^func\s+(?:\([^)]*\)\s*)?(\w+)\(", ln)
                if m:
                    func = m.group(1)
                reasons = [why for rx, why in WALL_CLOCK if rx.search(ln)]
                if ROOT_CHECK.search(ln) and any("Skip" in nxt for nxt in lines[i:i + 6]):
                    reasons.append("skips as root (the platform runs base mode as root)")
                if "user.Current()" in ln:
                    reasons.append("needs a passwd record for the current user (base mode also runs as a uid without one)")
                for why in reasons:
                    emit("REVIEW", "W1 skip allowlist candidate", f"{rel}:{i + 1} {func}: {why}: `{ln.strip()[:80]}`; the platform runs "
                         "base mode 12 times, as root and as uid 1000 (#213, #155)")
                    hits += 1
    return hits


def go_checks(repo, test_sh, sfiles):
    repo = Path(repo)
    if not (repo / "go.mod").exists() or not test_sh:
        return 0
    pkgs = go_list(repo)
    if pkgs is None:
        pkgs = go_scan(repo)
        emit("NOTE", "Go import graph", "regex parse of the import lines (no Go toolchain on PATH, or go list failed)")
    else:
        emit("NOTE", "Go import graph", "go list")
    profile = embedded_profile(test_sh)
    base, how = base_packages(test_sh, pkgs, profile)
    if not base:
        emit("REVIEW", "G0 base selection", f"no base-mode package read from test.sh ({how}); G1, G2 and W1 skipped")
        return 1
    emit("NOTE", "base-mode packages", f"{len(base)} from {how}")
    changed = {Path(p).parent.as_posix() for p in sfiles if p.endswith(".go") and not p.endswith("_test.go")}
    hits = check_helpers(pkgs, base, test_sh, profile)
    hits += check_importers(pkgs, base, changed, test_sh)
    hits += check_candidates(repo, pkgs, base)
    return hits


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
    # G1, G2, W1: Go import graph of the base checkout against the base-mode selection of test.sh
    hits += go_checks(repo, test_sh, sfiles)
    if not hits:
        emit("PASS", "tests lint", "no recurring platform pattern found")
    print(f"\n{out.count('FAIL')} FAIL, {out.count('REVIEW')} REVIEW")
    sys.exit(1 if "FAIL" in out else 0)


if __name__ == "__main__":
    main()
