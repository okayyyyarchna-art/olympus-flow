# Family profiles: how the platform agents decide (input to difficulty.md)

Planning data, never a gate and never a reason to change a sentence: the rollout measures. Sources: the 2026-11-12
retro of 12 tasks (olympus-product/analysis-20261112, lanes A-C, run ids there), the Orion profile of 2026-10-12
(17 runs, faust) and the Vega profile of 2026-10-19 (9 runs, faust). Agents get stronger week by week: when a row
here disagrees with a newer rollout, the rollout wins and the row is updated (section 4).

## 1. What every family does
- **Stated points are solved.** vet direct-deps: all 11 completed runs got every stated point right; both failures
  were on unstated points the repo decides. A named corner moves from rare to almost always (vet local-registry: the
  PR path, once named; faust task 11: a named rebalance clause 0/4 -> 4/4).
- **The description is used as a checklist.** Runs map sentence by sentence to code and write one own test per
  clause; final summaries repeat the sentences as bullets (vet direct-deps trajectories, Orion 2026-10-12 17/17).
- **The nearest repo code is copied.** When it is right the task is easy whatever the text says (direct-deps
  PathFrom/MayReach 13/16; standby `persisted_offset` Vega 3/4 + Nova 2/4 on the first rollout; table-visibility v1
  solved in 9.4 min). When it is wrong it is the best separator we have (below).

## 2. Hit rates per decision kind (share of runs that got the decision right; post-2026-10-20 evidence)
| Kind (difficulty.md) | Evidence | Planning rate |
|---|---|---|
| Stated in the text | every task | ~1.0 |
| Unstated, nearest repo code decides it right | direct-deps, standby progress, table-visibility v1 | ~1.0 |
| K1 misleading nearby idiom or helper | topic-start `int(ts*1000.0)`: Nova 4/4 copied it, Orion 1 of 4 exact; standby `_changelog_topic_name()`: 3 of 15 patches; unused-suppression `Header.Controls`: 15/16 wrong | 0.1-0.3 |
| K2 caller-context branch | live-readers handler pause: 3 of 6 Vega wrong; topic-start late reader: Vega 4/4 wrong, agent-inner Orion 1 wrong; table-visibility in-event branch: Vega 2, Nova 1 wrong | 0.3-0.5 |
| K3 second path or shortcut | local-registry PR previous version: Vega 4/4 and Orion 4/4 wrong; elio Duplicate Finder rename: Orion 3/4 wrong; swift multipart re-send | 0.2-0.4 |
| K4 intermediate semantics | turso UNION dedup before the TEXT compare (Vega 2/4 -> 1/4 with one more spelling) | 0.3-0.5 |
| K5 identity or timing | docker linked directory replaced: Vega 4 + Nova 4 wrong; elio stale-token guard | 0.2-0.4 |
| K6 exception neighbour | vet unknown control id: 15/16 wrong; docker removed directory: Vega 4, Nova 3, Orion 1 wrong; direct-deps open root with a known path: Nova 2 wrong | 0.1-0.4 |
| Second kind of the same object (breadth) | standby SetTable wrapper: Orion 4/4 wrong, Vega 0 | family-specific |
| Emergent global property (termination, duplicates) | standby livelock: 5/5 earlier passers wrong | ~0 once tested |
Rough sizing: predicted pass per family ~= product of its rates over the unstated decisions (problem-design.md
section 2 table). Two K1/K6 decisions on different paths put every family near or below 25%.

## 3. Per family
**Orion (Codex harness, behaves like GPT Sol 6.1 medium-high).**
- Short runs: sequence about 97-151K; reads 4-7K lines, then one-shot design (first edit holds 81-99% of the final
  lines); never re-reads the description after planning.
- Mirrors the sibling implementation, quirks included (9/9 on faust sqlite).
- Misses: a second kind of the same object (SetTable 4/4), implied cross-subsystem runtime interactions (flow
  control 0/8), latent adjacent upstream bugs (7/8).
- Breaks pinned upstream tests on the paths it changes (standby `test_open_rocksdict` 4/4, table-visibility
  FAIL_REGRESSION x4): the upstream coupling scan (hunt.md B step 8) matters most for Orion.
- Exact arithmetic sometimes right where the others copy the idiom (topic-start Orion #5, the only full pass).
- Platform Orion can sit far above local GPT solves (2026-11-02: local 1/4, platform 4/4).

**Vega (Claude Code with a Claude model at high effort).**
- Long runs: about 158-600K, 106-177 steps; reads dependency sources; runs the full suite often.
- Implements what is named, misses what is only implied (faust task 7: implied corners 0-2 of 8).
- Weakest on caller context: a callback inside the framework's own window (live-readers), a reader added later
  (topic-start 4/4), the in-event read branch (table-visibility).
- Takes the head/upgrading path and misses the base or previous side (local-registry 4/4).
- Each run misses a different corner on a broad task (live-readers: 5 of 6 missed at least one).

**Nova.**
- Very long runs: about 0.5-2.5M; the gate needs its average above 400K, which real depth gives for free.
- Copies the nearest idiom most often (topic-start int truncation 4/4).
- Takes defensible alternative readings (local-registry idD x3), so a Nova-only separator is fragile.
- No longer near 0%: direct-deps 3/4, standby 2/4 on the first rollout, local-registry 1/4 final.

## 4. Upkeep (rollout.md step 1)
After every rollout, add each decision the runs met to the Evidence cell of its kind in section 2: task, runs
right / runs total per family, and the run ids in the task's rollout digest. Re-derive the planning rate of a kind
when its newest three tasks disagree with it; drop evidence older than two months when newer exists.
