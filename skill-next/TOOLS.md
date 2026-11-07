# Tools

| Tool | State | Purpose |
|---|---|---|
| tools/machine.py, machine.sh | built (task 1) | machine profile loader; every tool reads limits and paths from it |
| tools/precheck.py | built | platform precheck replica (description, patches, Dockerfile rules) |
| tools/tests_lint.py | built | test.patch structural checks |
| tools/proof.py | built | four cells, uid/env -i, stability; image built once per identity |
| tools/replica.sh, round.sh, sweep.sh | built | model review lanes (one tracked call per lane is the target) |
| tools/watch.sh, pull.sh | built | read-only platform watcher and pull |
| scripts/certify.py | built | package structure, fingerprints, strict JUnit reconciliation |
| tools/repo_init.py + templates/<language> | built (task 2) | pin/clone clean base; manifest/CI file:line discovery, adapter profile/open decisions, parameterized Go/Python/TypeScript templates; unsupported adapters remain OPEN |
| tools/repo_check.py | built (task 2) | proof.py --build-only with cleanup disabled; one-slot Docker lock, native IDs, offline base, one ID, tamper/production failure and H6 report probes; Go qualified, Python final replay blocked by image loss, TypeScript UNPROVEN; [evidence](../BUILD-2-report.md) |
| corpus runner | next | apply each variant / platform patch, per-id vectors, execution states |
| evidence manifest + FP barrier | next | hash-keyed results; block hand-over on a missing replay or audit |
| per-lane launch + shared probe queue | next | each lane notifies on its own; one queue for container experiments |
