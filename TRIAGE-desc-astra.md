# Triage: GPT-6 Astra's description suggestions (eval/desc-recipe-astra.md) -> description rulebook

Decided by the architect, 2026-11-07. Source of each suggestion: desc-recipe-astra.md sections 2-6 (L = "what it
lacks", W = "what it gets wrong", R = "redundant", recipe and checklist items). Applied to skill-next/description.md
(and the live references/description-playbook.md, kept identical).

## Owner rules that no suggestion changes
- Requirement count: hard limit 9 units, target 5-8. Length: about 250 site words as guidance, not a limit.
- Order: I scan the draft -> the owner humanizes it -> I re-check -> we lock together.
- After the lock the text is fixed; the owner's single exception is one last change when the task is too easy.
- No local solves: the platform 2-2-2 rollout is the solver data. The rulebook is the only source of truth.

## Decisions
| # | Suggestion | Decision | Reason | Where in the rulebook |
|---|---|---|---|---|
| 1 | L1: obligations are required-explicit, required-implied or unspecified; "unnamed" is not "unrequired"; dropping a test needs proof the case is unspecified and the list of wrong designs the drop would release | ACCEPT | topic-start's drop list nearly released false passes; one false pass fails the task | R8; section 6 |
| 2 | L2: adjudicate every second reading (separating input, strongest repo disproof, disposition); a one-word fix is not always enough | ACCEPT | vet "turned off" still had an option-level reading after the one-word fix (both reading audits) | section 3 step 7 |
| 3 | L3: feasibility gate before the lock (prove the hard path with a disposable reference spike, sketch one valid alternative, run the base suite against the spike) | ACCEPT | vet's reference was redesigned after the lock; topic-start's base pin blocked 15/22 runs; ~20-30 min before the lock saves hours after | section 3 step 3 |
| 4 | L4: record the evidence type of every check (text-only / static / executed / platform); the DQ replica counts only with the real test.patch | ACCEPT | vet DQ s1 passed on empty patches at 12 units | section 3 step 8, lock record |
| 5 | L5: a failure exit when no allowed lever reaches the band | ACCEPT, MODIFIED | owner policy: the single text change is for too easy only; too hard after the test-side levers and more runs -> the owner decides a redesign (new version, fresh rollout) or retirement; never release a known false pass | section 0, section 6 |
| 6 | L6: classify rollout evidence first (eligible runs, per-family denominators, a re-evaluation adds no run) | ACCEPT | elio interrupted runs and re-evaluations distorted rates | section 6 (detail in rollout.md) |
| 7 | L7: the post-humanize diff covers every obligation and every known separator, not only tested cases | ACCEPT | vet "has not expired" trim; dead-letter "so" (GPT 0/8) | section 3 step 9 |
| 8 | W1: label the post-lock change as the owner's exception, not a lever | ACCEPT | already the owner's rule; wording made explicit | section 0 |
| 9 | W2: removing direction words is not the first too-easy lever | ACCEPT | false-pass audit and test discriminators come first (rollout.md) | section 6 |
| 10 | W3: "de-hinting took vet 3/4 -> ~1/4" is confounded (tests changed too) | ACCEPT | honest evidence | R2 evidence |
| 11 | W4: trap probabilities, "two stacked traps = 0%", "keep one implied trap for the band" are unvalidated numbers | ACCEPT | old 17-run profile, not a calibrated model; the inventory stays, qualitative | section 2 |
| 12 | W5: "local 1/4 -> Orion ~3/4" conversion | ACCEPT | not a stable conversion; no local solves now | section 2 (removed) |
| 13 | W6: "one sentence = one outcome" too strict | ACCEPT | task 12 carries earliest/latest/datetime in one sentence; the gate is the honest count (max 9) | R5 |
| 14 | W7: "no corner lists" / "only the exact word" too strong | ACCEPT | docker AR called its boundary examples necessary; an example is allowed when it disambiguates; never a list of hidden traps | R4, R16 |
| 15 | W8: "every sentence tested" -> every normative promise tested; context carries no promise | ACCEPT | context sentences are not requirements in the reading audits or DQ | R1, R7 |
| 16 | W9: do not name every unreachable variant; name the meaningful boundaries of reachable supported variants | ACCEPT | turso's catalogue of unsupported forms cost TPQ count | R11 |
| 17 | W10: category by the semantic change; the precheck shape check is a warning | ACCEPT | standby and turso are feature requests with bug-story openings | R15 |
| 18 | W11: narrowing after the sample also changes the contract; narrow before the lock | ACCEPT | topic-start's narrowing invalidated earlier runs | R14 |
| 19 | W12: separate accepted / finalizing / local-only rows; vet is local-only | ACCEPT | honest evidence | section 7 |
| 20 | W13: replaying old patches cannot measure a new wording | ACCEPT | a wording effect needs a fresh rollout; replay is for compatibility | section 6 |
| 21 | W14: pre-16-Oct tasks are historical mechanisms, not current rules | ACCEPT | evidence rule | R3, section 6 |
| 22 | W15: "DQ replica lands on the facts count +-1" is not a verified rule | ACCEPT, MODIFIED | the owner's hard limit 9 stays; the ledger count is conservative; the DQ result is recorded as is | section 3 step 8 |
| 23 | R1-R3: one rule table with IDs, one state table, difficulty stated once | ACCEPT | the same rules appeared four times and drifted | sections 0-2 |
| 24 | R4: label example counts once | ACCEPT | task 12: 113 words, 8 by platform extraction, 7 by our count | section 7 |
| 25 | Keep pre- and post-humanize checks separate; keep two reading lanes | ACCEPT | they inspect different texts and found different things | section 3 |
| 26 | Recipe 1: three-way boundary per case (outside the feature / preserve current behaviour / must reject) | ACCEPT | task 5's exclusion was read in reverse | R11, section 3 step 1 |
| 27 | Recipe 5: never fabricate anecdotes, typos or errors to look human | ACCEPT | authorship comes from the owner's own words | R13 |
| 28 | Recipe 8: word count with margin below 400 | REJECT | owner rule: about 250 is guidance, 9 requirements is the hard limit, platform cap 1000 | - |
| 29 | Recipe 8: every claim about current behaviour, API names and paths is source-checked | ACCEPT | docker "/export already hides these writes" was false -> major | R10 |
| 30 | Checklist: preservation sentences are tested, or removed together with their assertions | ACCEPT | docker deleted a sentence and "problem and tests aligned" failed | section 4 |
| 31 | Recipe 10: lock record (hash, pin, category, reviewed test/reference snapshot, count method, open external checks) | ACCEPT | evidence identity | section 3 step 11 |
| 32 | Section 5: sentence roles with real good and bad examples | ACCEPT | role rules instead of blanket bans | section 1b |
| 33 | A DQ pass is not proof of one reading | ACCEPT | vet's clean replicas coexisted with real separators | section 3 step 7 |
| 34 | F5 on vet: "turned off" still separates plugin-off from option-off | TASK NOTE, no rule change | rejected in vet triage with a reason (option = data source; plugin and checks stay on); recorded as a vet hand-over risk | vet hand-over |
