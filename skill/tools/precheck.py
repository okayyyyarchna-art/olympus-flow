#!/usr/bin/env python3
"""Deterministic replica of the platform prechecks plus our packaging checks. No model, runs in a second.

usage: python precheck.py <package-dir> [--category bugfix|feature_request] [--last-accepted <description.md>]
                          [--test-sh <test.sh>]
Package dir: description.md, test.patch, solution.patch, Dockerfile (test.sh lives inside test.patch). A file that is
not there yet is skipped with a SKIP line, so the Dockerfile-only stage (pkg/Dockerfile alone) runs the Dockerfile
rules. --test-sh checks one test.sh file on its own (a template) for process words.
Exit 0 = no FAIL. Prints one line per check: PASS / WARN / FAIL / SKIP with the reason.

Every rule here comes from a recorded platform result (platform results since 2026-11-05; BACKLOG rows named inline):
non-ASCII and URL fails, word cap, category shape, test.sh modes, malformed hunks, tests run during the Docker
build, process words in the test patch and in test.sh (AR Tests 0/3 Blocker), stray files, executable bit, em-dashes /
hard wrap (the "doesn't look AI-generated" precheck), predictable test file names, the allowed FROM lines, the
sbin PATH, the writable /app, the reason block above a deviating RUN, the Codex-filter words in names.
"""
import argparse
import re
import sys
from pathlib import Path

results = []

# The platform Dockerfile check (2026-11-13, #142): "Dockerfile must start with" one of these lines; --platform is rejected.
ALLOWED_FROM = ("FROM public.ecr.aws/x8v8d7g8/mars-base:latest",
                "FROM public.ecr.aws/d3j8x8q7/olympus-base:latest",
                "FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest")
# Words the Auto Review Tests lane reads as process leaks in a test runner (#152; a faust task lost Tests 0/3 to them).
# HARD words fail; SOFT words warn because accepted runners carry them as domain words (oss-rebuild's pristine view).
TEST_SH_HARD = re.compile(r"(?<![a-z])(grading|grade_roots|graded?|graders?|hidden_paths?|hidden[ _-](?:tests?|files?|paths?)|"
                          r"solvers?|cheat\w*|olympus|rollouts?|reference solution)(?![a-z])", re.I)
TEST_SH_SOFT = re.compile(r"(?<![a-z])(pristine|platform)(?![a-z])", re.I)


def out(level, name, msg=""):
    results.append(level)
    print(f"{level:4} {name}{': ' + msg if msg else ''}")


def site_words(text):
    return len([w for w in re.split(r"[\s\-/]+", text.strip()) if w])


def patch_files(patch):
    return re.findall(r"^diff --git a/(\S+) b/(\S+)", patch, re.M)


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def flagged_words():
    """The Codex-filter word list of lib/check_codex_brief.sh (#165: a task folder named with one blocks every replica)."""
    script = Path(__file__).resolve().parent / "lib" / "check_codex_brief.sh"
    m = re.search(r"^words='([^']*)'", script.read_text(encoding="utf-8"), re.M) if script.exists() else None
    return re.compile(m.group(1), re.I) if m else None


def test_sh_lines(tp):
    """The added lines of test.sh inside test.patch (test.sh is always a new file there)."""
    if "+++ b/test.sh" not in tp:
        return []
    body = tp.split("+++ b/test.sh", 1)[1].split("\ndiff --git", 1)[0]
    return [l[1:] for l in body.splitlines() if l.startswith("+") and not l.startswith("+++")]


def process_words(lines):
    hard = [f"{n}: {m.group(0)}" for n, l in enumerate(lines, 1) for m in TEST_SH_HARD.finditer(l)]
    soft = [f"{n}: {m.group(0)}" for n, l in enumerate(lines, 1) for m in TEST_SH_SOFT.finditer(l)]
    return hard, soft


def check_test_sh_words(lines, label):
    hard, soft = process_words(lines)
    out("FAIL" if hard else "PASS", f"no process words in {label} (AR Tests Blocker, #152; line: word)", ", ".join(hard[:8]))
    out("WARN" if soft else "PASS", f"no soft process words in {label} (pristine, platform; line: word)", ", ".join(soft[:8]))


def check_dockerfile(df):
    first = next((l.strip() for l in df.splitlines() if l.strip()), "")
    out("PASS" if first in ALLOWED_FROM else "FAIL", "Dockerfile first line is an allowed FROM line (no --platform, #142)",
        "" if first in ALLOWED_FROM else f"{first[:80]!r}; allowed: " + " | ".join(ALLOWED_FROM))
    # The platform reads a RUN with its "\" continuation lines as one command (vet 2026-11-06: go test -run '^$' on a
    # continuation line FAILED "Dockerfile guidelines", although it runs no test).
    joined = re.sub(r"\\[ \t]*\n", " ", df)
    # A runner at a command position only: `pip install pytest==7.4.4` (accepted faust Dockerfiles) is not a test run.
    runs_tests = re.findall(r"(?:^RUN\s+|&&\s*|;\s*|\|\s*)(?:python[0-9.]*\s+-m\s+)?((?:go test|go vet|pytest|cargo test|npm test|vitest run|jest|tox)\b[^\n&;|]*)", joined, re.M)
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
    # Rule (user 2026-11-06, amended 2026-11-07, vet task 6 accepted 2026-11-21): no comments in a Dockerfile, except one
    # block right above each RUN that deviates from the base image, stating why. The AI precheck failed vet's Go
    # reinstall once its "base has Go 1.26, go.mod needs 1.27.3" comment was removed (#139).
    lines = df.splitlines()
    blocks, prev = [], False
    for i, l in enumerate(lines):
        c = l.lstrip().startswith("#") and not l.lstrip().startswith("# syntax=")
        if c and not prev:
            blocks.append(i)
        prev = c

    def above_run(i):
        j = i
        while j < len(lines) and lines[j].lstrip().startswith("#"):
            j += 1
        return j < len(lines) and lines[j].lstrip().upper().startswith("RUN ")
    stray = [i + 1 for i in blocks if not above_run(i)]
    out("WARN" if stray else "PASS", "Dockerfile comments: only a reason block right above each deviating RUN (user rule)",
        f"{len(blocks)} reason blocks" + (f", not above a RUN at lines {stray}" if stray else ""))
    for i, l in enumerate(lines):
        if l.lstrip().upper().startswith("RUN ") and re.search(r"go[0-9.]+\.linux-amd64\.tar\.gz", l):
            has = i > 0 and lines[i - 1].lstrip().startswith("#")
            out("PASS" if has else "FAIL", "Go reinstall RUN has its reason block right above it (AI precheck failed vet without it, #139)",
                "" if has else f"line {i + 1}")
    # #153: ENV PATH without /usr/sbin and /sbin broke the platform's groupadd/useradd image step (verifyTests, verifySolution).
    for m in re.finditer(r"^ENV\b[^\n]*?\bPATH=(\S+)", df, re.M):
        value = m.group(1).strip('"')
        keeps = "$PATH" in value or "${PATH}" in value or all(d in value.split(":") for d in ("/usr/local/sbin", "/usr/sbin", "/sbin"))
        out("PASS" if keeps else "FAIL", "ENV PATH keeps /usr/local/sbin:/usr/sbin:/sbin (platform groupadd/useradd step, #153)",
            "" if keeps else value[:100])
    # #156: the Harbor oracle applies solution.patch in /app as uid 1000; /app owned by root and read-only for others
    # fails verifySolution with harbor_oracle_failed and no detail. chown to that user does the same job.
    writable = re.search(r"chmod -R a\+rwX(?: \S+)* /app(?=\s|$)|chown -R (?:1000:1000|model:model)(?: \S+)* /app(?=\s|$)", joined)
    out("PASS" if writable else "FAIL", "/app writable for every user at the end of the build (chmod -R a+rwX /app, #156)",
        "" if writable else "add `chmod -R a+rwX /app` (plus the caches test.sh writes) as the last RUN")
    out("WARN" if re.search(r"git (clone|fetch)|curl .*github", df) else "PASS", "Dockerfile builds from the checked-out repo (no clone)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg")
    ap.add_argument("--category", choices=["bugfix", "feature_request"])
    ap.add_argument("--last-accepted")
    ap.add_argument("--test-sh", help="a test.sh file to check for process words on its own (a template)")
    a = ap.parse_args()
    pkg = Path(a.pkg)
    desc_p = pkg / "description.md"
    if not desc_p.exists():
        desc_p = pkg / "task.md"
    desc = read(desc_p)
    tp = read(pkg / "test.patch")
    sp = read(pkg / "solution.patch")
    df = read(pkg / "Dockerfile")
    tfiles = [b for _, b in patch_files(tp)] if tp else []

    # --- names (#165): the replica briefs name the task path and the test files; a Codex-filter word there blocks them ---
    rx = flagged_words()
    if rx:
        folders = [p.name for p in (pkg.resolve(), pkg.resolve().parent) if p.name]
        hits = [n for n in folders if rx.search(n)]
        out("FAIL" if hits else "PASS", "task and package folder names avoid the Codex-filter words (lib/check_codex_brief.sh)", ", ".join(hits))
        if tp:
            tests = [f for f in tfiles if f != "test.sh"]
            names = [f for f in tests if rx.search(Path(f).name)]
            dirs = [f for f in tests if rx.search(Path(f).parent.as_posix())]
            out("FAIL" if names else "PASS", "hidden test file names avoid the Codex-filter words", ", ".join(names[:4]))
            out("WARN" if dirs else "PASS", "hidden test folders avoid the Codex-filter words (repo-owned folder: note it in the ledger)", ", ".join(dirs[:4]))

    # --- description ---
    if desc is None:
        out("SKIP", "description checks", "no description.md or task.md in the package yet")
    else:
        bad = [(i, ch) for i, ch in enumerate(desc) if ord(ch) > 127]
        out("FAIL" if bad else "PASS", "description ASCII only", f"{len(bad)} non-ASCII chars, first {bad[:3]}" if bad else "")
        urls = re.findall(r"\b[a-z][a-z0-9+.-]*://\S*|\bwww\.[a-z0-9-]+\.\S+", desc, re.I)
        out("FAIL" if urls else "PASS", "description has no URLs or scheme://", ", ".join(urls[:3]))
        w = site_words(desc)
        out("WARN" if w >= 250 else "PASS", "description site words (guidance: under 250; split on space - /)", str(w))
        out("FAIL" if w > 1000 else "PASS", "description platform ceiling (1000 site words)", str(w))
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
    if tp is None:
        out("SKIP", "test.patch checks", "no test.patch in the package yet")
    else:
        out("PASS" if "test.sh" in tfiles else "FAIL", "test.patch adds test.sh")
        sh_lines = test_sh_lines(tp)
        sh_body = "\n".join(sh_lines)
        modes = all(re.search(rf"\b{m}\b", sh_body) for m in ("base", "new"))
        out("PASS" if modes else "FAIL", "test.sh has distinct base and new modes")
        out("PASS" if re.search(r"new file mode 100755[\s\S]{0,200}b/test.sh|b/test.sh[\s\S]{0,200}new file mode 100755", tp) else "FAIL",
            "test.sh is executable (100755)")
        hunks_bad = re.findall(r"^\+@@ ", tp, re.M)
        out("FAIL" if hunks_bad else "PASS", "no malformed hunk headers", f"{len(hunks_bad)} '+@@' lines")
        words = re.findall(r"\b(graded?|grader|hidden tests?|olympus|reference solution|rollout|solver|cheat\w*)\b", tp, re.I)
        out("FAIL" if words else "PASS", "no process words in test.patch (AR Tests Blocker)", ", ".join(sorted(set(x.lower() for x in words))[:8]))
        # "platform" is a domain word in accepted hidden tests (vet task 6: "an entry that gains a platform field"), so it warns.
        soft = re.findall(r"^\+.*\b(platform)\b", tp, re.I | re.M)
        out("WARN" if soft else "PASS", "no soft process words in test.patch (platform)", f"{len(soft)} added lines")
        if sh_lines:
            check_test_sh_words(sh_lines, "test.sh")
        pred = [f for f in tfiles if re.search(r"(^|/)(test_[a-z]+\.py|[a-z]+_test\.go|tests?\.rs)$", f) and not re.search(r"[0-9a-f]{4,}|_[a-z]+_[a-z]+", Path(f).stem)]
        out("WARN" if pred else "PASS", "test file names not predictable (add a short hash suffix)", ", ".join(pred[:4]))
        stray = [f for f in tfiles if re.search(r"\.(patch|orig|rej|log|xml)$|(^|/)(eval|wip\d+)/", f)]
        out("FAIL" if stray else "PASS", "no stray files in test.patch", ", ".join(stray[:4]))

    # --- solution patch ---
    if sp is None:
        out("SKIP", "solution.patch checks", "no solution.patch in the package yet")
    else:
        sfiles = [b for _, b in patch_files(sp)]
        if tp is not None:
            overlap = set(sfiles) & set(tfiles)
            out("FAIL" if overlap else "PASS", "solution.patch and test.patch touch different files", ", ".join(sorted(overlap)))
        sp_tests = [f for f in sfiles if re.search(r"(^|/)tests?/|_test\.go$|test_[^/]+\.py$", f)]
        # vet task 2: platform SQ Code Quality 1/3, "No regression test accompanies the bug fix" (the repo REVIEW.md rule 4:
        # a bug fix needs a test that fails without the fix). The reference carries its own test, in the repo's style.
        out("PASS" if sp_tests else "WARN", "solution.patch adds its own regression test (repo review rules)", ", ".join(sp_tests[:4]))
        stray = [f for f in sfiles if re.search(r"\.(patch|orig|rej|log)$|(^|/)(eval|wip\d+)/", f)]
        out("FAIL" if stray else "PASS", "no stray files in solution.patch", ", ".join(stray[:4]))
        grader = re.findall(r"^\+.*#.*\b(for the (tests?|grader)|hidden test|so the test passes)\b", sp, re.M | re.I)
        out("FAIL" if grader else "PASS", "no grader-directed comments in solution (AR S4)")
    for name, body in (("test.patch", tp), ("solution.patch", sp)):
        if body is None:
            continue
        na = [l for l in body.splitlines() if l.startswith("+") and any(ord(c) > 127 for c in l)]
        out("WARN" if na else "PASS", f"{name} added lines ASCII", f"{len(na)} lines with non-ASCII")
        # vet 2026-11-06: antivirus removed malware-like test fixtures from the worktrees and a folder-wide git diff put
        # their deletion into test.patch; export patches from explicit paths and never ship a deletion by accident.
        dels = re.findall(r"^diff --git a/(\S+) b/\S+\ndeleted file mode", body, re.M)
        out("FAIL" if dels else "PASS", f"{name} deletes no file", ", ".join(dels[:3]))

    # --- Dockerfile ---
    if df:
        check_dockerfile(df)
    else:
        out("FAIL", "Dockerfile present")

    # --- a test.sh on its own (the template) ---
    if a.test_sh:
        check_test_sh_words(Path(a.test_sh).read_text(encoding="utf-8").splitlines(), a.test_sh)

    fails = results.count("FAIL")
    print(f"\n{fails} FAIL, {results.count('WARN')} WARN, {results.count('SKIP')} SKIP")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
