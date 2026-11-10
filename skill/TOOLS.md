# Tools

| Tool | State | Purpose |
|---|---|---|
| tools/machine.py, machine.sh | built (task 1) | machine profile loader; every tool reads limits and paths from it |
| tools/precheck.py | built | platform precheck replica (description, patches, Dockerfile rules) |
| tools/tests_lint.py | built | test.patch structural checks |
| tools/checklist_gate.py | built | one sheet row per checklist rule; fails on blank rows, vague locations and unclosed Blueprint cells (prompts/apply-build-checklist.md) |
| tools/proof.py | built | four cells, uid/env -i, stability; image built once per identity; `--build-only` needs only the Dockerfile; `--tamper PATH` overwrites a pinned input in the reference tree and base mode must not change |
| tools/replica.sh, round.sh, sweep.sh | built | model review lanes (one tracked call per lane is the target) |
| tools/watch.sh, pull.sh | built | read-only platform watcher and pull; pull keys run folders by run id and saves verdict.txt (label, batch), output.json (agentBlameUnfair), evalResult.json and testlog.txt, puts Go/testscript failure lines first, flags FP panel notes that only the web UI shows |
| tools/lib/replay_plan.py | built | delta replay plan after a test change: SKIP / LINE? / REPLAY per run, stages only REPLAY patches |
| tools/lib/dockrun.py | built | one machine-wide slot lock (~/.olympus/docker.lock, shared with the task tools); refuses build/pull under the profile's docker.min_free_gb |
| tools/lib/codex_job.sh | built | Codex jobs with a time box (CODEX_TIME_BOX_MIN, default 120) and a Docker budget in the prompt |
| scripts/certify.py | built | package structure, fingerprints, strict JUnit reconciliation |
| tools/repo_init.py + templates/<language> | built (task 2) | pin/clone clean base; manifest/CI file:line discovery, adapter profile/open decisions, parameterized Go/Python/TypeScript templates; unsupported adapters remain OPEN |
| tools/repo_check.py | built (task 2) | proof.py --build-only with cleanup disabled; one-slot Docker lock, native IDs, offline base, one ID, tamper/production failure and H6 report probes; Go qualified, Python final replay blocked by image loss, TypeScript UNPROVEN; evidence: BUILD-2-report.md in the product repo |
| corpus runner | next | apply each variant / platform patch, per-id vectors, execution states |
| evidence manifest + FP barrier | next | hash-keyed results; block hand-over on a missing replay or audit |
| per-lane launch + shared probe queue | next | each lane notifies on its own; one queue for container experiments |
| tools/lib/repo_traits.sh | built | Go repository host score (packages, LOC, unimplemented interfaces); hunt.md part A |
| tools/hunt.sh | built | stage 0 part B: facts, clone, shared brief, Codex + claude2 lanes |

Scripted edits on Windows keep LF: `open(p, 'w', encoding='utf-8', newline='')`, then check with `file <path>`.
Never put a brief at `eval/codex/<job>.md`: that is the job's report path.
