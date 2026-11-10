# Shaping the task from platform rollout results

The owner runs a calibration rollout of their choice on v1 (usually 3 Orion + 3 Vega) and
later tops up to 4+ runs per family. The builder keeps closing gaps; nothing waits for it.
The description stays locked: this file shapes tests and the reference only.

Route first. Every run fails: near-miss-release.md. Too many deserved passes: prompts/calibrate-one-passer.md. The steps
below apply on either route.
Once a family has one genuine pass at 4+ runs, tell the owner before topping it up: another pass can take it past 25%.

1. Pull every run read-only with `tools/pull.sh <id> <dir> --runs` (folders by run id: labels repeat across batches).
   Record per run: family,
   eligibility (complete, clean, current version), per-test result vector, patch, the verdict label with its full
   evalResult reasoning, and the agentBlameUnfair flag. On a Fair task or environment-blocker failure read these before
   changing anything: notes that carry no blame (vet task 2: Git shim, lint and module cache on nearly every run) are
   no reason to touch the Dockerfile, which would lose the re-eval.
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
   assertions), environment/harness failure, genuine miss.
4. Levers in priority order; use the next only when the one before cannot apply:
   1. Harness or environment defect (a valid design failed for a reason outside the
      contract): repair the harness and re-classify.
   2. Every passing run: one false-pass audit (a second only when the first says
      NOT_DESERVED or is unclear), its probes replayed on the reference too; reproduce each
      NOT_DESERVED in a container; a confirmed false pass gets the smallest fair test
      (gates.md Repair).
   3. A near miss that fails an assertion pinning unstated behaviour: fix the unfair
      assertion (never remove the promise). Unstated means no sentence covers the case.
      A case a sentence covers literally (the general rule applies and no exception
      sentence does) is stated even when no sentence names it, above all when the repo
      documents that input (a comment, a type, a fixture). Loosening such an assertion,
      or changing the reference to match the run, releases a false pass: both false-pass
      auditors run on the candidate before any re-eval is planned.
   4. Too easy with deserved passes: add a grounded discriminator for an unnamed variant
      of a stated rule (tests.md T2). Full procedure: prompts/calibrate-one-passer.md.
      Grading an upstream test that only a non-required design breaks is a fair lever (a run that edited it counts as a
      failure, PASS_CHEATED). Never grade a test every correct solution must edit.
   5. Too hard with valid near misses: more runs on unchanged files before any change.
   6. A proven ambiguity (runs of two or more families take one other reading that the words
      allow) or too easy after levers 1-4: stay in tests and the reference. The builder does
      not propose a description change. If the owner asks for one (description.md section 5b):
      report which runs it would change, whether tests or the reference could absorb it (vet
      stayed on an imperfect text because they could) and whether the wording names a case the
      runs are failing; then build it once from all the evidence, and run a fresh rollout.
5. Every change goes through gates.md Repair; target: one family in (0, 25%], the
   others at 0, with no false pass. Before a re-eval paste:
   - Tests a judge can follow: build-checklist.md, the "second reading" row.
   - Only-failure check (a warning, not a stop): from the replay, list the runs whose only failures are contested
     tests. Give each a failure on a plainly stated case where one honestly exists, and tell the owner about the rest.
   - Order for the owner: Test Quality, re-eval, Auto Review (before the re-eval it only reports no eligible runs),
     FP panel.
   - On whether a failure is blamed on the task, the per-run verdict replica outranks the Test Quality replica (vet
     task 2: platform fairness said fair while 5 of 7 runs failing one test were blamed on the task).
6. A task is never retired (owner rule): the flow ends only with an accepted task. When
   no lever above applies, name the one blocker (the assertion most runs fail first and
   the shared design mistake behind it), predict the smallest redesign that clears it,
   and give it to the owner for approval.
