# Passing Solution Quality once (the gate before every Solution Quality purchase)

Handover, 2026-11-21. It is built from every Solution Quality (SQ) result we have had on the platform since
2026-10-25, on tasks in five repositories (turso, swift, faust, elio, vet), and from the rounds where our own checks
had passed and the site still failed us. Section 8 lists that evidence.

Words used here: the **reference** is solution.patch; the **hidden tests** are test.patch; **base** is the repository
at the pinned commit, before the change; the **task image** is the Docker image built from the task's Dockerfile.

## 0. What the site's reviewer does

- It reads the description, the whole repository and every line of solution.patch, and it looks at what test.patch
  edits. It does not stop at the files the patch touches.
- It **runs things**. It builds a concrete input (on vet: a real git repository with links, a 4000-entry lockfile),
  runs the real command on base and on the reference, and compares the output. For speed it times best of 3 before
  and after, then stubs the suspected function out to prove the cause.
- It blocks on two things only:
  1. **Wrong output** on an input it executed. "Wrong" is judged by any of three sources: a description sentence, the
     behaviour before the change that the description keeps, or a contract the repository documents (a code comment,
     an upstream test, the sibling mechanism the new code mirrors).
  2. **A measured slowdown on the normal path** (vet: a plain scan 1.34x slower at 4000 entries was blocking).
- Everything else is a non-blocking note labelled **Design**, **Clutter** or **Practice**. Any number of notes still
  passes, but the same notes come back every round until they are fixed.
- Report format since 2026-11-18: "Found N blocking issues and M non-blocking issues". Each blocking item gives Input,
  Command, Expected output, Received, Why (it quotes the description and names the code path) and a suggested change
  with file:line. Before that the site printed Comprehensiveness x/3 and Code Quality x/3; a 1/3 failed.
- **Each paid round samples a new angle.** Five runs on one unchanged faust package gave four different findings;
  three runs on a turso task each quoted a different rejected shape. A pass is a sample. The lists below are the
  proof.
- A Medium that SQ quotes comes back in Auto Review's solution score with the same blocker. "Only a note" in SQ is
  not "ignore".

## 1. Hard rules for every solution.patch

1. Every promise holds on every path the repository ships: each entry point, mode, driver, backend, file format
   version and sibling file form. A path that is hard to run locally is still owned.
2. Outside what the description asks, the output is what base gives. A PR that changes nothing reports nothing.
3. The normal path pays nothing for the feature: no per-item work on runs that never read its result.
4. One logic in one place, every hunk needed, every comment and doc claim true through the real caller.
5. Nothing is parked. A finding inside a promise is fixed or disproved by a run; it is never a "residual", and the
   hand-over lists none. Twice the site quoted residuals we had written into our own hand-over.

## 2. Four lists, written down before the first upload

1. **Promise x path grid.** Split the description into promises, one observable outcome each, scope and exclusion
   sentences included. Then one row per path each promise runs through:
   - every call form the repository accepts for the named command (each flag on and off, each mode, each output);
   - every sibling form the tool or format defines inside a universal word such as "every lockfile" (vet: Terraform
     builds its lock from `*.tf` and `*.tf.json`; npm lockfiles come in versions 1, 2 and 3);
   - every driver, backend, store or transport the repository ships, also ones the description never names and ones
     not installed in the image (faust: two fails on the confluent driver no local lane had read);
   - every source that feeds the feature, and every read path including fast paths and compiled twins.
2. **Decision rows of the patch.** One row per if / else / case arm, guard, early return, default, cap, constant,
   threshold and heuristic. For each row write:
   - what happens to the state a promise talks about when that branch is taken (applied, kept for later, dropped);
   - for an early exit, what the function has already changed above it (an entry popped, a counter moved, a flag set);
   - for a heuristic, sample or threshold, the smallest in-scope input that breaks it. This is the site's favourite
     shape: it picks one design decision and builds the smallest input inside the promise that defeats it;
   - for a constant at a real limit, its source on the grader's platform (Linux follows 40 links, PATH_MAX is 4096).
3. **Rejection ledger.** Every branch that refuses, skips or returns "not handled": the input that reaches it, then
   either the description sentence that excludes that input or proof that base refuses it too. A row with neither is
   fixed by making the shape work, not by narrowing. A code comment defending the rejection did not help us.
4. **Touched-site ledger (existing behaviour).** For every site the patch touches:
   - each write the patch removes or makes conditional, and who reads it (grep Stat, Open, ReadDir, map lookups in
     every package, not only the touched one);
   - each side effect the old code produced there (diagnostics, counts, files in a temporary tree), and whether a
     second pass the patch adds repeats any of them;
   - the same input outside the described mode;
   - each per-item step the patch adds on paths that do not need the feature (input for section 4).

A cell is closed only by a run (section 3). A trace through the code is a hypothesis.

## 3. Close every cell by running it

Our static reviews passed a package that the site then failed twice on one input. Since then execution is mandatory.

- **Run the real command in the task image** on a built input, as a non-root user as well. At least 6 executed break
  attempts per round, plus every attempt whose result depends on the filesystem, paths, links, users or line ends.
  Record the command and the output next to the cell.
- **For code that handles paths or links, always run this set:** the target reached through a linked ancestor folder
  (as `/tmp` names `/private/tmp` on macOS); absolute link texts written through that alias and through the real
  path; a link to a file, to a folder, dangling, and pointing outside; a link checked out as a text file; a CRLF
  checkout.
- **Unchanged-PR sweep against upstream, after every solution change.** Build upstream and the reference. Scan trees
  whose last commit edits only an unrelated file, one tree per shape of each touched axis and per file name the code
  asks for. Expected: no record with a change. Validate any difference from upstream before the paste. Give each
  binary its own state folder (HOME / XDG), or one build reads the other's saved data and the result lies.
- **Shared-path run.** Run the same inputs outside the described mode on base and on the reference. A changed
  output is scope growth unless a sentence asks for it.
- **Every wrong-output finding from any earlier lane is executed before it is dropped,** whatever severity label it
  carried. The alias input that failed us on the site had been found by our own Auto Review lane and left as "Low"
  without a run.
- A lane's PASS counts only when its attempts ran. "Could not run" is NOT VERIFIED, and so is the verdict.
- Unit tests that solution.patch adds are not graded and prove nothing here.

## 4. Cost on the normal path

Correctness reviews and hidden tests use tiny inputs, so they never see this. Before every SQ purchase:
1. Take the per-item steps from list 4 that run on paths which do not need the feature (a plain run, other modes,
   other ecosystems).
2. Time base against the reference at 1x and 2x input size, best of 3, alone in the task image.
3. Fix superlinear growth, or more than about 5% added time: compute the value only where it is read, or in one
   linear pass. Keep the before and after timings; the next round needs them.
Also check every new loop over user data for a quadratic shape (a whole-file scan per entry was our blocking item).

## 5. Judging a candidate finding

Before any verdict, write three columns for the input: the description sentence, what base does on that input (run
it), and where the reference's rule came from (a platform finding, a stated sentence, or our own review round).

It **is** a finding when an executed, realistic input breaks one of the three sources in section 0.

It is **not** a finding when:
- it needs behaviour the description leaves open, or rests on one of two readings of a sentence;
- the reference does what base does for the equivalent plain case and the description asks for that ("as it does
  now", "keeps current behaviour");
- the input is outside the scope the description states.

These were never a defence when the site judged us:
- "base does the same", for a case inside a promise;
- "not observable through today's API" (the site counts stored state against "exactly the same state");
- "rare" or "contrived", for an input inside a stated sentence;
- "an upstream test pins nearby behaviour", until a fix gated on state that test does not set was tried and failed;
- "another reviewer passed it", or "the site did not flag it last time";
- a scope note that lives in our reviewer brief and not in the description. Never tell local reviewers what is "not
  promised"; they must stay free to escalate it.

When one instance is real, name the class and fix every member in the same batch: the other lockfile kinds, the other
controls that read the same field, the twin entry point, the other error kind. Fixing one member per round cost us
three rounds on one defect.

Every in-contract fix of the reference gets a fair hidden test and a kept wrong version; "fixed, no test" is not
closed. The reverse also holds: a behaviour that only a solution review asked for, with no sentence behind it, is
not test material, and Test Quality will call that test unfair.

## 6. Notes: Design, Clutter, Practice

The site writes several on every package. Sweep the whole patch for each label before the upload.
- **Design:** a list or rule kept in two places; a component redoing work another layer already did; the same logic
  written twice; a resource opened several times; a behaviour no sentence asks for (scope growth: we removed one).
- **Clutter:** code that only tests call; a forwarder that adds nothing; an unreachable fallback; a stored-format
  version that jumps by more than one; narrating or leftover comments; two doc paragraphs for one function.
- **Practice:** a quadratic loop over user data (measure it and quote the times); a value re-parsed on every call; an
  error dropped without a log; a caller's slice sorted in place; validation that mutates before it fails.
- **Around the patch:** configured linters and formatter clean; every claim in docs, CHANGELOG and comments traced to
  the code that enforces it, including claims about other components; no existing public output changed in a way
  that makes an upstream test stale, even one the test script deselects; when test.patch removes a test of the old
  behaviour from an existing file, a positive case of the feature goes into that same file.

Fix a note in the same batch when it is cheap and changes no behaviour. Otherwise decline it with a written reason
that the next round can copy (ours: "pinned upstream tests call this function, and the existing tests must pass
untouched"). A note that needs a redesign of tested behaviour goes to the owner with its cost.

## 7. Order and repair loop

- **After every change to solution.patch:** class audit, unchanged-PR sweep, timing, our own SQ review on the new
  bytes (executed attempts), the proof (hidden tests both ways, as root and as a non-root user, lint), then the
  paste. Say in the hand-over which hash each check saw.
- **Re-run order on the site after a solution paste:** prechecks and Scope Gate, Verify Solution, Verify Flakiness,
  Reward Hacking, Solution Quality, then Test Quality last. A solution edit stales all of them.
- **A report from the site:**
  1. Bind it to the bytes it graded.
  2. Put every item in a ledger: id, package hash, severity, real or misread, status. Keep a second list of what the
     site has accepted, and never redesign those parts.
  3. Reproduce each blocking item in the task image first, with its Input, Command, Expected and Received.
  4. Decide: real, fix it; misread, one plain comment at the misread line and no code; not reproducible, say so with
     the run.
  5. Sweep the item's class (section 5), then make the smallest fix: 5 to 15 lines, the repository's own helpers and
     style, no new module. Never remove a fix the site asked for earlier.
  6. Add the fair hidden test and the kept wrong version, prove, and run our SQ review again on the new hash.
- **Do not** buy the same bytes again after a fail, add code for cases no sentence covers, refactor what the site
  accepted, or change the description inside this loop.
- **Floor:** stop when only accepted or misread items are left. After a second fail, get fresh eyes on the four lists
  (independent reviewers given the method, the code and the report, not our conclusions) before a third purchase.

## 8. Evidence: what the site quoted, and why our checks had passed

| Task | Site result | What it quoted | Why we had missed it |
|---|---|---|---|
| turso, NOT IN view | 1/3, three runs | a different compound shape each run that one rejection branch refused, under "anything a materialized view already handles" | our reviewers sampled the class too; a comment defended the rejection |
| turso, same package | Code Quality 2/3 | test.patch deleted an old rejection test and added no positive case in that file | nobody read the test edits as part of the solution's quality |
| swift, versioned delete | 1/3 High | a "null" version delete after versioning was suspended and re-enabled took a pass-through | two reviewers had flagged it; parked on a scope note the description never makes and on a pinned upstream test |
| swift, same feature | 2/3 Medium | one entry point wrote a fresh ACL on the restored object, the bulk one did not | called a nit, "not observable through the API" |
| faust, table recovery | 2/3, several runs | a staleness check moved before awaited callbacks was missing after them; one table kind and one fast read path not covered | the contract was traced through one store class only |
| faust, dead letters | 1/3 twice | two defects in the confluent driver the patch had enabled | driver not installed in the image, so nobody reviewed it |
| faust, dead letters | 1/3 | a documented caveat, "unless the agent awaits something after its ack" | a limit written down inside a promise is a quotable gap; nobody grepped for "unless" |
| faust, dead letters | Code Quality 2/3 | per-partition state not pruned on revoke; in another run, a doc claim about another component that was false | the first was raised by our reviewer as Low and parked; the second was written from an assumption |
| elio, compressed files | 2/3 Medium | a replacement with the same size and timestamp kept the old preview | kept because the repository's own caches use the same key |
| elio, same task | findings two rounds running | a sampling stamp and a "more pages than other files" rule, each broken by one small input | both were residuals listed in our hand-over |
| vet, PR accuracy | FAIL, 1 blocking, 9 notes | a plain scan of a 4000-entry lockfile 1.34x slower | no check asked what a per-entry step costs on the normal path |
| vet, PR accuracy | FAIL twice | a repository reached through a linked folder, absolute link texts written through the alias | our SQ lanes were static; an earlier lane's finding was left as Low without a run |
| vet, PR accuracy | FAIL, 1 blocking, 3 notes | a lockfile name linking to a folder next to its manifest, PR edits README only: the reference reported REMOVED, base reports nothing | the patch removed a file write that code in another package read; no run compared an unchanged PR with upstream |
| vet, PR accuracy | PASS, 0 blocking, 6 notes | notes only, after the speed fix | not a miss: the slowdown was reproduced, fixed in one linear pass and re-timed before the paste |

## 9. The gate on one page (walk it on the exact bytes to be pasted)

- [ ] Promise x path grid filled: every call form, sibling form, shipped driver or backend, source and read path.
- [ ] Decision rows filled: state on each branch, state changed before each early exit, smallest breaking input for
      each heuristic, source of each limit constant.
- [ ] Rejection ledger: every refusal has an excluding sentence or proof that base refuses too.
- [ ] Touched-site ledger: every removed or conditional write has its readers named; no side effect doubled.
- [ ] At least 6 break attempts executed in the task image, non-root included; the path and link set run where the
      code touches paths; every earlier wrong-output finding executed.
- [ ] Unchanged-PR sweep against upstream: no record with a change; separate state folder per binary.
- [ ] Same inputs outside the described mode: output equal to base.
- [ ] Timing at 1x and 2x, best of 3: no superlinear growth, at most about 5% added on the normal path.
- [ ] Design, Clutter and Practice sweep done; cheap notes fixed, the rest declined with a written reason.
- [ ] Linters and formatter clean; every doc and comment claim traced to code; no stale upstream assertion.
- [ ] Every in-contract reference fix has a fair hidden test and a kept wrong version.
- [ ] Our own SQ review ran on this exact hash, with executed attempts.
- [ ] No residual inside a promise in the hand-over; the accepted-by-the-site list is untouched.
