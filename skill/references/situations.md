# Situations: trigger -> action -> why

One action per row. Evidence keys: MAP.md (workflow-build-20261105) sections and the platform data pulled 2026-11-05.
If two rows apply, do both. If none applies, decide by the ten rules in SKILL.md and add a row here afterwards.

## Pick and scope (S0-S1)
| ID | Trigger | Action | Why |
|---|---|---|---|
| P-1 | Seam needs a contract over every lifecycle event ("always consistent after any restart/rebalance/crash") | Pick another seam, or cut to one lifecycle edge with 4-5 boundaries | 30-61 wips each on T5/T7/T11, elio halted |
| P-2 | Feature spans several drivers/stores/table kinds | Choose one; name it in the setup line; refuse the rest at start | SQ FAIL per mode (window x4, T11 confluent x2) |
| P-3 | Any PR/issue in any state implements it, or README says "not supported" | Drop the seam | similarity DERIVATIVE x3, RIE Scope Gate x2 |
| P-4 | The hard point has fewer than 3 stated consequences, or the task has more than 2 hard points | Deepen the same rule (one more stated consequence) or cut the extra hard points | 1-2 hard points on every accepted task; many traps stalled (orange-orm, task 5, #751) |
| P-5 | All boundaries hit the same blind spot | Replace two with boundaries on other subsystem pairs | group-table task 0/23, failed the gate |
| P-6 | A boundary needs injected timing or a hook to observe | Cut it from core | 0/33 and 22/22 blocked on T12 |
| P-7 | Upstream default branch moved since you started | Re-base base/ and repo/ onto the tip before the Dockerfile | Harbor rebuild FAIL x3 on T11 |

## Description (S1, and D-LATE)
| ID | Trigger | Action | Why |
|---|---|---|---|
| D-1 | Over 14 requirement units or DQ replica blocking | Delete whole sentences together with their tests, or fold parts that share ONE outcome into a list in one sentence; turning a sentence into a clause with its own outcome does not lower the count; never add a parenthetical | <= 14 passed 8/8, >= 19 failed 5/5; osr-proxy 14/15/14; elio count failures |
| D-2 | DQ ai_generated on a sentence | Rewrite that sentence as observed behaviour in the user voice; drop mechanism/flag words | #751 and proxy drafts DQ FAIL |
| D-3 | DQ over_specification / inferable | Remove process instructions; split a blurred sentence | producer flush AR description band 2 |
| D-4 | A sentence has two readings | Rewrite to one reading; if locked, test that each reading is applied fully (either-or) | silences 0/10; T11 either-or reached 3/3 |
| D-5 | Scope/exclusion sentence without a measured base behaviour | Run base, assert it in a test, or delete the sentence | verifyFairness lists it as a requirement; T5 SQ 1/3 |
| D-6 | Category check suggests the other category | Switch category to match the text shape | category FAIL x2 |
| D-7 | DQ major: a present-behaviour claim is not literally true at the pin | Narrow or delete the claim (grep base for each "today it does X") | "as it does now", "/export already hides" majors (other machine) |
| D-8 | A stated case every plausible agent would fail (non-obvious unrelated base defect) | Scope it out before the lock, or accept it as THE hard point; never plan to drop its test later | orange-orm order 181: 16/16 agents missed it, hinted or not |
| D-LATE | After lock, before first paste: a sentence proven untestable/unreachable/too wide (S2-S6 evidence) | Cut or narrow it; then re-check the reference and every test leg against the remaining literal text (a cut sentence still binds if other sentences or the repo imply it; an old leg can turn unfair); precheck + DQ replica, new hash; never after the first paste | T12 two late changes; orange-orm SQ High after a cut, turso SQ FAIL, TQ 1/33 after a wording change (other machine) |

## Reference (S2) and SQ
| ID | Trigger | Action | Why |
|---|---|---|---|
| S-1 | SQ replica High on a stated promise, reproduced | Fix in code; sweep the same class on sibling paths in the same batch | T11 SQ 1/3 -> 3/3; class sweeps closed T7/T11 |
| S-2 | SQ High not reproducible | Write the contest note with the code trace; no change | task 7 claims that did not reproduce |
| S-3 | A fix would need behaviour the description leaves open | Do not build it; check the sentence (D-4) | contested items later tested -> TQ unfair (T12) |
| S-4 | Temptation to document a caveat or keep a "residual" | Fix the code or cut the promise (D-LATE) | 57 kept items became platform findings |
| S-5 | Medium quality issue (performance vs repo norm, naming, leftover comment) | Fix in the same batch | cheap Lows kept -> SQ 2/3 (T11, EOS) |
| S-6 | Reference would need a mode you scoped out | Refuse it at start with a clear error | reference code for excluded scope -> AR finding |
| S-7 | Compiled twin of a changed Python method exists | Change both; test the compiled path in Docker | task 7 Cython twin SQ High |
| S-8 | Platform SQ finding is a misread of indirect code | One plain comment at the misread line stating the fact; no new code | orange-orm SQ loop reached 3/3 + 3/3 this way |
| S-9 | SQ finding on a backend the repo ships but the text never names (e.g. no transactions) | Fix it there (all checks before the first write / locking read) or scope the backend out in the description before the lock | orange-orm Cloudflare D1: High in 3 of 5 runs until fixed |

## Tests and harness (S3) and fairness / AR tests
| ID | Trigger | Action | Why |
|---|---|---|---|
| T-1 | A test asserts an unstated rule, wording, private state or harness mechanism | Assert the stated outcome instead | TQ unfair fixed on 6 tasks |
| T-2 | Fairness/AR names a plausible wrong implementation that passes | Add one discriminating assertion (two-sided, non-empty, both effects) | AR T3/T4 band 1 on window, T11, goka, SetTable |
| T-3 | A stated mode runs through a replaced function in the harness | Route it through the real code path | SetTable AR tests band 1 |
| T-4 | A valid design fails a base test | Exact node-id deselect with a comment, or adapt the one obsolete line | T12 15/22 runs lost to one pin |
| T-5 | A wrong variant hangs instead of failing | Add an outer timeout and a fail-safe JUnit case | hangs hide results and kill Verify Tests |
| T-6 | Wall-clock wait decides an ordering | Replace with an event/handshake | goka AR T2/T3, task 8 T2 |
| T-7 | Agents converge on one valid design a test rejects | Loosen that test to the stated outcome | elio PDF private path (3 runs) |
| T-8 | Coverage suggestion "Would need prompt edit" | Ignore it (never test open behaviour) | it names behaviour the text leaves open |
| T-9 | Clean `test.sh new` > 300 s | Shorten waits/sizes; keep the hard timeout < platform kill | Verify Tests killed at 688 s (T11) |
| T-10 | T6: test.sh relies on the image ENV / tools found only on PATH of root | Export the toolchain env inside test.sh | turso T6 Blocker (2176 failures as uid 4242) |
| T-11 | Tests read generated output (dist, bundles) | Rebuild it in test.sh; re-eval agent patches carry no dist | orange-orm sole passer became TEST_BROKEN at re-eval |

## Gates and environment (S4, platform verify checks)
| ID | Trigger | Action | Why |
|---|---|---|---|
| E-1 | precheck FAIL | Fix the named item | each FAIL is a recorded platform fail |
| E-2 | verifyTests on platform fails but local passes | Pull the platform Dockerfile field; re-paste ours | sqlite: the field held the default template |
| E-3 | Fails only as a uid without passwd | Make HOME/cache paths writable in a scratch dir in test.sh | elio Verify Solution FAIL |
| E-4 | "Image failed to rebuild from your committed source" | Find the cause: upstream moved past the base -> re-base onto the tip (do not touch the Dockerfile); the Dockerfile fetches from the network at build (GitHub, nodejs.org), builds native code, or leaves a toolchain unpinned -> fix the Dockerfile (the platform rebuilds as uid 1000 without those hosts) | T11 re-base; turso pinned toolchain, orange-orm removed the native build and fetch (other machine) |
| E-5 | Flaky result between repeats | Find the scheduling dependence; never retry-until-green | verifyFlakiness runs 6+6 |
| E-6 | Downloaded platform files differ from the wip (mixed or stale paste) | Re-paste the differing field; re-check what it staled | a wip75 file next to wip78 files (other machine) |

## Rollout and FP (S8)
| ID | Trigger | Action | Why |
|---|---|---|---|
| R-1 | Failing runs blocked on a base test | T-4, then re-eval (same description: same patches re-run) | T12 |
| R-2 | 0 passes in every family, near-misses on fair boundaries | If the blocking test is of UNSTATED behaviour, it may go at re-eval. If a sentence states it, never remove its test (the closest run becomes a false pass): new runs, or a re-scope with a fresh rollout | orange-orm KA 32/32 (other machine); T12 wip12 passers were FP by definition |
| R-3 | Two families pass | Add one discriminator from a passer's own mechanism on a stated sentence (FP-1 style) | T9, T10 reached the gate this way |
| R-4 | One family > 25% | Same as R-3 for that family | gate text |
| FP-1 | A passer misses a stated sentence (reproduced) | Add one grounded test for it; never weaken the reference | snapshot, sqlite, T10 fixed this way |
| FP-2 | Passer differs only on unstated behaviour | Keep it; at re-eval an unstated late-added corner test may be dropped | task 7 F6 -> genuine pass, accepted |
| FP-3 | Temptation to drop/loosen a stated test to keep a passer | Never | T12 wip12 passers were FP by definition |

## Process
| ID | Trigger | Action | Why |
|---|---|---|---|
| X-1 | A stage overruns its box by 50% | Stop; the scope is too wide; cut a promise (before paste) or narrow | every long task was over-scoped |
| X-2 | Third fix cycle needed on one promise | Cut/narrow the promise | rounds never converge on concurrency features |
| X-3 | Local pass-rate estimate used to predict the platform | Do not; use only "solvable / where are the walls" | local proxies wrong both ways |
| X-4 | Platform result arrives while building | Answer it first (S9 loop) | findings age into more rounds |
| X-5 | Two different reviewers flag the same item | Treat as reproduced; fix | kept double flags returned on the platform |
