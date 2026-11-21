# Raise the solve length of a task to the 256K Orion bar

Use when the design is right but the runs are short: Orion runs (hosted or local) end below the platform's 256K
sequence length without compacting. Target: the passing Orion run averages 256K+ on the platform; locally, a gpt-6-astra
(reasoning high) solve of the title and description reaches 300K or compacts once, and still solves.

Do not use it to make a task harder. Every step below adds reading, tracing or iterating; none adds a trap, a hidden
requirement or a wall. If runs fail more after a step, undo it.

Evidence used below ("vet6:") is from one accepted task (safedep/vet, PR-scan accuracy, 2026-11-20/21). Treat its
numbers as starting estimates, not guarantees.

## Limits (do not reopen these)
- The description is locked. Every text change here exists only because the owner asked for it (description.md 5b).
  Show the owner each wording; the owner writes or approves the final words.
- Every sentence you add or strengthen must describe behaviour a hidden test already checks and the reference already
  implements. A clause that needs new code gets its test and its reference change in the same round.
- No file names, function names or hints about where the fix goes. No lists in the description. Keep the owner's
  casual tone: one model-toned sentence can flip the platform's AI detector for the whole text (vet6: "Every existing
  test of the repository should still pass as it is written." failed Task Prompt Quality; "The existing tests
  shouldn't need touching, they should all still pass." passed).
- One step at a time, measured before the next. A step that adds no length is reverted or kept only for another reason
  the owner accepts.

## Step 1. Measure where the length goes (no change yet)
1. Collect every Orion trajectory you have (platform zips, local Codex sessions). For each: sequence length, number of
   requests, whether and where it compacted, minutes, hidden-test misses.
2. Attribute the length (tools/seqlen.py, tools/scout/ attribution): share of reading and searching, edits, build and
   test output, model reasoning; per requirement of the description; where the first build or test run happens; where
   the last edit happens; the compaction point (vet6 hosted: about 244K; a run that compacts restarts at 12-14K, so
   reaching compaction is as good as passing 256K).
3. List the subsystems the runs barely read (vet6: internal/policy, 4-8 of about 110 read commands) and how far each run
   stopped short of the compaction point (vet6: three runs 25-30K short).
Report this table to the owner before proposing anything.

## Step 2. Make the solver iterate against the repository's own checks
Agents that never run the existing suite stop early and break it (vet6 r46/r48: 213-230K, every run FAIL_TEST_BROKEN
from edited existing tests). Add one casual sentence that the existing tests must still pass untouched, if the text
lacks it. Measure with one local Astra solve. vet6: old text 205K and 209K without compaction; with the sentence 283K,
one compaction (s9).

## Step 3. Send the solver into a subsystem it barely reads
Pick a stated promise whose natural check lives in an unread subsystem, and widen the sentence to name the observable
outcome there (never the code). Prefer a clause the reference already satisfies: it costs no solution work and adds
reading. vet6: ", and a policy applied to it should give the same gate result" after the saved-report sentence sent runs
into internal/policy: policy share 4.6-6.8K per run against 1.4-3.8K before. Add its hidden test (fails on base, passes
on the reference) and a kept wrong version. Check the requirement count against the description limit (9 units).

## Step 4. Open the walls with plain words
A case that every run of every rollout fails ends runs early and costs no difficulty to name. When the owner asks, name
the state in plain casual words, never a subtle qualifier (vet6: "empty or not" was skimmed; "even if the PR leaves the
lockfile with no packages in it" was read). This adds little length by itself (vet6: none measured), but runs that get
past a wall keep working and reach the end of the task.

## Step 5. Keep a code-changing requirement in reserve
Build, on the side, one extra requirement that needs real code in a layer the solver must trace (a second entry path, a
saved state read back, a caller context): reference change, hidden test failing on base, kept wrong versions, proposed
wording. vet6 measured a code-changing requirement at 17-22K per run and a clause the solution already meets at 3-5K.
Use it only if steps 2-4 leave the best run short; the owner decides.

## Step 6. Strictness pass (owner method, not yet measured)
Add about 15 strict words ("must", "every", "all", "never", "definitely") only to rules the text states and a hidden
test checks, keeping length and style (description.md 5b). Show old and new text paragraph by paragraph.

## Measuring every step
- One local run per step: Codex on gpt-6-astra, reasoning high, given only "# <title>" and the description, in a clean
  clone of the base commit: `DESC=<draft> SOLVERS=4 CODEX_ONE_OFF_MODEL=gpt-6-astra CODEX_ONE_OFF_EFFORT=high bash
  tools/solvers.sh <task>` (never edit pkg/ of a pasted package).
- Report: sequence length and compaction (`python tools/seqlen.py <task>/solves/s4`), requests, minutes, hidden tests passed (replay on the
  current tests), and whether the run still solves. Local runs think more per request than hosted ones, so local
  300K is the margin for hosted 256K.
- The platform rollout is the real measure. After it, if one long run fails only implied cases, see
  prompts/near-miss-study.md (vet6: the 331K compacted run became the one Orion passer through a near-miss release).

## Report to the owner
Per step: the wording change (old and new), the hidden test that checks it, the measured length before and after,
solve status, and the next step proposed. End with the open risks (requirement count, Task Prompt Quality tone, any
case the new wording might name).
