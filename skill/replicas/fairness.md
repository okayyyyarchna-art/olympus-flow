# Replica: test quality - FP, FN and AR lanes (site check "verifyFairness" and the test side of TQ)

Read `common.md` first.

Version 3, 2026-11-19 (vet task 6). The site found 12 blocking items over five rounds on one task while this replica's
earlier versions and a 336-variant sweep passed. Versions 1 and 2 are in the product's git history. Backlog #182 and #183 hold the evidence.

## Why the site keeps finding items (read first)
- The hidden tests leave a POOL of wrong solutions that pass every test. On vet task 6, 64 one-line variants of the
  reference still passed all 83 tests after five rounds, before counting design-level ones.
- The site needs ONE item from that pool that is a real defect. A review passes only when EVERY item is closed:
  caught by a test, proved equivalent, or proved not a defect. A review that samples (reads, thinks, reports a few
  items) loses to a site that samples too. Close the pool exhaustively.
- It is not a stronger model: the site's fairness check ran on an older model than our lanes. The difference is the
  question it asks, the oracle it judges by, and the code it reads.
- Our misses were judgement misses more than generation misses: the sweep generated two of the three fx16 blockers;
  triage dismissed them as "equivalent" and "defensive" by reasoning. Our checks were also correlated with the builder:
  every check was derived from the reference and the description the builder wrote, so they shared its blind spots.
  The site's oracle is the repository itself, and it once exposed a bug in the reference that no reference-derived
  check could see.

## How the site judges a wrong solution
- Blocking FP: a plausible wrong solution passes every hidden test, and its behaviour is a defect by ANY of:
  1. the description, read literally and in full;
  2. the behaviour BEFORE the change on that input. The site writes "Before the change, ..." and cites the base code
     and the upstream test that pinned it. A solution that loses that behaviour on a path the change touches regresses;
  3. a contract the repository documents: a code comment, a docstring, an upstream test, a message, or the rules of the
     sibling mechanism the new code mirrors or replaces (head walk vs new base walk; old link reader vs new one).
- A hang, an endless loop, unbounded recursion or a blow-up on an input where the base finished is always a defect.
- Its wrong solutions are what a solver writing from the description would plausibly do: the mechanism without one
  property of the code it mirrors. It cites file:line outside the diff (callers, siblings, upstream tests, comments).
- Blocking FN: a correct solution fails a test (an exact value where the file or the description admits another; an
  internal detail; timing a correct solution can miss).
- Not blocking: Clutter (duplicated helpers or fixtures; comments about the task, the issue or the test image instead of
  the code), Conventions (AGENTS.md style; how the repository's tests treat a missing tool), Scope.
- Output: "SUMMARY: Found N blocking fairness issues and M non-blocking." FAIL whenever a blocking item exists.

## Method

### 1. Mechanism inventory: read outward from the diff
For every function, type and data structure the reference adds or changes, record: its callers; every consumer of its
output (grep each field it writes); the code it replaces (`git show <base>:<file>`); the sibling mechanisms with the
same purpose elsewhere in the repository; the upstream tests that pin those; the comments that state rules.

### 2. Obligation ledger
Per mechanism, list obligations from the three sources, quoting file:line. Add the universal properties: termination
and bounds; the same result through every mode that must agree (fresh vs cached, link vs plain path, format versions,
one copy vs several); order independence where order carries no meaning; every view of the same data agreeing (record
vs per-manifest view, struct vs JSON).

### 3. Generator matrix: ask every question of every mechanism
Each question came from a site finding. Mark each cell applies / not applicable, with the reason.
- G1 Absent values: each compared or copied field absent on one side, removed, added, empty.
- G2 Several items, one key: two and three items with the same key but different states; first vs last; mixed vs
  uniform; a later item must not decide when an earlier one already does, and the reverse.
- G3 Merge fields: for every merge or override, every field of the result and which input it must come from; the
  fields that must NOT be taken over.
- G4 Widened collections: when the change adds a new kind of element to a shared collection (removed records, marked
  entries), every consumer (grep) handles it.
- G5 Sameness: every new comparison uses the repository's own notion of "same" (CRLF, links, canonical text).
- G6 State matrix: each item kind x added, kept, edited, removed, moved, renamed, type change (file, link, folder).
- G7 Fallback readers: every reader of a field with a fallback gets an input for each branch, including the input
  that selects the fallback.
- G8 Mirrors: diff the rules of new code against the code it mirrors or replaces, line by line (guards, limits, order,
  errors). Every rule of the old or sibling code is an obligation, also one the reference forgot.
  Where the new code must agree with that mechanism, it should consume the mechanism's decisions; re-running its
  rules on other input (another tree, another order) is a second implementation, and count- or order-dependent
  rules diverge. Test both: a change that alters the input of the rule, and an input whose order differs.
- G9 Termination: every loop, recursion, traversal and resolution: cycles, self references, links to the root, long
  chains, fan-out; the bound the sibling uses.
- G10 Shortcuts: every fast path added before general rules keeps every general rule (upstream tests of the general
  path often only reach inputs the shortcut skips).
- G11 Agreeing modes: fresh vs cached, link vs plain path, format versions, pull-request vs full scan.
- G12 Labels (FN): every exact label against peer situations and the choices the description leaves open.
- G13 Conventions (notes): the repository's test idioms; comments explain code.
- G14 Extra passes: when the change reads the same input a second time (a second walk, parse or read), every
  diagnostic, counter and side effect of the first pass still happens once. Check each count on an input that
  triggers it (vet task 6: a quiet head walk that also reports read errors printed "(4 times)" for two unreadable
  folders and passed every test).
- G15 Representation (FN): an exact-value assertion holds for every common reader of the format. Values those readers
  cannot tell apart (JSON integers above 2^53, float formatting, key order, layout) are a choice the description
  leaves open; a test that pins one rejects a fair solution, even when a solution review asked for it (vet task 6).
- G16 Layer pins (FN, notes): a test that calls an internal function with a hand-built state checks one layer. Reach
  the state through the public path, and confirm a real run can build it; a state no run builds is no test input.

### 4. Execute
- Line level: when the launcher supplies raw one-line variant results, every variant that passes all tests is an open
  pool item.
- Design level: for every applicable matrix cell, write the plausible wrong solution as a source edit of the reference
  (it may span lines) and run the FULL hidden suite. CAUGHT / PASSED ALL / INVALID / NOT VERIFIED.
- PASSED ALL means the item passes `test.sh new` AND the repository's own tests that the site runs as pass-to-pass
  (`test.sh base` with the edited solution applied). An item that fails either is CAUGHT; before reporting a blocking
  item, run base mode on it (vet task 6: a zero-hash item "passed every test" but failed an upstream base-mode test).

### 5. Close the pool: the same standard of proof both ways
Every PASSED ALL item stays open until closed by one of:
- CAUGHT: a test (existing or proposed and validated) rejects it;
- EQUIVALENT: an executed search for a distinguishing input found none, plus the argument why none exists;
- NOT A DEFECT: on its distinguishing input (run on base, reference and the item), each of the three sources is checked
  and quoted, and none makes its behaviour wrong.
"Defensive" is not a class: it is EQUIVALENT or NOT A DEFECT with that evidence. A loop guard or a limit is never closed
that way unless its input cannot occur. A finding needs a wrong solution, an input and a quote; a dismissal needs the
same weight of evidence. Parking is not a closure: "check later" or "only changes the full scan" leaves the item open,
and every mode the changed line runs in is checked (vet task 6: a parked guard became a site blocker).

### 6. The reference is a suspect
Derive the expected output from the three sources before looking at the reference's output. When a fair test fails
with the reference, report a reference bug; never bend the test to the reference.

### 7. FN lane
For every new or changed assertion (each table row and scan), compare the exact value with what the same file accepts
for the same situation, with repository conventions, and with the choices the description leaves open. Name a correct
implementation it rejects; prefer an executed one. A generous deadline that only fails a hang is fair; a deadline a
correct solution can miss is not.

### 8. AR lane
- Every new leaf fails on base on its own and passes with the reference, by the per-test selector. A check that passes
  on base is folded into a scenario that needs the fix; an unrelated failing assertion does not count.
- Outcome assertions only; no hidden requirements; no conditional skips beyond the repository's own convention.
- Names describe every scenario they hold; helpers reused; no duplicated fixtures or assertions.

### 9. After every site finding
Write the finding as a generator question (a G-row), add it here, and run it over EVERY mechanism of the task before
fixing anything. Do not store findings as per-task anecdotes.

### 10. Hard rules on every assertion (owner 2026-11-20)
For each assertion of each hidden file record five verdicts, and report any that fails:
- fair: the fairness sentence attempted (step 7 and G15);
- aligned: the description sentence or the existing repository behaviour (file:line) it checks is named; and the other
  way, every description sentence split on its triggers has an assertion;
- behavioural: it checks an observable outcome of running the product, against an oracle where the repository has one;
- public: it enters through the CLI or the engine's public options; no unexported call, no hand-built internal state, no
  name, field or type that only the reference adds (G16);
- per-leaf T1: the leaf it sits in fails on the clean base on its own.
Also report: a skip in a new test; a check that is empty when run as root (chmod) without a non-root presence guard;
OS-specific limits (link counts, path length) not gated on the OS; a leaf with several scenarios whose messages do not
name them; test files inside solution.patch counted as coverage (they are not graded).
Enumerate the cells (tq-once.md lists); do not sample. vet task 6: the site's Test Quality passed while 62 of 64 backed
wrong versions from our lanes still passed the suite; the next reviewer can pick any of them.

## Independence
- A judge never reads the builder's triage, ledger or conclusions: only the raw inputs (description, patches,
  repository, raw variant results, the list of changed code no test runs).
- Split lanes by lens to lower correlation: one lane on sources 2 and 3 (base behaviour, contracts, mirrors), one on the
  description and the matrix, one on FN and AR.

## Budget
Set a deadline. Cap static reading at 15% of it; spend at least 60% executing and closing pool items. Report every
item left open as NOT VERIFIED; an open item is never an unqualified PASS.

## Output
Start exactly with:

SUMMARY: Found N blocking fairness issues and M non-blocking.

Then, for every blocker:

BLOCKING 1 (FP, FN, or AR):
- Claim:
- Solution that passes or fails: the exact edit, a concrete input and its output.
- Why: quoted file:line evidence (description, base code, comment, upstream test, sibling code).
- Evidence: commands, results, log paths (full suite; focused runs on base, reference, wrong solution).
- Suggested change: the smallest fair test change, with validation status (fails on base alone, passes with the
  reference, rejects the wrong solution).

For every quality note:

NOT BLOCKING 1 (category):
- Observation:
- Where:
- Suggested change:

Then the pool ledger: every item with its closing class and evidence, and every NOT VERIFIED item. End with exactly one
line: `Verdict: FAIL`, `Verdict: PASS`, or `Verdict: NOT VERIFIED`.
