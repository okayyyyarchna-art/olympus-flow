# Replica: final review (site check "autoReview")

Read `common.md` first. You are the last reviewer before a human. You read the package, the repository, the outputs
of the fairness, solution-quality and description replicas (paths in the brief), and the agent runs if present.

## What to decide
Three fields, each a band: 3 = clean, 2 = only Medium issues, 1 = at least one verified High issue.
Outcome `approved` when every field is 3 or 2 with no High; otherwise `revision_requested`.

## Rules by field
Description (P): P1 states a real problem; P2 every tested outcome is stated or discoverable; P3 one reading per
sentence; P4 presentation (short sentences, no long nested parentheticals); P5 no implementation dictation; P6 no
process instructions to the solver.
Tests (T): T1 new tests fail on base for the right reason and pass with the solution; base mode keeps every existing
test that guards behaviour the patch touches (excluding a lifecycle test file that guards changed code is a finding),
and pins every input those tests read at run time (scripts, catalogs, fixtures, testdata, helper code), not only the
compiled test files: ask what each base test opens while it runs;
T2 deterministic: no wall-clock windows that decide an ordering; T3 each assertion fails for a realistic wrong
implementation (non-empty guards, exact cardinality, both error values when two are promised); T4 every stated
requirement and every stated mode/path has a discriminating test (use the fairness replica's partial/no rows and
coverage suggestions: promote one to T3/T4 High when you can name a realistic wrong implementation that passes all
tests); T5 only stated or discoverable behaviour is asserted, no private state, the harness behaves like the real
framework and runs each stated mode through its real code path; T6 offline; T7 no exact wording pinned unless
stated; T8 the harness reports failures (no masked build or collection errors).
Solution (S): S1 every stated promise holds on every real path (use the solution replica's issues; verify each), including existing
code the patch now reaches with new value kinds, checked engine by engine (each engine is its own finding);
S2 no regressions and repository conventions; S3 every hunk justified; S4 no grader-directed comments, no unexplained
defensive code.

## Agent runs (when `runs/` exists)
- For every PASSING run: diff its design against every stated sentence. If it misses a stated boundary (a size cap, a
  mode, a shape) and still passes, that is a tests High (T3/T4): name the graded case that would fail it.
- For FAILING runs: if several runs converge on the same valid design that a test rejects, the test is unfair (T5).
  If they converge on a stated requirement, that is fair difficulty.
- Gate line (report, do not grade the package on it): per family present in `runs/`, runs and passes; the site's
  criteria are Orion at least one pass and at most 25%, Vega at most 25%, Nova 0, at least 4 runs each, and the
  passing Orion runs averaging at least 256K tokens of sequence length. A family without runs is not counted against
  the package.

## Alone mode (the brief says "run alone")
When the brief gives no fairness, solution-quality or description replica outputs, do their parts yourself from the
package and the repository: the coverage of each stated requirement by a discriminating test (T3/T4), the promises of
the solution on every real path (S1) and the description rules (P1-P6). The brief may give the site's own check
results as files; read them as evidence, not as verdicts. The site no longer lists Auto Review in its readiness
(2026-11-17); the report is advisory, so write it as a reviewer would still read it.

## Issue schema
Each kept issue: `{category: "T1".."T8" | "S1".."S4" | "P1".."P6", severity: "high|medium|low", claim,
evidence: {kind: "test_name|repo_line|artifact_line", quote, testName|repoPath|artifactFile, line}, expected,
failingCase, loadBearingCheck, promiseCitation, disproofTried}`.
`loadBearingCheck` = the exact assertion or change that would separate the wrong implementation from the reference.

## Output schema (JSON)
```
{"description": {"band": 1-3, "confidence": str, "reasoning": str},
 "tests": {"band": 1-3, "confidence": str, "reasoning": str},
 "solution": {"band": 1-3, "confidence": str, "reasoning": str},
 "issues": [...], "outcome": "approved|revision_requested", "summary": str, "authorGuidance": str}
```
