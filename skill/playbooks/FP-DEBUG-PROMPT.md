You are debugging a FAILED platform false-positive (FP) check on an Olympus challenge package. Everything else
passed (quality checks, Auto Review, agent runs). The FP panel says at least one PASSING agent solution is wrong
and slipped through our hidden tests. Your job is to FIND THAT REAL DEFECT and close it. You are NOT allowed to
conclude "genuine pass" unless you meet the proof bar in step 7.

INPUTS
- Description (fixed, do not edit): <path>/description.md
- Hidden tests + harness: <path>/test.patch        Reference solution: <path>/solution.patch
- Base repo at the pinned commit: <path>           Docker image: <image>
- Every PASSING agent run: <runs dir>/<run>/solution-patch.patch (+ trajectory, eval-result.json)
- The platform FP verdict text, VERBATIM (judges + adjudicator, every tab): <path>/fp-verdict.txt
- Earlier FP verdicts and what we changed after each: <path>/eval/ (read them so you don't repeat a dead end)

GROUND RULES
1. The platform is right until proven otherwise. Our past "it's genuine" conclusions were wrong every time this
   check kept failing. Assume a real defect exists in at least one passer.
2. Never edit description.md. Fixes go in test.patch (or solution.patch if the reference itself is wrong).
3. Every claim needs an executed command and its output. No reasoning-only verdicts.
4. Run everything offline in the image: docker run --rm --network none ... ; work on copies, never the package.

PROCEDURE
1. Pin each FP report to its agent. The panel numbers tabs over PASSING runs only (tab 2 is not agent 2). Grep the
   identifiers, function names, file paths and values each verdict quotes against every passer's patch. Write the
   mapping table: tab -> run folder -> evidence line.

2. Reproduce the panel's own probe FIRST. For each flagged passer, extract the exact scenario the judges/adjudicator
   describe (inputs, sequence, expected vs actual). Write it as a small test or script. Run it on the passer AND the
   reference. A probe counts only if the reference passes and the passer fails, repeated 3+ times.
   If the verdict says "upheld" but you cannot reproduce it, your reproduction is wrong: re-read the verdict
   literally, vary the inputs at boundaries (empty, zero, one, many, duplicates, max), and try again before moving on.

3. Flakiness check (the panel's strongest upheld signal). Re-run the hidden suite on each passer with
   -count=20 -race (or the language equivalent) and with --cpus=1. Any test that ever fails on a passer but never
   on the reference = an FP finding (a race or timing bug in the passer). Report the failure rate.

4. Item ledger of the description. Split every sentence into atomic ITEMS (each noun, outcome, boundary, error,
   ordering word, "every/any/all/only/never", "after/until/since"). For each item, list: which test asserts it, and
   whether EACH passer satisfies it (probe it, do not read it). A passer that misses any stated item = FP.

5. Diff-driven hunt on each passer vs the reference (read the code, then probe). Check, for every item:
   - both directions of each validation rule (rejects what it must, still accepts the nearest legal input);
   - the complement: a rule meant for a subset must NOT fire on the rest;
   - lifecycle: create, update, delete, re-add, restart/reload, reject-then-retry, shutdown; stale caches, metrics,
     indexes, notifier/background loops still holding old state;
   - combinations of two rules; name/format collisions; same name across kinds or instances;
   - global rules ("every", "any", "all X") applied to PRE-EXISTING types/paths too, using one large enough that a
     wrong value exists between "empty" and "correct";
   - every entry point and every output format the repo uses for the feature, not just the one the tests use;
   - error paths: partial application, rollback, side effects left behind after a failure;
   - concurrency with the scenario the feature exists for (in-flight work during a change).

6. Seeded differential probe. Write a generator of random valid inputs/operation sequences drawn ONLY from what the
   description fixes. Run each passer and the reference side by side over 1,000+ seeds, normalised to stated
   behaviour (ignore unstated wording/ordering). Print the first differing seed, minimised to the shortest sequence.
   Any difference on a stated item = FP evidence.

7. Proof bar for "genuine". You may call a passer genuine ONLY if ALL hold, each with output shown:
   the panel's probe is reproduced and the passer passes it; zero flaky failures in step 3; every ledger item in
   step 4 is satisfied; zero differences over the step-6 probe; and you can state, in one sentence quoting the
   description, why the panel's concern is not a stated requirement. Otherwise it is an FP and you keep hunting.

8. Close every real finding with the smallest fair change:
   - a hidden test grounded in a QUOTED description sentence, assertions first in the file;
   - the test must pass on the reference, fail on the flagged passer, and be deterministic (repeat 20x);
   - replay ALL passers against the new test.patch: at least one genuine passer must still pass. If the fix would
     leave zero passers, say so explicitly and propose the alternative (narrower test, or the exact description
     sentence that would need to change and why no test-only fix is fair);
   - add a mutant of the reference reproducing the defect and confirm the new test kills it;
   - re-run the four states (base/new x with/without solution) and confirm nothing else moved.
   Probe EVERY other passer for the same defect class: the report is a sample, not a census.

OUTPUT
1. Tab -> run mapping table.
2. Per passer: verdict (FP / genuine), the reproducing probe (command + output on passer and reference), the
   description sentence it violates, flake rate, ledger misses, first differential seed.
3. The test.patch diff you propose, its replay table (each passer: pass/fail before and after), mutant result,
   four-state result.
4. Anything you could not reproduce, ranked by how likely the panel is to uphold it, with what you tried.
Do not stop at the first finding. Hunt until every flagged passer has a reproduced defect or meets the step-7 bar.
