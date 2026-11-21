# Seam bank (between tasks, in the background)

Stage 0 takes 30 minutes only when ready seams exist. Keep `$OLYMPUS_SEAMS_ROOT/<owner>-<repo>.md` with >= 3 ranked
seams per active repo. Refill it with one Codex lane while a task is in stages 2-6 (no conflict: it only reads a
separate clone).

## Seam entry (fixed schema)
```
## <seam title in user words>
- kind: bugfix | feature_request; repo tip: <sha>
- files (3-30 production, the value's real path): <paths>
- core outcome: <one sentence>
- boundaries (>= 3, each on a different subsystem pair): <boundary> | <subsystem A x subsystem B> | <testable how>
- OUT shapes (scope line candidates): <list>, base behaviour measured: yes/no
- novelty searches: <queries + result counts, issue/PR numbers seen>
- offline test plan: <real objects used, what is faked at the network edge>
- risks: <undiscoverable parts, timing needs, broad lifecycle contract, open input space without a boundary>
- depth: <file:line trace a solver must follow; why the symptom site and the nearest helper do not decide it>
- length design (problem-design.md section 2): files to read before the first correct edit <count, packages> |
  files to change <count> | layers crossed <list> | the repository loop that keeps failing <command or file, what it
  shows> | estimate <K tokens: 8K + 20K per code-changing requirement + 18% + 15%>
- test grid (problem-design.md section 7): decision points <count> | universal words x axis members <list> |
  within budget yes/no
- repo hints checked: <TODO / doc / comment / test-name / helper searches and their result>
- fair designs (>= 2): <design A> | <design B>
- upstream pins: <tests with wall-clock bounds or root skips in the touched packages; test-only helper packages;
  packages importing the changed code>
- decisions (difficulty.md section 1): <decision> | nearest helper file:line | right/wrong | kind K1-K7 | fair route | right answer near or far
- calibration reserve (difficulty.md section 6): <input> -> <expected> | grounding | probe
- score: boundaries independent (0-2) + offline real-object testability (0-2) + novelty (0-2) + size 3-30 files (0-2)
  + depth (0-2) + length (0-2: estimate >= 300K with a loop = 2, 250-300K = 1, under 250K = drop)
```

## Lane brief (Codex search mode, neutral wording; check with check_codex_brief.sh)
Give: repo clone path at the tip, the list of built and rejected seams (already_built_locally.md, the platform list
from `olympus problems mine`, seams already in the bank), the schema above, and these selection rules:
1. One clear feature or bug in stateful framework code; the change crosses 3-30 production files along the value's
   real path, about 15-20 of them changed.
2. At least 3 boundaries where the feature meets another subsystem (lifecycle with work in flight, identity vs proxy,
   ownership vs readiness, exact conversions, ordering of effects, scope of failure, memory of past events, a
   mechanism that must agree with an existing one, discoverable repo conventions), each testable offline through real
   objects.
3. No contract over every lifecycle event; no boundary that needs injected timing; every sentence over an open input
   space (links, outputs, "every X the tool knows") has a boundary the repository documents.
4. Novel: no implementation in any PR/issue state, not declined, fits the README.
5. Deep and unhinted: the answer is not visible from the surface (the symptom site, the nearest helper and the files
   the requirement's words grep to do not decide it; the solver traces the value across subsystems first); no TODO,
   comment, doc or README line, issue text, test name or existing helper states or already computes the fix; at least
   two materially different fair designs pass.
6. Long: a solver must read 80+ files across 3+ packages (or trace several large files end to end) before its first
   correct edit, and something it can run in the repository (its tests, a command, a saved file read back) keeps
   failing until the design is right. Give the reading chain as file:line and name that loop.
Output 5-8 seams ranked by score; the coordinator keeps the top 3.

Command: `bash tools/lib/codex_job.sh <bank-work-dir> seams-<repo> <brief.md> medium search`
(GPT Sol 6.1 at medium, the rule for every Codex job that is not a solve).
