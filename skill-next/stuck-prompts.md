# When stuck: prompts that already found the right path

Each row: the situation, the prompt that resolved it (the user's words, verbatim where kept), where it worked, and how I
run it. Read this table BEFORE choosing a fix path whenever a stage loops, a check repeats a finding, or a decision is
unclear. Ask the question of yourself first; the user should not have to.

## Description and difficulty
| Situation | Prompt (ask it of yourself) | Worked on | How I run it |
|---|---|---|---|
| Solves pass too easily (3-4/4) | "first tell me how many hints are present in our desc? ... and 3/4 solvers solve it right?" | vet wip01 (3/4 -> de-hint) | count every why/where/how sentence and "Currently ..." narration; remove them, behaviour diff, keep every tested outcome |
| A trim or rewrite | "did we lose anything during trimming? ... i always ask you to trim so that nothing lost related to task" | vet v2 (lost expired+unmatched) | behaviour diff table old vs new per tested case, shown to the user before the lock |
| Need difficulty | (superseded) "add something in desc that can be little tricky and can have 2 different results based on how agents read" | vet v5 -> backfired: reference broken, 3 sweeps, re-lock | difficulty from code paths of stated outcomes (other entry point, saved format, second code path, ordering), never from a two-reading word; description.md sections 1-3 |
| Description keeps changing | "why are you not making perfect change in desc? ... learn from everything we have evidence for desc .. and lock in once" | vet v6 | word-reach check (grep key words in the repo, use the repo's own term), reading audit lanes before the lock, one lock |
| Is it still solvable? | "are our problem yet solvable based on desc?" | vet v6 (0/4) | per tested outcome: where the repo tells a solver (file:line or diagnostic text), how hard, which solves failed it |
| Platform pass rate 0/10 | P3 + P3a + P3b (verbatim below) | faust tasks 3-11 | read every trajectory and patch, rank closest agents, inline observable hint (<= +60 words) or remove a test AND its promise |

## Tests, FP and passers
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| A passer exists | "you missed strict fp auditors on passer last time right?" | vet v4/v5 (s1 NOT_DESERVED found) | `replica.sh <task> fp-audit` x2 GPT Sol 6.1 HIGH on EVERY passer; reproduce each finding |
| A reproduced false pass | "we should add test case for this .. make sure reference works fine on this right? ... make sure added test is not unfair and should hold T1-T8 and S1-S4" | vet v5 s1 | smallest test on a stated sentence; battery: reference passes, passer fails as a variant, fair passers pass; the next sweep checks fairness + T1-T8/S1-S4 |
| Reference gaps the FP audit cannot see | "run strict fp auditors on our reference too .. 2 gpt strict auditors" | vet sweep lanes (ref-audit) | `replica.sh <task> ref-audit` x2 HIGH; every named wrong implementation becomes a test or a variant |
| Platform keeps finding one more gap | "We learn why it's very significant to cover all wrong design always in our test cases .. if we got stuck" | faust task 11 (wip49 3/3 + genuine FP) | per promise list every wrong design, reproduce each as a variant first, a test fails each, passer kept (memory cover-every-wrong-design) |
| Platform finds what local reviewers miss | "you have to understand how platform is figuring out different ways and finding issues, you have to do it the same way ... upgrade your TQ and SQ and auto reviewer with learning" | elio wip23-24, faust task 11 | literal promise + one reference heuristic + smallest breaking input; multiplicity sweep (memory reviewer-multiplicity-sweep, olympus-platform-finds-design-decisions) |
| A solver fails only 1-2 tests | near-miss study prompt (olympus-challenge-creation/references/near-miss-study-prompt.md) | faust tasks 11, 12 | complete the run in its own design, then probe + FP-audit it |

## Review rounds and findings
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| Review rounds find one gap each | "instead cut those review round ... rebuild it to cover all the gaps at once .. just like we used to do using subagent" | vet (7 rounds -> sweeps) | `sweep.sh` + in-process lanes on replicas/sweep-brief.md, complete table per sentence |
| Findings would complicate the task | "you should take care also about subagents finding sometimes they find something which makes our task complicated ... that is your task to look after" | vet sweeps 1-2 | triage ACCEPT/REJECT per finding with the reason (stated sentence, plausible, discoverable, no new requirement) |
| Tempted to keep a finding open | "why are you leaving it, in past whenever we leave something it comes after to us" | vet, faust tasks 8/11 | probe it the same session; a finding inside a promise is fixed or its sentence is cited, never kept as residual |
| Before any hand-over | "are you sure that's all you need now? no open gates no ambiguity" | vet wip01 | read flow-status top to bottom, every row DONE with evidence, every triage row closed |

## Solvers and process speed
| Situation | Prompt | Worked on | How I run it |
|---|---|---|---|
| A solver result looks too good | "are you giving opus any context? or is the solver somehow cheating?" | vet v5 | solve_watch.py CLEAN/SUSPICIOUS; only CLEAN solves count |
| A step repeats | "why are we doing this step of rebuild? what's the point?" / "why do we have to run proof and battery again and again?" | vet (image rebuilds, proofs per fix) | name the decision the step can change; build once, battery only between S4 and S7, full proof at S7 |
| Solves slow the flow | "how long are we going to run solver isnt this is making our progress slow again?" | vet (4 batches) | no local solves (2026-11-07): the platform 2-2-2 rollout is the solver data; keep closing gaps while it runs |

## Verbatim: P3, P3a, P3b (platform pass rate 0/10; faust tasks)
Full text and the run procedure: olympus-challenge-creation/references/prompts.md sections P3, P3a, P3b and "How P3 +
P3a + P3b run together". Target today: exactly one family in (0, 25%]. The 60-word hint allowance applies only to the
one allowed description change (rollout.md lever 6).
