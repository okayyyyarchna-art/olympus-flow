# Local checks: what runs, on which model, and how to decide

Design principle (from 16 tasks): our checks found most problems; our triage threw them away. So the check system has
three layers and one decision rule, and it runs once per stage, not in loops.

## Layer 1: deterministic gates (no model; best proof record)
| Gate | Tool | Pass bar | Platform check it predicts |
|---|---|---|---|
| Text + patch prechecks | `tools/precheck.py pkg` | 0 FAIL | prechecks stages (ASCII, URL, word cap, category, test.sh modes, Dockerfile, names) |
| Recurring test findings | `tools/tests_lint.py pkg repo` | 0 FAIL, REVIEW lines fixed or justified | AR T1/T3/T5/T7 patterns (base mode misses edited files' tests, vacuous all(), private state, mock pins, wall-clock waits, replaced framework methods, lifecycle not completed) |
| Docker proof | `proof.py base pkg [--stability]` | PROOF PASS: build; base passes / new all fail on clean; solved twice identical; uid 12345 + `env -i`; clean new < 300 s; 6+6 identical | verifyBuild, verifyTests, verifySolution (offlineUid), verifyFlakiness, T6 |
| Valid battery | `replay_patches.sh` on variants/valid-*.patch | every new test + base suite pass for >= 3 designs | fairness "Unfair" / AR T5 / rollout FAIL_TEST_BROKEN |
| Wrong battery | `replay_patches.sh` on variants/wrong-*.patch | each fails >= 1 new test, no hang | fairness partial / AR T3-T4 |
| Base pins | junit of base mode per valid variant | no base failure on a valid design (else exact deselect) | rollout runs lost to pins (T12 15/22) |

## Layer 2: platform replicas (Codex, GPT Sol 6.1 at medium effort for every check; user rule 2026-11-05)
The model is not the check. Each replica = platform output schema + procedure (branch inventory, exit-after-mutation,
mode x failure matrix, break attempts) + knowledge catalog of every way the site passed or failed packages
(replicas/knowledge/) + evidence rules; then an independent verify pass keeps or drops each finding.
| Replica | Prompt | Knowledge | Output schema = platform's |
|---|---|---|---|
| fairness (TQ per test) | replicas/fairness.md | tests | requirements + coverage + per-test fairness/concerns + suggestions |
| sq | replicas/sq.md | solution, tests | comp x/3 + quality x/3 + issues quoting a sentence; branch inventory + break attempts |
| dq (+ 8 task criteria) | replicas/dq.md | description | comments by category + separate-asks judgement + 8 task criteria + text prechecks |
| ar | replicas/ar.md | all three | bands D/T/S + issues (category, claim, evidence, failingCase, loadBearingCheck) |
| verify | replicas/verify.md | solution, tests | KEEP/DROP per finding with a fixed reason; bands after verification |
Order (user, 2026-11-06): S5 sweep 1 -> fix all -> S5b sweep 2 -> fix all (no gate in between) -> S5c strict FP audit
on every passer -> S6b before every hand-over: 1 sweep + `tools/round.sh <task> g1` and `g2`, the only platform-style
replica runs (sq runs twice: the platform's SQ verdict varies between runs on the same package).
Why a separate verify pass: calibration showed deep sq/ar runs find the platform's real Highs AND raise reading-
dependent or combination-corner findings the platform never raises; a fresh-context verifier with fixed drop rules
removes the second kind (generate, then verify). The gate counts only verified findings.
Calibration against platform verdicts on real packages: see `CALIBRATION.md` (agreement table and prompt versions).

## Layer 3: second opinions (only where calibration says they add)
- FP on agent passers: 4 x Sonnet medium + Codex GPT Sol 6.1 medium (P4 in platform.md). Sonnet x4 matched the platform
  panel on T12; a primed Codex lane over-flagged once.
- Claude Opus in-process SQ/AR only when the Codex replica and a reproduction disagree, as a tie-breaker.

## Decision rule (the part that failed before)
For every finding from any layer:
1. Reproduce it (a run of the failing case, a wrong variant passing, or base vs solved comparison). 10 minutes max.
2. Reproduced and inside a stated promise -> fix (solution or test) in this batch. Never "keep", "residual", "Low",
   "risk".
3. Reproduced but outside every sentence -> no change (it is unstated; testing it would be unfair).
4. Not reproduced -> contest note with the evidence; no change; never write a test for it.
5. Same item from two independent sources -> treat as reproduced.
After the batch: deterministic gates again, then only the replicas whose input changed (tag r2). No third cycle on one
promise (situations X-2).

## What not to run (no recorded value)
Blind solves, repeated platform_sim runs, 1000-seed sweeps, full review rounds after every change, local pass-rate
estimates for the gate.
