# Family profiles: how the platform agents decide (input to difficulty.md)

Planning data, never a gate and never a reason to change a sentence: the rollout measures. Sources: the 2026-11-12
retro of 12 tasks (olympus-product/analysis-20261112, lanes A-C, run ids there), the Orion profile of 2026-10-12
(17 runs, faust), the Vega profile of 2026-10-19 (9 runs, faust) and vet task 6 (10 hosted Orion trajectories,
2026-11-14 to 2026-11-20). Agents get stronger week by week, and the platform changes their models without notice:
read `aggStats.byModel` and the newest run after every rollout (platform.md); when a row here disagrees with a newer
rollout, the rollout wins and the row is updated (section 4).

## 1. What every family does
- **Stated points are solved.** vet direct-deps: all 11 completed runs got every stated point right; both failures
  were on unstated points the repo decides. A named corner moves from rare to almost always (vet local-registry: the
  PR path, once named; faust task 11: a named rebalance clause 0/4 -> 4/4; vet 6: a plainly named wall case went from
  0 of 4 runs to 1 of 2 fully and 1 of 2 nearly).
- **The description is used as a checklist, read by the nearest noun.** Runs map sentence by sentence to code and
  write one own test per clause; final summaries repeat the sentences as bullets. A scope word is read by its nearest
  noun ("every lockfile ..., paired with the manifest file" became a table of file names; no run asked which states of
  the lockfile count). A subtle qualifier is skimmed; a wall case needs plain words (description.md 5b).
- **The nearest repo code is copied.** When it is right the task is easy whatever the text says (direct-deps
  PathFrom/MayReach 13/16; table-visibility v1 solved in 9.4 min). When it is wrong it is the best separator we have.
- **A mirrored mechanism gets its own budget.** New code that must agree with an existing walk, reader or limit is
  rebuilt with a separate counter or order; the case above the limit is never tested by the agent (vet 6: 4 of 6
  Orion runs).
- **Their own tests decide when they stop.** They trace, write regression tests from their reading, fix, run the
  repository gate, and stop when it is green. Nothing they run corrects a narrow reading; a case they did not think
  of never fails for them.

## 2. Hit rates per decision kind (share of runs that got the decision right; post-2026-10-20 evidence)
| Kind (difficulty.md) | Evidence | Planning rate |
|---|---|---|
| Stated in the text | every task | ~1.0 |
| Unstated, nearest repo code decides it right | direct-deps, standby progress, table-visibility v1 | ~1.0 |
| K1 misleading nearby idiom or helper | topic-start `int(ts*1000.0)`: Nova 4/4 copied it, Orion 1 of 4 exact; standby `_changelog_topic_name()`: 3 of 15 patches; unused-suppression `Header.Controls`: 15/16 wrong | 0.1-0.3 |
| K2 caller-context branch | live-readers handler pause: 3 of 6 Vega wrong; topic-start late reader: Vega 4/4 wrong; table-visibility in-event branch: Vega 2, Nova 1 wrong | 0.3-0.5 |
| K3 second path or shortcut | local-registry PR previous version: Vega 4/4 and Orion 4/4 wrong; elio Duplicate Finder rename: Orion 3/4 wrong; vet 6 saved report read back per manifest: Orion 8/8 wrong | 0.1-0.4 |
| K4 intermediate semantics | turso UNION dedup before the TEXT compare (Vega 2/4 -> 1/4 with one more spelling); vet 6 a kept copy next to a removed copy of one package: Orion 4/8 wrong | 0.3-0.5 |
| K5 identity or timing | docker linked directory replaced: Vega 4 + Nova 4 wrong; elio stale-token guard | 0.2-0.4 |
| K6 exception neighbour | vet unknown control id: 15/16 wrong; docker removed directory: Vega 4, Nova 3, Orion 1 wrong; direct-deps open root with a known path: Nova 2 wrong | 0.1-0.4 |
| K7 mirrored mechanism with its own budget | vet 6 base walk with a separate link limit: Orion 4/6 wrong; folders linked under two names 3/6 | 0.3-0.5 |
| Second kind of the same object (breadth) | standby SetTable wrapper: Orion 4/4 wrong, Vega 0 | family-specific |
| Emergent global property (termination, duplicates) | standby livelock: 5/5 earlier passers wrong | ~0 once tested |
| A state no visible test or doc shows (an emptied input, a zero-byte file) | vet 6 emptied lockfile: Orion 0/4 until named plainly | ~0.1 unnamed, ~0.75 named |
Rough sizing: predicted pass per family ~= product of its rates over the unstated decisions (problem-design.md
section 2 table). Two K1/K6/K7 decisions on different paths put every family near or below 25%.

## 3. Per family
**Orion (Codex CLI, GPT Sol 6.1 at xhigh; a hosted build older than the current CLI).**
- Length: 100-145 requests, 25-31 minutes; reading and searching 75-79% of the context, edits 15%, build and test
  output 6%; first repository gate at 146-175K, last edit at 211-244K; compaction at about 244K; sequence lengths
  215-238K without compaction, 297K and 330K with one (vet 6). Earlier tasks: 97-151K. Tool output is capped near 10K
  characters per call, so big files take several reads, and a decisive line can be cut from a batched command (noise,
  not a property of the task).
- Reads 4-7K lines, then one-shot design (first edit holds 81-99% of the final lines); never re-reads the description
  after planning; on a wide task it reads a little per area (internal/policy got 4-8 of about 110 read commands).
- Mirrors the sibling implementation, quirks included (9/9 on faust sqlite), and rebuilds a mechanism it must agree
  with as a second implementation with its own limit (vet 6).
- Misses: a second kind of the same object (SetTable 4/4), implied cross-subsystem runtime interactions (flow
  control 0/8), latent adjacent upstream bugs (7/8), a saved form read back later (vet 6 8/8), states no visible test
  shows (emptied inputs 0/4 until named).
- Breaks pinned upstream tests on the paths it changes (standby `test_open_rocksdict` 4/4, table-visibility
  FAIL_REGRESSION x4): the upstream coupling scan (hunt.md B step 8) matters most for Orion.
- Exact arithmetic sometimes right where the others copy the idiom (topic-start Orion #5, the only full pass).
- Platform Orion can sit far from local GPT solves in both directions (2026-11-02: local 1/4, platform 4/4; vet 6:
  local xhigh solves 275-304K, hosted 215-238K): the local run is a stand-in, not a replica.

**Vega (Claude Code on Claude Opus 5.5).**
- Long runs: 158-600K, 106-177 steps; vet 6: 377K and 453K with no compaction (its window is much larger, so a Vega
  compaction needs about 3x the work of an Orion one); reads dependency sources; runs the full suite often.
- Implements what is named, misses what is only implied (faust task 7: implied corners 0-2 of 8).
- Weakest on caller context: a callback inside the framework's own window (live-readers), a reader added later
  (topic-start 4/4), the in-event read branch (table-visibility).
- Takes the head/upgrading path and misses the base or previous side (local-registry 4/4).
- Each run misses a different corner on a broad task (live-readers: 5 of 6 missed at least one).
- Must stay at or under 25%: a Vega pass is a cost under the current criteria, not a target.

**Nova (Gemini CLI; model read from the first run of each rollout).**
- Very long runs: about 0.5-2.5M. Must stay at 0 passes.
- Copies the nearest idiom most often (topic-start int truncation 4/4).
- Takes defensible alternative readings (local-registry idD x3), so a Nova-only separator is fragile.
- Not near 0% by itself: direct-deps 3/4, standby 2/4 on the first rollout, local-registry 1/4 final. A Nova pass
  fails the task: the separators must hold against the nearest-idiom design too.

## 4. Upkeep (rollout.md step 1)
After every rollout, add each decision the runs met to the Evidence cell of its kind in section 2: task, runs
right / runs total per family, and the run ids in the task's rollout digest; add each run's sequence length and
compaction to the family's length line; record the hosted harness fingerprint (tools/scout/stage_a.py: hidden prompt
size, reasoning per request, compaction point) so a platform change shows at once. Re-derive the planning rate of a
kind when its newest three tasks disagree with it; drop evidence older than two months when newer exists.
