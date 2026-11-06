# FLOW: one task, about 2 hours

Keep `flow-status.md` (from `templates/`) current at every gate; always continue at the first stage not DONE.
Long jobs (Docker, Codex) run in the background. A stage 50% over its box means the scope is too wide: cut, don't grind.

| Stage | Box | Do | Gate |
|---|---|---|---|
| S0 Pick | 15 min (+ hunt) | user gave a repo -> `tools/hunt.sh` + in-process lane, automatic pick (`references/hunt.md`); else a seam from the seam bank; `base/` + `repo/` at the upstream tip | novel, offline-testable, 2-4 production files, 1-2 hard points with 3-4 stated consequences |
| S0b Dockerfile | 15 min + user | **Dockerfile first, before every other stage (user rule 2026-11-06).** Preflight (1 min): start from the repo's accepted Dockerfile and the memory notes (dockerfile-no-test-run, <repo>-dockerfile-accepted), compare the go.mod / runtime version with the base image's (`docker run <base> go version`); `precheck.py` Dockerfile lines 0 FAIL (no test runner in any RUN, pinned toolchain, literal versioned URLs) and no comments in the Dockerfile (user rule 2026-11-06); build it ONCE locally with `proof.py base pkg --build-only` (build + one base run; the image is then reused by Dockerfile + commit hash). Create the challenge (`problems create`) and paste ONLY the Dockerfile; **the user builds it on the platform** (Dockerfile guidelines + rebuild-safe). Local speed-ups never change the Dockerfile itself: the platform builds the full file from scratch | user's platform build PASS -> Dockerfile LOCKED (a later change repeats this gate) |
| S1 Design + description | 45 min + user | **references/description-playbook.md section 3, in this order (user rule 2026-11-07):** **A. I scan before the user sees the draft**: facts list (5-8 tested outcomes, code path + natural wrong implementation each), variant table (inventory IN/OUT, run base for OUT), draft from the three sentence kinds (outcome, scope, anchor; no direction, corner list, excuse, meta-instruction), word-reach grep per key word, reading audit x2 (Codex + Claude), DQ replica count, precheck.py, checklist section 4. **B. The user humanizes** the scanned draft in their own words. **C. I re-check the user's text**: behaviour diff (every tested case, every pronoun/connective/qualifier), word-reach + reading check on every changed word, DQ replica + precheck again; misses go back to the user to fix in their words | all of A and C clean -> **LOCK together with the user** (hash in flow-status), then start `tools/solvers.sh <task>` in the background |
| S1b Sample | 30 min + user | every task: paste the locked description + the REAL test.patch (S3 tests, one per sentence, through public entry points) + a stub solution.patch (`references/platform.md` P1); the user runs prechecks, and only when every precheck passes the Scope Gate (the platform locks it until then; "Problem and tests are good quality" FAILS on stub tests, vet 2026-11-06); never DQ/Task Quality on the sample; local check = precheck + ONE run of test.sh new on base in the image built at S0b (patch applies, each new test fails for its reason); the sample carries the S0b-locked Dockerfile unchanged | prechecks all PASS, then Scope Gate PASS (a reject ends the task) |
| S2 Reference | 35 min | smallest design meeting every sentence on every IN path; sweeps (`references/solution.md`) | repo lint/type clean right away; every hunk maps to a sentence |
| S3 Tests + harness | 30 min | real framework objects, network faked at the edge; two-sided boundary tests; test.sh + Dockerfile from `templates/accepted/` | `tests_lint.py` 0 FAIL right away; each test fails on base for its intended reason |
| S4 Gates | 15 min | `precheck.py`, `tests_lint.py`, `proof.py base pkg` (add `--stability` once before the first paste), batteries (>= 3 valid, 1 wrong per sentence), grade the 4 solves with `replay_patches.sh` (too-easy alarm) | 0 FAIL, REVIEW lines justified, PROOF PASS, batteries as expected, solver rule below -> **FINAL LOCK** of the description |
| S5 Sweep 1 (subagent round, all files; the 4 olympus-* subagents run in their OLYMPUS-FLOW SWEEP MODE section, updated 2026-11-06) | 40 min | `tools/sweep.sh <task> s1` (claude2 olympus-auto-reviewer + olympus-sq-judge, 2 GPT Sol 6.1 HIGH ref-audit) AND at the same time in-process Agent lanes olympus-auto-reviewer + olympus-tq-judge, all on `replicas/sweep-brief.md` (complete table per sentence: every path, every wrong implementation that passes, the test that fails it). NO platform-style replica check here. Merge, reproduce, fix EVERY finding in one batch, prove each new test with a battery variant | every GAP / REFERENCE-BROKEN / UNFAIR fixed |
| S5b Sweep 2 (fresh scan after the fixes) | 40 min | `tools/sweep.sh <task> s2` + the in-process lanes again, on the fixed files; fix every finding in one batch, battery. NO gate run | every finding fixed |
| S5c Solves graded + auditor findings closed | 30 min | `tools/solve_watch.py <task>` first (solvers.sh runs it at the end): only CLEAN solves count, a SUSPICIOUS one (a tool call outside its clone, the task text and the repo) is discarded and re-run; grade the CLEAN solves (launched at the S1 lock); strict FP audit on EVERY passer (`replica.sh <task> fp-audit`, GPT Sol 6.1 HIGH, 2 auditors); close every finding (test or fix). A reproduced NOT_DESERVED pass = a test hole: add the smallest test on a stated sentence, prove it in the battery (reference passes, the passer fails as a new variant, every fair passer still passes, every old variant keeps its result), then the next sweep (S5/S5b, or S6b) checks the new test for fairness and T1-T8 / S1-S4 like every other test | every passer DESERVED, every finding closed |
| S6 Fix + re-run | 15 min each | reproduce each finding, fix in one batch, re-run only checks that read the changed file | every check's latest result clean |
| S6b Pre-hand-over safety net (REQUIRED before every final hand-over; user rule 2026-11-06) | 60 min | 1 sweep (`sweep.sh <task> s3` + in-process lanes) + 2 gate runs (`tools/round.sh <task> g1`, `g2`: the ONLY platform-style replica checks in the flow) + strict FP audit on every solver passer (fp-audit x2, HIGH). Fix every finding. A finding the sweeps missed means a gap in the sweep brief: add that path type to `replicas/sweep-brief.md` in the same batch, so the next task's sweep catches it | 0 open findings; sweep-brief updated for every miss |
| S7 Freeze | 15 min | `proof.py base pkg` on the final files (the ONE full proof after S4; image reused; `--stability` before the first paste), then copy `pkg/` to `wipNN/`, record hashes | PROOF PASS on the frozen files |
| S8 Paste | 5 min | `problems create/edit` only; then `problems download` and diff against the wip (catches mixed or stale pastes); start `tools/watch.sh` (the user runs checks and rollouts) | downloaded files byte-identical to the wip |
| S9 Platform findings | per round | watcher wakes -> `pull.sh` -> reproduce -> fix the class -> S4-S6 -> re-paste; after a rollout: `pull.sh --runs` into `<task>/runs/`, then `replica.sh <task> fp-audit` (audits every passer) | - |

## Rules that bound the work
- **When stuck, read references/stuck-prompts.md first:** the prompts that already found the right path (the user's and
  past tasks'), per situation. Ask that question of yourself before choosing a fix path.
- **Solves:** one batch per description lock, started at the lock in the background, never blocking a stage; no local
  re-run after the lock (rollouts measure). `stop_solves.sh` must leave 0 processes of the solve clones (check it).
- **Ready to paste** = every check's latest result is clean on the exact files. Never paste a failing gate.
- **Re-run only what reads the changed file:** solution.patch -> battery (valid rows), SQ x2, AR, verify; test.patch ->
  battery, fairness, AR, verify; Dockerfile -> proof. Between S4 and S7 a fix gets the battery only, never `proof.py`
  (user 2026-11-06): the battery already runs the reference on the new tests in the task image and its cheat row shows
  them failing without a solution; the full proof (base mode, uid + env -i, timing, two identical runs) runs once at S7.
  Battery = incremental: the reference, valid rows and fair passers on every script, plus only the wrong variants of
  the changed scripts; the whole battery once at S7 with the proof. The description is locked (situations D-LATE before the
  first paste only).
- **Caps:** two sweeps (S5, S5b) per version, then the S6b safety net (1 sweep + gate runs g1, g2) before each hand-over;
  a finding still open after that means the scope is too wide: cut or narrow it. A tests
  gap is fixed for its whole class at once: the same kind of gap checked against every sentence, not only the one
  named (vet: one narrow gap per round for 7 rounds came from per-instance fixes). Kept Mediums do not block the gate:
  after the last round they are fixed with a targeted re-run of the checks that read the changed file, not a new round. At most
  2 platform fix rounds per task (a 3rd means stop and report to the user).
- **Docker: full control + disk hygiene (user rule 2026-11-06):** I restart, prune and compact Docker myself. Before
  every image build and at task end keep C: >= 20 GB free: keep only the current task image and the olympus base
  images, `docker builder prune -af`, then trim + diskpart compact docker_data.vhdx (one UAC click). At most 2
  containers at once. At task end delete solver clones and old task repos/bases/zips; keep only learning files.
- **Coordinator triage of every subagent finding (user rule 2026-11-06):** accept a finding only if (1) it ties to a
  quoted sentence with one reading, (2) the wrong implementation is plausible for a real solver, (3) the test stays
  discoverable (no hidden corner), (4) it needs no description change or new requirement, (5) a solution change fixes
  a stated promise (no refactor or hardening beyond the text). Every finding gets a row in eval/triage-<round>.md:
  ACCEPT or REJECT with the reason. Findings that would make the task more complicated without a stated promise are
  rejected.
- **Nothing stays open on a guess (user rule 2026-11-06):** every candidate a check names (gap, wrong implementation,
  untested path) is checked in the same session with a probe on base and on the reference; it becomes a test, a fix
  or a recorded "probed: not reachable / behaves as stated" with the probe log. Open only when truly blocked, with the
  reason and the next step. Strict audits (fp-audit, ref-audit) run on GPT Sol 6.1 HIGH.
- **Every finding:** reproduce first; reproduced and inside a stated promise -> fix (never keep); outside every
  sentence -> no change; not reproduced -> contest note, no change. Mediums are fixed too (cheap).

## Too-easy alarm (4 local solves, an alarm only, never a prediction)
Launched at the S1 lock (2 Opus: this account + claude2; 2 GPT Sol 6.1 via Codex), they run while I build; graded at
S4 against the hidden tests. Between the draft lock (S1) and the final lock (S4) the description may change for
these two alarms only, one sentence each, before the first paste:
- 3-4 of 4 pass everything -> too easy: add one more stated consequence of the SAME rule (+1 unit, stay <= 14).
- 0 of 4, all failing the same stated consequence -> make that consequence discoverable: state it as a plain
  observable outcome in exact words ("greater than or equal to that time", "the whole app should fail"), never as
  mechanism or a hint; or scope it out if it needs an unrelated non-obvious base fix.
- anything else -> no change; never tune the task to a local number.
Each change: I draft the one sentence, the user rewrites it in their own words, then precheck, the DQ replica and the
fairness replica re-run, and the tests are re-checked against the new text. After the final lock nothing changes. Side benefits: a correct-looking
solve failing one test points to an unfair test; passing and failing solves join the S4 batteries.

## Where the detail lives
Problem choice: `references/problem-design.md`. Text: `references/description.md`. Reference: `references/solution.md`.
Tests and harness: `references/tests-harness.md`. Checks: `references/checks.md`. Platform: `references/platform.md`.
Any failure: `references/situations.md` (one row, one action).
