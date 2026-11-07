# Build task 5: make the skill-next tools enforce what the cards say

Work only inside C:/Users/ASUS/OSS/olympus-product/skill-next/tools/ and skill-next/scripts/ (git repo; one commit
per fix with `git -c user.name=olympus -c user.email=olympus@local commit`). The review that found these is
C:/Users/ASUS/OSS/olympus-product/REVIEW-4-report.md (findings F3, F5, F6, F7, F8, and F4's input validation). Read it
first, then skill-next/harness.md, gates.md and PIPELINE.md, which are the contract the tools must follow.

## Fixes
1. **F3 precheck.py:** a description of 250 or more site words FAILs (site split on whitespace, "-" and "/", the same
   counting as description.md). Keep the platform ceiling as a separate check. Add tests for 249 / 250 / 251.
2. **F5 sweep.sh and round.sh:** add a per-lane mode (one lane or one check per invocation, blocking until it ends,
   writing its own report) so the coordinator starts each lane as its own tracked job. Keep the aggregate mode only as a
   documented convenience that waits for every child and exits non-zero if any child failed or wrote no report. No
   detached or unwaited background children anywhere (also the repository-search launcher).
3. **F6 cleanup and capacity:** proof.py (and any tool) runs Docker cleanup only when the machine profile's
   docker.cleanup_allowed is true. dockrun.py and round.sh: an environment override may LOWER the profile's slot limit,
   never raise it. Remove fixed machine-limit claims from comments.
4. **F7 proof.py:** parse JUnit with scripts/certify.py's strict reconciliation for every cell (duplicate, missing,
   unexpected ids and new-mode skips fail; process exit status and report must agree). Expected ids come from a file the
   caller passes (base and new). Run the unknown-uid cell in the literal harness.md H4 environment: cwd /, read-only
   /app, cleared environment, HOME unset, only the platform's minimal PATH, writable output dir. Key image reuse by
   Dockerfile + build context identity (base commit tree) + resolved base image digest + platform.
5. **F8 summarize.py / round gate:** each checkpoint declares its required reports (fairness, sq samples, dq, ar,
   verify); a missing, empty or malformed report FAILs the gate; an unresolved in-scope finding FAILs the gate; SQ
   findings are merged as a union with their source ids instead of picking the larger report.
6. **F4 input validation:** replica.sh, sweep.sh and round.sh check that every prompt / knowledge file they need exists
   (skill-next/replicas/ now holds them) before starting, and fail with the missing path.

## Proof of each fix
For every fix add an offline unit or integration test (mock Docker and model calls; no real container, platform call
or paid job), and run: `python -B -m unittest discover -s skill-next/scripts -p "test_*.py"`, the new tests, `bash -n`
on every .sh, `python -m py_compile` on every .py. Keep the tools' existing style and sparse comments. Write
BUILD-5-report.md in the repo root: per fix the change, the test that proves it, and the command output.
