# Handover: what to change in the Olympus task workflow (state of 2026-11-20)

You build coding tasks for the Olympus platform with the `olympus-flow` workflow (find a repository and a seam, write
the description, hidden tests, test.sh, reference solution and Dockerfile, prove them, hand the package over, shape the
task from the rollout). Another machine has spent several weeks on one hard task (safedep/vet, "pull request scan
accuracy", called vet 6 below) and has paid for most of what is written here with failed platform rounds.

Your job with this document: update your copy of the workflow so the next task does not repeat those rounds. Do not
rebuild vet 6. For each numbered section, find the matching card in your workflow (named in brackets), merge the rules
in, and keep them as standing rules. If you have no such card, create it from the text here. Section 12 lists changes
that are decided but not yet written into any card: do those first. Appendix A (sent with this file) holds the scripts.

Everything here was measured on real platform results unless a line says "one task of evidence" or "inference".

## 1. Platform facts that changed

**Rollout gates (since 2026-11-17).** At least 4 completed runs per agent family, and:
- Nova: 0 passes.
- Orion: at least one pass and at most 25%. With 4 runs that is exactly 1 pass.
- Vega: at most 25%; 0 is fine.
- Orion's passing runs average at least 256K tokens of sequence length.
- No run flags the task unfair or broken, at least one solve, cheat rate under 20%, no environment or verifier blocker.

The old target ("exactly one family passes, the others zero") is gone. Target Orion, never a Vega-only pass.

**Agents.** Orion = Codex CLI on GPT Sol 6.1 at xhigh effort. Vega = Claude Code on Claude Opus 5.5. Nova = Gemini
CLI. Read the model names from the newest run after every rollout; they have changed without notice before.

**Sequence length** is the sum of each context window's peak. In an accepted task, window 1 peaked at about 247-250K,
compaction came at about 245K, window 2 added 41-67K. So "256K" means "the passing Orion run compacted once". A run that
finishes before compacting stays under about 250K however good it is. Only passing Orion runs count, so long failed
runs do not help. In every older task of ours Orion's passes were 106K-190K: none would meet the bar.

**Quality checks.** Seven: verifyTests, verifySolution, verifyFairness (Test Quality), solutionQuality,
descriptionQuality (Task Prompt Quality), categoryAlignment, rewardHacking. Auto Review is no longer a readiness item.
Each paid round samples a new reviewer, so a pass is a sample, not a proof: vet 6 passed Test Quality once while 62 of
64 scripted wrong solutions still passed its tests.

**Order after a paste.** Prechecks and Scope Gate, Task Prompt Quality, Verify Tests, Verify Solution, Verify
Flakiness, Reward Hacking, Solution Quality, Test Quality last. Any test.patch edit makes the earlier results stale.
The owner runs every check and every rollout; the builder only prepares files and reads results. Never paste while a
platform run is active, and read every result against the file hashes it graded.

## 2. How each reviewer judges [platform.md, replicas/]

**Test Quality (verifyFairness).** It runs the hidden tests without the solution, reads the description and the
repository, infers the solution's shape, writes realistic wrong solutions, and blocks on two things only:
- a gap: a wrong solution passes every test;
- an unfair test: a correct solution fails one.

A wrong solution counts as wrong by any of three sources: the description, the behaviour before the change on that
input, or a contract the repository documents (comments, upstream tests, the sibling mechanism the new code mirrors).
Its wrong solutions are plausible from-scratch designs that drop one property. It is not a stronger model than ours;
it needs one real defect from the pool of wrong solutions that still pass. Code quality notes on the tests are not
blocking.

**Solution Quality.** It builds a concrete input repository, runs the tool, and blocks on a wrong output (it prints
Input, Command, Expected, Received, Why, Suggested change) or on a measured slowdown of the normal path (vet 6: a full
scan 1.34x slower on a 4000-entry lockfile, in code the full scan did not even need). Everything else is a non-blocking
note labelled Design, Clutter or Practice. Notes repeat every round until fixed or declined with a written reason. A
static review of the solution does not reproduce this check: our lanes must execute inputs.

**Verify Solution.** Root applies the tests and runs `test.sh base` on the clean repository; uid 1000 (user `model`)
applies the solution, runs `test.sh new`, then `test.sh base` again. It fails when the baseline has a failure, a new
case does not pass, a new case also exists in the baseline, the after run has a case that is neither a baseline pass
nor new nor skipped, or a baseline pass does not pass afterwards. `/app` must be writable by uid 1000
(`chmod -R a+rwX /app`), test.sh must accept `[--output_path F] <base|new>`, and it must write JUnit, not raw events.

**Verify Tests.** Every new test case must fail on the clean repository. This is per leaf: a subtest that passes on
the clean repository fails the check even when its parent fails.

**Task Prompt Quality.** It counts requirement units and runs an AI-text detector. One formal sentence flipped the
detector for the whole text, and the detector quoted old, unchanged paragraphs as the reason. Bisect by removing the
newest sentence. Text in the owner's own casual words has passed every time.

## 3. Hard rules for every hidden test [tests.md, tq-once.md, replicas/fairness.md]

1. **Fair.** For every assertion try the sentence "a correct implementation that satisfies every sentence could still
   do X, and X fails this". If you can write it, weaken the assertion, accept both values, or delete it. Never pin a
   value that common readers of the format do not tell apart (JSON integers above 2^53), a field the description does
   not name, a behaviour only because a solution review asked for it, or a count that another fair design would double.
2. **Aligned with the description, both ways.** Every test traces to a sentence or to existing behaviour at a touched
   site (cite file:line). Every sentence, split on its triggers (every, any, each, lists, "X or Y"), has tests. Nothing
   the description excludes is tested.
3. **Behavioural.** Assert what running the product produces. Where an ordinary path must agree, compare with it
   (the full scan of the same tree, the clean code on the old input, the saved report read back) instead of a typed
   literal.
4. **No API-based tests.** No call into unexported code, no hand-built internal state a real run never produces, no
   name that only the reference adds, no fake that constrains the design.
5. **Public behaviour only.** Enter through public entry points and check what a user can observe.

Hygiene the platform enforced:
- Each leaf fails on the clean repository. Re-check after every test edit: splitting a loop into subtests, or deleting
  one assertion, has left leaves that pass there. A scenario that passes on the clean repository is folded into a leaf
  led by a scenario that fails there; it is never its own subtest.
- No skips in new tests. For a user-dependent input (chmod), compare with an oracle and guard on "not root".
- No real clock, no goroutine deadlines. Operating-system limits only behind an OS check.
- A leaf with several scenarios names the scenario in every assertion message. Prefer table-driven rows.
- Hidden tests carry their own helpers and test.sh hides the package's other test files in new mode, so an agent that
  changes unexported code or edits repository tests cannot stop the hidden tests from compiling. Two rollouts were
  flagged "test broken" for exactly that. Reuse a helper from a non-test package of the repository when one exists.
- Unit tests inside solution.patch are not graded and count as no coverage.

## 4. Hard rules for the solution [solution.md, replicas/sq.md]

- Every decision point of the patch (each branch, each term of a compound condition, each list member, constant, early
  return) has a hidden test that fails when only it changes.
- For every write the solution removes or makes conditional (files, map entries, temp-tree entries), list who reads
  it and keep one executed case per reader. vet 6 was blocked because a removed temp-file write had been the thing
  another package's `Stat` call relied on. No decision point of ours looked wrong on its own.
- A second pass over the same input repeats no side effect of the first (diagnostics, counts).
- Run the same input outside the described mode; change that output only if the description asks.
- Time every per-item step added on paths that do not need the feature: clean code versus solution at 1x and 2x input,
  best of 3. Fix superlinear growth or more than about 5% added time.
- Sibling forms that the tool or the format defines are inside a universal word (a lock file built from two file
  kinds, three versions of a lockfile format).
- One logic in one place. A constant at a real limit names its source.
- Leave a platform-approved solution alone unless a finding forces a change; every change re-opens Solution Quality.

## 5. The proof before every paste [tq-once.md, gates.md]

Write three lists before the first upload and keep them current:
1. Everything the solution does: one row per decision point, each with the test that fails when only that row changes,
   plus one row per existing behaviour at each touched site.
2. Every call form the repository accepts for the named commands (flags, input forms, modes, outputs).
3. Every description sentence split on its triggers.

Then:
- **Kept wrong versions.** Each gap becomes a scripted edit of the reference (a small Python file: KIND wrong or
  control, EXPECT the test it must fail, EDITS as (path, old, new) that asserts the old text occurs exactly once).
  First prove the current tests pass it (else the finding is stale). After the fix, re-run all kept versions on every
  final suite: each wrong one fails its named test, each control passes. A kept script whose edit no longer applies
  must fail the step.
- **Variant sweep.** Over the changed lines the tests run: negate each condition, drop each operand, delete each
  assignment. Every survivor is closed either with a test or with a written reason. Parking a survivor is not closure:
  two platform blockers were survivors the sweep had flagged and the builder had set aside.
- **Field-list sweep (new).** For every function that compares or copies a list of fields, one wrong version per
  field. vet 6: a 12-field comparison had tests for 5 fields; the platform found the sixth.
- **Unchanged-change sweep (new).** For each input shape of the touched axis, make a change that edits only an
  unrelated file and require "nothing changed" in the output. Run it on the clean tool and on the solution, and
  compare. A regression against upstream at a touched site is blocking every time.
- **Reserve rows on real agent solutions.** For each open wrong version write one behavioural row, then run every row
  on the reference, its wrong version, the clean repository and each stored agent solution. Add rows that the strong
  runs pass; fold a row that passes on the clean repository into a failing leaf. vet 6 closed 24 of 37 open versions
  this way at no cost to the Orion runs.
- **Probe before writing.** Run candidate rows on the clean repository and the reference first. It shows which rows
  may be subtests and exposes fixture mistakes before they reach the package.
- **Fix the whole class.** A platform item is reproduced first, then every sibling is swept (the other member of the
  pair, the other error kind, the flag's other state) and fixed in the same round.

## 6. Fast hand-over check [new card; scripts in Appendix A]

The full hand-over proof took an hour because the full suite ran seven times, mostly in parallel on a small Docker VM.
Run each check only when its inputs changed:
- Three fingerprints: test.sh, the hidden test files, the solution patch.
- Root's baseline run on the clean repository depends on test.sh alone (base mode runs no added test file). Run it
  once per test.sh and commit the container as a snapshot image; keep its JUnit file.
- The after run (uid 1000, solution, base mode) is saved per test.sh + solution and reused.
- Every run: new mode with the solution as uid 1000 and as a user id with no account; every leaf fails on the clean
  repository with none skipped; format, vet, lint on changed files; kept wrong versions, each running only the test it
  names; then the Verify Solution set check over the three JUnit files.
- The cold two-user replay is repeated only when test.sh changes. Say in the hand-over which parts were reused.
- One heavy container at a time. Contention, not the suite, made the runs slow (5 minutes alone, 20+ shared).
- Compare builds of a command-line tool with a separate HOME and state folder per binary: a shared cache made a
  correct fix look broken.

Measured: 6 to 14 minutes per run instead of about an hour, with the same verdict inputs.

## 7. Description [description.md]

- The description is locked once; the owner writes the final words. The builder never proposes a change after the
  lock. If the owner asks for one, report first: which runs it would change, whether tests or the solution could absorb
  it instead, and whether the wording names a case the runs fail. Then do it once, with a fresh rollout.
- Requirements only, no hints. Deletion test: delete the sentence; if the rest plus a repository line still decides
  the outcome, the sentence is a hint.
- At most 9 requirement units (target 5 to 8). An "even when" clause counts.
- Word reach before the lock: grep the repository for each key word and list every state it covers. Each covered
  state is tested or the word changes. Examples that cost rounds: "every lockfile vet reads packages from" (a lockfile
  the change empties has no packages to read, yet reviewers hold it in scope); "empty" also reaches a zero-byte file
  the parser rejects.
- **Estimate the grid before the lock (new).** Count the decision points of the planned change and the cells each
  universal word opens (axis members times conditions). vet 6 had about 300 decision points in 27 files and universal
  words over 16 finding families, 16 outputs and 21 lockfile names: 20+ fix rounds, each one a new cell. Above a
  budget, narrow the seam or the word before locking.

## 8. Difficulty and the length gate [hunt.md, difficulty.md, problem-design.md]

- Sequence length comes from depth, not width. Listing more rules widened vet 6 and did not make the agent work
  longer: a stand-in solve was one pass (63 calls, 32 minutes, no compaction) because no command the agent could run
  showed its solution wrong.
- Seam test: how much code must a solver read and trace before the first correct edit, and does its own feedback (a
  reproducible command, build and test output) keep failing layer after layer until the work is done?
- Good signs: the work crosses several layers, 80+ files read and about 20 changed, several execution paths that must
  agree, a suite slow enough to wait on. Warning signs: one module, a prompt that points at the fix, instant tests.
- Passing runs that compacted looked like this: 150-200 requests, compaction after 140-165 of them, about one hour,
  context growing about 1.5K per request, most of it reading code.
- Size: 3 to 30 production files on the value's real path; the answer sits away from the symptom; the repository
  itself gives no hint; at least two fair designs.

## 9. Rollout handling [rollout.md]

- Pull every run read-only; record per run the family, the per-test results, the patch, the verdict with its full
  reasoning and the blame flag, before changing anything.
- Keep every agent patch and replay it on later test versions. Grade a patch through the real test.sh.
- No test may be failed by every strong run for an unstated reason; a test that every run fails is a wall, not a
  discriminator. Check each new row against the stored runs.
- **Removing a test cell is not free (new).** vet 6 removed "emptied lockfile" rows because all four Orion runs failed
  them, and kept the code. The next Test Quality round blocked on exactly that gap. When a cell is removed, either the
  code path goes too or a test stays; otherwise show the owner the hole before the paste.
- When a gate fails on "unfair" or "environment", read each run's verdict reasoning first. Notes without the blame
  flag are no reason to touch the Dockerfile, and a Dockerfile change loses the stored runs.
- Fixes that turned "unfair" verdicts into "missed requirement" on one task (one task of evidence): neighbouring cases
  showing the rule both ways, a comment above each assertion that states the behaviour, test names that say what they
  check.
- A description change needs a fresh rollout; test and solution changes are graded on the stored runs.

## 10. Finding types the platform has raised (re-check list) [new card]

Walk this list on the final tests and solution before every paste, with an executed proof per row.

Tests:
| # | Finding type | Check |
|---|---|---|
| T1 | A wrong solution passes every test | every kept wrong version fails its named test |
| T2 | Exact value where several are right; a pinned unstated count | no leaf failed by every strong stored run |
| T3 | A state no real run builds; a call into internals | list every unexported name the hidden tests use |
| T4 | A check that is empty for root | hidden tests as root: all fail clean, all pass with the solution |
| T5 | Skips | zero skipped in every JUnit file |
| T6 | Real clock or goroutine deadline | grep sleeps, timers, deadlines |
| T7 | Operating-system limits assumed | each behind an OS check |
| T8 | Several scenarios, no name in the message; not table-driven | read every new test |
| T9 | Comments quoting the task text; copied helpers | read every new test |
| T10 | A leaf that passes on the clean repository | new mode on the clean repository: all fail |
| T11 | Hidden tests stop building after an agent's changes | every stored agent patch through test.sh new: 0 build errors |
| T12 | Flaky result | five runs across three user ids |
| T13 | Verify Solution set rules; /app not writable | the two-user run and the set check |

Solution:
| # | Finding type | Check |
|---|---|---|
| S1 | Wrong output on an input the reviewer builds | the unchanged-change sweep over every input shape |
| S2 | Regression against upstream at a touched site | the same trees on the clean tool, side by side |
| S3 | Slower normal path | best-of-3 timing at 1x and 2x input |
| S4 | One rule computed in two places | read the diff |
| S5 | Dead code, repeated literal, narrating comment | read the diff |
| S6 | An error dropped, a caller's data changed | read the diff |
| S7 | Behaviour no sentence asks for | each behaviour maps to a sentence |

## 11. Working rules that saved or cost the most time

- Validate before fixing: reproduce every platform item on the graded bytes, then fix.
- Every long job is its own tracked background job. Before saying a job is "still running", check its last output
  time and the container list; after an interruption, list the lanes and restart the dead ones in the same reply.
- Never drop a hand-over check silently; say what was run, what was reused and what was skipped.
- Every workflow change found during a task goes into the product backlog in the same reply.
- Keep a ledger per task: one row per finding (check, quote, real or misread, fix, next result).
- Give the owner options, never a bare "no"; decisions on description wording, rollouts and releases are the owner's.
- On Windows with Git Bash: write code that contains backslashes with the editor's write tool, not a shell heredoc
  (a doubled backslash became a real newline twice); keep LF line endings in scripted edits; strip `\r` from values
  Python prints; antivirus can delete test fixtures.
- Codex helper briefs use neutral words, or the provider's filter stops them.

## 12. Decided, not yet written into the workflow: do these first

1. Add the fast hand-over check (section 6, Appendix A) as a standing tool with the three fingerprints.
2. Add the unchanged-change sweep and the "who reads a removed write" list to the solution card and the Solution
   Quality replica (section 4, section 5).
3. Add the field-list sweep and the reserve-row method to the Test Quality card (section 5).
4. Make a kept wrong version whose edit no longer applies fail the step; add the reserve list to the kept step.
5. Split the kept-version step so a layout-only test change repeats new mode, the clean run and lint, not every kept
   version (it is about a third of the run time).
6. Add the "removed cell" rule to the rollout card (section 9).
7. Add the grid estimate and the depth test to the seam and description cards (sections 7 and 8).
8. Add the liveness check before any "still running" statement.
9. Add the re-check list of section 10 as a card and walk it before every paste.

## 13. Where vet 6 stands (context only, not your work)

Test Quality on the last pasted version blocked on two gaps: a change that empties a lockfile, and a saved report
that showed one integrity hash for two manifests. Both are fixed in tests only (120 hidden tests; the solution is
unchanged) and the fast check passes. Open with the owner: one small wording change to the description for the
emptied-lockfile case, which would also need a one-line solution change for a zero-byte lockfile.
