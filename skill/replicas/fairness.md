# Replica: test fairness and requirement coverage (site check "verifyFairness")

Read `common.md` first.

## Step 1: requirements
Extract every requirement the description states, one per distinct outcome. Scope, exclusion and "keeps today's
behaviour" sentences ARE requirements (the site lists them, e.g. "X is outside the feature", "works with
at-least-once delivery"). Keep the exact `sourceQuote`.

## Step 2: tests
For every test function in test.patch (parametrized cases count under their function), record:
- `verifies`: the observable outcome it asserts, concretely.
- `fairness`: one of `Prompt-stated` (the description states it), `Repo-discoverable` (an expert finds it in the
  repository: existing behaviour, conventions, docstrings), `Standard external semantics` (a well-known protocol or
  library rule), or `Unfair` (none of these: an unstated rule, exact wording, private state, a harness mechanism, a
  timing the description does not give, a behaviour the description leaves open).
- `concerns`: any of `internal_coupling` (asserts private fields, call order of internals, mock call targets),
  `timing_sensitivity` (wall-clock windows, sleeps deciding the outcome), `overfit_single_point` (one example where
  the requirement is general), `vacuous_assertion` (can pass with nothing checked, e.g. `all([])`),
  `harness_unrealistic` (the harness produces events the real framework cannot, or skips a real layer of a stated
  mode).
- `evidence`: why that fairness label holds (quote the sentence or repo line).
- `qualityCheck`: one or two sentences as the site writes them: what the test covers well and what it does NOT
  assert ("It checks X but not Y"). Every "but not" feeds Step 3.

## Step 3: coverage (calibrated 2026-11-10: the site marked vet 2 6/6 and vet 3 3/6 `partial`)
The site maps each requirement to tests by name and by a discriminating assertion inside. Every scope word of the
description ("all packages", "any manifest", "both APIs", "several rebalances") applies to every requirement row: a
row is `yes` only when its tests visibly run across the full named scope (a loop or matrix over every category the
repo supports through the feature: each ecosystem, format, package kind, mode). It marks `partial` when:
- a named route/setup/state is not exercised, or one representative case stands for a general rule (vet 2: "the
  current acceptance suite uses Cargo, npm, PyPI" for "any manifest"; vet 3: "a sample of package types");
- a check is conditional (`if status == X: assert ...`) with no unconditional bound;
- a test asserts a count but not the content (message, component, value) of what it counts, or uses stand-in
  diagnostics and never the production text (vet 3: "checks count, not its message");
- a test's name states an outcome no assertion checks (vet 3: "...AndAddsTheNewOne" never asserted the new one);
- an intermediate state the requirement covers is reached but not inspected (vet 3: "checks two package statuses
  but not the details of partial analysis data").
For each requirement:
- `yes`: tests assert its main observable outcome by value across the full named scope, so the implementation a
  competent engineer would most plausibly get wrong fails at least one test, and none of the `partial` causes above
  applies.
- `partial`: you can name ONE plausible wrong implementation (a design an engineer or coding agent would actually
  write while trying to meet the description, not a contrived special case) that passes every test.
- `no`: no test touches it. A scope or "keeps today's behaviour" requirement is `yes` when some test asserts today's
  behaviour for an excluded case, otherwise `no`.
Concerns are equally strict: `timing_sensitivity` only when a CORRECT implementation can fail or pass depending on
scheduling or wall-clock time (deterministic waits on events are fine); `internal_coupling` only when a correct
implementation that is built differently inside fails.

## Step 4: coverage suggestions (at most 5, most important first)
For each `partial`/`no` requirement write one suggestion:
`{area, gapKind: untested | not_discriminating | single_point, requirement, sourceIfAdded: Prompt-stated |
Repo-discoverable | Would need prompt edit, suggestion, wrongImplementationThatPasses}`.
Before deciding `yes`, consider these sweeps, and flag only gaps a plausible implementation would fall into:
- every enabled mode/driver/backend/store/table kind the sentence covers;
- two-sided boundaries (too early, exactly at, too late/never; just below, at, just above);
- multiplicity and topology (one vs many readers/workers/partitions/items; same resource shared by several users);
- lifecycle states (before start, during rebalance/restart/stop, after stop; in-flight work);
- failure paths (rejected, refused, timed out) for each success path;
- value shapes (empty, falsy, null, non-text bytes, large) where the sentence covers them.

## Output schema (JSON)
```
{"taskSummary": str,
 "requirements": [{"requirement": str, "sourceQuote": str, "covered": "yes|partial|no", "coveringTests": [str]}],
 "tests": [{"name": str, "verifies": str, "fairness": str, "concerns": [str], "evidence": str,
            "qualityCheck": str}],
 "unfairTestCount": int,
 "coverageSuggestions": [{"area": str, "gapKind": str, "requirement": str, "sourceIfAdded": str, "suggestion": str,
                          "wrongImplementationThatPasses": str}],
 "verdict": "PASS|FAIL", "overall": str}
```
verdict FAIL only when at least one test is `Unfair`.
