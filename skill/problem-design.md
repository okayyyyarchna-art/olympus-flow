# Problem design: what to give the platform agents

Evidence: platform runs and Auto Review notes on 15 tasks and our 16-task history (olympus-product/history and
analysis-20261112), and vet task 6 (2026-11-13 to 2026-11-21: 10 hosted Orion runs with trajectories, 54 rollouts in
all, every platform check several times).

## 1. What the platform agents do today (2026-11)
- **Orion** is the Codex CLI on GPT Sol 6.1 at xhigh effort (a hosted build older than the current CLI; it compacts
  at about 244K of input and reasons 2-3x less per request than a local xhigh run). Its loop: trace, write its own
  regression tests from its reading of each sentence, fix, run the repository gate (`make check`), stop when green.
  Nothing it runs corrects a narrow reading: a case it did not think of never fails for it. It reads a sentence by its
  nearest noun ("every lockfile ... paired with the manifest file" became a table of file names). It never re-reads
  the description after planning. vet task 6 runs: 100-145 requests, 25-31 minutes, 75-79% of the context on reading
  and searching, 15% edits, 6% build and test output; first repository gate at 146-175K; last edit at 211-244K;
  sequence lengths 215K-238K without compaction and 297K / 330K with one.
- **Vega** is Claude Code on Claude Opus 5.5 (a much larger window: vet task 6 runs of 377K and 453K with no
  compaction). It implements what is named and misses what is only implied; weakest on caller context and on the
  base or previous side of a comparison.
- **Nova** is the Gemini CLI (its model is read from the first run of a rollout; it changed twice in October and
  November). Nova must stay at 0 passes: it copies the nearest idiom most often and takes defensible alternative
  readings, so a Nova-only separator is fragile.
- All families build the main feature almost every time. Failing runs are near-complete (57-60 of 61 tests, 113 of
  120); the verdict is almost always `FAIL_MISSED_REQUIREMENT`. They fail on **stated boundaries where two subsystems
  meet**. Every accepted task's Auto Review lists 2-4 of them:

| Task | Platform status | Boundaries the failing runs missed (all stated or repo-discoverable) |
|---|---|---|
| commits vs buffered changelog (producer flush) | ACCEPTED, Orion 1/6 | caller-facing future vs the Kafka delivery future; snapshot owned by each flush; shutdown with a send in flight |
| EOS offsets | ACCEPTED, Orion 1/4 | persistence tied to the exact producer transaction, not the aggregate commit; standby vs active; retained transaction across rebalance |
| table visibility | ACCEPTED, Vega 1/4 | assignment vs recovery readiness; ownership re-check during paused iteration; in-flight agent after ownership loss |
| standby promotion | ACCEPTED, Vega 1/5 | progress counted across all tables; custom changelog topics; SetTable storage wrapper |
| docker proxy (oss-rebuild) | ACCEPTED, Orion 1/8 | a parent directory's own change vs descendant changes; alias vs physical file; a deletion remembered after reappearing |
| windows expiry | ACCEPTED, Orion 2/8 (older gate) | wait for an in-flight callback before flow control stops; superseded recovery; zero/falsy values |
| sqlite store | ACCEPTED, Orion 1/9 | ownership-epoch fencing for deferred commits; queued events for excluded standbys; stale rebalance cleanup |
| live readers | ACCEPTED, Vega 1/6 | pause ownership during rebalance; late/restarted isolated agents; final reader removal; supervised restart |
| topic start_from | in review (approved 3/3/3) | datetime -> Kafka millisecond lower bound; whole app fails on a late conflicting reader; reapply on reassignment |
| conditional writes (swift) | in review | retry of a completed multipart upload; return 412 only after rollback; check-then-write race |
| NOT IN views (turso) | in review | INTEGER vs REAL through UNION dedup; `NOT (x IN ...)` as an equivalent form |
| folder history (elio) | in review | live duplicate-finder selection; moves completed before a paste is cancelled; moved current/in-flight directory |
| pull-request scan accuracy (vet 6) | rollout in progress | a mechanism mirrored with its own limit (two link budgets); a kept copy next to a removed one; the saved report read back per manifest |

- Under the current criteria (platform.md) Orion must pass 1 of 4 AND its passing run must average 256K+ tokens;
  every Orion pass of our earlier tasks was 106K-190K and would fail that bar. Tasks with 0 passes in every family
  (group-table writes: Orion 0/11, Vega 0/8) fail the gate even with fair tests.

## 2. The difficulty model and the length model (use both to size every task)
**Difficulty: 1-2 hard points, each one deep rule an oracle can check** (owner rule; every accepted task had one:
"closed once", "same as RocksDB", "412 leaves nothing", "the standby with the most changes"). Many independent traps
stalled every time (orange-orm 80 wips, task 5 ~30, Burrow #751, goka 0/23). A deep rule is hard because it has
**stated consequences where it meets other subsystems**: 1-2 hard points -> 3-4 stated consequences in total, all
written in the description and each with a test. Never add unrelated traps to raise difficulty. Two moderate hard
points are preferred over one extreme point (owner 2026-11-09, a suggestion and never a gate).
Rough sizing: if an agent gets each stated consequence right with probability p and there are k of them, pass rate
~= p^k (core assumed solved). p ~= 0.6-0.75 today; k = 3-4 gives 13-42%; target Orion near 25% per run.
| p \ k | 3 | 4 |
|---|---|---|
| 0.60 | 22% | 13% |
| 0.70 | 34% | 24% |
| 0.80 | 51% | 41% |
As agents improve, deepen the SAME rule (one more stated consequence of it), never add a second unrelated trap.
Consequences must sit on different subsystem pairs, or they collapse into one blind spot.

**Length: the passing Orion run must compact once (256K), and we design for 300K+.** Measured facts (vet task 6, the
owner's notes on an accepted task):
- Sequence length is the sum over context windows of the window's peak of input + output tokens (the platform's
  rule `window_peaks_2026_11b`; `tools/seqlen.py` matches its field). The hosted window 1 peaks at about 244.6K,
  window 2 restarts at 12-14K and adds 40-90K: a run that compacts lands at 290-330K; a run that stops before
  compacting stays under 250K. The local GPT Sol 6.1 stand-in has a 475K window, so it reaches 300K without
  compacting: the local gate is the length, not the compaction.
- Runs make 100-200 requests at about 1.4-1.7K of context each; reading is 56-79% of the context, edits 15-24%,
  build and test output 4-10%, the fixed prompt about 8K.
- Attribution per requirement: a requirement that needs a code change costs a run 17-22K; one the reference already
  meets 3-7K; the deepest mechanism (links traced across the head walk, the base checkout and the cache) 38K; tests
  and builds 18%; reasoning and messages 14%.
- Width did not help: 8 rules across 27 files peaked at 205-238K in 5 of 6 runs. A hint added no length. Three runs
  stopped 25-30K short of the compaction point: the seam was one layer too shallow.
So a seam is long when the solver must read and trace a lot before its first correct edit, and when its own runs keep
showing the solution wrong, layer after layer (owner 2026-11-20: "give a difficult enough task so that the agent
first takes time to understand the problem and code ... an iterative task that requires the agent to examine its log
and its current solution, repeatedly refine the solution, and handle a substantial scope"). The three tests at the
seam pick (hunt.md step 6b):
1. **Reading before the first edit:** the chain of files a solver must open to know where the value is computed, kept
   and read again (80+ files across 3+ packages, or several large files traced end to end), as a file:line trace.
2. **Iteration loop:** which command, test or saved file of the repository keeps failing until the design is right
   (the repository gate, a round trip through a saved form, a second entry path that disagrees), so the agent reads
   output and refines instead of stopping when its own tests are green. A seam where nothing the agent can run shows
   it is wrong is one pass (vet 6: 63 calls, 32 minutes, 33 hidden leaves missed).
3. **Scope:** about 15-20 files changed in the reference, several execution paths that must agree, on one mechanism.
Estimate = 8K + 20K per code-changing requirement + 18% + 15%; under 250K at the pick is a drop or a deepening. The
estimate is confirmed by the stage-2 length spike (difficulty.md section 2) before the lock; nothing after the lock
adds length except an owner-decided description change with a fresh rollout.

## 3. Boundary types that work (stated, testable, cross-subsystem)
- Lifecycle with work in flight: stop/rebalance/revoke/reload while a callback, send, or iteration is running.
- Identity vs proxy: the caller's handle vs the real completion (delivery future, transaction, physical file vs alias).
- Ownership vs assignment vs readiness: who may read/write at a given moment, standby vs active.
- Exact conversions and comparisons: units (ms vs datetime), inclusive/exclusive bounds, type affinity, collation,
  equivalent syntax forms.
- Ordering of effects: rollback before reply, delete before close, durable before acknowledge.
- Scope of failure: one request vs the whole app; one object per write in a multi-object request.
- Memory of past events: a deletion remembered after the item reappears; a superseded operation must not apply.
- A mechanism that must agree with an existing one (a base walk next to the head walk): consume its decisions; a
  mirror with its own limit or order diverges, and agents build the mirror almost every time (vet 6: 4 of 6 runs).
- Discoverable repo conventions: response envelope, existing store contracts, typed declarations.

## 4. Boundary types that fail (each cost us)
- Undiscoverable corners (no agent can know): 0/33 on task 12 until cut.
- Races that need injected timing (a write between two lookups, a slow broker during recovery): blocked 22/22 runs and
  discriminated nothing.
- "Keep behaving as today" for a list of shapes nobody measured on base: platform Highs class after class.
- Mode coverage the reference does not really have (every driver, every table kind): SQ FAIL per mode.
- Long unbounded lifecycle contracts ("sets equal all accepted changes after any restart, rebalance, crash"): 30-61
  wips each; elio halted after 54.
- A sentence over an open input space with no boundary ("if a manifest file is followed via a symbolic link"): every
  shape becomes a requirement; vet 6 spent ten rounds and two platform SQ failures on links before the owner's one
  change named the boundary (description.md R12).
- Hidden size caps or fixed limits inside a promise: the passer with a 256 MiB cap became a tests High.
- Crafted test cells no sentence reaches (a 300-link chain, a folder named like a manifest file): they separate
  nothing but the reference's own variant and come back as Test Quality holes when removed.

## 5. Seam shapes that produced accepted tasks (ACCEPTED first; in review marked)
- A per-entity option threaded through API -> config -> runtime (topic start_from, in review).
- A guarantee broken at one lifecycle edge (commits vs buffered records; window expiry after recovery).
- A selection rule that ignores a better signal (standby promotion by progress).
- A visibility/ownership rule after rebalance (table visibility).
- A protocol rule not honoured on every route (docker proxy writes, ACCEPTED; conditional writes, in review).
- A query form not supported in an incremental engine (NOT IN in materialized views, in review).
- Path tracking after rename/move (folder history, in review).
- A comparison against a second source of truth (the base side of a pull-request scan) that must agree with the
  existing walk (vet 6, in rollout): the shape that produced the one 330K Orion pass.
Common: one clear feature or bug, a real repository subsystem on each side of every boundary. Earlier accepted tasks
touched 2-4 production files and their Orion passes were 106-190K; the current criteria need the 3-30 file range with
the reading chain of section 2.

## 6. Size
Rough guide at stage 0 only, never a target: a reference of about 150-500 changed production lines over 3-30 files, about
15-20 of them changed in a deep seam. The solution is whatever the sentences need, every hunk mapped to a sentence.
Tests 30-60 leaves (scenarios inside one leaf when the parts would pass on the clean repository); 6-15
platform-extracted requirements from <= 8 wanted outcomes in the text (hard limit 9 units). Length follows the
reading chain and the iteration loop of section 2, not the line count: a small reference is no reason to widen a task,
and a wide reference is no proof of length.

## 7. Stage 0 checklist
1. `base/` = pristine worktree at the upstream tip of the default branch (a base behind the tip fails the Harbor
   rebuild check); `repo/` = working worktree at the same commit.
2. Novelty, 3 searches: issues + PRs in every state for the feature words; `git log -S` for the key symbol; our
   `$OLYMPUS_SHARED_ROOT/already_built_locally.md` and `olympus problems mine`. Any implementation, a declined issue or a
   README "not supported" note -> pick another seam.
3. Fit: stateful framework code; 3-30 production files along the value's real path (files a correct change must
   touch, never padding); core outcome assertable offline through real objects; 1-2 hard points (one deep rule each)
   whose stated consequences sit on different subsystem pairs; no "consistent across every lifecycle event" contract.
3b. Depth, no repo hint, more than one fair design (drop the seam if any fails):
   - Depth: the solution is not visible from the surface. Grep the symptom words and the requirement's words: the
     files they land on, the symptom site and the nearest helper must not decide the outcome; the solver has to trace
     the value through other subsystems (where it is computed, kept and read again) before the fix is clear. Record
     that trace as a file:line chain in the seam entry.
   - No repo hint: no TODO/FIXME, comment, doc or README line, issue or PR text, commented-out code, test name or
     existing helper states or already computes the fix. Fairness still holds: the required behaviour follows from
     the description plus the repo's public contracts; only the route to it stays off the surface.
   - More than one fair design: at least two materially different correct implementations exist (fix at the source
     or at the reader, a kept value or a recomputation). A seam that only one exact edit can pass is dropped; the
     second design becomes the stage-4 valid-alternative variant (build-checklist.md section 4).
3c. Length design (section 2, hunt.md step 6b): the reading chain, the iteration loop, the scope, the estimate; under
   250K is a drop or a deepening before the pick.
3d. Test-grid budget (hunt.md step 6c): decision points and universal-word cells within what 30-60 leaves and one
   kept wrong version per decision can cover; otherwise narrow the seam or the word before the lock.
4. Every task, also on a repo that already has a task: the sample and Scope Gate of PIPELINE.md stage 1b (the
   builder's draft words + basic real tests + a small solution sketch, before stage 2; platform.md has the details);
   a stub test patch fails the "good quality" precheck, which locks the Scope Gate. Never run DQ or Task Quality on a
   stub-patch sample: they grade whatever test.patch is pasted.
