# Difficulty retro synthesis (12 tasks, 2026-11-12)

Sources: lane-a-vet.md (4 vet tasks), lane-b-faust.md (4 faust), lane-c-other.md (docker proxy, turso, elio, swift).
Every claim below is backed in those reports with run ids, test names and file:line.

## 1. Hard on the first suite: almost never

| Task | Hard on the first suite? | How it reached the band |
|---|---|---|
| docker proxy | yes (1/16) | already hard |
| turso NOT IN | no (Vega 2/4) | one added test: `NOT (x IN ...)` spelling -> Vega 1/4 |
| elio history | no (Orion 4/4 on 40 tests) | one added test: Duplicate Finder rename -> Orion 1/4 |
| swift writes | no (Vega 4/4, Orion 3/4) | suite grew 6 -> 8 -> 10 tests -> Orion 1/4 |
| vet local-registry | no (5/6 at v1) | PR path stated, then one separator case (first called unfair) |
| vet unused-suppression | split by one late unnamed case | one assertion (unknown control id) carries Vega 1/8 |
| vet continue-usage | split only by fake enrichers | parked; no real-code case split the passers |
| faust live-readers / standby / table-visibility / topic-start | mostly no | calibration on near-misses; standby's livelock found after the first rollout |
| **vet direct-deps** | no (13/16) | **no calibration possible: zero behavioural spread among 14 passers** |

**Most accepted tasks were made hard after the first rollout, not before.** The workflow's real engine is
calibration: near-passers that differ by one decision, then one fair test on that decision. Direct-deps failed
because that engine had nothing to work on.

## 2. What the hard decisions had in common

In every task that reached the band, the separator was **one decision the agent had to make itself, where the
natural default was wrong**. Six kinds, all seen at least twice:

| Kind | Examples |
|---|---|
| Misleading nearby idiom or helper (copying it gives the wrong answer) | topic-start `int(ts*1000.0)`; standby `_changelog_topic_name()`; unused-suppression `Header.Controls` (right helper `controls.Catalog` sits far away) |
| Caller-context branch (same API, different caller state) | table-visibility read during an event; live-readers user handler inside faust's rebalance window; topic-start error inside an agent body |
| Second path or shortcut that skips the shared site | vet local-registry PR prior lookup; swift multipart re-send returns 200; elio Duplicate Finder rename |
| Intermediate semantics inside one site | turso: UNION dedupes 1 and 1.0 before the TEXT comparison |
| Identity or timing | docker: symlink resolved at write time; elio: stale-token guard drops completed moves |
| Exception neighbour (the cleanup fails, an unknown state, the evidence arrives as an error) | swift: rollback delete fails; vet unknown control id vs turned off |

**Direct-deps had none.** Every decision was made correctly by the nearest code: store on the finding like
reach (evaluate.go), PathFrom/MayReach (graph.go:175/217), even the exact three-way rule at reach.go:309-312.

## 3. My first gate was wrong as a veto

- (a) "one choke point = red": turso had one site and was hard (intermediate semantics); elio had many and was easy at first.
- (b) "a helper exists = red": helpers that are near and RIGHT make a task easy; near and WRONG make it hard (a green flag).
- (c) the obvious-design spike was right in spirit, but only when written at agent strength (a naive spike over-rated standby and continue-usage).
- (d) design spread was always met by the hard tasks: near-misses differed by one choice, not by architecture.
(a) and (b) are useful as prompts, never as vetoes.

## 4. The check we were missing: a decision inventory before the build

At stage 0, for the seam, list every decision an implementer must make (where to compute, where to store, which
helper, which identity, which caller contexts, which paths reach the promise, what happens when cleanup fails).
For each: what the nearest repo idiom or helper would decide, and whether that is right.
**Gate: at least 2 wrong-by-default decisions on different paths or kinds, each reachable by a fair case the text
covers (stated, or repo-discoverable).** Evidence types: the six kinds above.
Then measure: the agent-strength obvious-design spike must fail those cases. Optional: 2 Orion runs on the sample
and a replay of their patches on the planned probes.

Applied backwards: direct-deps = 0 wrong-by-default decisions (reject or widen at stage 0); turso, topic-start,
standby, unused-suppression, swift, docker each show >= 2 when the inventory is done honestly (lanes A-C).

## 5. Other missing checks the lanes found (to fold in)
1. Upstream test coupling scan at stage 0: base tests that pin the code the fix must change (topic-start
   `test_seek_to_committed` blocked 15 of 22 runs; table-visibility, standby).
2. Breadth and trap-stack cap: one deep family + one neighbour was enough (turso, elio, swift); live-readers'
   ~20 corners / 110 cases cost 61 wips.
3. Single-assertion fragility: if removing one assertion makes the task too easy, flag it before submit.
4. The separator must follow a stated sentence or a repo line, never a choice made only inside the reference
   (local-registry idD, unused-suppression older report).
5. Persistence probe for every saved-state hard point (direct-deps: the finding JSON made saved scans free).
6. Too-easy alarm: a short valid variant built on repo helpers that passes everything (direct-deps V11, 35/35).
7. Global-property fuzz (termination, duplicates) of the obvious design (standby livelock, found late).
8. Pass counts per family from the view JSON, including infra replacements.
