# Kit cold read (2026-11-13)

Reader: a new agent with no context, reading only `skill/` (SKILL.md, PIPELINE.md, every card linked for stages 0-10,
prompts/, replicas/*.md) and `agents/`. Playbooks were not opened: no skill card sends the reader there (only the
agent files do). The tools/ scripts were not read, so anything the cards leave to a script counts as undefined here.

Line numbers are file line numbers. Problems are ranked by how likely each one is to make an agent waste time or loop.
Tags: LOOP, CONTRA (contradiction), UNDEF (undefined), MISSING (missing step).

---

## 1. LOOP + CONTRA: Repair re-closes G1-G4 after every fix, and nothing says how that fits the stage-7 schedule
- gates.md:89 "## Repair - mandatory after every fix"
- gates.md:102-106 "**Recheck FP risk now:** ... execute reference + valid alternatives + known wrong variants + all stored clean solver patches against the repaired package."
- gates.md:107 "Audit every new/changed passer once"
- gates.md:117-118 "Close affected G1 -> G2 -> G3 -> G4 on exact repaired bytes. Required independent samples have different IDs even on identical inputs; do not reuse one as another."
- PIPELINE.md:40-45 sets a fixed order: "sweep 1 ... -> one fix batch -> replica batch ... -> one fix batch -> verification batch (3 replicas) ... There is no sweep 3."
- PIPELINE.md:55-56 "After the final checkpoint, any fix needs Repair and affected semantic reclosure on the new snapshot. Do not restart all checkpoints by default"
- tests.md:60-62 and solution.md:30 "Run gates.md Repair even for a small final solution edit."

What an agent does: after each fix batch in stage 7 it runs Repair. Step 6 says "required independent samples", so it
launches new G1-G4 confirmations, which are model reviews. Those reviews find more items, which means another fix, then
Repair, then reclosure again. PIPELINE's "one fix batch per step" and gates.md's "after every fix" never say which one
wins, or that the stage-7 batches already count as the G1-G4 samples. Also, "affected" is decided by the agent.
Rounds: there is no limit. Stage 7 already has 3 fix batches, and each one can spawn a G1-G4 reclosure. With
"Low notes too" (item 7) this runs until reviewers stop finding anything, which in practice is 5 or more rounds.
The fix: one sentence saying the stage-7 batches are the G1-G4 samples, and that Repair after a stage-7 fix means a
deterministic replay only.

## 2. LOOP + CONTRA: the agent definitions carry standing "before every paste" triggers that the pipeline never schedules
- agents/olympus-auto-reviewer.md:3 "... Use before every paste."
- agents/olympus-sq-judge.md:3 "... Run before every solution.patch paste."
- agents/olympus-tq-judge.md:3 "... Run before every test.patch paste."
- agents/olympus-fp-auditor.md:3 "... Use before every FP check and after every rollout."
- agents/olympus-auto-reviewer.md:319 and olympus-sq-judge.md:212 "Before EVERY paste the brief says \"full\": review the WHOLE patch."
- Against: PIPELINE.md:14 (sample) "Minutes, not a build: no proof, no gates, no check that the tests pass or fail."
- No skill card names these four agents (grep of skill/ for `olympus-auto-reviewer|sq-judge|tq-judge|fp-auditor`: 0 hits).

What an agent does: the harness lists these as subagent types, and their descriptions read as instructions. So the agent
runs four Opus reviewers with Docker before the Dockerfile, sample, locked-text, v1 and every v2 paste, which is up to
5+ pastes times 4 agents. Each one has a 20-30 min box or more (auto-reviewer.md:322-324, fp-auditor.md:76-84).
Their output must then be triaged and fixed (item 1). The pipeline itself uses Codex replicas (PIPELINE.md:69), so this is
a second, unscheduled review layer.

## 3. UNDEF + MISSING: "replica batch", "verification batch", "replica round" and "sweep lanes" are never defined, and there is no step after a failed final gate
- PIPELINE.md:40-44 "replica batch (3 independent replicas in parallel on the same frozen files; Codex GPT Sol 6.1 medium; 25 min time box each) ... verification batch (3 replicas). If the verification batch reproduces a new class of finding: sweep 2 (once) -> fix -> one more verification batch as the gate."
- PIPELINE.md:40 "sweep 1 (all lanes, one round)". Which lanes? situations.md:123 "`sweep.sh` + in-process lanes on replicas/sweep-brief.md"; the agents say "Role in the sweep" (e.g. auto-reviewer.md:28). No card connects the two.
- replicas/ holds sq, ar, dq, fairness, verify, ref-audit, fp-audit, and CALIBRATION.md:37 "round.sh = fairness + sq x2 + dq -> ar -> verify". Is "a replica" one of these, or one full round.sh? Is the "verification batch" verify.md (the "finding verification" replica), or three more rounds?
- platform.md:34 "after one replica round"; rollout.md:68 "4b. one replica round on the changed files"

What an agent does: it guesses the composition. It might run 3 full round.sh runs (6 model calls each) or 3 times one
check. "New class of finding" has no definition, so any new finding triggers sweep 2. If the final verification batch
(the gate) fails, nothing says what comes next: a third batch, sweep 3 (forbidden), or an owner decision. The agent either
loops on verification batches or stalls.

## 4. LOOP: checklist edits during a task invalidate the sheet, and the fresh-reviewer step has no limit
- PIPELINE.md:46-48 "Every reproduced finding gets a cause. ... Checklist: sharpen the row that should have caught it (the example and why it slipped), or add a row when no rule covers it."
- prompts/apply-build-checklist.md:37 "A later checklist change makes the gate ask for a new sheet. Running `sheet` again keeps rows whose rule did not change."
- prompts/apply-build-checklist.md:29-31 "After each of steps 6 and 8, give a fresh reviewer ... Reopen every row it rejects, after checking its reason yourself."
- PIPELINE.md:104 "that stage's card is fixed before the next task" (this one is after the task, but item 4 above sits inside the stage-7 schedule)

What an agent does: a stage-7 finding leads it to sharpen a checklist row. The gate then asks for a new sheet, the changed
rows are re-walked, `check --through 7/8` runs again, and step 9 calls for another fresh reviewer, whose rejections reopen
rows. This can repeat once per reproduced finding, which on a stage-7 run is 5-15 times. There is no "one reviewer pass
per step" cap, and nothing says to defer checklist edits until hand-over.

## 5. MISSING + LOOP: the stage-3 runs arrive while stages 4-7 run, and nothing says what to do when they land late
- PIPELINE.md:16 "Stages 4-5 go on locally meanwhile; their stop signal and keeper are read as soon as they end."
- PIPELINE.md:17 "Shaped on the stage-3 runs (difficulty.md section 4): the keeper and the reference pass; every gap of the other runs, V-OBVIOUS and the variants gets a fair test."
- difficulty.md:82-84 "so the tests are shaped once, before the only full paste ... The builder keeps building locally while they run; nothing is pasted until they end."
- difficulty.md:88-90 stop signal "stop before v1"

What an agent does: it finishes stages 4, 5, 6, 6a and 7 (sweeps, replicas, verification) before the four runs finish.
Then the runs add keeper-shaped tests. That is a test change, so by gates.md Repair:111-118 it re-closes everything.
Does stage 7 run again (sweep 1 + 2 batches, about 75 min)? Nothing says. If the stop signal fires, all of stages 4-7
are wasted. A rule is missing: either do not start stage 6/7 until the runs have been read, or make the post-run test
additions go through one replica round only.

## 6. CONTRA + LOOP: how many platform runs and versions, and when it stops
- rollout.md:3-4 "so the rollout is 4-4-4 with no repeat. Any later version is a re-eval of these stored runs, not new runs."
- rollout.md:49 "5. Too hard with valid near misses: more runs on unchanged files before any change."
- rollout.md:9 "Once a family has one genuine pass at 4+ runs, tell the owner before topping it up"
- situations.md:74 (R-2) "If a sentence names it, never remove its test ...: new runs."
- description.md:196-197 (5b) "lock for good, a fresh rollout"
- PIPELINE.md:24 lists only "8b. v2 paste (calibration, only when needed)". It has no v3 and no stop rule, while SKILL.md:10 says "A task is never retired".
- PIPELINE.md:26 stage 10 "final checks, rollout to 4+ per family", while platform.md:41 says "v1 is the complete package: the owner runs the full checks once, not per paste".

What an agent does: if v2's re-eval is still outside the band, the cards offer v3, v4 and so on (each with "one replica
round"), or more runs, or REDESIGN, with no count and no order between them. Stage 10 then reads as a second full check
and rollout after stage 9, repeating 7b.

## 7. CONTRA: the closing bar (3/3/3, Lows, and "every High") against ">= 2" and "unreproduced changes nothing"
- gates.md:42 "Local target is clean description/tests/solution bands (3/3/3), with every concrete in-scope defect closed."
- platform.md:59 "act on findings that reproduce and on every High."
- platform.md:64-65 "An approval \"with reservations\" still goes to a human reviewer, so clear Low notes on the tests and reference too."
- Against: replicas/CALIBRATION.md:51-52 "gate = bands >= 2 everywhere (the site approved orange-orm with tests band 2)"; replicas/ar.md:8 "approved when every field is 3 or 2 with no High"; PIPELINE.md:49 "Unreproduced findings change nothing."; situations.md:36 (S-2) "SQ High not reproducible | Write the contest note ...; no change".

What an agent does: it chases every Medium and Low, and unreproduced Highs, to reach 3/3/3. Every fix runs Repair (item 1).
This is the fuel for the item-1 loop.

## 8. CONTRA + LOOP: when the sample is pasted and what it contains
- PIPELINE.md:14 (1b, before stage 2) "Builder's own draft description + a basic test.patch (one plain test per sentence ...) + a small solution sketch"; hunt.md:6 "Every pick then goes to stage 1 (Dockerfile) and stage 1b (sample and Scope Gate) before any real build."
- problem-design.md:102-105 "paste a sample (locked description + the real test.patch + a stub solution.patch ...) right after the S1 lock ... S2 starts only after it passes."
- platform.md:46-48 says the AI precheck fails a stub test patch, but problem-design.md:102 asks for "a stub solution.patch".
- description.md:45 (R14) "The sample's promises are the final contract; narrow or widen only before the lock" and description.md:172 "the sample's promises equal the locked promises (R14)".

What an agent does: it pastes the sample at 1b from a draft written before the stage-2 work (obligation ledger, variant
table, spike, reading audits). Any promise that stage 2 changes breaks R14, so it re-pastes the sample and asks for the
Scope Gate again. That happens once per stage-2 change, and once more for each widen (difficulty.md:62). Following
problem-design.md instead moves the sample to after the lock and blocks stage 4/5 on the Scope Gate.

## 9. CONTRA: FP probe repeats and Docker use
- PIPELINE.md:51-52 "Each probe runs once unless a result looks flaky (vet task 2: audits repeating probes 3x held the Docker queue for about 50 min)."
- agents/olympus-fp-auditor.md:48 "deterministic (repeat it 3+ times; also check ... by repeating the hidden tests 6-10 times, including with --cpus=1)"; :54 "Always re-run each passer's hidden suite with -count>1 and -race first"; :78 "repeat the hidden suite 3 times (not 6-10) and a discriminating probe 3 times"; :69-71 platform FP fail -> "seeded differential probe over 1,000+ seeds".
- prompts/near-miss-study.md:193 "Repeat the test 3 times on the run and 3 times on the reference."
- PIPELINE.md:51 "Each audit replays its probe on the reference too", but replicas/common.md:25 says "Do not run Docker, network calls or long builds." and replicas/fp-audit.md has no replay step. near-miss-release.md:136 also admits "Local auditors do not replay their probe on the reference".

What an agent does: either it holds the Docker slot for about 50 min per audit, or it cannot meet the "replay on
reference" rule with the replica, so it adds a second audit.

## 10. CONTRA: how many sweeps and reference audits
- PIPELINE.md:45 "There is no sweep 3."
- build-checklist.md:329-330 "The sweep count is decided from that data with the user, not from a fixed threshold (R8)."
- All four agents :17-18 "a later round finding one more gap is a failure of this round" (this invites another round to prove it).
- PIPELINE.md:20 "one strict audit of the reference | `tools/replica.sh <task> ref-audit pre1`" against situations.md:114 "`replica.sh <task> ref-audit` x2 HIGH". SKILL.md:41 puts replica checks at "medium".

## 11. CONTRA: who may propose a description change, and when cuts are allowed
- SKILL.md:31-32 "The only exit is a change the owner asks for (description.md section 5b); the builder never proposes one."
- description.md:19 REDESIGN: "the builder names the one blocker and proposes the smallest new version that clears it (new lock, fresh rollout)". gates.md:119-120 and rollout.md:77-80 also have the builder propose a redesign.
- agents/olympus-auto-reviewer.md:147-148, fp-auditor.md:65-66 "\"Desc change needed: YES\" with the exact sentence that would have to change"; auto-reviewer.md:157-158 "the description scope is the lever, not more tests".
- situations.md:84 (X-1) "Stop; the scope is too wide; cut a promise (before paste) or narrow"; :85 (X-2) "Cut/narrow the promise". Against PIPELINE.md:88-89 "never an omitted gate or a post-lock scope cut".
- situations.md:30 D-LATE "After lock, before first paste". The locked text is pasted right at the lock (PIPELINE.md:16), and the sample was pasted before it (1b). So this window is empty, or "first paste" is undefined.

## 12. CONTRA: how a test added after the lock must be grounded
- description.md:181-183 "Every test added after the lock quotes the sentence that literally covers its path; check this before each paste. A test with no such sentence is dropped."
- Against: description.md:37 (R7) "every test traces to a sentence or to a repo line cited at the assertion ... An implied case is traced to the repo"; difficulty.md:92-93 the keeper-shaped tests (added after the lock, at stage 4) use "a stated sentence or a repo line at the assertion"; build-checklist.md:240-243 implied case = "the repo file:line that decides it".
- prompts/near-miss-study.md:232 "NOT STATED: only implied or a general expectation -> no test", against description.md:38 (R8) "an implied consequence of a stated invariant is required" and rollout.md:39-41 "A case a sentence covers literally ... is stated even when no sentence names it".

What an agent does: it adds stage-4 tests grounded on the repo, then drops them at the "before each paste" check, then a
sweep re-raises them as GAP. That flip can repeat.

## 13. UNDEF/MISSING: tools and files the stages depend on do not exist
- PIPELINE.md:19 stage 6 "The corpus runner replays every wrong design ... and platform patch", while TOOLS.md:18 marks it "| corpus runner | next |" (not built). TOOLS.md:19 "evidence manifest + FP barrier | next".
- difficulty.md:69 "Run it on the planned tests built from the section 1 rows (eval/variants.py)". No card or TOOLS row says how to make it.
- PIPELINE.md:67 "the configured fresh read-only `codex_review.sh` route and reviewer skill". There is no such tool in tools/ or tools/lib/, and "reviewer skill" is not named.
- agents/*:14 "~/.claude/skills/olympus-flow/references/checks.md, tests-harness.md, solution.md: the current rules". skill/ has no references/ folder. auto-reviewer.md:38-39 and fp-auditor.md:35-36 still say "Read first" for the LEGACY `olympus-challenge-creation/references/site-rubric.md`, `fp-runner.md`, `auto-review-selfcheck.md`.
- replicas/sweep-brief.md:10 and agents/*:24 "eval/gates.md, eval/battery-*.log". No card says to write these files or what goes in them.
- description.md:129-130 "the ledger's \"Hard points (not named)\" list". ledger-template.md has no such section.
- description.md:89 "Obligation ledger (eval/description_facts.md)" makes a second ledger, against SKILL.md:13-14 "[the ledger] is the single contract".
- PIPELINE.md:70 "Configure other lanes explicitly with the coordinator". "The coordinator" is never defined.

## 14. UNDEF: ID collisions
- tests.md has steps "T1"-"T6" and solution.md has "S1"-"S5", while the platform rubric is T1-T8 and S1-S4 (build-checklist.md:369-383). PIPELINE.md:17 "Follow T1-T6/H1-H6" and :18 "Follow S1-S5". So "T5" means either "Control time and faults" (tests.md:28) or "no unspecified behaviour" (rubric).
- situations.md:5 "S0-S1 = stages 0-3, S2 = stage 5, S3 = stage 4, S4 = stage 6, S8 = stages 8-10", while the same file uses row IDs S-1..S-9 and T-1..T-11. S5/S6 are used but never mapped: replicas/sweep-brief.md:1 "(S5, one round ...)", seam-bank.md:5 "while a task is in S2-S6", situations.md:30 "S2-S6 evidence". problem-design.md:105 "S1 lock ... S2 starts" uses S-numbers as stages with a different meaning.
- build-checklist.md cites "(R2)", "(R3)", "(R5)", "(R7)", "(R8)" (e.g. :93, :137, :246, :248, :330) from an outside "Astra review R1-R8" (:56), which clash with description.md R1-R16. Also M1-M6, C01-C31, P1-P15, A2, B1, "codex 1-8" all point to vet/eval files that are not in the kit.

## 15. CONTRA: the requirement-count limit (rewording loop at stage 2-3)
- description.md:20 "at most **9 requirement units** (target 5-8)"; SKILL.md:32 "the hard limit is 9 requirement units".
- replicas/dq.md:23-25 "<= 14 units passed 8 of 8, >= 19 failed 5 of 5 ... `blocking: true` at >= 19, and at 15-18 when ..."; dq.md:29 "typically 8 or more such independent asks".
- replicas/CALIBRATION.md:32 "dq v2 | ... blocking at >= 11".
- situations.md:22 (D-1) "Over 9 requirement units ... | <= 14 passed 8/8, >= 19 failed 5/5".
- The stop rule description.md:105 "When the DQ replica's count equals the number of tested outcomes, stop rewording" is a different test from the 9-unit cap.

---

## Lower-ranked

16. CONTRA (agents, internal): auto-reviewer.md:50 "build it as a mutant of the reference" and :53-56 "Write BOTH wrong implementations as reference mutants and RUN them ... try 10 s, 60 s and 600 s" against :180 "Never run mutation batteries, mutant sweeps ... the coordinator does mutation once after all checks". auto-reviewer.md:176-177 "Advisory coverage gaps ... are to be reported as findings with the smallest fair test, not ignored" goes against platform.md:61-62 (triage partials, "otherwise leave it and say why"), CALIBRATION.md:103-106 (coverage-to-yes removed 2026-11-11) and verify.md:18-21 (drop combination corners).
17. LOOP (agents): about 25 headed sections end in "- check every one" or "MANDATORY" (e.g. auto-reviewer.md:150, 164, 330, 345, 442 "MANDATORY, do it FIRST"; sq-judge.md:305, 319, 363, 408, 577; tq-judge.md:460, 501). They are faust, elio and swift specific. Only the sweep-mode header (:19-20) says "The faust/Python patterns below are EXAMPLES". An agent on a new repo walks all of them.
18. CONTRA: platform.md:66-68 "a mismatch ... is fixed as a general rule in replicas/ (replicas/CALIBRATION.md has the method)". This is product work in the middle of a task, and CALIBRATION.md:9-10 says "The data and scripts of that run are not part of this repository".
19. UNDEF (references a new agent cannot look up): "claude2" (hunt.md:5, PIPELINE.md:34, :70) is never defined; "Nova" has no harness or model (profiles.md:54); models are named "GPT Sol 6.1" (SKILL.md:41), "GPT Sol 6 medium" / `gpt-6-sol` (PIPELINE.md:34) and `gpt-6.1-sol` (seam-bank.md:34); "$OLYMPUS_SHARED_ROOT", "$OLYMPUS_SEAMS_ROOT" (hunt.md:11, :65); "MAP.md (workflow-build-20261105)" (situations.md:3, problem-design.md:4); "backlog #15" (near-miss-release.md:137); "TPQ" (description.md:36); "Harbor rebuild-safe" (platform.md:57); "Iron 4 per hour" (platform.md:21); "both machines", "the other machine" (PIPELINE.md:91-92); agents "Shared-memory digest (repo memory sync 2026-10-25)" (auto-reviewer.md:494, sq-judge.md:559, tq-judge.md:377); gates.md:22 "verify current criteria when starting a task" (no way to verify is given).
20. MISSING: the Dockerfile's platform build result is never a gate, but difficulty.md:83 says "Never change the Dockerfile after them" (the stage-3 runs). PIPELINE.md:6 says "paste, notify, keep going". A late build failure after the stage-3 paste has no path.
21. MISSING: stage 9 "Freeze and hand over ... Call this LOCAL READY, not platform accepted" (PIPELINE.md:25) comes after 7b/8/8b, when the platform has already graded v1. Then stage 10 repeats the checks. The real order of freeze, v1 and hand-over is unclear.
22. CONTRA: problem-design.md:26 "Nova runs ... almost never pass" against profiles.md:58 "No longer near 0%: direct-deps 3/4". seam-bank.md:12 "boundaries (>= 4 ...)" against hunt.md:47 "3-4 stated consequences" and problem-design.md:99-100 ">= 4 / 1-2 hard points" (broken line).
23. CONTRA (FP audit count): PIPELINE.md:33-34 (owner-asked local solves) always uses 2 audits, against PIPELINE.md:50-51 "one per passing run; a second only when the first says NOT_DESERVED". rollout.md:44 "both false-pass auditors run on the candidate", which implies two always.
24. MINOR: apply-build-checklist.md:28 "Before the v1 paste, run `check --through 7`", while PIPELINE.md:20 places it at 6a, before stage 7. CALIBRATION.md:73-74 has a duplicated, garbled "Next:" sentence. CALIBRATION.md:15 "templates/accepted" should be templates/examples/accepted.
25. Standing triggers that are cheap and fine: platform.md:35 "Before every paste and every status claim ... pull"; build-checklist.md:49-50 "Re-mark every test added after the lock before each paste". Listed only for completeness.
