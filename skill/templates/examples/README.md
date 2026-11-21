# Templates

Copy from `accepted/`, or from the newest in-review package that passed every platform check when this file says so below (the platform accepted these packages). `in-review/` holds packages that passed every
check but are still in finalizing review: use them only for a language with no accepted example, and say so in
the ledger. Draft packages are never templates. A package moves from `in-review/` to `accepted/` only when the
owner says so.

For Go, copy `test.sh.go-vet-pr-accuracy`: it is the most complete bash runner (pinned test files through
`go test -overlay`, test-only helper packages in PINNED, BASE_SKIP with reasons, acceptance scripts restored from
the pinned commit) and the bash runner is the proven route for the platform's Harbor oracle; the generated
adapter (`templates/go/test.sh`) is unproven there (BACKLOG #156-#159). Check the copy with
`python -B tools/tests_lint.py pkg base` (G1: every test-only helper pinned; G2: every importer of changed code in
base mode; W1: wall-clock and root-skip candidates).

When copying `Dockerfile.rust-elio`, drop its `cargo test --no-run` step: dockerfile.md E4 now forbids any test runner in
RUN, and the platform has since failed compile-only runs. The Python Dockerfiles predate the platform's FROM rule of
2026-11-13 (`olympus-base-python` is no longer on the allowed list): copy them with
`FROM public.ecr.aws/d3j8x8q7/olympus-base:latest` and add `chmod -R a+rwX /app` as the last RUN (#142, #156).

| Folder | Language | test.sh / Dockerfile | Source (platform status, results) |
|---|---|---|---|
| accepted | Python (faust) | *.python-faust-table-visibility | table visibility, ACCEPTED (AR 3/3/3, Vega 1/4, Orion 0, Nova 0) |
| accepted | Python (faust) | *.python-faust-eos | EOS offsets, ACCEPTED (Orion 1/4) |
| accepted | Go | *.go-oss-rebuild | oss-rebuild docker proxy, ACCEPTED (AR 3/3/3, Orion 1/8) |
| accepted | Go | *.go-burrow-snapshot | Burrow snapshot, ACCEPTED (older gates) |
| in-review | Go | *.go-vet-pr-accuracy | vet pull-request scan accuracy, passed platform build, verifyTests, verifySolution (Harbor oracle), Test Quality and Solution Quality (2026-11-21); rollout in progress |
| in-review | Python (faust) | *.python-faust-topic-start | topic start, finalizing review |
| in-review | Python | *.python-swift | swift conditional writes, finalizing review |
| in-review | Rust | *.rust-elio | elio folder history, finalizing review (no accepted Rust package yet) |

No accepted TypeScript package exists on this account yet.
Adapt: the new test file list, the base selection (every test file guarding touched code), the base commit, the exact
deselect list with one comment per id. Keep: two modes, scratch copy with base tests restored, fail-safe JUnit, hard
timeout below the platform kill, the call interface `[--output_path F] [--mode] <base|new>` (any order, mode default
base, output path optional, exit 2 on a malformed argument) and `go test -v` text on stdout.
