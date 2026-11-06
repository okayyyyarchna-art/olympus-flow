# Platform stage (S8-S9) through the Olympus CLI

**Current rule (user, 2026-11-05): I PASTE, the user RUNS. After the last full local round passes clean I create or
edit the draft (`problems create`, `problems edit` with the four files, title, category, repo, commit) and confirm the
fields with `problems view`. I never run `checks run`, `checks run-all`, `checks run-prechecks`, `runs run`,
`problems lock`, `problems submit` or `problems version create`; the user runs those and decides their order. After
the user's runs I read results with the read-only commands and `tools/pull.sh`.**

**Automatic error pickup:** right after every paste, start `bash tools/watch.sh <id> <task-dir>` in the background
(it exits after each finished batch so I wake up; restart it right after handling the batch until the stage is done)
(read-only, polls every 5 min). It exits when the user's runs have finished something new. If it reports a failure:
`tools/pull.sh <id> eval/platform/<round> --runs`, then the S9 loop below without waiting to be asked (reproduce,
fix the class, re-run only the local checks that read the changed file (FLOW table) until clean, re-paste with
`problems edit`, start the watcher again, tell the user
what changed and that it is ready for their run). Respect the cap: 2 platform fix rounds per task, then stop and
report.

CLI: `@shipd-ai/olympus-cli` (`olympus`), credentials in `~/.shipd/olympus/`. Always `export OLYMPUS_NO_UPDATE_CHECK=1`;
strip `\r` from ids on Windows. `olympus auth status` before starting (login is the one physical step).

| Command | Effect |
|---|---|
| `problems mine/view/download`, `problems version list`, `checks view`, `runs view/show/artifact`, `tools/pull.sh` | read only |
| `problems create`, `problems edit`, `problems version create`, `checks run-prechecks` | change the draft (no token cost recorded) |
| `checks run <key>`, `checks run-all` | spend revision tokens (SQ 2.5, TQ 1.5, DQ 4) |
| `runs run` | spends rollout tokens (a 12-run batch ~80) |
| `problems lock`, `problems submit` | final; only when readiness is all green |

Budget rule: one `checks run-all` per locked version, one rollout batch per version. Everything else is local.

## P1 Draft, prechecks, Scope Gate (ALWAYS right after S1 lock, with stub patches: the sample; user rule 2026-11-05)
Every task gets the sample first, also on a repo that already has a task. I paste; the user runs the prechecks and the
Scope Gate. S2 starts only after the Scope Gate passes. The Scope Gate unlocks only after EVERY precheck passes, and the
AI precheck "Problem and tests are good quality" FAILS a stub test patch (vet 2026-11-06: "Tests cover required
behavior [ERROR]"). So the sample carries the real test.patch (S3 tests, one per sentence; they may fail on base and
with the stub solution) and a stub solution.patch.
```
olympus problems create --title "<title>" --repo <url> --commit <tip sha> --language <lang> --category <bugfix|feature_request> --difficulty hard --json
olympus problems edit <id> --description-file pkg/description.md --test-patch pkg/test.patch --solution-patch pkg/solution.patch --dockerfile pkg/Dockerfile
olympus checks run-prechecks <id>; olympus checks view <id> --json > eval/platform/checks-p1.json
```
Read every precheck line. FAIL -> situations row of that check; a WARN on "only necessary information" is normal
(it fires on every accepted task). Scope Gate status is in readiness (`scopeGate`); a reject ends the task (never
reword and retry: RIE was rejected twice).
Title: the problem in user words (accepted examples: "Topics can choose where reading starts without a committed
offset", "Conditional writes leave refused data behind").

## P2 Quality checks (once per version, after S4-S6 are green)
Order that worked on the other machine (the user decides): Verify Build/Tests/Solution/Flakiness first, then SQ,
then TQ and Task Quality, then DQ and Auto Review. The platform's verdicts vary run to run: running SQ and TQ 2-3
times and acting on findings that repeat (and on any High) was the other machine's practice. Every platform iteration
costs about 150 tokens: spend only on checks that can change a decision.
When reading a result, check it quotes the CURRENT files (results can grade an older paste).
Keep `eval/platform-ledger.md`: one row per platform finding (check, date, quote, real/misread, fix, next result) and
re-verify every row on the new package before the next paste.
`olympus checks run-all <id>` then `olympus checks wait <id>`; pull with `tools/pull.sh <id> eval/platform/p2`.
Read in this order: verifyBuild/Tests/Solution/Flakiness (environment), verifyFairness (requirements + coverage),
taskQuality (8 criteria), solutionQuality, descriptionQuality, autoReview (bands + issues + authorGuidance).
Also check readiness: "repository verification expired" = re-run prechecks right before submit; "Rebuild-safe" and
"Harbor rebuild-safe" must pass ("image failed to rebuild from your committed source" = re-base onto the tip).

Local-vs-platform comparison (every P2, keeps the local checks calibrated): put the platform verdict per check next to
our S5/S6 replica verdict for the SAME files in `eval/platform/compare.md`. For each mismatch:
1. Reproduce the platform finding. If the platform contradicts itself on this package (rerun differs), log only.
2. Name the failing layer: generator never looked (add a procedure step/table), generator found it but verify dropped
   it (fix a verify rule), pattern unknown (add to replicas/knowledge/), depth (raise that one check to Sol 6.1
   high). Fixes are general rules, never task-specific hints.
3. Re-run the changed check on this package AND on two approved controls (no new false High).
4. Two attempts max; then mark a known blind spot in CALIBRATION.md and add an explicit S2 sweep or S4 gate for that
   finding class.
Bar: no missed FAIL verdict, no false High on an approved package; Medium-level differences are tolerated.
Append the case to CALIBRATION.md (package, check, platform vs local, layer, fix).

## P3 Rollout
`olympus runs run <id> --solver nova --evaluator orion --count 4`, same for orion and vega (evaluator: orion; our
accepted tasks used the platform's default pairing, keep the same evaluator for all three batches).
Then `tools/pull.sh <id> eval/platform/p3 --runs`.
Read first, before any conclusion: every run's verdict, `fault`, `environmentBlocker`, and for every FAIL the first
failing tests in `runs/<id>/failures.txt`. Classify each failing run: stated boundary missed (fair) / base test pin
(our harness: deselect) / environment (our Dockerfile/test.sh) / unfair test (several runs converge on one valid design
a test rejects).
Feedback loop (agents improve every week): append to `~/OSS/shipd/seams/boundary-stats.md` one line per boundary of
this task: boundary type, families that got it right / wrong (from failing tests per run and the AR otherNotes on
convergence). problem-design.md section 2 uses these rates (p) to size k for the next task; when a boundary type is
solved by most runs of two families, stop counting it as a boundary.
Gate (exact platform text): exactly one of Nova, Orion, Vega solves it, >0% and <=25%; the other two 0%; >=4 runs
each; Nova average > 400K sequence length; cheat rate < 20%; no environment blockers; passers hold under the FP panel.

## P4 False-pass review of every passer (before the platform panel decides)
For each PASS_LEGITIMATE run: diff its solution against every description sentence (design diff, not test replay).
Prompt: `replicas/fp-audit.md` (`tools/replica.sh <task> fp-audit`, audits every passer in `<task>/runs/`). Lanes: 4 x Sonnet medium
(in-process + claude2, neutral brief) and 1 Codex GPT Sol 6.1 medium. A pass is NOT DESERVED only if
all hold: it breaks a quoted sentence; the input is legal, in scope and realistic; a run reproduces the failure; the
reference gets it right; the sentence has one reading. Then add ONE grounded discriminator test (situations row
FP-1) and re-run the affected checks; this voids that passer, so plan the rollout count with it.

## P5 Submit
Readiness all pass (prechecks incl. fresh repository verification, Scope Gate, 7/7 quality checks, Auto Review,
Rebuild-safe, Harbor rebuild-safe, every rollout criterion). `olympus problems lock <id>` then `olympus problems submit
<id>`. Record the final hashes in flow-status.

## S9 Findings loop (any platform finding, any stage)
1. Pull (`tools/pull.sh`), copy the exact finding text into `eval/decisions.md`.
2. Reproduce: build the failing case (scenario run, wrong variant, or base comparison). Not reproducible -> contest
   with base evidence (the AR has a `runContests` path; the platform accepted a contest backed by repo lines).
3. Find the class: the same defect shape on sibling paths (other modes, other shapes, other lifecycle edges). Fix the
   whole class in one batch (one finding per round cost task 11 seven SQ runs).
4. Deterministic gates (S4) + only the affected replicas (S6 rule) + precheck.
5. Freeze a new wip, `problems edit` the changed files only, re-run only the affected platform checks
   (`checks run <key>`), never the description.
6. Re-eval of a rollout with unchanged description and Dockerfile re-runs the same agent patches: predict it exactly
   with `replay_patches.sh` before pasting.
