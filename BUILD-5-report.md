Verdict: PASS (offline); created `BUILD-5-report.md`, `skill-next/scripts/test_capacity.py`, `skill-next/scripts/test_launchers.py`, `skill-next/scripts/test_precheck.py`, `skill-next/scripts/test_proof.py`, `skill-next/scripts/test_summarize.py`, `skill-next/tools/lib/inputs.sh`; changed `skill-next/tools/hunt.sh`, `skill-next/tools/lib/claude2_run.sh`, `skill-next/tools/lib/dockrun.py`, `skill-next/tools/lib/replay_patches.sh`, `skill-next/tools/machine.py`, `skill-next/tools/precheck.py`, `skill-next/tools/proof.py`, `skill-next/tools/replica.sh`, `skill-next/tools/round.sh`, `skill-next/tools/summarize.py`, `skill-next/tools/sweep.sh`.

| Fix | Change | Offline proof |
|---|---|---|
| F3 | Reject >=250 site words using whitespace/hyphen/slash splitting; retain a separate 1000-word platform ceiling. | `test_precheck.py`: actual CLI checks for 249/250/251 and the separate ceiling. |
| F4 | Validate every required prompt/catalog before creating outputs or launching jobs. Aggregate preflight validates every selected lane. Missing/empty inputs name their path. | `test_launchers.py`: remove each check's prompt/common/catalog; empty aggregate input; assert no model invocation. |
| F5 | `sweep.sh --lane` and `round.sh --check` execute one blocking job with its own report. Documented aggregate convenience executes serially, waits for every child, and propagates exit/report failures. Hunt also blocks on both children. Claude requires a successful process and fresh report; stale replica results are cleared. | `test_launchers.py`: individual lanes, all-child completion after failure/missing report, real Claude wrapper with a fake executable, and no background launches in sweep/round/hunt. |
| F6 | Cleanup requires literal profile permission; validate its Boolean type. Clamp Docker/review overrides to the profile maximum and reject invalid values. Remove fixed machine-limit comments. | `test_capacity.py`: cleanup permission and slot bounds, mocked dockrun refusing cleanup; `test_launchers.py`: real round capacity calculation with overrides 999/1/-1. |
| F7 | Require caller-provided base/new ID files; use `certify.inspect_junit` for every cell and preserve test exit/log/XML. Prepare patches separately, then run all cells with read-only `/app`, cwd `/`, offline unknown uid absent from passwd, cleared environment, unset HOME, minimal PATH, writable scratch/output. Reuse hashes Dockerfile, commit/tree, resolved FROM digests and platform; builds pin those digests. | `test_proof.py`: duplicates/missing/extra IDs, skips, malformed/empty XML, contradictory process exits, baseline skip allowlist, H4 command/mount/uid checks, digest resolution, every identity dimension, and all 19 main/stability invocations receiving the correct ID sets. |
| F8 | Declare all required checkpoint reports; validate schemas and fail on missing/empty/malformed evidence. Require source-specific dispositions for every finding at every severity; kept or unresolved findings block. Preserve both SQ samples and their finding union/source IDs. Use exact-tag inputs and propagate summary/tee failure. | `test_summarize.py`: clean checkpoint, each report absent/empty/malformed/incomplete, omitted check/reused sample, all severities, kept Medium, unknown disposition, union/source preservation and DQ-only rejection. `test_launchers.py`: real gate failure and complete mocked round success. |

Verification commands and captured output:

```text
python -B -m unittest discover -s skill-next/scripts -p "test_*.py"
......................................
----------------------------------------------------------------------
Ran 38 tests in 22.077s

OK
```

Each new test module was also run individually using
`python -B -m unittest discover -s skill-next/scripts -p <filename>`:

```text
test_precheck.py:  Ran 1 test   OK
test_capacity.py:  Ran 3 tests OK
test_proof.py:     Ran 8 tests OK
test_summarize.py: Ran 7 tests OK
test_launchers.py: Ran 9 tests OK
```

Syntax checks enumerated every `.sh` and `.py` under `skill-next/`, after test scratch copies had finished:

```text
Bash: C:\Program Files\Git\usr\bin\bash.EXE
bash -n: 14 shell files; PASS
python -m py_compile: 16 Python files; PASS
git diff --check: exit 0, no output
```

The first syntax-check attempt resolved bare `bash` to Windows' unavailable WSL launcher. Re-running with the explicit Git Bash executable passed. Python bytecode was redirected into disposable scratch under `skill-next/scripts/` and removed afterward.

Usage examples:

```text
bash skill-next/tools/sweep.sh TASK s1 --lane ref-a
bash skill-next/tools/round.sh TASK r1 --check sq-a
bash skill-next/tools/round.sh TASK r1 --check sq-b
bash skill-next/tools/round.sh TASK r1 --check gate
python skill-next/tools/proof.py BASE PKG --base-ids base-ids.json --new-ids new-ids.json
```

Coordinator jobs schedule each lane/check independently; AR and verify follow their declared prerequisites. A gate requires fairness, both SQ samples, DQ, AR and verify; optional reference audits become required when declared. Aggregate mode is a serial convenience, not the coordinator's lane scheduler.

Six commits cover F3, F4, F5, F6, F7 and F8. No real Docker, platform or paid model jobs ran. Actual container behavior, registry access and model report generation remain NOT VERIFIED. Protected task folders and other builders' files were untouched.
