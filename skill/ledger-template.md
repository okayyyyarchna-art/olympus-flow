# Construction ledger: fill while writing

Keep one ledger; link raw immutable logs/diffs/reports rather than copy their prose.
Replace example rows. PLANNED means designed, not executed. OPEN means required work
remains. NOT VERIFIED means unknown with a named next probe. COVERED requires actual
assertions and current execution evidence; OUT requires an exact exclusion or proof
of unreachability. No untested in-scope row may become OUT or a reserve waiver.

## Identity and current stage

| Field | Value/evidence |
|---|---|
| Task/title/category/language; working/frozen paths | Fill |
| Repository URL; full commit; tree; source cleanliness; submodules/LFS | Fill |
| Platform criteria/version/date; eligibility/novelty evidence | Fill |
| D/T/S/L raw hashes; immutable image ID/base digest/platform | Fill |
| Current stage; DIRTY/LOCAL READY/PLATFORM VERIFIED; blockers | Fill |
| Human description lock + hash; Dockerfile build check ID; Scope Gate | NOT VERIFIED |
| Rollout minimum per family; long-horizon rule; source/date | NOT VERIFIED |
| Docker lock path; configured container limit (machine profile); allowed filesystem paths | Fill |

## Repository adapter profile (cite manifest/CI file:line for each value)

| Item | Discovery and qualified command/location | Evidence |
|---|---|---|
| Toolchain / package manager / locks / build / dependency fetch | Fill | NOT VERIFIED |
| Format / lint / types / normal solver development tools | Fill | NOT VERIFIED |
| Test framework / enumerate IDs / run one / reporter version | Fill | NOT VERIFIED |
| Production paths / upstream tests, fixtures, config / compiled twins | Fill | NOT VERIFIED |
| Pristine restore source / hidden overlay / rebuild and loaded-code identity | Fill | NOT VERIFIED |
| Base selectors / exact deselect or skip IDs / reasons / replacement checks | Fill | NOT VERIFIED |
| New selectors / expected base-ID and new-ID JSON paths | Fill | NOT VERIFIED |
| uid/gid / passwd absence / PATH / HOME / cwd / mounts / network / watchdog | Fill | NOT VERIFIED |

## Difficulty (difficulty.md; fill at stage 0, solver runs after the lock, reserve used at stage 8)

| Decision | Nearest helper (file:line) and what it decides | Right/wrong (separating input) | Kind | Fair route | Stated fix leads to it? |
|---|---|---|---|---|---|
| Fill | | | | | |

Inventory author (fresh reader): Fill.

| Length (problem-design.md section 2; difficulty.md section 2) | Value/evidence |
|---|---|
| Stage-0 estimate: files to read before the first correct edit (count, packages); files to change; layers crossed; the repository loop that keeps failing; estimate in K | Fill |
| Test-grid budget: decision points; universal words x axis members; within budget | Fill |
| Length spike on the draft (2 Codex GPT Sol 6.1 xhigh solves): windows and peaks, requests, sequence length (platform count: input + output per window peak) per solve; mean (gate >= 300K, none under 250K); separators missed | NOT VERIFIED |
| Deepening applied after a short spike (what layer, which sentence) | none |

Solver runs (difficulty.md section 3): local 3 Opus + 3 GPT, platform 2 Orion + 2 Vega; graded passers, FP audits, keeper: Fill.

| Reserve probe | Input -> expected | Grounding | Probe command | Passers that fail it (stage 8) |
|---|---|---|---|---|
| Fill | | | | |

## Contract and meanings

| ID | Exact public quote + pinned-repo grounding | Atomic effect/condition; allowed readings/results | Outside / preserve / reject distinction | Known separating input; word-reach/reader disposition | Status |
|---|---|---|---|---|---|
| C01 | Fill | Fill | Fill | Fill | PLANNED |

Human rewrite diff: old/new text hashes; every obligation and known separator's
before/after behavior; intended changes; accidental changes; owner resolution.
Mechanical count method/result and actual description/precheck results stay separate.

## Paths, transitions, faults (same inventory for solution and tests)

| ID / contract IDs | Entry/sibling/mode/store/format, public reachability | State/event orders, intermediate + eventual result | Resource owner/invalidation; fault/cleanup | Production location; assertion location; grouping/exclusion rationale | Status |
|---|---|---|---|---|---|
| P01 / C01 | Fill | Fill | Fill | Fill | PLANNED |

## Blueprint (fill before any code; tools/checklist_gate.py checks it)

One row per combination that differs, for every contract row not OUT. Write n/a for an axis that cannot vary.
"Copy or data state" includes live -> saved -> reloaded through the real reader (build-checklist.md section 3
item 2); "Lifecycle edge" includes the repeated trigger. The full round-trip set and the edge-case matrix are
calibration levers (prompts/calibrate-one-passer.md Levers K and L, owner 2026-11-16), not Blueprint cells.
Disposition is one of: `TESTED <test name>`, `OUT "<exact description sentence>"`, `OUT unreachable <file:line>`,
`SAME <cell> <why it behaves the same>`.

| Cell | Contract | Entry point | Change kind or mode | Copy or data state | Lifecycle edge | Expected result | Disposition |
|---|---|---|---|---|---|---|---|
| M01 | C01 | Fill | Fill | Fill | Fill | Fill | Fill |

## Tests, fixtures and design freedom

| Canonical test ID | Contract/path IDs; exact assertions and observable sinks | Oracle derivation; data separating wrong rules | Fake capabilities/fixture provenance; valid design it must permit | Intended base failure; result records |
|---|---|---|---|---|
| Fill | C01/P01 | Fill | Fill | NOT VERIFIED |

## Discriminator corpus (include actual solver patches)

| Variant/run ID; kind (wrong/valid/solver) | Exact diff/hash; base-relative or S-relative | Requirement, legal separator, expected ID/result | Effective postimage/loaded code; APPLIED/RESTORED_AWAY/APPLY_ERROR/EXECUTED | Base/new result + diagnostic/log | Disposition |
|---|---|---|---|---|---|
| V01 | Fill | C01 | NOT VERIFIED | NOT VERIFIED | OPEN |

## Harness failure table and proof cells

| Probe/cell | Injection after restore; expected IDs/diagnostic/exit | Input identity + command | Actual per-ID vector/exit/raw log/report hashes | Disposition |
|---|---|---|---|---|
| base/base; new/base; base/reference; new/reference (separate rows) | Fill | Fill | NOT VERIFIED | OPEN |
| production build; test build; collection; zero selected (separate rows) | Fill | Fill | NOT VERIFIED | OPEN |
| timeout; missing/empty/malformed report; converter failure (separate rows) | Fill | Fill | NOT VERIFIED | OPEN |
| test/config tamper; relative/spaced output; cwd; loaded-source probe | Fill | Fill | NOT VERIFIED | OPEN |
| final six unsolved + six solved new-mode repeats | Same IDs/vectors in each state | Fill | NOT VERIFIED | OPEN |

## Gate evidence and repairs

| Gate/sample ID (G1, G2, G3, G4) | Complete read-set + input hashes; prompt/model/effort/tool identity | Command/report ID; result and contradictory detail fields | Output hashes/current or STALE | Required next action |
|---|---|---|---|---|
| Fill | Fill | NOT VERIFIED | STALE | Fill |

| Finding ID / all sources | Quoted obligation; legal failing input; expected/actual; reproduction or disproof | Accept/reject/merge/NOT VERIFIED and reason | Changed artifacts; sibling-class fix; new assertion | Repair replay + FP-audit eligibility; affected gate reclosure |
|---|---|---|---|---|
| F01 | Fill | NOT VERIFIED | Fill | OPEN |

Track samples separately: reading A/B; the length spike (2 solves); the stage-7 replica round (fairness, sq, dq,
ar, verify) with its fix batch and the one verification round; the repair loop of each platform finding (kept wrong
version or executed input, class sweep, fast check); FP auditor A (+B on demand) **for each passing run**. A sample
records its own inputs, independence and findings. Identical hashes never turn one sample into two.

## Run pool and hand-over

| Run/trajectory ID | Task family/model; original D/B/E hashes; isolation/completion/eligibility | Current production patch; replay B/T/E; base/new outcomes | Auditor A/B + reference comparison + FP disposition | Counts toward which current family N? |
|---|---|---|---|---|
| Fill | Fill | NOT VERIFIED | NOT VERIFIED | No until qualified |

| Family | Current eligible unique attempts N | Genuine passes | Rate | Criterion (platform.md): Orion 1 <= passes <= N/4 and passing runs average >= 256K; Vega <= N/4; Nova 0; N >= 4 | Passing runs' sequence lengths, compacted | Result |
|---|---|---|---|---|---|---|
| Orion | 0 | 0 | undefined | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Vega | 0 | 0 | undefined | NOT VERIFIED | n/a | NOT VERIFIED |
| Nova | 0 | 0 | undefined | NOT VERIFIED | n/a | NOT VERIFIED |

Hand-over: repo URL/full pin; title/category/language; exact four artifact hashes;
final runtime/stability and G1-G4 evidence; remaining human actions; no open grounded
findings; authorized upload/read-back comparison when available. Record LOCAL READY
separately from platform acceptance. Do not fill unknown results with expected PASS.
