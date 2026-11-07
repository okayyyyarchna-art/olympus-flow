# Gap sweep brief (S5, one round, every lane in parallel; user rule 2026-11-06)

You are one of several independent reviewers running at the same time. The goal of this round is to find EVERY gap
at once, not the most important one: a later round that finds one more gap is a failure of this round.

## Inputs (task folder given in your launch message)
- pkg/description.md: the only promises. Every sentence is a requirement, scope sentences included.
- pkg/test.patch: the hidden tests (test.sh + scripts). pkg/solution.patch: the reference.
- repo/: the pinned commit with both patches applied. base/: the pinned commit, untouched.
- eval/gates.md, eval/battery-*.log: the wrong designs the tests are already proven to catch. Do not report those again.

## What to produce: one sweep table per description sentence, complete
For each sentence, list EVERY row; never stop after the first finding.
| path | what the reference does (file:line) | a wrong implementation that would still pass every current test | the smallest fair test that fails it and passes the reference | verdict |
- path = every real way the sentence is reached: each entry point (each command, each saved-input format), each store,
  each mode, each kind of record that reaches the code (every selector, every finding source), empty input, two of a
  kind (multiplicity), first/last/order, repeated application, interaction with every other sentence.
- verdict per row: COVERED (an existing test fails that wrong implementation; name it), GAP (no test does; give the
  test), REFERENCE-BROKEN (the reference itself breaks the sentence on a legal input; give the input), UNFAIR (a current
  test asserts something no sentence states; quote the test line).

## Rules
- Quote the sentence and file:line for every claim. Run a check when you can; otherwise mark the row NOT VERIFIED.
- A GAP needs a concrete wrong implementation, not "coverage could be better".
- Style, hardening and behaviour no sentence states are notes, never GAP.
- INDEPENDENCE: do not open other reviewers' reports (eval/sweep-*, eval/claude2/, eval/replica/, eval/codex/,
  eval/triage-*) until your own report is written. The only coordinator data you may read is eval/gates.md and the
  newest eval/battery-*.log (wrong designs already proven caught).
- Read-only on pkg/, repo/, base/. Write only your report file (path in the launch message).

## Report
Your sweep tables, then three lists: GAPS (each with its test), REFERENCE-BROKEN (each with its input), UNFAIR (each with
the test line). End with counts per list.
