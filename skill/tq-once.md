# Pass Test Quality once (gate before every Test Quality purchase)

From an owner handover (2026-11-19, an agent that passed TQ on its third paid run) and vet task 6, where the same check
failed several rounds. The site's reviewer runs the hidden tests without the solution, reads the description and the
repository, infers the solution's shape, writes realistic wrong solutions and blocks on two things only: a gap (a
wrong solution passes every test) or an unfair test (a correct solution fails one). Each paid round samples a new
reviewer, so a pass proves nothing about the next round. Find every cell yourself first.

Hard rules for every hidden test (owner 2026-11-20; details in tests.md): fair; aligned with the prompt both ways;
behavioural; no API-based tests; public behaviour only. vet task 6 passed Test Quality once while 62 of 64 backed wrong
versions still passed its suite: a pass is a sample, the lists below are the proof.

## 1. Three lists, written down before the first upload
1. Everything the solution does: one row per decision point of solution.patch (each if / else / case arm, each term
   of a compound condition, each list member, default, cap, constant, cast, early return, special case), each with the
   test that fails when only that row changes. Plus one row per existing behaviour at each site the patch touches
   (data, diagnostics and counts the code already produced there). vet 6: the platform blocked on an existing warning
   count that a new second walk could double; our sweep had flagged the line and I parked it.
2. Every call form the repository accepts for the named commands: each flag on/off, input form, mode, output.
3. Every description sentence split on its triggers: a list of N needs N rows plus one off the list; any / each /
   every / other / including need an input nobody would hard-code; "X or Y" and "with or without" need both.
A cell is covered only when a test makes that call and compares with an oracle: an ordinary path that must agree
(the full scan of the same tree, the base code on the old input, the live scan against a saved report), not a typed
literal. Fill every admitted cell; write the reason for each excluded one.

## 2. Prove every gap with a kept wrong version
- Write the wrong version as a scripted edit of the reference (eval/wrong/<lane>/<name>.py with EDITS = [(path, old,
  new)]), run the current suite: it must pass, else the finding is stale. Run it as well against the repository's
  own tests of the package it edits.
- Add the check inside the existing test for that area. A new test function only where no test covers the area, and
  only if it fails on the clean base: T1 is per leaf. vet 6: splitting a 35-pair loop into subtests made 15 leaves
  pass on base; deleting one assertion made another leaf pass on base. Loop axis members inside one test.
- Keep every wrong version (eval/wrong/kept/, KIND wrong|control|held, EXPECT leaf; `tools/wrong_versions.py` runs
  them, the fast check calls it) and re-run all of them on the final suite: each wrong one fails exactly its leaf,
  each control passes, a script whose edit no longer applies fails the step.
- A wrong version for a design that differs in structure from the reference changes the structure (not a constant
  the reference never reaches), with a control of the same structure and the right decision. For every function
  that compares or copies a list of fields, one wrong version per field.
- A cell removed for a rollout (a near miss fails only it) leaves its code path untested, and the next reviewer can
  block on exactly that path (vet 6 fx30/fx32). Replace it: write the natural wrong design for that path (the
  reference minus one check), find an input where that design fails and the near miss passes, add it as a case of
  the same test with a kept wrong version; dry-run the input against the near miss's own code first. What stays
  uncovered is the near miss's own variant: record it and tell the owner before the paste.
- One-line variants miss guards made always true, compound return predicates and constants; the sweep only touches
  lines the tests run, so an untested branch makes no variant at all. Lanes that read the code fill that in.

## 3. Fairness: the one-sentence test, over the whole file, every round
For every assertion try: "a correct implementation that satisfies every sentence could still do X, and X fails this".
If it can be written, weaken the assertion to what the sentence states, accept both, or delete it. Patterns seen:
- values common readers do not tell apart (JSON integers above 2^53: npm and Go's default decode read one value);
- a behaviour a solution review asked for is no test by itself (vet 6 blocking 2 came from our own SQ request);
- counts a design that walks a checkout of the base would double: count only what only the head has;
- internal functions called with hand-built states a real run never builds;
- a field the statement does not name (the record's Local flag);
- "the manifest file" singular where the build tool uses one of two files (Gradle).
For an unfair finding, keep the correct code it rejected as a control; it must pass the whole suite afterwards.
Field notes from another author's package (2026-11, a Go WebSocket task through SQ and TQ): a bad-data case is valid
apart from its one defect and has a valid twin, checked against the standard library (if the library accepts the
case, do not require rejection); a reference variant that differs only in unstated details (a narrower integer type,
another error value) must still pass; every enumerated item gets a row through each API form (sync and async).

## 4. Runtime, determinism, no skips
- No skip in new tests: a skipped leaf counts as passing for the reviewer and as a gap for Trial QA. For a check that
  depends on the user (chmod), compare with an oracle instead: as root both sides are 0, as uid 1000 both are N.
- One solo run of the new suite under 6 minutes; no wall-clock races (rely on go test -timeout). The platform's
  oracle runner is slower than local Docker: time the suite at half a CPU, avoid thousands of tiny inputs and tight
  deadlines (field notes: a test sending about 10,000 small frames passed locally and failed the oracle), and run the
  reference three times plus once pinned to a single CPU before a paste.

## 5. Order and repair loop
- Re-run order after a paste: prechecks and Scope Gate, Task Prompt Quality, Verify Tests, Verify Solution, Verify
  Flakiness, Reward Hacking, Category Alignment, Solution Quality, then Test Quality last (a test.patch edit stales
  the others). Every status names the version hash it graded.
- A report: bind it to the bytes it graded; reproduce each item as a wrong version first; sweep the item's class
  (every sibling: the other member of a pair, the other error kind, the flag's other state, each existing behaviour at
  every touched site); fix once inside existing tests; fairness over the whole file; prove (clean base: every leaf
  fails, none skipped; every kept wrong version fails its leaf; reference passes; lint; the three Verify Tests runs as
  the offline user, in one container so it compiles once).
- Code-quality notes: fix when free, else decline with a written reason that the next round copies.
- After a second Test Quality fail: fresh eyes on the grid (independent lanes and a Codex review given the method, the
  code and the report, not our conclusions) before buying a third run.
