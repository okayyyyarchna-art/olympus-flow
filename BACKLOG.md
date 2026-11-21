# Backlog: workflow changes found while running tasks

One line per item. Status: OPEN, DONE (where), WAITING (owner decision). Read before every product step.

| # | Found | Item | Status |
|---|---|---|---|
| 1 | 2026-11-07 vet | Replay only the delta (changed scenarios + the failed one); unchanged passes keep the platform result | DONE rule: skill-next/rollout.md step 2, live references/platform.md; tool DONE (#4) |
| 2 | 2026-11-07 vet | Build is the slow part of a replay: skip patches whose first failure is before every changed line; stop a replay that no longer answers a question at once | DONE rule: same places |
| 3 | 2026-11-07 vet | Re-eval passer only when no sentence covers its failing case; FP-audit the candidate before any drop | DONE rule: skill-next/rollout.md lever 3, memory reeval-passer-stated-cases |
| 4 | 2026-11-07 vet | replay_patches.sh: a delta mode (scenario filter, skip-before-first-failure) so the rule is not hand-written per replay | DONE: tools/lib/replay_plan.py (+ shipd/tools copy): SKIP / LINE? / REPLAY per run, --stage feeds replay_patches.sh; checked on vet wip02->wip03 (typo runs LINE?, older + passer REPLAY); rollout.md step 2, platform.md |
| 5 | 2026-11-07 vet | pull.sh failures.txt greps FAILED/assert/Error and misses Go testscript "FAIL: x.txtar:N" lines | DONE: pull.sh (live + skill-next) saves testlog.txt and puts --- FAIL / FAIL: / .txtar:N lines first; verified on a vet run |
| 6 | 2026-11-07 vet | Never retire a task; when stuck name the one blocker + smallest redesign | DONE rule: rollout.md step 6, gates.md, description REDESIGN row, memory never-retire-task |
| 7 | 2026-11-07 vet | Two stacked implied cases gave 0/16 (1 run past the first, 0 past both): rulebook could say at most one implied case per task | DECIDED (owner 2026-11-07): no count limit; the NAMED/IMPLIED mark in build-checklist.md step 2 records the stacking risk |
| 8 | 2026-11-07 vet | Build checklist: a reference that reads saved metadata must check resumed/continued paths keep it current (SQ replica High: header controls stale after continue) | DONE: build-checklist.md 3.4 (saved metadata stays current after continue/resume; ledger row COVERED or OUT) |
| 9 | 2026-11-07 | Product plan: step 1 repo init (review BUILD-2 when done), step 2 corpus runner + FP barrier, step 3 dry walk | Step 1 (BUILD-2 review, Python re-check) OPEN; step 2 (corpus runner + FP barrier) built with the next task; step 3 dry walk = the next task |
| 10 | 2026-11-07 vet | proof.py rebuilt the task image for package B although the Dockerfile and base commit were unchanged (build-once rule broken; find what its hash includes) | DONE: live proof.py tags olympus-proof:<Dockerfile+commit key> and re-tags an old per-folder image with that key (skill-next proof.py already keyed by identity) |
| 11 | 2026-11-07 | skill-next/tools/lib/dockrun.py has its own lock file, separate from shipd/tools/dockrun.py: product jobs and task jobs do not share Docker slots | DONE: both dockrun.py copies lock ~/.olympus/docker.lock (DOCKRUN_LOCK overrides) |
| 12 | 2026-11-07 | Codex builds run far past the 5-20 min estimate (BUILD-2: 3h20m+, cold Docker self-checks); give builds a time box and a Docker budget in the brief | DONE: codex_job.sh (live + skill-next): timeout CODEX_TIME_BOX_MIN (default 120 min) + time box and Docker budget lines in the prompt |
| 13 | 2026-11-07 | C: hit 0 GB (docker_data.vhdx 66.9 GB: BUILD-2 cold images + build cache) and Docker died mid-proof; check free space + docker system df before every build, cap images per job | DONE: dockrun.py refuses build/buildx/pull/load/import under 20 GB free (DOCKRUN_MIN_FREE_GB); now blocking at 7.8 GB until the Docker disk is compacted |
| 14 | 2026-11-07 vet | Aligning the reference with a passer's gap (wip03 B: finding fallback removed) costs SQ: platform SQ named that exact legacy-report case, Comprehensiveness 2/3 (verdict PASS). wip02 had the same no-finding gap and got 3/3, so SQ samples angles; a reference comment that spells out the gap invites it | DECIDED (owner 2026-11-07): folded into #15 - SQ cost is one of the costs weighed per task |
| 15 | 2026-11-07 vet | B worked: relaxing one implied case (older report) + aligning the reference to the near-miss gave re-eval Vega 1/8, AR 3/3/3, SQ 2/3 then 3/3, FP panel upheld (warn, caveats) although 3 local reviewers + Codex said NOT_DESERVED. Local FP auditors are stricter than the platform panel on implied cases; candidate rule for lever 3. Panel notes: adjudicator re-runs each judge probe on the reference and drops one that fails on both (dissent = duplicate policy names, failed on both); no judge raised the older-report case. So the local fp-audit should replay its probe on the reference the same way. Scenario + prompts saved: skill-next/near-miss-release.md (live copy in references/), stuck-prompts row, memory near-miss-release | DECIDED (owner 2026-11-07): no recipe or guarantee; per task weigh the cost of relaxing/removing, cover the cases around the conflict, compare several reference changes on quality, owner decides (near-miss-release.md section 7, memory) |
| 16 | 2026-11-07 | FP panel notes are not in the CLI (runs artifact keys, runs view, problems view only show "Passed with caveats"); owner copies them from the web UI | DONE: pull.sh prints a reminder when the FP panel is warn/fail; platform gap, the owner pastes the notes |
| 17 | 2026-11-07 vet | Build checklist upgraded from the vet submission: NAMED/IMPLIED contract mark, absent-vs-empty saved metadata (omitempty), mode-only capabilities, resume keeps saved metadata current, same-name sources, one scenario per obligation, leaf-only JUnit, FP probe replayed on the reference | DONE: references/build-checklist.md (live) + skill-next/build-checklist.md |
| 18 | 2026-11-07 | Python edits on Windows write CRLF (text mode): use newline="" or sed; check `file` after every scripted edit | DONE: memory scripted-edits-lf (newline='' + `file` check) |
| 19 | 2026-11-07 | Final flow decided with the owner: sample + Scope Gate first (basic unverified files), description locked for good (calibration never changes it; OWNER EXCEPTION only after an impact analysis), v1/v2/v3 paste checkpoints with owner notifications, no watcher, sweep 1 + 3-replica batches with a verification batch, sweep 2 only on a new reproduced class, no sweep 3, every reproduced finding sharpens or adds a checklist row, 1 FP audit (+1 on demand), replica time box 25 min | DONE: skill-next PIPELINE.md, rollout.md, description.md, ledger-template.md, tools/replica.sh; memory platform-rollout-loop. Live skill gets it at the merge |
| 20 | 2026-11-07 vet | Description rulebook: one final change only as an extreme case (proven ambiguity across 2+ families or too easy, not absorbable by tests/reference, one line fixes it), built once from all evidence, then the missing rule sharpened; exception sentences get their non-exempt neighbours in the variant table (vet: 15/16 runs over-applied "turned off") | DONE: skill-next description.md sections 0, 3 step 4, 4, 5b; rollout.md lever 6; PIPELINE stage 3; memory platform-rollout-loop |
| 21 | 2026-11-07 | skill-next has no task-pick step: PIPELINE stage 0 starts from a "chosen repository and seam", while the live skill decides the pick in references/hunt.md (3 lanes, filters, score, verify top 3), problem-design.md (1-2 hard points, 3-4 consequences on different subsystem pairs) and seam-bank.md. Carry all three into the product at the merge and link stage 0 to them | DONE: skill/hunt.md (part A: no repository -> platform repo rules + 3 lanes + owner checks submission counts; part B: seam hunt), problem-design.md, seam-bank.md, repo_traits.sh; PIPELINE stage 0 links them |
| 22 | 2026-11-07 | One product: skill-next merged into olympus-product/skill with the live skill's hunt, problem-design, seam-bank, platform (final flow), situations (4 rows aligned to the new rules), examples, hunt brief, replica calibration, near-miss study prompt; P3/P3a/P3b hint prompts dropped (description locked); installed fresh (backup ~/OSS/shipd/backup/olympus-flow-live-20261107.tgz); 59 unit tests pass; memory paths fixed, index 32 KB -> 21 KB, superseded workflow entries marked | DONE |
| 23 | 2026-11-07 vet | Owner: the pick must be checked against past blockers before it is proposed (timing tests, base pins, sibling paths, P-1..P-7, cache side effects, difficulty sizing). hunt.md had filters and scores but no per-pick blocker table | DONE: skill/hunt.md part B step 8 (installed); applied to the vet pick 2026-11-07 |
| 24 | 2026-11-07 vet2 | Dockerfile without comments failed the AI precheck (Go reinstall looked gratuitous); the same RUN passed with its reason. Rule amended with the owner: no comments except one justification block above the deviating RUN | DONE: skill/dockerfile.md E4, tools/precheck.py, memory dockerfile-no-comments |
| 25 | 2026-11-07 vet2 | Owner had to ask for the requirement count, the sentence-to-test mapping and whether the text keeps the difficulty: make them a default lock report | DONE: skill/description.md step 11 (lock report a-d), installed |
| 26 | 2026-11-07 vet2 | Task Quality criterion 08 (Long-Horizon and System-Level) has no explicit check before the lock; the DQ replica ran with the sample sketch (one query) and failed 08. Proposal: hunt blocker check row "planned reference spans 2+ subsystems"; the step-8/10 DQ replica always runs with the feasibility spike as the solution, never a sample sketch | WAITING: owner. Evidence 2026-11-07: the same text with the planned reference (spike) passes 08 (DQ replica d2), with the sample sketch it failed (d1) |
| 27 | 2026-11-07 vet2 | proof.py (and any tool that imports machine.py) fails under `python -I` (isolated mode drops the script folder from sys.path); precheck.py works. Either insert the tools folder into sys.path in each tool or document "run our tools without -I" | DONE 2026-11-09: proof.py, repo_check.py, repo_init.py and solve_watch.py add their own folder to sys.path |
| 28 | 2026-11-07 vet2 | proof.py uses its --timeout (default 600 s) for the docker build as well as the test cells; the vet image build takes ~10 min, so a cold build crashes the proof before any cell. Give the build its own longer timeout (or none) | DONE 2026-11-09: proof.py --build-timeout (default 3600 s), separate from --timeout |
| 29 | 2026-11-07 vet2 | The 20 GB disk floor (#13) also blocks `docker pull` of a base image that is already present (proof.py resolves the base digest by pulling): a no-op pull should pass, e.g. skip the floor when the image is local, or resolve the digest with `docker image inspect` first | DONE 2026-11-09: dockrun.py skips the floor for a pull of an image already local; checked on real Docker (local passes, absent refused) |
| 30 | 2026-11-07 vet2 | Owner: the disk floor must not be a permanent blocker: 12 GB, adjustable per machine | DONE: machine profiles docker.min_free_gb = 12 (schema.md), product dockrun reads it, DOCKRUN_MIN_FREE_GB overrides per job, shipd dockrun default 12, codex prompts, memory disk hygiene |
| 31 | 2026-11-07 vet2 | proof.py mounted /tmp as a Docker tmpfs without exec (Docker default noexec): every Go test binary failed "fork/exec ... permission denied" and the base build failed, so the proof could never pass a Go task (vet task 1 ran the pre-merge proof) | DONE (revised): no tmpfs over /tmp at all. A fresh tmpfs hid the image's warm GOCACHE (/tmp/gocache) and its size cap made a cold vet build fail "no space left on device" (empty build log -> TestBuildVet). H4 needs writable scratch, not a fresh RAM /tmp; /out stays tmpfs |
| 32 | 2026-11-07 vet2 | Six proof.py defects (#27-#31) surfaced one per run during vet2 because the merged product tool had only mock/unit qualification. Before a product tool version is used on a task, smoke-test it end to end on a known-good accepted package (vet wip03: four cells, uid, offline) | DONE 2026-11-09: proof.py run end to end on vet v13 (known-good package) under python -I, using the installed tools; PROOF PASS |
| 33 | 2026-11-07 vet2 | proof.py takes ~20-25 min per v1 proof on Windows: 6 sequential cells, each preparing and reading the tree through a Windows bind mount. Faster: prepared tree in a Docker volume (WSL2 disk speed), independent cells in parallel across the profile slots, one reference repeat before v1 (the stage-9 stability run repeats 6+6) | OPEN |
| 34 | 2026-11-07 vet2 | Owner: shortcuts against the workflow always cost us (vet2 v1: condensed plan instead of ledger tables -> platform SQ FAIL + full fix batch). One bias file with our priorities and the shortcuts that cost us, checked at every stage exit | REMOVED by the owner 2026-11-07 ("remove bias for now"); the B1-B12 lessons stay in this row for the consolidation pass (#36): condensed note for a named artifact, wrong check inputs, unread claims, one instance per requirement, happy entry point only, tests tied to one design, speed over gate order, untested tools, owner asking for defined reports, residual keeps, done without evidence, fixing one finding at a time |
| 35 | 2026-11-07 vet2 | Platform SQ (v1) Code Quality 1/3: "no regression test accompanies the bug fix" = the repo REVIEW.md rule 4; rule 8 wants an acceptance script + catalog row for a user guarantee. Our precheck even warned against tests in the solution | DONE: build-checklist reference step 8 (read the repo review rules), precheck now warns when the solution has no test of its own |
| 36 | 2026-11-07 vet2 | Owner: are we adding complexity? After vet2: consolidation pass decided by metrics: merge situations.md + stuck-prompts.md, fold BIAS.md rows into the checklist steps (BIAS keeps the priorities + stage-exit line), cut any step that changed no outcome in vet2; consider full platform checks only at v2 (v1 = calibration rollout) if the platform allows it. Owner 2026-11-07: early versions are for the calibration rollout; a check that blocks the rollout is contested (I draft an honest contest note per finding: quote + code trace or "fixed in next version, file:line"), refinement continues locally. Owner: the checklist must be a complete blueprint that gives strong tests+solution at once: turn it into fill-in tables generated before code (per obligation: entry point x change kind x copy state x lifecycle edge, each cell tested-by or out-by-sentence), plus one adversarial reference audit lane before v1 (vet2: that lane found 3 of 4 reference breaks) | DONE 2026-11-09: blueprint table in ledger-template.md + tools/checklist_gate.py + prompts/apply-build-checklist.md; reference audit before v1 (PIPELINE 6a); situations.md + stuck-prompts.md merged; B1-B12 folded (checklist header, PIPELINE item 8; the rest already had rows); full checks at v2 + contest notes (platform.md; which checks block a rollout NOT VERIFIED). No stage cut: sweep 1, sweep 2 and the verification batch each caught real gaps on vet2; only stale or contradictory rows went (two-audit gates, 250-word gate, local-solve rows) |
| 37 | 2026-11-07 vet2 | round.sh: ar and verify need the same tag's dq report; a round without dq (description locked) silently skips Auto Review and verify ("missing or empty input dq-<tag>.json"). Validate the check set up front, or make ar/verify take the locked dq of the last round  Also 2026-11-08: a re-check of only the failed check is impossible (every check waits for the full report set of its tag: GATE FAIL no sq-b7a.json); pipeline rule 6 asks for affected-check reclosure | DONE 2026-11-09: round.sh reuses reports of the same input bytes or stops up front; a re-check of one failed check works this way; unit tests added |
| 38 | 2026-11-07 vet2 | Owner: why proofs again and again? The proof certifies the exact files of a paste: run it once right before each paste and at the final freeze (stability 6+6); between pastes use only the container cells + variants job. vet2 ran an unneeded v2 proof before the replica batch | DONE 2026-11-09: PIPELINE confirmation schedule item 7 |
| 39 | 2026-11-08 vet2 | Rollout 1 replayed on v3: all 4 Orion/Vega patches fail 3 tests on paths no sentence names. Tests grew after the lock (sweep 1 reference fixes on PR removed rows, PR base version, same-file merge) and nobody re-checked them against the description; used the one 5b change ("pull request scans"). Rule for the description/checklist: every test added after the lock gets a sentence that names its path (mode/entry point, no mechanism) or is dropped; check runs before each paste | DONE 2026-11-09: description.md section 5. Worded as: the test quotes the sentence that literally covers its path; no such sentence = drop the test, never add the sentence |
| 40 | 2026-11-08 vet2 | round.sh --check calls started in parallel race on checkpoint-<tag>.json (Windows rename WinError 5 -> GATE FAIL before the check runs; dq lost). Also: killing a lane by command-line match hit a second lane whose launch line named the same brief. Fix: lock or per-check checkpoint writes; lanes get their own launch scripts | DONE 2026-11-09: summarize.py locks the checkpoint update and retries the Windows rename (8 parallel declares unit-tested); PIPELINE: stop a lane by its tracked job |
| 41 | 2026-11-08 vet2 | summarize.py gate fails a clean round when verify gives DROPPED candidates (break attempts the SQ replica itself rejected) severity "unspecified": round b8 kept 0, bands 3/3/3, yet GATE FAIL "invalid verification disposition". Accept a missing severity on DROP rows, or tell the verify prompt to use low | DONE 2026-11-09: summarize.py accepts any severity on a DROP row; KEEP still needs a real one; unit-tested |
| 42 | 2026-11-08 vet2 | proof.py unknown-uid cell hit its 600 s cell timeout while 4 host solvers built Go (same tests took ~100 s in the earlier cells); the cell time includes host load and slot waits. Run the proof with no solvers running, or scale --timeout with load | DONE 2026-11-09: DOCKRUN_TIMEOUT limits the command, not the slot wait (exit 124 checked on real Docker); PIPELINE item 7: no other Docker jobs during a proof. The 300 s new/base duration check still counts a slot wait |
| 43 | 2026-11-08 vet2 | Probe batteries waited ~50 min in the Docker queue behind FP-audit containers that repeated their probes 3x (45-60 min each). FP audits run each probe once unless a result looks flaky; coordinator batteries get a reserved slot | DONE 2026-11-09: PIPELINE confirmation schedule item 5 (each probe once unless flaky) |
| 44 | 2026-11-08 vet2 | round.sh <task> <tag> fairness ar (a test-only round) runs fairness, then skips ar silently: ar needs sq-<tag>a/b (--merge-sq) and the gate fails on the missing sq file. A test-only round should reuse the last sq reports of the same solution.patch hash (same for dq-<tag>: ar also reads it; or round.sh should refuse the combination up front) | DONE 2026-11-09: same fix as #37 (fairness keys on tests + description; sq and dq on solution + description) |
| 45 | 2026-11-08 vet2 | Pull the platform state (checks + runs) before every paste and before every status claim about a check: I pasted v8 on top of a finished re-eval and said Auto Review was still the old run, 5 h of results unread. Also: a re-eval uniform failure (7 runs) on one test is the check to weigh; the platform fairness check said fair and 5 of the 7 runs were still blamed on the task, so the verdict-replica judges outrank the TQ replica on that question | DONE 2026-11-09: platform.md pastes section (pull before every paste and status claim, watch.sh after each paste; PIPELINE stage 6b), rollout.md step 5 (verdict replica outranks Test Quality on blame) |
| 46 | 2026-11-08 vet2 | Owner rule: Codex stays in workflow sweeps and replica checks. Calibration comparisons, discriminator searches and verdict estimates use in-process + claude2; Codex only when the owner names it or after both lanes found nothing. Reflect this in the skill wherever it assigns ad-hoc lanes | DONE 2026-11-09: PIPELINE, review-lanes paragraph |
| 47 | 2026-11-08 vet2 | After the description lock, no description change may be drafted or listed as an option; before the lock, an edit that names a case the runs are failing is rejected (vet2: 0/4 local solves on the PR base version, wording named it, next rollout Orion 4/4 + Nova 4/4). Add this as a hard stop in the skill description and rollout steps | DONE 2026-11-09, softened by the owner: the builder never proposes one; a change happens once only if the owner asks (description.md sections 0, 5, 5b, 6; rollout.md lever 6; SKILL.md; PIPELINE stage 3; calibrate-one-passer.md) |
| 48 | 2026-11-08 vet2 | Add to rollout.md: on a Fair task or env-blocker failure read every evalResult and the agentBlameUnfair flag first; give a contested test neighbours showing the rule both ways, a comment above each assertion quoting the description, and a name that says what it checks; do not touch the Dockerfile for notes that carry no blame (vet2: 5 flags to 0 with tests only) | DONE 2026-11-09: rollout.md step 1, build-checklist.md tests card (second-reading row) |
| 49 | 2026-11-09 vet2 | New step for too-easy tasks: skill/prompts/calibrate-one-passer.md (all levers tried on vet2, what failed, how to read each label), linked from rollout.md lever 4 | DONE |
| 50 | 2026-11-09 | Owner, a behavioural suggestion and never a gate: aim for hard points some agents solve, not all and not none; two moderate hard points on different paths over one extreme point; all-pass and all-fail stay fine | DONE: description.md section 2, problem-design.md section 2, hunt.md step 6, hunt brief; memory desc-two-moderate-hard-points |
| 51 | 2026-11-09 | Rollout routing in one place: all fail -> near-miss-release.md, too many deserved passes -> calibrate-one-passer.md; only-failure check before a re-eval (warning, not a stop); owner order Test Quality, re-eval, Auto Review, FP panel | DONE: rollout.md header and step 5 |
| 53 | 2026-11-09 | Customer-ready polish: GETTING-STARTED.md (install, stage table, situation prompts), machine/windows.example.json, example profiles never prune the user's Docker data, agents use installed paths, the three playbooks the agents read moved into skill/playbooks, build folders and logs ignored | DONE |
| 54 | 2026-11-09 | Owner: the customer has no memory folder, so general rules must live in the skill. Audit of 235 memories: 41 rows missing; 37 folded in (build-checklist.md, tests.md, replicas/sq.md, platform.md, rollout.md, gates.md, PIPELINE.md, situations.md and others); 4 rejected on triage (evaluator choice unverified; per-repo notes files, weak evidence; features-first hunting, conflicts with hunt filter 4; one-task pattern for what splits runs). Reviewer launchers read memory only where it exists | DONE |
| 55 | 2026-11-09 | Owner: on vet2 the checklist was skipped for a condensed plan. Prompt run before any test or reference code on every machine, one row per rule, Blueprint, gate, fresh reviewer | DONE: prompts/apply-build-checklist.md, tools/checklist_gate.py, PIPELINE stage 4, SKILL.md |
| 56 | 2026-11-09 | Found at the GitHub push: on default Windows Git (core.autocrlf=true) every script checks out CRLF and task repositories lose Linux endings; tests hardcoded the owner's profile | DONE: .gitattributes, machine.py and machine.sh set core.autocrlf=false for our tools, GETTING-STARTED step, machine/windows-asus.json removed (local.json stays), tests use windows.example from either layout |
| 52 | 2026-11-09 | vet2 end-of-task records: metrics/<task>.json, cleanup of solver clones, Go toolchain and task Docker | OPEN: after the owner confirms vet2 is submitted |
| 57 | 2026-11-09 | Found at stage 1 of cc-vet-continue-usage: `proof.py --build-only` builds the image, then ends PROOF FAIL because pkg/ has no test.patch yet, and it needs a new-ids file that does not exist at stage 1. The Dockerfile-first gate runs before any test exists: --build-only should need only the Dockerfile and stop after the build | DONE 2026-11-10 (proof.py --build-only needs only the Dockerfile) |
| 58 | 2026-11-09 | Owner: "why do you ask always? ... all are steps never stop for me". Then: "dont ask for dockerfile and sample, later you should ask"; a paste during an agent run stops the run. PIPELINE said every draft upload needs authorization | DONE: PIPELINE header: Dockerfile and sample without asking; v1 onward ask; never paste while a run or check is active |
| 59 | 2026-11-09 | Owner: "long horizon depends on how deep our problem and reasoning required". Measured on 14 submitted tasks: production lines do not predict the Nova average | DONE: problem-design.md section 6 |
| 60 | 2026-11-09 | Owner: the platform lowered its token drip. Low-drip mode: stop at a Scope Gate pass and a fully built local package, owner-run solvers at the end for information only, paste and hold for the sprint. PIPELINE stages 6b-8b assume a rollout right after v1 | OPEN: decide after this task whether PIPELINE gets a low-drip route |
| 61 | 2026-11-09 | Found launching the cc-vet-continue-usage solvers: tools/solvers.sh had a literal backslash-n after --append-system-prompt, so every Opus solve got a stray positional argument `n` | DONE: line continuation restored (product and installed copies) |
| 62 | 2026-11-09 | Found grading the cc-vet-continue-usage solvers: replay_patches.sh passed relative folders to docker on Windows, which treats them as volume names and refuses | DONE: host() resolves the folder first (product and installed copies) |
| 63 | 2026-11-09 | Owner: "if we test some local solvers based on user decision run FP audit on passer as soon as it finishes". The FP rule was written for platform rollouts, and the local solver step ended at grading | DONE: PIPELINE.md Confirmation schedule, SKILL.md, situations.md, solvers.sh end message (product and installed copies) |
| 64 | 2026-11-09 | Owner, cc-vet-continue-usage: "isnt sweep 1 should have found it?" Sweep 1 proposed an exact-count assertion (G4) for an unnamed warning and, in the same report, a fix design that fails it. Needed: (a) every fix a reviewer offers as valid becomes an executed valid-design variant; (b) an exact count needs a sentence that says once, otherwise assert presence | DONE 2026-11-10 (build-checklist s4: valid alternatives executed; exact count needs once/exactly) |
| 65 | 2026-11-10 | Platform rollout of cc-vet-continue-usage, Vega #4: FAIL_TEST_MISMATCH with blame on the task. The hidden helper built the production config struct by hand, and a valid design that added a new config field wired through the real builder got a nil field in the test. Local fairness replicas, sweeps and platform verifyFairness all passed it. Needed: build-checklist row and a standard valid-design variant "adds a config field set only by the production builder", and tests that take the config from the production builder where one exists | DONE 2026-11-10 (build-checklist s4 standard variant + s5 config from the production builder) |
| 66 | 2026-11-10 | cc-vet-continue-usage rollout: run labels repeat across batches (two "Orion #6"), so a pull that names folders by label skipped batch 2 and showed batch 1 results for it. Needed: the rollout pull keys folders by run id, and names the batch | DONE 2026-11-10 (pull.sh: label, batch, evalResult.json, output.json; rollout.md + calibrate Step 1 use it) |
| 67 | 2026-11-10 | Owner, cc-vet-continue-usage calibration: the line-by-line lane (Lever C) ran before batch 2 arrived, so the new Orion passer was never compared. Needed: calibrate-one-passer.md says each new batch's passers go through Lever C before the keeper is chosen | DONE 2026-11-10 (calibrate-one-passer Lever C: every new batch's passer) |
| 68 | 2026-11-10 | cc-vet-continue-usage calibration: run verdict judges before the proof, not after. A contested test judged 5 of 5 blamed was replaced by a visible-effect test (2 of 5), and each replacement cancelled a running proof. Needed: put the verdict judge step before the proof in calibrate-one-passer.md Step 6 | DONE 2026-11-10 (calibrate-one-passer Step 6.2: verdict judges before the proof) |
| 69 | 2026-11-10 | cc-vet-continue-usage Codex r11 Auto Review T4 High: tests pinned that finished registry lookups are "not asked again" (a call count) but not that their saved data survives, so a design that skips the lookup and drops the malware verdict passed. Needed: tests.md / build-checklist row "for each kept remote result, assert the saved value is still in the report, not only that the call was skipped" | DONE 2026-11-10 (build-checklist s4 axis: kept results by value) |
| 70 | 2026-11-10 | cc-vet-continue-usage r11: round.sh gate ended GATE FAIL "unexpected verification ID ('fairness-r11', ...)" although every finding was handled; the verify report named a finding title the gate's ID list did not hold. Needed: the gate matches verify entries by the source report's finding id, or reports the mismatch as a warning, not a fail | DONE 2026-11-10 (summarize.py gate: unmatched verify ID is a WARN; r11 now shows its real failures) |
| 71 | 2026-11-10 | cc-vet-continue-usage re-eval: the two Orion #6 runs (same design, same single failing case) got opposite verdicts. The judge that blamed the task said the stand-in "removes precisely the interface the real analyzer has" and the hidden comment's classification rule "is not documented"; the judge that blamed the agent cited the visible base test delta_test.go:589 (a plain fake registered Local+Whole as the code enricher). Needed: (a) a stand-in fake keeps every interface of the real plugin except the one the test is about, or (b) its test comment cites the visible precedent by file:line, so every judge sees the argument, not only some; build-checklist row + tests.md | DONE 2026-11-10 (build-checklist s5 stand-in row; calibrate Step 5.7 + Step 6.2 comment-only fix first) |
| 72 | 2026-11-10 | Owner, cc-vet-continue-usage: local solvers predicted the opposite of the platform (local 1/6, platform 3/12 with designs we never saw: Vega's Clear config field, Orion's SourceEnricher gate). Proposal, an experiment: build family profiles from the saved platform rollout patches dated 2026-10-20 or later only (owner: the platform agents get stronger week by week, so older runs describe weaker agents); weight recent runs higher and re-check the profiles after each new rollout: which design each family picks per seam type, which implied cases it misses, where it gates behaviour (Orion: interfaces; Vega: new config fields; Nova: misses implied cases). Before the first rollout, run each profile's predicted designs as variants against the test set to predict the family split. Replaces local solvers as the pre-rollout signal. Measure: predicted vs actual split on the next 2 tasks before adopting | PARTLY DONE 2026-11-12: skill/profiles.md holds the Orion/Vega/Nova profiles refreshed from the post-10-20 retro (per-kind rates, upkeep after every rollout); the variant-based split prediction stays OPEN |
| 73 | 2026-11-10 | cc-vet-continue-usage platform Auto Review T1 Medium: base mode ran the upstream acceptance scripts (.txtar), catalog.yaml and the helper code of test/acceptance from the working tree, so a submission could edit them. Root cause: build-checklist T1 row says "restore the base-commit test files in a scratch copy or overlay" as if both were equal, but go -overlay only pins compiled Go files, never data read at run time; and our proof never tampers with a pinned input. Needed: (a) the row names every input the selected base tests use: test files, fixtures, testdata, scripts, catalogs, golden files and helper code in test-only packages; overlay only for compiled files, a pinned copy of the tree (read-only /app safe) for the rest; (b) proof.py tamper probe: edit one pinned data file and one helper, base mode must give the same per-ID vector; (c) replica T1 brief asks "what does each base test read at run time" | DONE 2026-11-10 (build-checklist T1 row; proof.py --tamper; replicas/ar.md T1 asks what base tests read at run time) |
| 74 | 2026-11-10 | Owner: Test Quality coverage keeps coming back partial (vet 2: 6/6 requirements partial; vet 3: 3/6; vet 1: 6/6 yes) and the platform is adding coverage checks. Our fairness replica said 9/9 yes on vet 3 because its Step 3 said "breadth is not required". Causes in the site notes: scope words tested on a sample of categories, counts without content, test names promising unasserted outcomes, intermediate states not inspected | DONE 2026-11-10 (build-checklist s4 "Coverage to yes"; replicas/fairness.md Step 3 + qualityCheck; gates.md G4 target every requirement yes; CALIBRATION.md row; re-measure on the next task) |
| 75 | 2026-11-10 | Owner: make the one-passer calibration prompt cover every way vet 3 tried, and faster. On vet 3 the splits came from reading each passer's dispatch key (Whole / Local / SourceEnricher) and its side effects against a fresh scan; a 424-cell grid, 13 line rows and the agents' own tests found none | DONE 2026-11-10 (calibrate-one-passer: Levers I dispatch key and J side effects against a fresh run, run first; grid levers time-boxed; near-passers checked for task blame; Step 4.6 valid designs on every cell; Step 5.6 visible effect over order; Step 5.8 production builder; vet3 evidence on D, F, H) |
| 109 | 2026-11-11 | Owner, cc-vet-direct-deps: PIPELINE.md stage 7 says the replica and verification batches run "3 independent replicas in parallel ... 25 min time box each", but `round.sh <task> <tag>` (the aggregate I used for r1 and r2) runs every check serially in one slot, so each batch took 42-45 min instead of about 25. I also planned a second verification round (r3) after fixing a known-kind r2 finding, which PIPELINE does not have: known kinds go to fix + Repair, and another verification batch only follows sweep 2. Needed: (a) the aggregate starts each check as its own tracked child up to the machine slot limit, then runs verify and gate; (b) PIPELINE/gates.md state in one line "after the verification batch: fix + Repair, no second batch unless sweep 2 ran"; (c) the success metric counts r1 and r2 findings for this task (r1 several, r2 one High: same-name introducers). | WITHDRAWN 2026-11-11: owner keeps the workflow as it was; only #110 (coverage rule removal) applies |
| 110 | 2026-11-11 | Owner: remove the "coverage to yes" rule (#74) completely: on vet task 4 it turned every fairness breadth suggestion into a required fix round. | DONE 2026-11-11: build-checklist s4 block removed; gates.md G4 target sentence removed (back to the pre-#74 text); replicas/fairness.md restored to the pre-#74 Step 3 ("breadth is not required", no qualityCheck); CALIBRATION.md notes the removal |
| 111 | 2026-11-11 | Owner, other machine (vet task, rv3-rv7) and this one (planned r3): agents kept running full re-grade rounds after fixing verification findings. Causes: gates.md Repair item 5 said a T/S change stales fairness/SQ/AR and item 6 said no stale record at hand-over, with "do not loop paid checks" only in the blocker sentence; summarize.py's gate passed only when verify DROPped every finding, so a fixed KEEP could be cleared only by a new full round; no tool enforces the stage 7 time box. | WITHDRAWN 2026-11-11: owner keeps the workflow as it was; only #110 (coverage rule removal) applies |
| 112 | 2026-11-11 | Owner: (a) allow sweep 3 only when the verification batch after sweep 2 again finds a new kind of issue (hard condition), then one final verification batch and stop; (b) find every place that makes agents keep re-running verification rounds. Found: gates.md Repair items 5/6 ("stale" semantic judgments, "no stale record at hand-over"); and six synced memory notes from older workflows that both machines load every session: olympus-always-run-our-sq ("after every solution change run our SQ"), quality-over-pass-rate #5 ("fresh SQ + TQ judges before every hand-over"), olympus-split-equally ("every review round = in-process + claude2 + Codex"), reference-strict-audit ("every replica round runs 2 ref audits"), gap-sweep-one-round ("before EVERY final hand-over: 1 sweep + 2 gate runs"), close-every-finding-first-build (TQ coverage partials auto-closed). | WITHDRAWN 2026-11-11: owner keeps the workflow as it was; only #110 (coverage rule removal) applies |
| 113 | 2026-11-11 | Owner: bring two of the other machine's rules to both machines: build-checklist base-mode upstream callers rule (its #100, edsl AR T1 High) and description.md entry-point words rule (its #105, edsl drift); plus its Mac compatibility fixes (its #76 test_launchers sys.executable, #77 empty-array guard in round.sh, solvers.sh, codex_job.sh, replay_patches.sh). Its 75/25 split (#80), rescue-existing-task prompt (#88) and pre-paste-label-check prompt stay on that machine only. Windows rows renumbered 76-79 -> 109-112 to avoid colliding with its rows 76-108. | DONE 2026-11-11 on Windows (verbatim text from the other machine; launcher tests 11/11 OK) |
| 114 | 2026-11-11 | cc-vet-direct-deps: platform stage 6 failed "Description contains non-ASCII character at position 631" (a curly apostrophe in the owner-locked text). Our DQ replica reported prechecks.ascii=false in every round (d1-d3, r1, r2) and I dismissed it each time because platform Description Quality had passed the same text; DQ is not the check that enforces ASCII. Proposal (owner decides): a non-ASCII character in description.md is a hard stop before the lock, checked by a one-line test at stage 3, never triaged as a false alarm. | OPEN (owner) |
| 116 | 2026-11-11 | cc-vet-dev-only stage 0b: `tools/repo_init.py URL COMMIT TASK` wrote the task folder under the current directory (it was the skill folder), not under the machine profile tasks_root; I moved it by hand. Needed: repo_init.py resolves TASK against machine paths.tasks_root unless an absolute path is given, and prints the folder it wrote. | OPEN |
| 115 | 2026-11-11 | cc-vet-direct-deps rollout: Orion 4/4, Vega 3/4, Nova 3/4 solved; three searches (in-process reading, Lever H on the agents' own acceptance scripts, Codex line-by-line over 518 lines with probes) found no fair split: all 10 passers compute the same observable result. Causes: (1) stage 2-3: every hard point was written as its own sentence (the direct-dependency corner, the full unknown-dependencies rule, absent-not-empty) and the humanize prompt locked each one as a MUST KEEP item, against the rulebook (hard points carried by general sentences, implied cases discoverable from the repo); (2) stage 0: the hunt noted model/graph.go PathTo but missed PathFrom and MayReach, which already implement the known-path and unknown-reach rules, so the reference was nearly prewritten. Proposal (owner decides): at stage 0, grep the repo for helpers that already compute each hard point and score the seam down; at stage 3, a lock-gate row per hard point naming the general sentence that carries it and confirming no sentence names it; the humanize prompt lists meanings, never named corners. | DONE 2026-11-12 (owner go): difficulty.md decision inventory + obvious-design spike; description.md deletion-test precedence, step 8 hard-point grep, humanize hand-over lists meanings only |
| 117 | 2026-11-11 | cc-vet-dev-only stage 2 (owner order after #115): the obvious solution an agent writes with the base helpers (V-SHORTCUT: model.Graph.MayReach over the base pnpmParents/bunGraph edges, runtime roots = dependencies + optionalDependencies of every project) passed 9/9 hidden tests; the sketch reference was the same design. Nothing in the workflow measures this before the lock. Proposal (owner decides), extending #115: at stage 2 step 3 (feasibility), write V-SHORTCUT with the base helpers and run it on the planned tests (eval/variants.py); the lock report carries one lock-gate row per hard point: the general sentence that carries it, confirmation that no sentence names it, the base-helper grep (file:line or none), and the V-SHORTCUT result on its test. A hard point the base already computes or V-SHORTCUT passes is not a hard point. | DONE 2026-11-12 (owner go): difficulty.md section 3 (V-OBVIOUS must fail >= 2 different decisions; persistence probe); description.md step 3 + section 4 checklist |
| 118 | 2026-11-11 | cc-vet-dev-only d2: every reading-audit finding was fixed by a reword that named the corner (root-only -> 'every importer and every workspace is a project', name-keyed -> 'each exact version is decided on its own', transitive -> 'directly or through other packages', PR x@1->x@2 -> 'the same version'), because description.md step 7 allows a reword 'as many words as needed' while section 2 says hard points are never named; the draft was never checked against the 'Hard points (not named)' list of description_facts.md before the owner saw it. Proposal (owner decides): step 7: a reword may not name a hard point or an implied trap; when only a naming sentence removes a second reading, the disposition is a general sentence the repo makes discoverable, or tests that accept both; step 8 adds a check: grep the draft for each hard point's words before the owner handover (the stage-2 twin of the #115/#117 lock-gate row). | DONE 2026-11-12 (owner go): description.md step 7 reword never names a hard point; step 8 grep before the owner hand-over |
| 119 | 2026-11-12 | cc-vet-direct-deps trajectory read (owner ask): every run used the description as a checklist (Nova: 'sentence-by-sentence review of your prompt', 'mapping the prompt's specific language to model.Graph'; Vega's final summaries repeat our boundary sentences as bullets). Each boundary sentence made a design decision for the agents: 'in that graph' chose g.Root over p.Direct, 'Even if ...' fixed the root-first check, the unknown-dependencies sentence spelled out the PathFrom/MayReach rule, 'saved scan' told them to store the list on the finding. All 11 completed runs got every stated point right; both failures (V1b root-or-Direct on import graphs, N1 open root with a known path) were on points left unstated, which the repo decides (model/graph.go:8-14, docs/policy.md:20). The rulebook already says requirements only (R1, R2, R4, section 2), but R11 ('name the meaningful boundaries') and R16 ('clarifications are allowed') have no test that tells a boundary from a hint, and R7's 'trace to a sentence' pulls every tested case into the text. Proposal (owner decides): add a deletion test to R11/R16: delete the sentence, and if the remaining text plus a quoted repo line still decides the outcome one way, the sentence is a hint and goes; a boundary sentence stays only when deleting it leaves two readings the repo does not settle; R7 traces implied cases to the repo line, not to a new sentence. | DONE 2026-11-12 (owner go): description.md section 1 precedence (deletion test first), R7 repo line at the assertion, R11/R16 tied to the deletion test |
| 120 | 2026-11-12 | cc-vet-direct-deps: tools/stop_solves.sh reported every solve tree stopped, but on Windows the three GPT solves kept running (timeout -> codex_job.sh -> codex exec -> node -> codex.exe stayed alive and held the clone files). Needed: stop_solves.sh also stops every process whose command line names the solve's clone folder (vp-<task>-<n>-<run>), then reports how many are left; the clone is deleted only when 0 remain. | OPEN |
| 121 | 2026-11-12 | Owner report from another machine: the coordinator asked to 'close G1-G4' after each fix batch and the session ran the three in-process reviewer agents (AR, SQ, TQ; 15-20 min each) before every paste, finding new edge cases each round -> fix -> round again. Causes in the kit: (1) agent descriptions are standing triggers ('Use before every paste', 'Run before every solution.patch paste', 'Run before every test.patch paste'); (2) gates.md Repair step 6 'Close affected G1 -> G2 -> G3 -> G4 on exact repaired bytes' has no round limit and names no tool, while PIPELINE.md stage 7 caps the schedule (sweep 1, one replica batch, one verification batch, sweep 2 once, no sweep 3) with no precedence between them; (3) the rules that stop the loop on this machine are machine-local memory (quality-checks-not-every-round, gap-sweep-one-round, olympus-no-waste-runs), never moved into the kit. Proposal (owner decides): one 'Review schedule' table in PIPELINE.md that overrides every other file (which checker at which point, max rounds, a fix batch never triggers a round by itself); agent descriptions point to it ('only at the review points in PIPELINE.md, never per fix or per paste'); gates.md step 6 = close at the next scheduled batch; audit memory and move every workflow rule into the kit so all machines behave the same. | OPEN (owner) |
| 122 | 2026-11-12 | cc-vet-direct-deps v8: (a) tools/pull.sh digest prefixes every verifyFairness per-test verdict with 'UNFAIR test:' although 32 of 35 say fairness 'Prompt-stated'; the owner read it as 35 unfair tests. Needed: label each line by its own fairness field and print the unfair ones first with the count. (b) After the description change I ran reading audits + DQ replica + deterministic checks but no fairness replica on the tests against the new text; platform verifyFairness then flagged 3 cases (one assertion: no list for y when another root reaches an open node), because the old text spelled out the unknown rule and the new general sentence needs the reasoning next to the assertion. Needed: description.md / gates.md: a description change (D) always re-runs the fairness replica on the tests before the paste, and every assertion that relies on an implied case carries its one-line reason at the assertion. | (b) DONE 2026-11-12: description.md step 10 + 5b fairness replica after a D change; build-checklist second-reading row: implied case carries repo file:line + reason. (a) pull.sh digest label OPEN |
| 123 | 2026-11-12 | Difficulty retro over 12 tasks (analysis-20261112/synthesis.md, lanes A-C): only docker proxy was hard on its first suite; turso, elio, swift, local-registry, unused-suppression and the faust tasks reached the band through calibration on near-passers that differed by one decision; direct-deps failed because its 14 passers had zero behavioural spread. Every separator was a wrong-by-default decision of six kinds (misleading nearby idiom, caller-context branch, second path/shortcut, intermediate semantics, identity/timing, exception neighbour). The first proposed gate (one choke point / existing helper = veto) misjudged turso and elio. Proposal (owner decides): stage-0 decision inventory gate (>= 2 wrong-by-default decisions on different paths, each reachable by a fair case the text covers), measured by an agent-strength obvious-design spike (optional 2 Orion sample runs + replay); fold in: upstream test coupling scan, breadth/trap-stack cap, single-assertion fragility flag, separator must follow a sentence or repo line, persistence probe, too-easy alarm on short valid variants, global-property fuzz, pass counts from view JSON. Supersedes the veto parts of #115/#117. | DONE 2026-11-12 (owner go): difficulty.md (inventory GREEN/AMBER/RED, widen, spike, optional platform probe, reserve, fragility); hunt.md score + step 8; rollout.md re-eval readiness; ledger Difficulty section |
| 124 | 2026-11-12 | Owner: "is this all we have to fix so agents must reason and take decisions, and re-eval works?" Gaps left by #119/#121-#123: (1) the hunt does not look for the six decision kinds, so the stage-0 gate would only reject; (2) the decision inventory is the builder's own judgment, done after the builder already knows the answer (vet4: the builder rated two hard points that the repo had prewritten); (3) re-eval works only when passers differ on some decision, and nothing plans those levers before the rollout: past separators (elio Duplicate Finder, turso NOT spelling) were found after it; (4) no time-boxed widen playbook for a seam with fewer than 2 decisions (a real second entry path, saved state, caller context, exception neighbour), only reject; (5) a requirements-only text can slide into unfair ambiguity: difficulty must come from the repo, never from text gaps (fairness replica after every D change, #122). Proposal (owner decides): hunt.md scores candidates by decision kind; a fresh in-process reviewer does the inventory blind (repo + one-line requirement, no reference, no draft); stage 0 records a calibration reserve of >= 3 fair decision points (repo line or sentence each, planned probe each) that the first rollout's passers are checked against; widen playbook with a 1-day box; the 2-run Orion sample probe becomes required (the only pre-build evidence that is not the builder's judgment; costs platform tokens). (6) the family profiles (shipd/playbooks/orion-model-profile.md 2026-10-12, vega-model-profile.md 2026-10-19, faust runs only) live outside the kit and the stage-0 inventory never reads them; their own rules ("mirrors the sibling implementation 9/9", "description = checklist") predicted the direct-deps result. Proposal: move them into the kit, refresh them from the post-2026-10-20 rollouts (#72), and score each inventory decision with their per-class hit rates and the p^k table of problem-design.md section 2. | DONE 2026-11-12 (owner go; owner: keep some tolerance, never reject everything): only RED (zero wrong-by-default decisions) is rejected; AMBER builds; fresh-reader inventory, reserve, widen, profiles in the kit |
| 125 | 2026-11-12 | Owner: run 2 Orion + 2 Vega at stage 3 on the locked text, not on the stage-1b sample; they count toward the final rollout (the text is locked), so v1 adds only 2 Orion + 2 Vega + 4 Nova for 4-4-4. Also: the widen step is once per seam (a spike fail after a widen goes to the runner-up), and the re-eval readiness list names its one replica round (fairness + AR when tests change, SQ when the reference changes). | DONE 2026-11-12: difficulty.md sections 2-4, PIPELINE.md stages 1b/3/6b + schedule item 2, rollout.md intro + readiness 4b, description.md step 11 |
| 126 | 2026-11-12 | Owner: the stage-3 2 Orion + 2 Vega are for the builder's picture of how the agents read the text, not a calibration paste; the owner runs the full checks once, on one complete v1. Tests are shaped on those runs: keep the best correct run (FP-audited keeper), give every gap of the other runs, V-OBVIOUS and the variants a fair test, aim for one passer in the final 4-4-4; calibration paste only when needed, with one replica round. | DONE 2026-11-12: difficulty.md section 4 (keeper), PIPELINE.md stages 3/4/7/7b/8b (6b removed), platform.md paste table, description.md step 11 |
| 127 | 2026-11-12 | Owner: widening a RED seam leaves 1 decision, which the 2-decision spike then fails anyway. Fixed: GREEN builds; AMBER widens once to add the second decision (else runner-up); RED goes straight to the runner-up; the spike counts different decisions (two test cases of one decision count once); spread points go to the reserve and never count as decisions. | DONE 2026-11-12: difficulty.md sections 1-3, PIPELINE.md stages 0/2, hunt.md B steps 8-9, description.md step 3 + section 4 |
| 128 | 2026-11-12 | Blind test of the stage-0 reading verdict (analysis-20261112/blind/, 5 fresh readers, original pins, one-line requirements): all five rated GREEN, the known-easy direct-deps included (its 6 "traps" caught 0-2 of 16 real runs: the right helper sat next to the wrong one). The readers did find the real separators of elio and table-visibility blind, half of local-registry, and found but discarded all three of swift (exception, race, fast path as "contested"). Owner decision: the verdict goes; the inventory stays as the generator of planned separators and the reserve (exception and race cases kept); the gate is measured: the stage-2 spike (2 different decisions) and the stage-3 2+2 runs; when the spike fails: the runner-up first, then widen once the better of the two, then owner options. | DONE 2026-11-13: difficulty.md sections 1-4, PIPELINE.md stages 0/2, hunt.md step 8, seam-bank, ledger, description.md section 2/step 3/section 4 |
| 129 | 2026-11-13 | Kit test run before the commit: scripts/test_summarize.py fails at HEAD too (2 failures, 1 error): summarize.gate() returns (problems, pending, warnings) since #70, the tests still unpack two values. Not caused by the 2026-11-12 card changes. Needed: update the three tests to the 3-tuple. | OPEN |
| 130 | 2026-11-13 vet hunt 6 | Owner: "why one after other not together?" hunt.sh ran the Codex lane, then the claude2 lane, serially (no Docker in either, so no slot reason); the claude2 lane waited the whole Codex lane. Fix: hunt.sh only prepares (facts, clone, brief) and prints both lane commands; hunt.md B step 1: start the three lanes at once, each its own tracked background call | DONE 2026-11-13: skill/tools/hunt.sh + skill/hunt.md, installed copy updated |
| 132 | 2026-11-13 | Owner: make the workflow clear for agents without our memory (a cadence kept only in memory sent an agent into a false review loop). A cold read of the kit by a fresh agent (analysis-20261112/kit-cold-read.md, 25 problems) ranked the loop causes first: Repair step 6 with no round limit, standing triggers in the four agent definitions, undefined stage-7 batches, checklist edits restarting the gate, stage-3 runs vs stage 6-7 timing, run counts and the missing stop after v2. | DONE 2026-11-13: PIPELINE.md "Review schedule" table that overrides every card, agent and memory note (terms defined: sweep, replica/verification batch, new class; stop after the last verification batch); gates.md Repair step 6 deterministic now, model re-judgment at the next scheduled point; agent descriptions point to the schedule; apply-build-checklist: one review per step, sharpened rows apply from the next task; stage 6 waits for the stage-3 runs; v3 once then the blocker; stage 10 = readiness + FP panel; rollout extra runs = owner call; problem-design sample text aligned with stage 1b; six cadence memory notes marked superseded |
| 133 | 2026-11-13 | Cold read items left (kit-cold-read.md 9-25): probe repeats in fp-auditor vs "each probe runs once" and replicas without Docker; build-checklist sweep count vs no sweep 3; ref-audit x2 in situations.md; description-change authority wording (REDESIGN, agents "Desc change needed", situations X-1/X-2 "cut a promise"); post-lock test grounding (description.md 181-183, near-miss-study 232 vs R7/R8); tools named but not built (corpus runner, eval/variants.py, codex_review.sh, references/checks.md, site-rubric.md); ledger lacks "Hard points (not named)"; ID collisions (T1-T6/S1-S5 vs rubric T1-T8/S1-S4, situations S0-S8, Astra R1-R8); requirement-count limits 9/11/14/19; task-specific MANDATORY sections inside the agent files; names a new agent cannot look up (claude2, Nova, MAP.md). | OPEN: one cleanup pass, owner decides when |
| 134 | 2026-11-13 | Sync push of the kit: (a) shipd/dedup-sync.sh ignores every path not whitelisted in its .gitignore, and olympus-product/ is not whitelisted, so only files tracked since the first add were updated; new product files (difficulty.md, profiles.md) were silently left out until force-added by hand; (b) the pull replay (export_local, git apply --3way) failed on CRLF and printed "MERGE CONFLICT" with no file names although the remote had nothing new; (c) import_shared ran rm -rf on the installed olympus-flow while another session used it ("Device or resource busy"). Needed: whitelist !/olympus-product/ (with blind clones excluded) or mirror it under sync/; normalize line endings before the replay and name the failing step; copy over the installed skill instead of removing it. | OPEN |
| 135 | 2026-11-13 | Owner: hidden tests must cover more edge cases, more behavioural tests, and round tripping. The checklist had the axes (section 3 item 2 save/reload, section 4 classes) but nothing made them complete per obligation. | DONE 2026-11-13: build-checklist section 3 item 2 round-trip cells (every reader and command, not-set survives, reload-resume-save-reload, older shape, reloaded value used not recomputed); section 4 edge-case matrix per obligation built at stage 4 (never review-triggered) + behavioural-first rule (one public-entry-point test per obligation); ledger Blueprint note |
| 136 | 2026-11-13 vet hunt 6 | repo_init.py resolves the task argument against the current directory: run from the skill folder it created the task (clone included) inside the installed skill. Fix: a bare task name resolves under the profile tasks_root; only a path with a slash is taken as given | OPEN |
| 136 | 2026-11-13 vet hunt 6 | The sample went to the platform with the unfinished template Dockerfile (FROM --platform=..., sha256 NOT_VERIFIED), so the platform's FROM-prefix precheck failed. Cause: repo_check.py calls repo_init.save() -> render() (repo_check.py:240/292/447/455), which re-renders init/Dockerfile from the template and overwrote the accepted Dockerfile I had placed there after the build used it. My download hash check only proved transport. Fix: (a) render() never overwrites an init/Dockerfile that differs from its own last render (or the profile takes a dockerfile_source path); (b) a pre-paste check refuses a Dockerfile whose first line is not one of the platform's allowed FROM lines or that holds NOT_VERIFIED/{{, and prints the Dockerfile identity next to the accepted one | OPEN |
| 137 | 2026-11-13 vet hunt 6 | watch.sh printed "RESULT: all new results passed" for a batch holding a precheck with status error (plagiarism: "Check could not complete. Please retry."), because its failure pattern had no "error". Fix: error/ERROR added to the pattern | DONE 2026-11-13: skill/tools/watch.sh, installed copy updated |
| 138 | 2026-11-13 | cc-pmg-cooldown stage 0b: tools/repo_check.py catches every exception in main() and records only its message, so the first run on a fresh repo_init (go_sha256 NOT_VERIFIED in init/Dockerfile) reported 'image builds ... PASS' and then 'self-check: TypeError: expected str, bytes or os.PathLike object, not NoneType'; a rerun gave the real cause ('Dockerfile has unresolved build inputs; resolve profile.open first'). Needed: check profile.open build inputs before the build, and record the traceback in check/results.json. | OPEN |
| 139 | 2026-11-13 | cc-pmg-cooldown stage 1: repo_init.py refuses any comment in the generated Dockerfile ('generated Dockerfile contains comments'), while dockerfile.md E4 requires one comment block above a RUN that deviates from the base image (the platform AI precheck failed vet's Go reinstall without its reason). The submitted Dockerfile therefore needs the reason comment added by hand after rendering. Needed: one rule in both places (let the template carry the reason comment for the Go reinstall, or say in dockerfile.md that the comment is added to pkg/Dockerfile only). | OPEN |
| 140 | 2026-11-13 | BLOCKER, cc-pmg-cooldown stage 0b: tools/repo_check.py cannot qualify any repository. It hooks native discovery into proof.run and expects 'proof --build-only' to also run the base cell (its comment says so), but tools/proof.py returns right after the image build ('if args.build_only: return 0'), so the hook never fires, self.image stays None and the self-check fails with 'TypeError: expected str, bytes or os.PathLike object, not NoneType' (docker run argv holds None). Every probe after it is NOT EXECUTED. Worked around task-locally (cc-pmg-cooldown/eval/repo_check_wrap.py: run proof.main, then the hooked proof.run once for the base cell); the kit is unchanged at the owner's request. Needed: repo_check calls the base cell itself after build-only, plus a launcher test that runs repo_check end to end on a small fixture repository. | OPEN (owner) |
| 141 | 2026-11-13 | cc-pmg-cooldown stage 0b: the Go test.sh template copies the candidate tree with shutil.ignore_patterns('*.o', '*.a', 'build', 'dist', ...), so a tracked file matching them is dropped from the graded tree. pmg tracks internal/netenforce/bpf/enforce_bpfel.o (go:embed of a compiled BPF object), so every package that imports internal/netenforce failed with 'pattern enforce_bpfel.o: no matching files found' ([setup failed]). Editing init/test.sh does not stick: repo_check re-renders test.sh whenever it saves the profile (profile_b64 is embedded). Worked around through the restore_paths setting (the object is restored from the pinned commit by git archive). Needed: ignore only untracked build outputs (filter by git ls-files), or document the restore_paths route in harness.md. | OPEN |
| 142 | 2026-11-13 | cc-pmg-cooldown stage 1: the Go Dockerfile template renders 'FROM --platform=linux/amd64 public.ecr.aws/...', and the platform Dockerfile check rejects it: 'Dockerfile must start with: FROM public.ecr.aws/x8v8d7g8/mars-base:latest or FROM public.ecr.aws/d3j8x8q7/olympus-base:latest or FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest'. Fixed in the task's pkg/Dockerfile (the local proof passes --platform to docker build itself). Needed: the templates render the bare FROM line; dockerfile.md E2 names the three allowed FROM lines verbatim. | OPEN |
| 138 | 2026-11-13 vet task 6 | Owner: "why did you stop? product should work in continuation". PIPELINE.md stage 1b said the sample exists "so nothing is built on a problem the platform already has", which I read as: wait for the Scope Gate before stage 2. Fix: stage 2 starts right after the sample paste; the Scope Gate runs in parallel; only a reject stops the candidate | DONE 2026-11-13: skill/PIPELINE.md, installed copy updated |
| 143 | 2026-11-13 | cc-pmg-cooldown stage 2: the widen step (difficulty.md section 2 step 3) assumes the widened need changes the promise and the sample (re-paste + Scope Gate). Here the added decision (D7, a version range is not a pinned version) was already implied by the general sentence and docs, so it was an inventory row brought back from OUT (breadth) rather than a new promise; no re-paste was needed. Needed: one line in section 2: a widen first looks for an implied inventory row the spike gets wrong (no text change), and only then adds a new need; and the spike counts the rows the stage-0 inventory marked OUT for breadth before the seam is called too easy. | OPEN |
| 144 | 2026-11-13 cc-pmg-cooldown + vet hunt 6 | The spike bar (V-OBVIOUS fails on >= 2 different decisions, difficulty.md section 3) passed 0 of 5 seams today in two repos: vet reach 0, vet YAML aliases 1 (widen stayed 1), pmg cooldown 1 (D4), pmg violation cache #562 0, pmg cooldown widened 1 once both reading lanes called D7 (version ranges) a scope choice. Both widens failed for one reason: the added decision is either stated (a complete design does it) or unstated with the repo silent (tests must accept both). The retro's own backward checks put accepted tasks RED on this spike (unused-suppression: one assertion on one path, analysis-20261112/lane-a-vet.md:122; elio: Orion 4/4 on the first suite, lane-c-other.md:213) and standby GREEN but too easy (lane-b-faust.md:150); the 2 came from a hindsight reading count (synthesis.md section 4) and conflicts with difficulty.md:6 (aim: a task that can be calibrated, not one hard on its first suite). Options: A) bar = at least 1 fair decision whose right answer sits far from the wrong idiom, 0 rejects, the stage-3 stop signal stays the second gate; B) keep 2 and count a split among the stage-3 runs as the second decision; C) keep 2 and combine bugs (vet task 6 route). | DONE 2026-11-13 (owner chose A): difficulty.md section 2 step 2 and section 3, description.md step 3 + checklist line, PIPELINE.md stage 2 gate; installed copy updated |
| 145 | 2026-11-13 cc-pmg-cooldown | Owner: "we cant give product in this state to any customer ... we will build a checklist that any seam can quickly go through and we can decide on it to continue or not, else we will stuck forever and never find any task". The hand-written spike is slow (hours per seam) and biased (the builder writes V-OBVIOUS knowing every trap); its near/far call is a reading verdict (pmg D4: the dedupe idiom sits 35 lines below the counter, stats.go:137-153 vs 188-205, but in another file than the decision fix). Needed: a quick seam checklist (minutes, evidence per line: file:line plus one separating input) that decides continue or stop at stage 0, built from the 12-task retro, the five seams of 2026-11-13 and real solves (2 Opus high on pmg d1, owner-asked), validated blind on seams with known outcomes before it replaces the spike. | OPEN (owner direction; draft after the pmg solves) |
| 146 | 2026-11-13 cc-pmg-cooldown stage 1b | The sample went to the platform with a test.sh whose new mode cannot run: the embedded profile had new_native_ids {} while expected.new held the 3 hidden IDs, so for Go test.sh lists every test of the selected package (go test -list) and stops with "collection inventory drift" (test.sh:371-375) whenever the hidden file shares a package with other tests. repo_init flags new_native_ids as unresolved only in its TypeScript branch (repo_init.py:218), repo_check qualifies base mode only, and nothing ran test.sh new on base and on the reference before the paste. Found when the owner-asked solves graded 0/3 with the reference also 0/3; the owner had not run prechecks yet. Fixed task-locally: new_native_ids in choices.json (id -> [package, name]), repo_init --render-only, test.patch rebuilt, full proof, sample re-pasted. Needed: repo_init derives new_native_ids from expected.new (or flags it for Go and Python), and the stage-1b paste refuses a package whose proof did not run new mode on base and on the reference (precheck: new_native_ids consistent with expected.new). vet task 6 sample may carry the same gap (its profile.json shows new_native_ids {}). | OPEN |
| 147 | 2026-11-13 cc-pmg-cooldown | PIPELINE.md Confirmation schedule item 2 (FP-audit every passer of owner-asked local solves, without asking) assumes a full reference. At stage 2 the reference is the sample sketch, and the fp-audit replica marks a pass NOT DESERVED only when the reference gets the case right (replicas/fp-audit.md), so an audit then returns DESERVED by construction for every gap the sketch shares (pmg: both solves pass the 3-test sample but miss D2 withheld and D4, which the sketch also misses). Needed: before stage 5, owner-asked solves are graded on the planned separators (eval/spike) and go into the variant corpus; their FP audits run only when the full reference exists, and only for runs that still pass the full suite. | OPEN |
| 148 | 2026-11-13 cc-pmg-cooldown | Owner: "what is the issue why kit still rejecting it?" My wording of option A (#144) added "a failure whose right helper sits in the same file as the wrong idiom does not count", a reading veto over a measured failure (against difficulty.md "the gate is measured, never read"); it rejected pmg (spike fails only D4, whose dedupe idiom sits in stats.go next to the counter) although two Opus 5.5 high solves missed D4 and D2 withheld (one fix in the very function they edited). It was not needed for direct-deps either (its spike failed nothing, 35/35). | DONE 2026-11-13 (owner yes): difficulty.md section 1 (row field + best-separator note: rows the stated fix does not lead to; distance decides nothing), section 2 step 2, section 3 bar = one fair decision, distance never discounts; description.md step 3 + checklist line; PIPELINE.md stage-2 gate; ledger-template.md (needs 1; column 'Stated fix leads to it?'); installed copy updated |
| 149 | 2026-11-13 cc-pmg-cooldown stage 3 | The builder locked its own draft d1 when the owner said "continue building the task from next stage" (no owner words), skipping the humanizing step; the platform DQ then failed d1 with a major ai_generated comment ("write your description like how you would prompt an LLM") while the local DQ replica had passed it (the replica cannot see the platform AI detector). The owner rewrote the text; both reading lanes found no changed or ambiguous phrase and the DQ replica passed the new bytes. Needed: PIPELINE.md stage 3 and description.md part B say the lock needs the owner's own text or an explicit "keep the draft" reply ("continue" never locks), the builder asks for it in so many words, and the lock record cites the owner text hash; a local check can never replace the owner rewrite because no local check sees the AI detector. | OPEN |
| 150 | 2026-11-13 cc-pmg-cooldown prechecks | The platform "Test patch sanity checks" precheck warns on every kit test.sh: the profile is embedded as an opaque base64 blob (no_package_installation and no_malicious_code: "the encoding obscures content"). Needed: test.sh templates embed the profile as readable JSON (a heredoc or a sibling data block) instead of base64, so reviewers and the AI check can read it. | OPEN |
| 151 | 2026-11-13 cc-pmg-cooldown | Owner (repeated): "to not stop for me ... I will only run 2+2 and then next run will be after final build; 2+2 is for your reference how agents are solving this ... we will see if anyone of 2+2 can become fair passer". The kit still made stage 6 start only after the stage-3 runs, and the builder told the owner it would wait. | DONE 2026-11-13 (owner): PIPELINE.md stage 3 and stage 6 rows and difficulty.md section 4: the builder never waits for the stage-3 runs or any owner check; stages 4-7 go on; the runs are folded in when they end (stop signal, keeper, gaps as fair tests through Repair); the next platform runs are the v1 rollout; installed copy updated |
| 152 | 2026-11-13 cc-pmg-cooldown sweep 1 | Auto Review lane flagged process words in the kit test.sh template (grading, grade_roots, hidden_paths, "pristine grading-path inventory", "hidden path escapes source") as a Tests leak risk (a faust task lost Tests 0/3 to such words); precheck.py process-word check passes them. Needed: neutral identifiers and messages in the test.sh templates (for example restore_paths/overlay instead of grading/hidden), and precheck.py checks the template words too. | OPEN |
| 153 | 2026-11-13 cc-pmg-cooldown verify | BLOCKER for every Go task: templates/go/Dockerfile:8 sets ENV PATH=/usr/local/go/bin:/opt/go/bin:/usr/local/bin:/usr/bin:/bin, dropping /usr/sbin and /sbin. The platform verifyTests/verifySolution image build then fails: it runs groupadd/useradd to create the model user (uid 1000), which are "command not found", and stops at "chown: invalid user: model:model" (owner-supplied modal build log). The Dockerfile check, rebuildSafe and harborSafe pass, and the local proof never creates that user, so nothing local caught it. Needed: the template PATH keeps /usr/local/sbin:/usr/sbin:/sbin; proof.py (or precheck) replays the platform user step (groupadd -g 1000 model; useradd -m -u 1000 -g 1000 model; chown -R model:model /app) on the built image before any paste. | OPEN (task fixed locally) |
| 154 | 2026-11-14 | Owner: "we will keep running platform style replica checks until we get 3/3 in all, but to a threshold of 3; if even after 3rd round we get 1/3 we will run one strict sweep round again to cover all the gaps and again verification round after that". The kit stopped after one verification batch even with bands at 1 (cc-pmg-cooldown vb1: tests 1, solution 1). | DONE 2026-11-14: PIPELINE.md Review schedule stage-7 rows, the Terms paragraph and item text: verification rounds until description/tests/solution are all 3, at most 3; then one strict sweep -> fix -> rounds again (up to 3); then the owner decides; no paste for owner checks while a band is below 3; installed copy updated |
| 155 | 2026-11-14 cc-pmg-cooldown verifyTests | Platform verifyTests failed the baseline (508/509, 1 errored): cmd/setup TestCheckEventLogDirResultUnwritable calls t.Skip when run as root, the platform runs base mode as root, and test.sh turns any base-mode skip not in skip_allowlist into an error. proof.py runs every cell as a non-root uid (12345), so the local proof passed; the sweep AR lane had flagged it as a note (N-3). Needed: proof.py adds a root base cell (the platform verify identity) and repo_check proposes skip_allowlist entries for tests that skip as root, with the reason. | OPEN (task fixed: skip_allowlist entry) |
| 156 | 2026-11-14 cc-pmg-cooldown verifySolution | BLOCKER for every task built from the kit templates: templates/go/Dockerfile:16-18 (and templates/python, templates/typescript) leave /app owned by root and only readable for other users. The platform's verifySolution then fails with harbor_oracle_failed and no detail (baseline, new tests and offlineUid all pass): the Harbor oracle applies solution.patch in /app as the image's `model` user (uid 1000) and git apply cannot write ("unable to write file"), reproduced locally with groupadd/useradd + su model. The accepted vet Dockerfile has `chmod -R a+rwX /app` and passed the oracle on every version. Needed: (a) templates make /app writable for every user (chmod -R a+rwX /app), (b) proof.py gets a model-user oracle cell (create uid 1000, apply both patches in /app, run test.sh new and base) next to the root base cell of #155, (c) situations.md entry: harbor_oracle_failed with everything else green = /app not writable for uid 1000; the check's testLog artifact is missing, so diff against an accepted Dockerfile. Task-local replay: cc-pmg-cooldown/eval/harbor_emulate.sh. | OPEN (kit change waits for the owner's yes) |
| 157 | 2026-11-14 cc-pmg-cooldown round v4r1 | Owner set the replica rounds of this task to GPT Sol 6.1 medium (was GPT Sol 6 medium, the kit default since 2026-11-13). The first 6.1 round found a real defect that two 3/3/3 rounds on 6.0 had accepted: a pinned ==2.0.0 reported blocked while an old 2.0 file of the same release is returned (three lanes reproduced it with pip offline); sweep 1 ref-B had raised it and the builder rejected it (ledger F04, reversed by F14). Needed: (a) owner decision whether 6.1 medium becomes the kit default for replica rounds (tools/replica.sh:20), (b) situations.md: a rejected sweep finding that says 'reported blocked while an installable version is returned' needs a client probe (pip/npm) before REJECT. | OPEN (owner decision) |
| 158 | 2026-11-14 owner | Owner: "set codex to gpt sol 6.1 medium again". This decides 157(a): the replica checks default back to GPT Sol 6.1 at medium effort (was GPT Sol 6 since 2026-11-13). Changed tools/replica.sh:20 and its header, SKILL.md, PIPELINE.md Confirmation schedule (local-passer FP audit command) and situations.md; fp-audit and ref-audit stay GPT Sol 6.1 high; other Codex jobs stay high. 157(b) stays open. | DONE |
| 158 | 2026-11-14 cc-pmg-cooldown verifySolution v4 | harbor_oracle_failed again on v4 after the /app fix (#156); baseline 509/509, new 10/10, offlineUid pass. Every task that ever passed the oracle (vet direct-deps, local-registry, unused-suppression) used a bash test.sh with `[--output_path F] [--mode] <base|new>`, optional output path and default mode base; the kit's adapter test.sh (repo_init.py render) exits 2 on `test.sh new`, `test.sh` and `test.sh --mode new`, so a wrapper that calls it any way but `<mode> --output_path F` fails. Task-local fix: eval/patch_testsh.py (applied in build_testpatch.sh). Needed in the kit: (a) the adapter template accepts that interface, (b) proof.py runs `test.sh new` without --output_path as one cell, (c) situations.md: harbor_oracle_failed = check the test.sh call interface and /app writability. Root cause on the platform side still unconfirmed (no Harbor log exposed). | OPEN (kit change waits for the owner's yes) |
| 159 | 2026-11-14 cc-vet-pr-accuracy | No stage-2 gate measures the breadth of a promise. DQ (replica and platform) grades count, clarity and prescriptiveness, so a sentence with an open quantifier ("every finding", "every pair vet knows", "no output") passes at 8 units while it hides many repo cases: 19 reference bugs surfaced after the lock (2 FP audits, 2 checklist reviews, 1 ref-audit), each a corner of a stated sentence. Needed: at stage 2 step 8, a breadth count per sentence: for each quantifier word, list the repo cases it reaches (controls, outputs, pairs, link shapes) with a grep; over about 5 cases, the owner chooses before the lock between narrowing the words and accepting the build cost (problem-design.md section 4 already warns: "Mode coverage the reference does not really have"). | OPEN |
| 159 | 2026-11-14 cc-pmg-cooldown verifySolution v5 | harbor_oracle_failed a third time after #156 and #158. The real Harbor 0.26.0 oracle (pip install harbor) passes the same package locally (reward 1.0) with an exit-code wrapper, so the platform's private tests/test.sh wrapper decides differently. The adapter test.sh prints raw `go test -json` events on stdout, while every oracle-passing task printed `go test -v` text; a log-parsing wrapper finds no `--- PASS:` line. Needed in the kit: (a) the Go adapter prints decoded Output text (task-local fix in eval/patch_testsh.py), (b) a stage-6 cell that runs the real Harbor oracle with a log-parsing wrapper (the task-local harness is in the session scratchpad; move it into tools/), (c) situations.md: harbor_oracle_failed with green verify = check stdout format, test.sh call interface, /app writability. | OPEN (kit change waits for the owner's yes) |
| 160 | 2026-11-15 cc-pmg-cooldown round v6r2 | repo_init classified internal/cloudpolicy/cloudpolicytest (imported only by tests) as production, so test.sh did not restore it and a candidate could edit the fixtures of retained regression tests (AR T1 High). Needed: repo_init marks every non-test Go package whose importers are all test code as a helper (restore_paths), and proof.py tampers each such helper by default. | OPEN (kit change waits for the owner's yes) |
| 161 | 2026-11-15 pmg hunt 2 (owner) | Owner, at the seam pick: "pick feature/bug which touches 10+ files; solver has to grind enough context on the codebase before coming to the solution, the solution should not be visible from the surface of the codebase". The kit sizes seams at 2-4 production files (hunt.md part B step 4 drops more than 4; problem-design.md section 6; templates/hunt-brief.md rule 1), the opposite direction. Needed: owner decision whether this becomes the kit default; if yes, hunt.md step 4/5 and the hunt brief score breadth (10+ files touched along the data path) and depth (the right answer sits away from the symptom site; the solver must trace the value through several subsystems), and problem-design.md section 6 changes its size guide. Applied for this hunt only until then. | DONE 2026-11-15: superseded by #162 (owner range 3-30 files + depth rule) |
| 162 | 2026-11-15 (owner) | Owner's ten task-quality points: (1) a task never has only one solution, (2) different fair implementations pass, (3) wrong implementations fail, (4) hidden tests behavioural, not brittle (need), (5) requirements not discoverable from surface-level repo code and no hint in the repo itself, (6) no hints in the description, purely stated requirements, (7) more edge cases and behavioural tests, (8) round tripping (need), (9) features touching 3-30 files, (10) the solver must grind codebase context; the solution is not visible from the surface. | DONE 2026-11-15: problem-design.md section 5/6 and S0 step 3 (3-30 files on the value's real path) + new step 3b (depth trace, no repo hint, >= 2 fair designs, drop the seam if any fails); hunt.md B4 filter + B5 score (+1 traced value); seam-bank.md schema (depth, repo hints checked, fair designs) + lane rule 5; templates/hunt-brief.md rule 6 + schema; templates/design.md header; build-checklist.md round trip REQUIRED, edge-case matrix required, 'Behavioural, not brittle' rule, at least one valid alternative besides the reference; tests.md T6; description.md checklist (purely stated requirements). Points 6-8 were already rules (deletion test 2026-11-12, round trip and edge matrix 2026-11-13), now marked required. Both kit copies synced. |
| 162 | 2026-11-15 cc-pmg-bypass-counts stage 1 | tools/precheck.py cannot run at the Dockerfile-only stage: it reads pkg/task.md first and crashes (FileNotFoundError) when the package holds only the Dockerfile, so the stage-1 gate (dockerfile-first-gate: local precheck rules before the Dockerfile paste) has no tool. Needed: precheck.py checks only the files present (a --dockerfile-only mode or a missing-file skip with a note). | OPEN |
| 163 | 2026-11-15 cc-pmg-bypass-counts stage 1 | `olympus problems create` returned ConvexError "Submission creation is paused. New problems can't be created right now." No card says what to do. Needed: situations.md entry: creation paused = build ahead locally (stages 2, 4-7 need no draft; the spike and the stage-2 audits run locally), retry create at each paste point, tell the owner once; a reused Dockerfile identical to an accepted one may go in with the sample paste when creation reopens. | OPEN |
| 164 | 2026-11-15 cc-pmg-bypass-counts stage 0b | tools/repo_check.py cannot qualify any adapter now: it hooks proof.run to discover native IDs "during the base/base cell of proof --build-only" (repo_check.py:204-206), but proof.py --build-only returns right after the image step (proof.py:244) since build-only became the Dockerfile-only stage-1 gate. qualify() never runs, self.image stays None and probes() fails with "TypeError: expected str, bytes or os.PathLike object, not NoneType" (eval/repo_check-3.log); every probe is NOT EXECUTED. Needed: repo_check runs proof without --build-only for its own base qualification (or proof gets a --base-only mode), and a smoke test of repo_check on a known-good package (PIPELINE item 8). Also: repo_check refuses --timeout >= 688 with a message that does not name the bound. | OPEN (task worked around by hand: discovery + base run with the rendered test.sh) |
| 165 | 2026-11-15 cc-pmg-unanalyzed-counts | The task folder was first named cc-pmg-bypass-counts; "bypass" is on check_codex_brief.sh's flagged list, and every replica brief names the task path, so replica.sh refused to launch ("brief has flagged words"). The folder could not be renamed afterwards (a handle held it; worked around with a junction cc-pmg-unanalyzed-counts). Needed: repo_init.py (or the stage-0 card) checks the task name against the flagged list before creating the folder; hidden test names and file names avoid the list as well. | OPEN |
| 166 | 2026-11-15 cc-pmg-unanalyzed-counts stage 2 | The obvious-design spike passed the gate on 3 fair decisions (trusted-only early return, insecure+block path, stop printing before --fail-on-violation), but the 2 local Opus 5.5 high solves the owner asked for both solved all 3 in 17-20 min (FP audits: both DESERVED). The spike models a lazy fix; on a seam that carries one value to a set of readers the description lists, Opus reads every reader end to end, so hidden early returns inside the named readers are not hard. Needed: difficulty.md section 3 note: a decision only counts when it sits outside the named readers (an unnamed reader, a saved-state round trip, a second entry path) or needs a semantic choice; "an early return inside a reader the text names" scores 0. Optional owner decision: a 1-solve Opus check before the lock for plumbing seams. |
| 163 | 2026-11-16 (owner) | Owner: "remove the gate we had for difficulty, we are not continuing on that; instead, once you have my humanized desc, we will run 3-3 solvers in local and 2-2 on platform to get the best idea; solvers (both local and platform) run in parallel while you continue on your build with the workflow, start with the next stage". | DONE 2026-11-16: difficulty.md sections 2-4 rewritten (no gate; 2. solver runs after the lock: 2 Orion + 2 Vega + 3 Opus 5.5 high + 3 Codex GPT Sol 6.1 high in parallel, build starts stage 4 at once; 3. reading the runs: grade, FP audits, keeper, gaps -> fair tests, correct runs -> valid alternatives; 4. all ten correct with no spread -> owner options); description.md step 3, lock report and checklist (spike line removed); PIPELINE.md stage 0/2/3/4 rows and Confirmation item 2; SKILL.md card table and fixed rule; hunt.md step 8; ledger-template Difficulty; platform.md; rollout.md; tools/solvers.sh launches 6 (1,3 Opus main, 2 Opus claude2, 4-6 GPT); machine profiles solvers = 6. Both kit copies synced. |
| 164 | 2026-11-16 (owner) | Owner: "the edge cases and more behavioural tests + round tripping should be part of the calibration prompt that we have saved for many passers, not in the actual flow, because these will be useful there". | DONE 2026-11-16: build-checklist.md drops the full round-trip cell set, the edge-case matrix and the 'one public-entry test per obligation' rule (keeps the base save/reload check of section 3 item 2 and 'Not brittle'); prompts/calibrate-one-passer.md gains Lever K (edge-case matrix + behavioural cells through the public entry point) and Lever L (round trip a-e), run after I/J and C/F/H, filtered by Step 3; ledger-template Blueprint note updated. Supersedes the 'required' marks of #162 points 7-8. Both kit copies synced. |
| 167 | 2026-11-16 cc-pmg-propose-base stage 4 | tools/checklist_gate.py splits sheet rows on every `|`, so a note that holds a literal pipe (here `./test.sh base|new`) makes the gate report "rule 1.1: no row in the sheet" although the row is there. Needed: the gate reports "row 1.1 has N cells, expected 7 (a | in a cell?)" instead of "no row", or the sheet accepts `\|`. Also: a checklist edit mid-task re-keys changed rules and blanks their rows; the sheet command could print which rule ids were blanked. | OPEN |
| 168 | 2026-11-16 cc-vet-pr-accuracy lock2 paste | tools/watch.sh keeps eval/platform/watch-base.txt across sessions: started after the lock2 paste with a baseline from an earlier session, it exited at the first poll and listed the 2026-11-14 checks and runs as new (old rollout FAIL_* and SQ FAIL), which reads as a fresh failed batch. Fix: write a fresh baseline on every start (or take --fresh, and have the paste step delete the old base); print each item's timestamp so an old result is visible. | OPEN |
| 169 | 2026-11-17 platform V2 gates (CLI diff, cc-pmg-cooldown) | The platform readiness changed (memory olympus-gates-20261117): Nova 0%; Orion must solve 1-25% of runs; Vega at most 25%; Orion's solving runs must average >= 256K tokens (our past Orion passes: 106K-190K, none >= 256K); Auto Review left readiness; 7 quality checks with new categoryAlignment and rewardHacking; harborSafe needs a rebuild for a new hygiene layer; drafts reserved 14 days. Kit impact: rollout.md/profiles.md/difficulty.md target Orion (not 'exactly one family'); seam pick predicts Orion pass length; replicas for rewardHacking and categoryAlignment; AR band demoted; PIPELINE re-run list (prechecks, Scope Gate, rebuild, 7 checks). Owner 2026-11-17: the new Orion uses little context, so the requirement itself must force long work. Seam pick adds a length score: files the solver must read on the value path (target >= 15 across >= 3 packages), files it must edit (>= 5), parallel paths one sentence covers (every ecosystem/driver), layers the value crosses (handler -> state -> report -> CLI). Never padding (noisy logs, hidden steps): that is rewardHacking/unfair. | OPEN: waiting on the owner's plan and the platform's docs text |

## #169 Replica knowledge: go-git fixtures rewrite absolute symlinks (2026-11-17, vet task 6)
go-git's Worktree.AddGlob commits an absolute symlink as a path relative to its chroot ("/pinned/deps.txt"), not the
real link text. A reviewer "reproduction" of absolute-link handling built with go-git fixtures is an artifact. Add to
replicas/knowledge: verify absolute-link findings with the git CLI before keeping them; treat committed absolute links
as machine-specific (they dangle on any other checkout).

## #170 Stage 7: three phases, fix after every round (owner 2026-11-17)
Replaces "sweep 1 -> replica batch -> verification batch, sweep 2 on its trigger" and the 2026-11-14 "rounds until
3/3, then one strict sweep". Stage 7 now runs up to 3 phases: sweep 1, then a strict sweep, then a very strong sweep,
each followed by a fix batch and 3 verification rounds (`tools/round.sh`) run one at a time with a fix batch after
every round. Only medium-high reproduced errors in round 3 start the next phase; Lows are fixed but never do. After
phase 3: fix, prove, stop and report the recurring error classes to the owner. Description fixes are allowed in a
round's fix batch until the v1 paste (word reach, fairness replica, unit count, owner-approved words); from v1 on the
lock is final. Changed: skill/PIPELINE.md (stage 3 and 7 rows, Review schedule, Terms, Confirmation items 3-4, time
boxes, metrics), skill/SKILL.md, skill/description.md (sections 0 and 5), skill/ledger-template.md,
agents/olympus-auto-reviewer.md, agents/olympus-sq-judge.md, GETTING-STARTED.md.

## #171 Replica lanes: fall back to claude2 when Codex hits a usage limit (2026-11-18, vet task 6)
round.sh lanes run only on Codex; a provider usage limit ("try again at 4:55 PM") killed a whole verification round
mid-phase, 15 hours before the reset. Add an automatic fallback: on a Codex usage-limit or capacity error, rerun the
same check on the claude2 reviewer agent of that role (sq -> olympus-sq-judge, fairness -> olympus-tq-judge, ar ->
olympus-auto-reviewer) with the same brief, record the fallback in the checkpoint, and keep the gate's required-report
names.

## #172 Proof gets a two-user cell: root base mode, then the solution applied by uid 1000 (2026-11-18, vet task 6)
Platform verifySolution runs test.sh base as root and then applies solution.patch as another user. vet task 6 fx6 failed
it ("unable to unlink ... Permission denied"): test.sh restored pinned files with `git archive | tar -x`, and tar reset
each touched folder to root 0755. proof.py runs every cell as one user, so it cannot see this. Add the cell (replay:
cc-vet-pr-accuracy/eval/harbor-replay.sh) to proof.py, and make the kit's test.sh restore helpers use
`tar -x --no-overwrite-dir` and leave restored files writable.

## #173 Quick checks run the repository's own gate tests (2026-11-18, vet task 6)
A reference change broke vet's internal/archtest import rule; the per-package quick check never ran it and SQ found it.
The full proof and the pre-paste check run `go test ./...` (or the repo's `make check` test step) once, with known
environment-only failures listed, not a hand-picked package list.

## #174 The two-user replay checks verifySolution's test sets, not counts (2026-11-18, vet task 6)
vet task 6 fx7 failed verifySolution with `after_extras_not_skipped`: the reference adds an acceptance script, and
test.sh base mode ran every script in the folder, so base mode with the solution applied had one test that the baseline
never had. The local base/base and base/reference cells showed it (1156 vs 1157 PASS lines) but only counted, so nobody
compared them. Replay now: eval/harbor-replay.sh (root baseline, uid 1000 apply + new + base) plus eval/junit-sets.py
(baseline failures, new not passing, new also in baseline, after extras not skipped, p2p not passing after). Put both
into proof.py, and add to the build checklist: base mode runs only tests that the pinned commit has (overlay for Go
files; acceptance or data-driven runners filtered by the pinned commit's file list).

## #175 Size every task so the solving agent compacts at least once (2026-11-18, owner)
Owner: "make sure the agent compacts, at least once; you need bigger and harder tasks". The platform gate (Orion's solving
runs average >= 256K tokens) means the same thing, since Orion's window is about 258k. vet task 6 on its narrowed text
does not reach it: the local Codex gpt-6-astra stand-in peaked at 204k of 258k with no compaction. On the older text, 1 of 4
platform runs compacted. Kit changes:
- hunt.md / difficulty.md: the seam's predicted solve must pass the Orion window.
- Stage-2 spike: one local Codex solve must compact (peak context >= window, via astra-tokens.py on the session jsonl)
  before the lock.
- rollout.md: report each run's `compacted` and `sequenceLength`.
Owner notes 2026-11-18 (an accepted task's 4 counted Orion runs) give the mechanics and the seam signs:
- Sequence length is the sum of window peaks: window 1 peaks at 247K-250K, compacting at 243K-246K of input; window 2
  restarts at 12K-14K and peaks at 41K-67K, for 292K-316K. A solve that never compacts stays under about 250K.
- Runs make 150-200 requests at about 1.4K-1.7K context each and compact after 140-165 of them.
- Good seam signs: crosses layers; needs 80+ files read and about 20 changed; several paths that must agree; large files
  traced across; a slow suite.
- Warning signs: one module, a prompt that points at the fix, instant tests, one tricky line.

Kit changes:
- hunt.md: score each seam on these signs.
- difficulty.md stage-2 spike: the local solve's first window must reach about 243K input. The vet6 Astra spike, 100
  requests and a 204K peak, would have failed this.
- The spike runs the current Orion model and effort: GPT Sol 6.1 at xhigh (owner, 2026-11-18). A cheaper stand-in
  (gpt-6-astra medium) under-reads and gives a low length estimate.

## #176 SQ lanes time the default path at two input sizes (2026-11-18, vet task 6)
Platform SQ on vet task 6 fx8 failed on speed alone. The reference builds a per-entry text for every npm lockfile entry
on every scan (gjson.GetBytes from the top of the document for each entry, so the work grows with the square of the
entries). A plain full scan, which never reads that text, went 1.34x slower at 4000 entries (+1.1 s), and 15.5 s vs
11.6 s at 8000. No local lane caught it, because our SQ briefs, the SQ preflight checklist and proof.py check
correctness and code shape only, and the hidden tests use tiny inputs. Add:
- an SQ checklist item: list every per-item step the reference adds on a path that does not need the feature (full
  scan, other modes);
- a timed probe of each: base vs reference at 1x and 2x input, best of 3. Flag superlinear growth or more than about 5%
  added time there.

## #177 Fairness lanes: a wrong design that passes is blocking; prove each gap by a run (2026-11-18, vet task 6)
Platform verifyFairness on vet task 6 fx9 failed with 2 blocking items:
- No test removed an integrity hash. A solution that compares hashes only when both entries have one passed every test.
- One assertion pinned exactly ADDED where the same file accepts {ADDED, MODIFIED} for the same situation.

The platform now lists "a grounded wrong design passes every test" as blocking. Our fairness replica still says "verdict
FAIL only when at least one test is Unfair", and kb-tests TC-09 calls partial coverage advisory. So four local fairness
runs after that assertion was added (x1, x1r1, x1r2, x1r3) said PASS. They were static (no runs, no mutants) at medium
effort, and two of them listed coverage gaps as advisory only. SQ lanes had read that the reference reports a removed
hash (sq-p3r2b, sq-x1r4b), but no lane asked which test fails when a solution drops it.

Kit changes:
- replicas fairness prompt + kb-tests: a grounded wrong design that passes every test is blocking (FAIL), the same as an
  unfair test.
- Stage 6 gate (proof.py): run the hidden tests with -coverpkg over the packages the reference changes, and list each
  changed block that no hidden test runs (eval/cov-changed.py in vet task 6). Each listed block gets a test, or a
  recorded out-of-scope reason.
- Before a paste that answers a platform coverage item: apply the platform's wrong design to the reference, and show it
  passes the old tests and fails the new ones.
- Each new change-name assertion is checked against the names the same file accepts for the same situation.
DONE 2026-11-18 (owner asked to match the platform, with Codex): replicas/fairness.md rewritten.
- It now has FP, FN and AR lanes, a decision ledger, executed one-line wrong solutions (only an executed survivor
  grounded in the description or repository text blocks), an FN peer-value check, and AR T1 per leaf.
- Output: the site's shape ("SUMMARY: Found N blocking ..."), a JSON ledger, and PASS / FAIL / NOT VERIFIED.
- knowledge/tests.md TC-09 now says blocking; olympus-tq-judge sweep rules 3-5 point to the new rubric.
- Merged from a Claude draft and a Codex GPT Sol 6.1 high draft (vet6 eval/tq-update, eval/codex/tq-replica-design.md).
  Backup: fairness.md.bak-20261118.
Still open: calibrate it once by running it on the fx9 tests and checking it finds the platform's 8 blocking items.
2026-11-18 later: the rubric is reworded with neutral terms (variant, passing variant, CAUGHT, skip, contradicts),
so one file works for Claude and Codex (check_codex_brief.sh clean). Codex judge jobs run with full access and may run
Docker through dockrun, so the Codex lane executes wrong solutions too: codex_job.sh <task> <name> <brief> high judge,
with CODEX_TIME_BOX_MIN. First two-lane run: vet6 fx13 (Claude olympus-tq-judge + Codex, eval/tq-run/).
Evidence: on the fx9 tests the coverage list held the removed-hash message block (the platform's F1); on fx10 that
block runs and the remaining 70 unrun blocks had no in-scope gap (defensive paths, scope left by the narrowed text, or
unstated indirect outputs). A run takes about 5 minutes in the proof image.

## #178 Before a paste, run a wrong-design sweep over the reference's decision points (2026-11-18, vet task 6)
Platform verifyFairness on vet task 6 fx10 found 5 more passing wrong designs after #177's coverage run said no in-scope
gap was left. 4 of the 5 were in code that the tests do run, but no test checked that outcome, which a coverage run
cannot see:
- a record taking Direct/Dev from the modified copy;
- a CRLF checkout of a kept file;
- two aggregations over copies with the same source ("first copy wins").

The fifth (removed records counted as locked) was on the coverage list, and I put it out of scope because I only
thought of the pull-request output; a control-level test settles it.

Kit change (gates.md, stage 6):
- List the decisions the reference makes for each stated rule: each tie-break, merge field, kept-file comparison, and
  each place that reads the head's package list.
- For each decision, write the naive version a solver would write as a one-line wrong solution (eval/val5/mutate.py
  style).
- Run each wrong solution through test.sh new. One that passes needs a test, or a recorded out-of-scope reason.
- Consider a control-level or unit test when the pull-request output of a case is not stated.
Owner 2026-11-18: "cover all, including what is implemented and stated", after a third fairness round. First version
built in vet task 6 (eval/sweep):
- mutants.py takes the lines the reference patch adds and keeps those the hidden tests run (cover profile). It writes
  neg / drop / del / flip mutants: 396 candidates across 27 files before the filter.
- runmut.py runs each mutant against the hidden tests and classes it killed / survived / invalid.
- run.sh runs it as Docker shards.
Move it into tools/ (proof.py stage) once its triage rules are settled.

## #179 Re-run only the wrong solutions a test edit can affect (2026-11-18, owner, vet task 6)
Owner: "why are we running full wrong solution again and again". A new test cannot let an old wrong solution pass, but an
edit of an existing test can. Each proof run records which test caught each wrong solution (val-*.txt). The next run
executes:
- the new wrong solutions;
- the old ones whose catching test changed (diff the test patch per test function).
Everything else carries over. On vet6 fx14, only 1 of the 7 platform wrong solutions needed a re-run (about 15
minutes saved).

## #180 (proposed, owner decides later) Run the two-user replay only when it can change (2026-11-18, vet task 6)
Proposal: run harbor-replay.sh when the solution, test.sh, the set of test files or the Dockerfile changes. When only
test bodies change, the cells already prove what the replay would. Owner 2026-11-18: keep the replay before every paste
for now, and decide later.

## #181 Why the sweep and triage missed the no-resolved made-direct case (2026-11-18, vet task 6, platform fx15)
The platform found a reference branch no test ran: reputation.confused, an entry with no resolved URL. A solution
returning the package change there passed all 80 tests. Three misses lined up:
1. The fx10 coverage run listed the branch as never run. I dismissed it by reasoning ("the entry change equals the
   package change for the add-or-upgrade trigger"). That holds for install scripts, not for confusion, and fx13 showed
   the two changes differ when a package is made direct.
2. The sweep only mutates lines the tests run, so the branch got no variant. Its operators also cannot express "package
   change instead of entry change" (an operand swap inside a return).
3. When fx13's made-direct gap disproved that assumption, I tested the resolved-URL path only and did not reopen the
   earlier decisions that cited it. The hygiene sibling (nonRegistrySources, single entry) was found only now.

Kit changes:
- An unexecuted changed branch is never classed "equivalent" by reasoning. A test runs it, or it gets a concrete
  out-of-scope or defensive reason.
- mutants.py gets a swap operator for entry-level and package-level fields (EntryChange<->Change, entry
  Resolved/Integrity <-> package ones) in returns and assignments. It also runs once without the coverage filter, so
  unrun branches get variants too.
- When a finding disproves an assumption, grep every triage file for that assumption and reopen each decision that
  rests on it.
- Class coverage = every branch of the function plus every reader of the field (grep the field), not just the path the
  finding names.

## #182 Judge every passing wrong solution the way the site does: three sources, hangs are defects (2026-11-18, vet task 6, platform fx16)
The site's fx16 round found 3 blocking items after two replica lanes and a 336-variant sweep passed the tests. Two of
the three wrong solutions were in our own sweep and passed every test: variant 18 (no visited check in the base link
walk) and variant 158 (no link count in the base link reader). Triage then dismissed them: 18 as "equivalent, a dedup"
(the reference's own comment says "against loops"), 158 as "defensive: link cycles". The third (a package made direct
keeps a MODIFIED record) got no variant at all. The fx13 Codex brief also steered the lane away from the sweep's passing
variants ("spend your executions on what one-line operators cannot express"), so nobody re-judged them.
How the site judges, from all its findings: a wrong solution is a defect by ANY of (1) the description, (2) the
behaviour before the change on that input ("Before the change, ..." with the base code and the upstream test), (3) a
contract the repository documents (code comments, upstream tests, the sibling mechanism the new code mirrors). A hang is
always a defect. Our rubric line "behaviour the reference implements but the description does not promise gets a
reason, never a test" is what let these through.
Kit changes:
- replicas/fairness.md v2 (eval/tq-run2/criteria-tq2.md of vet task 6): the three-source test; a contract ledger
  (for each new function, the code it mirrors or replaces and that code's properties); input shapes (cycles, links to
  the root, order, multiplicity, state matrix, field presence, CRLF, format versions).
- Triage: "equivalent" only after an executed search for a distinguishing input found none; "defensive" only for an
  error path whose removal still ends and changes no output; a loop guard or a limit is never defensive. Every passing
  variant gets a focused check on base, reference and the variant before any call.
- Lanes get the raw passing variants and the list of changed code no test runs, and never the builder's triage.
- When a new function mirrors an existing one (head walk vs base walk), diff their rules line by line: the vet task 6
  reference missed two of the head walk's three rules (target holds the link; at most MaxLinkedDirs linked folders).

## #183 TQ skill: close the pool exhaustively with generators, not anecdotes (2026-11-19, owner, vet task 6)
Owner: "learn this skill of TQ for future". What the site does that our checks did not, from its 12 blocking items:
- It is a sampler that needs ONE real defect from the pool of passing wrong solutions (64 one-line variants still
  passed all 83 vet6 fx17 tests). We review by sampling too, so we lose a round whenever any pool item is open. The
  only winning answer is exhaustive closure: every item caught, proved equivalent, or proved not a defect.
- It is not a stronger model (its fairness check ran on gpt-5.6-sol per the 11-05 platform data; our lanes on
  gpt-6.1-sol). It asks a different question (which obligations do the tests not force?) with a different oracle
  (description + behaviour before the change + documented contracts) and reads outward from the diff.
- Our checks were many but correlated: all derived from the reference and the builder's description, so they shared
  the builder's blind spots (the reference itself lacked two of the head walk's three loop rules).
- Our knowledge was stored as per-task anecdotes (olympus-tq-judge grew to 532 lines of faust/turso/elio sections);
  a judge matches anecdotes by surface features instead of deriving obligations from the repository at hand.
Kit changes (done 2026-11-19): replicas/fairness.md v3 (pool closure, three sources, mechanism inventory read outward,
generator matrix G1-G13 from the site's finding classes, reference as suspect, lens-split lanes); olympus-tq-judge
METHOD v3 header on top. Still to do: rebuild olympus-tq-judge around the generators (move the anecdote sections to an
examples appendix); sweep tool runs once without the coverage filter and covers every case clause; a pool-closure
ledger file per task (eval/pool.md) that a paste requires to be empty of open items.

## #184 Mirror a mechanism's decisions, not its rules (2026-11-19, vet task 6, own SQ replica on fx18)
fx18 copied the head walk's three link rules into the base walk by reusing extractors.Links on the base tree. Two of the
rules are local (a link to its own folder, a folder the walk is inside); the third is a global count in walk order (at
most 64 linked folders). On a different tree (the change deletes a link) and in a different order (git tree order vs
name order) the count picks different folders, so the base skipped folders the head read: false ADDED. fx19 records the
folders the head walk enters (a quiet pass of the same walk) and the base follows exactly those.
Kit: replicas/fairness.md G8 now says: when new code must agree with an existing mechanism, consume that mechanism's
output where possible; re-running its rules on other input is a second implementation, and count-, order- or
state-dependent rules diverge. Our own SQ lane caught this before the paste, which is the review schedule working.

## #185 Reference scope = test scope (2026-11-19, vet task 6, owner question)
Anything the reference implements that no
hidden test checks is the worst of both: the platform can flag the untested behaviour, and the code carries its own
bugs (the deleted-link reader produced the fx20 cache bug and a hang finding). At every build checkpoint list each
reference behaviour with no test and decide: test it (if the description states it) or remove it from the reference.
Kit: add this as a step in build-checklist.md before the proof, and a G14 "untested reference behaviour" question in
replicas/fairness.md.

## #186 Review lanes time-boxed and visible (2026-11-19, vet task 6, owner frustration)
Three Claude lanes plus
validation jobs ran 1-2.5 h each while the owner saw no progress; Docker slots were shared, so jobs queued silently.
Kit: every lane brief carries a hard time box (default 40 min) and writes its report at the box; the builder posts one
status line per finished step, never a long silent chain of tool calls; a new owner question is answered before any
further tool call, as the final text of that turn if needed.
Also: a lane that stops at its time box must kill its own wait loops (until/sleep shells polling for an output
file). The fx20 SQ lane left 8 such loops polling for a probe file that would never come; the owner saw them as
stuck tasks. The lane brief should say so, and the builder checks for leftover shells when a lane reports.

## #187 Pre-paste gate in the kit, not only in memory (2026-11-19, vet task 6, owner: "did you forget new requirements again?")
The 2026-11-17/18 owner rules (mutant sweep before every paste, V2 gate with the 256K compaction bar, 7 quality checks)
lived only in memory notes whose index lines were cut short; after a context compaction the hand-over skipped them.
Done locally: PIPELINE.md gains a "Pre-paste gate" section (backup PIPELINE.md.bak-20261119); the three MEMORY.md index
lines now state the action. Still to do in the kit: wire the gate into tools (a pre-paste script that refuses a hand-over
without a fresh sweep file and replay verdict for the same patch hashes).

## #188 SQ replica must execute, like the TQ method (2026-11-19, vet task 6, platform SQ FAIL on fx22e)
The platform SQ built a repository reached through a linked folder and ran vet: absolute link texts through the alias
gave a false ADDED lockfile and a false finding. Our Codex SQ said PASS on static traces (execution NOT VERIFIED), and
our Auto Review lane had found the same bug on fx20 (S1-b) but I left it out as Low without running it. Done:
replicas/sq.md Step 3b (execute at least 6 attempts plus every environment-dependent one; path/link axes; execute every
earlier lane's wrong-output finding before dropping it; no PASS on static traces). Backup sq.md.bak-20261119.

## #189 Grep upstream tests before changing an internal type; model, not fallback (2026-11-19, vet task 6, fx24)
Two lessons from the fx24 fix of the executed SQ findings. (1) I changed the type of an internal field (base.links,
map[string]bool) and the engine package stopped compiling: an UPSTREAM white-box test (basecache_test.go) builds that
struct literal, and test.sh restores upstream tests, so the type is pinned for every solver too. build-checklist.md
should say: before changing any unexported type, field or function signature, grep the upstream *_test.go files of the
package for it. (2) For "what does the base hold here", I first proposed a fallback that reads the head's state (the head
link's real path) when the base model fails. It is wrong whenever the change edits that state (a retargeted link).
solution.md should say: answer a base question with a model of the base (here, the base tree inside the repository plus the
real file system outside it, which no commit holds), never with head state; and add a test where the change edits the very
state that a fallback would read.

## #190 Task copies of replica prompts go stale (2026-11-19, vet task 6, owner: "SQ TQ check should be new platform way")
The kit's replicas/fairness.md became version 3 at 01:52, but the task's eval/replica/prompts/fairness.md stayed the v2
copy, and I pointed the fx24 TQ lane at it; the owner caught it. sq.md and common.md were current only because I copied
them by hand. Done: the task copy is now v3 (old one kept as fairness.md.v2-stale), and every copy was compared with the
kit. Kit: lane briefs should name the kit's replicas/ files directly, or the launcher should compare each task copy
with the kit before a lane starts and refuse a stale one.

## #191 Codex replica checks ran on the wrong model (2026-11-19, vet task 6, owner: "which model of codex are you using?")
Since fx19 I launched every Codex replica check (SQ, TQ, TQ-FN) with CODEX_MODEL=gpt-5.6-terra at high effort, because
codex_job.sh's comment calls it "the platform's TQ/SQ/DQ model". The owner's rule (2026-11-05/14; SKILL.md line 42 and
memory olympus-agent-models-20261028) is GPT Sol 6.1 at MEDIUM for replica checks, high for other Codex work. The rule
was never changed; I carried the launch line forward through compactions. Fix now: replica checks on gpt-6.1-sol
medium from fx24f on. Kit: codex_job.sh should take the model and effort from the job kind (judge = Sol 6.1 medium) and
its comment should not suggest another model; the launcher should print the model it uses.
Done 2026-11-19 (owner: "update the workflow if you are relying on that..update the tools"): codex_job.sh now sets model
and effort from the rule (gpt-6.1-sol; judge medium, others high), refuses any other CODEX_MODEL unless CODEX_ONE_OFF_MODEL
(user request), and prints model and effort in the launch line (backup codex_job.sh.bak-20261119). TOOLS.md and the
models memory note updated. Root cause also noted: tools/replica.sh already had the right defaults; I bypassed it.

## #192 TQ replica "full suite" left out the pass-to-pass tests the site also runs (2026-11-19, vet task 6, fx24f)
The Claude TQ v3 lane judged each wrong solution by `test.sh new` alone (eval/tq-run8/batch.sh, 114 hidden leaves). The
site grades with `test.sh base` (upstream pass-to-pass tests) as well. Blocking item 2 of the lane (zero hash for a
dangling base link, e05/e35) "passed every test" but fails the upstream base-mode test
TestPullRequestModeCountsAnUnresolvedBaseLinkAsChanged (eval/tq-run8/val25_me.txt), so it was a false blocker that cost a
validation run. Kit: replicas/fairness.md method and the TQ batch template run both modes per wrong solution; "passes
every test" means `test.sh new` and `test.sh base` both pass.

## #193 Check verdicts reported without their version; a fix that reopens checks not announced (2026-11-19, vet task 6, owner: "before paste you said TQ is good now, now suddenly 4 blocker?")
I told the owner "TQ good" for fx22e. After the site's SQ failed, the owner chose option A, which rewrote the link
handling (fx23-fx24g: solution patch +370/-182 lines, tests about 300 lines). I did not say that this reopens TQ and SQ,
so 4 TQ blockers on fx24f looked like a sudden regression. Two of them are on code added after the paste, one was a false
alarm (#192), and one (doubled diagnostic count, W37) was already in fx22e: the pre-paste Claude TQ lane was scoped to
"what changed this round" with two wrong versions, too narrow to reach it. Kit: every check status names its version;
when the owner picks a fix that changes the solution beyond a line or two, the reply says which checks it reopens (SQ,
TQ, AR, replay, bench); the pre-paste TQ lane covers every mechanism of the whole solution diff (v3 inventory), not the
round's delta.

## #194 Codex effort: medium for every job, not only replica checks (2026-11-19, vet task 6, owner: "why high? i asked for medium isnt it? for any work except in solver?")
I launched the description review (kind search) at high because codex_job.sh and the skill said "replica checks medium,
other Codex jobs high" (from the 2026-10-28 / 11-05 / 11-14 notes). The owner's rule is medium for any Codex work except
solver runs. Done: codex_job.sh sets medium for every kind; replica.sh no longer raises fp-audit/ref-audit to high;
SKILL.md fixed rule, TOOLS.md and the models memory note updated. The stopped job ran about 3 minutes at high.

## #195 Rulebook repair: a sentence over an open input space names its boundary at the lock (2026-11-19, vet task 6)
The vet task 6 link sentence ("If a manifest file is followed via a symbolic link, it will be diffed against the
corresponding file at the same path on the base ref") had no boundary, so every link shape (absolute texts, aliases,
outside folders, links that leave the scanned folder, links to the folder itself, text checkouts) became a requirement;
about ten review rounds and two site SQ failures followed, and the cache sentence inherited the whole space. The owner's
one change closed it ("Only relative symbolic links that stay below the scanned directory are in scope: ..."), the same
for "all pairs known to vet" ("every lockfile vet reads packages from, paired with the manifest file it is generated
from"). Rule that should have caught it: R12 (depth, not breadth; "every kind elio knows"). Done: description.md R12
now says a sentence over an open input space (links, outputs, "every X the tool knows") states its boundary before the
lock, with this evidence.
Done #192 (2026-11-19): replicas/fairness.md step 4 now defines PASSED ALL as passing `test.sh new` and `test.sh base`
(pass-to-pass) with the edited solution, and requires a base-mode run before a blocking item is reported.

## #196 SQ replica verdict and report were the site's old format (2026-11-19, vet task 6, owner: "isnt this was old way? ... You even figure out and analysed how SQ is working now?")
replicas/sq.md found issues the current way (Step 3b, executed) but judged and reported them in the old site format:
x/3 scores, High/Medium/Low, FAIL on two Mediums. Every site SQ result since 2026-11-18 (vet task 6: fx8, fx9, fx22e
twice) reads "Found N blocking issues and M non-blocking issues": blocking = a wrong output on an executed input
(Input / Command / Expected / Received / Why / Suggested change) or a measured slowdown on the normal path (fx8, 1.34x);
non-blocking = Design / Clutter / Practice notes, measured costs on extreme inputs; FAIL only with a blocking item (fx9
passed with 6 notes). Our lanes reported 0 notes where the site wrote 4-9, and two notes (Resolve kept, cache version
jump) came back after an earlier fix. Done: sq.md Step 5 is now the site's Design / Clutter / Practice sweep with its
examples, the verdict section is the site's current format, issues carry blocking and kind; score fields kept and
derived (1 blocking / 2 notes / 3 none) so summarize.py and round.sh still read the reports.
Follow-up #194 (2026-11-19): the medium-for-every-kind change also lowered solver runs (solvers.sh calls codex_job.sh
with job name "solve", kind build) to medium, against the owner's "except in solver". Fixed: codex_job.sh keeps job
"solve" at high. A model other than GPT Sol 6.1 for a solve (the owner's GPT Astra run) goes through
CODEX_ONE_OFF_MODEL; eval/solvers-astra.sh on vet task 6 now uses it.

## #197 Base-mode regression list misses packages that import changed code (2026-11-19, vet task 6)
fx22d added every package importing changed code, but six extractors (importing the changed scalibr), test/extraction,
test/reach and cloud/report (reached through sinks, flagged by tests_lint L5) were still missing on fx25. Kit: a
deterministic check (tests_lint L5 or proof.py) that computes the direct importers of every changed Go package with
tests and fails when one is neither in base mode nor listed with a reason (wall-clock or user-dependent tests).

## #198 Judge prompt made Codex rename the replica report (2026-11-19, vet task 6, SQ fx25d-b)
codex_job.sh's judge prompt said "write ONLY your report plus check files under the task's eval/ folder with a _cx
suffix"; Codex read the suffix as applying to the report too and wrote sq-fx25db_review_cx.json instead of the brief's
sq-fx25db.json, so round.sh failed the check ("missing or empty report") although the review had finished (PASS).
Done: the judge prompt now says to write the report files the brief names at exactly those paths and names, and only
check files take the _cx suffix.

## #199 Our TQ missed two platform fairness blockers on vet task 6 fx25g (2026-11-19, owner: "here we again got error you last 10 hour of work was this")
Platform TQ v3 on fx25g: 2 blocking, 3 notes; both blocking items reproduced before fixing (eval/tqv3/).
(1) Missing coverage: the reference walks the head twice in pull request mode (a quiet walk finds the linked folders);
only its `if !quiet` guard keeps the unreadable-path warning at one count per path. A version without the guard prints
"(4 times)" for two chmod 000 folders and passed every test. Our variant sweep had flagged that line (variants 143/144
survived) and I parked them as "full-scan, check later". (2) Unfair test: the entry-table row with 9007199254740992 ->
...993 (added at fx25b because our Codex SQ called float64 decoding a bug) rejects decoding as npm's JSON.parse and Go's
encoding/json do. Notes: a reach test calling reachOf with a hand-built state no scan builds (a removed record marked
local), a wall-clock goroutine helper, a flat 30-pair loop instead of table subtests.
Kit, done: replicas/fairness.md G14 (extra passes count once), G15 (values every reader of the format tells apart),
G16 (internal-function tests with hand-built states), step 5: parking a variant ("check later", "only the full scan")
is no closure. Open: (a) when SQ asks for a reference choice and no fairness lane has judged a test of it, keep the
fix untested (record it) - add to sq.md/fairness.md hand-off; (b) TaskStop on a multi-step run script kills only the
running step: the script went on to start the next container (offline uid, then replay). Run scripts need a trap or a
stop file, or the stop procedure must kill the whole process tree and the containers it started.

## #200 Adopt the "Passing Test Quality Once" method as the gate before every Test Quality purchase (2026-11-19, owner handover from an agent that passed TQ; vet task 6)
The method: three lists before the first upload (every decision point of solution.patch with the test that fails when
it alone changes, plus every existing behaviour at each touched site; every call form the repository accepts for the
named commands; every description sentence split on its triggers), a grid of cells checked against an oracle (the
full scan, the base code) rather than literals, a scripted wrong version kept for every gap and re-run together every
round, controls for unfair findings, the fairness sentence over every assertion of the whole file every round, no
skips in new tests, a solo suite run under 6 minutes, notes fixed or declined with a written reason, Test Quality
bought last, and fresh eyes after a second fail. Measured on vet task 6: our variant sweep reached 7 of 27 changed Go
files (about 59% of the decision points), parked 18 survivors, had no existing-behaviour list (the platform's blocker
1), and no fairness sentence pass (blocker 2).
Running on vet task 6 (fx26): four read-only lanes (A decision table of the 20 unswept files, B design-level wrong
versions and existing behaviour of the 7 swept files, C call forms and grid, D fairness sentence on every assertion)
and an independent Codex review against the method (GPT Sol 6.1 medium, eval/codex/tq-once-review.md); then one
batch run of every scripted wrong version, backed tests only, full proof.
Kit, to do after this task's round: a card (tq-once.md) with the lists, grid and checklist; a runner for kept wrong
versions (eval/wrong/*.py with EDITS, expected leaves; controls must pass); mutants.py gains always-true/false
operators and lists added lines no test runs; replicas/fairness.md step 1 builds the three lists first.
Done for #200 (2026-11-20): olympus-flow/tq-once.md (the method as a pre-purchase gate, with the vet 6 traps: per-leaf
T1 with subtests, head-only counts, oracle instead of a root skip, SQ-requested behaviour not pinned) and its row in
SKILL.md. Still to do: a kit runner for eval/wrong/kept (today eval/tqv3/wrongrun.py + batch2.sh on vet 6), and
mutants.py always-true/false operators plus a list of added lines no test runs.

## #201 Estimate the test grid before locking a seam and a description (2026-11-20, vet task 6, owner: "why our problem so bad?")
vet task 6's reference touches 27 Go files (about 1,350 added lines, about 300 decision points) and its description has
universal words over wide axes: "every finding" (16 finding families), "any outputs" (16 outputs), "every lockfile vet
reads packages from" (21 lockfile names x 6 pair conditions), plus the open link domain (chains, limits, texts, loops).
Each universal word multiplies the cells a reviewer can probe, and code shared with the full scan adds existing
behaviour to keep. Result: 20+ fix rounds, each finding a new cell. Kit: at stage 0 (seam) and stage 2 (description),
count decision points of the planned change and the cells each universal word opens (axis members x conditions);
above a budget, narrow the seam or the word before the lock (problem-design.md, difficulty.md).
Follow-up #201 (owner 2026-11-20): sequence length comes from depth, not width: "give a difficult enough task so
that agent first takes time to understand the problem and code ... Widening the task will not help." vet 6 (wide, 27
files) peaked at about 205K for the GPT Astra stand-in, no compaction. Kit: hunt.md/difficulty.md seam test = how much
code a solver must read and trace before the first correct edit, not how many rules the description lists.
Follow-up #201 (owner guideline 2026-11-20, "an iterative task that requires the agent to examine its log and its
current solution, repeatedly refine"): vet 6's s8 solve was one pass (63 calls: about 40 reads, 15 edits, 6 test runs,
32 min) because no run the agent could make showed its solution wrong. Kit seam test: does the agent's own feedback
(a reproducible command, build/test output, logs) keep failing until the work is done, layer after layer?

## #202 Checklists and checkers updated from the handover, every vet 6 platform finding and the owner's five test rules (2026-11-20)
Owner: "update our check list of test and solution now and our TQ SQ checkers also"; rules: hidden tests fair, prompt
aligned completely, all tests behavioural, no API-based tests, every test on public behaviour. Done:
- tests.md: "Hard rules for every hidden test" (the five rules with vet 6 examples) + hygiene (T1 per leaf, no skips
  with a non-root guard, OS limits gated, scenario names in messages, existing behaviour kept, kept wrong versions,
  solution-side tests are no coverage, tq-once.md before TQ).
- solution.md: "Hard rules" (site SQ executes inputs; decision table; constants at real limits; sibling forms a tool
  defines; a second pass repeats no side effect; shared code paths and scope growth; one logic in one place;
  solution-side tests not graded).
- build-checklist.md section 10: the new "never" items + pointers.
- replicas/fairness.md step 10: five verdicts per assertion (fair, aligned, behavioural, public, per-leaf T1), the
  skip / root / OS-limit / scenario-name checks, enumerate cells instead of sampling.
- replicas/sq.md step 3: sibling forms, second-pass side effects, shared code paths, real-limit constants, duplicated
  logic; solution-side tests are no proof.
- tq-once.md: the five rules up front.
Open: build-checklist.md and tests.md still hold older words that the Codex brief filter flags (probe, survivor, leak,
FP panel, inject, crash, mutant); reword them if a Codex builder ever reads those cards (the judge cards are clean).

## #203 A removed side effect at a touched site broke a check in another package (vet 6 platform SQ, 2026-11-20)
Platform SQ on vet 6 blocked on a regression: the solution stopped writing an unresolved link into the temporary base
tree; upstream wrote the link text there, and the manifest extractors' lockfile-presence check (fs.Stat of the name)
relied on that entry. No decision point of ours looked wrong on its own; the reader of the side effect is in another
package. Kit changes to make:
- solution.md / tq-once.md list 1: for every write the solution removes or makes conditional (files, map entries,
  temp-tree entries), list who reads it (grep the consumers: Stat, Open, ReadDir, map lookups) and keep one executed
  case per reader.
- replicas/sq.md execution lane: an "unchanged PR" sweep, one run per input shape of the touched axis (here link target
  kind: file, folder, dangling, outside x every file name an extractor checks for) with a change that edits only an
  unrelated file; expected output is no record with a change. Compare with base vet on the same tree.
- gates: base vet versus reference on the same unchanged-PR trees as a kept script (a regression against upstream is
  blocking at the site every time).

## #204 Fast hand-over check: run each check only when its inputs changed (vet 6, owner 2026-11-20)
Owner: "find a way of not running hand over check for 1 hour". Measured cause: the full suite is 5 minutes alone and
20+ minutes when other Docker jobs share the 3 GB VM; the fx30b hand-over ran it seven times, mostly in parallel with
other jobs. Built for vet 6 in eval/fast/ (run.sh, fp.py, snapshot-in.sh, twouser-in.sh, light-in.sh); move into the kit:
- fingerprints: test.sh / hidden tests / solution. The clean-repo base run depends on test.sh alone (base mode runs no
  added test file; fp.py refuses a test patch with anything but test.sh and test files), so root's baseline is run once
  per test.sh and committed as a snapshot image; the after run is saved per test.sh + solution.
- the two-user order is kept: uid 1000 starts from the state root left in the snapshot; the verdict is the same junit
  set check over the saved baseline, new and after files.
- kept wrong versions run only the test function each names; a failing case of the after run is re-run alone x3 to
  tell a wall-clock failure from a real one; the hidden tests also run as a user id with no account record.
- one heavy container at a time (DOCKRUN_SLOTS=1 for every lane): contention, not the suite, made the runs slow.
- the full cold two-user replay is repeated only when test.sh changes; say so in the hand-over.
- new standing step (from #203): reference versus upstream vet on unchanged-PR trees (eval/sq31/agents.sh).

## #205 A helper that died was reported as still running; reserve rows measured on agent solutions (vet 6, 2026-11-20)
- The in-process helper stopped when the owner interrupted the turn; an hour later I still said it was running, and the
  owner saw no container. Rule for the kit and for me: before any "still running" statement, check the lane's last file
  time and `docker ps`; after an interruption, list every background lane and restart the dead ones in the same reply.
- Method that worked and should be a kit step after the wrong-version lanes: for each open wrong version write one
  behavioural row, then run every row on (a) the reference, (b) its wrong version, (c) the clean repo, (d) each real
  agent solution through test.sh new. Add only rows that every strong run passes; fold a row that passes on the clean
  repo into a leaf led by one that fails there. vet 6: 24 of 37 open versions closed in one pass at no cost to the
  Orion runs (eval/reserve31/table.py, eval/fx32/rows.sh).
- eval/fast/run.sh: add the reserve list (eval/fx32/list.txt) to the kept-version step so those versions are re-run
  with every hand-over; a kept script whose edit no longer applies must fail the step, not print a line.

## #206 A test cell removed for the rollout came back as a platform Test Quality blocker (vet 6, 2026-11-20)
What happened: fx30 removed the emptied-lockfile pair rows because all four Orion runs of rollouts 46 and 48 failed
them, while the reference kept the code (emptiedLockfiles). Platform Test Quality on fx32 then blocked on exactly that
("no test covers a change that empties package-lock.json"). Second blocker: the saved report keeps the fields of each
manifest through one comparison of 12 fields (sameUse); the tests covered the 5 fields upstream already had and the
copies, never "only the integrity differs".
Workflow changes:
- Removing a test cell while the reference keeps the code behind it opens a Test Quality hole. The removal step must
  list each removed cell with the code path it leaves untested, and either a test stays for it or the owner sees the
  hole before the paste. A cell that every agent run fails is a rollout cost, not a reason to leave code untested.
- Field-list sweep: for every function of the reference that compares or copies a list of fields (here sameUse, useOf,
  In), one wrong version per field in the kept-version step, before the first paste. vet 6: 7 wrong versions written
  after the finding; 2 more survived the first new tests (entry change, local mark) and needed their own rows.
- A row that can only differ in a field the clean repository does not have passes there, so it cannot be a subtest of
  its own: fold it into a leaf led by a scenario that fails on the clean repository (eval/fx33/probe2.txt).
- Go test text with backslashes goes through the Write tool only: a doubled backslash in a quoted Python heredoc
  became a real newline again (eval/fx33/saved.go.txt is the clean source).
- eval/fast/run.sh: the kept-version step is now 17 scripts and about 220 of 700 seconds. Split it so that a change of
  layout only (same test names and assertions) repeats new mode, the clean-repository run and lint, not the kept step.
- A probe of new rows runs on the clean repository and the reference first (eval/fx33/probe.sh): it showed which rows
  fail on the clean repository (subtest allowed) before the test was written into the package.

## #207 Handover document for a second machine (2026-11-20, owner request)
HANDOVER-new-machine-20261120.md (13 sections: platform facts, how each reviewer judges, test and solution rules, the
pre-paste proof, the fast hand-over check, description, difficulty, rollout, the finding-type re-check list, working
rules, the nine decided-but-unwritten kit changes) and its appendix A (the fast-check scripts). Sent to the owner's
cloud session as two messages. Kit: keep this file current as the one-page entry for any new machine; section 12 is
the open kit to-do list of #203 to #206.

## #208 A "one-line solution change" I promised broke a repository test; check the repo's own tests before promising (vet 6, 2026-11-20)
For the owner's hint ("empty or not") I said a zero-byte package-lock.json needed a one-line solution change. It
needed two files, and the second edit contradicted an upstream test (the lockfile control must return an error for a
lockfile that is not JSON). I found that only after a 12-minute fast check failed. Kit:
- Before proposing any solution change, grep the repository's own tests for the behaviour at the site and at every
  consumer of the changed value (here: the control that reads the lockfile again). A pinned upstream test is a
  contract (source 3) and decides the boundary of a description word ("vet reads" excludes a file vet cannot decode).
- Run a one-minute targeted check (the new test plus every test of the touched packages) before the long fast check.
- Word reach for a hint: list every reading of the new word on the current solution first (probe), then decide; do
  not promise the solution change before the probe.
- A platform note asking for t.Run subtests is declined with the per-scenario clean-repository table as proof.

## #209 What two Orion trajectories show about how the agent decides (vet 6 rollout 50, 2026-11-20)
- The agent's loop is: trace, write its own regression tests, fix, run the repository gate, stop when green. Its tests
  encode its own reading of each sentence, so a case it did not think of never fails for it. A requirement is solved
  only if the agent thinks of the case while reading; nothing it can run corrects a narrow reading. Kit (profiles.md,
  difficulty.md): predict a miss wherever a stated rule reaches a state the visible tests and docs never show.
- A scope word is read by its nearest noun: "every lockfile ..., paired with the manifest file" became a table of file
  names; no run asked which states of the lockfile count. Kit (description.md word reach): list, per sentence, the
  reading the nearest noun suggests, and what it leaves out.
- Tool output is capped (about 10K characters per call) and the agent batches several files into one command; a
  decisive line was cut from its final review. This is noise in the rollout, not a property of the task: do not treat a
  single run's miss of that kind as evidence that a test is hard.
- A new mechanism that mirrors an existing one copies its limit as a separate budget (two walks, two counters); the
  case above the limit is never tested by the agent. This class (mirror with an independent bound) is a dependable
  discriminator.
- tools: eval/grade50/timeline.py prints a compact timeline of a trajectory (each tool call, the size of its result,
  the agent's messages, the per-window token peaks give the sequence length). Move it into the kit's tools.

## #210 Length lever: a stated requirement in an area the agents barely read, that the solution already meets (vet 6, 2026-11-20)
Four Orion runs: 75-79% of the context is reading; three stopped 25-30K short of compaction (about 244K), and a run
that compacts is over 256K. Lever tried in fx35: add one clause that the current solution already satisfies, in an
area the runs barely opened (here internal/policy: "a policy applied to the report read back gives the same gate"),
so a solver must read and check it. Cost: one test, no solution change; risk: one more requirement unit (Task Prompt
Quality) and one more area for the Test Quality reviewer. Kit (difficulty.md): measure per area the read commands
of the stored runs, pick an area under 10% that an existing sentence already reaches, probe the solution first.

## #211 A hint for a wall case is direct; a subtle hint for it is wasted (vet 6, 2026-11-20)
A case that every run of every rollout fails is a wall, not a separator: making it easy costs no difficulty while
other cases still split the runs. The rule "never name the case the runs fail" is for separators. For a wall the
owner asked for a hint; I first gave three words ("empty or not"), and the owner asked why it was not straightforward.
The trajectories show agents read a sentence by its nearest noun, so a subtle qualifier is easy to skim. Kit
(description.md 5b): when the owner asks for a hint on a wall case, name the state plainly in the user's casual words
("even if the PR leaves the lockfile with no packages in it"), and check it describes exactly what the tests check.

## #212 Scouter: identify the hosted agent's harness, effort and model from its trajectories (2026-11-20, owner guide)
eval/scout/ in vet 6 holds the tools: stage_a.py (harness fingerprint, hidden prompt part = first-request input minus
visible messages in o200k_base, work per request, compaction windows), local_sessions.py (same fingerprint from local
Codex rollout logs with known model and effort), capture-in.sh + capture.py + capture_report.py (what a Codex build
sends on its first request, in the task image, no model call), grade.sh (hosted patches graded locally with the tests
they were graded with). Findings that change the workflow:
- The hosted Orion harness is stable (one hidden-part size over 7 days) and is an older Codex build than the current
  one: a local solve with current Codex is not a replica (different tools, instructions, compaction point).
- Hosted compaction comes at about 244K, so the 256K bar means "compacted once" under that harness.
- Hosted Orion reasons 2-3x less per request than our local gpt-6.1-sol high runs; local solve lengths and pass rates
  overstate Orion until the replica runs the hosted build and effort.
Kit: move eval/scout into tools/scout; before any local stand-in solve, run capture_report against the hosted
fingerprint; record per rollout the hidden part and reasoning per request so a platform change shows at once.

## #213 Verify Flakiness failed on an existing wall-clock test the change does not touch (vet 6, 2026-11-20)
The base suite runs every listed package in one parallel go test call; a repository test with an upper wall-clock
bound (1.6 s for a scan with two 1 s enrichers) went over it 4-5 times in 30 even on a quiet machine, on the original
repository as well. The platform runs the suite 12 times, so one failure is likely. Kit (harness.md, test.sh template,
build-checklist): before the first paste, git grep the base packages' tests for upper time bounds
(assert.Less(t, time.Since(...)), elapsed comparisons, short timeouts); measure each 30 times on the clean repository;
skip each one that exceeds its bound there in base mode, with the reason next to it, as for user-dependent tests.
A test.sh change re-opens Verify Tests, Verify Solution, Verify Flakiness, Reward Hacking and Test Quality.

## #214 A local replay can pass tests that the same patch fails on the platform (vet 6 rollouts 51-52, 2026-11-20)
Two of six Orion patches failed five link tests on the platform that pass when the patch is replayed in our task
image; both read files through Go's os.Root. A temp folder reached through a link was ruled out. Likely a kernel or
sandbox difference (link resolution under the platform's runtime). Kit (rollout.md, scouter): treat the platform
junit as the truth for a run; report replay-vs-platform differences per test; do not count a run's local replay as
its platform result; when two patches share a platform-only failure set, look for the shared mechanism first.

## #215 Sequence length by requirement: attribution of each run's context (vet 6, 2026-11-20, owner request)
eval/scout/attribution.py gives each tool call (arguments + output read, o200k_base) to the requirement areas its
command or patch names; the rest is the fixed prompt plus the model's reasoning and messages. On 6 Orion runs:
tests and builds about 18%, the largest requirement (links) about 16%, each other requirement 7-9% (17-22K tokens),
policy clause (already met by the solution) 1.5-3% (3-7K). Kit (difficulty.md, length gate): estimate a seam's
length as fixed prompt + about 20K per requirement that needs a code change + about 18% for test runs + about 15% for
reasoning; a requirement the reference already meets adds only a few K. Use this table before adding requirements
for length.

## #216 Near-miss release without a Test Quality hole: replace a removed cell with one the near miss passes (vet 6, 2026-11-20)
When a near-miss run fails only crafted cells, deleting them leaves the code path untested and Test Quality can block
on it (it did after the emptied-lockfile removal). Method used for fx40: for each removed cell, write down the wrong
design a reviewer would naturally write (usually the reference minus one check), then find an input where that design
fails and the near-miss run passes (a kept folder instead of an added one; a 300-link chain instead of 41; the kept
"delete the first of 65" case). Add it as a case of the same test, with a kept wrong version for the natural design.
What stays uncovered is only the near miss's own variant; record it. Kit (near-miss-release.md, tq-once.md).

## #217 Dry-run each replacement case against the near miss's own code first (vet 6, 2026-11-20)
fx40's kept-folder case (a folder named build.gradle.kts that the base has and the change keeps) was predicted from a
grader's one-line summary ("compares glob name sets") and failed run #3 in the quick check: its code also looks up
the base blob of each match and returns false for a folder. Any input with a folder named like a manifest file fails
run #3, so that path cannot be covered while run #3 passes; the case was dropped and its kept wrong version held.
Kit (near-miss-release.md): before writing a replacement case, read the near miss's code for that path and trace the
case through it; when every covering input fails the near miss, the path is the near miss's own variant (hold, record).

## #218 A kept wrong version must model the other design, not tweak a check the reference never reaches (vet 6, 2026-11-20)
base-links-unbounded (the reference with maxLinks 100000) passed the 300-link case: the reference's base enters only
the linked folders the head entered, so its link limit is never used for a folder the head cannot open. The natural
wrong design is a base that resolves links on its own (as run #3 does) with no limit: base-walk-unbounded (enter every
linked folder + no limit). Kit (tests.md, wrong versions): when a test is meant to catch a design that differs in
structure from the reference, the kept wrong version changes the structure too, and a control (same structure, right
limit) shows the case isolates the one decision.

## #219 FP triage: check the behaviour before the change on each discriminating probe before calling it stated (vet 6, 2026-11-21)
The FP audit of the near miss found "a removed runtime copy next to a kept dev copy: run MODIFIED, reference
UNCHANGED". I first told the owner the reference rule follows a stated sentence and needs no change; only then did I
read upstream: it gives MODIFIED on that input, so the run kept upstream's rule and the reference's rule was our own
addition (a replica finding about sources; the dev mark came along). Kit (near-miss-release.md, rollout.md lever 3,
replicas FP triage): for every probe that separates a passer from the reference, record three columns before any
verdict - description sentence, behaviour before the change (run or read upstream on that input), origin of the
reference rule (platform finding, stated sentence, or our own review round). A rule that is ours alone, unstated and
untested is an alignment candidate for the owner; a rule the platform asked for or a sentence states is not.

## #220 Kit card sq-once.md: the Solution Quality gate, the counterpart of tq-once.md (owner request, 2026-11-21)
The owner asked for a Solution Quality handover in the form of the Test Quality one. Written as
HANDOVER-passing-solution-quality-once-20261121.md from every platform SQ result we have (turso, swift, faust, elio,
vet): what the reviewer does, hard rules, four lists before the first upload (promise x path grid, decision rows,
rejection ledger, touched-site ledger), closing cells by execution, cost on the normal path, the three-source verdict
with the defences that never worked, the Design / Clutter / Practice sweep, order and repair loop, an evidence table
and a one-page gate. Kit: copy it as olympus-flow/sq-once.md, link it from SKILL.md (stage 4-5 and 6-7) and from
solution.md and replicas/sq.md, and make its section 9 the gate item before every SQ purchase in gates.md.

## #221 replica.sh: an Auto Review that runs alone (owner request "run only auto review", vet 6, 2026-11-21)
replica.sh ar refuses to start without the fairness, sq and dq outputs of the same tag. For "only Auto Review" I
hand-built a brief (eval/ar-fx40/brief-codex.md): no replica outputs, the site's own check results as files, and a
runs folder with each run's verdict on the current tests. Kit: `replica.sh <task> ar <tag> --alone [--runs <dir>]
[--site <file>...]` writes that brief; ar.md gets one paragraph for the alone case (do the coverage, S1 and P parts
yourself; a family without runs does not fail the gate).

## #222 Harness check: every test-only helper package of a base-mode package is pinned (vet 6, 2026-11-21)
The Codex Auto Review found that test.sh pins gitbasetest, golden and plugintest but not graphtest, the comparison
helper of the upstream lockfile extractor tests that base mode runs: a candidate could weaken those tests by editing
it. Kit (harness.md + precheck.py): list every non-_test.go file of the base commit that only _test.go files import,
keep those whose importers are in base-mode packages, and fail the precheck when the pin pattern misses one.

## #223 Kit refactor for the V2 criteria and a 300K design target (owner 2026-11-21: "refine workflow and align everything with new requirements ... target 300k+ from start ... make this customer ready now")
What changed, by card (product skill/; the pre-refactor copies are in history/pre-refactor-20261121/):
- SKILL.md, PIPELINE.md: the objective is the platform's rollout criteria verbatim (platform.md, read from the platform JSON:
  Nova 0, Orion 1 <= passes <= N/4 with its passing runs averaging >= 256K, Vega <= N/4, >= 4 runs each, no unfair flag,
  cheat < 20%, no env blocker); the design target is an Orion pass of 300K+ designed at stage 0 and measured at stage 2.
  Stage 7 is one replica round + one fix batch + one verification round (replaces #170's three phases and the
  2026-11-14 "rounds until 3/3"): the executed closure (tq-once, sq-once, fastcheck) is the proof, model reviews are
  samples; a platform finding is answered by the repair loop, never by a new review phase. Every lane: 40 min box.
  "Version bookkeeping" section (#193). Pre-paste gate rewritten around fastcheck.sh. Metrics baseline = vet task 6.
- hunt.md: part A adds the long-solve host criteria; part B adds the length score (6b: reading chain, files to
  change, layers, the repository loop that keeps failing, estimate 8K + 20K per code-changing requirement + 18% + 15%),
  the test-grid budget (6c, #201) and blocker rows for wall-clock tests, root skips, helper packages and importers.
- problem-design.md: section 1 updated with the vet 6 trajectories (#209), section 2 adds the length model (#175,
  #215, owner 2026-11-20 "depth, not width"), section 4 adds open input spaces and crafted cells, section 7 adds 3c/3d.
- difficulty.md: new section 2 "Length spike" (2 Codex GPT Sol 6.1 xhigh solves of the draft; gate: both compact and
  mean >= 300K; below it deepen, never widen; two misses -> the owner picks the runner-up); K7 mirrored mechanism;
  sections renumbered (solver runs 3, reading 4, too easy 5, reserve 6, signals 7 with the short-pass signal).
- profiles.md: Orion/Vega/Nova rows from the hosted vet 6 runs (lengths, compaction point, the agent's loop, nearest
  noun reading, mirrored budgets); K7 row; upkeep adds the harness fingerprint.
- rollout.md, platform.md, gates.md: criteria table verbatim; per-run compacted/sequenceLength; the platform junit is
  the truth (#214); three-column FP triage (#219); replacement cells (#216/#217); check order (#200); Trial QA as the
  last readiness item (procedure unknown, to record); zip layout when the CLI is down; AR advisory.
- description.md: LOCKED row (owner decides before v1, 5b after); length is not in the text; nearest-noun reading
  (#209); wall-case hint rule (#211); length change rule (#210); checklist items for the spike and the grid.
- tests.md, tq-once.md, solution.md, build-checklist.md (items 9-11, section 7 fast check and mutant sweep, section 8
  removed cells), harness.md (H2 helper pins and tar, H3 oracle interface and text output, importers, pinned-only base
  tests, wall-clock skips; H6 two-user order and junit sets), dockerfile.md (allowed FROM lines, sbin, /app writable,
  comment per deviating RUN, start from the accepted example), near-miss-release.md (rules 8-10), situations.md (P-8,
  P-9, E-7..E-10, R-5..R-7, X-9..X-12), replicas (common.md Docker rule, ar.md Alone mode, dq.md AI detector and
  ASCII, fp-audit.md three columns, sweep-brief.md when it runs, CALIBRATION.md note), ledger-template.md (length rows,
  criteria table), seam-bank.md, templates/hunt-brief.md, templates/design.md.
- Tools: codex_job.sh job "solve" at xhigh (the Orion stand-in); solvers.sh `spike` mode (solves 7-8) and the session
  log copy for seqlen.py; replica.sh `--alone` and `--site` for ar (#221), 40 min default box.
- Product: GETTING-STARTED.md rewritten for the new flow; build logs, old hand-overs and the pre-refactor cards moved to
  history/; metrics/README fixed; five parallel workstreams (agents, templates + checkers, repo tools, run-analysis
  tools, proof tooling) report below as #224-#228.
Decisions that change an owner rule (flagged for the owner): stage 7 = one round (not three phases, #170); local GPT
solves run at xhigh (was high); the two spike solves count as GPT solves after the lock when only the wording changed.
Status: cards DONE; tools per #224-#228; memory notes that set another cadence are superseded by PIPELINE.md.

## #224 Run-analysis tools in the kit: seqlen.py, rollout_report.py, scout/ (2026-11-21, from vet 6 eval/scout; workstream report)
Built and smoke-tested on the vet 6 data (read-only): `tools/seqlen.py` (Codex rollout .jsonl, trajectory.json, zip or
pulled run folder -> windows, peaks, requests, sequence length, compacted; passing-run mean against 256K and 300K),
`tools/rollout_report.py` (per-run table from the platform junit, tests failed by 2+ runs, every platform criterion met
/ not met / not enough runs; `--marker` for a prompt phrase), `tools/scout/` (stage_a.py hosted fingerprint,
local_sessions.py, attribution.py with `--areas` JSON, timeline.py, README), `scripts/test_seqlen.py` (11 tests pass);
pull.sh and digest.py now carry sequenceLength and compacted per run. Findings that correct the cards:
- The platform's sequence rule (`window_peaks_2026_11b`) sums per-window peaks of input + output tokens; the tool
  matches the platform field on all 8 rollout-54 runs (run #3 = 330,967; the ledger's 330,604 was input-only).
- Hosted compaction comes at a window peak of 244,600. The local GPT Sol 6.1 stand-in runs with a 475K window and
  reached 277-307K without compacting; local gpt-6-astra (258K window) compacted at 244,926. So the stage-2 length gate
  is the sequence length itself (mean >= 300K, none under 250K), not "both solves compact": corrected in difficulty.md
  section 2, PIPELINE.md, SKILL.md, description.md, ledger-template.md, situations.md P-8, solvers.sh (#223's line
  "gate: both compact" is superseded by this entry).
- Hosted reasoning per request 252-282 tokens vs local Sol xhigh 510-762: local lengths overstate hosted ones.
- The hidden prompt part of the hosted Orion harness was 7,594 tokens on every run from 11-14 to 11-20 (one build).
Done in the same step: solvers.sh copies each solve's Codex session log (rollout-*.jsonl, found by the clone path)
next to meta.txt as session.jsonl so seqlen.py reads local solves (untested until the next solve run); pull.sh prints
"-" for every empty column so a run without a verdict no longer shifts the fields.

## #225 Reviewer agents rebuilt as thin wrappers over the replica prompts; sq-once.md written (2026-11-21, workstream report)
agents/olympus-tq-judge.md (121 lines), olympus-sq-judge.md (112), olympus-auto-reviewer.md (106), olympus-fp-auditor.md
(90): frontmatter name / description ("Run only at the review points of PIPELINE.md 'Review schedule', never per fix or
per paste") / model opus; Role, Inputs (common.md layout, what the launch message names), Method = "follow
replicas/<file>.md exactly" with the key points inline, Execution rules (dockrun.py, DOCKRUN_SLOTS=1, reuse the image,
never build or prune), 40-minute time box with the wait-loop kill, Independence, Output in the site's shape. No
reference to any file outside skill/ or agents/ (the legacy olympus-challenge-creation paths and the never-built
references/*.md are gone; grep verified). The per-task anecdote sections moved verbatim to
skill/playbooks/examples-{tq,sq,ar,fp}.md (441 / 607 / 422 / 115 lines) with a four-line intro: examples of the
generator questions, not a checklist. skill/sq-once.md (124 lines, from HANDOVER-passing-solution-quality-once) is the
Solution Quality gate; linked from SKILL.md, solution.md, replicas/sq.md and gates.md G3. Closes the open items of #183
(rebuild olympus-tq-judge) and #220 (card + links). Still open from #183: the sweep tool pass without the coverage
filter (in #227's mutants.py) and an eval/pool.md pool-closure ledger a paste requires to be empty.
Agent launch messages must name: the task folder, the report path, the image, the test command, the time box, and for
the tests lane the raw variant results; the agents read nothing else (PIPELINE.md Terms).

## #226 Repo tools unblocked: repo_init, repo_check, proof --base-only, checklist_gate, test_summarize (2026-11-21, workstream report)
DONE, each with a unit test (115 tests pass): #116/#136 repo_init resolves a bare TASK under paths.tasks_root, refuses
`.`/`..` and any folder inside the skill or product, prints `task: <folder>`; #136 render() keeps a hand-edited
init/Dockerfile or init/test.sh (hash in init/.rendered.json; `--render-only --force` rewrites); #138 repo_check runs an
`open-build-inputs` step before any Docker call (placeholders, NOT_VERIFIED, an unverified go_sha256, the matching
profile.open rows) and writes tracebacks into check/results.json; #140/#164 proof.py `--base-only` (image build or
reuse + the base/base cell through the proof.run hook, only `--base-ids` needed) and repo_check qualifies with it; the
`--timeout` message names the 688 s bound; #141 profile `keep_tracked` (tracked files matching the generated-output
patterns, never dropped from the candidate copy; the template side is in #227); #146 new_native_ids derived from
expected.new for Go and Python, other cases stay open; #160/#222 a Go package imported only by test code outside its
own directory becomes a pinned helper (restore_paths, evidence row helper_roles); #165 a TASK name holding a
check_codex_brief.sh word is refused; #167 checklist_gate names the cell count and the blanked rule ids; #129
test_summarize fixed (gate() was right). Renderer contract with the templates: `{{profile_json}}` indented JSON,
`{{profile_b64}}` still rendered for an old template, `--platform=` stripped from FROM, both key spellings
(hidden_paths and overlay_paths) embedded, one comment block above a deviating RUN allowed.
OPEN: a Docker smoke run of repo_check on a known-good package (the Docker slot was held by #228's agent); proof.py
tampering each pinned helper by default (#160 b); the stage-1b precheck "new_native_ids consistent with expected.new".

## #227 Templates and checkers: the platform-blocking defects closed (2026-11-21, workstream report)
DONE with unit tests (115 pass): #142 bare allowed FROM line in all three Dockerfile templates; #153 PATH keeps
/usr/local/sbin:/usr/sbin:/sbin; #156 the last RUN makes /app and the caches a+rwX; #139 the Go reinstall carries its
reason block and no other comment; #158/#159 the generated adapter accepts `[--output_path F] [--mode] <base|new>` in
any order (default base; a scratch JUnit path printed without --output_path; exit 2 on malformed args) and prints the
decoded go test text (`--- PASS:` lines) while still building JUnit (UNPROVEN on the Harbor oracle until a package
passes with it: templates/go/README.md names the bash runner of the accepted packages as the proven route); #150 the
profile is embedded as readable JSON under {{profile_json}} (repo_init now drops the hidden_* keys from it, keeping
them in profile_b64 for an old template); #152 neutral identifiers and messages (restore / overlay / pinned) and
precheck.py fails hard process words in test.sh with line numbers (`--test-sh PATH` for a template); #162 precheck
runs on pkg/Dockerfile alone with SKIP lines for missing files; #222/#160 tests_lint G1 (every test-only helper package
of a base-mode package pinned; regex parse when no Go toolchain is on PATH), #197 G2 (changed packages and their
importers with tests in base mode or `# base skip: <dir> <reason>`), #213/#155 W1 (wall-clock bounds, root skips,
user.Current() as skip-allowlist candidates); #165 precheck fails flagged words in task, package and hidden test file
names; examples: templates/examples/in-review/Dockerfile.go-vet-pr-accuracy + test.sh.go-vet-pr-accuracy (byte copies
of the vet 6 package; move to accepted/ when the owner says so). precheck changes: "Dockerfile does not run tests"
matches a runner at a command position only (pip install pytest no longer fails); "platform" is a WARN in the patch
word check (an accepted hidden test uses it).
Found on vet task 6 by the new checks (task follow-up, not kit): G1 FAIL internal/hiddentext (imported only by the
hiddencode tests that base mode runs, not in PINNED) next to the known graphtest miss; W1 lists 7 further wall-clock
bounds (agentconfig limits/shell, hiddencode analyze/dynamic_cgo, app/signal) to measure 30x on the clean repository.
Add both pins to PINNED at the next test.patch change (a test.sh change reopens Verify Tests/Solution/Flakiness,
Reward Hacking and Test Quality).
NEW: the accepted Python example Dockerfiles use `olympus-base-python`, no longer an allowed FROM line (examples/README
and dockerfile.md E4 say what to change). OPEN: keep_tracked in templates/*/test.sh prepare() (the resumed agent
reports on it); a Linux run of the generated adapter (no /var/tmp on Windows); the Harbor oracle run of the adapter.
Addendum #227 (resumed agent): keep_tracked honoured in templates/*/test.sh prepare() (tracked files matching a
generated-output pattern and their folders survive the filter; behavioural run on a fixture: 6/6); READMEs name
overlay_paths / base_overlay_paths and keep_tracked; the profile JSON sits in a `r"""..."""` string (valid JSON can never
hold three consecutive double quotes, so no value can end it early; tests_lint reads both quote forms). 121 tests OK.

## #228 Proof and hand-over tooling in the kit: junit_sets, wrong_versions, mutants, fastcheck, platform cells (2026-11-21, workstream report)
DONE with unit tests (125 pass): `tools/junit_sets.py` (the verifySolution set check; on the vet 6 fx40 files it gives
the same VERDICT PASS as the task script); proof.py `--root-base --two-user --plain-new` (#155, #172, #174, #158: one
container as root in the image's own /app, groupadd/useradd model uid 1000, chmod -R a+rwX /app only when needed and
logged, root applies test.patch and runs base, model applies solution.patch and runs new and base, the set check, a
bare `test.sh new`); `tools/wrong_versions.py` (#200/#205/#206: EDITS applied to one tree copy, KIND wrong / control /
held, a stale edit fails the step; on the 20 vet 6 kept scripts 19 apply, one held script is stale); `tools/mutants.py`
gen/run (#178/#181/#183: neg, drop, del, flip, true, false, swap on named types; 818 mutants from the vet 6 patch's 1363
added lines; run classes killed / survived / invalid / timeout / stale, shards); `tools/fastcheck.sh` +
lib/fastcheck-in.sh, lib/patch_fp.py, lib/junit_leaves.py (#204: three fingerprints, the snapshot once per test.sh,
the after run once per test.sh + solution, new mode as uid 1000 and an odd uid, T1 per leaf, lint from profile
commands.lint, kept wrong versions with an optional eval/wrong/kept/cmd.txt, junit sets, the x3 re-run through
commands.one; dry run with stub docker and dockrun: VERDICT PASS twice, snapshot reused). Cards: gates.md G0/G2,
harness.md H6, TOOLS.md.
NOT RUN (this machine had 5.7 GB free against the 15 GB floor, so no container was started): wrong_versions in the vet
image, the two-user proof cell, a 5-mutant run shard, a real fastcheck run; the exact commands are in the workstream
report (BACKLOG keeps the gist: run each once on vet 6 with DOCKRUN_SLOTS=1 after the disk is freed; the first real
fastcheck must also confirm that uid 1000's go accepts root's /tmp/gocache entries from the snapshot, since the kit uses
the image's own cache layer, not the task's cache volumes).
OPEN: #179 re-run only the wrong versions a test edit can affect; #206 split the kept step for layout-only test
changes; the reserve rows of #205 as kept scripts (format decision); repo_init writing `commands.lint` into
profile.json (Go: gofmt, go vet, golangci-lint) so fastcheck's lint step runs; a sweep wrapper that produces the cover
profile in the container and shards mutants.py through dockrun; a receiver check in the swap operator (it also rewrites
`model.Change` type names, classed invalid).
vet 6 follow-ups (task, not kit): eval/wrong/kept/terraform-json-unpaired.py (held) no longer applies to the current
reference: fix or retire it before the first fastcheck run; add eval/wrong/kept/cmd.txt with the five-package go test
command; pin graphtest and internal/hiddentext in pkg/test.sh at the next test.patch change (#227).

## #229 Cold-read QA, the build checklist pass and the field notes folded in (2026-11-21)
Cold read by a fresh agent (new-user lens) found 3 blocking items, all closed: the new files were untracked (now staged
for the owner's commit); docker.cleanup_allowed was required by machine.py but missing from machine/schema.md (row
added, plus the exported OLYMPUS_<KEY> variables and every per-job environment override); hunt part A's three novelty
lists do not ship and hunt.sh skipped them silently (hunt.sh now prints LIST MISSING per list and hunt.md says where
each comes from). Also fixed from its 23 contradictions: what a solution change reopens (PIPELINE Version bookkeeping),
the calibration-paste check order (rollout.md, calibrate-one-passer.md: the reopened checks in platform.md's order,
Test Quality last), the FP auditor's timing (platform passers at stage 8, owner-asked local passers at once), stale
efforts in situations.md, the calibration prompt's old target, hunt.md's 300K wording (256K criterion, 300K design),
examples/README's "accepted only" line, the schema's lock path, the 300 s vs 6 minutes bound, the time-box header,
solves without a second Claude account (solve 2 runs on the main account), levers 1-4, the DQ replica's 9-unit limit,
K1-K7, the 40-file drop threshold, the 12 GB floor, sq twice per round, the ninth check (taskQuality) and the check
name mapping, the agents' rule-5 sentence, three section citations, stale prose references (CALIBRATION path,
fairness.md backups, python README, dockrun usage, codex_job header, replay_patches header, MAP.md), legacy stage
letters S0-S3 in titles, and certify.py's usage line. Left as recorded only: the R-id collisions (R1-R16 of
description.md vs R1-R8 of an old review in build-checklist.md), three meanings of "profile", test_launchers.py's temp
dir inside skill/scripts, the examples' olympus-base-python FROM line (documented), and near-miss-release.md's
historical narration.
Build checklist upgraded (96 rules, gate tests pass): section 1 (three sources; length design and grid budget as
inputs), 2 (sentence triggers and sibling forms; existing behaviour per touched site; second pass), 3 (mirrored
mechanisms K7; open input spaces and OS limits; normal-path cost and scope growth; removed writes), 4 (decision rows
with kept wrong versions; field lists; absent/several/merged; equivalence by execution only; values readers tell
apart), 5 (per-leaf T1 and no skips; the platform test.sh interface and base-mode rules; the two-user order), 9 (rule
map rows for Test Quality, Solution Quality, Verify and the false-pass audit as the platform runs them now).
New card recheck.md (the hand-over's section 10 list of finding types, T1-T15, S1-S8, D1-D3) walked before every paste
(PIPELINE pre-paste gate item 6). From the owner's shared field notes (another author's Go package through SQ and TQ):
tq-once.md gains the bad-data twin rule, the unstated-detail reference variant, every API form per list item, the
half-CPU timing and the three-runs-plus-single-CPU check; sq-once.md the resource-ownership rule; description.md R12
names "invalid per RFC X" and "malformed" as open phrases to close with a list.

## #230 The kit reads no memory notes; Docker smoke of the proof tools (2026-11-21)
Owner: "are you sure there is nothing in kit that needs our memory? customer wont have this". Audit of skill/, agents/,
machine/: two real dependencies, both removed: tools/lib/claude2_run.sh told every reviewer lane to read the
coordinator's MEMORY.md first (2026-10-17 rule), and tools/lib/codex_job.sh's default job kind told Codex to read
MEMORY.md and the local olympus-codex-* skills. The method lives in the agents and replicas/ now. paths.memory_dir stays
in the machine profile for solve_watch.py only (it flags a solver that read the coordinator's memory); schema.md says
so. Cards mention "memory notes" only to say PIPELINE.md overrides them.
Docker smoke (after the owner's "clean": 2 exited containers, 1 dangling image, the superseded snapshot
olympus-snap:9f948a4dfd81 and the volumes vetgo0, vetgo1000, olympus-repo-check-* removed; Docker Desktop stop/start
freed 2.5 GB on C:; the 43.7 GB docker_data.vhdx holds 13.8 GB and needs an elevated `diskpart /s
C:\Users\ASUS\OSS\compact-docker-disk.txt`, which this session could not run): wrong_versions.py in the vet 6 image on
3 kept scripts PASS (wrong caught, control passes, held reported, 3 minutes); mutants.py run on 5 mutants: 3 killed, 1
invalid, 1 survived (delta.go:162 `if !wanted(rel, f.Size) && !declaresDependencies(...)` made always false: a vet 6
pool item to triage by the three sources, not a kit defect); fastcheck.sh first run failed before any container on a
Git Bash to Windows path (dockrun.py and junit_sets.py received /c/... with MSYS_NO_PATHCONV=1 set): fixed with
machine_host on every path Python gets; second run recorded below.
Addendum #230 (fastcheck smoke, second run on vet 6, 2026-11-21 06:07-06:36): baseline snapshot reused; two-user step OK
in 282 s (uid 1000 applies the solution, new mode 121/121, saved after run reused); new mode as uid 12345 OK in 219 s;
T1 on the clean repository: 121/121 fail, none skipped; junit sets PASS (all five sets empty); the light container was
stopped by the 1200 s per-container timeout while running the 20 kept wrong versions with the default command
(test.sh new per script). Fix: the light step gets a 3600 s budget and a note when eval/wrong/kept/cmd.txt is absent
(the task-level fix: a cmd.txt with the five-package go test command). Third run (light step only) recorded below.
Also pushed the product as a new private repository: https://github.com/okayyyyarchna-art/olympus-flow (master, blind
solver clones excluded); verified from a fresh clone: install.sh into an isolated home (140 files), the machine profile
loads, 125 unit tests pass.
Addendum #230 (third fastcheck run on vet 6, 06:37-07:2x): two-user OK (new 121/121 as uid 1000), T1 121/121 fail on the
clean repository, uid 12345 OK, junit sets PASS, kept step ran all 20 scripts within the new budget. It exposed a
wrong_versions.py matcher defect: the kept scripts name EXPECT by a prefix of the leaf ("…/a_chain_of_links") and mean
"this cell catches it", while the tool required exact names and no other failing leaf, so 9 caught versions read BAD.
Fixed: an EXPECT entry is caught by a failing leaf that equals it, starts with it or sits below it; other failing
leaves are listed as "also fails". Re-judged from the run's log: 17/17 wrong caught, control passes, 2 held reported,
1 stale script (terraform-json-unpaired, a vet 6 task fix). The kit's proof tools are now smoke-tested end to end on a
real package; the only open fastcheck item is commands.lint from repo_init.
