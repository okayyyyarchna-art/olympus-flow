# Difficulty: measure the seam before the build (stages 0, 2, 3, 8)

Why (retro of 12 tasks, olympus-product/analysis-20261112/synthesis.md): only one task was hard on its first suite.
The others reached the band through calibration: their passers differed on one decision, and one fair test on that
decision did the rest. vet direct-deps could not be calibrated: the repo made every decision for the agents, and its
14 passers behaved the same. So the aim is a task that **can be calibrated**, not one that is hard on its first suite.

The gate is measured, never read: the obvious-design spike (section 3) and the stage-3 runs (section 4). A reading
verdict was tried and failed a blind test (2026-11-12, analysis-20261112/blind/): fresh readers rated all five seams
hard, the known-easy direct-deps included, because a strong agent reads the code next to a misleading idiom and a
reader cannot tell how far "next to" reaches. The same readers found the real separators of elio and
table-visibility blind, so the inventory stays, as the generator of planned separators and the reserve.

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
  contested (blind test: the swift reader found all three decisive cases and set them aside).

**Per decision, one row:** the nearest repo idiom or helper (file:line), what it would decide, right or wrong for the
requirement (with one input where the two differ), the kind below (or none), the fair route that makes it gradable (a
sentence the text will need, or a repo line), and where the right answer sits (same file as the wrong idiom, or far).

| Kind | What it looks like | Examples |
|---|---|---|
| K1 misleading nearby idiom or helper | copying the nearest code gives the wrong answer; the right helper sits far away | topic-start `int(ts*1000.0)`; standby `_changelog_topic_name()`; unused-suppression `Header.Controls` |
| K2 caller-context branch | the same API behaves differently by caller state | live-readers handler inside the rebalance window; table-visibility read during an event |
| K3 second path or shortcut | a path that skips the shared site | local-registry PR previous version; swift multipart re-send; elio Duplicate Finder rename |
| K4 intermediate semantics | a step inside one site changes the value first | turso UNION dedups 1 and 1.0 before the TEXT compare |
| K5 identity or timing | which object, at which moment | docker symlink resolved at write time; elio stale-token guard |
| K6 exception neighbour | the state next to an exception is not the exception | vet unknown control id vs turned off; swift rollback delete fails |

The builder opens every cited line before trusting a row; a claim that does not hold is dropped. The rows become the
planned separators that V-OBVIOUS is run against (section 3) and the calibration reserve (section 5). Rows where the
right answer sits far from the wrong idiom, or where no helper exists, are the best separators (a right helper in
the same file is found by strong agents: direct-deps PathFrom and MayReach beside PathTo).
Planning rate (optional, for the owner): per family, the product of its profiles.md rates over the unstated rows;
never a gate and never a reason to change the text.

## 2. Order when a seam is too easy: runner-up first, widen last
The spike (section 3) decides; the order is fixed by the owner (2026-11-12):
1. The top candidate fails the spike -> the hunt's runner-up: its own sample and Scope Gate (stage 1b), stage 2 steps
   1-3, its own spike. The Dockerfile and image usually carry over on the same repository.
2. The runner-up fails too -> widen once (45 minutes) the one of the two with the better chance, judged by: the
   spike failed on one decision rather than none; the inventory holds an unused far-from-the-idiom or no-helper row
   that is a real user need; the smaller breadth after widening.
3. **Widen:** add one real user need on that seam that brings a decision the spike gets wrong: a second entry path the
   repo documents (saved file, second command, base side of a comparison), a reader of saved state, a caller context
   the repo has, the neighbour of a stated exception, a second kind of the same object. Never an invented trap, an
   undiscoverable corner, a timing race or a contract over every lifecycle event (problem-design.md section 4). Keep
   the breadth cap: one deep rule plus at most one neighbour family (live-readers' ~20 corners cost 61 wips). The
   widened promise changes the sample: paste it again before the lock and the owner re-runs the Scope Gate (R14).
   Then run the spike again.
4. The widened seam fails the spike -> stop and give the owner the options (a new hunt, a redesign), never a bare no.

## 3. Obvious-design spike (stage 2 step 3, before the lock): the first gate
Write V-OBVIOUS: the solution a strong agent writes from the requirement with the nearest helpers and the sibling
code, complete and self-tested (a naive spike over-rated standby). Run it on the planned tests built from the section
1 rows (eval/variants.py).
- It must fail on at least two different decisions (owner 2026-11-12: kept strict until tasks become hard to find);
  two test cases of one decision count once. If it fails on fewer (direct-deps V11 passed 35/35, dev-only 9/9): stop
  before the lock and follow section 2. The spike is step 3, before the variant table, draft and reading audits, so
  a fail here loses stage 0 and steps 1-3 only.
- Persistence probe: for each decision that touches saved state, check whether the base already saves what the
  feature needs (direct-deps: findings already carried engine facts, so the saved scan came free).
- Global property: when the obvious design loops, retries or frees resources, fuzz it for termination and duplicates
  (standby's livelock was found only after the first rollout).

## 4. The stage-3 runs: the second gate and the builder's picture of the agents (the owner runs them)
Right after the lock, paste the locked text with the sample tests (no run or check active) and notify the owner. The
owner runs **2 Orion + 2 Vega**. They are for the builder: how the platform agents read this exact text and which
designs they build, so the tests are shaped once, before the only full paste. The text never changes after the lock,
so the four runs also count toward the final rollout (re-evaluated on v1). Never change the Dockerfile after them
(it would lose their re-eval). The builder keeps building locally while they run; nothing is pasted until they end.

When they finish:
1. Pull them; replay every patch on the planned tests, V-OBVIOUS's separators and the reserve probes.
2. **Stop signal:** all four give the same output on every separator and probe and pass them all (zero spread, as on
   direct-deps): stop before v1 and give the owner the options in the section 2 order (the runner-up if not
   tried, then widen once, then a new hunt or a redesign). Anything else continues.
3. **Keeper:** the best run that is correct, confirmed by an FP audit with probes replayed on the reference. The
   suite is built so the keeper and the reference pass it and every other design fails on a fair case: each gap in
   the other three runs, V-OBVIOUS, the variants and the reserve gets a fair test (a stated sentence or a repo line
   at the assertion, never a case invented to reject one run). The aim is one passer in the final 4-4-4. With no
   correct run there is no keeper: the tests still close every gap, and the band comes from the new runs.
4. Every gap a run showed is also a design a new run may take, so it goes into the variant corpus (must fail).

## 5. Calibration reserve (recorded at stage 0, refined at stage 4, used at stage 8)
At least 3 fair decision points from section 1 (wrong-by-default decisions or spread points), each with: the input,
the expected output, its grounding (sentence words or repo file:line) and the probe that runs it on a patch. The
reserve lists probes; it never withholds a test a required consequence needs (description.md R8). After the first
rollout, run every probe on every passer before any other calibration lever (rollout.md step 1); a split is the
first candidate for prompts/calibrate-one-passer.md.

## 6. Signals that the plan failed (report to the owner, then route by rollout.md)
- A rollout where every passer gives the same output on every reserve probe: the seam had no spread; name it in the
  retro and note which inventory row or spike case should have shown it.
- One assertion carries the band (removing it lifts a family above 25%): flag it before the re-eval paste
  (unused-suppression rested on one line).
