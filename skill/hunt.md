# Stage 0: find the task (repository, then seam)

Two entry points. When the owner gives a repository, skip part A and work on that repository only. When the owner
gives none, part A finds one first. Both parts use the same three lanes with one shared brief: Codex (GPT Sol 6.1
high, search mode), claude2 (Opus) and the in-process lane (Agent tool, read-only). Every pick then goes to stage 1
(Dockerfile) and stage 1b (sample and Scope Gate) before any real build.

## A. No repository given: find one
1. **Platform repo rules (a fail drops the repo):** public; 500+ stars; a commit within the last 12 months;
   production-level code; permissive licence; an allowed language; not archived; not on
   `$OLYMPUS_SHARED_ROOT/DISALLOWED-REPOS.csv` (the platform's list), `REJECTED-REPOS.md` or
   `already_built_locally.md` (`grep -ix "<owner>/<repo>"`).
2. **What makes a good host (evidence from accepted tasks, ranks the rest):**
   - Stateful framework code with lifecycle, ownership or saved formats, where a feature meets other subsystems
     (problem-design.md section 3). faust, oss-rebuild and vet each carried several accepted or approved tasks.
   - Depth: many packages and real seams; a thin repo caps difficulty. Many small, stable packages with declared but
     unimplemented interfaces are a plus (gnmi fingerprint; `tools/lib/repo_traits.sh <repo-dir>` scores a Go repository).
   - Tests that run offline through real objects and finish fast in Docker (Python and Go are smooth; Rust builds
     and test runs are slow).
   - Issue-rich, but not crowded: a very high number of merged PRs per year (`hunt.sh` prints it; faust ~73) means
     more novelty risk, and an open issue that describes the exact seam is a magnet for other submitters.
3. **Lanes:** each lane returns 5-8 repositories that pass step 1, each with the rule facts (stars, last commit,
   licence, language, list check), two candidate seams in one line each, and how its tests run offline. Codex
   search jobs need network access: run them in `workspace-write` with network (`danger-full-access` was blocked for
   search launches); write the brief in neutral words (`check_codex_brief.sh`).
4. **Decide:** merge into one table, drop every repository that fails step 1, rank by seam potential (part B shape),
   offline testability, depth, and crowding. Give the owner the top 3 with the reason. **The owner checks the
   platform's submission count for each** (no CLI access to it); a repository with many existing submissions is
   dropped. The owner's pick goes to part B.

## B. Repository given or picked: find the seam
1. `bash tools/hunt.sh <repo> "<already taken: one line per task to exclude>"` writes the facts (stars, licence,
   last push, language, merged PRs, list hits), clones the tip, writes `brief.md` from `templates/hunt-brief.md`
   and runs the Codex and claude2 lanes; start the in-process lane with the same brief at once (read-only: it never
   builds or runs the repository's code; reproductions are written tests marked NOT RUN). Exclude every task already
   built on the repository, ours and those the owner names from the platform.
2. A blocker in the facts (rule fail of part A step 1) stops the hunt: tell the owner before the lanes finish.
3. **Merge** all candidates into one table; the same seam from several lanes is one row noting each lane.
4. **Filters (drop the row if any fails):** overlaps an excluded task; any PR or issue in any state implements or
   declines it; the README says unsupported; needs network, live services or injected timing; more than 2 hard
   points or a contract over every lifecycle event; more than 4 production files (situations.md P-1..P-7).
5. **Score:** the lanes' rubric (0-8, the lowest lane's value when they differ) + 1 for each additional lane that
   found it independently + 1 for a bug whose reproduction is clear in the code - 1 per design choice the
   description would have to invent (a choice no sentence of the repo's docs or behaviour settles).
6. **Shape check (problem-design.md section 2):** 1-2 hard points, 3-4 stated consequences, each on a different
   subsystem pair. Two consequences on one pair collapse into one blind spot (goka 0/23; vet stacked two implied
   cases on "which checks ran" and got 0/16).
7. **Verify the top 3 myself:** open every cited file:line, re-run two novelty searches, write the 3-4 consequences
   in plain words. A claim that does not hold removes the candidate.
8. **Pick** the highest verified score; ties go to the one whose consequences meet more different subsystem pairs,
   then to the smaller change. Record the top 3 in `$OLYMPUS_SEAMS_ROOT/<owner>-<repo>.md` (seam-bank.md schema) and
   give the owner a short table: pick, why, two runners-up. The owner may override; otherwise stage 1 starts.
