#!/usr/bin/env python3
"""junit_leaves.py <junit.xml> pass|fail|list-fails: the leaves of one test.sh run.

pass: every leaf passes and none is skipped (the suite with the solution); fail: every leaf fails and none is skipped
(T1 on the clean repository); both print one summary line, the first offending leaves, and exit 1 on an offender or
an empty report. list-fails: one `classname<TAB>name` line per failing leaf, for re-runs of single cases.
"""
import sys
import xml.etree.ElementTree as ET

path, want = sys.argv[1], sys.argv[2]
leaves = []
for case in ET.parse(path).getroot().iter("testcase"):
    if case.find("failure") is not None or case.find("error") is not None:
        status = "fail"
    elif case.find("skipped") is not None:
        status = "skip"
    else:
        status = "pass"
    leaves.append((case.get("classname", ""), case.get("name", ""), status))
if want == "list-fails":
    for classname, name, status in leaves:
        if status == "fail":
            print(f"{classname}\t{name}")
    sys.exit(0)
counts = {s: sum(leaf[2] == s for leaf in leaves) for s in ("pass", "fail", "skip")}
print(f"{len(leaves)} leaves: {counts['pass']} pass, {counts['fail']} fail, {counts['skip']} skipped (want every leaf {want})")
bad = [leaf for leaf in leaves if leaf[2] != want]
for classname, name, status in bad[:20]:
    print(f"   {status}: {name}")
sys.exit(1 if bad or not leaves else 0)
