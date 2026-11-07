# Platform work through the Olympus CLI (stages 1, 1b, 6b, 7b, 8b, 10)

**I paste, the owner runs.** I create or edit the draft (`problems create`, `problems edit` with the four files,
title, category, repo, commit) and confirm the fields with `problems view` and a download. I never run
`checks run`, `checks run-all`, `checks run-prechecks`, `runs run`, `problems lock`, `problems submit` or
`problems version create`; the owner runs those and decides their order and the rollout mix. I read results only
with the read-only commands and `tools/pull.sh`.

CLI: `@shipd-ai/olympus-cli` (`olympus`), credentials in `~/.shipd/olympus/`. Always `export OLYMPUS_NO_UPDATE_CHECK=1`;
strip `\r` from ids on Windows; run `--help` before a command you have not used. `olympus auth status` before
starting (login is the one physical step). Arguments: `runs artifact <challenge-id> <run> --key <key>`.

| Command | Effect |
|---|---|
| `problems mine/view/download`, `problems version list`, `checks view`, `runs view/show/artifact`, `tools/pull.sh` | read only |
| `problems create`, `problems edit`, `problems version create`, `checks run-prechecks` | change the draft |
| `checks run <key>`, `checks run-all` | spend revision tokens (SQ 2.5, TQ 1.5, DQ 4) |
| `runs run` | spends rollout tokens (a 12-run batch ~80) |
| `problems lock`, `problems submit` | final; only when readiness is all green |

## Pastes and notifications
Pastes happen only at these points, each followed by a push notification and a message to the owner (version,
file hashes, what changed, exactly which checks to run and which runs are still needed):
| Paste | Content | The owner runs |
|---|---|---|
| Dockerfile (stage 1) | Dockerfile only | the platform image build |
| Sample (stage 1b) | my draft words + basic tests + a small solution sketch | prechecks, Scope Gate |
| v1 (stage 6b) | the checklist-built package | the checks, the calibration rollout (their mix, usually 3 Orion + 3 Vega) |
| v2 (stage 7b) | all stage-7 fixes in one version | only the affected checks; re-eval |
| v3 (stage 8b) | rollout shaping, predicted by a local replay | affected checks, re-eval, runs to reach 4+ per family (Nova included) |
No watcher by default: the owner says when results are in. `tools/watch.sh` exists for when the owner asks for it.
Every result is read against the version it graded: a check that ran on an older paste says nothing about the
current files.

## Sample and Scope Gate (stage 1b)
The Scope Gate unlocks only after every precheck passes, and the AI precheck fails a stub test patch ("Tests cover
required behavior [ERROR]", vet 2026-11-06). So the sample carries basic real tests: one plain test per sentence in
the repo's own test style, an executable test.sh, a small solution sketch; nothing is verified. A WARN on "only
necessary information" is normal. A Scope Gate reject ends the candidate (never reword and retry: RIE was rejected
twice). Every later paste marks the Scope Gate stale; the owner re-runs it on the final package.
Title: the problem in user words ("Topics can choose where reading starts without a committed offset").

## Reading check results (after the owner's runs)
`tools/pull.sh <id> eval/platform/<round> [--runs]`. Read in this order: verifyBuild/Tests/Solution/Flakiness,
verifyFairness, taskQuality, solutionQuality, descriptionQuality, autoReview (bands, issues, authorGuidance), then
readiness ("repository verification expired" = the owner re-runs prechecks right before submit; "Rebuild-safe" and
"Harbor rebuild-safe" must pass; "image failed to rebuild from your committed source" = re-base onto the tip).
Platform verdicts vary run to run (vet SQ: 2/3 then 3/3 on the same files): act on findings that reproduce and on
every High. Keep `eval/platform-ledger.md`: one row per finding (check, quote, real/misread, fix, next result).
Local vs platform: put each platform verdict next to our replica verdict for the same files in
`eval/platform/compare.md`; a mismatch names the failing layer (generator never looked, verify dropped it, pattern
unknown, depth) and is fixed as a general rule in replicas/ (replicas/CALIBRATION.md has the method).

## Rollout results (stage 8)
`tools/pull.sh <id> <dir> --runs` saves per run the verdict, the patch, `testlog.txt` and `failures.txt` (Go and
testscript failure lines first). Read every run's verdict, fault and environment blocker before any conclusion,
classify every run, then shape with rollout.md. After a test change, plan the replay with
`tools/lib/replay_plan.py <old test.patch> <new test.patch> <dir>/runs --stage <patches-dir>` (SKIP / LINE? /
REPLAY per run) and replay only the staged patches with `tools/lib/replay_patches.sh`; the re-eval of the same
description and Dockerfile re-runs the same patches, so the replay predicts it exactly.
FP audit: one per passing run (`tools/replica.sh <task> fp-audit`), a second only when the first says NOT_DESERVED
or is unclear; each probe is replayed on the reference too. The platform's FP panel notes are shown only in the web
UI: pull.sh says when to ask the owner to paste them.
Gate (platform text): exactly one family in (0, 25%], the other two at 0; >= 4 runs each; Nova average > 400K
sequence length; cheat rate < 20%; no environment blockers; passers hold under the FP panel.

## Submit (stage 10)
Readiness all pass (prechecks incl. fresh repository verification, Scope Gate, 7/7 quality checks, Auto Review,
Rebuild-safe, Harbor rebuild-safe, every rollout criterion; an FP "warn: passed with caveats" does not block). The
owner locks and submits. Record the final hashes in the ledger.
