# Construct test.sh and qualify its adapter

1. **H1 - Discover the repository interface.** Record toolchain/build/test/format/lint
   commands from manifests and CI with file:line evidence. Find test enumeration,
   single-ID execution and JUnit support, including reporter versions. Inventory test
   helpers/configuration separately from production files. Define stable canonical
   IDs as `classname::name` (or just name when classname is absent). Qualify dynamic
   subtests or enumerate them before compilation; names must survive missing-feature
   builds. Do not assume a Python, Go, Rust or Node convention in a generic runner.
2. **H2 - Establish source authority.** Copy current candidate production into unique
   writable scratch. Restore selected upstream tests, helpers and grading configuration
   from the exact base commit or verified immutable archive, then overlay the author's
   hidden tests/intentional test edits. Never restore candidate production. Remove
   stale generated binaries/import shadows and rebuild from candidate source, including
   compiled twins. If pristine tests cannot be obtained, fail; no warning-and-continue
   fallback or runtime network fetch. Prove a simulated solver test/config edit is
   neutralized without erasing its production change.
3. **H3 - Implement two modes.** Support `./test.sh --output_path <file> base|new`
   and the option after the mode; reject malformed/unknown arguments nonzero. Resolve
   relative output paths against the caller's cwd before changing directories. Base
   runs upstream regressions for affected code and callers; new runs only feature
   cases. No fail-fast. Any deselection names an exact ID, reason, base evidence and
   replacement behavior check. A true compatibility regression is never deselected.
4. **H4 - Own the environment.** Locate source relative to the runner; work from cwd
   `/`, offline, with an arbitrary uid absent from passwd, cleared environment/HOME,
   read-only `/app`, writable scratch/output, and the platform's minimal PATH. Set
   toolchain locations and writable HOME/cache/temp paths inside test.sh. Read shared
   dependencies from uid-readable locations; copy mutable caches when necessary.
   The outer probe must not restore image ENV to conceal a runner dependency. Record
   architecture, flags, network policy and watchdog below the platform kill limit.
5. **H5 - Preserve every result.** Predeclare nonempty expected ID sets per mode from
   successful discovery and reconcile every report against them. Preserve test,
   pipeline, build, discovery and reporter statuses separately; a successful XML
   converter/cleanup cannot turn failure into success. Keep raw diagnostics in stdout
   and XML (escaped). For a build/setup/collection/timeout failure, mark every affected
   missing ID as an explicit error with the real cause, not a fake assertion result.
   Retain completed IDs and distinguish infrastructure from behavioral failures.
   Missing/empty/malformed XML, duplicate/unexpected/missing IDs, new-mode skips or
   reporter failure must exit nonzero. Base skips need an exact predeclared allowlist
   and reason; they must not erase valid regressions. Avoid a lone catch-all test.
6. **H6 - Probe the runner itself.** Inject production-build failure, test-build
   failure after restoration, collection failure, zero selection, timeout, absent/
   empty/malformed report and converter failure; verify affected IDs, actual diagnostic
   and exit. Verify mutations remain in the effective tree before execution. Check
   relative/absolute/spaced output paths and cwd independence. Run the four proof cells
   in the literal H4 environment and retain timing; historical target for clean new
   mode is <300s, with the actual platform limit recorded. Commit test.sh as 100755.

## Pre-submit self-check, in priority order

| Gate | Evidence required |
|---|---|
| Auto Review T1/T2/T6/T8 | Base/base PASS; new/base each intended FAIL; base/reference PASS; new/reference PASS. Exact IDs/status vectors, preserved diagnostics, executed failure probes, offline unknown-uid/read-only-source proof, stable repeats. |
| False pass | Test/config tampering cannot bypass grading; loaded source/binary is the candidate; no missing/zero IDs accepted; no restored-away probe counted as executed. |
| Solution Quality | Native affected regressions pass; all promised modes and compiled twins actually execute. |
| Task Quality T5/T7 | Base exclusions are exact and justified; alternate correct designs work with pristine tests; harness does not impose implementation order or machine-specific performance. |

The repository adapter implements these steps. `scripts/certify.py junit` checks
report structure/status, not execution provenance or intended failure causes.
