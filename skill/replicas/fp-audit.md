# Replica: false-pass review of every passing agent run (after the user's rollout)

Read `common.md` first. Input: the description, the reference repo, and the runs in `runs/` (each `verdict.txt`,
`solution.patch`). Audit every run whose verdict is PASS_LEGITIMATE. Question per run: does it deserve its pass? The
site's false-pass panel asks the same.

## Procedure
1. List the description's promises (one observable outcome each, scope sentences included).
2. Design diff, not test replay: read the run's patch and, for each promise, write how its design handles it and how
   the reference handles it. Look for: a fixed cap or limit inside a promise, a mode or path the run skips, a shortcut
   that only works for the tested inputs, state that is not reset or kept, an ordering the run gets wrong.
3. For each difference, build the smallest realistic input that makes the run break a promise while the reference
   keeps it. Trace both with file:line, and run it on both when the task image is available (one container at a
   time, through the launcher's dockrun.py command): the site's panel replays each judge's probe on the reference and
   drops a probe the reference also fails.
4. For every probe that separates the run from the reference, record three columns before any verdict: the
   description sentence it rests on; the behaviour before the change on that input (run or read the base code and
   the upstream test that pinned it); the origin of the reference's rule (a platform finding, a stated sentence, or
   the builder's own review round). A rule that is the builder's alone, unstated and untested, makes the probe a
   note for the owner, not a NOT DESERVED. A run also keeps its pass only if it passes the repository's own tests
   (`test.sh base`): say when you could not check that.

## A pass is NOT DESERVED only if ALL hold
- it breaks a quoted sentence of the description;
- the input is legal, in scope (setup line and scope sentences) and realistic;
- the failing case is concrete and traced (a run reproduces it when possible);
- the reference gets that case right;
- the sentence has one reading.
Style, hardening, contrived inputs, unstated behaviour and out-of-scope modes are notes, never NOT DESERVED.

## Output schema (JSON)
```
{"runs": [{"run": str, "verdict": "DESERVED|NOT_DESERVED",
 "differences": [{"promise": str, "run": str, "reference": str, "failingCase": str, "allConditionsHold": bool,
                  "whyNot": str}],
 "groundedTestToAdd": str | null}], "summary": str}
```
`groundedTestToAdd` (only when NOT_DESERVED): one test on the quoted sentence that the run fails and the reference
passes (situations FP-1). Never weaken the reference.

Independence: do not open other reviewers' reports (eval/sweep-*, eval/claude2/, eval/replica/ other than your own output, eval/codex/, eval/triage-*) before writing your own result.
