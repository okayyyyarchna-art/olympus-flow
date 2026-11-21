# Replica checks: shared rules (read this first)

You reproduce one quality check of a task-grading site. A task is a pinned public repository plus four files:
- `description.md` (or `task.md`): the only text a solving agent reads.
- `test.patch`: hidden tests and `test.sh` (two modes: `base` runs existing repository tests, `new` runs the added tests).
- `solution.patch`: the reference solution.
- `Dockerfile`: the offline image.

Task folder layout (paths are given in the brief):
- `<task>/description.md` or `<task>/task.md`, `<task>/test.patch`, `<task>/solution.patch`, `<task>/Dockerfile`
- `<task>/repo/`: the repository at the pinned commit WITH both patches applied (read code here).
- `<task>/runs/` (optional): agent runs, one folder per run with `verdict.txt` and `solution.patch`.
- `<task>/eval/replica/`: earlier replica outputs (other checks), when the brief names them.

Network checks use a generic User-Agent; never put the operator's email or name in any request.

Evidence rules (the site works this way; do the same):
1. Every finding quotes its evidence exactly: a description sentence, a test line with its test name, or a repository
   line with `path:line`. No quote, no finding.
2. Every finding names a concrete failing case: inputs, steps, the wrong result, and the right result.
3. Before keeping a finding, write its strongest disproof (the best argument that it is not a real problem) and check
   it against the code. Keep the finding only if the disproof fails. Report the disproof you tried.
4. Read the real code path end to end (callers, every enabled driver/backend/mode, compiled twins, lifecycle start
   and stop). Do not judge from the diff alone.
5. No network calls and no image builds. Where your check file says to execute (the fairness check's wrong solutions,
   the solution-quality check's break attempts), run the task's existing image through the launcher's dockrun.py
   command, one container at a time, inside your time box; small read-only scripts (grep, Python one-liners) are
   always fine. A static trace is a hypothesis, not a result.
6. Judge only what the description states or what an expert can discover from the repository. Behaviour the
   description leaves open is never a defect of the tests and never required of the solution.

Output: write ONE JSON file at the path the brief gives, exactly in the schema of your check file, then return a short
Markdown summary (verdict line first, then each finding in one line). Never edit any task file.
