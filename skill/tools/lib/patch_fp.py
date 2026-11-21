#!/usr/bin/env python3
"""patch_fp.py <test.patch> <solution.patch>: the three fingerprints of the fast hand-over check, printed as
`TS HT SOL` (12 hex digits each).

TS = the test.sh section of test.patch: the clean-repository base run depends on it alone, because base mode runs
no file that test.patch adds; HT = the other sections of test.patch (the hidden tests); SOL = solution.patch.
A test patch whose other files do not look like test files (no `test` or `spec` in the name, not under a tests,
testdata or spec folder) is refused (exit 2): base mode could run or read such a file, so root's baseline would
depend on it and a snapshot keyed by TS alone would be stale.
"""
import hashlib
import re
import sys

TESTLIKE = re.compile(r"(^|/)(tests?|testdata|__tests__|spec)/|[^/]*(test|spec)[^/]*$", re.I)


def fingerprints(test_patch, solution_patch):
    parts = re.split(rb"(?m)^(?=diff --git )", test_patch)
    runner = [p for p in parts if p.startswith(b"diff --git a/test.sh ")]
    hidden = [p for p in parts if p and not p.startswith(b"diff --git a/test.sh ")]
    if len(runner) != 1:
        raise ValueError("test.sh is not in the test patch exactly once")
    for part in hidden:
        name = part.split(b"\n", 1)[0].split(b" b/", 1)[-1].decode(errors="replace")
        if not TESTLIKE.search(name):
            raise ValueError(f"the test patch holds a file that base mode may run or read: {name}")
    digest = lambda chunks: hashlib.sha256(b"".join(chunks)).hexdigest()[:12]
    return digest(runner), digest(hidden), digest([solution_patch])


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[0], file=sys.stderr)
        return 2
    try:
        with open(argv[0], "rb") as f, open(argv[1], "rb") as g:
            print(*fingerprints(f.read(), g.read()))
    except (OSError, ValueError) as exc:
        print(f"patch_fp: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
