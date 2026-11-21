# Quick seam checklist (DRAFT for the owner, 2026-11-13; BACKLOG #145)

Goal: decide in about 20 minutes, from reading with evidence, whether a seam is worth building. It replaces the
hand-written obvious-design spike as the stage-0 gate. The measured gate stays at stage 3 (2 Orion + 2 Vega, zero
spread stops). Every answer needs file:line evidence and, where asked, one concrete input with both outputs.

## Evidence it rests on
- 12-task retro (synthesis.md): accepted tasks reached the band on ONE decision the agent had to make itself, after
  the first rollout. The one true failure (direct-deps) had zero: the nearest code made every decision right.
- 2026-11-13: the 2-decision spike passed 0 of 5 seams. On pmg, 2 real Opus 5.5 high solves both fixed the named
  symptom and both missed two outputs the text covers but does not name (the withheld hint named a never-served
  version; one package fetched twice was counted twice). My hand-written spike passed one of those (I knew the trap).
- Both misses had their right answer NEAR the wrong code (same function; same file). Distance did not predict the
  miss; being an unnamed consumer of the same data did. Same shape in the retro: elio Duplicate Finder (an unnamed
  second path), turso NOT (x IN ...) (an unnamed second form), swift multipart re-send, vet unknown control id.

## The checklist
| # | Question | STOP when |
|---|---|---|
| 1 | Is there a sibling feature that already does the whole requirement, so copying it decides everything right? Cite it. | yes (direct-deps: reach + PathFrom/MayReach; dev-only shortcut 9/9) |
| 2 | Name the one symptom the description will state (one input, wrong output, right output). | it cannot be shown on the pinned code |
| 3 | List every other reader of the same data or decision: counters, report lines, hints, audit events, saved state, exit codes, a second command or entry path, a second kind of object, an error or cleanup path. | (list only) |
| 4 | For each reader: does a fix of only the stated symptom leave it wrong? One input, both outputs. | no reader stays wrong |
| 5 | For each row from 4: does the general sentence plus a repo line (doc, code comment, user-visible text) settle the right answer? Cite it. A choice the repo leaves open is a scope choice and does not count. | no row is settled |
| 6 | Can the description stay general (no row named) and still be fair for the row? | every row would have to be named to be fair (a named row is one agents do) |
| 7 | Practical: tests offline and deterministic; no upstream test pins the code the fix must change (or it can be restored); one rule plus at most one neighbour family; at most 9 units; not a Scope Gate duplicate. | any line fails and cannot be fixed |

**Decision:** at least one row passes 4, 5 and 6 -> CONTINUE (those rows are the planned separators and the
calibration reserve). Otherwise STOP -> the runner-up seam (difficulty.md section 2).

## pmg applied (worked example)
1 no sibling does it. 2 an npm package whose only eligible version has no publish time is reported blocked.
3-5: withheld hint (stats.go:185 "versions stripped from a package's metadata") - wrong after a symptom-only fix,
settled; blocked count and block list (stop.go:109 "%d package(s) blocked") - wrong, settled; latest tag - wrong in
one of two solves, but which version becomes latest is a design choice (out); version ranges - scope choice (out).
6 the text stays general. -> CONTINUE with 2 rows; both real solves failed exactly those 2.

## Before it replaces the spike in the kit
- Blind validation: a fresh agent applies it, without outcomes, to seams whose outcome we know (direct-deps,
  dev-only, vet reach, pmg #562 = expected STOP; elio, turso, swift, unused-suppression, pmg cooldown = expected
  CONTINUE). Accept if it gets them right; my own backward check is not proof (I know the outcomes).
- Optional early read when the owner wants one: one local Opus high solve on the sample text, replayed on the rows.
