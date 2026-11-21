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
   neutralized without erasing its production change. Pin every test-only helper
   package of a base-mode package (a non-test package that only test files import: a
   candidate could weaken upstream tests by editing it; vet 6: graphtest was missed
   while three siblings were pinned). Restore with `tar -x --no-overwrite-dir` and
   leave restored files writable: the platform applies the solution as uid 1000 after
   root ran the baseline (vet 6: "unable to unlink ... Permission denied").
3. **H3 - Implement two modes.** Support `./test.sh [--output_path <file>] [--mode] <base|new>`
   in any order: the output path is optional (write a scratch JUnit file and print its
   path when absent), the mode defaults to base, malformed/unknown arguments exit 2.
   The platform's Harbor oracle calls it both ways and parses text output: print the
   runner's normal text (`--- PASS:` / `--- FAIL:` lines for Go) and keep the JUnit
   result (every oracle-passing package did; the raw `go test -json` stream failed it
   three times). Resolve relative output paths against the caller's cwd before changing
   directories. Base runs upstream regressions for affected code and callers: every
   package with tests that imports changed code is in base mode or listed with a
   reason; base mode runs only tests the pinned commit has (an acceptance or data-driven
   runner is filtered by the pinned file list, so a script the reference adds never
   shows up as an extra test after the apply); new runs only feature cases. No
   fail-fast. Any deselection names an exact ID, reason, base evidence and replacement
   behavior check: tests that skip when run as root, and tests with an upper wall-clock
   bound (`assert.Less(t, time.Since(...))`, elapsed comparisons, short timeouts;
   measure each 30 times on the clean repository, vet 6: 4-5 of 30 over the bound on a
   quiet machine) go on the skip allowlist with their reason, because the platform
   runs the suite about 12 times for flakiness. A true compatibility regression is
   never deselected.
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
   mode is <300s (one solo run under 6 minutes), with the actual platform limit
   recorded. Run the platform's two-user order too (`proof.py --root-base --two-user
   --plain-new`, or `tools/fastcheck.sh` before a paste): root runs base mode in the
   image's own /app, then uid 1000 applies solution.patch and runs new and base, and
   `tools/junit_sets.py` must find the five verifySolution sets empty (baseline failures,
   new not passing, new also in baseline, after extras not skipped, pass-to-pass not
   passing after); `test.sh new` with no --output_path must exit 0. Commit test.sh as 100755. The
   platform-accepted runners in templates/examples/ are the proven shape; the generated
   adapter is the fallback (templates/go/README.md).

## Pre-submit self-check, in priority order

| Gate | Evidence required |
|---|---|
| Auto Review T1/T2/T6/T8 | Base/base PASS; new/base each intended FAIL; base/reference PASS; new/reference PASS. Exact IDs/status vectors, preserved diagnostics, executed failure probes, offline unknown-uid/read-only-source proof, stable repeats. |
| False pass | Test/config tampering cannot bypass grading; loaded source/binary is the candidate; no missing/zero IDs accepted; no restored-away probe counted as executed. |
| Solution Quality | Native affected regressions pass; all promised modes and compiled twins actually execute. |
| Task Quality T5/T7 | Base exclusions are exact and justified; alternate correct designs work with pristine tests; harness does not impose implementation order or machine-specific performance. |

The repository adapter implements these steps. `scripts/certify.py junit` checks
report structure/status, not execution provenance or intended failure causes.

Before every paste run `tools/tests_lint.py <pkg> <base checkout>` and `tools/precheck.py <pkg>`: G1 every test-only
helper package of a base-mode package is pinned; G2 every package with tests that is changed or imports changed code
is in base mode or has a `# base skip: <dir> <reason>` line; W1 lists the wall-clock-bounded, root-skipping and
user.Current() tests as skip-allowlist candidates to measure 30 times on the clean repository (the platform runs base
mode about 12 times, as root and as uid 1000); precheck fails a process word (grading, hidden paths, solver) in
test.sh with its line, and a flagged word in the task, package or hidden test file names.

Adapter facts (tools/repo_init.py, repo_check.py): `repo_init.py URL COMMIT TASK` puts TASK under the machine profile's
paths.tasks_root (a path only when it holds a separator or is absolute); a name holding a check_codex_brief.sh word is
refused; init/Dockerfile and init/test.sh that differ from the last render are kept (`--render-only --force` rewrites
them). A tracked file matching a build-output pattern (*.o, *.a, build/, dist/ ...) is listed in the profile's
`keep_tracked` and kept in the candidate copy. A Go package imported only by test code outside its own directory is a
helper pinned through restore_paths (profile evidence `helper_roles`). expected.new fills new_native_ids for Go
(ImportPath::Test) and Python (node id); any other case stays OPEN until --settings supplies the map. repo_check's
`open-build-inputs` step stops before Docker while a placeholder, NOT_VERIFIED or an unverified go_sha256 remains, and
qualifies the adapter with `proof.py --base-only`.
