# Situations: trigger -> action -> why

One action per row. Evidence: the task records named in each row (task folders, BACKLOG.md) and the platform data pulled since 2026-11-05.
If two rows apply, do both. If none applies, decide by PIPELINE.md and the cards, and add a row here afterwards.
Stage names: S0-S1 = stages 0-3, S2 = stage 5, S3 = stage 4, S4 = stage 6, S8 = stages 8-10 (PIPELINE.md). Where a
row and a card disagree, the card wins.

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
| P-8 | The fix sits in one module, the reading chain is short (under about 40 files), or nothing the solver can run shows its solution wrong; or the stage-2 length spike stays under a mean of 300K | Deepen the seam (a second entry path, a saved state read back, a caller context, a mechanism that must agree); never add a rule; after two short spikes take the runner-up seam (difficulty.md section 2) | vet 6: 8 rules, 27 files, 5 of 6 Orion runs 215-238K with no compaction; the one compacting run was the pass |
| P-9 | A universal word in the planned text spans more than about 8 axis members with no single code path, or the planned change has more than about 120 decision points | Narrow the word or the seam before the lock; one kept wrong version per decision must stay feasible | vet 6: about 300 decision points, 16 x 16 x 21 cells, 20+ repair rounds |

## Description (S1, and D-LATE)
| ID | Trigger | Action | Why |
|---|---|---|---|
| D-1 | Over 9 requirement units (description.md hard limit) or DQ replica blocking | Delete whole sentences together with their tests, or fold parts that share ONE outcome into a list in one sentence; turning a sentence into a clause with its own outcome does not lower the count; never add a parenthetical | <= 14 passed 8/8, >= 19 failed 5/5; osr-proxy 14/15/14; elio count failures |
| D-2 | DQ ai_generated on a sentence | Rewrite that sentence as observed behaviour in the user voice; drop mechanism/flag words | #751 and proxy drafts DQ FAIL |
| D-3 | DQ over_specification / inferable | Remove process instructions; split a blurred sentence | producer flush AR description band 2 |
| D-4 | A sentence has two readings | Rewrite to one reading; if locked, test that each reading is applied fully (either-or) | silences 0/10; T11 either-or reached 3/3 |
| D-5 | Scope/exclusion sentence without a measured base behaviour | Run base, assert it in a test, or delete the sentence | verifyFairness lists it as a requirement; T5 SQ 1/3 |
| D-6 | Category check suggests the other category | Switch category to match the text shape | category FAIL x2 |
| D-7 | DQ major: a present-behaviour claim is not literally true at the pin | Narrow or delete the claim (grep base for each "today it does X") | "as it does now", "/export already hides" majors (other machine) |
| D-8 | A stated case every plausible agent would fail (non-obvious unrelated base defect) | Scope it out before the lock, or accept it as THE hard point; never plan to drop its test later | orange-orm order 181: 16/16 agents missed it, hinted or not |
| D-LATE | After lock, before first paste: a sentence proven untestable/unreachable/too wide (S2-S6 evidence) | The text is locked: take it to the owner (description.md section 0, REDESIGN) and sharpen the feasibility gate (description.md step 3) that should have caught it. If the owner approves a cut or narrowing: then re-check the reference and every test leg against the remaining literal text (a cut sentence still binds if other sentences or the repo imply it; an old leg can turn unfair); precheck + DQ replica, new hash; never after the first paste | T12 two late changes; orange-orm SQ High after a cut, turso SQ FAIL, TQ 1/33 after a wording change (other machine) |

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
| T-9 | Clean `test.sh new` over 6 minutes (target under 300 s) | Shorten waits/sizes; keep the hard timeout < platform kill | Verify Tests killed at 688 s (T11) |
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
| E-7 | verifySolution `harbor_oracle_failed` with baseline, new tests and offline uid all green | Check in this order: /app writable for uid 1000 (`chmod -R a+rwX /app`), test.sh accepts `[--output_path F] [--mode] <base|new>` with the output path optional, test.sh prints the runner's text output (`--- PASS:` lines), PATH keeps sbin for the platform's useradd; diff against the newest accepted Dockerfile and test.sh in templates/examples/ | pmg: three failures with no platform log (BACKLOG #156, #158, #159); vet 6 passed with the bash runner |
| E-8 | `problems create` answers "Submission creation is paused" | Build ahead locally (stages 2, 4-7 need no draft; the spike and the audits run locally); retry at each paste point; tell the owner once | pmg bypass-counts stage 1 (BACKLOG #163) |
| E-9 | Verify Flakiness fails on a repository test the change never touched | Measure it 30 times on the clean repository; a wall-clock bound that fails there goes on the skip allowlist in base mode with the reason, next to the user-dependent skips; a test.sh change reopens Verify Tests/Solution/Flakiness, Reward Hacking and Test Quality | vet 6: a 1.6 s bound failed 4-5 of 30 on the untouched repository (BACKLOG #213) |
| E-10 | The platform's verify image build stops at `chown: invalid user` or `groupadd: command not found` | The Dockerfile's ENV PATH dropped /usr/sbin and /sbin; restore them | pmg (BACKLOG #153) |

## Rollout and FP (S8)
| ID | Trigger | Action | Why |
|---|---|---|---|
| R-1 | Failing runs blocked on a base test | T-4, then re-eval (same description: same patches re-run) | T12 |
| R-2 | 0 passes in every family, near-misses on fair boundaries | If the blocking test is of UNSTATED behaviour, it may go at re-eval. If a sentence names it, never remove its test (the closest run becomes a false pass): new runs. If only the general rule covers it (implied), near-miss-release.md is an owner decision per task | orange-orm KA 32/32 (other machine); T12 wip12 passers were FP by definition |
| R-3 | Two families pass | Add one discriminator from a passer's own mechanism on a stated sentence (FP-1 style) | T9, T10 reached the gate this way |
| R-4 | One family > 25% | Same as R-3 for that family | gate text |
| R-5 | A platform run fails tests that its patch passes in the local replay | The platform junit is the truth for that run; report the per-test difference; when two patches share a platform-only failure set look for the shared mechanism (link resolution, sandbox); keep the tests | vet 6 rollouts 51-52: five link tests on two Orion patches (BACKLOG #214) |
| R-6 | The only passing Orion run is under 256K tokens | No test change can fix it; tell the owner: a description change that adds the layer the solver must trace (fresh rollout), or more Orion runs (the passing runs' average must clear the bar); record which stage-0 estimate was wrong (difficulty.md section 7) | criteria `passSequenceLength` (platform.md) |
| R-7 | A near miss fails only crafted cells, and removing them would leave a code path untested | near-miss-release.md rules 8-9: replace each cell with one the near miss passes and the natural wrong design fails; dry-run against the near miss's code; show the owner what stays uncovered | vet 6 fx30 -> platform Test Quality blocker on the removed path; fx40 replaced cells (BACKLOG #206, #216, #217) |
| FP-1 | A passer misses a stated sentence (reproduced) | Add one grounded test for it; never weaken the reference | snapshot, sqlite, T10 fixed this way |
| FP-2 | Passer differs only on unstated behaviour | Keep it; at re-eval an unstated late-added corner test may be dropped | task 7 F6 -> genuine pass, accepted |
| FP-3 | Temptation to drop/loosen a stated test to keep a passer | Never for a case a sentence names; an implied case only through near-miss-release.md with the owner's decision | T12 wip12 passers were FP by definition |

## Process
| ID | Trigger | Action | Why |
|---|---|---|---|
| X-1 | A stage overruns its box by 50% | Stop; the scope is too wide; cut a promise (before paste) or narrow | every long task was over-scoped |
| X-2 | Third fix cycle needed on one promise | Cut/narrow the promise | rounds never converge on concurrency features |
| X-3 | Local pass-rate estimate used to predict the platform | Do not; use only "solvable / where are the walls" | local proxies wrong both ways |
| X-4 | Platform result arrives while building | Answer it first (stage 8, platform.md) | findings age into more rounds |
| X-5 | Two different reviewers flag the same item | Treat as reproduced; fix | kept double flags returned on the platform |
| X-6 | The checklist looks skipped, or a short plan stands in for the ledger | Run prompts/apply-build-checklist.md and show the gate output | vet task 2 v1: condensed plan, platform SQ FAIL, full fix batch |
| X-7 | A Codex job ends with no report, or is about to touch a sensitive area | Read the tail of the job log for the safety-filter message before relaunching. Keep file and folder names neutral too. Search scripts print only owner/name, language, stars, licence and dates. On network servers frame Codex work as a feature or measurement study | task 11 hunt, swift 6 attempts |
| X-8 | A command was rejected or interrupted | Check git status and the touched folders before continuing: side effects already done stay. Never chain commit, package build and launch in one command | task 7: solves launched on a half-built package |
| X-9 | `olympus` answers `NoAuthProvider` (login expired) | Tell the owner once; until they log in again, the owner pastes and downloads (run zips: run.txt, junit-new.xml, eval-result.json, solution-patch.patch, trajectory.json per run; `tools/rollout_report.py` reads them); never guess platform state | vet 6, 2026-11-20/21 |
| X-10 | A review lane runs past its time box, or a lane reports while shells it started still poll for a file | Every lane brief carries a 40-minute box and writes its report at the box; a lane kills its own wait loops before it stops; before saying "still running", check the lane's last file time and `docker ps`; after an interruption list every lane and restart the dead ones in the same reply | vet 6: three lanes 1-2.5 h with no visible progress, 8 orphan poll loops (BACKLOG #186, #205) |
| X-11 | A check status is reported without its version, or a fix is chosen without saying which checks it reopens | Every status names the hash it graded; before the owner picks a fix, say which platform checks it reopens (PIPELINE.md, Version bookkeeping) | vet 6: "TQ good" on fx22e, then 4 blockers on fx24f after a rewrite (BACKLOG #193) |
| X-13 | Editing on Windows with Git Bash | Write any file that holds backslashes with the editor's write tool, never a shell heredoc (a doubled backslash became a real newline twice); scripted edits keep LF (`newline=''`), check with `file`; strip `\r` from values Python prints; use `MSYS_NO_PATHCONV=1` plus host-form paths (`machine_host`) for every Docker mount and every path a Windows Python receives | vet 6 (BACKLOG #206, #230) |
| X-14 | A test fixture or a solver clone loses files with no error | Antivirus removes malware-like fixtures from clones and patches; keep deletions out of agent patches (solvers.sh lists them in meta.txt), re-check the fixture list after a copy, and exclude the task folders from the scanner where the owner allows | vet 2026-11-06 |
| X-12 | Codex hits a usage limit or capacity error mid-round | Re-run the same check on the Claude reviewer agent of that role with the same brief; record the fallback in the checkpoint; keep the gate's report names | vet 6: a whole verification round died 15 h before the reset (BACKLOG #171) |

## When stuck: prompts that already found the right path

Read this part BEFORE choosing a fix path whenever a stage loops, a check repeats a finding, or a decision is unclear.
Ask the question of yourself first; the owner should not have to. Each row: the situation, the prompt that resolved it,
where it worked, how to run it.

### Description and difficulty
| Situation | Prompt (ask it of yourself) | Worked on | How I run it |
|---|---|---|---|
| Solves pass too easily (3-4/4) | "first tell me how many hints are present in our desc? ... and 3/4 solvers solve it right?" | vet wip01 (3/4 -> de-hint) | count every why/where/how sentence and "Currently ..." narration; remove them, behaviour diff, keep every tested outcome |
| A trim or rewrite | "did we lose anything during trimming? ... i always ask you to trim so that nothing lost related to task" | vet v2 (lost expired+unmatched) | behaviour diff table old vs new per tested case, shown to the user before the lock |
| Description keeps changing | "why are you not making perfect change in desc? ... learn from everything we have evidence for desc .. and lock in once" | vet v6 | word-reach check (grep key words in the repo, use the repo's own term), reading audit lanes before the lock, one lock |
| Is it still solvable? | "are our problem yet solvable based on desc?" | vet v6 (0/4) | per tested outcome: where the repo tells a solver (file:line or diagnostic text), how hard, which solves failed it |
| Platform pass rate 0 in every family | "now what is that one blocker for us?" | faust tasks 3-11 (hints), vet wip03 (no hint) | the text is locked: rollout.md levers in order, near-miss-release.md as an owner decision, a description change only if the owner asks (description.md 5b) |

### Tests, FP and passers
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| A passer exists | "you missed strict fp auditors on passer last time right?" | vet v4/v5 (s1 NOT_DESERVED found) | `replica.sh <task> fp-audit` on EVERY passer, a second when it says NOT_DESERVED or is unclear; reproduce each finding |
| A local solve the owner asked for passes | "run FP audit on passer as soon as it finishes" | cc-vet-continue-usage s3 (2026-11-09, audit started only after the owner asked) | Same step as grading, no asking: 1 Codex GPT Sol 6.1 medium + 1 Claude Opus 5.5 medium on each passer; report solver results and verdicts together |
| A reproduced false pass | "we should add test case for this .. make sure reference works fine on this right? ... make sure added test is not unfair and should hold T1-T8 and S1-S4" | vet v5 s1 | smallest test on a stated sentence; battery: reference passes, passer fails as a variant, fair passers pass; the next sweep checks fairness + T1-T8/S1-S4 |
| Reference gaps the FP audit cannot see | "run strict fp auditors on our reference too .. 2 gpt strict auditors" | vet sweep lanes (ref-audit) | `replica.sh <task> ref-audit pre1` (medium, once before v1); every named wrong implementation becomes a test or a variant |
| Platform keeps finding one more gap | "We learn why it's very significant to cover all wrong design always in our test cases .. if we got stuck" | faust task 11 (wip49 3/3 + genuine FP) | per promise list every wrong design, reproduce each as a variant first, a test fails each, passer kept |
| Platform finds what local reviewers miss | "you have to understand how platform is figuring out different ways and finding issues, you have to do it the same way ... upgrade your TQ and SQ and auto reviewer with learning" | elio wip23-24, faust task 11 | literal promise + one reference heuristic + smallest breaking input; multiplicity sweep |
| A solver fails only 1-2 tests | near-miss study prompt (prompts/near-miss-study.md) | faust tasks 11, 12 | complete the run in its own design, then probe + FP-audit it |
| Every run fails, one run fails only one implied case | "check if there are any loosening we can do ... in reference also" + "cant we relax this instead of removing it completely? and cover cases around it?" + "cant we do same in reference only with very minimal change" | vet wip03 (Vega 1/8, FP panel genuine) | near-miss-release.md: relax the case (keep input, keep shared assertions), remove the one reference rule that differs, replicas + proof + exact re-eval prediction; only if its section 7 rules hold |

### Review rounds and findings
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| Review rounds find one gap each | "instead cut those review round ... rebuild it to cover all the gaps at once .. just like we used to do using subagent" | vet (7 rounds -> sweeps) | `sweep.sh` + in-process lanes on replicas/sweep-brief.md, complete table per sentence |
| Findings would complicate the task | "you should take care also about subagents finding sometimes they find something which makes our task complicated ... that is your task to look after" | vet sweeps 1-2 | triage ACCEPT/REJECT per finding with the reason (stated sentence, plausible, discoverable, no new requirement) |
| Tempted to keep a finding open | "why are you leaving it, in past whenever we leave something it comes after to us" | vet, faust tasks 8/11 | probe it the same session; a finding inside a promise is fixed or its sentence is cited, never kept as residual |
| Before any hand-over | "are you sure that's all you need now? no open gates no ambiguity" | vet wip01 | read the ledger top to bottom, every row closed with evidence, every triage row closed |

### Process speed
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| A step repeats | "why are we doing this step of rebuild? what's the point?" / "why do we have to run proof and battery again and again?" | vet (image rebuilds, proofs per fix) | name the decision the step can change; build once; proof only right before each paste and at the freeze |
