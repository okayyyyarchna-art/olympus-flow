Verdict: needs the listed edits first; the prose reflects most decisions, but conflicting instructions and executable gate failures block a reliable dry walk.

Independent Codex review of `skill-next/` and `machine/*.json`. Findings below use source locations or isolated host probes; Docker and model calls were mocked, and no real container, platform check, or paid job was started. Probe code: `eval/review4_probe_cx.py:1` and `eval/review4_edges_cx.py:1`.

## Owner decisions

| Decision | Assessment | Evidence |
|---|---|---|
| 1. Machine limits, cleanup permission and paths come from the profile | **Partly** | Profiles contain distinct slots/memory values and cleanup permission (`machine/windows-asus.json:18`, `machine/mac.example.json:16`); loader and shell exports consume profile data (`skill-next/tools/machine.py:33`, `skill-next/tools/machine.py:78`). However, cleanup permission is ignored by unconditional pruning (`skill-next/tools/proof.py:141`); slot overrides bypass the profile maximum (`skill-next/tools/lib/dockrun.py:25`); machine-limit comments still claim two containers/default two rounds (`skill-next/tools/lib/replay_patches.sh:44`, `skill-next/tools/round.sh:18`). See F6. |
| 2. No local blind solves; first draft goes to owner checks/2-2-2 rollout while closure continues; every patch enters the corpus | **Partly** | Correct narrative and corpus instruction appear at `skill-next/PIPELINE.md:26` and `skill-next/rollout.md:3`. Local solves remain an explicit instruction at `skill-next/description.md:82`. The stage table dispatches platform quality checks/rollout only after confirmation and freeze (`skill-next/PIPELINE.md:18`, `skill-next/PIPELINE.md:20`). See F1–F2. |
| 3. `description.md` is the sole description rulebook; every description under 250 site words | **Partly** | Sole-authority statement: `skill-next/SKILL.md:50`; strict limit: `skill-next/description.md:29` and `skill-next/description.md:86`. Precheck nevertheless passes 250, 251 and 400 words (`eval/review4_probe_results_cx.txt:28`–`:30`). Stuck guidance supplies conflicting calibration rules (`skill-next/stuck-prompts.md:15`, `skill-next/stuck-prompts.md:45`). See F3 and F9. |
| 4. Product tools listed in `TOOLS.md`, using the machine profile | **Partly** | Tool states and future work are listed at `skill-next/TOOLS.md:3`; shell loader is used by launchers (`skill-next/tools/replica.sh:12`). The advertised review tools lack their prompt resources; proof and summary tools do not implement the required gates faithfully. Several shipped tools are absent from the inventory, including the active local-solve launcher (`skill-next/tools/solvers.sh:5`, `skill-next/TOOLS.md:3`). See F4, F6–F8. |
| 5. Stage time boxes; overrun reports progress and never skips a gate | **Reflected for local stages; partly overall** | Stages 0–8 have boxes and an explicit overrun/report/no-omission rule (`skill-next/PIPELINE.md:56`–`:60`). Stage 9 has no stated builder-work box (`skill-next/PIPELINE.md:20`). The listed local allocations total 315 minutes if fully used, versus the stated 2–4 hour target; clarify target versus allocations (`skill-next/PIPELINE.md:56`–`:59`). |
| 6. Stuck-prompts and tracked-jobs rule linked from `SKILL.md` | **Partly** | Stuck-prompts has a working relative link (`skill-next/SKILL.md:34`). Tracked jobs is a sentence, without a rule link (`skill-next/SKILL.md:50`); the fuller rule is in `skill-next/PIPELINE.md:52`. Shipped launchers violate that rule. See F5. |

The requested quality priority is **reflected in the rule text**: Auto Review → false pass → Solution Quality → Task Quality (`skill-next/SKILL.md:12`, `skill-next/gates.md:20`, `skill-next/gates.md:46`, `skill-next/gates.md:66`, `skill-next/gates.md:74`). Its executable enforcement is incomplete, as F7–F8 demonstrate.

## Required edits

### F1 — High: the authoritative description procedure still launches forbidden local solves

`PIPELINE.md` explicitly forbids local blind solves (`skill-next/PIPELINE.md:26`), but the description lock procedure orders a background batch of two Opus and two GPT solves (`skill-next/description.md:82`). Its after-lock procedure still evaluates that batch (`skill-next/description.md:94`). Stuck guidance repeats “one solve batch per description lock” (`skill-next/stuck-prompts.md:40`), and `solvers.sh` implements the launch (`skill-next/tools/solvers.sh:104`–`:110`). A builder following the rulebook therefore violates decision 2.

**Edit:** replace those active instructions with platform rollout handling. Remove or explicitly disable/deprecate the local-solve launcher in this product, and label historical local rates as historical evidence only.

### F2 — Medium: the stage sequence delays owner validation until after local closure

The owner’s concurrent loop is stated in the narrative (`skill-next/PIPELINE.md:26`–`:31`), but the table places deterministic closure, all confirmation sweeps/replicas, and final freeze before the platform-validation stage (`skill-next/PIPELINE.md:17`–`:20`). There is no explicit owner-dispatch transition when the locked description, tests and reference first exist at stage 5 (`skill-next/PIPELINE.md:16`). A table-following builder can finish all local checkpoints before giving the owner the first complete draft.

**Edit:** add the first complete-draft handoff immediately after reference construction, followed by concurrent owner validation and builder closure. Keep final freeze distinct from this early dispatch.

### F3 — High: the precheck accepts descriptions the rulebook prohibits

The rule is strictly **under 250**, so 250 must fail (`skill-next/description.md:29`). The executable instead fails only above 1000 and warns only above 400 (`skill-next/tools/precheck.py:55`). An in-memory package probe returned exit 0 and a word-count PASS for 250, 251 and 400 words (`eval/review4_probe_results_cx.txt:28`–`:30`). This matters because the lock procedure requires a clean precheck (`skill-next/description.md:73`, `skill-next/description.md:81`).

**Edit:** enforce `words >= 250` as failure, using the rulebook’s counting method, and cover the 249/250 boundary. Keep any separate platform ceiling clearly separate from the product rule.

### F4 — High: advertised review tools have missing inputs, and pipeline description references are stale

`replica.sh` loads `skill-next/replicas/common.md`, a check-specific prompt, and knowledge files (`skill-next/tools/replica.sh:22`, `skill-next/tools/replica.sh:30`). `sweep.sh` loads `skill-next/replicas/sweep-brief.md` (`skill-next/tools/sweep.sh:16`). These resources do not exist in this tree; existence probes confirm the representative paths (`eval/review4_probe_results_cx.txt:20`–`:22`). These tools are nevertheless marked **built** (`skill-next/TOOLS.md:9`). They use `set -uo pipefail`, without `-e`, so the failed resource copies are not an automatic stop before later work (`skill-next/tools/replica.sh:11`, `skill-next/tools/replica.sh:66`).

Separately, stages 2–3 tell the builder to follow D1–D7 (`skill-next/PIPELINE.md:13`–`:14`), but the current rulebook uses sections 1–8 and procedure steps 1–9, not those IDs (`skill-next/description.md:60`–`:82`). Stuck guidance points to absent `references/description.md` sections 8–9, while the actual rulebook ends with section 8 (`skill-next/stuck-prompts.md:12`, `skill-next/stuck-prompts.md:45`, `skill-next/description.md:158`; absence: `eval/review4_probe_results_cx.txt:24`). The shipped hunt tool similarly needs an absent template (`skill-next/tools/hunt.sh:30`; `eval/review4_probe_results_cx.txt:23`).

**Edit:** provide/version the prompt resources or mark those launchers unavailable with a concrete supported replacement. Validate all required inputs before starting work. Update pipeline and stuck references to the actual rulebook sections; remove or document the out-of-scope hunt tool and its dependencies.

### F5 — High: multi-lane launchers contradict the tracked-job rule

The rule requires one blocking tracked call per lane and explicitly prohibits `&` and detached shells (`skill-next/PIPELINE.md:52`–`:54`). Yet sweeps launch four children with `&` and issue one aggregate `wait` (`skill-next/tools/sweep.sh:18`–`:23`); rounds do the same for review checks (`skill-next/tools/round.sh:30`–`:41`). The hunt launcher uses detached subshells without waiting (`skill-next/tools/hunt.sh:42`–`:45`). `TOOLS.md` describes per-lane tracking merely as a target (`skill-next/TOOLS.md:9`).

**Edit:** expose one blocking lane invocation per tracked job, with the coordinator scheduling each separately and handling each completion. Link the tracked-job rule directly from `SKILL.md`. Do not present aggregate background launchers as conforming implementations.

### F6 — High: cleanup permission is decorative, and capacity can escape the profile

After a build, proof unconditionally requests `docker builder prune -af` (`skill-next/tools/proof.py:137`–`:141`), despite the environment card granting no cleanup authority (`skill-next/dockerfile.md:45`). A mocked invocation with `cleanup_allowed=False` still requested pruning (`eval/review4_edges_results_cx.txt:1`–`:2`). No real pruning was executed.

The Docker lock uses an unrestricted `DOCKRUN_SLOTS` override instead of enforcing the profile maximum (`skill-next/tools/lib/dockrun.py:25`); rounds similarly accept an unrestricted `ROUND_SLOTS` override (`skill-next/tools/round.sh:21`). Thus a two-slot profile does not bound a caller setting a larger override. Hardcoded comments still describe two containers and a default of two rounds as machine-wide facts (`skill-next/tools/lib/replay_patches.sh:44`, `skill-next/tools/round.sh:18`), although the Mac profile specifies eight Docker slots and six review lanes (`machine/mac.example.json:17`, `machine/mac.example.json:25`).

**Edit:** validate and honor cleanup permission before any cleanup; reconcile this with the card’s authorization boundary. Let per-run overrides reduce profile limits, or require capacity changes in the profile. Remove fixed machine-limit claims from generic tools and replace the ledger’s “single-container limit” label with the configured limit (`skill-next/ledger-template.md:20`).

### F7 — High: the built proof tool can certify incomplete or failed execution

The harness contract rejects duplicate/missing IDs, new-mode skips and inconsistent process/report results (`skill-next/harness.md:31`–`:40`). Proof’s parser overwrites duplicate IDs in a dictionary and its solved predicate only checks that failures equal zero (`skill-next/tools/proof.py:53`–`:61`, `skill-next/tools/proof.py:164`). Targeted probes show duplicate cases collapse to a passing result and an all-skipped report satisfies that solved predicate (`eval/review4_probe_results_cx.txt:31`–`:32`). `run()` also discards the Docker return code; a mocked exit 17 returned a passing result dictionary (`skill-next/tools/proof.py:79`–`:84`; `eval/review4_probe_results_cx.txt:33`). The generated shell ends with report printing rather than preserving the test status (`eval/review4_probe_results_cx.txt:34`).

The claimed environment proof is weaker than H4: the uid run changes into writable `/app`, supplies `HOME=/tmp`, and mounts only patches read-only (`skill-next/tools/proof.py:73`–`:80`), whereas H4 requires cwd `/` and read-only `/app` (`skill-next/harness.md:24`–`:29`). Image reuse is keyed only by Dockerfile and HEAD (`skill-next/tools/proof.py:105`–`:110`), contrary to the complete environment identity required by E5 (`skill-next/dockerfile.md:27`–`:31`).

**Edit:** preserve process status, qualify expected IDs, and use the existing strict JUnit reconciliation (`skill-next/scripts/certify.py:114`) for every cell. Run all required cells in the literal H4 environment, and use the documented full environment identity for reuse. Keep the tool marked partial until these checks are implemented.

### F8 — High: a round summary can pass with required evidence missing or defects retained

The summary checks files only when they exist, then passes if its accumulated gate list is nonempty and true (`skill-next/tools/summarize.py:25`, `skill-next/tools/summarize.py:55`, `skill-next/tools/summarize.py:109`). With only a DQ PASS file supplied, the probe printed **GATE PASS** with no AR, SQ or fairness evidence (`eval/review4_probe_results_cx.txt:35`–`:43`). The summary also explicitly allows kept Medium findings to remain without blocking (`skill-next/tools/summarize.py:104`–`:105`), contradicting the no-open-defect requirement (`skill-next/gates.md:42`, `skill-next/gates.md:111`).

The round selects whichever SQ report has the larger issue count for its plain-tag copy (`skill-next/tools/round.sh:42`–`:59`), while the pipeline requires the finding union rather than the report with most findings (`skill-next/PIPELINE.md:44`–`:46`). Both original reports remain available to the verifier (`skill-next/tools/replica.sh:41`), so actual loss by a model is **NOT VERIFIED**; the aggregation contract is nevertheless inconsistent.

**Edit:** declare required fields/samples for each requested checkpoint, fail on missing or malformed evidence, block unresolved in-scope findings, and merge findings with their source identities. Do not let a partial summary represent full round closure.

### F9 — Medium: description authority and shaping levers conflict across cards

The entry card says to keep text fixed after lock (`skill-next/SKILL.md:40`), while the rulebook allows a final change for either too-easy or unsolvable tasks (`skill-next/description.md:6`). Its first too-easy lever removes wording (`skill-next/description.md:100`–`:108`); rollout puts that change after harness, FP, fairness and test discriminators (`skill-next/rollout.md:11`–`:23`). Stuck guidance separately offers a hint of up to 60 words or removal of a test and promise (`skill-next/stuck-prompts.md:15`, `skill-next/stuck-prompts.md:44`–`:45`). A builder receives different permitted actions depending on the card opened.

**Edit:** make the rulebook state the owner’s single exception and delegate only lever ordering to rollout. Make stuck guidance link to that decision rather than supply independent permission to alter text or promises. Replace the blanket lock statement with the same explicit owner-controlled exception.

## Requested checks

| Check | Executed result | Evidence |
|---|---|---|
| `python -B -m unittest discover -s skill-next/scripts -p test_certify.py` | **PASS: 10 tests**, exit 0 | `eval/review4_probe_results_cx.txt:2` |
| `bash -n` on every `.sh` under `skill-next/` | **PASS: all 13 files**, each exit 0 | `eval/review4_probe_results_cx.txt:3`–`:15` |
| `python -m py_compile` on every `.py` under `skill-next/` | **PASS: all 11 files**, exit 0; cache redirected under `eval/review4_cache_cx/` | `eval/review4_probe_results_cx.txt:16`; environment setup at `eval/review4_probe_cx.py:46` |
| Load both supplied machine profiles | **PASS**, both accepted by the loader | `eval/review4_probe_results_cx.txt:18`–`:19` |

Actual Docker environment behavior, real model review results, platform acceptance, first-time check success and rollout calibration remain **NOT VERIFIED**. The executed checks above establish syntax, the existing certify tests, and the specifically demonstrated mocked tool behavior; they do not establish end-to-end readiness.
