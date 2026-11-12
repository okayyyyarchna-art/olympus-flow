# Seam bank (between tasks, in the background)

Stage 0 takes 15 minutes only when ready seams exist. Keep `$OLYMPUS_SEAMS_ROOT/<owner>-<repo>.md` with >= 3 ranked seams per
active repo. Refill it with one Codex lane while a task is in S2-S6 (no conflict: it only reads a separate clone).

## Seam entry (fixed schema)
```
## <seam title in user words>
- kind: bugfix | feature_request; repo tip: <sha>
- files (2-4 production): <paths>
- core outcome: <one sentence>
- boundaries (>= 4, each on a different subsystem pair): <boundary> | <subsystem A x subsystem B> | <testable how>
- OUT shapes (scope line candidates): <list>, base behaviour measured: yes/no
- novelty searches: <queries + result counts, issue/PR numbers seen>
- offline test plan: <real objects used, what is faked at the network edge>
- risks: <undiscoverable parts, timing needs, broad lifecycle contract>
- decisions (difficulty.md section 1): <decision> | nearest helper file:line | right/wrong | kind K1-K6 | fair route | right answer near or far
- calibration reserve (difficulty.md section 5): <input> -> <expected> | grounding | probe
- score: boundaries independent (0-2) + offline real-object testability (0-2) + novelty (0-2) + size 2-4 files (0-2)
```

## Lane brief (Codex search mode, neutral wording; check with check_codex_brief.sh)
Give: repo clone path at the tip, the list of built and rejected seams (already_built_locally.md, the platform list
from `olympus problems mine`, seams already in the bank), the schema above, and these selection rules:
1. One clear feature or bug in stateful framework code; the change crosses 2-4 production files.
2. At least 4 boundaries where the feature meets another subsystem (lifecycle with work in flight, identity vs proxy,
   ownership vs readiness, exact conversions, ordering of effects, scope of failure, memory of past events,
   discoverable repo conventions), each testable offline through real objects.
3. No contract over every lifecycle event; no boundary that needs injected timing.
4. Novel: no implementation in any PR/issue state, not declined, fits the README.
Output 5-8 seams ranked by score; the coordinator keeps the top 3.

Command: `bash tools/lib/codex_job.sh <bank-work-dir> seams-<repo> <brief.md> high search`
(no CODEX_MODEL: config default gpt-6.1-sol, which is also the Orion model).
