# Near-miss study prompt (reusable)

Use when a solver run (local or platform rollout) fails only a few hidden tests, or when a platform passer exists
and we need to know which wrong behaviours it keeps that our tests do not catch. Built from faust task 11
(wip43-wip49: Auto Review 3/3 + a genuine FP pass with a passer that had a real defect) and task 12 (GPT xhigh
near-misses at 28-29/32). Words are neutral on purpose, so the same text can be given to Codex.

Fill the <...> fields, then paste everything below the line.

---

You are studying near-miss solutions of a coding task, to find behaviours the hidden tests do not yet check.
This is a read-only study: do not change description.md, test.patch, solution.patch or the Dockerfile in
<PACKAGE_DIR>. Write everything you produce under <STUDY_DIR>.

Inputs
- Task description (locked; it is the only contract): <PACKAGE_DIR>/description.md
- Hidden tests: <PACKAGE_DIR>/test.patch (graded through test.sh). Reference: <PACKAGE_DIR>/solution.patch
- Base repository at the pinned commit: <BASE_REPO>. Task image: <IMAGE>. Run containers only through
  <DOCKER_WRAPPER> (at most <N> at a time).
- Near-miss runs and the hidden tests each fails: <RUNS> (e.g. solve1: test_x, test_y)
- Known incorrect designs and valid alternatives already covered: <BATTERY_FILE> (if any)
- Test tiers (core / optional corners), if the package has them: <TIER_FILE>
- Runs that already PASS all hidden tests (platform or local passers): <PASSERS> (e.g. platform Orion #4: patch path)

Step 1 - Confirm every failure is real (no fixes yet)
For each failing hidden test of each run:
- Trace the cause with the run's patch applied (logs or temporary prints in a scratch copy), and write it in one
  line: what the run does, what the description requires, which sentence.
- Repeat the test 3 times on the run and 3 times on the reference. If the run's result changes between repeats,
  say so (timing-dependent). The reference must pass every repeat.
- Run the test's scenario on plain base WITHOUT the feature (same reader shape, the option left out). If base
  already fails to deliver or behave there, the test leans on a pre-existing problem: mark the TEST questionable.
- Run the same test on each valid alternative in <BATTERY_FILE>. If a valid alternative or the reference fails, or
  if the test needs something the description does not state, mark the TEST as questionable and stop on that item.

Step 2 - Complete each run in its own design
- Make the smallest change that makes the run pass all hidden tests, keeping its own structure and approach.
  Never copy the reference's mechanism into it. List each change (file, lines, which failure it addresses).
- Run the full hidden suite 3 times on each completed run. It must pass all three.

Step 3 - Check the completed runs from the outside
For each sentence of the description, list the outcomes a user could observe (results returned, messages read,
positions, errors raised, crashes, commits, files written ...). Then, for each completed run, the reference and
plain base, run scenarios that vary what the hidden tests fix in place:
- order and timing (events before / during / after startup, during a lookup, during a restart or rebalance);
- multiplicity (several partitions, topics, readers, members, names, instances);
- lifecycle (restart, rebalance, revoke, stop, recovery, retry, failure in the middle);
- boundary values (empty, first, last, minimum, maximum, exact equality, other time zones);
- every entry point the feature is reachable from (each API, clone/copy paths, generated objects).
Compare outcomes only, never internal state. Where the description says behaviour stays as before, compare
with plain base, not with the reference.

Step 4 - Second opinion
Give 2-3 independent reviewers the description, one completed run's patch and the hidden tests (not the reference
and not your findings). Ask each for situations where that patch does not do what the description says, each with a
concrete scenario. Run every scenario they give. A reviewer item without a reproduced run is dropped.

Step 5 - Classify every difference you reproduced
For each, one row:
| id | sentence | scenario | completed run | reference | base | class | proposed check |
Classes:
- STATED: a sentence decides it -> propose a hidden test that the reference and every valid alternative pass.
- TWO READINGS: the sentence allows two behaviours -> propose an either-or check (each reading applied in full
  passes; a mixture fails).
- PARTIAL: the run gets some outcomes of a stated case right and one wrong that the text does not decide -> propose
  a check of the outcomes it gets right; leave the undecided one unchecked and list it as a residual.
- AS BEFORE: base behaves the same -> no test (the description did not ask for a change); note the base evidence.
- NOT STATED: only implied or a general expectation -> no test; list it for the owner to decide.
For each proposed check: which runs and which known incorrect designs it fails, and confirm the reference and every
valid alternative pass it (run it). Keep the total test time inside <TIME_BUDGET>.

Step 6 - Protect existing passers, without hiding real defects
For every proposed check and every passer in <PASSERS>:
- Run the check on the passer. If the passer passes it, keep the check.
- If the passer fails it, trace why and decide with the description in hand:
  - the passer breaks what a sentence states -> keep the check; the passer is not a deserved pass and would fail
    the false-positive review anyway. Report it as "passer has a stated defect", with the scenario.
  - the sentence allows the passer's behaviour (a second reading) -> turn the check into an either-or check
    that accepts the passer's reading applied in full, and still fails a mixture.
  - the passer gets the stated outcomes right and differs only in an outcome the text does not decide -> narrow
    the check to the outcomes it gets right; list the undecided outcome as a residual with the passer's behaviour.
- After the changes, run the full hidden suite on every passer, the reference and every valid alternative: all must
  pass, and every known incorrect design must still fail at least one test.
- For every passer, list its defects that stay unchecked, each with the reason (not stated / as before / two
  readings), so the false-positive review can be answered sentence by sentence.

Output (in <STUDY_DIR>/near-miss-study.md)
1. Per run: the failing tests, the traced cause, timing-dependent or not, the completion changes.
2. The classified table from Step 5, with the commands that reproduce each row.
3. Proposed checks, ready to add at the next allowed point (before the first paste or at platform re-eval),
   ordered by how many incorrect designs each catches. Nothing is applied to the package by this study.
4. Questionable hidden tests from Step 1, if any, with evidence.
5. Per passer: the checks it passes, the checks it fails with the decision from Step 6, and its unchecked
   residuals with reasons.

Rules
- Reproduce before you conclude; a claim without a run is not a finding.
- Never weaken the reference or remove a fair test to make a run pass.
- The description is never changed by this study.
- Keep the full matrix in one pass (all scenarios x all runs), not one scenario per round.
- A passer is kept only for differences the description does not decide; a passer that breaks a stated sentence
  is reported, never protected.
