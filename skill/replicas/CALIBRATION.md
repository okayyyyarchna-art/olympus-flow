# Replica calibration against real platform verdicts (2026-11-05)

MODEL NOTE: the rounds below ran on gpt-5.6-terra (sq, dq) and gpt-5.6-sol (fairness, ar, verify). From 2026-11-05
22:00 every check runs on GPT Sol 6.1 medium (user rule); the check design is unchanged. Re-check round on Sol 6.1
medium: section at the end.

Method: exact pasted files downloaded with `olympus problems download`; repo at the pinned commit with both patches
applied; replicas run blind (no platform output in their inputs). Only platform verdicts that are fresh for those
files (not stale) are compared. The data and scripts of that run are not part of this repository
(`compare.py` prints the table).

Role of each package: a calibration package is a DETECTOR TEST with a known platform answer, not a model to copy.
Packages the platform failed (SetTable draft, #751 draft, elio gzip, window) test that our replicas catch what the
platform caught; packages the platform passed (accepted or approved) test that our replicas raise no false alarms.
What to build is modelled only on ACCEPTED tasks (templates/accepted, problem-design.md status column).

Packages: SetTable draft (SQ FAIL, 2 Highs), topic start (all pass, AR approved), standby promotion (all pass),
goka group-table writes (SQ PASS, fairness), elio gzip (SQ CQ 2/3 Medium, AR revision: 256 MiB passer + PDF
private-path test + P4), Burrow #751 description (DQ FAIL: ai_generated + over_specification).

## Version history (what each change fixed)
| Version | Change | Observed |
|---|---|---|
| sq v1 | promise-by-promise trace | PASS on all 4 PASS cases (correct); missed both SetTable Highs ("PASS by source trace": confirmed the design) |
| sq v2 | branch inventory + >= 12 break attempts | SetTable still PASS: saw both branches, judged them fine; elio: false High (audio detection for unknown names) |
| sq v3 | + exit-after-mutation table, + mode x failure-path matrix, + "a verified disproof drops the finding" | SetTable FAIL with the platform's send-error High (+ the platform's other branch found in the table); topic start: false High (reading-dependent) |
| verify v1 | separate fresh pass, fixed drop rules | dropped topic start's and elio's false Highs (reading); wrongly dropped SetTable's real send-error High over a bad scenario story |
| verify v2 | + "judge the defect, not the story", + combination-corner rule, runs after ar | final round below |
| fairness v1 | coverage yes/partial/no | far too strict: SetTable 11 partial vs platform 1, topic start 4 vs 0, standby 14 concerns vs 0 |
| fairness v2 | partial only for a plausible wrong implementation; concerns only when a correct implementation can fail | final round below |
| dq v1 | categories + count | #751 FAIL (match, same sentence flagged); standby falsely blocking (counted 12: split qualifiers) |
| dq v2 | merge qualifiers into the behaviour they refine; blocking at >= 11 | final round below |
| ar v1 | T/S/P rules + runs | elio: matched desc band 2 and the 256 MiB passer High; missed PDF private path; topic start and standby falsely tests band 1 (combination corners) |

| verify v3 | + restate the core and test it against every promise before a code/realism drop | SetTable: keeps the platform's exact High (accepted ack lost after retention) and drops the false crash story; topic start: keeps nothing |

## Final round f1 (final prompts, no catalogs; round.sh = fairness + sq x2 + dq -> ar -> verify)
| Package | Platform (fresh) | Local f1 (after verify) | Match |
|---|---|---|---|
| SetTable (draft) | SQ FAIL 2 High; AR (stale) tests band 1 | SQ High kept = platform High #1; tests band 1 (threaded path gap) | yes (High #2 found in an earlier sq run, not this one) |
| topic start | all PASS, AR 3/3/3 | all PASS, AR 3/3/3, nothing kept | yes |
| standby | all PASS, AR 3/3/3 | all PASS, AR 3/3/3, nothing kept | yes |
| elio gzip | AR revision: tests band 1 (256 MiB passer), desc 2 (P4); SQ PASS with CQ Medium | tests High (256 MiB passer) kept; SQ PASS; desc band 1 (P3) and dq count blocking | verdict yes; description stricter than site; CQ Medium missed |
| #751 description | DQ FAIL (ai_generated + over_specification) | DQ FAIL (count 12 blocking) | verdict yes, reason differs |
| goka | SQ PASS (AR stale) | SQ PASS x2; AR S1 High kept (failed reconciliation write) | no: open, not yet reproduced either way |

### Fix round on the extended packages (verify v4, dq v3, gate = no High in any field)
Changes, each from a package that went wrong: verify looks for the simplest in-scope wrong implementation before
dropping a tests gap (window); exclusions "does not apply to X" remove the requirement, only "keeps today's behaviour"
needs a test (orange-orm Cloudflare D1); DQ "too many requirements" judges separate asks, not a number (orange-orm
passed with 24 extracted requirements, gzip failed with 10); gate = bands >= 2 everywhere (the site approved
orange-orm with tests band 2).

| Package | Repo / language | Platform on these files | Local gate | Match |
|---|---|---|---|---|
| topic start | faust / Python | approved 3/3/3 | PASS 3/3/3 | yes |
| standby promotion | faust / Python | approved 3/3/3 | PASS 3/3/3 | yes |
| producer flush | faust / Python | approved, description band 2 (process instruction) | PASS 2/3/3, same sentence | yes |
| conditional writes | swift / Python | approved 3/3/3 | PASS 3/2/3 (one Medium: base mode drops 6 multipart tests) | yes (gate) |
| docker proxy | oss-rebuild / Go | approved 3/3/3 | PASS 3/3/3 | yes |
| folder history | elio / Rust | approved 3/3/3 | PASS 3/3/3 | yes |
| concurrency strategies | orange-orm / TypeScript | SQ PASS, DQ PASS (AR stale) | PASS 3/3/3 | yes |
| SetTable | faust / Python | SQ FAIL (2 High) | FAIL: solution High = platform High #1 | yes |
| gzip preview | elio / Rust | revision: tests band 1 (256 MiB passer) | FAIL: tests High = the passer gap | yes |
| window expiry (HELD OUT) | faust / Python | revision: tests band 1 (3 findings) | FAIL: tests High = platform's T1 (base mode omits app lifecycle tests) | yes (1 of 3 findings) |
| #751 description | Burrow / Go | DQ FAIL | DQ FAIL | yes |
| group-table writes | goka / Go | SQ PASS; AR not run on these files | FAIL: AR S1 High (failed final reconciliation write) | open (no Go toolchain to reproduce; SQ x2 agreed PASS) |

Agreement on the gate: 11 of 11 packages with a known platform answer, across 7 repositories and 4 languages.
Known weaknesses: one SQ run finds only one of SetTable's two Highs (two runs per round help); window's `all([])` and
JSON-null test gaps were not found; elio gzip's code-quality Medium was missed.

Next: hold-out before/after test of the knowledge catalogs (replicas/knowledge/). (window, producer flush, swift, oss-rebuild, elio folder history, orange-orm), then the
hold-out before/after test of the knowledge catalogs (replicas/knowledge/).

## GPT Sol 6.1 medium (all checks; from 2026-11-05 22:00)
| Package | Platform | Sol 6.1 medium | Match |
|---|---|---|---|
| SetTable (catalogs on) | SQ FAIL (2 High) | SQ FAIL in BOTH runs, platform High #1 kept by verify | yes (better than the old models: 1 of 2 runs) |
| topic start (catalogs on) | approved | PASS | yes |
| topic start wip6 (held out, no catalogs) | SQ 2 Medium + 1 unfair test | SQ lookup-deadline fallback = platform P2 (rated High), unfair test missed | partial (1 of 3) |
| dead letter wip46 (held out, no catalogs) | SQ High + AR T5 High + 2 Medium | re-read test flagged = platform T5 test; SQ High missed | partial (1 of 4) |

## Deterministic tests lint (tools/tests_lint.py, no model)
| Package | Platform finding | Lint |
|---|---|---|
| window (held out) | AR T1 High: base mode omits tests/unit/app/test_base.py | FAIL L5 on exactly that file |
| dead letter wip46 (held out) | AR T5 High: re-read test starts a rebalance it never ends | REVIEW L10/L9 on exactly that test |
| SetTable | AR tests band 1: harness replaces send_soon, threaded path never runs | REVIEW L9 (helpers replace send_soon) |
| topic start, standby, swift (approved) | none | clean or one reminder line |

## Knowledge catalogs on vs off (Sol 6.1 medium; b2 = off, s1 = on)
| Package | Platform findings | Off | On |
|---|---|---|---|
| window | 3 tests findings | (old-model f1: 1) | 2 of 3 (base mode, JSON null) |
| dead letter wip46 | SQ High, T5 High, T4 Medium x2 | 1 (T5 re-read test) | 1 (T4 header prefix) + 2 unfair-test Highs the platform never raised |
| topic start wip6 | SQ Medium x2, 1 unfair test | 1 | 1 (same) |
| SetTable | SQ High | - | both SQ runs |
| standby, topic start | approved | - | PASS |
Decision: keep the catalogs (cheap, more platform findings found); watch the fairness "unfair" noise they add. Gate
verdict right on every package; one-off findings still partly missed.

## Coverage grading (2026-11-10)
| Package | Site verifyFairness coverage | Replica (old Step 3) |
|---|---|---|
| vet 1 | 6/6 yes | - |
| vet 2 | 6/6 partial (sampled ecosystems) | - |
| vet 3 final | 3/6 partial (sampled package types, counts without messages, a name promising an unasserted outcome) | 9/9 yes |
Decision: Step 3 drops "breadth is not required" and lists the site's partial causes; tests carry a `qualityCheck`
line. Re-measure on the next task's first fairness round against the site.
