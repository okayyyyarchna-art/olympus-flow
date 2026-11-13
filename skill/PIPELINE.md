# From a repository (or none) to hand-over

Use a private working folder and immutable version snapshots. Never alter the
chosen base checkout or a frozen/pasted package. The owner writes the final
description, builds the image on the platform, and runs platform checks/rollouts.
The Dockerfile and sample pastes are ordinary steps: paste, notify, keep going. From v1 on, ask
first; never paste while a platform run or check is active, it would stop the run (owner 2026-11-09).

| Stage | Inputs -> construction outputs | Exit gate and human action |
|---|---|---|
| 0. Find and qualify | The owner's repository, or none -> picked repository, seam, ledger Identity and Profile; exact commit/tree, source inventory, CI commands, affected regressions, supported domain | [hunt.md](hunt.md): with no repository, part A finds one (platform repo rules, 3 lanes, the owner checks submission counts); with a repository, part B finds the seam (3 lanes, filters, score, top 3 verified). **Decision inventory on the pick by a fresh reader ([difficulty.md](difficulty.md) section 1): the planned separators and the calibration reserve (section 5); no verdict here, the gate is the stage-2 spike.** Confirm the problem exists at the pin and is observable offline. Record missing facts as NOT VERIFIED. No LOC quota or assumed language. |
| 0b Repository init | Pinned repository + machine profile -> [repo_init.py](tools/repo_init.py), profile.json, init/Dockerfile and init/test.sh from language templates | Run [repo_check.py](tools/repo_check.py): locked build, native ID qualification, offline base and H6 failure probes. Resolve profile.open explicitly; base-adapter qualification does not certify feature four-cell proof or the human platform build. |
| 1. Environment first | Profile -> Dockerfile, runner skeleton, immutable image identity, base-ID inventory | Follow E1-E5/H1-H6. Build once per complete environment identity; run baseline and adapter failure probes. **Human builds this Dockerfile on the platform**; preserve its result separately from local proof. Environment failure returns here, not to task wording. |
| 1b. Sample and Scope Gate | Builder's own draft description + a basic test.patch (one plain test per sentence, real test files, executable test.sh from the template) + a small solution sketch -> pasted sample | Only purpose: pass the platform prechecks and reach the Scope Gate. Minutes, not a build: no proof, no gates, no check that the tests pass or fail. **Owner runs prechecks and Scope Gate.** Stage 2 starts right after the paste, with no wait for the result: the Scope Gate runs in parallel (owner 2026-11-13: the product works in continuation). A reject stops this candidate (never reword and retry); the work done meanwhile is the accepted cost. Later pastes mark the Scope Gate stale; the owner re-runs it on the final package. |
| 2. Define meaning | Pinned code, working environment -> atomic obligations, path/fault inventory, discriminator and valid-alternative plans, draft | Follow description.md section 3, part A (steps 1-8: problem, obligation ledger, feasibility gate, variants, draft, word reach, two reading audits with adjudication, counts). Prove feasibility of the difficult path with a small disposable experiment; it is not the final solution. **Gate: the obvious-design spike (difficulty.md section 3) must fail on at least two different decisions before the lock; if not, the runner-up seam, then widen once (difficulty.md section 2).** Two independent readers resolve output-changing interpretations. No undecided public behavior at lock. |
| 3. Human wording and lock | Audited draft + fact ledger -> human's final description, meaning diff, hash | **Human writes the final words.** Follow description.md section 3, part C (steps 9-11: counterexample diff, re-check of changed words, lock record) on those exact bytes. Fix unintended meaning changes before lock. **The lock is final**: no calibration step changes the text; only a change the owner asks for (description.md section 5b) or REDESIGN can, after an impact analysis. **Then paste the locked text with the sample tests and notify the owner: the owner runs 2 Orion + 2 Vega** (difficulty.md section 4) so the builder sees how the agents read this text; they count toward the final 4-4-4. Stages 4-5 go on locally meanwhile; their stop signal and keeper are read as soon as they end. |
| 4. Tests | Locked text + planned ledger -> real test.patch including executable test.sh, fixtures, stable IDs | **Start with [prompts/apply-build-checklist.md](prompts/apply-build-checklist.md); `tools/checklist_gate.py check --through 5` passes before any code.** Built by walking build-checklist.md (ledger first). Follow T1-T6/H1-H6. Base-mode/base passes; each new ID fails on base for its intended reason. Shaped on the stage-3 runs (difficulty.md section 4): the keeper and the reference pass; every gap of the other runs, V-OBVIOUS and the variants gets a fair test. |
| 5. Reference | Same contract/path inventory -> solution.patch, native quality evidence | Follow S1-S5 and build-checklist.md step 6; every in-scope path implemented and tested. |
| 6. Deterministic closure | Four artifacts + variants + known patches -> four-cell proof, failure-probe evidence, corpus results | Starts after the stage-3 runs are pulled and the keeper is chosen (difficulty.md section 4); stages 4-5 may start before. Run G0, then gate order G1 -> G2 -> G3 -> G4. The corpus runner replays every wrong design (must fail), valid alternative (must pass) and platform patch. No OPEN in-scope obligation, unexplained survivor, failed valid alternative, or stale execution evidence. |
| 6a. Reference audit | Closed candidate -> one strict audit of the reference | `tools/replica.sh <task> ref-audit pre1` before v1, and `checklist_gate.py check --through 7`. Fix each reproduced BROKEN promise and add its test (vet task 2: this kind of audit found 3 of the 4 reference breaks, but only after v1). |
| 7. Local confirmation | Closed candidate (not pasted yet) -> sweep 1, replica batch, verification batch, sweep 2 only on its trigger | Schedule below; one fix batch per step through Repair. |
| 7b. v1 paste (the complete package, once) | Closed stage-7 candidate -> pasted v1 | Clean-repo proof, paste, confirm the fields, then **notify the owner** (push notification + message: version, hashes, "run the checks and the rest of the rollout"). The owner runs the full checks once, the re-eval of the four stage-3 runs, and 2 Orion + 2 Vega + 4 Nova (4-4-4 in total). The builder starts tools/watch.sh and pulls read-only. |
| 8. Rollout analysis | Platform runs (any version) -> classified runs, FP audits, shaping plan | Pull read-only; run the calibration reserve probes on every passer, then replay every agent patch on the current files (replay_plan.py + corpus); FP audits per the schedule; shape with [rollout.md](rollout.md); update [profiles.md](profiles.md). What the agents show about the description goes into the rulebook for the next task, never into this text. Every change is predicted by a local replay before its paste. |
| 8b. v2 paste (calibration, only when needed) | Shaped candidate + predicted re-eval -> pasted v2 | Only when the 4-4-4 is outside the band (several passers, or none) or a check failed. Re-eval readiness check passed (rollout.md step 5, one replica round on the changed files). **Notify the owner**: changed files, predicted result per family, the affected checks; a re-eval of the stored runs, no new runs. If the re-eval is still outside the band, stage 8 runs once more (v3) the same way; after that the builder names the one blocker to the owner (rollout.md step 6). |
| 9. Freeze and hand over | Closed candidate -> final four-cell/offline/stability proof, immutable package, exact hashes, ledger and compact hand-over | Final new-mode stability: six base and six reference runs with identical per-ID vectors; investigated differences block. Include repo URL, full pin, title/category/language, four files, image/build evidence, check IDs and remaining external gates. Call this LOCAL READY, not platform accepted. |
| 10. Human platform validation | Exact frozen fields -> readiness re-checks before submit (prechecks, rebuild-safe), the FP panel; the rollout is the 4-4-4 already run at stages 3 and 7b | **Human runs checks/rollouts and submits.** Read results via CLI after `--help`; compare uploaded/downloaded bytes. Classify every run with [rollout.md](rollout.md). |

## Review schedule (overrides every other card, every agent definition and every memory note)
Model reviews (reading audits, sweeps, replica batches, the reviewer agents, FP audits) run only at these points. A fix
never starts a review round by itself: it is closed with deterministic evidence at once (gates.md Repair step 6) and
re-judged at the next point in this table. A memory note or an older card that sets another cadence ("after every
change", "before every paste", "every round runs X") is superseded by this table.
| Point | What runs | How many times |
|---|---|---|
| Stage 2 step 7 | two reading audits (description.md) | once per draft; step 10 re-checks only the changed words |
| Stage 2 steps 8 and 10 | DQ replica | once at step 8, once on the owner's final bytes |
| Stage 4 (checklist step 9) | one fresh checklist reviewer after checklist steps 6 and 8 | once each; the builder fixes the rows it rejects, no second review |
| Stage 6a | `replica.sh <task> ref-audit pre1` | once, before v1 |
| Stage 7 | sweep 1 -> fix batch -> replica batch -> fix batch -> verification batch | once each |
| Stage 7, only on its trigger | sweep 2 -> fix batch -> one more verification batch | once; there is no sweep 3 |
| Stage 8 | one FP audit per passing run (a second only when the first says NOT_DESERVED or is unclear) | once per run |
| Stage 8b, before a calibration paste | one replica round on the changed files (rollout.md step 5, item 4b) | once per paste |

Terms: a **sweep** is `tools/sweep.sh <task> <tag>` with every lane following replicas/sweep-brief.md (the reviewer
agents olympus-auto-reviewer, olympus-sq-judge and olympus-tq-judge are its in-process lanes). A **replica batch** and a
**verification batch** are each one `tools/round.sh <task> <tag>` run (fairness, sq, dq and ar replicas, ar after dq,
then verify and the gate). A **new class of finding** is a finding whose kind no earlier finding of this task had; a new
instance of a known kind is fixed through Repair and never triggers sweep 2. If the last verification batch still
reproduces a finding: fix it through Repair, prove the fix deterministically, and report it to the owner; no further
batch runs. Checklist rows sharpened during a task (item 4 below) apply from the next task; the current task's sheet
is not regenerated for them.

## Confirmation schedule and remaining model runs

1. At stage 2, two independent reading samples see draft + pinned repository only.
   Their question is semantic ambiguity/discoverability; grep cannot decide it.
2. No local blind solves unless the owner asks for them (owner decision 2026-11-07). When the owner
   asks, grade them as soon as they finish, and start the FP audits of every passer in the same step, without
   asking: 1 GPT Sol 6 medium + 1 claude2 Opus 5.5 high (`REPLICA_MODEL=gpt-6-sol REPLICA_EFFORT=medium replica.sh <task> fp-audit <solve>` plus `claude2_run.sh fp <task> pkg <brief> high`).
   Report the solver results together with the audit verdicts. Solver evidence otherwise comes from the
   platform: 2 Orion + 2 Vega on the locked text at stage 3, then 2 Orion + 2 Vega + 4 Nova on v1. Three runs
   per family show the direction; the band is judged at 4+ runs per family, and Nova needs
   4 runs before submit. Replays of one trajectory are not new runs. Runs failing a hard point, local or platform, are
   the task working and never a reason to reword it (description.md section 5).
3. Stage 7 order: sweep 1 (all lanes, one round) -> triage -> one fix batch -> replica
   batch (3 independent replicas in parallel on the same frozen files; Codex GPT Sol 6
   medium; 25 min time box each) -> the builder judges every finding at once -> one fix
   batch -> verification batch (3 replicas). If the verification batch reproduces a new
   class of finding: sweep 2 (once) -> fix -> one more verification batch as the gate.
   There is no sweep 3. (vet: replica rounds took 6-19 min, sweeps 28-95 min.)
4. Every reproduced finding gets a cause. Description: it goes to the owner; the text stays
   locked unless the owner takes the exception. Checklist: sharpen the row that should have
   caught it (the example and why it slipped), or add a row when no rule covers it. The row applies from the next
   task (Review schedule above).
   Unreproduced findings change nothing.
5. FP audits: one per passing run; a second only when the first says NOT_DESERVED or is
   unclear. Each audit replays its probe on the reference too (build-checklist step 8). Each probe runs once unless a
   result looks flaky (vet task 2: audits repeating probes 3x held the Docker queue for about 50 min).
   Before probe-heavy audits, add up their containers against the Docker slots: at most 2-3 audits at once, one container
   each.
6. After the final checkpoint, any fix needs Repair and affected semantic reclosure
   on the new snapshot. Do not restart all checkpoints by default or silently
   bless changed files with old verdicts. Unclosed findings block hand-over.
7. The clean-repo proof certifies the exact files of a paste: run it once right before each paste and at the freeze,
   with no other Docker jobs running (its duration limits count host load). Between pastes use only the container
   cells and the variants job.
8. A changed product tool is smoke-tested end to end on a known-good package before a task uses it (vet task 2: six
   proof.py defects surfaced one per run).

All review inputs include exact artifact identities and the literal contract;
independent lanes do not read one another's conclusions. Merge their finding union,
not the report with the most findings. Package reviews on this machine use the
configured fresh read-only `codex_review.sh` route and reviewer skill; do not silently
substitute the builder session. Configure other lanes explicitly with the coordinator.
Codex runs the workflow sweeps and replica checks. Ad-hoc analysis (calibration comparisons, discriminator searches,
verdict estimates) runs in-process plus claude2; Codex only when the owner names it or both lanes found nothing.

Review briefs carry the description verbatim. Never write "not promised", "out of scope" or "known residual" unless the
text excludes the case, never list known-and-kept items, and describe what changed, never that it resolves a finding
(swift: a brief's scope claim preceded SQ 1/3 High on that branch).

Container limits come from the machine profile (machine/*.json: slots, memory,
parallel workers, cleanup permission), never from this file; run Docker work through
the profile's `dockrun.py` lock. Every long job is its own tracked background command
that blocks until it ends (no `&`, no detached shells), one per lane, so each lane's
completion is seen at once. Stop a lane by its tracked job, never by matching a command line (vet task 2: a match
killed a second lane). On Windows that stop ends only the outer shell: then find the processes whose command line
holds that job's own unique path, `taskkill /PID <pid> /T /F` them, and re-list. Queue experiments while independent reading proceeds.

Time boxes (owner target 2-4 h local work; platform and human waits counted apart):
0 Qualify 20 m | 1 Environment 20 m + owner build | 2-3 Meaning and lock 40 m + owner
rewrite | 1b Sample 15 m + owner Scope Gate | 4 Tests 45 m | 5 Reference 45 m | 6 Closure 20 m |
7 Confirmation: sweep 1 35 m + replica batch 20 m + verification batch 20 m (sweep 2 35 m only on its
trigger) | 9 Freeze 20 m. An overrun triggers a progress
report and a decision with the owner, never an omitted gate or a post-lock scope cut.

## Metrics record (every task, both machines)
At hand-over write `metrics/<task>.json` in the product repo and commit it (the other machine pulls it): machine,
repo, language, minutes per stage, description changes after the lock, new findings per sweep and replica batch,
checklist rows sharpened or added, false alarms, false-pass escapes (found after the last verification batch or by
the platform), platform checks passing on the first run, and
the rollout result per family. Success criteria (fixed 2026-11-07, vet task as the baseline):
| Measure | vet baseline | Target |
|---|---|---|
| Description changes after the lock | 6 | 0 |
| New findings after sweep 1 (replica and verification batches, sweep 2) | many | at most 2 small ones |
| False-pass escapes | 2 | 0 |
| Platform checks passing on the first run | several rounds | all |
| Total local time | ~24 h | <= 5 h Windows, <= 3.5 h Mac |
A missed target names the stage that failed; that stage's card is fixed before the next task.
