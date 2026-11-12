# Apply the build checklist rule by rule

Run this before writing any test or reference code (stage 4), on every machine and every task. No condensed plan
replaces it.

Why it exists: on vet task 2 the builder wrote a short plan instead of the ledger tables. v1 failed platform Solution
Quality and needed a full fix batch, with the paths and change kinds the checklist already named.

## Prompt
You are about to build test.patch and solution.patch for <task-dir>. Follow these steps in order.

1. Read all of build-checklist.md now, top to bottom. Do not work from memory or a summary.
2. Copy ledger-template.md to <task-dir>/ledger.md if it is not there. Fill Contract, Paths, Discriminators and
   Fixtures, one row per item.
3. Fill the ledger's Blueprint before any code. One row for each materially different combination of entry point, change
   kind or mode, copy or data state, and lifecycle edge, for every contract row. Close each row with exactly one of:
   - `TESTED <test name>`
   - `OUT "<sentence copied exactly from the description>"`, or `OUT unreachable <file:line>`
   - `SAME <cell> <why it behaves the same>`, for a combination no plausible wrong rule can tell apart. Do not build the
     full cross product (checklist section 10).
   A cell you cannot close is an open problem in the design. Solve it now.
4. Run `python <skill>/tools/checklist_gate.py sheet <task-dir>`. It writes eval/checklist-run.md with one row per rule.
5. Walk the sheet in order. For each row, open the full rule in the checklist, do what it says for this task, then record
   `APPLIED` with where it now lives (a ledger row, a test, a file), or `NA` with the reason it cannot apply here. Fill
   each row only after doing the work. "See above", "covered", or marking a batch at once does not count.
6. Run `python <skill>/tools/checklist_gate.py check <task-dir> --through 5`. No code until it passes.
7. Build the tests and reference from the ledger, filling the step 6 and 7 rows as you go.
8. Before the v1 paste, run `check <task-dir> --through 7`. It also confirms every TESTED name is in test.patch.
9. After each of steps 6 and 8, give a fresh reviewer only build-checklist.md, the sheet, ledger.md, the description and
   the files so far. Ask it to open the cited place of every APPLIED row and every NA reason, and answer: does this really
   do what the rule says? Reopen every row it rejects, after checking its reason yourself, and fix it; this review runs once per step, never again
   for the fixed rows. The gate shows a row was filled.
   This review shows it is true.
10. After the sweeps, run `check <task-dir> --through 8`.
11. Tell the owner: the gate output, how many rows are APPLIED and NA, every NA row with its reason, and what the
    reviewer rejected.

A later checklist change makes the gate ask for a new sheet. Running `sheet` again keeps rows whose rule did not change.
Rows sharpened during a task apply from the next task; do not regenerate the current task's sheet for them
(PIPELINE.md "Review schedule").
