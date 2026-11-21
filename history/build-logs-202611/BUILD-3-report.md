Verdict: built for coordinator review. Created `skill-next/SKILL.md`, `skill-next/PIPELINE.md`, `skill-next/description.md`, `skill-next/tests.md`, `skill-next/harness.md`, `skill-next/solution.md`, `skill-next/dockerfile.md`, `skill-next/gates.md`, `skill-next/ledger-template.md`, `skill-next/scripts/certify.py`, `skill-next/scripts/test_certify.py`, and this `BUILD-3-report.md`. No existing workflow or challenge package was edited; the replacement is not installed.

# BUILD-3: construction skill proposal

The design makes the ledger an input to construction, separates planned coverage
from execution, and closes Auto Review -> false-pass -> SQ -> TQ in that order.
The owner's three two-lane sweeps, two independent auditors per passing run and two
replica rounds remain intact. First-time platform success, a guaranteed rollout
distribution, universal language support and time savings are **NOT VERIFIED**.

## Evidence and its limits

Sources were read on 2026-11-07. These abbreviations make the rule map readable:

| Key | Location |
|---|---|
| Brief | `C:/Users/ASUS/OSS/olympus-product/BUILD-3-skill-next.md` |
| F | `C:/Users/ASUS/.claude/skills/olympus-flow/` |
| V | `C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/` |
| H | `C:/Users/ASUS/OSS/claude-code/challenges/shadow-2lane/` |
| P | `C:/Users/ASUS/OSS/shipd/workspace/claude-code/challenges/` |
| M | `C:/Users/ASUS/.claude/projects/c--Users-asus-OSS/memory/` |
| R | `C:/Users/ASUS/.codex/skills/olympus-challenge-creation/references/site-rubric.md` |
| B | F`references/build-checklist.md` |
| C | V`eval/checklist-cx.md` |
| A | V`eval/checklist-review-astra.md` |
| EP / EA | V`eval/checklist-evidence-platform.md` / `checklist-evidence-accepted.md` |
| DR / WS / CO | V`eval/desc-recipe-astra.md` / `workflow-smooth-astra.md` / `check-optimize-cx.md` |

The corpus scan loaded 62 workflow/reference/replica/tool/template text files,
1,226 current-task text artifacts, 24 shadow artifacts and 8,976 historical archive
text artifacts, excluding checkout/dependency directories where identifiable.
Those counts include duplicate patches and some source fixtures, not independent
experiments. The memory index linked 130 distinct files, which were loaded. Inspection
focused on construction rules, the named studies, description histories/readings,
triage, battery/replica outcomes and their cited mechanisms. Large logs and repeated
patches were surveyed by mechanism, not re-executed as historical package reviews.

The studies' claims are not all compatible. For example, EA:447 generalizes successful
offline execution, while C:78 and A:91 retain an offline hazard. The live payload
below confirms that contradiction. Similarly, `V/eval/variants-final.log:4-7`
records surviving variants, but without their complete execution provenance it does
not prove four independently reproduced false passes. `A:31,73-95` makes this limit
explicit. I did not turn labels in old logs into new runtime claims.

CLI use was read-only: `--help`, `problems mine --json --limit 100`, `problems view`,
`checks view`, `runs view` and attempted `runs show`. Eight check payloads were
parsed, covering topic-start, Swift writes, Turso, vet, table visibility, standby,
Docker proxy and SetTable. A ninth (gzip) returned warning-prefixed output and is
not used as freshly verified check evidence here. Two `runs show` attempts (full ID
and exact label) returned server errors; the detailed passer artifact is therefore
**NOT VERIFIED** in this session. No check, rollout or submission was started.

| Current primary observation | Exact check text/field and implication |
|---|---|
| Topic-start `kh72y19gr92knpsq9tktr40y458hbxzx` | `autoReview` job `nx71fagmhej0r9sqgwf27jnz4x8hgk5b`: D/T/S 3/3/3, approved. `verifyTests`: "New tests: 32 tests, 32 failed." `verifySolution`: 957 p2p, 32 f2p, `offlineUidPassed: true`. Concrete support for differential evidence, not a guarantee for a new task. |
| Same topic-start pool | Readiness: "Nova 0/4 solved · Orion 1/4 solved · Vega 0/4 solved"; `agentNoFalsePositives`: "Passed with caveats". `runs view` identifies Orion #5 as `PASS_LEGITIMATE` and still records missing validation-tool friction. Do not erase caveats or substitute evaluator family for task family. |
| Turso `kh717sntzsjbhhmm8grsw7g3r18gys98` | `verifySolution` job `nx73a6g724trqtfy6enmfvew9h8h19n4`: `verdict: PASS`, **`offlineUidPassed: false`**, message "Offline-eval hazard". A headline PASS cannot override a failed operational property. |
| SetTable `kh70yqhmm2xm7b2em939ddtqcn8gatqe` | Current SQ FAIL: "loses accepted stale-partition writes after retention and mishandles pre-future send errors for non-threaded aiokafka." Its older AR is stale and identifies the bypassed threaded transport. Real-mode/fault coverage is necessary; stale AR is historical, not a verdict on today's files. |
| Vet `kh79x33za8xwhg484hnfxj6pws8hnax2` | Runtime/SQ/fairness checks report PASS; readiness says "7/7 passing, some stale", Scope Gate is stale, Auto Review "not run yet". This task is a draft, not proof that the new process already achieved its goal. |
| Recent accepted examples | `mine` reports table visibility, standby and Docker proxy accepted; their fetched AR checks are approved and runtime differentials pass. Topic-start, Swift writes and Turso are **finalizing_review**, not manager-accepted. No eventual acceptance is inferred. |

The numeric T1-T8/S1-S4 meanings come from the dated verbatim rubric R:4-24 and
F`replicas/ar.md:14-26`. Live payloads expose bands, not a complete numbered rule
sheet; current numbering is **NOT VERIFIED** independently. The new skill preserves
the established map and requires current criteria at task start. Post-2026-10-16
submissions carry most weight; older memory is used for failure mechanisms only.

## Construction rule map

IDs below refer to card steps, not identically numbered platform rules. Quoted text
is evidence; the generalized instruction is a proposed control unless directly
specified in the brief or rubric. The cited studies remain documentary evidence
where their original reproductions were not rerun here.

| Card IDs | Construction decision and evidence |
|---|---|
| description D1 | Separate outside/preserve/reject semantics; measure preservation. DR:62 says these "have different test obligations"; B:33-39 requires exact exclusions and forbids reference-only docs as grounding. |
| description D2 | Atomic obligations, not sentence-count games. A:35-45: "each verb, subject/kind, condition, quantifier, and observable effect". DR:193-203 rejects a deterministic platform count threshold; 5-8 is a planning heuristic only. |
| description D3 | Difficulty from necessary cross-layer behavior, with a feasible oracle. F`references/description-playbook.md:48-53` distinguishes real paths from two-reading words; DR:64-68 rejects numeric trap probabilities. Vet de-hinting effects are confounded (DR:190), not a measured rate dial. |
| description D4 | Concise observable prose; keep necessary examples/names, no algorithm or solver-process instructions. DR:70,193-197; V`eval/desc-audit-A.md:570-584` and `desc-audit-B.md:565-581` show narration/examples can pass. R:8,10 grounds what tests may demand. |
| description D5 | Search vocabulary and require concrete separators before lock. F`references/description-playbook.md:67-71`; V`eval/reading-audit-cx.md:3,82-98` says "AMBIGUOUS" and separates off/unavailable/old metadata. A hidden test cannot choose public meaning. |
| description D6 | Human final words and behavior diff, including counterexamples. Brief:47-48; DR:78,182; V`eval/workflow-changes.md:13` records the trim losing expired+unmatched behavior. Historical word split/cap: F`references/description-playbook.md:87` plus DR:76; current numeric limit must be checked. |
| description D7 | Exact lock; redesign requires new solve evidence. DR:198-200: "A stored patch cannot show how its author would reason with changed text." V`eval/desc-history-digest.md:416-433` documents late cuts and meaning changes. |
| tests T1 | Shared path inventory and explicit equivalence classes. B:41-59; C:142-145. A:119-127: an uncovered promise is "OPEN and blocks completion", not "not tested". |
| tests T2 | Multiplicity, both exemption sides, negative space, boundaries, stale/new/unrelated results. C:146-153; EA:392-405. V`eval/variants-final.log:4-7` is a useful warning about single-instance fixtures, not a standalone verified FP verdict. |
| tests T3 | Nonvacuous, independent oracles and all semantic effects. A:39-45 cites the missing second error/effect; C:157-158; R:6,10. A:135-143 corrects absolute "never message text" and "allow extras" rules. |
| tests T4 | Real paths, capable fakes, genuine saved formats, complete lifecycles. EP:89-90; C:156 quotes "its dependency footprint is not a required implementation." Current SetTable SQ and stale AR corroborate the mode-bypass mechanism. |
| tests T5 | Intermediate and eventual states, controlled clocks/events, fault effects. A:47-57; EP:68; R:5. A:163-167 distinguishes an outer watchdog from elapsed-time proof of order. |
| tests T6 | Explicit export, stable suffixed names, clean artifact wording and executed variants/alternatives. EP:97,105,107,110; A:97-107; B:148-154. A:129-133 rejects arbitrary mutation quotas. |
| harness H1 | Discover language adapter from manifests/CI; list IDs/run one/report. F`references/repo-init.md:16-24,39-41`; A:99-107. That repo-init file is marked DRAFT; universal adapter success is **NOT VERIFIED**, so the skill requires qualification. |
| harness H2 | Restore pristine grading assets without restoring candidate production; rebuild twins. EP:91; C:164-165; A:77-83: "verify it remains in the effective tree". No silent restore fallback. |
| harness H3 | Separate modes, exact exclusions, real compatibility retained. R:15-17; EP:92-94. EP:92 records "15 of 22 platform runs" blocked by an internal seek-call pin; that is evidence for investigating the specific pin, not dropping regression suites. |
| harness H4 | Offline arbitrary uid/cleared ENV, scratch HOME/caches, read-only source. B:104-109; A:145-153 rejects externally restoring image ENV. Turso's current `offlineUidPassed: false` is direct corroboration. Read-only source is a conservative portability probe, not a claim every platform uses that exact mount. |
| harness H5 | Expected IDs, diagnostics, exits, failure categories and report counts must agree. R:11-12; C:161-164; A:63-69. V`eval/battery-18.log:30` shows one catch-all compile-error ID, which is insufficient to establish all expected-ID failure behavior. |
| harness H6 | Inject failures after restoration; record actual execution. V`eval/battery-18.log:31`: "acceptance compile error: rc=0 cases=10". A:79 says restoration is a possible explanation, **NOT VERIFIED**. Test the postimage rather than guessing why that probe passed. |
| solution S1 | Plan paths/resources/faults before code. B:41-59; C:166-168; EP:75-79 shows sibling modes and retained residuals causing later SQ failures. |
| solution S2 | Repository ownership and compatible interfaces; no universal fallback semantics. A:155-161 corrects overgeneralization; current topic-start SQ praises API -> conductor -> consumer -> aiokafka integration and explicit capability handling. |
| solution S3 | Review mutation exits, stale callbacks, optional states and rejection side effects. C:153-154,166-168; EP:75-83. Current Swift SQ explicitly credits version rollback and cleanup failures; this is a pattern to investigate, not a rule to force 503 in other repositories. |
| solution S4 | Native quality and focused changes, no LOC padding. R:21-24; B:124-138. Current topic-start AR says "no effective-LOC floor". Normal development tools matter: its current run summaries still report missing validation dependencies. |
| solution S5 | Exported patch proof and a test for every in-contract reference fix. A:97-107; V`eval/triage-sweep-w1.md:7` accepted an old-report fix "no test"; V`eval/triage-fp-v7.md:5` later reproduced that exact escape. |
| dockerfile E1 | Discover pin-specific toolchain/dependency/reporting needs. F`references/repo-init.md:16-29`; V`eval/workflow-changes.md:8`; F`templates/README.md:18-20` says adapt selectors/pin/deselects, not copy them wholesale. |
| dockerfile E2 | Pin complete build inputs and provision test/development tools. CO:38-40,51; current topic-start run summaries identify missing coverage/type tools. EP:108 has a generic rebuild failure and an inferred rebase remedy, not proof that every pin must always be latest. |
| dockerfile E3 | Shared readable dependencies plus writable scratch; no hidden/stale executable shadows. A:73-83,145-153; C:161,165; current Turso offline hazard. |
| dockerfile E4 | No tests in image RUN; comments are style, not a claimed platform ban. EP:104 quotes "The Dockerfile runs tests during build". V`wip02/Dockerfile:3-5,17-21,30-32` still has comments while its build checks pass. |
| dockerfile E5 | Complete image identity and separate local/platform qualification. CO:39-40,51-54; V`eval/workflow-changes.md:9` records wasteful rebuilds. Brief:47-48 reserves the platform build for the human. |
| gates G0/G1 | Four cells, actual IDs/cause, T1-T8/S1-S4 and description, with semantic judgment labeled. R:4-24; A:59-71,113-117. Live topic-start differentials support the mechanics. Three clean bands are a product target, not an invented universal acceptance threshold. |
| gates G2/Repair | No FP waiver; reference defects do not excuse candidate defects; replay after every repair. Brief:12-13,56-58; WS:68-77; V`eval/triage-fp-v5.md:5` is a concrete mixed healthy/failed-check escape. |
| gates G3/G4 | Separate SQ completeness/code quality and per-test fairness/requirement coverage. Current topic-start SQ has both scores 3/3; its separate `taskQuality` payload lists eight criteria. C:138 warns against inventing numbered subrules from those API fields. |
| identity, closure and tools | Hash complete read-sets, outputs and sample IDs; never cache one mandatory independent sample as another. CO:36-70; A:85-95. `certify.py` implements byte hashing, diff syntax/mode separation and XML/ID/status reconciliation only. It cannot establish semantic coverage or provenance. |
| confirmation and scheduling | Brief:23-25 fixes the sample counts. H`answer-key.md:6-12,19-26` records unique findings across lanes. CO:103-110 warns that equal recall after reducing reviewers is unproven. Single-container dockrun/no deletion comes from the active assignment, overriding F's older two-slot/pruning policy. |
| rollout closure | Brief:16; current topic-start/Turso per-family readiness; DR:113-129 requires genuine passes and unique eligible attempts. Local/proxy forecasts, reused trajectories and current historical aggregates cannot prove a fresh-text rollout band. |

## Kept, changed and dropped

Kept: a small coherent contract, human final wording, early environment qualification,
real tests for the sample, one shared path inventory, real execution with external
fakes, pristine regression restoration, exact report IDs, four-cell proof, valid
alternatives/wrong-rule variants, immutable versions, full FP closure and all owner
confirmation samples. These survive across the recent Go/Python/Rust examples;
they are expressed as adapter contracts rather than copied commands.

Dropped or corrected:

- **Review-driven construction and automatic rounds per fix.** Write the obligation,
  path, oracle, wrong-rule and failure-table rows first. Repair once per related batch,
  execute FP closure, refresh affected evidence. Scheduled independent samples remain.
- **Majority vote as reproduction.** F`references/checks.md:47` treats two reports as
  reproduced. The new rule requires an actual scenario/probe or concrete disproof.
- **"Fix, no test, reserve" and rare-case waivers.** The older-report sequence above
  demonstrates the risk. A concrete legal in-scope miss blocks regardless of rarity.
- **Absolute prose bans, sentence counts and numeric trap forecasts.** DR:188-203 and
  the two description audits contradict those generalizations. Preserve necessary
  clarity; never obscure a requirement to make the task harder.
- **Post-lock hint cycling, test weakening to keep a passer, and reference alignment
  to a solver.** DR:117-129 prioritizes correctness and explicit redesign. A failed
  band can be an honest task outcome; it cannot be repaired by certifying a known FP.
- **Arbitrary mutant/alternative quotas and exhaustive Cartesian matrices.** A:129-133
  supports distinct wrong-rule/equivalence classes instead. No finite count proves
  completeness; the independent semantic confirmation remains.
- **PASS headlines, tag/HEAD-only caching and newest-report selection.** Current Turso,
  current vet staleness and CO:38-70 demonstrate why complete identities/details matter.
- **Automatic latest-tip rebasing, universal Docker comment bans, old LOC floors,
  multi-container/prune defaults and inherited platform write permissions.** These
  are unsupported universalizations, superseded policy, or outside this assignment.
- **Guaranteed 1-2 hour completion.** CO:114-116 and WS:53,66 label time budgets as
  hypotheses. The proposed skill reports queues/remaining gates instead of dropping work.

## Remaining model decisions

| Point | Why a written rule cannot decide it |
|---|---|
| Builder's domain design/implementation | Source semantics determine equivalence classes, legal inputs, owning layers and independent oracles; a language-independent regex cannot do that. These are construction work, not extra review jobs. |
| Two pre-lock independent readers | Public meaning and discoverability can differ despite identical words/counts. Require a concrete separating input, not an unsupported opinion. |
| One bounded authorized blind batch per lock | Actual problem-solving behavior is empirical. It supplies diagnostic designs, not a predicted platform percentage. Extra batches need a material reason/authorization, not a desire to tune a number. |
| Three two-lane sweeps and two replica rounds | Owner-required independent semantic confirmation catches unenumerated wrong designs, fairness failures and architectural defects. Repeated sampling has no deterministic equivalence proof. |
| Two FP auditors for every passer | The actual passing design may omit a promised case that neither reference tests nor a reference-only audit reveals. Concrete reproductions settle disagreements. |
| Human platform checks/rollouts | Current acceptance, authorship/plagiarism, build policy and counted model distribution are external results. The skill does not impersonate or automatically invoke them. |

No additional model is used to count words, parse patches, hash identities, reconcile
JUnit or decide whether an unchanged deterministic execution record has the same
complete inputs. Semantic audit reuse is explicitly narrower than deterministic reuse.

## Validation and owner questions

- `python -B -m unittest discover -s skill-next/scripts -p test_certify.py`: **PASS, ten tests**,
  covering contradictory exits/aggregates, missing/extra/duplicate
  IDs, skip/partial-failure holes, empty diagnostics, nested namespaced XML, patch
  syntax and independent-sample identity. These validate the helper, not task quality.
- `certify.py package` read both V`wip01` and V`wip02` successfully: respectively
  198/147 site-style words, 9/10 test paths and 7 solution paths. These are parser
  checks only, not a new package-quality verdict or proof of applicability.
- Bundled `skill-creator/scripts/quick_validate.py` failed to import PyYAML. Its
  frontmatter constraints were inspected and checked directly for this skill's two
  plain scalar fields. Full bundled-validator execution is **NOT VERIFIED**; no
  global dependencies were installed. All twelve deliverables passed LF/UTF-8,
  Python syntax and Markdown routing-link checks; Git whitespace is checked at staging.
- No Docker, historical mutation battery, model review, new solve or platform mutation
  was run. Cross-language adapter execution, improved first-draft yield and reduced
  review discovery are **NOT VERIFIED**, not inferred from this documentary build.

Open questions for the owner (nonblocking for this proposal):

1. Confirm the pinned current platform policy snapshot, including minimum runs,
   sequence-length criterion, word limit and what build inputs Harbor permits. The
   supplied history is not a stable API contract for future tasks.
2. Approve a pilot on at least two language families before installation, measuring
   unique later-sweep discoveries, false alarms, FP escapes and actual elapsed effort.
   This is a proposal; no pilot or extra agent work was launched.
3. Choose the bounded blind-batch size/model mix and authorized resource budget. Keep
   it fixed before seeing results; confirm the repository adapter on each new language.
4. Decide whether LOCAL READY should require every external sample/build result or
   may explicitly carry a pending human gate. This design requires environment/Scope
   gates before full construction and keeps final platform acceptance separate.
