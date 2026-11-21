# design: <task name>

## Header (stage 0)
- repo / tip sha:
- seam (one sentence, user words):
- kind: bugfix | feature_request
- novelty searches (query -> result):
- production files expected (3-30, the value's real path; about 15-20 changed):
- depth trace (file:line chain the solver must follow):
- length design: files to read before the first correct edit (count, packages) | files to change | layers crossed |
  the repository loop that keeps failing | estimate (8K + 20K per code-changing requirement + 18% + 15%):
- test-grid budget: decision points | universal words x axis members | within budget:
- repo hints checked (none may state the fix):
- fair designs (>= 2):
- length spike result (stage 2): solve 1 windows/peaks/sequence | solve 2 | mean | compacted both: yes/no

## Inventory (S1.1)
| Shape / mode / driver / kind | IN or OUT | If OUT: base behaviour measured (command + result) | Where stated (setup line / scope sentence) |
|---|---|---|---|

## Requirements (S1.2), <= 8 wanted outcomes
| # | Kind (core / boundary / scope) | Sentence (as it will read) | Subsystem pair (boundary only) |
|---|---|---|---|

Boundary independence check: no two boundaries on the same subsystem pair or the same blind spot (situations P-5).
Expected per-family pass ~ p^k with k = number of boundaries (problem-design.md section 2): k = , estimate = .

## Variant table (S1.3)
| # | Shapes a user can hit | TESTED / EXCLUDED / TWO-READINGS | Planned test (name_<hash>) | Wrong design it catches | Valid alternative it accepts | Discoverable? |
|---|---|---|---|---|---|---|

## Outcome-word check (S1.4)
| # | Words an agent could satisfy while missing the intent | Fix |
|---|---|---|

## Wrong / valid variants for the batteries (S4)
- wrong-<id>.patch: <design> -> must fail <test>
- valid-<id>.patch: <design> -> must pass all
