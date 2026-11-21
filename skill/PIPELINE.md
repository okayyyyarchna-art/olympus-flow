# From a repository (or none) to hand-over

Use a private working folder and immutable version snapshots. Never alter the chosen base checkout or a frozen/pasted
package. The owner writes the final description, builds the image on the platform, and runs platform checks and
rollouts. I paste; from v1 on I ask first, and never while a platform run or check is active (it would stop the run).

Target: the platform's rollout criteria (platform.md, read from the platform on 2026-11-21): 4+ completed runs per
family; Nova 0; Orion at least one pass and at most 25% (1 of 4); Vega at most 25%; the passing Orion runs average 256K+
tokens of sequence length (the sum over context windows of the window's peak of input + output tokens), which means
the passing run compacted once (the hosted Orion harness compacts at a peak of about 244.6K; a run that finishes
before compacting stays under about 250K however good it is). We design for 300K+ at stage 0 and measure it at stage
2 (difficulty.md section 2); nothing later in the flow can add length.

| Stage | Inputs -> construction outputs | Exit gate and human action |
|---|---|---|
| 0. Find and qualify | The owner's repository, or none -> picked repository, seam, **length design**, **test-grid budget**, ledger Identity and Profile; exact commit/tree, source inventory, CI commands, affected regressions, supported domain | [hunt.md](hunt.md): with no repository, part A finds one (platform repo rules, 3 lanes, the owner checks submission counts); with a repository, part B finds the seam (3 lanes, filters, score, top 3 verified). The length design (problem-design.md section 2): the file:line chain a solver must trace before its first correct edit, the files it must read and change, the layers crossed, the repository's own loop that keeps failing until the design is right, and the estimate in tokens. The test-grid budget (problem-design.md section 7): decision points of the planned change and the cells each universal word opens. Decision inventory on the pick by a fresh reader (difficulty.md section 1) and the calibration reserve (section 6). Confirm the problem exists at the pin and is observable offline. Record missing facts as NOT VERIFIED. No LOC quota or assumed language. |
| 0b Repository init | Pinned repository + machine profile -> [repo_init.py](tools/repo_init.py), profile.json, init/Dockerfile and init/test.sh from language templates | Run [repo_check.py](tools/repo_check.py): locked build, native ID qualification, offline base and H6 failure probes. Resolve profile.open explicitly; base-adapter qualification does not certify feature four-cell proof or the human platform build. |
| 1. Environment first | Profile -> Dockerfile, runner skeleton, immutable image identity, base-ID inventory | Follow E1-E5/H1-H6 (allowed FROM line, PATH keeps sbin, /app writable for every user, one comment block above each RUN that deviates from the base image, no test runner in RUN). Build once per complete environment identity; run baseline and adapter failure probes. **Human builds this Dockerfile on the platform**; preserve its result separately from local proof. Environment failure returns here, not to task wording. Never change a pasted Dockerfile afterwards: it loses the re-eval of every stored run. |
| 1b. Sample and Scope Gate | Builder's own draft description + a basic test.patch (one plain test per sentence, real test files, executable test.sh from the template) + a small solution sketch -> pasted sample | Only purpose: pass the platform prechecks and reach the Scope Gate. Minutes, not a build: no proof, no gates; only `test.sh new` once on base and once on the sketch, so the runner's new mode is known to run (pmg: a sample whose new mode could not run graded every solve 0). **Owner runs prechecks and Scope Gate.** Stage 2 starts right after the paste; a reject stops this candidate (never reword and retry). Later pastes mark the Scope Gate stale; the owner re-runs it on the final package. |
| 2. Define meaning and measure length | Pinned code, working environment -> atomic obligations, path/fault inventory, discriminator and valid-alternative plans, draft, **length spike result** | Follow description.md section 3, part A (steps 1-8). Prove feasibility of the difficult path with a small disposable experiment. Then the **length spike** (difficulty.md section 2): 2 local Codex solves of the draft text with the sample tests (GPT Sol 6.1 at xhigh, the Orion stand-in; `tools/solvers.sh <task> spike`), measured with `tools/seqlen.py` (the platform's count: per-window peak of input + output tokens, summed). Gate: the mean sequence length of the two solves is 300K or more and neither is under 250K (the local stand-in has a 475K window and does not compact where the hosted build does, at about 244.6K). Below it: deepen the seam (another layer, path or saved state the value must be traced through; never another rule), redraft, re-paste the sample, run the spike again; after two failed spikes the owner chooses between the runner-up seam and a redesign. The spike also shows which separators the stand-in missed: they go into the tests. Two independent readers resolve output-changing interpretations. No undecided public behaviour at lock. |
| 3. Human wording and lock | Audited draft + fact ledger -> human's final description, meaning diff, hash | **Human writes the final words** (or says in so many words "keep the draft"; "continue" never locks). Follow description.md section 3, part C (steps 9-11) on those exact bytes. Fix unintended meaning changes before lock. **The lock is final for the builder**: a finding on the text goes to the owner, who decides (description.md section 5b). Then paste the locked text with the sample tests and notify the owner: the owner runs 2 Orion + 2 Vega, and 3 Claude Opus + 3 Codex GPT local solves start at the same moment (`tools/solvers.sh`; the two spike solves count as GPT solves when only the wording changed). They count toward the final 4-4-4. **The builder never waits for them or for any owner check**: stages 4-7 go on; as runs end, their keeper, gaps and valid alternatives are folded in (difficulty.md section 4) before the v1 paste. |
| 4. Tests | Locked text + planned ledger -> real test.patch including executable test.sh, fixtures, stable IDs | **Start with [prompts/apply-build-checklist.md](prompts/apply-build-checklist.md); `tools/checklist_gate.py check --through 5` passes before any code.** Write the three lists of tq-once.md (decision points with the test that fails when only that point changes, call forms, sentences split on their triggers) before the first test; keep a scripted wrong version for every gap from the start (`eval/wrong/kept/`, `tools/wrong_versions.py`). Follow T1-T6/H1-H6 and the hard rules of tests.md. Each new leaf fails on base for its intended reason. Shaped on the solver runs (difficulty.md section 4). |
| 5. Reference | Same contract/path inventory -> solution.patch, native quality evidence | Follow S1-S5, build-checklist.md step 6 and sq-once.md (promise x path grid, decision rows, rejection ledger, touched-site ledger). Reference scope = test scope: a behaviour no hidden test checks is tested or removed. Before changing an unexported type or signature, grep the upstream tests of the package: a pinned test is a contract for every solver. |
| 6. Executed closure | Four artifacts + variants + known patches -> `tools/fastcheck.sh` VERDICT PASS, failure-probe evidence, corpus results | Runs as soon as the tests and the reference exist. The fast check: four cells with T1 per leaf, root baseline and the two-user cell with the JUnit set check (the platform's verifySolution), every kept wrong version caught and every control passing, the mutant sweep with every survivor triaged, default-path timing at 1x and 2x input, the base-mode regression list with importers and helper pins, the repository's own gate tests, lint, no skips, OS limits gated, and the unchanged-input regression sweep against upstream. The corpus replays every wrong design (must fail), valid alternative (must pass) and solver patch. Run G0, then G1 -> G2 -> G3 -> G4 of gates.md. No OPEN in-scope obligation, unexplained survivor, failed valid alternative or stale evidence. |
| 6a. Reference audit | Closed candidate -> one strict audit of the reference | `tools/replica.sh <task> ref-audit pre1` before v1, and `checklist_gate.py check --through 7`. Fix each reproduced BROKEN promise and add its test. |
| 7. One replica round | Closed candidate (not pasted yet) -> one round of platform replicas, one fix batch, one verification round | `tools/round.sh <task> r1`: fairness, sq, dq, ar, then verify, on Codex; the Claude reviewer agents (tq-judge, sq-judge) are the second lens when the owner wants two lanes; each lane 40 minutes. Triage every finding (reproduce before fixing; "equivalent" only after an executed search), fix the whole class in one batch, close it with the fast check, then one verification round on the lanes whose inputs changed. Then v1. There is no second phase: a later platform finding is answered with the repair loop of tq-once.md / sq-once.md (reproduce as a kept wrong version or an executed input, sweep its class, fix once, fast check), never with a new review phase. |
| 7b. v1 paste (the complete package, once) | Closed stage-7 candidate -> pasted v1 | Fast check on the exact files, paste, confirm the fields, then **notify the owner** (version, hashes, the check order of platform.md, and "the re-eval of the four stage-3 runs, then 2 Orion + 2 Vega + 4 Nova"). The builder starts tools/watch.sh and pulls read-only. |
| 8. Rollout analysis | Platform runs (any version) -> classified runs, FP audits, shaping plan | Pull read-only; `tools/rollout_report.py` gives per run the family, misses, verdict, sequence length, compaction and requests, and the criteria table; the platform junit is the truth for a run (a local replay can pass what the platform failed). Run the calibration reserve probes on every passer, then replay every agent patch on the current files; FP audits per the schedule; shape with [rollout.md](rollout.md); record the harness fingerprint (`tools/scout/`) and update [profiles.md](profiles.md). What the agents show about the description goes into the rulebook for the next task, never into this text. Every change is predicted by a local replay before its paste. |
| 8b. v2 paste (calibration, only when needed) | Shaped candidate + predicted re-eval -> pasted v2 | Only when the 4-4-4 is outside the criteria or a check failed. Re-eval readiness passed (rollout.md step 5, one replica round on the changed files). **Notify the owner**: changed files, predicted result per family, the checks it reopens; a re-eval of the stored runs, no new runs. If still outside after v3, the builder names the one blocker (rollout.md step 6). |
| 9. Freeze and hand over | Closed candidate -> final fast check, immutable package, exact hashes, ledger and compact hand-over | Final new-mode stability: six base and six reference runs with identical per-ID vectors; investigated differences block. Include repo URL, full pin, title/category/language, four files with hashes, image/build evidence, check IDs with the version each graded, the criteria table of rollout_report.py and the remaining platform steps. Call this LOCAL READY, not platform accepted. |
| 10. Human platform validation | Exact frozen fields -> readiness re-checks before submit | **Human runs checks, rollouts, Trial QA and submits.** Readiness: prechecks (repository verification fresh), Scope Gate, the quality checks, Rebuild-safe and Harbor rebuild-safe, the rollout criteria, and `trialQa` (a readiness item the platform added on 2026-11-17; its procedure has not been seen yet: record what it asks for the next task). Compare uploaded/downloaded bytes. Classify every run with [rollout.md](rollout.md). |

## Review schedule (overrides every other card, every agent definition and every memory note)
Model reviews run only at these points. A fix never starts a review round by itself: it is closed with executed
evidence at once (gates.md Repair step 6, the fast check) and re-judged at the next point in this table. A memory
note or an older card that sets another cadence ("after every change", "before every paste", "three phases", "rounds
until 3/3") is superseded by this table.
| Point | What runs | How many times |
|---|---|---|
| Stage 2 step 7 | two reading audits (description.md) | once per draft; step 10 re-checks only the changed words |
| Stage 2 steps 8 and 10 | DQ replica | once at step 8, once on the owner's final bytes |
| Stage 2 | the length spike: 2 Codex GPT Sol 6.1 xhigh solves of the draft (difficulty.md section 2) | once per draft; again only after a deepening |
| Stage 4 (prompts/apply-build-checklist.md step 9) | one fresh checklist reviewer after checklist steps 6 and 8 | once each; the builder fixes the rows it rejects, no second review |
| Stage 6a | `replica.sh <task> ref-audit pre1` | once, before v1 |
| Stage 7 | one replica round (fairness, sq, dq, ar, verify; the Claude reviewer agents as a second lens on request) -> one fix batch -> one verification round on the lanes whose inputs changed | once; then v1 |
| A platform finding | the repair loop (tq-once.md / sq-once.md): reproduce it as a kept wrong version or an executed input, sweep its class, fix once, fast check; re-run only the replica lane of that check on the changed input | per finding; never a new review phase |
| Stage 8 | one FP audit per passing run (a second only when the first says NOT_DESERVED or is unclear) | once per run |
| Stage 8b, before a calibration paste | one replica round on the changed files (rollout.md step 5, item 4b) | once per paste |

Terms: a **replica round** is one `tools/round.sh <task> <tag>` run (fairness, sq twice, dq and ar replicas on Codex
GPT Sol 6.1 medium through `tools/replica.sh`, ar after dq, then verify and the gate: six Codex jobs). The Claude reviewer agents
(olympus-tq-judge, olympus-sq-judge, olympus-auto-reviewer, olympus-fp-auditor; Opus 5.5 medium) are the second lane
when the owner asks for two lanes or Codex is unavailable (a usage limit falls back to them); each follows its replica
prompt and reads only the inputs its launch message names (task folder, report path, image, test command, time box,
and for the tests lane the raw variant results). Every lane brief names the kit's `replicas/` files directly, never a
task copy. Every lane has a 40-minute time box: at the box it writes its
report with what is NOT VERIFIED and kills its own wait loops. `tools/sweep.sh` (the wide gap sweep) is kept for a
platform failure the repair loop cannot place, at the owner's request. A **new class of finding** gets a checklist
row for the next task; a new instance of a known class is fixed through Repair.

## Confirmation schedule and remaining model runs
1. At stage 2, two independent reading samples see draft + pinned repository only. Their question is semantic
   ambiguity and discoverability; grep cannot decide it.
2. The length spike at stage 2: 2 Codex solves on GPT Sol 6.1 at xhigh (Orion's model and effort; the same harness
   family, but a 475K local window: it does not compact where the hosted build does, at about 244.6K, and it reasons
   2-3x more per request, so local lengths overstate hosted ones: that is why the local bar is a mean of 300K for a
   256K gate, measured in the platform's own count). Measure with `tools/seqlen.py` (windows, peaks, requests,
   compaction); record which planned separators each solve missed. Both solves count as owner-asked solves: grade
   them, and audit a passer as soon as a full reference exists.
3. Solver runs after the lock: 3 Claude Opus 5.5 high + 3 Codex GPT Sol 6.1 xhigh local solves (`tools/solvers.sh`)
   and the owner's 2 Orion + 2 Vega on the platform, all in parallel while the build goes on (difficulty.md section
   3). Grade the local ones as soon as they finish, and start the FP audits of every passer in the same step, without
   asking: 1 Codex GPT Sol 6.1 medium (`replica.sh <task> fp-audit <solve>`) + 1 Claude Opus 5.5 medium
   (olympus-fp-auditor, in-process or on the second account). Report solver results together with the audit verdicts.
   Runs failing a hard point, local or platform, are the task working and never a reason to reword it.
4. Stage 7 is one round. Every reproduced finding gets a cause. Description: it goes to the owner; the text stays
   locked unless the owner takes the exception. Checklist: sharpen the row that should have caught it, or add a row
   when no rule covers it; the row applies from the next task. Unreproduced findings change nothing.
5. FP audits: one per passing run; a second only when the first says NOT_DESERVED or is unclear. Each audit replays
   its probe on the reference and records the three columns of rollout.md lever 2 (sentence, behaviour before the
   change, origin of the reference rule). Each probe runs once unless a result looks flaky. Audits take turns on the
   Docker slot with the fast check: never two heavy containers at once.
6. After the final checkpoint, any fix needs Repair and the fast check on the new snapshot. Do not restart all
   checkpoints by default or silently bless changed files with old verdicts. Unclosed findings block hand-over.
7. The fast check certifies the exact files of a paste: run it right before each paste and at the freeze, alone on
   the Docker slot. Its baseline and after-run snapshots are reused while their inputs are byte-identical.
8. A changed product tool is smoke-tested end to end on a known-good package before a task uses it (the vet task 6
   package is the current one).

All review inputs include exact artifact identities and the literal contract; independent lanes do not read one
another's conclusions. Merge their finding union, not the report with the most findings. Codex runs the workflow
replica checks and solves; ad-hoc analysis (calibration comparisons, discriminator searches, verdict estimates) runs
in-process or on the second Claude account; Codex only when the owner names it or both lanes found nothing.

Review briefs carry the description verbatim. Never write "not promised", "out of scope" or "known residual" unless the
text excludes the case, never list known-and-kept items, and describe what changed, never that it resolves a finding.

Container limits come from the machine profile (machine/*.json: slots, memory, parallel workers, cleanup permission),
never from this file; run Docker work through the profile's `dockrun.py` lock with one slot for every heavy lane.
Every long job is its own tracked background command that blocks until it ends (no `&`, no detached shells), one per
lane. Stop a lane by its tracked job, never by matching a command line; on Windows that stop ends only the outer
shell: then find the processes whose command line holds that job's own unique path, `taskkill /PID <pid> /T /F` them,
and re-list. Before saying a lane is "still running", check its last file time and `docker ps`; after an interruption,
list every background lane and restart the dead ones in the same reply. Post one status line per finished step; a new
owner question is answered before any further tool call.

## Version bookkeeping (owner 2026-11-19)
- Every check result is bound to the hashes it graded (four files, title). A status line names the version
  ("Test Quality PASS on test.patch c20d13b7"); a result on an older paste says nothing about the current files.
- A test.sh change reopens Verify Tests, Verify Solution, Verify Flakiness, Reward Hacking and Test Quality. A hidden
  test change reopens Verify Tests, Verify Flakiness and Test Quality. A solution change reopens Verify Solution, Verify Flakiness, Reward Hacking, Solution Quality and Test Quality (the
  wrong versions were written against the old decisions), and locally the replay of stored runs, the timing probe and
  the reference audit. A Dockerfile change loses the re-eval of every stored run. A description change needs a fresh
  rollout. Say which checks a proposed fix reopens before the owner picks it.
- Platform check order after a paste (platform.md): prechecks and Scope Gate, Task Prompt Quality, Verify Tests,
  Verify Solution, Verify Flakiness, Reward Hacking, Category Alignment, Solution Quality, Test Quality last.

## Time boxes (owner target 3-5 h of builder time per task; the boxes are upper bounds and sum to about 6 h; platform and human waits counted apart)
0 Qualify 30 m | 0b-1 Environment 20 m + owner build | 1b Sample 15 m + owner Scope Gate | 2 Meaning 40 m, then the
length spike (two solves in parallel, 60-90 m wall; the build goes on) | 3 Lock + owner rewrite | 4 Tests 60 m |
5 Reference 60 m | 6 Executed closure 30 m (the fast check takes 12-20 m alone on the slot) | 7 One replica round 45 m
+ fix batch + verification round 30 m | 9 Freeze 20 m. An overrun triggers a progress report and a decision with the
owner, never an omitted gate or a post-lock scope cut.

## Metrics record (every task, both machines)
At hand-over write `metrics/<task>.json` in your copy of the product repo and commit it there: machine, repo, language, minutes per
stage, pastes, description changes after the lock, findings per replica round, checklist rows sharpened or added, false
alarms, false-pass escapes (found after the verification round or by the platform), platform checks passing on their
first paid run, the rollout result per family with each Orion pass's sequence length, and the length spike result.
Success criteria (baseline vet task 6, 2026-11-13 to 2026-11-21):
| Measure | vet task 6 | Target |
|---|---|---|
| Pastes before the platform checks all passed | 40+ versions | <= 3 |
| Platform quality checks passing on their first paid run | several rounds each | all |
| Description changes after the lock | 4 (owner) | 0 |
| False-pass escapes | 0 | 0 |
| Passing Orion run sequence length | 330K (one run of 8) | >= 300K, designed at stage 0 |
| Total local time | weeks | <= 5 h |
A missed target names the stage that failed; that stage's card is fixed before the next task.

## Pre-paste gate (owner rules 2026-11-17/18; every paste, every version)
Run these on the exact files before any paste or hand-over, even when the owner is waiting. None of them may be
skipped on a "hurry" instruction; say which one is running instead.
1. `tools/fastcheck.sh <task> <image> <tag>` VERDICT PASS: it holds the four cells with T1 per leaf, the two-user
   replay with the JUnit set check, every kept wrong version, lint and the clean-repository run.
2. Mutant sweep over the reference's changed lines (`tools/mutants.py`, one pass with and one without the coverage
   filter): every survivor is triaged by execution (a test when it breaks a stated rule, a repository contract or the
   behaviour before the change; a recorded reason otherwise; "defensive" is not a class).
3. Default-path timing: base vs reference at 1x and 2x input, best of 3, alone on the slot; no superlinear growth and
   no more than about 5% added time on a path that does not need the feature.
4. The hand-over states the current rollout criteria (platform.md) and the per-run fields it will read (verdict,
   compacted, sequenceLength), and lists the checks to re-run in the order of platform.md.
5. Every test added after the lock quotes, in its comment, the sentence or the repository line it checks; a cell
   removed for a rollout lists the code path it leaves untested, with the owner's yes (near-miss-release.md).
6. Walk [recheck.md](recheck.md), the finding types the platform has raised, with an executed proof per row; a row
   without a run is open.
