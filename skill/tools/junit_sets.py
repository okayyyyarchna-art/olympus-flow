#!/usr/bin/env python3
"""The set checks of the platform's verifySolution over three JUnit files.

usage: junit_sets.py <baseline.xml> <new.xml> <after.xml>
baseline = base mode run by root with the tests applied and no solution; new = new mode with the solution; after =
base mode with the solution (both as uid 1000). Prints the five sets and VERDICT PASS or FAIL (exit 1): baseline
failures; new cases not passing; new cases that the baseline also has; after extras (cases of the after run that are
neither baseline passes nor new cases and are not skipped); baseline passes not passing in the after run.
A case is classname::name, as in the rest of the kit.
"""
import sys
import xml.etree.ElementTree as ET


def cases(path):
    """{case id: pass | fail | skip} of one JUnit file."""
    out = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        name, classname = case.get("name", ""), case.get("classname", "")
        cid = f"{classname}::{name}" if classname else name
        if case.find("failure") is not None or case.find("error") is not None:
            out[cid] = "fail"
        elif case.find("skipped") is not None:
            out[cid] = "skip"
        else:
            out[cid] = "pass"
    return out


def check(base, new, after):
    """The five sets verifySolution rejects; every one must be empty."""
    p2p = {i for i, s in base.items() if s == "pass"}
    return {
        "baseline failures": {i for i, s in base.items() if s == "fail"},
        "new cases not passing": {i for i, s in new.items() if s != "pass"},
        "new cases that the baseline also has": set(new) & set(base),
        "after extras (not a baseline pass, not a new case, not skipped)":
            {i for i, s in after.items() if s != "skip" and i not in p2p and i not in new},
        "baseline passes not passing in the after run": {i for i in p2p if after.get(i) != "pass"},
    }


def report(base, new, after):
    """Print the counts, the five sets (first 20 ids each) and the verdict; True when every set is empty."""
    sets = check(base, new, after)
    print(f"baseline {len(base)} cases: pass {sum(s == 'pass' for s in base.values())} "
          f"skip {sum(s == 'skip' for s in base.values())}; new {len(new)} cases; after {len(after)} cases")
    for title, ids in sets.items():
        print(f"{title}: {len(ids)}")
        for i in sorted(ids)[:20]:
            print("  -", i)
    good = not any(sets.values())
    print("VERDICT", "PASS" if good else "FAIL")
    return good


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    base, new, after = (cases(p) for p in argv)
    return 0 if report(base, new, after) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
