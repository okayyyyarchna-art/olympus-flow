# Platform work through the Olympus CLI (stages 1, 1b, 3, 7b, 8b, 10)

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

Tokens drip hourly by tier (Iron 4 per hour when recorded). Refunds cover infrastructure failures only. If real source
lives under build/, dist/ or target/, list those protected folders for the FP check. A contributor may submit at most
12 tasks per repository.

## Pastes and notifications
Pastes happen only at these points, each followed by a push notification and a message to the owner (version,
file hashes, what changed, exactly which checks to run and which runs are still needed):
| Paste | Content | The owner runs |
|---|---|---|
| Dockerfile (stage 1) | Dockerfile only | the platform image build |
| Sample (stage 1b) | my draft words + basic tests + a small solution sketch | prechecks, Scope Gate |
| Locked text (stage 3) | the locked description + the sample tests | 2 Orion + 2 Vega, for the builder's picture of the agents (difficulty.md section 4); they count toward the 4-4-4 |
| v1 (stage 7b) | the complete package after stage 7, shaped on the stage-3 runs | the full checks once, the re-eval of the four stage-3 runs, 2 Orion + 2 Vega + 4 Nova |
| v2 (stage 8b), only when needed | calibration, predicted by a local replay, after one replica round | the affected checks, re-eval (no new runs) |
Before every paste and every status claim about a check, pull the platform state (`tools/pull.sh`): vet task 2 pasted
over a finished re-eval and left about 5 h of results unread. After each paste, start `tools/watch.sh <id> <task>` as a
tracked background job so a finished check wakes the builder; it only reads, and the owner still decides what runs.
Every result is read against the version it graded: a check that ran on an older paste says nothing about the
current files.

v1 is the complete package: the owner runs the full checks once, not per paste (owner 2026-11-12). If a check blocks it,
contest it honestly, one note per finding: the quote plus a code trace, or "fixed in the next version, file:line". Local
refinement goes on meanwhile.

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
Do not forecast Requirement Coverage x/y: the platform re-splits requirements per run. Triage every partial and
suggestion in the ledger with a reason: add it if a realistic wrong design can slip through or a whole stated mode is
untested; add it if it costs no difficulty and a paste is happening anyway; otherwise leave it and say why.
Auto Review mirrors Solution Quality: a reproducing Medium at SQ 2/3 comes back as solution 1/3. Before the reference is
platform-approved, close it when the fix is small. An approval "with reservations" still goes to a human reviewer, so
clear Low notes on the tests and reference too.
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
The FP panel never sees the Auto Review, SQ or TQ reports, so an approving note is no evidence for a passer: predict FP
only from the description, the tests and the patch. Before every rollout, sort the Test Fairness coverage suggestions
into noise and true gaps.
Gate (platform text): exactly one family in (0, 25%], the other two at 0; >= 4 runs each; Nova average > 400K
sequence length; cheat rate < 20%; no environment blockers; passers hold under the FP panel.

## Submit (stage 10)
Readiness all pass (prechecks incl. fresh repository verification, Scope Gate, 7/7 quality checks, Auto Review,
Rebuild-safe, Harbor rebuild-safe, every rollout criterion; an FP "warn: passed with caveats" does not block). The
owner locks and submits. Record the final hashes in the ledger.
