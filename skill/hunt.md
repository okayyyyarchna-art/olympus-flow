# Stage 0: find the task (repository, then seam)

Two entry points. When the owner gives a repository, skip part A and work on that repository only. When the owner
gives none, part A finds one first. Both parts use the same three lanes with one shared brief: Codex (GPT Sol 6.1
medium, search mode), a second Claude account (Opus) and the in-process lane (Agent tool, read-only). Every pick then
goes to stage 1 (Dockerfile) and stage 1b (sample and Scope Gate) before any real build.

What the pick must give (the platform's rollout criteria, platform.md): a task Orion solves about 1 time in 4 with a
passing run of 256K+ tokens (it compacted once; we design for 300K+), Nova never, Vega rarely. Length comes from depth: the solver must
read and trace a lot of code before its first correct edit, and its own runs must keep telling it the solution is
still wrong (problem-design.md section 2). Width (more rules) multiplies test cells instead (vet task 6: 8 rules
across 27 files, 20+ review rounds, and Orion runs of 215-238K that never compacted).

**The 256K Orion plan (owner, 2026-11-21): apply it in part A and part B.**
1. **Pick fan-out repos.** Generators and multi-backend libraries where one contract change touches every output
   flavour plus committed generated fixtures. Start list: orval, openapi-typescript, progenitor, typify, prost,
   openapi-python-client, mockery; new directions: oapi-codegen, ogen, gqlgen, sqlc, ent, goa, quicktype, utoipa.
2. **Size by edit-and-verify sites, 25+.** Count the places where the solver must edit, regenerate, run a suite and read
   the diff. That fills the window; lines of code do not.
3. **Gate at blind calibration: 150K mean, 170K best.** Short reads mean widen the surface (more fan-out sites), never
   add rules.
4. **Keep the band:** Nova 0, Orion 1-25%, Vega at most 25%. The fan-out shape blocks short lucky solves.
5. **Buy Orion last:** Vega and Nova rollouts first to confirm difficulty, then Orion (16 tokens a run).
- No scope-ups of old drafts: the cliff is confirmed; only unit-triangular and vm-state-snapshots run as they are.
- Recalibrate the 150K/170K gate after 2-3 fresh problems have Orion data.

## A. No repository given: find one
1. **Platform repo rules (a fail drops the repo):** public; 500+ stars; a commit within the last 12 months;
   production-level code; permissive licence; an allowed language; not archived; not on
   `$OLYMPUS_SHARED_ROOT/DISALLOWED-REPOS.csv` (the platform's list: the owner downloads it from the platform and
   drops it there), `REJECTED-REPOS.md` or `already_built_locally.md` (your own lists, one `owner/repo` per line;
   `grep -ix "<owner>/<repo>"`). hunt.sh names every missing list: a missing list is not a pass.
2. **What makes a good host (evidence from accepted tasks, ranks the rest):**
   - Stateful framework code with lifecycle, ownership or saved formats, where a feature meets other subsystems
     (problem-design.md section 3). faust, oss-rebuild and vet each carried several accepted or approved tasks.
   - Depth for long solves: several layers between an input and its output (command -> engine -> state -> saved form
     -> reader), large source files that must be traced across, mechanisms with several execution paths that must
     agree (modes, cached vs fresh, saved formats), and a suite slow enough that a solver waits on it. A thin repo or
     one module per feature cannot give a 300K solve, however hard the rule is.
   - Many packages and real seams; many small, stable packages with declared but unimplemented interfaces are a plus
     (`tools/lib/repo_traits.sh <repo-dir>` scores a Go repository).
   - Tests that run offline through real objects and finish in Docker within minutes (Python and Go are smooth; Rust
     builds and test runs are slow).
   - Issue-rich, but not crowded: a very high number of merged PRs per year (`hunt.sh` prints it; faust ~73) means
     more novelty risk, and an open issue that describes the exact seam is a magnet for other submitters.
3. **Lanes:** each lane returns 5-8 repositories that pass step 1, each with the rule facts (stars, last commit,
   licence, language, list check), two candidate seams in one line each with their depth, and how its tests run
   offline. Codex search jobs need network access: run them in `workspace-write` with network; write the brief in
   neutral words (`check_codex_brief.sh`).
4. **Decide:** merge into one table, drop every repository that fails step 1, rank by seam potential (part B shape and
   depth), offline testability, and crowding. Give the owner the top 3 with the reason. **The owner checks the
   platform's submission count for each** (no CLI access to it); a repository with many existing submissions is
   dropped. The owner's pick goes to part B.

## B. Repository given or picked: find the seam
1. `bash tools/hunt.sh <repo> "<already taken: one line per task to exclude>"` writes the facts (stars, licence,
   last push, language, merged PRs, list hits), clones the tip, writes `brief.md` from `templates/hunt-brief.md`
   and prints the Codex and second-account lane commands. Start the three lanes at the same time, each its own
   tracked background call: the two printed commands and the in-process lane with the same brief (read-only: it never
   builds or runs the repository's code; reproductions are written tests marked NOT RUN). Exclude every task already
   built on the repository, ours and those the owner names from the platform.
2. A blocker in the facts (rule fail of part A step 1) stops the hunt: tell the owner before the lanes finish.
3. **Merge** all candidates into one table; the same seam from several lanes is one row noting each lane.
4. **Filters (drop the row if any fails):** overlaps an excluded task; any PR or issue in any state implements or
   declines it; the README says unsupported; needs network, live services or injected timing; more than 2 hard
   points or a contract over every lifecycle event; fewer than 3 or more than 30 production files on the value's
   real path; an answer visible from the surface, a repo hint that states the fix, or only one fair design
   (problem-design.md section 7 step 3b); no depth: the fix sits in one module, or nothing the solver can run shows
   it is still wrong (situations.md P-1..P-8).
5. **Score:** the lanes' rubric (0-8, the lowest lane's value when they differ) + 1 for each additional lane that
   found it independently + 1 for a bug whose reproduction is clear in the code + 1 for each decision of a
   difficulty.md kind (K1-K7) the lanes cite with file:line - 1 per design choice the description would have to
   invent (a choice no sentence of the repo's docs or behaviour settles) - 1 when the nearest repo helper already
   computes the core outcome, plus the **length score** (step 6b): files a correct solver must read before its first
   correct edit (80+ across 3+ packages: +2; 40-80: +1; under 40: drop), files it must change (15+: +1), layers the
   value crosses (3+: +1), a loop the repository itself provides that keeps failing until the design is right (its
   tests, a command's output, a saved file read back: +1), several execution paths that must agree (+1); minus 2
   when the test-grid budget (step 6c) is over.
6. **Shape check (problem-design.md section 2):** 1-2 hard points (two moderate ones preferred over one extreme),
   3-4 stated consequences, each on a different subsystem pair. Two consequences on one pair collapse into one blind
   spot (goka 0/23; vet stacked two implied cases on "which checks ran" and got 0/16).
6b. **Length design (problem-design.md section 2, written into the seam entry):** the file:line chain a solver must
   trace before the first correct edit; the count of files it must read and the packages they span; the files it must
   change; the layers the value crosses; the repository loop that keeps failing (which command, which output); the
   estimate: about 8K fixed prompt + about 20K per requirement that needs a code change + about 18% for test and
   build runs + about 15% for reasoning (vet task 6 attribution); a requirement the reference already meets adds only
   3-7K. A seam whose estimate is under 250K is one layer too shallow: find the layer (a second entry path, a saved
   state read back later, a caller context, a mode that must agree) before the pick, never a second rule.
6c. **Test-grid budget (problem-design.md section 7):** count the decision points of the planned change (about one
   per branch, merge field, tie-break, cap, cast) and, for each universal word the description will need (every, any,
   each, all pairs, any output), the axis members times the conditions. Guidance: a hidden suite of 30-60 leaves must
   cover every decision point with one kept wrong version each; a universal word over more than about 8 axis members
   needs one code path that treats all members alike, or a narrower word. vet task 6: about 300 decision points, 16
   finding families x 16 outputs x 21 lockfile names, 20+ repair rounds.
7. **Verify the top 3 myself:** open every cited file:line, re-run two novelty searches, write the 3-4 consequences
   in plain words, and walk the length chain of 6b myself. A claim that does not hold removes the candidate.
8. **Blocker check on the pick (and on a runner-up before it replaces the pick)**, written as a table in the seam
   bank, each row with file:line evidence; a row that cannot be cleared drops the candidate:
   - every consequence has a deterministic test path through an existing repo seam (CLI, stub counters, the
     engine's own stage hook); no sleep-then-act ordering (Auto Review T2 Medium on goka and task 8);
   - base tests that pin the current behaviour of every function the fix touches (grep their tests; task 12 lost
     15 of 22 runs to one pin): a deselect plan or a design that keeps them valid; upstream tests with an upper
     wall-clock bound in the touched packages (they fail Verify Flakiness on their own: vet task 6) and tests that
     skip as root, each with its skip-allowlist reason;
   - test-only helper packages of the touched packages (pinned in base mode, or a solver can weaken upstream tests),
     and the packages that import the changed code (they join the base-mode regression list);
   - sibling paths of the same rule (other queries, modes, the pull-request base side, counts) that the reference
     must also cover (task 11 SQ FAIL x2 on an unread driver path);
   - situations.md P-1..P-8, side effects across runs (caches), and the base at the current tip;
   - the length design of 6b verified by reading (not estimated from the lanes' prose) and the test-grid budget of 6c;
   - difficulty: the decision inventory of difficulty.md section 1, written by a fresh reader (the planned
     separators the solver runs are replayed on); record the calibration reserve (difficulty.md section 6) in the
     seam bank entry. Keep the runner-up verified too: it is the option when the length spike or the runs show the
     seam is too shallow or too easy (difficulty.md sections 2 and 5).
9. **Pick** the highest verified score; ties go to the deeper chain (6b), then to the one whose consequences meet
   more different subsystem pairs, then to the smaller change. Record the top 3 in
   `$OLYMPUS_SEAMS_ROOT/<owner>-<repo>.md` (seam-bank.md schema) and give the owner a short table: pick, why, length
   estimate, two runners-up. The owner may override; otherwise stage 1 starts.
10. **Cleanup:** after the pick, delete the clones, toolchains and caches the lanes created inside the hunt folder, and
    report the space freed. Keep reports, triage tables and the chosen clone. In any cleanup keep every version folder,
    eval report, brief and tool.
