# Construct test.patch: hidden tests and fixtures

1. **T1 - Start from the ledger, before the reference.** For each obligation record
   assertion locations, observable effects and public derivation. Inventory actual
   entry points, live/saved forms, optional legacy metadata, modes, sibling/fast paths,
   transitions and faults. Partition them by materially different behavior; explain
   grouping. Avoid an unbounded Cartesian product, but do not dismiss a concrete
   in-scope interaction because it is rare. Context-only text needs no artificial test.
2. **T2 - Choose separating fixtures.** For each distinct plausible wrong rule, plan
   the smallest counterexample: zero/one/many, two items in the same scope, shared
   labels with distinct identities, both precedence orders, equality and neighboring
   representable values, prerequisite without decisive event, partial/empty input.
   Pair exemption and eligible cases; pair stale removal with new results of each
   promised kind and unrelated sentinels. A new preservation check must share a
   relevant feature case that fails on base; legacy-only regressions belong in base.
3. **T3 - Assert the full observable contract.** Derive the oracle from fixture data,
   an independent specification or trusted repository convention. Check the scenario
   actually occurred: nonempty results, exact identities/cardinality, both errors if
   both are promised, and the underlying state change as well as its message. Allow
   permitted winners/extra metadata; reject prohibited duplicates or stale effects.
   Pin wording/order/format only with public grounding. Reference-only docs do not count.
4. **T4 - Exercise real execution.** Use public entry points and repository framework
   objects; stub external boundaries. For each fake list capabilities a valid design
   may use. Generate saved fixtures via real writers, or demonstrate equivalence to
   supported formats. Save/reload through real readers, including supported older
   shapes. Start and finish every lifecycle. Keep the feature layer and all promised
   modes real; a replacement of that layer cannot prove it works.
5. **T5 - Control time and faults.** For temporal promises assert both the forbidden
   intermediate state and required eventual state. Keep observers active through
   transitions; use barriers or the clock production reads. Exercise too-early,
   too-late/never and plausible finite-cap designs. Permit delayed correct designs
   and every allowed event winner. A bounded watchdog detects hangs; elapsed wall
   time is not evidence of order or an unstated product latency guarantee. On
   rejection, inspect every promised side effect and resource cleanup at its sink.
   Put a controlled-clock jump before every "not yet" and "still one copy" check. A jump also expires the harness's
   own timers, so a harness wait that can span one counts real time (faust task 8: a valid design failed on the
   harness TimeoutError). Run caps and delays on both sides of every boundary.
6. **T6 - Export and demonstrate discrimination.** Name new test/fixture files with a
   collision-resistant suffix, retaining framework discovery. Export explicit paths
   with the harness; inspect removals, modes and accidental files. Keep added test
   code/comments and filenames free of platform, solver and grading-process leaks
   (including task-branded challenge/quest/olympus names); inspect matches in context.
   Follow current patch-encoding rules without changing tested Unicode semantics.
   Through test.sh,
   prove base fails each new ID for its intended missing behavior and reference
   passes it. Execute each planned wrong-rule variant and every available materially
   different valid alternative that challenges a pin, always at least one besides the reference (owner
   2026-11-15). No numerical mutant quota:
   class coverage and observed discriminators are the gate. A build/apply error,
   erased mutation or unrelated timeout is not a caught wrong implementation.

## Pre-submit self-check, in priority order

| Gate | Evidence required |
|---|---|
| Auto Review T1-T8 | Per-ID base/reference differential (T1); controlled timing/order/data (T2); meaningful counterexamples (T3); obligation/path map (T4); public grounding and capable fakes (T5); offline runs (T6); contract-relative output pins (T7); intact diagnostics (T8). Run harness.md too. |
| False pass | No unexplained wrong rule that still passes; every available clean solver patch replayed; both auditors' grounded passer findings closed. Every reference fix inside a promise has a corresponding test. |
| Solution Quality | Tests cover every promised path/fault and reveal genuine regressions; their oracle is independent of the reference's algorithm. |
| Task Quality | Each test has a fairness verdict with grounding, each obligation has coverage, valid alternatives pass both modes. Missing coverage is OPEN, not a reserve waiver. |

When a valid alternative fails, repair the assertion/fake or the obsolete regression
pin with a documented replacement. When a wrong design passes, add the smallest fair
discriminator. Both changes must go through gates.md Repair before claiming closure.

## Hard rules for every hidden test (owner 2026-11-20, from vet task 6)

1. **Fair.** Every assertion passes the one-sentence test: "a correct implementation that satisfies every sentence
   could still do X, and X fails this". Admit every reading the description allows. Never pin a value that common
   readers of the format do not tell apart (JSON integers above 2^53), a field the description does not name, a
   behaviour only because a solution review asked for it, or a count that a design walking a checkout of the base
   would double (count only what only the head has).
2. **Aligned with the prompt, both ways.** Each test names, in its comment, the description sentence it checks or the
   existing repository behaviour at a touched site that the change must keep (file:line). Each description sentence,
   split on its triggers (every / any / each, lists, "X or Y", "added or modified"), has tests. Nothing the
   description excludes is tested.
3. **Behavioural.** Assert what running the product produces: findings and their change labels, records, report and
   saved-report contents, diagnostics a user sees, exit status. Where the repository has an ordinary path that must
   agree, compare with it (the full scan of the same tree, the base code on the old input, the live scan against the
   reloaded report) rather than with a typed literal.
4. **No API-based tests.** No call into an unexported function or method; no hand-built internal state that a real
   run never produces (vet 6: reachOf on a removed record marked local, a platform note); no exported name, field or
   type that only the reference adds (the test file compiles on base and with any fair solution); no fake whose
   signature constrains the design beyond the repository's existing interfaces.
5. **Public behaviour only.** Enter through the public entry points (the CLI command, the engine's public run
   options, the report readers) and check only what a user of the tool can observe.

Hygiene the platform enforced on vet task 6:
- T1 is per leaf. Per-case subtests, or deleting one assertion, can leave a leaf that passes on the clean base. Re-run
  the base check after every test edit; loop axis members inside one leaf.
- No skip in a new test. For a user-dependent input (chmod), compare with an oracle (as root both sides are 0, as uid
  1000 both are N) and guard the presence check with `os.Geteuid() != 0`.
- OS limits only where the OS has them: Linux follows 40 links and has PATH_MAX 4096, macOS 32 and 1024. Gate such
  cases on `runtime.GOOS`.
- A leaf that holds several scenarios names each scenario in its assertion messages; split it only when every part
  still fails on base.
- Existing behaviour at each touched site (counts, diagnostics, recorded fields) has a keeping test.
- Every gap has a kept scripted wrong version (eval/wrong/kept/<name>.py with EDITS, KIND wrong | control | held and
  EXPECT leaves; `tools/wrong_versions.py` runs them all; the fast check re-runs them on each final suite). A wrong
  version meant to catch a design that differs in structure from the reference changes the structure too (vet 6: the
  reference with its link limit raised passed, because its base never used the limit; the natural wrong design
  resolves links on its own with no limit), and a control with the same structure and the right decision shows the
  case isolates one decision. For every function that compares or copies a list of fields, one wrong version per
  field, before the first paste.
- Test files inside solution.patch are not graded (test.sh new runs only the hidden files): they are no coverage.
- Before buying Test Quality, walk [tq-once.md](tq-once.md).
