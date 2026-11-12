# Lane A: difficulty retro on the four safedep/vet tasks (2026-11-12)

Read-only. Evidence comes from the local task folders under `C:/Users/ASUS/OSS/claude-code/challenges/` plus one platform
fetch (a trajectory for local-registry Nova #9). Guesses are marked as guesses. Tasks 2 to 4 were read by
three helper lanes. I triaged their reports and re-checked the direct-deps run counts myself (see the correction below).

---

## 1. cc-vet-unused-suppression (Vega 1/8, Orion 0/4, Nova 0/4; accepted in final review)

Repo safedep/vet @ 7574fa1d. The final package is wip03, which is the same as pkg/
(`cmp wip03/solution.patch pkg/solution.patch` gives the same file; the same holds for test.patch).

### Platform history
- wip02 rollouts (runs-platform-20261107, -20261107b, platform-pull-20261107d/runs.txt): **0/16**.
  - 15 runs failed the typo-control assertion.
  - The one Vega that got the typo case right (seq 163167) failed only the older-report case. The stale rows in
    the eval/platform/reeval-wip03 digest say: "treats its missing control list as evidence that a check was off".
- wip03 relaxed the older-report case and dropped the reference's finding fallback.
  - Re-eval: **Vega 1/8** (rd7ak4zagj3g7hj41fnxn0trpx8hr7ps PASS_LEGITIMATE), Orion 0/4, Nova 0/4.
  - eval/decisions.md: "All 15 failures first at check-not-run.txtar:21 (typo id); 2 Vega also fail full-scan:11 +
    package-rule:7".
  - The FP panel upheld the pass with a judge dissent. Auto Review gave 3/3/3.
- Local solves (flow-status.md S1d-S6b; eval/solves-summary.md):
  - wip01: 3/4 (too easy).
  - Deepening sentence ("check turned off"): 2/4, then 1/4 after the FP audit.
  - v7: 1/4.
  - After the typo case was added: 0/4 ("s2, s4 miss only the typo line; s1 only the older-report line").

### Q1 Hard point
**Typo case.** In check-not-run.txtar, a `typo.yml` suppression whose `control:` is an id vet does not know
must still get `policy_suppression_unused` (wip03/test.patch, check-not-run block lines 26-27).
- All 15 failing re-eval runs miss it (digest "Runs" table: "treats an unknown control ID as a disabled check").
- **Not named.** The description says only "If a check was turned off for that scan, we should not report its
  suppressions as unused". Auto Review defended the case as the default rule: "an unknown control was not turned off".
- It is a **neighbour state of the exception**: an id that is not on, but also is not off.
- It was added late, at sweep w3 (eval/triage-sweep-w3.md row 1: "ACCEPT (user 2026-11-06: fix + test)", from 5
  lanes).

**Second miss.** 2 of 8 Vega runs count a shadowed second match as used (full-scan:11, package-rule:7).
- This is implied by "does not suppress a finding" together with base first-match ownership. The R2 sentence was
  merged out at the user re-open (flow-status S1).

**Older-report case (wip02 only).** A saved report with no `controls` in its header.
- The header doc (base/report/report.go:33-36) says "A report of an older vet has none".
- It caught the eventual passer, and the case was relaxed in wip03.

### Q2 Obvious design vs reference
The obvious design is the one every platform run built:
- used set = `f.Suppression.Rule` plus the expired refs;
- skip a suppression when `!ran[s.Control]`, where `ran` comes from `Header().Controls`. Seen in
  rd71p76mj3yfpf2rexrvvrm40s8hsddg/solution.patch:225-231 and rd70aym2sy8t5rwcfvaxw060d98hrjvr :146;
- `Header().Scan.Mode != delta` for pull request scans;
- delete the old policy diagnostics before re-evaluation.

The reference (wip03/solution.patch:151-180) differs only in the turned-off predicate. It skips a suppression only
when the control is **known** (`controls.Catalog()` plus the header plus RuleControl) and **not on**:
`if sup.Control != "" && known[sup.Control] && !on[sup.Control] { continue }`.

The passer did the same thing: it built `Options.Controls` from `controls.Catalog()` in runner.go
(rd7ak4zagj.../solution.patch:524-530).

### Q3 Choke points
Entry points:
- full scan;
- continued scan;
- PR scan (`--base-ref`);
- `report show --policy` on the scan DB, JSON and JSONL.

All of them reach **one site**, `policy.Evaluator.Finalize`. It is called from 3 places:
- base/internal/engine/engine.go:397
- base/internal/runner/runner.go:332
- base/internal/runner/saved.go:218

Mode and controls both come from `Store.Header()`: state/records.go:17 and reportdoc/doc.go:99.

The one secondary site is the runner-written `base_policy_invalid` on report show.
- Local GPT solves missed it (solves-summary s3).
- No platform run missed it.

So an agent that edits Finalize, plus a delete method on the two stores, gets every path right.

### Q4 Primitives at base
Yes, for everything except the hard point:
- `finding.Suppression.Rule` (base/finding/finding.go:327) already records which suppression hid each finding, so
  the used set comes for free.
- `suppression()` (base/internal/policy/eval.go:135-148) already collects expired refs.
- `Header.Controls` (report/report.go:36) lists the controls of the scan.
- `Header().Scan.Mode` gives the PR mode.

The hard point's own primitive also exists: `controls.Catalog()` (base/internal/plugins/controls/catalog.go:15).
But its only production caller is `vet policy control` (base/internal/cmd/policy/control.go:23), far from the seam.

Meanwhile the nearest primitive, `Header.Controls`, invites the wrong predicate. So the primitive that is near the
seam leads to the obvious design, and the one that computes the hard point sits elsewhere. That is why the case
stayed hard.

### Q5 Design spread
There was one semantic design. It had two variants of the turned-off predicate:
- "absent from the header": 14 runs;
- "known and absent": the passer and the reference.

There was also a third variant on the older-report neighbour: "an empty header list means everything is off". In
wip02 it was the passer's only miss.

The used-set variant ("matches = used", 2 Vega runs) is a slip, not a design. The final passer was separated by the
typo case alone. The separator before it was the older-report case, and that was relaxed rather than kept.

### Q6 Source
- **Final hard point:** a neighbour state of an exception (unknown id vs turned-off check), not named in the
  description.
- **Planned hard points that did not bite on the platform:**
  - the expired-after-live order bug, R4;
  - PR mode;
  - report-show replacement.
- Second code path: minor (base_policy_invalid, local solves only).

### Q7 Gates
- **(a) Choke-point map: RED.** One Finalize covers every entry point.
- **(b) Primitive grep: RED** for the core (Suppression.Rule, Header.Controls, Scan.Mode). The hard point's
  primitive is distant, which is the reason the task survived.
- **(c) Obvious-design spike: RED.** The header-driven design fails only one assertion (typo) on one path.
  Before sweep w3 it failed nothing: wip01 3/4 locally, and the wip02 platform runs all pass everything except the
  typo and older-report lines.
- **(d) Design spread: RED.** One design plus a single predicate choice.

All four gates would have rated the seam too easy, and they would have been right about the seam. The task was
accepted only because a late, unnamed neighbour case (one assertion) split the runs, after a second neighbour case
had to be relaxed. That is fragile: the FP panel had a judge dissent, and SQ once scored 2/3 on that exact predicate
(eval/decisions.md).

---

## 2. cc-vet-local-registry (status finalizing_review, v1 locked; final Nova 1/4, Orion 0/4, Vega 0/4)

Helper lane report, triaged. Sources: ledger.md, eval/rollout1-analysis.md, eval/decisions.md, eval/verify-v13.log,
eval/compare/c2/report.md, eval/diffgrid/result2.txt, and the trajectory of Nova #9 (rd7555975n).

### Platform history
| Round | Description | Nova | Orion | Vega |
|---|---|---|---|---|
| Rollout 1 | continued scans only | 2/2 | 2/2 | 1/2 |
| Rollout 2 | adds the PR clause "including the version a package is upgraded from" | 4/4 | 4/4 | 0/4 |
| Re-eval 1 | same as rollout 2 | 1/4 | 0/4 | 0/4 |
| Re-eval 2 (v13, 25 tests) | same as rollout 2 | 1/4 (rd7dgct89k15) | 0/4 | 0/4 |

Re-eval 1 had 5 runs with the fault put on the task.

### Q1 Hard point
- **Nova x3 (23/25):** `pull-request-previous-only-local` and its pypi twin, case "idD". The base registry copy of a
  version, in another manifest, is switched to vendored at head. The reference does not look it up, because at head
  every copy is local.
  - Not named; at most implied by "If the version is only a local package we should not look it up", read at head.
  - The platform called it unfair in re-eval 1. It accepted it only after both-direction steps were added.
- **Orion x4:** idD, plus `pull-request-previous-version` and `TestContinuePullRequestLooksUpPreviousVersion8d2b`.
  Locality was taken from a base-only snapshot. These are stated cases.
- **Vega x4 (18-20/25):** only the upgrading manifest's base locality, so the PR previous-version tests fail.
  Vega #3 also fails same-lockfile duplicates because of the dedupe in
  internal/plugins/extractors/scalibr/convert.go:87, which is discoverable only from the repo.

### Q2 Obvious design vs reference
Obvious design, as built by all of rollout 1: prefer the non-local copy in the `PackagesToEnrich` copy subquery
(base/internal/state/query.go:412), and re-open the local skip on continue.

The reference also changes four more things:
- the same-manifest merge in convert.go;
- REMOVED rows ordered last;
- `skipped` counts only while no registry row exists;
- prior locality is the AND of the upgraded rows' `PreviousLocal`, overridden by any head registry row
  (query.go PriorToEnrich).

### Q3 Choke points
There are many:
- copy subquery, query.go:412;
- continue skip, internal/engine/enrich.go:179-181 plus the `enriched` predicate at query.go:431;
- extractor dedupe, convert.go:87;
- PR removed rows lose `Local` at delta.go:260;
- PR previous version: delta.go:241-243 and PriorToEnrich, query.go:467-490.

Editing the shared subquery covers only fresh and plain PR scans.

### Q4 Primitives
- **Headline case: yes.** `Package.Local` and `Checkable()` (model/package.go:44, :109), and the copy rule is a single
  `ORDER BY manifest_id`. The fix is one line, which is why v1 was 5/6.
- **Prior-version locality: no.** PriorToEnrich builds `Package{ID}` with Local=false. diff's `exact` map
  (delta.go:212) holds the base package, but the code never reads its Local. New plumbing was needed
  (PreviousLocal).

### Q5 Spread
- **Re-open mechanism:** 4 Nova mechanisms that are observably equivalent (compare c2 rows c2-c4).
- **Prior locality:** 4 observable designs:
  1. Vega: upgrading manifest only.
  2. Orion: base-snapshot registry evidence.
  3. Nova x3: head registry rows OR a base copy switched to local.
  4. Nova #9: same as the reference.

The separator was idD alone. 3 compare lanes, 26 cells and a 72-scenario grid found no other fair split.

### Q6 Source
- A second code path: PR previous version through diff and then PriorToEnrich, plus the extractor dedupe.
- The final separator is a neighbour state (a copy switched to local in another manifest) that turns on the
  reference's own base-vs-head choice.
- The reference is not consistent here: it counts REMOVED base registry rows but not switched (MODIFIED) ones.
  claude2 AR flagged this as an S1 Medium; the platform did not.
- The PR path had to be **named** before anyone reached it.

### Q7 Gates
- **(b) RED at v1:** one ORDER BY on an existing Local flag.
- **(c) RED at v1:** the sample sketch failed only the two continuation tests, which is one path family.
- **(d) RED** on the main seam (observably equivalent designs).
- **(a)** looks "many" when drawn honestly, but stages 0-3 mapped only fresh plus continue through the one query. The
  PR and extractor sites surfaced only in the rollout-1 replay.

The gates would have flagged v1 as too easy, correctly. The final split rests on a reference design decision that the
platform first called unfair.

---

## 3. cc-vet-continue-usage (draft, parked; rollout 1 Vega 1/4, Orion 2/4, Nova 0/4)

Helper lane report, triaged. Sources: eval/platform/rollout1 and reeval1, eval/platform/compare.md,
eval/calib/{options-summary,a-report,lever-h-triage}.md, eval/grade-solvers.log,
shipd/seams/safedep-vet.md:137-165. The CLI `problems view` timed out for the lane, so the live state is unchecked.

### Platform history
- Rollout 1 (description 7b4818e0, 24 tests): Vega 1/4 (Vega3), Orion 2/4 (Orion6, B2Orion6), Nova 0/4, for 3/12.
  Local solvers on the same files: 1/6.
- Calibration paste (40 tests), local replay prediction: Vega 1/4, Orion 0/4, Nova 0/4.
- The platform re-evaluated the two Orion passers. Both fail only
  `TestContinuedScanReplacesTheWarningsOfAnEnricherMarkedAsTheCodeAnalysis7c4e/an_enricher_marked_as_the_code_analysis`.
  - One got FAIL_MISSED_REQUIREMENT (agent blamed).
  - The other got FAIL_TEST_MISMATCH (task blamed: "synthetic... lacks SourceEnricher").

### Q1 Hard points
- **Nova x4:** `KeepsFinishedRegistryLookups7c4e` and `KeepsOtherWarnings7c4e`. They count any `plugin.Diagnoser` as
  code analysis, and the hidden registry fake implements Diagnostics. The sentences are named, but the trigger
  exists only in a fake: at base, codeusage is the only Diagnoser.
- **Vega4, B2Vega3, B2Vega4:** `TestFailedAnalysisLeavesNoUsageFromTheStoppedRun7c4e`. The hidden helper built
  `engine.Enricher` by hand, without the agents' new Clear callback. The platform blamed the task 3/3. The case is
  implied.
- **B2Orion5:** the planned Merge trap. `Enrichment.Merge` (model/package.go:72-77, `cmp.Or`) keeps the stale Usage.
  This is the only genuine catch of the planned hard point, and it is implied.
- **Orion5:** the extraction warning is duplicated through the revive fast path (extract.go:280-287). This is a
  second path, implied by "other warnings ... displayed".

### Q2 Obvious design vs reference
The nearest pattern is `ClearFindings` (scanfile.go:581, called at evaluate.go:24): on Continued, delete the code
enricher's rows and run it again.

All 12 platform runs went further and cleared Usage and rebuilt the graph. They diverged from the reference on three
choices:
- **Which enricher counts as code analysis:** the reference uses `Whole`; Vega3 `Local`; the Orion runs
  `SourceEnricher`; Nova `Local || SourceEnricher || Diagnoser`.
- **Where Usage is cleared:** in the engine, or through a Spec callback.
- **How the graph is refreshed:** re-graph, or re-extract.

### Q3 Choke points
There is one entry point (the continued `vet scan`; PR mode and endpoint audit share its code). It runs through four
sites:
- the skip query, state/query.go:431;
- Merge, model/package.go:72-77;
- the diagnostics append, scanfile.go:716;
- the revive fast path, extract.go:280-287.

They form one linear pipeline that a trace of `Continued` reaches, and every run touched both enrich and extract. In
effect this behaves like one site.

### Q4 Primitives
Yes:
- `ClearFindings` (scanfile.go:581);
- `r.graph` (extract.go:349), which the reference reuses;
- `ReviveArtifact` (scanfile.go:555).

The Merge trap fell to `json_remove` or a blob rewrite (11 of 12 runs). What stayed open was the selector, and every
candidate selector has exactly one real member at base: codeusage (enrichers.go:106, codeusage.go:392).

### Q5 Spread
- 3 passers built 2 designs. The near-passers add 2 more (the Clear callback and the Diagnoser selector).
- Lane A measured 424 real-code cells and found **0 cells that split Vega3 from Orion6** (a-report.md).
- Only fakes split the designs: `localWarning7c4e`, and a stand-in partial extractor with a venv grapher.
  lever-h-triage found 0 fair cells.

### Q6 Source
In production this is lifecycle (the continue edge), a second path (revive) and a neighbour state (Merge). These
caught only 2 of 12 runs.

The measured separation came from a classification that exists only in fakes: multiplicity of 1 in production. The
judges blamed the task on 4 of the 5 split runs they judged.

### Q7 Gates
- **(a)** counted 4 sites as "many", but one trace reaches all of them. The gate should count traces, not sites.
- **(b) RED, missed:** ClearFindings, r.graph and ReviveArtifact. Stage 0 scored "p~0.7, ~24%"
  (safedep-vet.md:162).
- **(c) passes on paper:** the naive design fails 2 or more fair cases on different paths. It was misleading, because
  no strong agent built the naive design.
- **(d) RED, not checked:** the selector freedom has no production consequence.

---

## 4. cc-vet-direct-deps (draft; too easy)

Helper lane report, triaged, with the counts re-checked.

### Platform counts (correction)
I checked eval/platform/rollout1/runs.txt, rollout2/runs.txt and pull-now/view-*.json. The real count is
**13 passes of 16 graded runs**, not 14/16. Nova #2 rd7791rb failed on infrastructure and has no verdict.

| Description | Nova | Orion | Vega |
|---|---|---|---|
| v1 c02601e7, 35 tests | 2/4 (fails rd7fjfwr and replacement rd7fwwdj) | 4/4 | 3/4 (fail rd7861jp) |
| v8, requirements only | 0 runs | 2/2 | 2/2 |

"Solved by one model only" fails. Two FP audits (eval/fp/fp-r8-claude.md, eval/replica/fp-audit-r8.md) find every v8
passer DESERVED.

### Q1 Hard point
- **Vega #1, rd7861jp, 33/35:** fails `TestGraphOfImportsOfARequirementsFiled1b9` and its unknown-dependencies
  twin. It used the extractor's `p.Direct`, which is true for every requirements.txt package, instead of the graph
  roots. The rule is stated; the failing input is found only in the repo.
  - The builder's own sample sketch has the same bug: sample-pasted/solution.patch:36.
- **Nova x2, 34/35:** fail `TestUnknownDependenciesLeaveNoListd1b9/an_unknown_direct_dependency_that_pulls_the_package_in_by_a_known_path`.
  Their hand-written walk does `continue` at an open node and drops its known edges (rd7fjfwr solution.patch:300-302).
  The case is implied.
- **The intended hard points did not bite.**
  - Unknown dependencies, meaning no list versus a partial list: this is exactly the base
    `PathFrom`/`MayReach` tri-state.
  - Saved scans: findings persist as a JSON blob (internal/state/scanfile.go:663), so a new field round-trips for
    free. Live and saved policy runs share `policy.NewInput` (input.go:99). 0 of 16 runs failed this.

### Q2 Obvious design vs reference
Obvious design: loop over `m.Graph.Roots()` in `evaluateManifest`. A root with a `PathFrom` path is listed. If any
root without a path can `MayReach` the package, there is no list.

This **is** the reference predicate. V11, 9 lines, passes 35/35 (eval/variants-v8.log).

### Q3 Choke points
- **Entry points:** full, PR, continued and endpoint scans, plus policy in Finalize, saved scans, and JSON/JSONL
  reports.
- **One compute site:** `run.evaluateManifest` (internal/engine/evaluate.go:54-70). All 16 runs edited it.
- **One exposure site:** `NewInput`.
- **Persistence:** automatic.

### Q4 Primitives
Yes:
- `Graph.PathFrom` (model/graph.go:175) and `Graph.MayReach` (graph.go:217).
- The exact tri-state is already written at internal/engine/reach.go:309-312: `case len(m.Graph.PathFrom(from,
  p.ID)) > 0: ... case m.Graph.MayReach(from, p.ID): ReachNoDependencySource`.
- `Graph.Root` (graph.go:71).

The builder's own facts call the hard point "MayReach vs PathFrom" (eval/description_facts.md:44).

### Q5 Spread
1 semantic design in 4 implementation shapes. Passers differ only in where the field lives and in speed, and no test
checks either.

### Q6 Source
- **Intended:** a neighbour state of an exception, plus a second path.
- **Actual:** both were neutralised by the repo. What remained was wording plus repo (the Direct flag versus the graph
  root), which caught 1 run.

### Q7 Gates
All four RED:
- **(a)** one compute site plus one exposure site;
- **(b)** a helper computes the hard point. The hunt listed only PathTo (shipd/seams/safedep-vet.md:176);
- **(c)** the sketch existed before the Scope Gate and fails 2 cases on one path. Without `p.Direct` it passes
  everything;
- **(d)** 1 design.

The cheapest catch was (b) at the hunt: a grep of `func (g *Graph)` and of callers in internal/engine shows
reach.go:309.

---

## Verdicts

**cc-vet-unused-suppression.** The seam is easy. One Finalize site covers every entry point. The repo already records
which suppression hid each finding (`Suppression.Rule`), the scan mode and the scan's controls. The obvious
header-driven design passes everything except one late, unnamed neighbour case: an unknown control id is not a
turned-off check. That case is computable with `controls.Catalog()`, which is far from the seam. It reached Vega 1/8
only after a second neighbour case (an older report with no control list) was relaxed. The result is accepted but
fragile: the platform split rests on one assertion line, and SQ and the FP panel each wobbled on that same predicate
once. The stage-0 gates would all have said "too easy", and the history shows they would have been right about the
seam.

**cc-vet-local-registry.** v1 was too easy: one ORDER BY change on an existing `Local` flag gave 5/6 passes.
Difficulty arrived only once the description named the PR previous-version path. That path has no primitive and needs
plumbing across delta, model and state. The final 1/12 (Nova only) rests on idD, a base-vs-head choice inside the
reference, which itself treats removed and switched copies differently. The platform first called it unfair. Orion's
and Vega's misses are real misses on stated PR cases. Nova x3's miss is a defensible alternative reading.

**cc-vet-continue-usage.** The seam looked like two moderate hard points (the Merge trap and the graph revive). Strong
agents found both, because the repo has the clear-and-recompute template (`ClearFindings`) and the graph helper, and
one trace of `Continued` reaches every site. The Merge trap caught 1 of 12 runs. Separating the designs further needed
fake enrichers, because every selector property has exactly one real implementation (codeusage). The judges called
those fakes unfair on 4 of the 5 split runs they judged, so the task is parked.

**cc-vet-direct-deps.** It was too easy before any test was written. vet already ships the reachability machinery:
`PathFrom` and `MayReach`, with the exact tri-state written out at reach.go:309-312. There is a single per-finding loop,
and findings persist as JSON, which makes saved scans free. The obvious design is the reference (V11, 35/35). The only
real trap was the `Direct` flag versus the graph root, and it caught 1 of 16 runs, plus the builder's own sketch.
Removing the corner sentences (v8) changed nothing, because the repo carries the answer. All four gates would have
flagged it, and the evidence was already written down (description_facts.md:12,44 and the sample sketch).

## Summary table

| task | hard point | source | choke points one/many | primitive yes/no | obvious design fails? | design spread | gate verdict |
|---|---|---|---|---|---|---|---|
| cc-vet-unused-suppression | unknown/typo control id must still be reported as unused (check-not-run.txtar:26-27); earlier the older report with no control list | neighbour state of an exception (unnamed) | one (policy.Finalize, 3 callers; mode and controls from Store.Header) | yes for the core (finding.go:327 Suppression.Rule, report.go:36 Header.Controls); the hard-point helper controls.Catalog exists but is distant (catalog.go:15, one caller cmd/policy/control.go:23) | yes, but only 1 assertion on 1 path (14/16 runs built it) | 1 design, 2 predicate variants | a/b/c/d all RED; accepted only through a late unnamed neighbour case, so fragile |
| cc-vet-local-registry | PR previous-version locality; final separator idD (a copy in another manifest switched to local) | second code path + neighbour state that turns on the reference's base-vs-head choice; the PR path had to be named | many (query.go:412, enrich.go:179, convert.go:87, delta.go:241-260, PriorToEnrich) | yes for the headline (Local, ORDER BY); no for prior locality | v1: no (5/6 pass); final: yes (Vega and Orion fail stated PR cases) | main seam 1 observable; prior locality 4 | (b)(c)(d) RED at v1; hard only after the PR path was added; final split fragile |
| cc-vet-continue-usage | stale Usage after a failed analysis (Merge) + graph of a revived manifest; measured split = which enricher counts as code analysis | lifecycle + second path in production; the split comes from a fake-only classification (multiplicity 1) | 4 sites on one trace (acts as one) | yes (ClearFindings scanfile.go:581, r.graph extract.go:349, ReviveArtifact scanfile.go:555) | naive design yes (2 fair cases); no strong agent built it | 4 designs; 0 real-code cells split the passers | (a)(b)(d) red flags missed; (c) passed but misleading; parked |
| cc-vet-direct-deps | intended: unknown deps -> no list, saved scan; actual bite: Direct flag vs graph root (1/16) | neighbour state + second path, both neutralised by the repo | one (evaluate.go:54-70 + NewInput; persistence automatic) | yes (graph.go:175 PathFrom, :217 MayReach, tri-state at reach.go:309-312) | no (sketch fails 2 cases on 1 path; V11 passes 35/35) | 1 semantic design, 4 shapes | a/b/c/d all RED; (b) at the hunt is the cheapest catch |

## Checks the workflow is missing

1. **Primitive grep near the seam, completed and weighted.**
   - List every method of the core types and every caller of the helpers the hard point needs, near the hook site.
     direct-deps stopped at PathTo and missed reach.go:309.
   - Grade each helper as "near the seam" (same file family or already on the path) or "distant".
   - A near helper that computes a hard point is a stop.
   - A near helper that invites the *wrong* predicate is a good sign. In unused-suppression, `Header.Controls` was
     near and `controls.Catalog` was distant, and that was the only difficulty that survived.
2. **Choke-point map counted in traces, not sites.**
   - Ask: does one trace of the flag or entry point reach every site? continue-usage had 4 sites on one trace;
     unused-suppression had one Finalize behind every entry point.
   - Map every scan mode (PR, continued, saved, extractor dedupe) before the lock, not only the modes the description
     names. local-registry found its PR and extractor sites only in the rollout-1 replay.
3. **Strong obvious-design spike before the Scope Gate.**
   - Write the obvious design at agent strength, from the description words plus the nearest repo pattern, not a naive
     one.
   - Run it against the planned test list. Require at least 2 fair failures on different paths or neighbours.
   - Evidence that the samples already were spikes and nobody counted them:
     - direct-deps: the sample sketch;
     - local-registry: the v1 sketch;
     - unused-suppression: the header-driven design, which fails one assertion.
4. **The "valid simple variant" alarm.**
   - When a short variant built on repo helpers passes the whole suite, raise the too-easy alarm automatically.
     direct-deps V11 passed 35/35 and was only recorded as PASSES.
   - The same goes for when local solves pass everything except one late-added assertion.
5. **Production multiplicity count.**
   - For each property a test discriminates on, count the real implementers at base.
   - If there is 1, only fakes can separate designs, which is a fairness risk. continue-usage: Local, Whole,
     SourceEnricher and Diagnoser each have only codeusage.
   - Hidden tests must build plugins through the production builder, not through literals.
6. **Persistence and round-trip probe for every "saved state" hard point.**
   - Check whether a new field on the stored struct round-trips by itself. direct-deps: finding JSON at
     scanfile.go:663.
7. **The separator must be a stated case.**
   - Before accepting a split, confirm it comes from a sentence in the description, not from a choice inside the
     reference.
   - Check that the reference is consistent across sibling states:
     - local-registry idD: removed vs switched copies;
     - unused-suppression: the older report with no control list.
8. **Single-assertion dependence.**
   - Record how many assertions carry the platform split. If removing one assertion turns the result into "too easy",
     flag the task as fragile before submit.
   - unused-suppression: check-not-run.txtar:26-27 alone carries Vega 1/8.
9. **Pass-count bookkeeping from the view JSON.**
   - Count passes per family from the view JSON, including infra replacements. The direct-deps runs.txt misses
     rd7fwwdj, and the true count is 13/16, not 14/16.
