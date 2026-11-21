# Gates, repair and evidence identity

`D/T/S/L` mean description/test.patch/solution.patch/Dockerfile. `B` is the pristine
commit **and tree**; `E` is image digest, architecture, toolchain/dependencies, runner,
environment/mount/timeout policy. Execution evidence includes command, exit, expected
IDs, per-ID results, raw log, source/postimage identity and output hashes. A model
record also includes prompt/catalog/model/effort and independent sample identity.
Dates, mutable tags, latest-file globs and summary labels are not sufficient keys.

## G0 - Evidence prerequisites (deterministic)

Reconstruct explicit exported paths in grading order on pristine B. Inspect modes,
apply checks, overlaps, removals and accidental files. Run through executable test.sh.
Complete H6 and the four cells: base/base PASS, new/base every expected ID FAIL for
the intended missing feature, base/reference PASS, new/reference PASS. Missing new
APIs may cause a verified feature-related compiler error; incidental setup failures
do not prove T1. Keep those reasons distinct. All new IDs must appear without skips;
base skips are exact, predeclared, justified and unchanged across candidate runs.
Before every paste run `tools/fastcheck.sh <task> <image> <tag>`: it repeats only the parts whose inputs changed
(test.sh -> the root baseline snapshot; test.sh + solution -> the after run as uid 1000; hidden tests -> new mode, T1 per
leaf, lint, the kept wrong versions) and ends with the verifySolution set verdict (`tools/junit_sets.py`); a kept wrong
version whose edit no longer applies fails it. The platform-identity cells of proof.py (`--root-base --two-user
--plain-new`) are the same check inside the full proof.

## G1 - Auto Review rubric, the local structure check

Auto Review left the platform's readiness list on 2026-11-17 (its report still exists and mirrors Solution Quality);
the checks that block a task today are Test Quality (verifyFairness) and Solution Quality, and both execute inputs.
T1-T8 and S1-S4 stay the best local rubric for the shape of the package: walk them first, then close G2-G4 by
execution (tq-once.md, sq-once.md, `tools/fastcheck.sh`) before any model review. D = deterministic evidence, J =
semantic judgment by the builder and the scheduled independent confirmation (not an extra model call per row).

| Rule | Exact local self-check | Kind |
|---|---|---|
| T1 | Four cells complete, intended base-failure reasons; affected regressions retained. | D + J for cause |
| T2 | No oracle depends on uncontrolled time/randomness/order; causal gates/controlled clock and final repeat vectors. | D + J |
| T3 | Assertions are nonvacuous and each plausible wrong-rule class has an executed behavioral discriminator. | D + J for class completeness |
| T4 | Every atomic obligation, ordinary variant and materially distinct promised path maps to assertions; no unexplained gap. | J, checked against D evidence |
| T5 | Every assertion has text/base grounding; fixtures/fakes permit valid designs and real promised modes. | J + alternative execution |
| T6 | All four cells run offline under the actual uid/env/mount contract; dependencies available. | D |
| T7 | Wording/order/format pins are public; all permitted results remain accepted. | J + alternative execution |
| T8 | Exact IDs, statuses, exits and real diagnostics survive every H6 failure branch. | D |
| S1 | All promised effects/paths/faults implemented, including code newly reached by the change. | J + probes |
| S2 | Native checks/regressions pass; patterns, interfaces and lifetimes remain compatible. | D + J |
| S3 | Every hunk maps to required behavior/integration; no unrelated churn or grading bypass. | J + diff inventory |
| S4 | No process residue, weird/generated comments, unjustified defenses or inconsistent conventions. | D lint + J |
| Description | description.md (the rulebook) checklist all yes, about 250 site words as guidance; grounded, single-reading, clear, necessary text; current category/prechecks. | D mechanics + J meaning |

Local target is clean description/tests/solution bands (3/3/3), with every concrete
in-scope defect closed. This is the product's stronger target, not a claim that the
platform always rejects band 2. Record actual field bands/issues and policy version.

## G2 - False-pass review, second priority

Execute the reference, valid alternatives, wrong-rule variants and every stored
clean solver patch on current tests. Grade pristine base tests too. Record APPLIED,
RESTORED_AWAY, APPLY_ERROR, BUILD_ERROR, HARNESS_ERROR, TIMEOUT or EXECUTED separately.
Only the intended behavioral failure proves a discriminator. For each survivor,
either establish it is valid, cite a real exclusion/unreachability proof, or keep OPEN.
Every gap has a kept wrong version (eval/wrong/kept: EDITS, KIND, EXPECT) that `tools/wrong_versions.py` re-runs on
the final suite, each wrong one failing exactly its leaves and each control passing; `tools/mutants.py gen` and `run`
sweep the reference's added lines (neg, drop, del, flip, true, false, swap), once with and once without the coverage
filter, and every survivor gets a test or a written reason checked against the three sources.

One independent auditor (a second when it says NOT_DESERVED or is unclear) inspects every current passing **run**, its actual production
patch and the literal contract. They give a per-obligation design trace and attempt
concrete legal counterexamples. Reproduce a suspected false pass: current suite
accepts candidate; an in-scope probe shows it violates a grounded requirement. Run
the reference on the same probe. If the reference also fails, fix both the reference
and missing coverage; this does not excuse the passer. A reference audit alone, test
replay alone, rarity, or reviewer agreement cannot certify a deserved pass.

Gate: no confirmed or unresolved grounded FP, and a current independent disposition
per passer. Missing runs/audits are NOT VERIFIED. Zero passers vacates per-passer jobs
but does not demonstrate solvability. No finite battery proves absence of all defects.

## G3 - Solution Quality, third priority

Walk S1-S5 against all obligation/path rows. Report comprehensiveness and code quality
separately on the 0-3 scale; target 3/3 each. Inspect mutation exits, rejected inputs,
fallbacks, ownership and sibling modes, not only lines added. Native checks are D;
architectural fit and completeness are J. In-scope defects are fixed, never retained
as residuals because base has the same behavior. Do not alter locked text to excuse one.

Test world vs real world: list what the harness simplifies (retention, time between steps, transactions and buffering,
crashes and fencing, one clock or node, modes no test sets) and trace the reference against production code and default
configuration for each. Mutants only break code the reference has (faust window: 2 Auto Review Highs past 60+ mutants).
Gate before every Solution Quality purchase: sq-once.md section 8 walked on the exact bytes (executed inputs on the
normal path, the timing at 1x and 2x, every note fixed or declined in writing).

## G4 - Task Quality, fourth priority

For each test record fair/unfair/uncertain, assertion, visible grounding and any valid
design it rejects. For each obligation record covered/partial/missing with actual
assertions and a plausible escaping wrong design for a claimed gap. No unfair test,
unresolved uncertainty or missing in-scope coverage may close. These are J with D
probe support. Also retain the platform's distinct eight taskQuality fields: authentic
engineering, presentation, clarity, fairness, bounded scope, nontriviality, objective
verification and long-horizon/system-level work. `verifyFairness` and `taskQuality`
are different API checks; neither is inferred from the other's PASS.

## Repair - mandatory after every fix (deterministic; model reviews follow PIPELINE.md "Review schedule")

1. Mark the candidate DIRTY. Record the finding's exact quote, legal input, expected/
   actual result and evidence. Consensus is not reproduction. Test speculative claims;
   NOT VERIFIED is neither accepted fact nor a dismissal. Reject only with concrete
   scope/valid-alternative/disproof evidence. Merge duplicates but retain every source.
   When reviewers split, decide by what Auto Review enforces: a literal promise holds on every branch, and a wall-clock
   timer in a test is a T2 finding. Never by majority, by "the platform did not flag it last time", or to keep a passer
   (near-miss-release.md is the only exception). Write which rule decided the row (goka: both overruled findings came
   back from the platform).
2. Fix the whole demonstrated class on sibling paths in one batch. Add the smallest
   grounded discriminator for every in-contract reference fix. Repair unfair pins
   without removing the underlying promise. Never select cases merely to hit a rate.
3. **Recheck FP risk now:** regenerate affected obligation/assertion links; execute
   reference + valid alternatives + known wrong variants + all stored clean solver
   patches against the repaired package. Include deep failures after relaxations or
   harness/environment changes. Record the newly accepted wrong designs a relaxation
   could release. Inspect probe postimages so restored-away edits cannot count.
4. Audit every new/changed passer once (a second audit on the trigger above). An old semantic audit can carry only with an
   explicit identical read-set and sample record; uncertain dependency means re-audit.
   A changed reference may reveal coverage missing from every passer. Close G2 even
   when the fix originated in G1, G3 or G4.
5. Invalidate and refresh evidence by actual inputs. T changes stale all execution,
   fairness/alignment and affected semantic judgments; S changes stale reference and
   S-relative variants, SQ and broad reviews; L/B/E changes stale runtime proof and
   applicable semantic scope; D changes rederive all meaning and fresh solve evidence.
   Include fixtures, expected IDs, selectors and tool sources. Unrestricted reviews
   depend on everything they could read. Refresh final stability if its inputs changed.
6. Close affected G1 -> G2 -> G3 -> G4 on exact repaired bytes with deterministic evidence now: the fast check
   (`tools/fastcheck.sh`: cells, two-user replay, kept wrong versions, lint), the variant corpus, the finding's own
   kept wrong version or executed input (fails on the wrong design, passes on the reference) and the linters.
   Semantic records that step 5 marks stale are refreshed at the next point of PIPELINE.md "Review schedule", never
   by a review round started for this fix. Required independent samples have different IDs even on identical
   inputs; do not reuse one as another. No open/stale required record at hand-over. If repair cannot satisfy locked meaning,
   report the concrete blocker and the smallest redesign that clears it; do not loop paid checks.
   Never propose retiring a task: the flow ends only with an accepted task (owner rule).

## Rollout closure and small tools

Use current, complete, unhinted, eligible platform runs and their actual task family
(not the evaluator's family). Keep scratched/stale/incomplete/contaminated attempts
visible but outside the eligible denominator per current platform policy. Re-evaluating
one trajectory never increases N. The criteria (platform.md, 2026-11-21): N >= 4 per family; Orion
`1 <= passed <= N/4`; Vega `passed <= N/4`; Nova `passed = 0`; the passing Orion runs average >= 256K tokens of
sequence length; no unfair/broken flag, cheat rate < 20%, no environment blocker. Resolve FP and
environment/fairness caveats before claiming the criteria. Historical/local rates, a local replay of a platform run
and an unchanged patch replay after new wording cannot certify them (`tools/rollout_report.py` prints the table
from the platform's own run data).

Tools (Python standard library + Git for package diff syntax; no Docker/model/network):

```text
python scripts/certify.py package <package-dir>
python scripts/certify.py fingerprint <file> ... [--metadata <identity.json>]
python scripts/certify.py junit <report.xml> --ids <ids.json> --expect pass|fail --exit-code <n> [--allow-skips <ids.json>]
python -B -m unittest discover -s scripts -p test_certify.py
```

IDs files are nonempty JSON string arrays using H1's canonical names. The optional
skip list is only for documented baseline skips. Package checks validate syntax,
basic modes and file separation; they do not apply patches or judge content.
Fingerprints hash raw bytes, tool version and supplied metadata; the caller must
supply the complete read-set. JUnit checking detects structural/status contradictions;
it cannot know whether diagnostics are genuine or failures were intended. Language
adapter, battery runner, cache scheduler and review launcher remain task-specific
implementations to qualify with H6, not fictitious implemented commands.
