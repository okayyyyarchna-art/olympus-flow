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
| 2. Define meaning | Pinned code, working environment -> atomic obligations, path/fault inventory, discriminator and valid-alternative plans, draft | Follow D1-D5. Prove feasibility of the difficult path with a small disposable experiment; it is not the final solution. Two independent readers resolve output-changing interpretations. No undecided public behavior at lock. |
| 3. Human wording and lock | Audited draft + fact ledger -> human's final description, meaning diff, hash | **Human writes the final words.** Follow D6-D7 on those exact bytes. Fix unintended meaning changes before lock. Later wording/scope changes require an explicit redesign decision and fresh solve evidence. |
| 4. Tests and sample | Locked text + planned ledger -> real test.patch including executable test.sh, fixtures, stable IDs | Follow T1-T6/H1-H6. Base-mode/base passes; each new ID fails on base for its intended reason. Prepare the sample with real tests and a clearly labeled provisional solution where the current platform permits it. **Human runs prechecks and Scope Gate.** Scope rejection stops this candidate; sample results never certify final quality. |
| 5. Reference | Same contract/path inventory -> solution.patch, native quality evidence | Follow S1-S5; every in-scope path implemented and tested. A sample stub is replaced. Reconstruct exported patches, not just the development checkout. |
| 6. Deterministic closure | Four artifacts + variants + available solver patches -> four-cell proof, failure-probe evidence, discrimination/fair-alternative results | Run G0, then gate order G1 -> G2 -> G3 -> G4. No OPEN in-scope obligation, unexplained survivor, failed valid alternative, or stale execution evidence. |
| 7. Owner's confirmation | Frozen candidate -> three sweeps of two independent lanes, two independent FP audits per passing run, two platform-style replica rounds | Follow the fixed schedule below. Findings invoke Repair before the next checkpoint. Required independent samples cannot be cached away. |
| 8. Freeze and hand over | Closed candidate -> final four-cell/offline/stability proof, immutable package, exact hashes, ledger and compact hand-over | Final new-mode stability: six base and six reference runs with identical per-ID vectors; investigated differences block. Include repo URL, full pin, title/category/language, four files, image/build evidence, check IDs and remaining external gates. Call this LOCAL READY, not platform accepted. |
| 9. Human platform validation | Exact frozen fields -> current prechecks, quality checks, rollout pool and FP findings | **Human runs checks/rollouts.** Read results via CLI after `--help`; compare uploaded/downloaded bytes when available. Require current readiness and classify every run. Repair in a new version, then repeat affected gates. |

## Confirmation schedule and remaining model runs

1. At stage 2, two independent reading samples see draft + pinned repository only.
   Their question is semantic ambiguity/discoverability; grep cannot decide it.
2. After stage 3 and a usable environment, start one bounded blind solve batch if
   authorized by the task. Record model/family, effort, budget and sample IDs first.
   Give only pinned source and locked task text. Inspect isolation and completion;
   replays of one trajectory are not new solves. Local outcomes diagnose difficulty,
   not predict platform percentages. Tests/solution edits need replay, not new solves.
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

Run Docker work one container at a time through the configured `dockrun.py` lock.
Never bypass its lock or run `docker rm/rmi/prune`. Track long jobs and completion;
queue probes while independent reading proceeds. Timeboxes trigger a progress report
and a scope/budget decision, never omitted gates or automatic post-lock scope cuts.
