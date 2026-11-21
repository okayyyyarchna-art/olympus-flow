# Platform work through the Olympus CLI (stages 1, 1b, 3, 7b, 8b, 10)

**I paste, the owner runs.** I create or edit the draft (`problems create`, `problems edit` with the four files,
title, category, repo, commit) and confirm the fields with `problems view` and a download. I never run
`checks run`, `checks run-all`, `checks run-prechecks`, `runs run`, `problems lock`, `problems submit` or
`problems version create`; the owner runs those and decides their order and the rollout mix. I read results only
with the read-only commands and `tools/pull.sh`.

CLI: `@shipd-ai/olympus-cli` (`olympus`), credentials in `~/.shipd/olympus/`. Always `export OLYMPUS_NO_UPDATE_CHECK=1`;
strip `\r` from ids on Windows; run `--help` before a command you have not used. `olympus auth status` before
starting (login is the one physical step; it expires: `NoAuthProvider` means the owner logs in again, and until then
the owner pastes and downloads for me). Arguments: `runs artifact <challenge-id> <run> --key <key>`.

| Command | Effect |
|---|---|
| `problems mine/view/download`, `problems version list`, `checks view`, `runs view/show/artifact`, `tools/pull.sh` | read only |
| `problems create`, `problems edit` (every paste of mine is a `problems edit` of the draft) | change the draft |
| `problems version create`, `checks run-prechecks` | change the draft; the owner's |
| `checks run <key>`, `checks run-all` | spend revision tokens (SQ 2.5, TQ 1.5, DQ 4) |
| `runs run` | spends rollout tokens (a 12-run batch ~80) |
| `problems lock`, `problems submit` | final; only when readiness is all green |

Tokens drip hourly by tier. Refunds cover infrastructure failures only. If real source lives under build/, dist/ or
target/, list those protected folders for the FP check. A contributor may submit at most 12 tasks per repository. A
draft is reserved for its creator for 14 days after creation (`reservedForUserId`, `reservationExpiresAt`). When
`problems create` answers "Submission creation is paused", build ahead locally (stages 2 and 4-7 need no draft; the
spike and the audits run locally), retry at each paste point, and tell the owner once.

## Rollout criteria (platform text, read from `problems view --json` on 2026-11-21; `runs.criteria.criteria[]`)
| Key | Platform description |
|---|---|
| fair | No agent run flagged the task as unfair or broken |
| solvable | At least 1 agent run must solve the problem |
| codenameCoverage | At least 4 runs must complete on each of Nova, Orion and Vega |
| novaUnsolved | Nova must stay at 0% over at least 4 runs |
| passStructure | Orion solves it in at least one run and at most 25% of runs |
| vegaPassRate | Vega solves it in at most 25% of runs |
| passSequenceLength | Orion's solving runs must average at least 256K tokens of sequence length |
| noCheating | Cheat rate must be below 20% (across all agents) |
| noEnvBlocker | No run should be blocked by environment or verifier issues |
Agents (`aggStats.byModel`, `runs.agentRuns[].taskAgentCodename/taskAgentType`): Orion = `codex_cli` on GPT Sol 6.1
(xhigh), Vega = `claude_code` on Claude Opus 5.5, Nova = `gemini_cli` (model read from its first run); each run is
graded by an evaluator agent (verdict such as `FAIL_MISSED_REQUIREMENT`, `FAIL_TEST_BROKEN`, `PASS_LEGITIMATE`,
`PASS_CHEATED`) and carries `output.sequenceLength`, `output.compacted`, `output.environmentBlocker`, `fault`,
`hinted`. Re-read the models after every rollout: they have changed without notice.

Quality checks (`checks.dynamicChecks`): descriptionQuality (Task Prompt Quality), verifyTests, verifySolution,
verifyFlakiness, rewardHacking, categoryAlignment, solutionQuality, verifyFairness (Test Quality), taskQuality (the
eight task criteria: authentic engineering, presentation, clarity, fairness, bounded scope, nontriviality, objective
verification, long-horizon); the cards use the platform's own names in that mapping; each
may be overridden by the platform (`_<check>Overridden`). Readiness (`checks.readiness`): `canSubmit`, `criteria`,
`cooldownAppliesToProblem`, `trialQa`. Auto Review is no longer a readiness item (2026-11-17); its report still
exists and mirrors Solution Quality, so a reproducing Medium there comes back as an SQ note. `trialQa` is a readiness
item whose procedure we have not seen yet: when the owner runs it, record what it asks and what it checks, and add it
here.

## Pastes and notifications
Pastes happen only at these points, each followed by a push notification and a message to the owner (version,
file hashes, what changed, exactly which checks to run in which order, and which runs are still needed):
| Paste | Content | The owner runs |
|---|---|---|
| Dockerfile (stage 1) | Dockerfile only | the platform image build |
| Sample (stage 1b) | my draft words + basic tests + a small solution sketch | prechecks, Scope Gate |
| Locked text (stage 3) | the locked description + the sample tests | 2 Orion + 2 Vega, in parallel with 3 + 3 local solves (difficulty.md section 3); they count toward the 4-4-4 |
| v1 (stage 7b) | the complete package after stage 7 | the checks once in the order below, the re-eval of the four stage-3 runs, 2 Orion + 2 Vega + 4 Nova |
| v2 (stage 8b), only when needed | calibration, predicted by a local replay, after one replica round | the checks it reopens, re-eval (no new runs) |
Before every paste and every status claim about a check, pull the platform state (`tools/pull.sh`): vet task 2 pasted
over a finished re-eval and left about 5 h of results unread. After each paste, start `tools/watch.sh <id> <task>` as a
tracked background job with a fresh baseline so a finished check wakes the builder; it only reads, and the owner still
decides what runs. Every result is read against the version it graded: a check that ran on an older paste says
nothing about the current files (PIPELINE.md, Version bookkeeping).

**Check order after a paste** (owner 2026-11-19/20): prechecks and Scope Gate, Task Prompt Quality, Verify Tests,
Verify Solution, Verify Flakiness, Reward Hacking, Category Alignment, Solution Quality, Test Quality last (a
test.patch edit stales the others). Each paid round samples a new reviewer: a pass is a sample, not a proof; the
executed closure (tq-once.md, sq-once.md) is the proof.

v1 is the complete package: the owner runs the full checks once, not per paste. If a check blocks it, reproduce each
item first (a kept wrong version or an executed input), then fix the whole class once; contest honestly only what does
not reproduce, one note per finding: the quote plus a code trace. Local refinement goes on meanwhile.

## Sample and Scope Gate (stage 1b)
The Scope Gate unlocks only after every precheck passes, and the AI precheck fails a stub test patch ("Tests cover
required behavior [ERROR]"). So the sample carries basic real tests: one plain test per sentence in the repo's own
test style, an executable test.sh whose new mode was run once on base and once on the sketch, a small solution
sketch; nothing else is verified. A WARN on "only necessary information" is normal. A Scope Gate reject ends the
candidate (never reword and retry: RIE was rejected twice). Every later paste marks the Scope Gate stale; the owner
re-runs it on the final package. Title: the problem in user words ("Topics can choose where reading starts without a
committed offset").

## Reading check results (after the owner's runs)
`tools/pull.sh <id> eval/platform/<round> [--runs]`. Read in this order: verifyBuild/Tests/Solution/Flakiness,
rewardHacking, categoryAlignment, solutionQuality, verifyFairness, descriptionQuality, taskQuality, autoReview
(advisory), then readiness ("repository verification expired" = the owner re-runs prechecks right before submit;
"Rebuild-safe" and "Harbor rebuild-safe" must pass; "image failed to rebuild from your committed source" = re-base
onto the tip; harborSafe "rebuild it so the hygiene layer applies" = a new image build by the owner).
What each blocking check does today (replicas/ reproduce them):
- Test Quality: runs the hidden tests without the solution, infers the solution's shape, writes realistic wrong
  solutions, blocks on a gap (a wrong solution passes every test) or an unfair test (a correct one fails); a wrong
  solution is wrong by the description, the behaviour before the change, or a documented repository contract. Code
  quality notes are not blocking.
- Solution Quality: builds an input repository, runs the tool, blocks on a wrong output (Input / Command / Expected /
  Received / Why / Suggested change) or a measured slowdown of the normal path; everything else is a Design, Clutter or
  Practice note that repeats until fixed or declined in writing.
- Verify Flakiness: runs the suite about 12 times; an upstream test with an upper wall-clock bound fails it on its own.
- Verify Solution: root baseline, then solution.patch applied as uid 1000 in /app; compares test sets (baseline
  failures, new not passing, new also in baseline, after extras not skipped, pass-to-pass not passing after); its
  Harbor oracle calls `test.sh` with `[--output_path F] [--mode] <base|new>` and parses text output; `/app` must be
  writable for every user.
Platform verdicts vary run to run (vet SQ: 2/3 then 3/3 on the same files): act on findings that reproduce and on
every blocking item. Keep `eval/platform-ledger.md`: one row per finding (check, version hash, quote, real/misread,
fix, next result). Do not forecast Requirement Coverage x/y: the platform re-splits requirements per run. Triage every
note in the ledger with a reason: fix it when free; otherwise decline with a written reason the next round copies.
Local vs platform: put each platform verdict next to our replica verdict for the same files in
`eval/platform/compare.md`; a mismatch names the failing layer (generator never looked, verify dropped it, pattern
unknown, depth) and is fixed as a general rule in replicas/ (replicas/CALIBRATION.md has the method).

## Rollout results (stage 8)
`tools/pull.sh <id> <dir> --runs` saves per run the verdict, the patch, `testlog.txt` and `failures.txt` (Go and
testscript failure lines first). When the CLI is down, the owner downloads each run's zip: a folder per run with
`run.txt`, `junit-new.xml`, `eval-result.json`, `solution-patch.patch`, `trajectory.json`; `tools/rollout_report.py`
reads both layouts. Read every run's verdict, fault, environment blocker, sequence length and compaction before any
conclusion, classify every run, then shape with rollout.md. After a test change, plan the replay with
`tools/lib/replay_plan.py <old test.patch> <new test.patch> <dir>/runs --stage <patches-dir>` (SKIP / LINE? /
REPLAY per run) and replay only the staged patches with `tools/lib/replay_patches.sh`; the re-eval of the same
description and Dockerfile re-runs the same patches, so the replay predicts it, except where the platform's sandbox
differs (link resolution on vet 6): the platform junit is the truth for a run.
FP audit: one per passing run (`tools/replica.sh <task> fp-audit`), a second only when the first says NOT_DESERVED
or is unclear; each probe is replayed on the reference too. The platform's FP panel notes are shown only in the web
UI: pull.sh says when to ask the owner to paste them. The panel never sees the Auto Review, SQ or TQ reports, so an
approving note is no evidence for a passer: predict FP only from the description, the tests and the patch.

## Submit (stage 10)
Readiness all pass (prechecks incl. fresh repository verification, Scope Gate, every quality check, Rebuild-safe,
Harbor rebuild-safe, every rollout criterion, Trial QA; an FP "warn: passed with caveats" does not block). The
owner locks and submits. Record the final hashes in the ledger.
