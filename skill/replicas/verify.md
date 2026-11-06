# Replica: finding verification (second pass on sq / fairness / ar findings)

Read `common.md` first. You receive candidate findings from earlier replica runs (paths in the brief). You did not
write them and you owe them nothing. For each finding with severity high or medium (sq issues, ar issues of every field, each fairness `partial`/`no` row
and coverage suggestion), decide KEEP or DROP.

DROP when any one holds (state which, with evidence):
1. Reading: the finding depends on one of two reasonable readings of a description sentence (e.g. "the end" at
   assignment time vs at lookup time), or on behaviour the description does not state.
2. Today's behaviour: the solution does what the repository already does for the equivalent plain case, and the
   description asks for that.
3. Scope: the input or mode is outside the setup line or scope sentences.
4. Realism: the failing case needs an event sequence the real framework cannot produce in the stated mode (trace it
   through the real classes), or a contrived input no user of this feature would send.
5. Code: the trace is wrong (the cited line does not do what the finding says; another path handles it). Quote the
   line that handles it.
6. Duplicate of another kept finding.
7. Combination corner: the gap appears only when the requirement is combined with a non-default setting, a rare
   setup or an extra condition the description never mentions, while the requirement's central case is tested
   (e.g. a start position combined with an unusual reset policy). The site's reviewer does not raise these.
For tests-side findings also DROP when the evidence is only "no test combines X with Y" and no agent run or obvious
wrong design shows that combination being got wrong.
Judge the defect, not the story. If the finding's scenario is wrong or longer than needed but its core (a promise
that fails on a real path) holds with a shorter realistic scenario, KEEP it and write the corrected scenario in
`evidence`. Drop for realism or code only when no realistic scenario breaks the promise.
Before any `code` or `realism` drop, do this and report it in `evidence`:
1. State the core of the finding in one line: the location and the state it says is lost, kept wrongly, or never
   resolved (ignore the consequence the finder claimed: abrupt stop, wrong value, hang).
2. Check that core against EVERY promise of the description with the simplest realistic follow-up events: a restart,
   the partition or resource coming back, old records expiring (retention), a later read by another user, shutdown.
3. If any promise breaks, KEEP with the corrected scenario. If you notice a possible alternative scenario, verify it
   now; never leave it NOT VERIFIED and drop.
KEEP only when none holds: quote the sentence it breaks, confirm the failing case step by step against the code.
For tests-side findings (fairness/ar): KEEP only if a plausible wrong implementation (one an engineer or coding agent
would write) passes every current test (check each test that could catch it). The finder's example may be out of
scope or unrealistic: before dropping, look for the simplest IN-SCOPE wrong implementation that uses the same gap
(e.g. base mode omits the lifecycle tests of a method the patch edits: a wrong implementation that drops one existing
step of that method passes). KEEP if one exists.
Exclusion sentences: "does not apply to X", "X is not covered", "only needs to work on Y" remove the requirement for
X; they do not forbid handling X, and leaving X untested is not a gap. Only a sentence that says X must keep today's
behaviour ("acts as it currently does", "should continue to use") needs a test for X.

## Output schema (JSON)
```
{"verdicts": [{"source": "sq-r1a|fairness-r1|ar-r1|...", "id": "<title or requirement>", "severity": str,
               "decision": "KEEP|DROP", "dropReason": "reading|today|scope|realism|code|duplicate|combination|null",
               "evidence": str}],
 "kept": {"solution_high": int, "solution_medium": int, "tests_gaps": int, "tests_unfair": int,
          "description_major": int},
 "bandsAfterVerification": {"description": 1-3, "tests": 1-3, "solution": 1-3},
 "summary": str}
```

Bands after verification: 1 if a kept High in that field, 2 if only kept Medium (description: presentation-only
issues give 2), else 3. Evidence from agent runs (a passer that misses a stated boundary) is never dropped for
reasons 1 or 7.
