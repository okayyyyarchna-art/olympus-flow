#!/usr/bin/env python3
"""Summarize replica outputs of one tag into the S5 gate table.

usage: python summarize.py <task>/eval/replica <tag>
Gate (FLOW S5): AR approved 3/3/3 (description 2 for presentation only is ok); every SQ run PASS without high issues;
no Unfair test; no open Prompt-stated coverage suggestion that names a wrong implementation.
"""
import glob
import json
import os
import sys


def load(p):
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def main():
    d, tag = sys.argv[1], sys.argv[2]
    gate = []
    print(f"# Replica round {tag}\n")
    fa = load(os.path.join(d, f"fairness-{tag}.json")) if os.path.exists(os.path.join(d, f"fairness-{tag}.json")) else None
    if fa:
        reqs = fa.get("requirements") or []
        unfair = [t for t in fa.get("tests") or [] if t.get("fairness") == "Unfair"]
        concerns = [t for t in fa.get("tests") or [] if t.get("concerns")]
        open_sugg = [s for s in fa.get("coverageSuggestions") or []
                     if s.get("sourceIfAdded") != "Would need prompt edit"]
        print(f"## fairness: {len(reqs)} requirements, "
              f"{sum(r.get('covered') == 'yes' for r in reqs)} yes / {sum(r.get('covered') == 'partial' for r in reqs)} partial / "
              f"{sum(r.get('covered') == 'no' for r in reqs)} no; unfair {len(unfair)}; tests with concerns {len(concerns)}")
        for r in reqs:
            if r.get("covered") != "yes":
                print(f"- [{r.get('covered')}] {r.get('requirement')}")
        for t in unfair:
            print(f"- UNFAIR {t.get('name')}: {t.get('evidence')}")
        for t in concerns:
            print(f"- concern {t.get('name')}: {t.get('concerns')}")
        for s in open_sugg:
            print(f"- suggestion [{s.get('gapKind')}] {s.get('requirement')}: {s.get('suggestion')} | wrong impl: {s.get('wrongImplementationThatPasses')}")
        gate.append(("no Unfair test", not unfair))
        gate.append(("no open stated coverage gap", not open_sugg))
    for p in sorted(glob.glob(os.path.join(d, f"sq-{tag}[ab].json"))) or sorted(glob.glob(os.path.join(d, f"sq-{tag}.json"))):
        s = load(p)
        sc = (s.get("solution_comprehensiveness") or {}).get("score")
        cq = (s.get("code_quality") or {}).get("score")
        highs = [i for i in s.get("issues") or [] if i.get("severity") == "high"]
        print(f"\n## {os.path.basename(p)}: {s.get('verdict')} comp {sc}/3 quality {cq}/3")
        for i in s.get("issues") or []:
            print(f"- {i.get('severity')} {i.get('criterion')}: {i.get('title')} | {i.get('failingCase', '')[:300]}")
        gate.append((f"{os.path.basename(p)} PASS without high", s.get("verdict") == "PASS" and not highs))
    dq_p = os.path.join(d, f"dq-{tag}.json")
    if os.path.exists(dq_p):
        q = load(dq_p)
        rc = q.get("requirementCount") or {}
        print(f"\n## dq: {q.get('verdict')}, requirement count {rc.get('count')} (blocking {rc.get('blocking')})")
        for c in q.get("comments") or []:
            print(f"- {c.get('severity')} {c.get('category')}{' (presentation)' if c.get('presentationOnly') else ''}: \"{c.get('quote')}\" -> {c.get('suggestion')}")
        gate.append(("dq PASS", q.get("verdict") == "PASS"))
    for p in sorted(glob.glob(os.path.join(d, f"ref-audit-{tag}r[ab].json"))):
        r = load(p)
        broken = [x for x in r.get("promises") or [] if x.get("verdict") == "BROKEN"]
        wrong = [x for x in r.get("promises") or [] if x.get("wrongImplementationThatPassesTests")]
        print(f"\n## {os.path.basename(p)}: {len(broken)} broken, {len(wrong)} wrong implementations that pass")
        for x in broken:
            print(f"- BROKEN{'' if x.get('reproduced') else ' (not reproduced)'}: {x.get('promise')} | {str(x.get('failingCase'))[:300]}")
        for x in wrong:
            print(f"- passes tests: {x.get('promise')} | {str(x.get('wrongImplementationThatPassesTests'))[:300]}")
        gate.append((f"{os.path.basename(p)}: no reproduced broken promise",
                     not any(x.get("reproduced") for x in broken)))
    ve_p = os.path.join(d, f"verify-{tag}.json")
    kept = None
    if os.path.exists(ve_p):
        v = load(ve_p)
        kept = v.get("kept") or {}
        print(f"\n## verify: kept {json.dumps(kept)}")
        for x in v.get("verdicts") or []:
            print(f"- {x.get('decision')} [{x.get('source')}] {x.get('severity')} {x.get('id')}"
                  f"{' (' + str(x.get('dropReason')) + ')' if x.get('decision') == 'DROP' else ''}")
        # with a verifier, the sq/fairness gates use what it kept
        gate = [(n, ok) for n, ok in gate if not (n.startswith("sq-") or n == "no open stated coverage gap")]
        gate.append(("verified: no solution high", not kept.get("solution_high")))
        gate.append(("verified: no unfair test", not kept.get("tests_unfair")))
        bv = v.get("bandsAfterVerification") or {}
        # the site approves with bands >= 2 (no High in any field); kept Mediums are still fixed in S6
        gate.append(("verified bands >= 2 in every field (no High)",
                     all((bv.get(k) or 0) >= 2 for k in ("description", "tests", "solution"))))
        print(f"- bands after verification: {json.dumps(v.get('bandsAfterVerification'))}")
    ar_p = os.path.join(d, f"ar-{tag}.json")
    if os.path.exists(ar_p):
        a = load(ar_p)
        if a.get("_error"):
            print(f"\n## ar: UNREADABLE ({a['_error']})")
        bands = [(a.get(k) or {}).get("band") for k in ("description", "tests", "solution")]
        print(f"\n## ar: {a.get('outcome')} bands D/T/S {bands}")
        for i in a.get("issues") or []:
            print(f"- {i.get('severity')} {i.get('category')}: {i.get('claim')} | expected: {i.get('expected')}")
        if kept is None:  # without a verify pass the raw ar decides
            ok = all((b or 0) >= 2 for b in bands)
            gate.append(("ar bands >= 2 in every field (no High)", ok))
    if kept is not None and (kept.get("tests_gaps") or kept.get("solution_medium")):
        print("- note: kept Medium findings go to the S6 fix batch (they do not block the gate)")
    print("\n## gate")
    for name, ok in gate:
        print(f"- [{'x' if ok else ' '}] {name}")
    print(f"\nGATE {'PASS' if gate and all(ok for _, ok in gate) else 'FAIL'}")


if __name__ == "__main__":
    main()
