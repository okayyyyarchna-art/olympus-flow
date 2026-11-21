# Shaping the task from platform rollout results

The owner runs 2 Orion + 2 Vega on the locked text at stage 3, alongside 3 + 3 local solves (difficulty.md section 3);
v1 adds the re-eval of those four plus 2 Orion + 2 Vega + 4 Nova, so the rollout is 4-4-4 with no repeat. Any later
version is a re-eval of these stored runs, not new runs; extra runs are the owner's call, and only a description
change the owner takes (description.md section 5b) needs a fresh rollout. The builder keeps closing gaps; nothing
waits for it. The description stays locked: this file shapes tests and the reference only.

The criteria (platform.md, verbatim from the platform): with N runs per family, Orion needs at least 1 pass and at
most N/4 (1 of 4; 2 of 8), Vega at most N/4, Nova 0; the passing Orion runs must average 256K+ tokens of sequence
length; no run flags the task unfair or broken; cheat rate under 20%; no environment blocker. A passing Orion run
under 256K is a design success and a gate failure that no test change repairs (difficulty.md section 7).

Route first. Every run fails: near-miss-release.md. Too many deserved passes: prompts/calibrate-one-passer.md. The
steps below apply on either route. Once a family has one genuine pass at 4+ runs, tell the owner before topping it
up: another pass can take it past 25%; another Orion pass that is short can pull the average under 256K.

1. Pull every run read-only with `tools/pull.sh <id> <dir> --runs` (folders by run id: labels repeat across batches);
   when the CLI is unavailable the owner downloads the run zips (platform.md). `tools/rollout_report.py <runs>` prints
   per run: family, misses, verdict with its full evalResult reasoning, sequence length, compacted, requests, the
   agentBlameUnfair flag; the tests failed by two or more runs; and the criteria table. The platform junit is the
   truth for a run; a local replay can pass tests the platform failed (vet 6: a sandbox difference on link
   resolution), so report replay-vs-platform differences per test and never count a replay as the platform result.
   On a Fair-task or environment-blocker failure read the notes before changing anything: notes that carry no blame
   (Git shim, lint, module cache) are no reason to touch the Dockerfile, which would lose the re-eval.
   Then, before any lever: run every calibration reserve probe (difficulty.md section 6) on every passer and record
   the split in the ledger; add what the runs show to profiles.md sections 2-3; record the hosted fingerprint
   (`tools/scout/stage_a.py`) so a model or harness change shows at once.
2. Add every patch to the permanent false-pass corpus (replayed after every later fix).
   A replay runs only the delta: per patch, the scenarios whose test files changed since
   that run plus the scenario it failed (the runner stops at its first failing assertion,
   so later lines in it never ran). Unchanged scenarios it passed keep the platform result.
   The build, not the tests, is the slow part (vet: 2-3 min per patch), so plan slots:
   a patch whose first failing line comes before every changed line needs no replay, and
   a replay that no longer answers an open question is stopped at once (TaskStop and
   remove its container), never left holding a slot. `tools/lib/replay_plan.py <old test.patch> <new test.patch>
   <runs-dir> --stage <dir>` marks each run SKIP / LINE? / REPLAY and stages only the REPLAY patches for
   replay_patches.sh.
3. Classify each run: deserved pass, false pass, near miss (fails only a few related
   assertions), environment/harness failure, genuine miss; note each run's length next to its class.
4. Levers in priority order; use the next only when the one before cannot apply:
   1. Harness or environment defect (a valid design failed for a reason outside the
      contract): repair the harness and re-classify.
   2. Every passing run: one false-pass audit (a second only when the first says
      NOT_DESERVED or is unclear), its probes replayed on the reference too. For every probe that separates the
      passer from the reference, write three columns before any verdict: the description sentence; the behaviour
      before the change on that input (run or read the base code); the origin of the reference's rule (a platform
      finding, a stated sentence, or our own review round). A rule that is ours alone, unstated and untested is an
      alignment candidate for the owner (vet 6: the reference's dev-mark rule was our own addition; upstream and the
      passer agreed); a rule the platform asked for or a sentence states is not. Reproduce each NOT_DESERVED in a
      container; a confirmed false pass gets the smallest fair test (gates.md Repair).
   3. A near miss that fails an assertion pinning unstated behaviour: fix the unfair
      assertion (never remove the promise). Unstated means no sentence covers the case.
      A case a sentence covers literally (the general rule applies and no exception
      sentence does) is stated even when no sentence names it, above all when the repo
      documents that input (a comment, a type, a fixture). Loosening such an assertion,
      or changing the reference to match the run, releases a false pass: both false-pass
      auditors run on the candidate before any re-eval is planned. A removed cell leaves its code path untested:
      replace it with a case the near miss passes and the natural wrong design fails (near-miss-release.md), or show
      the owner the hole before the paste.
   4. Too easy with deserved passes: add a grounded discriminator for an unnamed variant
      of a stated rule (tests.md T2). Full procedure: prompts/calibrate-one-passer.md.
      Grading an upstream test that only a non-required design breaks is a fair lever (a run that edited it counts as a
      failure, PASS_CHEATED). Never grade a test every correct solution must edit.
   5. Too hard with valid near misses: ask the owner for more runs on unchanged files before any change.
   6. A proven ambiguity (runs of two or more families take one other reading that the words
      allow), too easy after levers 1-4, or a passing Orion run that is too short: stay in tests and the reference
      where they can absorb it. The builder does not propose a description change. If the owner asks for one
      (description.md section 5b): report which runs it would change, whether tests or the reference could absorb it,
      whether the wording names a case the runs are failing, and what it adds to the reading chain; then build it once
      from all the evidence, and run a fresh rollout. A hint for a wall case (every run of every rollout fails it) is
      written plainly in the owner's words; a subtle qualifier is skimmed.
5. Every change goes through gates.md Repair; target: the criteria above with no false pass. Before a re-eval paste:
   - Tests a judge can follow: build-checklist.md, the "second reading" row.
   - Only-failure check (a warning, not a stop): from the replay, list the runs whose only failures are contested
     tests. Give each a failure on a plainly stated case where one honestly exists, and tell the owner about the rest.
   - **Re-eval readiness (all yes before the paste):**
     1. every stored patch replayed on the new files (replay_plan.py), giving the exact predicted result per family,
        with each predicted Orion pass's sequence length;
     2. every new test passes the fairness replica, and each assertion on an implied case carries its sentence
        words, repo file:line and reason (build-checklist.md, the second-reading row);
     3. every predicted new failure fails on a stated sentence or a cited repo line, so a Fair-task judge blames the
        agent, not the task;
     4. the FP audit has run on every predicted passer (each probe replayed on the reference too);
     4b. one replica round on the changed files, once (never a loop): fairness and Auto Review T1-T8 when tests
        changed, SQ when the reference changed; DQ only if the text changed (it cannot after the lock);
     5. no single assertion carries the band (difficulty.md section 7), or the owner was told;
     6. no Dockerfile or description change; the fast check passes on the exact files;
     7. pass counts per family come from the view JSON, infrastructure replacements included.
   - Order for the owner: the checks the change reopens, in platform.md's order (Test Quality last), then the
     re-eval, then the FP checks; Auto Review is advisory and reports no eligible runs before the re-eval.
   - On whether a failure is blamed on the task, the per-run verdict replica outranks the Test Quality replica (vet
     task 2: platform fairness said fair while 5 of 7 runs failing one test were blamed on the task).
6. A task is never retired (owner rule): the flow ends only with an accepted task. When
   no lever above applies, name the one blocker (the assertion most runs fail first and
   the shared design mistake behind it, or the missing layer behind short runs), predict the smallest redesign that
   clears it, and give it to the owner for approval.
