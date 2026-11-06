# S0 hunt: the user gives a repository, three lanes search, the decision is automatic

## 1. Start (about 2 minutes of my time; the lanes take 10-30 minutes)
1. `bash tools/hunt.sh <repo> "<already taken: one line per task>"` -> facts, clone at the tip, `brief.md`, and the
   Codex and claude2 lanes in the background.
2. Start the in-process lane with the same brief (Agent tool, read-only: it must not build or run the repository's
   code; reproductions are written tests marked NOT RUN). Save its returned report to `eval/inprocess-hunt.md`.
3. If the facts show a blocker (under 500 stars, no commit in 12 months, non-permissive licence, on one of our
   lists), stop and tell the user before the lanes finish.

## 2. Decide (automatic, when all three reports are in or after 45 minutes with what arrived)
1. **Merge:** one table of all candidates; the same seam found by several lanes is one row noting each lane.
2. **Filters (drop the row if any fails):** overlaps an excluded task; any PR/issue implements or declines it; README
   says unsupported; needs network, live services or injected timing; more than 2 hard points or a "consistent across
   every lifecycle event" contract; more than 4 production files.
3. **Score:** the lanes' rubric (0-8, take the lowest lane's value when they differ) + 1 for each additional lane that
   found it independently + 1 for a bug whose reproduction is clear in the code - 1 per design choice the description
   would have to invent (a choice no sentence of the repo's docs or behaviour settles).
4. **Verify the top 3 myself** (10 minutes): open every cited file:line, re-run two novelty searches, and write the
   3-4 stated consequences in plain words. A claim that does not hold removes the candidate.
5. **Pick** the highest verified score. Ties: prefer the one whose consequences meet more different subsystem pairs,
   then the smaller change.
6. **Record** the top 3 in `~/OSS/shipd/seams/<owner>-<repo>.md` (seam-bank schema) and tell the user in a short
   table: pick, why, two runner-ups. The user may override; otherwise continue to S1 with the pick. Every pick,
   also on a repo that already has a task, goes through the S1b sample (Scope Gate PASS) before S2.
