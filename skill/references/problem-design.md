# Problem design: what to give the platform agents

Evidence: platform runs and Auto Review notes on 15 tasks (workflow-build-20261105/platform-agents.md) and our 16-task
history (MAP.md).

## 1. What the platform agents do today (2026-11)
- They build the main feature almost every time. Failing runs are near-complete: 57-60 of 61 tests, 19 of 20, 7-8 of
  10, 32 of 34. The verdict is almost always `FAIL_MISSED_REQUIREMENT`.
- They fail on **stated boundaries where two subsystems meet**. Every accepted task's Auto Review lists 2-4 of them:

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

- Nova runs are long (avg 0.4-2.2M tokens) and almost never pass; the gate needs Nova > 400K average, which real depth
  gives for free. Orion and Vega are the families that land at 1/4.
- Tasks with 0 passes in every family (group-table writes: Orion 0/11, Vega 0/8) fail the gate even with fair
  tests: their boundaries all hit the same blind spot (assuming a failed local write did not change storage).

## 2. The difficulty model (use it to size every task)
**Shape: 1-2 hard points, each one deep rule an oracle can check** (user rule; every accepted task on both machines
had one: "closed once", "same as RocksDB", "412 leaves nothing", "the standby with the most changes"). Many
independent traps stalled every time (orange-orm 80 wips, task 5 ~30, Burrow #751, goka 0/23).
A deep rule is hard because it has **stated consequences where it meets other subsystems**: the 2-4 boundaries the
failing runs missed in the table above all come from ONE rule (topic start: one start_from rule -> ms lower bound,
whole-app failure, reassignment). So: 1-2 hard points -> 3-4 stated consequences in total, all written in the
description and each with a test. Never add unrelated traps to raise difficulty.
Rough sizing: if an agent gets each stated consequence right with probability p and there are k of them, pass rate
~= p^k (core assumed solved). Today p ~= 0.6-0.75 (failing runs miss 1-2 of 3-4); k = 3-4 gives 13-42%; target one
family near 25% per run.
| p \ k | 3 | 4 |
|---|---|---|
| 0.60 | 22% | 13% |
| 0.70 | 34% | 24% |
| 0.80 | 51% | 41% |
As agents improve (p -> 0.8), deepen the SAME rule (one more stated consequence of it), never add a second unrelated
trap. Consequences must sit on different subsystem pairs, or they collapse into one blind spot (goka: all on "a
failed local write did not change storage", 0/23). Families differ per consequence type (Orion: precise
conversions, explicit API edges; Vega: ownership/visibility state); you cannot pick the family reliably.

## 3. Boundary types that work (stated, testable, cross-subsystem)
- Lifecycle with work in flight: stop/rebalance/revoke/reload while a callback, send, or iteration is running.
- Identity vs proxy: the caller's handle vs the real completion (delivery future, transaction, physical file vs alias).
- Ownership vs assignment vs readiness: who may read/write at a given moment, standby vs active.
- Exact conversions and comparisons: units (ms vs datetime), inclusive/exclusive bounds, type affinity, collation,
  equivalent syntax forms.
- Ordering of effects: rollback before reply, delete before close, durable before acknowledge.
- Scope of failure: one request vs the whole app; one object per write in a multi-object request.
- Memory of past events: a deletion remembered after the item reappears; a superseded operation must not apply.
- Discoverable repo conventions: response envelope, existing store contracts, typed declarations.

## 4. Boundary types that fail (each cost us)
- Undiscoverable corners (no agent can know): 0/33 on task 12 until cut.
- Races that need injected timing (a write between two lookups, a slow broker during recovery): blocked 22/22 runs and
  discriminated nothing.
- "Keep behaving as today" for a list of shapes nobody measured on base: platform Highs class after class.
- Mode coverage the reference does not really have (every driver, every table kind): SQ FAIL per mode.
- Long unbounded lifecycle contracts ("sets equal all accepted changes after any restart, rebalance, crash"): 30-61
  wips each; elio halted after 54.
- Hidden size caps or fixed limits inside a promise: the passer with a 256 MiB cap became a tests High.

## 5. Seam shapes that produced accepted tasks (ACCEPTED first; in review marked)
- A per-entity option threaded through API -> config -> runtime (topic start_from, in review).
- A guarantee broken at one lifecycle edge (commits vs buffered records; window expiry after recovery).
- A selection rule that ignores a better signal (standby promotion by progress).
- A visibility/ownership rule after rebalance (table visibility).
- A protocol rule not honoured on every route (docker proxy writes, ACCEPTED; conditional writes, in review).
- A query form not supported in an incremental engine (NOT IN in materialized views, in review).
- Path tracking after rename/move (folder history, in review).
Common: one clear feature or bug, 2-4 production files, a real repository subsystem on each side of every boundary.

## 6. Size
Rough guide at S0 only, never a target: a reference of about 150-500 changed production lines over 2-4 files. The
solution is whatever the sentences need, every hunk mapped to a sentence. Beyond that, a guide for the rest: tests 10-40 functions (parametrized cases fine); 6-15
platform-extracted requirements (verifyFairness) from <= 8 wanted outcomes in the text.

## 7. S0 checklist
1. `base/` = pristine worktree at the upstream tip of the default branch (a base behind the tip fails the Harbor
   rebuild check); `repo/` = working worktree at the same commit.
2. Novelty, 3 searches: issues + PRs in every state for the feature words; `git log -S` for the key symbol; our
   `~/OSS/shipd/already_built_locally.md` and `olympus problems mine`. Any implementation, a declined issue or a
   README "not supported" note -> pick another seam.
3. Fit: stateful framework code; 2-4 production files; core outcome assertable offline through real objects; >= 4
   1-2 hard points (one deep rule each) whose stated consequences sit on different subsystem pairs; no "consistent
   across every lifecycle event" contract.
4. Every task (user rule 2026-11-05, also on a repo that already has a task): paste a sample (locked description +
   the real test.patch + a stub solution.patch; stub tests fail the "good quality" precheck, which locks the Scope Gate) right after the S1 lock so a Scope Gate reject costs nothing; the user runs the Scope Gate. S2 starts
   only after it passes. Never run DQ or Task Quality on a stub-patch sample: they grade whatever test.patch is pasted
   (the same text failed with one test.patch and passed with the next).
