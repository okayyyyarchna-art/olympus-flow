#!/usr/bin/env python3
"""Deterministic replica of the platform prechecks plus our packaging checks. No model, runs in a second.

usage: python precheck.py <package-dir> [--category bugfix|feature_request] [--last-accepted <description.md>]
Package dir: description.md, test.patch, solution.patch, Dockerfile (test.sh lives inside test.patch).
Exit 0 = no FAIL. Prints one line per check: PASS / WARN / FAIL with the reason.

Every rule here comes from a recorded platform result (MAP.md section 11, 2026-11-05):
non-ASCII and URL fails, word cap, category shape, test.sh modes, malformed hunks, tests run during the Docker
build, process words in the test patch (AR Tests 0/3 Blocker), stray files, executable bit, em-dashes / hard wrap
(the "doesn't look AI-generated" precheck), predictable test file names.
"""
import argparse
import re
import sys
from pathlib import Path

results = []


def out(level, name, msg=""):
    results.append(level)
    print(f"{level:4} {name}{': ' + msg if msg else ''}")


def site_words(text):
    return len([w for w in re.split(r"[\s\-/]+", text.strip()) if w])


def patch_files(patch):
    return re.findall(r"^diff --git a/(\S+) b/(\S+)", patch, re.M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg")
    ap.add_argument("--category", choices=["bugfix", "feature_request"])
    ap.add_argument("--last-accepted")
    a = ap.parse_args()
    pkg = Path(a.pkg)
    desc_p = pkg / "description.md"
    if not desc_p.exists():
        desc_p = pkg / "task.md"
    desc = desc_p.read_text(encoding="utf-8")
    tp = (pkg / "test.patch").read_text(encoding="utf-8")
    sp = (pkg / "solution.patch").read_text(encoding="utf-8")
    df = (pkg / "Dockerfile").read_text(encoding="utf-8") if (pkg / "Dockerfile").exists() else ""

    # --- description ---
    bad = [(i, ch) for i, ch in enumerate(desc) if ord(ch) > 127]
    out("FAIL" if bad else "PASS", "description ASCII only", f"{len(bad)} non-ASCII chars, first {bad[:3]}" if bad else "")
    urls = re.findall(r"\b[a-z][a-z0-9+.-]*://\S*|\bwww\.[a-z0-9-]+\.\S+", desc, re.I)
    out("FAIL" if urls else "PASS", "description has no URLs or scheme://", ", ".join(urls[:3]))
    w = site_words(desc)
    out("FAIL" if w > 1000 else ("WARN" if w > 400 else "PASS"), "description site words (split on space - /)", str(w))
    long_lines = [l for l in desc.splitlines() if l.strip()]
    wrapped = sum(1 for l in long_lines if 60 <= len(l) <= 80) >= 4 and all(len(l) <= 100 for l in long_lines)
    out("WARN" if wrapped else "PASS", "description not hard-wrapped (AI-look precheck)")
    out("FAIL" if "—" in desc or " -- " in desc else "PASS", "no em-dashes")
    bullets = len(re.findall(r"^\s*([-*]|\d+\.)\s", desc, re.M))
    out("WARN" if bullets > 3 else "PASS", "no rule-sheet lists", f"{bullets} list lines")
    ticks = desc.count("`"); semis = desc.count(";")
    nwords = max(1, len(desc.split())); commas = desc.count(",") * 20 / nwords
    out("WARN" if ticks or semis or commas > 0.9 else "PASS", "AI-look hygiene (no backticks, no semicolons, <= 0.9 commas / 20 words)",
        f"backticks {ticks}, semicolons {semis}, commas/20w {commas:.2f}")
    directive = len(re.findall(r"^\s*(-\s*)?(It )?[Ss]hould\b", desc, re.M))
    out("WARN" if directive >= 3 else "PASS", "no 'Should ...' directive list", f"{directive} lines start with Should")
    process = re.findall(r"(every (single )?file|entire (repo|repository)|step by step|make sure to run|you must)", desc, re.I)
    out("WARN" if process else "PASS", "no process instructions to the solver (DQ inferable)", ", ".join(x[0] for x in process))
    if a.category:
        bugish = re.search(r"\b(broken|doesn'?t|dont|don't|not being|wrong|instead of|fails?|crash|error|currently)\b", desc, re.I)
        askish = re.match(r"\s*(add|support|allow|let|implement|we want|we need|it would be)", desc, re.I)
        sugg = "feature_request" if askish and not (bugish and not askish) else ("bugfix" if bugish else a.category)
        out("WARN" if sugg != a.category else "PASS", "category matches description shape", f"chosen {a.category}, shape suggests {sugg}")
    if a.last_accepted:
        old = Path(a.last_accepted).read_text(encoding="utf-8")
        out("WARN" if old.strip() != desc.strip() else "PASS", "description unchanged since last accepted text",
            "changed: every earlier run is void and DQ re-runs" if old.strip() != desc.strip() else "")

    # --- test patch ---
    tfiles = [b for _, b in patch_files(tp)]
    out("PASS" if "test.sh" in tfiles else "FAIL", "test.patch adds test.sh")
    sh_body = tp.split("b/test.sh", 1)[1].split("\ndiff --git", 1)[0] if "b/test.sh" in tp else ""
    modes = all(re.search(rf"\b{m}\b", sh_body) for m in ("base", "new"))
    out("PASS" if modes else "FAIL", "test.sh has distinct base and new modes")
    out("PASS" if re.search(r"new file mode 100755[\s\S]{0,200}b/test.sh|b/test.sh[\s\S]{0,200}new file mode 100755", tp) else "FAIL",
        "test.sh is executable (100755)")
    hunks_bad = re.findall(r"^\+@@ ", tp, re.M)
    out("FAIL" if hunks_bad else "PASS", "no malformed hunk headers", f"{len(hunks_bad)} '+@@' lines")
    words = re.findall(r"\b(graded?|grader|hidden tests?|platform|olympus|reference solution|rollout|solver|cheat\w*)\b", tp, re.I)
    out("FAIL" if words else "PASS", "no process words in test.patch (AR Tests Blocker)", ", ".join(sorted(set(x.lower() for x in words))[:8]))
    pred = [f for f in tfiles if re.search(r"(^|/)(test_[a-z]+\.py|[a-z]+_test\.go|tests?\.rs)$", f) and not re.search(r"[0-9a-f]{4,}|_[a-z]+_[a-z]+", Path(f).stem)]
    out("WARN" if pred else "PASS", "test file names not predictable (add a short hash suffix)", ", ".join(pred[:4]))
    stray = [f for f in tfiles if re.search(r"\.(patch|orig|rej|log|xml)$|(^|/)(eval|wip\d+)/", f)]
    out("FAIL" if stray else "PASS", "no stray files in test.patch", ", ".join(stray[:4]))

    # --- solution patch ---
    sfiles = [b for _, b in patch_files(sp)]
    overlap = set(sfiles) & set(tfiles)
    out("FAIL" if overlap else "PASS", "solution.patch and test.patch touch different files", ", ".join(sorted(overlap)))
    sp_tests = [f for f in sfiles if re.search(r"(^|/)tests?/|_test\.go$|test_[^/]+\.py$", f)]
    out("WARN" if sp_tests else "PASS", "solution.patch adds no tests", ", ".join(sp_tests[:4]))
    stray = [f for f in sfiles if re.search(r"\.(patch|orig|rej|log)$|(^|/)(eval|wip\d+)/", f)]
    out("FAIL" if stray else "PASS", "no stray files in solution.patch", ", ".join(stray[:4]))
    for name, body in (("test.patch", tp), ("solution.patch", sp)):
        na = [l for l in body.splitlines() if l.startswith("+") and any(ord(c) > 127 for c in l)]
        out("WARN" if na else "PASS", f"{name} added lines ASCII", f"{len(na)} lines with non-ASCII")
    # vet 2026-11-06: antivirus removed malware-like test fixtures from the worktrees and a folder-wide git diff put
    # their deletion into test.patch; export patches from explicit paths and never ship a deletion by accident.
    for name, body in (("test.patch", tp), ("solution.patch", sp)):
        dels = re.findall(r"^diff --git a/(\S+) b/\S+\ndeleted file mode", body, re.M)
        out("FAIL" if dels else "PASS", f"{name} deletes no file", ", ".join(dels[:3]))
    grader = re.findall(r"^\+.*#.*\b(for the (tests?|grader)|hidden test|so the test passes)\b", sp, re.M | re.I)
    out("FAIL" if grader else "PASS", "no grader-directed comments in solution (AR S4)")

    # --- Dockerfile ---
    if df:
        # The platform reads a RUN with its "\" continuation lines as one command (vet 2026-11-06: go test -run '^$' on a
        # continuation line FAILED "Dockerfile guidelines", although it runs no test).
        joined = re.sub(r"\\[ \t]*\n", " ", df)
        runs_tests = re.findall(r"^RUN .*\b(pytest|go test|go vet|cargo test|npm test|tox)\b.*$", joined, re.M)
        out("FAIL" if runs_tests else "PASS", "Dockerfile does not run tests during build", runs_tests[0][:80] if runs_tests else "")
        # vet 2026-11-06: ENV GOTOOLCHAIN=go1.x with no explicit install FAILED "Dockerfile guidelines" ("never installs
        # or activates" the toolchain), although go downloads it; install the pinned release with its SHA-256 instead.
        tc = re.search(r"^ENV GOTOOLCHAIN=(go[0-9.]+)", df, re.M)
        installs = re.search(r"go\$\{?GO_VERSION\}?|go[0-9.]+\.linux-amd64\.tar\.gz", joined) and "sha256sum" in joined
        out("FAIL" if tc and not installs else "PASS", "Go toolchain installed explicitly (pinned + SHA-256), not only GOTOOLCHAIN",
            tc.group(0) if tc and not installs else "")
        # vet 2026-11-06: "Image is not rebuild-safe ... downloads a file at build time from a URL that isn't
        # version-locked" for curl "https://go.dev/dl/go${GO_VERSION}..." - the check reads the URL literally, so a
        # build-time fetch needs the version written in the URL itself (no ${VAR}).
        fetches = re.findall(r"(?:curl|wget)[^\n]*?(https?://\S+)|^ADD\s+(https?://\S+)", joined, re.M)
        urls = [u for pair in fetches for u in pair if u]
        unlocked = [u for u in urls if "$" in u or not re.search(r"\d+\.\d+", u)]
        out("FAIL" if unlocked else "PASS", "build-time downloads use a literal versioned URL (Harbor rebuild-safe)",
            unlocked[0][:80] if unlocked else "")
        # user rule 2026-11-06: never write comments in a Dockerfile (WARN, not FAIL: the vet unused-suppression task
        # kept its locked, commented one)
        comments = [l for l in df.splitlines() if l.lstrip().startswith("#") and not l.lstrip().startswith("# syntax=")]
        out("WARN" if comments else "PASS", "no comments in the Dockerfile (user rule)", f"{len(comments)} comment lines")
        out("PASS" if re.search(r"^FROM public\.ecr\.aws/d3j8x8q7/olympus-base-[a-z]+:latest", df, re.M) else "WARN",
            "FROM the platform base image (public.ecr.aws/d3j8x8q7/olympus-base-<lang>:latest)")
        out("WARN" if re.search(r"git (clone|fetch)|curl .*github", df) else "PASS", "Dockerfile builds from the checked-out repo (no clone)")
    else:
        out("FAIL", "Dockerfile present")

    fails = results.count("FAIL")
    print(f"\n{fails} FAIL, {results.count('WARN')} WARN")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
