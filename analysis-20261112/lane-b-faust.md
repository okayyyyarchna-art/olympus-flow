# Lane B: faust difficulty retro (4 tasks)

Read-only retro. Sources:
- Platform data through the Olympus CLI (`runs view`, `problems view`, and `runs artifact` with evalResult, testLog and solutionPatch) for all four problems. I fetched final description, testPatch and solutionPatch from `problems view`.
- Local folders under `C:/Users/ASUS/OSS/claude-code/challenges/`. Standby has the full rollout zips in `rollouts/agent-runs-36|37|39`. Topic-start has `eval/`. Live-readers and table-visibility keep only the wip packages, because their eval folders were cleaned up.
- Memory notes, used only as background and checked against the run data.
- Base checkouts:
  - faust `3442a90f` (live-readers, standby, table-visibility), checked out as a shared clone in the scratchpad (`retro-b/base3442`).
  - faust `ca53750f` (topic-start), from `cc-faust-topic-start/dev/clean`.

All file:line references below are base-commit lines.

Platform outcome summary, from the criteria block of `runs view`:

| task | final gate | sequence length (completed runs) | solution size of the reference |
|---|---|---|---|
| live-readers | Vega 1/6, Nova 0/8, Orion 0 (not counted) | Vega 488-586K, Nova 0.79-1.39M | 19 files |
| standby-promotion | Vega 1/5, Nova 0/4, Orion 0/4 | Vega 158-231K, Nova 489-793K, Orion 97-120K | 13 files |
| table-visibility | Vega 1/4, Nova 0/4, Orion 0/4 | Vega 207-274K, Nova 515-857K, Orion 106-151K | 9 files |
| topic-start | Orion 1/4, Vega 0/4, Nova 0/4 (FP "passed with caveats") | Vega 170-254K, Nova 0.94-1.20M, Orion 104-115K | 11 files |

---

## 1. cc-faust-live-readers (kh70afkwq3q1ha6zh6j1grgy7n8gchz4, accepted)

### Q1 Hard points (final re-eval 4 of the Vega batch, wip61 tests: 55 tests x 2 conductors = 110 cases)

| run | result | missed tests (each in both [python] and [compiled]) | named / implied |
|---|---|---|---|
| Vega #1 rd7anr8rj10t (re-eval of rd7e8chhnb31) | PASS 110/110 | none | n/a |
| Vega #3 rd719zqvxr0g | 108/110 | `test_pause_and_resume_made_from_a_rebalance_handler_are_kept` | implied (the description says only "Our pauses are reset when we rebalance") |
| Vega #3 rd75rejvbqh2 | 108/110 | the same test | implied |
| Vega #2 rd773shkn9y4 | 104/110 | the handler pause; `test_backpressure_still_works_after_a_rebalance` (it resumes a revoked partition); `test_stream_stopped_while_a_processor_is_busy_does_not_stall_the_others` | handler pause and revoked resume implied; busy processor named |
| Vega #1 rd7ah3ppgr38 | 102/110 | `test_isolated_agent_started_later_gets_the_next_messages`, `test_isolated_agent_stopped_and_started_again_while_the_worker_runs` (names and pattern) | named |
| Vega #4 rd7bgy2k8jb3 | 102/110 | `test_agent_restarted_after_a_crash_keeps_its_messages`: the backlog passes; stopping after the restart hangs | crash restart named; stopping afterwards implied |
| Nova #1-#8 | 30-60+ failures each | the flow tests plus isolated, crash, pattern and handler tests | mixed |

Why the runs failed, from the evalResult reasoning:
- **Handler pause.** Both Vega #3 runs and Vega #2 classify every pause made "while `app.rebalancing` / `_in_rebalance()`" as a framework pause. A user callback on `app.on_partitions_assigned` runs inside that window, so its pause goes into the framework set and recovery releases it.
- **Isolated agents.** Vega #1 (rd7ah3pp) never seeds a late isolated agent's actors from the partitions the worker already owns (agent.py:348/365 in its patch).
- **Crash restart.** Vega #4 keeps a restarted actor's stream routed after `Agent.on_stop`.

There was no single hard point. Each Vega run missed a different corner, and five of the six missed at least one. The passer itself first failed only F6, the Forfeit give-up stall (verdict FAIL_MISSED_REQUIREMENT on 10-20). It passed after F6 was removed in wip54; this follows the memory notes, and the re-eval history confirms it.

### Q2 Obvious design vs reference
- **Routing.** The obvious design rebuilds `_tp_index` on `Conductor.add/discard` by reusing `_update_tp_index(assignment)`. It matches patterns by regex against assigned topics, and it keeps user pauses apart from internal pauses with a time-window heuristic: anything called during a rebalance counts as internal.
- **Where it diverges from the reference.** The reference, and the passer, mark ownership by caller. The passer sets a contextvar `_flow_control_pausing` at faust's own call sites (art/live-pass-sol.patch, `pause_partitions` at about line 1411). User pauses also survive revoke: the patch removes `self._paused_partitions.difference_update(revoked)`, which is consumer.py:655 at base.
- **Other corners.** The reference also seeds isolated actors from the current assignment, and it releases restarted actors' streams on stop.

### Q3 Choke points: many, no shared site
| entry point | base site |
|---|---|
| stream started late | `Conductor.add` conductor.py:451; tp index rebuilt only in `on_partitions_assigned` :387-417; the Cython twin `transport/_cython/conductor.pyx` |
| pattern stream | `_update_indices` :366-385 indexes `channel.topics` only; aiokafka subscribe has `# XXX pattern does not work :/` at aiokafka.py:779 |
| isolated agent late start or restart | `_update_tp_index` isolated branch :406-411; the agent supervisor in agents/agent.py |
| user pause | `Consumer.pause_partitions/resume_partitions` consumer.py:622-632 share `_paused_partitions` with recovery.py:316/448/475/492/544/649 and app/base.py:1735/1814; cleared on revoke and assign :655/:675 |
| fetch gating and backpressure | `_buffered_partitions` and `on_buffer_full/drop` consumer.py:547-560, :761 |
| stream stop and acks | streams.py plus `_cython/streams.pyx` |
| crash restart | agents/actor.py |

The final reference touches 19 files.

### Q4 Primitives
- **Partial primitive.** `Conductor._update_tp_index(assigned)` (conductor.py:402) computes routing for a given assignment, so late-reader routing is about one call away. Early prototypes reused it (memory notes: "A reuses B's _update_tp_index pattern branch").
- **No primitive for the hard points.** Nothing in base separates pause owners, holds a restarted actor's buffer, or gates fetching per reader. So the primitive covered the easy named corner only.

### Q5 Design spread
At least three designs sat at the pause seam:
1. The time-window heuristic: Vega #3 x2 and Vega #2.
2. The caller-identity contextvar: the passer.
3. No separation at all: most Nova runs.

Isolated seeding and restart cleanup varied independently. During calibration the cases that separated runs were F6 (the Forfeit stall; 3 of 4 Vega failed it on wip52), the handler-pause test (an FP-closer added in wip52, which killed both Vega #3 runs), and the earlier refill / names-to-pattern / crash corners. Hit rates on wip40 were 1/4, 2/4 and 3/4, from memory notes.

### Q6 Source
Mainly **multiplicity**: the description grew from 164 words (description-v1-accepted.md) to 348 words (wip61/description.md), each named corner with its own miss rate. The second source is **lifecycle/ordering**: a pause made inside the framework's rebalance window, stop after a crash restart, stop while a processor is busy. A **second code path** (Python and Cython conductor twins) added cost but did not separate runs, because both parametrizations fail together.

### Q7 Gate check
- (a) Many sites: passes.
- (b) Primitive covers only late routing: passes.
- (c) The obvious design (time-window pause ownership) fails the handler-pause and revoked-resume cases on different paths: passes.
- (d) Spread is at least 3: passes.

The stage-0 gate would have rated the seam hard enough. What it would not have caught is that it was **too broad**: 61 wips, 5 platform SQ/AR rounds, and every round found a new corner (memory olympus-task7-learnings). A breadth cap was missing (named corners x paths).

---

## 2. cc-faust-standby-promotion (kh7dvvpbmrbz4c4k3n6t1k4etn8gq1rr, accepted)

### Q1 Hard points
First rollout on wip13/15 (13 tests, `rollouts/agent-runs-36`): Vega 3/4 passed (rd79h8gzztqs, rd77svd45vx1, rd70mqg4qjnq), Nova 2/4 (rd7e7a7ddb8b, rd71c8jp8d1h), Orion 0/4. That is too easy.

Failing runs missed:

| run(s) | missed tests | named / implied | cause |
|---|---|---|---|
| Orion #1 #4 #5 #6, Nova #1 rd7bqft84nzr | `test_changes_of_a_set_table_are_counted_too`, `test_a_set_table_copy_kept_after_a_standby_was_given_up_counts_too` | implied by "Counting across all tables" | they added a new store method that the SetTable storage wrapper (objects.py) never forwards |
| Vega #4 rd746s74trb4, Nova #2 rd73d3jc0qzs, Orion #1 rd7egaj9039v | `test_changes_are_counted_over_all_tables_of_the_partition`, `test_new_standbys_go_to_the_worker_with_the_most_changes_on_disk` (both have a custom `changelog_topic=` branch, test lines 743-795) | implied by "all tables", discoverable from the repo | wrong changelog name |
| all four Orion runs (baseline) | `tests/unit/stores/test_rocksdb.py::TestRocksDBOptions::test_open_rocksdict` (base test lines 70-82) | n/a | they changed the rocksdict read-only open mode to read old copies |

The decisive case was `test_the_group_starts_after_a_deploy_left_copies_of_ten_partitions`, added in wip16 after the FP hunt found a livelock in the reference itself:
- In re-eval on wip16 (`agent-runs-37`), all 5 earlier passers fail it (Vega x3, Nova x2). They time out in the standby free-up loop. Vega #4 fails it too.
- It is not named in the description, and the description gives no hint of it. It is a termination property of base's free-up loop under the new ordering, found only by reasoning or fuzzing.
- 4 more Vega runs gave 1 pass, rd73fnv4hfr7, 14/14 (`agent-runs-39`).

### Q2 Obvious design vs reference
The obvious design has three parts:
1. Each worker reports per-partition progress in its join metadata.
2. The leader sorts promotable standbys by that progress in `_find_promotable_standby`.
3. Progress is read through the store's offset.

It diverges in three places:
- **Changelog name.** 3 of 15 stored patches built names with `table._changelog_topic_name()`, which is the repo's own idiom at partition_assignor.py:322 and tables/base.py:470-471. It ignores a custom `changelog_topic` (base.py:661-672). Every run that did this failed the custom-topic tests: grep counts gen=4/1/3 for Nova, 8 for Orion #1, 6 for Vega #4.
- **SetTable.** The progress method is not forwarded through `ChangeloggedObjectManager` (objects.py:103-109 forwards only `persisted_offset`).
- **Ordering.** The new placement order livelocks the free-up step (copartitioned_assignor.py:245-260 frees "the first full standby assignment"). Reference v6 frees a full client that holds a partition it can re-home.

### Q3 Choke points
There is one decision site and many input paths.
- **Decision.** `CopartitionedAssignor._assign_round_robin` / `_find_promotable_standby` (copartitioned_assignor.py:162-175, 189-260) covers promotion, sequential deaths, leader leaving and new standbys. Editing it gets every entry point's choice right.
- **Inputs.** The value it needs crosses about 6 hops:
  1. `PartitionAssignor.metadata` (partition_assignor.py:146)
  2. `ClientMetadata` (client_assignment.py)
  3. cluster_assignment
  4. table progress: `Collection.persisted_offset` (tables/base.py:254), the store (rocksdb.py:386-404), and the SetTable wrapper (objects.py:103)
  5. on-disk copies that are not open (`_open_for_partition` rocksdb.py:489)
  6. the changelog topic name (custom vs generated)

### Q4 Primitives
Yes, partly:
- `persisted_offset` exists on every store (stores/base.py:58, rocksdb.py:386, memory.py:72), on tables (tables/base.py:254) and on SetTable (objects.py:103).
- Recovery already tracks `standby_offsets` (recovery.py:104, 222-232).

So "progress" was precomputed, which explains Vega 3/4 and Nova 2/4 on the first rollout. Where the repo had a helper it was **misleading**: `_changelog_topic_name()` is used by the assignor itself (partition_assignor.py:322). The case that made the task hard (livelock) had no primitive.

### Q5 Design spread
Two data-gathering designs, both visible in the files changed:
- A store API layered through tables/base.py and objects.py: all Vega runs and Orion #4.
- Direct store reads inside the assignor: Nova, with no objects.py change.

Naming choice and free-up order varied independently. Calibration was separated first by SetTable and custom topic (Orion/Nova), then only by the livelock test. It killed 5/5 earlier passers; the final passer rd73fnv4 survives it ("1 hang in 3000 simulated deploys", memory note).

### Q6 Source
- **A second kind of object**: SetTable storage wrapper, custom changelog topic. Repo-discoverable, and the nearest repo pattern is wrong.
- **Lifecycle/algorithmic global property**: assignor termination on dense layouts with full standby slots.
- An Orion-only **regression** on a pinned upstream test.

### Q7 Gate check
- (a) Map of the decision site alone: one site, so red flag. That was correct, since the first rollout came out too easy. A data-path map would have shown many hops and passed.
- (b) Primitive grep: `persisted_offset` is red. Correct.
- (c) The obvious design spike (copy the repo's naming idiom, add a store method) fails custom-topic and SetTable on two paths: passes. But platform Vega did not take the obvious path (3/4 passed), so the spike **overestimated** difficulty.
- (d) Spread is at least 2: passes.

Verdict: the gate as written would have passed the seam on (c) and (d), and the first rollout would still have been too easy. The checks that would have caught it: a strong-agent spike (one real Opus solve before the build) and a termination/global-property fuzz of the obvious design. The case that made the task hard was found only after the rollout.

---

## 3. cc-faust-table-visibility (kh7bfzrhqdc4m97ez8gspb9hw98gtx2v, accepted)

### Q1 Hard points (wip24 tests: 18 functions / 48 cases; 12 runs plus re-eval 1)

| run(s) | missed | named / implied |
|---|---|---|
| Vega #9 rd7fpyb4thkz, Vega #12 rd7bf5162ae6 | `test_a_lost_partition_stays_out_of_the_table_for_an_agent_still_busy_with_it[rocksdb://-moved/-demoted]` | implied ("however we read it", "while the agents keep adding and updating users") |
| Vega #10 rd7c20qy6x7n, Nova #1 rd7fkm2nf4av | the same test, `[memory://-moved/-demoted]`: a late agent's write to a lost partition shows up | implied |
| Nova #2 rd72qhbbdcfx, Nova #4 rd79a2q6p9p4 | the walk family: `test_the_timer_walks_on_after_a_rebalance_*`, `test_every_way_of_walking_*`, `test_a_walk_paused_across_two_rebalances_*`, `test_a_walk_going_on_between_two_rebalances_*`, plus the lost-partition test | named ("dictionary changed size during iteration") |
| Orion #1 rd7cqhyb672q, Orion #8 rd72ajfftzr4 | `test_partitions_taken_over_show_up_once_recovery_is_done`, `test_the_timer_publishing_through_a_takeover_reports_nothing_taken_over_early` | the first named; the window variant implied |
| Nova #3 rd744qhs2jvd | passed first; re-eval 1 failed `test_the_timer_publishing_through_a_takeover_*` (added in wip24) | implied |
| Orion #5-#8 (baseline, FAIL_REGRESSION) | mock-based upstream tests on exactly the paths the fix must change: `test_memory.py::test_apply_changelog_batch__different_partitions_repartition_*`, `test_rocksdb.py::test__get__has_event` / `test__contains__has_event` (base test lines 328/548) | n/a |

The evalResult for Vega #12 says the agent "filters `_get_bucket_for_key`, `_dbs_for_key`, and iteration through active databases, but leaves the event-specific branches of `Store._get` and `Store._contains` unchanged". Those are rocksdb.py:495-507 and :646-656 at base, which read `_db_for_partition(event.message.partition)` directly.

### Q2 Obvious design vs reference
- **Obvious design.** Filter reads by `assignor.assigned_actives()`, copying rocksdb `_dbs_for_actives` (rocksdb.py:679-690), and prune the memory dict at recovery completion (memory.py:57-70).
- **Reference (v24).** It splits the memory store into visible and aside dicts, with `__setitem__/__delitem__` routed by the event partition at write time. RocksDB gets a `_served` gate on **every** branch, including the in-event branch, plus a cursor registry closed on revoke. Recovery gets `_superseded` guards (memory notes; solution: 9 files).
- **Where it diverges.**
  - The context-dependent branch: a current event is set, so the store takes another code path.
  - Late writes from an agent still busy with the old partition.
  - Walks that span a rebalance.
  - The window between `assignor.on_assignment` and `tables.on_rebalance`.

### Q3 Choke points
The two stores behave differently:
- **Memory store.** One dict `self.data` backs every read, so a visible/aside split covers all reads, nearly one site. Writes and changelog apply (memory.py:21-55) are separate.
- **RocksDB.** At least 6 sites:
  - out-of-event lookup `_get_bucket_for_key` :523
  - `_dbs_for_key` :671
  - in-event `_get` :495 and `_contains` :646
  - iteration `_dbs_for_actives` :679
  - `revoke_partitions` :575
- **Shared.** Recovery completion (recovery.py) and the GlobalTable exception.

No single site covers both stores.

### Q4 Primitives
Yes, strongly:
- `_dbs_for_actives` (rocksdb.py:679) already filters iteration by actives.
- memory `on_recovery_completed` (memory.py:57-70) with the `_key_partition` map (:16, :54) already prunes non-active keys.

The first proxy solve of desc v1 copied `_dbs_for_actives` and solved everything in 9.4 min (memory notes, 2026-10-23), so the primitive red flag predicted it correctly. After the re-scope (timer walks, RocksDB lookups), the final hard point was the in-event branch, which no primitive covers. It sits beside the primitive and looks already handled.

### Q5 Design spread
At least 4 designs among the near-passers:
1. RocksDB event branch left open: Vega #9, #12.
2. Memory late writes not routed: Vega #10, Nova #1.
3. Reading roles from the assignor at read time: Nova #3, which leaks in the takeover window.
4. Snapshot walks: Nova #2, #4.

Two tests separated the final passer Vega #11 (rd7898qr1fme / rd7a17fbmdny) from the rest: `test_a_lost_partition_stays_out...` (wip23) and `test_the_timer_publishing_through_a_takeover...` (wip24, which killed the Nova #3 passer).

### Q6 Source
- **A second code path** (in-event branch; the write path vs the read path).
- **Lifecycle/ordering/concurrency** (walk across one or two rebalances, held recovery, the assignor-to-tables window).
- **Multiplicity** (2 stores x moved/demoted/kept).
- Orion runs also hit **upstream test coupling** (mock tests pin the in-event paths).

### Q7 Gate check
- (b) Primitive grep was red on v1, correctly; the re-scope was the right call.
- On the final scope: (a) many RocksDB sites, passes; (c) the obvious design (copy `_dbs_for_actives`, prune at recovery) fails the in-event and walk cases on different paths, passes; (d) spread at least 4, passes.

The gate would have rated the final seam hard. What it lacked was an explicit inventory of **context-dependent branches** (current event set vs not, `is_global`, `use_partitioner`). The decisive branch was found only on the 23rd wip.

---

## 4. cc-faust-topic-start (kh72y19gr92knpsq9tktr40y458hbxzx, final review)

### Q1 Hard points (wip15: 20 functions / 32 cases; batch 11-03, 12 runs)

| run(s) | missed | named / implied |
|---|---|---|
| Nova #9-#12 (4/4), Vega #1 rd78m3fdw92a, Vega #3 rd74rr385j9n | `test_a_time_exactly_at_an_old_message_d29e4c`, `test_a_time_just_after_a_message_d29e4c` | named ("greater than or equal to that time"); the float trap is discoverable only by careful arithmetic |
| Orion #6 rd77jt155dpv | `test_a_time_exactly_at_an_old_message_d29e4c` only | as above |
| Vega #1-#4 (4/4) | `test_readers_that_disagree_are_refused_d29e4c[task-plain]` and `[agent-inner]` | named ("agents/streams ... whole app should fail"); the late-registration path is not named |
| Orion #7 rd73jrk3evaa | `[agent-inner]` only | as above |
| Orion #8 rd74c33zcyhn | `test_retention_between_two_assignments_d29e4c`, `test_partitions_back_after_a_rebalance_d29e4c` | named ("when we are given a partition") |
| Orion #5 rd7fqw3dc32n | PASS | n/a |

Why the runs failed, from the evalResult reasoning:
- **Exact millisecond.** Nova #12 truncates `int(ts*1000.0)` (its aiokafka.py:1076). Orion #6 does `ceil(initial.timestamp()*1000.0)`, and float error moves an exact-ms instant one ms late.
- **Late reader.** Vega #2 runs the conflict check only from `_update_indices` and `on_partitions_assigned`, so a reader added later through `Conductor.add` is never checked.
- **Agent-inner.** Orion #7 raises in `Conductor.add`, but the agent supervisor catches it and only that actor crashes (`Agent._execute_actor`).
- **Reassignment.** Orion #8 positions partitions in `on_partitions_assigned` before delegating, so a reassignment skips the backlog.

Earlier, wip10 went 0/11 on a table test and a lookup race. Both were later dropped as undiscoverable or unfair (memory olympus-task12).

### Q2 Obvious design vs reference
- **Obvious design.** Add `Topic.start_from`, and in `perform_seek` call seek_to_beginning, seek_to_end or offsets_for_times for partitions with no committed offset. Convert datetimes with the repo idiom `int(timestamp * 1000.0)` (aiokafka.py:454, :1431) and check conflicts when indices are built.
- **Reference.**
  - exact integer ceil to milliseconds (`_timestamp_ms`)
  - a conflict check on every reader registration in `Conductor.add` that crashes the **app**, not only the actor
  - start positions chosen per assignment, kept until a commit and cleared on revoke
  - generation guards around the awaited lookups

### Q3 Choke points
- **Seeking: one shared site.** `Consumer.perform_seek` (consumer.py:565) is reached from recovery.py:655 (the no-table path, the only one in scope), recovery.py:321 (tables, out of scope) and consumer.py:772. Editing it covers every assignment entry point.
- **Configuration: several hops.** `app.topic` kwarg, then `Topic` `_clone_args`, then `derive_topic` for group_by.
- **Conflict check: two entry paths plus a neighbour.** `Conductor._update_indices` (:366) and `Conductor.add` (:451), with the agent actor's exception supervisor next to them.

### Q4 Primitives
- **No faust primitive for start_from.** aiokafka offers the library primitives `seek_to_beginning`, `seek_to_end` and `offsets_for_times`, which made the core easy: "core-only catches 20/40" (memory).
- **The nearest repo idiom for seconds-to-milliseconds is wrong for this case**: `int(timestamp * 1000.0)` at aiokafka.py:454 and :1431. All 4 Nova runs effectively copied it.

### Q5 Design spread
Different designs at both hard points:
- Conversion: int truncation (Nova), float ceil (Orion #6, Vega), exact integer math (Orion #5, the reference).
- Conflict check: at index build only (Vega), a synchronous raise in add that crashes only the actor (Orion #7), an app-level crash (the passer).

Calibration was separated by the exact-ms test (added in wip13 from an FP-panel finding; it took out 3 of 12 replay passers) and `[agent-inner]` (added in wip15). Orion #5 is the only run correct on both.

### Q6 Source
- **Other: numeric representation**, made worse by a misleading repo idiom.
- **A second code path** (late registration through `Conductor.add`) plus a **neighbour state** (an exception inside an agent body is swallowed by the actor supervisor).
- **Lifecycle** (reassignment).

The scope also had to drop **environment/undiscoverable** corners (tables, the startup lookup race) after a 0/11 rollout.

### Q7 Gate check
- (a) The seek site is single: red flag, and correct for the core. Most runs got the core right.
- (b) No faust primitive, but the misleading idiom: green, and correct.
- (c) The obvious design (repo idiom, check at index build) fails exact-ms and late-reader cases on two different paths: passes.
- (d) Spread at least 3: passes.

The gate would have rated it hard, but it would also have approved the table and race corners that the platform later showed were unfair. A **discoverability check** was missing: run the corner's shape on plain base without the feature, before building (memory lesson in olympus-task12, wip10).

---

## Verdicts

**live-readers.** Hard through breadth, not depth. About 20 named corners over 7 or more independent sites (conductor and its Cython twin, consumer pause/flow, agents, actors, streams, aiokafka subscribe). Each Vega run missed a different one. The sharpest single trap was pause ownership: user handlers run inside faust's own rebalance window, so a time-window heuristic misclassifies them (Vega #3 x2, Vega #2). The gate would have passed it, but it cannot see the cost: 19 files, 110 cases, 61 wips, a new SQ corner every round, and the final pass came only after dropping F6.

**standby-promotion.** The seam looked hard (4-6 files) but its core was precomputed: `persisted_offset` on every store and table, and one decision site in the assignor. Vega 3/4 and Nova 2/4 passed the first rollout. The breadth traps (SetTable wrapper, custom changelog name, where the repo's own `_changelog_topic_name()` misleads) caught Orion and some Nova runs, but not Vega. The case that actually made it hard, assignor livelock on dense deploys, was emergent, unnamed, and first found as a defect in our own reference.

**table-visibility.** v1 was too easy because `_dbs_for_actives` and memory `on_recovery_completed` already computed the invariant (solved in 9.4 min). After the re-scope, the decisive hard point was a context-dependent second code path: the in-event `_get`/`_contains` branch in RocksDB and late agent writes in memory. Lifecycle windows (walk across rebalances, the assignor-to-tables window) separated Nova and Orion. Design spread was wide, at least 4 failure classes.

**topic-start.** The core (one `perform_seek` site plus aiokafka library calls) was easy. Difficulty came from two narrow, named-but-deep points:
- exact millisecond conversion, where the repo idiom `int(ts*1000.0)` is wrong
- the conflict rule on late readers, where `Conductor.add` is a second path and the actor supervisor swallows the exception

The first hard corners chosen (tables, the startup race) were undiscoverable and had to be dropped after 0/11.

## Summary table

| task | hard point | source | choke points one/many | primitive yes/no | obvious design fails? | design spread | gate verdict |
|---|---|---|---|---|---|---|---|
| live-readers | pause made inside a rebalance handler; late or restarted isolated agents; stop after crash restart (each Vega misses a different one) | multiplicity + lifecycle/ordering (+ Python/Cython twin path) | many (7+ sites, 19 files) | partial (`_update_tp_index` conductor.py:402 for late routing only) | yes (time-window pause ownership fails handler-pause + revoked-resume) | >=3 at the pause seam | gate passes; misses the over-breadth cost (no upper bound) |
| standby-promotion | livelock on dense deploy (decisive); SetTable wrapper; custom changelog name | algorithmic global property (termination) + second kind + misleading repo idiom | one decision site, many input hops | yes (`persisted_offset` stores/tables/objects.py:103; `standby_offsets` recovery.py:104); misleading `_changelog_topic_name()` partition_assignor.py:322 | yes locally (custom topic, SetTable), but platform Vega avoided both (3/4 passed) | 2 data designs x naming x free-up order | (a)+(b) red flags correct; (c) overestimated; termination fuzz missing |
| table-visibility | in-event read branch (RocksDB) and late agent writes (memory) for a lost partition | second code path + lifecycle/concurrency | memory ~one (dict), RocksDB many (6+) | yes for v1 (`_dbs_for_actives` rocksdb.py:679, memory.py:57-70); no for the final hard point | yes (copying `_dbs_for_actives` fails the in-event and walk cases) | >=4 | v1 correctly red; final passes; branch inventory missing |
| topic-start | exact-ms datetime conversion; conflicting reader added late or inside an agent body | numeric representation + misleading idiom; second path + neighbour (supervisor) | seek one (perform_seek consumer.py:565); conflict check two paths | no faust primitive (aiokafka library calls); misleading `int(ts*1000.0)` aiokafka.py:454 | yes (repo idiom + index-time check fail 2 paths) | >=3 | passes; a discoverability check was missing (tables/race dropped after 0/11) |

## Checks our workflow is missing

1. **Data-path choke map, not just the decision site.** Map every input that feeds the decision, per object kind:
   - table kinds (Table vs SetTable wrapper)
   - store kinds (memory vs RocksDB)
   - naming variants (generated vs custom changelog topic)
   - on-disk vs open state

   Standby looked like "one site" yet failed on input hops. Gate (a) as written cannot tell the two apart.
2. **Misleading-idiom grep.** Find the repo's nearest helper or idiom for the hard computation and check whether copying it gives a wrong answer: `_changelog_topic_name()` at partition_assignor.py:322; `int(timestamp*1000.0)` at aiokafka.py:454/1431. A correct helper is a red flag. A plausible but wrong helper is a green flag for difficulty. Gate (b) currently only knows the red case.
3. **Context-branch inventory.** For every promised read/write API, list the branches that depend on caller context:
   - `current_event()` set vs not; `is_global`; `use_partitioner` (rocksdb.py:495/646)
   - called inside vs outside the rebalance window (live-readers handler pause)
   - raised inside an agent body vs at startup (topic-start agent-inner)

   All three decisive cases in this lane sat in such a branch.
4. **Ownership-by-caller check for shared state.** When framework and user both mutate one structure (`_paused_partitions`, consumer.py:622-675), check whether user code can run inside the framework's own window (signals, handlers). If it can, a time-window heuristic fails: a natural trap.
5. **Global-property fuzz of the obvious design at stage 0.** Termination, no duplicates, capacity. Standby's livelock (copartitioned_assignor.py:245-260 free-up loop) was found only after the first rollout, and in our own reference.
6. **A strong-agent spike next to the obvious-design spike.** One real Opus/Vega solve on the draft seam before the full build. The repo-pattern spike said standby was hard, but platform Vega passed 3/4. The single proxy solve on table-visibility v1 caught "too easy" at once.
7. **A breadth upper bound.** Count named corners x independent sites, and cap it. Live-readers (about 20 corners, 19 files, 110 cases) passed every difficulty gate but cost 61 wips, and every SQ/AR round found a new corner.
8. **Discoverability check before building.** Run each candidate hard corner's shape on plain base without the feature, and check that base faust can even produce that state. Topic-start's table and lookup-race corners cost a 0/11 rollout and were dropped.
9. **Upstream test coupling scan at stage 0.** Grep upstream tests that mock or pin the choke sites the fix must change, and decide deselection before the build:
   - `test_rocksdb.py::test__get__has_event` / `test__contains__has_event` (table-visibility Orion FAIL_REGRESSION x4+)
   - `test_open_rocksdict` (standby Orion 4/4 baseline failures)
   - `test_seek_to_committed` (topic-start; blocked 15/22 runs before it was deselected)
