# Chosen repository to hand-over

Use a private working folder and immutable version snapshots. Never alter the
chosen base checkout or a frozen/pasted package. The owner writes the final
description, builds the image on the platform, and runs platform checks/rollouts.
Draft upload is a separate action requiring authorization in the active task;
prepare all fields before it. This skill does not authorize platform mutations.

| Stage | Inputs -> construction outputs | Exit gate and human action |
|---|---|---|
| 0. Qualify | Chosen repository, seam, current platform criteria -> ledger Identity and Profile; exact commit/tree, source inventory, CI commands, affected regressions, supported domain | Verify novelty/eligibility from current evidence without starting another hunt. Confirm the problem exists at the pin and is observable offline. Record missing facts as NOT VERIFIED. No LOC quota or assumed language. |
| 1. Environment first | Profile -> Dockerfile, runner skeleton, immutable image identity, base-ID inventory | Follow E1-E5/H1-H6. Build once per complete environment identity; run baseline and adapter failure probes. **Human builds this Dockerfile on the platform**; preserve its result separately from local proof. Environment failure returns here, not to task wording. |
| 2. Define meaning | Pinned code, working environment -> atomic obligations, path/fault inventory, discriminator and valid-alternative plans, draft | Follow description.md section 3, part A (steps 1-8: problem, obligation ledger, feasibility gate, variants, draft, word reach, two reading audits with adjudication, counts). Prove feasibility of the difficult path with a small disposable experiment; it is not the final solution. Two independent readers resolve output-changing interpretations. No undecided public behavior at lock. |
| 3. Human wording and lock | Audited draft + fact ledger -> human's final description, meaning diff, hash | **Human writes the final words.** Follow description.md section 3, part C (steps 9-11: counterexample diff, re-check of changed words, lock record) on those exact bytes. Fix unintended meaning changes before lock. Later wording/scope changes require an explicit redesign decision and fresh solve evidence. |
| 4. Tests and sample | Locked text + planned ledger -> real test.patch including executable test.sh, fixtures, stable IDs | Follow T1-T6/H1-H6. Base-mode/base passes; each new ID fails on base for its intended reason. Prepare the sample with real tests and a clearly labeled provisional solution where the current platform permits it. **Human runs prechecks and Scope Gate.** Scope rejection stops this candidate; sample results never certify final quality. |
| 5. Reference | Same contract/path inventory -> solution.patch, native quality evidence | Follow S1-S5; every in-scope path implemented and tested. A sample stub is replaced. Reconstruct exported patches, not just the development checkout. |
| 5b. First draft to the owner | Locked description + tests + reference with G0 four cells passing -> pasted draft | Paste the first complete draft (the owner authorizes uploads). **Owner runs the platform checks and the 2-2-2 rollout.** The builder does not wait: stages 6-7 continue on the same version; any fix is pasted as a new version before the owner's next run. Rollout results enter at stage 9. |
| 6. Deterministic closure | Four artifacts + variants + available solver patches -> four-cell proof, failure-probe evidence, discrimination/fair-alternative results | Run G0, then gate order G1 -> G2 -> G3 -> G4. No OPEN in-scope obligation, unexplained survivor, failed valid alternative, or stale execution evidence. |
| 7. Owner's confirmation | Frozen candidate -> three sweeps of two independent lanes, two independent FP audits per passing run, two platform-style replica rounds | Follow the fixed schedule below. Findings invoke Repair before the next checkpoint. Required independent samples cannot be cached away. |
| 8. Freeze and hand over | Closed candidate -> final four-cell/offline/stability proof, immutable package, exact hashes, ledger and compact hand-over | Final new-mode stability: six base and six reference runs with identical per-ID vectors; investigated differences block. Include repo URL, full pin, title/category/language, four files, image/build evidence, check IDs and remaining external gates. Call this LOCAL READY, not platform accepted. |
| 9. Human platform validation | Exact frozen fields -> current prechecks, quality checks, 2-2-2 rollout and FP findings | **Human runs checks/rollouts.** Read results via CLI after `--help`; compare uploaded/downloaded bytes. Classify every run; shape with [rollout.md](rollout.md). Repair in a new version, then repeat affected gates. |

## Confirmation schedule and remaining model runs

1. At stage 2, two independent reading samples see draft + pinned repository only.
   Their question is semantic ambiguity/discoverability; grep cannot decide it.
2. No local blind solves (owner decision 2026-11-07). Solver evidence comes from the
   platform: when every platform check passes, the owner runs a 2-2-2 rollout (two runs
   per model family). Do not wait for it: from the first locked draft onward keep
   closing gaps (sweeps, replica rounds, repair). When the rollout lands, pull every
   run read-only, add every patch to the permanent false-pass corpus, and follow
   [rollout.md](rollout.md). Replays of one trajectory are not new runs.
3. Stage 7: sweep 1 (lanes A/B) -> repair; sweep 2 (fresh A/B) -> repair;
   sweep 3 (fresh A/B) -> repair; replica round 1 -> repair; replica round 2 -> repair.
   Each sweep lane independently covers the entire G1-G4 contract. Each replica
   round independently emits all gate fields in gates.md. These are the owner's
   required samples; they look for semantic omissions beyond enumerated examples.
4. Every current passer receives two independent FP audits of its actual design.
   This is separate from auditing the reference. No passers means no FP audit jobs,
   and no evidence of solvability. Auditors may overlap read-only confirmation work.
5. After the final checkpoint, any fix needs Repair and affected semantic reclosure
   on the new snapshot. Do not restart all five checkpoints by default or silently
   bless changed files with old verdicts. Unclosed findings block hand-over.

All review inputs include exact artifact identities and the literal contract;
independent lanes do not read one another's conclusions. Merge their finding union,
not the report with the most findings. Package reviews on this machine use the
configured fresh read-only `codex_review.sh` route and reviewer skill; do not silently
substitute the builder session. Configure other lanes explicitly with the coordinator.

Container limits come from the machine profile (machine/*.json: slots, memory,
parallel workers, cleanup permission), never from this file; run Docker work through
the profile's `dockrun.py` lock. Every long job is its own tracked background command
that blocks until it ends (no `&`, no detached shells), one per lane, so each lane's
completion is seen at once. Queue experiments while independent reading proceeds.

Time boxes (owner target 2-4 h local work; platform and human waits counted apart):
0 Qualify 20 m | 1 Environment 20 m + owner build | 2-3 Meaning and lock 40 m + owner
rewrite | 4 Tests 45 m | 5 Reference 45 m | 6 Closure 20 m | 7 Confirmation 3 x 35 m
(sweeps) with replica rounds alongside | 8 Freeze 20 m. An overrun triggers a progress
report and a decision with the owner, never an omitted gate or a post-lock scope cut.
