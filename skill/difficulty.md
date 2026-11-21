# Difficulty and length: measure the seam before the build (stages 0, 2, 3, 8)

Why (retro of 12 tasks, olympus-product/analysis-20261112/synthesis.md, and vet task 6): only one task was hard on
its first suite. The others reached the band through calibration: their passers differed on one decision, and one
fair test on that decision did the rest. vet direct-deps could not be calibrated: the repo made every decision for
the agents, and its 14 passers behaved the same. And no earlier task was long enough for the current criteria: every
Orion pass before 2026-11 was 106-190K, while the platform needs the passing Orion run to average 256K+ (one
compaction). So the aim is a task that **can be calibrated** and whose solve **compacts**: difficulty is seen in the
solver runs after the lock (section 3); length is designed at stage 0 (problem-design.md section 2) and measured
before the lock by the length spike (section 2), because nothing after the lock can add it.

There is no correctness gate before the lock (owner 2026-11-16): a reading verdict failed a blind test (fresh readers
rated all five seams hard, the known-easy direct-deps included). The inventory stays as the generator of planned
separators and the reserve. The length spike is a number, not a verdict, and it is a gate.

## 1. Decision inventory (stage 0, hunt.md part B step 8): a generator, not a verdict
**Who:** a fresh in-process Agent (read-only), never the builder. Its brief: the clone at the pin, the requirement in
one line of user words, and this section. No reference, no draft, no hunt notes, no list of hard points (the builder
rated two hard points on direct-deps that the repo had already written).

**What it lists:** every decision an implementer must make for the requirement:
- where to compute, and where to keep the result (does a saved scan, report, restart or second command read it?);
- which helper, idiom or identity to use (copy the sibling code or not; which key, unit, name);
- which caller contexts reach the code (inside a framework window, a handler, a late registration, an error path);
- which entry paths reach the promise (another command, a saved file, the base side of a comparison, a fast path that
  answers early, a second kind of the same object);
- intermediate steps that change a value before it is used;
- what happens next to every exception or failure: unknown, missing, failed, partial, older state, and an undo or
  cleanup that itself fails. Exception, cleanup-failure and race cases are listed as candidates, never discarded as
  contested (blind test: the swift reader found all three decisive cases and set them aside);
- an existing mechanism the new code must agree with (a walk, a reader, a limit): does the implementer consume its
  decisions or rebuild its rules? A rebuilt mirror with its own limit or order is the most dependable separator we
  have (vet 6: 4 of 6 Orion runs built two link budgets).

**Per decision, one row:** the nearest repo idiom or helper (file:line), what it would decide, right or wrong for the
requirement (with one input where the two differ), the kind below (or none), the fair route that makes it gradable (a
sentence the text will need, or a repo line), and whether the stated fix leads an implementer to the right answer.

| Kind | What it looks like | Examples |
|---|---|---|
| K1 misleading nearby idiom or helper | copying the nearest code gives the wrong answer; the right helper sits far away | topic-start `int(ts*1000.0)`; standby `_changelog_topic_name()`; unused-suppression `Header.Controls` |
| K2 caller-context branch | the same API behaves differently by caller state | live-readers handler inside the rebalance window; table-visibility read during an event |
| K3 second path or shortcut | a path that skips the shared site | local-registry PR previous version; swift multipart re-send; elio Duplicate Finder rename |
| K4 intermediate semantics | a step inside one site changes the value first | turso UNION dedups 1 and 1.0 before the TEXT compare |
| K5 identity or timing | which object, at which moment | docker symlink resolved at write time; elio stale-token guard |
| K6 exception neighbour | the state next to an exception is not the exception | vet unknown control id vs turned off; swift rollback delete fails |
| K7 mirrored mechanism | new code rebuilds an existing mechanism's rules instead of consuming its decisions | vet 6 base walk with its own link budget (false REMOVED above the limit) |

The builder opens every cited line before trusting a row; a claim that does not hold is dropped. The rows become the
planned separators the solver runs are replayed on (section 4) and the calibration reserve (section 6). The best
separators are rows the stated fix does not lead to: a reader, path or state the text does not point at, or a wrong
idiom with no right helper. Distance alone decides nothing: agents find a nearby helper when the asked-for fix leads
them to it, and miss a nearby fix for a case the text does not point at. Predict a miss wherever a stated rule reaches
a state the visible tests and docs never show: the agents write their own tests from their reading, so nothing they
run corrects a narrow reading (vet 6 trajectories). Planning rate (optional, for the owner): per family, the product
of its profiles.md rates over the unstated rows; never a gate and never a reason to change the text.

## 2. Length spike (stage 2, before the lock; owner 2026-11-18: "make sure the agent compacts, at least once")
**What:** two local blind solves of the draft text (with the sample tests) by the Orion stand-in: Codex CLI, GPT Sol
6.1, xhigh effort (`bash tools/solvers.sh <task> spike`: solves 7 and 8, each in its own clone of base, given only the
title and the text). They run in parallel with the reading audits; the builder keeps working.
**Measure:** `python tools/seqlen.py <task>/solves/s7 <task>/solves/s8` (the Codex session log of each solve, copied
next to its meta.txt): windows, each window's peak, requests, sequence length, compacted yes/no. Sequence length is
counted as the platform counts it (rule `window_peaks_2026_11b`): the sum over context windows of the window's peak of
input + output tokens of one request; the tool matches the platform's own field on every stored run. Record both
solves in the ledger's Difficulty section and the design file.
**Gate:** the mean sequence length of the two solves is 300K or more, and neither is under 250K. Do not ask the local
stand-in to compact: GPT Sol 6.1 runs locally with a 475K window and reaches 300K without compacting, while the hosted
Orion build compacts at a window peak of about 244.6K (so a hosted run of 300K has compacted once; vet 6 run #3:
244,600 + 86,367 = 330,967). The local run also reasons 2-3x more per request than the hosted one (510-762 vs
252-282 reasoning tokens), so local lengths overstate hosted ones; 300K local is the margin for the platform's 256K.
(vet 6: the local gpt-6-astra stand-in on the narrowed text peaked at 205-209K; local Sol xhigh solves of the wider
text reached 277-307K; 5 of 6 hosted runs then stayed at 206-238K and the one that compacted was the pass.)
**Below the gate:** the seam is one layer too shallow. Deepen it, never widen it: add the layer, path or saved state
the value must be traced through (a second entry path the repository documents, a reader of saved state, a caller
context the repository has, a mechanism that must agree with the new one). Redraft the sentence that names the
outcome (one requirement, no mechanism), re-paste the sample (the Scope Gate is re-run on the final package anyway),
run the spike again. After two failed spikes the owner chooses: the hunt's runner-up seam or a redesign. Never a
hidden step, noisy logs or padding: that is reward hacking and unfair.
**What else the spike gives:** which planned separators (section 1) each solve missed, graded on the sample tests and
the inventory probes; they go into the tests at stage 4 and into the variant corpus. A spike solve that passes
everything is audited as a passer once the full reference exists (PIPELINE.md, Confirmation schedule).
Local solves are not a replica of the hosted harness (different build, tool set, context window and compaction
point): read the local fingerprint with `tools/scout/local_sessions.py --marker <clone name>` and compare it with the
hosted one (`tools/scout/stage_a.py` on the rollout's trajectories: hidden prompt part, requests, reasoning per
request, windows) after each rollout; a changed hidden part means a changed hosted build.

## 3. Solver runs after the lock (owner 2026-11-16)
Right after the lock on the owner's humanized text (description.md step 11):
1. Paste the locked text with the sample tests (no run or check active) and notify the owner: the owner runs
   **2 Orion + 2 Vega** on the platform.
2. At the same moment start **3 + 3 local solves** of the locked text: 3 Claude Opus 5.5 high and 3 Codex GPT Sol 6.1
   xhigh (`bash tools/solvers.sh <task>`: solves 1-3 Opus, 4-6 GPT; each in its own clone of base, given only the
   title and the text). When only the wording changed between the spike and the lock, the two spike solves count as
   two of the three GPT solves. Local and platform runs go in parallel.
3. The builder never waits for any of them: stage 4 (tests) starts at once and the build goes on by the workflow. The
   text never changes after the lock, so the four platform runs count toward the final rollout (re-evaluated on v1);
   never change the Dockerfile after them (it would lose their re-eval). Nothing is pasted until the platform runs
   end; only a platform reject stops the build.

## 4. Reading the runs (at whatever stage the build is)
1. Grade each local solve as it finishes (only the CLEAN ones, solves/watch.md; `tools/lib/replay_patches.sh`) and
   start the FP audits of every passer in the same step (PIPELINE.md, Confirmation schedule). Pull the platform runs
   when they end (`tools/rollout_report.py`: misses, verdict, sequence length, compaction, requests per run). Replay
   every patch, local and platform, on the planned tests, the inventory separators (section 1) and the reserve probes
   (section 6). The platform's junit is the truth for a platform run: a local replay can pass tests the platform
   failed (vet 6: five link tests on two runs, a sandbox difference); report replay-vs-platform differences per test.
2. **Keeper:** the best run that is correct, confirmed by an FP audit with probes replayed on the reference. The suite
   is built so the keeper and the reference pass it and every other design fails on a fair case: each gap in the
   other runs, the variants and the reserve gets a fair test (a stated sentence or a repo line at the assertion, never
   a case invented to reject one run). The aim is one Orion passer in the final 4-4-4, and that passer long. With no
   correct run there is no keeper: the tests still close every gap, and the band comes from the new runs.
3. Every gap a run showed is also a design a new run may take, so it goes into the variant corpus (must fail); every
   correct run that differs from the reference is a valid alternative that must pass (build-checklist.md section 4).
4. Length reading: every platform run's `compacted` and `sequenceLength`, and per area how many read commands the
   runs spent (`tools/scout/attribution.py`). Three runs that stop 25-30K short of the compaction point say the seam
   is one layer shallow for the platform; one compacting pass among short failures says the depth is there and the
   pass rate decides.

## 5. When every run is correct with the same output (too easy)
All runs correct on the planned tests and on every separator and probe, with no spread (as on direct-deps): tell the
owner at once with the options and their costs, never a bare no and never a retired task: calibration from the
reserve (section 6); a deepening with one real user need on the seam that brings a decision the runs got wrong (a
second entry path the repo documents, a reader of saved state, a caller context the repo has, the neighbour of a
stated exception; never an invented trap, an undiscoverable corner, a timing race or a contract over every lifecycle
event; the widened promise needs a new sample, Scope Gate and lock); the hunt's runner-up seam; a redesign. Anything
else continues.

## 6. Calibration reserve (recorded at stage 0, refined at stage 4, used at stage 8)
At least 3 fair decision points from section 1 (wrong-by-default decisions or spread points), each with: the input,
the expected output, its grounding (sentence words or repo file:line) and the probe that runs it on a patch. The
reserve lists probes; it never withholds a test a required consequence needs (description.md R8). After the first
rollout, run every probe on every passer before any other calibration lever (rollout.md step 1); a split is the
first candidate for prompts/calibrate-one-passer.md. Before a reserve row becomes a test, run it on the clean
repository, the reference, its wrong version and every real agent solution: add only rows every strong run passes,
and fold a row that passes on the clean repository into a leaf led by one that fails there.

## 7. Signals that the plan failed (report to the owner, then route by rollout.md)
- A rollout where every passer gives the same output on every reserve probe: the seam had no spread; name it in the
  retro and note which inventory row or run should have shown it.
- One assertion carries the band (removing it lifts a family above 25%): flag it before the re-eval paste
  (unused-suppression rested on one line).
- A passing Orion run under 256K: the design is right and the length is not; no test change fixes it. The options
  are the owner's: a description change that adds the missing layer (fresh rollout) or more Orion runs (the average
  of the passing runs must clear the bar). Record which stage-0 estimate was wrong.
- The spike passed and the platform runs stay short: the local stand-in over-read; lower the trust in the estimate
  for that repository and record the hosted fingerprint (tools/scout/).
