# Pass Solution Quality once (gate before every Solution Quality purchase)

From an owner hand-over (2026-11-21) built from every platform Solution Quality result since 2026-10-25 (turso, swift,
faust, elio, vet) and the rounds where our own checks had passed and the site still failed us. The site's reviewer
reads the description, the whole repository, every line of solution.patch and what test.patch edits, then runs things:
it builds a concrete input (a real git repository with links, a 4000-entry lockfile), runs the real command on base
and on the reference, compares the output and times best of 3 before and after. It blocks on two things only: a wrong
output on an executed input, judged by any of three sources (a description sentence; the behaviour before the change
that the description keeps; a contract the repository documents: a comment, an upstream test, the sibling mechanism
the new code mirrors), and a measured slowdown on the normal path (a plain scan 1.34x slower at 4000 entries). All
else is a note labelled Design, Clutter or Practice: any number passes, but the same notes come back every round until
fixed or declined in writing. The report reads "Found N blocking issues and M non-blocking issues"; a blocking item
gives Input, Command, Expected output, Received, Why and a fix at file:line. Each paid round samples a new angle (five
runs on one unchanged faust package gave four different findings): a pass is a sample, the lists below are the proof.

Hard rules for every solution.patch: every error path and every \"error, then reuse the same object\" path releases its resources through the owner, never inside a callback that still holds them (field notes 2026-11: a double close through a wrapper deadlocked, then closed a reused descriptor); every promise holds on every path the repository ships, also the ones hard to run
locally; outside what the description asks the output is what base gives (a PR that changes nothing reports nothing);
the normal path pays nothing for the feature; one logic in one place, every hunk needed, every comment and doc claim
true through the real caller; nothing is parked: a finding inside a promise is fixed or disproved by a run, never a
"residual" (twice the site quoted residuals we had written into our own hand-over).

## 1. Four lists, written down before the first upload
1. Promise x path grid: one promise per observable outcome, scope sentences included, times every path it runs through:
   each call form of the named command (flags on and off, modes, outputs), each sibling form a universal word covers
   (*.tf and *.tf.json; npm lockfile versions 1-3), each driver, backend or store the repository ships (named or not,
   installed in the image or not), each source that feeds the feature and each read path, fast paths and twins included.
2. Decision rows: one per if / else / case arm, guard, early return, default, cap, constant, threshold and heuristic:
   what it does to the promised state, what an early exit has already changed above it, the smallest in-scope input
   that breaks a heuristic or threshold (the site's favourite shape), the source of a limit constant on the grader's
   Linux (40 links, PATH_MAX 4096).
3. Rejection ledger: every branch that refuses, skips or returns "not handled", the input that reaches it, then the
   sentence that excludes it or proof that base refuses it too; a row with neither is fixed by making the shape work,
   not by narrowing (a code comment defending the rejection did not help us).
4. Touched-site ledger: for every site the patch touches, each write it removes or makes conditional and who reads it
   (grep every package); each side effect the old code produced there (diagnostics, counts, temporary files) and
   whether a second pass repeats it; the same input outside the described mode; each per-item step added on paths that
   do not need the feature (the input for section 3).
A cell is closed only by a run; a trace through the code is a hypothesis.

## 2. Close every cell by running it
- Run the real command in the task image on a built input, as a non-root user as well: at least 6 executed break
  attempts per round plus every attempt that depends on the filesystem, paths, links, users or line ends; record command
  and output next to the cell. Path or link code always gets: a target reached through a linked ancestor folder,
  absolute link texts through that alias and through the real path, links to a file, a folder, dangling and outside, a
  link checked out as a text file, a CRLF checkout.
- Unchanged-PR sweep against upstream after every solution change: build upstream and the reference, scan trees whose
  last commit edits only an unrelated file, one per shape of each touched axis and per file name the code asks for;
  expected: no record with a change; one state folder (HOME / XDG) per binary. Shared-path run: the same inputs outside
  the described mode on base and reference; a changed output is scope growth unless a sentence asks for it.
- Every wrong-output finding from any earlier lane is executed before it is dropped, whatever its label (the alias input
  that failed us had been left as "Low" by our own Auto Review lane, without a run). A PASS counts only when the
  attempts ran; "could not run" is NOT VERIFIED, and so is the verdict. Unit tests in solution.patch are not graded.

## 3. Cost on the normal path
Correctness reviews and hidden tests use tiny inputs, so they never see this. Before every SQ purchase: take the
per-item steps from list 4 that run on paths which do not need the feature; time base against the reference at 1x and
2x input size, best of 3, alone in the task image; fix superlinear growth or more than about 5% added time (compute the
value only where it is read, or in one linear pass); keep the before and after timings for the next round. Check every
new loop over user data for a quadratic shape (a whole-file scan per entry was our blocking item).

## 4. Judging a candidate finding
Before any verdict write three columns: the description sentence, what base does on that input (run it), and where the
reference's rule came from (a platform finding, a stated sentence, or our own review round). A finding: an executed,
realistic input breaks one of the three sources. Not a finding: behaviour the description leaves open or one of two
readings; the reference does what base does for the equivalent plain case and the description asks for that; an input
outside the stated scope. Never a defence when the site judged us: "base does the same" inside a promise; "not
observable through today's API" (the site counts stored state); "rare" or "contrived" inside a stated sentence; "an
upstream test pins nearby behaviour"; "another reviewer passed it" or "the site did not flag it last time"; a scope note
in our reviewer brief and not in the description (never tell local reviewers what is "not promised"). One real instance
names a class: fix every member in the same batch (one member per round cost us three rounds). Every in-contract fix
gets a fair hidden test and a kept wrong version; the reverse holds: a behaviour only a solution review asked for, with
no sentence behind it, is not test material, and Test Quality will call that test unfair.

## 5. Notes: Design, Clutter, Practice
Sweep the whole patch for each label before the upload. Design: a list or rule kept in two places; work another layer
already did; the same logic twice; a resource opened several times; a behaviour no sentence asks for. Clutter: code only
tests call; a forwarder that adds nothing; an unreachable fallback; a stored-format version that jumps by more than one;
narrating or leftover comments; two doc paragraphs for one function. Practice: a quadratic loop over user data (measure
it and quote the times); a value re-parsed on every call; an error dropped without a log; a caller's slice sorted in
place; validation that mutates before it fails. Around the patch: linters and formatter clean; every doc, CHANGELOG and
comment claim traced to the code that enforces it, claims about other components included; no public output changed so
that an upstream test goes stale, even a deselected one; when test.patch removes a test of the old behaviour from an
existing file, a positive case of the feature goes into that same file. Fix a note in the same batch when it is cheap
and changes no behaviour; otherwise decline it with a written reason the next round can copy; a redesign of tested
behaviour goes to the owner with its cost.

## 6. Order and repair loop
- After every change to solution.patch: class audit, unchanged-PR sweep, timing, our own SQ review on the new bytes
  (executed attempts), the proof (hidden tests both ways, root and non-root, lint), then the paste; the hand-over says
  which hash each check saw. Site order after a solution paste: prechecks and Scope Gate, Verify Solution, Verify
  Flakiness, Reward Hacking, Solution Quality, then Test Quality last; a solution edit stales all of them.
- A report from the site: bind it to the bytes it graded; ledger every item (id, hash, severity, real or misread,
  status) and keep a list of what the site accepted, never redesigning those parts; reproduce each blocking item in the
  task image first (Input, Command, Expected, Received); real: fix it; misread: one plain comment at that line and no
  code; not reproducible: say so with the run; sweep the item's class, then the smallest fix (5 to 15 lines, the
  repository's own helpers and style, no new module, never removing a fix the site asked for); add the fair hidden test
  and the kept wrong version, prove, and run our SQ review again on the new hash.
- Do not buy the same bytes again after a fail, add code for cases no sentence covers, refactor what the site accepted,
  or change the description inside this loop. Floor: stop when only accepted or misread items are left; after a second
  fail, fresh eyes on the four lists (independent reviewers given the method, code and report, not our conclusions).

## 7. Evidence in three lines
- Fourteen rows of site results on five repositories quoted, among others, a rejected shape, a mode history, a driver
  nobody had read, a documented "unless", a cache key, two listed residuals, a 1.34x slowdown, an alias path and a
  removed write.
- We missed them by sampling a class, parking a finding (a residual, a nit, a Low without a run, a scope note the
  description never makes), reading instead of running, leaving a path or a test edit unread, or never timing a step.
- The one PASS (vet, 0 blocking, 6 notes) followed a slowdown reproduced, fixed in one linear pass and re-timed.

## 8. The gate on one page (walk it on the exact bytes to be pasted)
- [ ] Promise x path grid filled: every call form, sibling form, shipped driver or backend, source and read path.
- [ ] Decision rows filled: state per branch and before each early exit, smallest breaking input per heuristic, limits.
- [ ] Rejection ledger: every refusal has an excluding sentence or proof that base refuses too.
- [ ] Touched-site ledger: every removed or conditional write has its readers named; no side effect doubled.
- [ ] At least 6 break attempts executed in the image, non-root included; the link set run where the code touches paths.
- [ ] Every earlier wrong-output finding executed before it was dropped.
- [ ] Unchanged-PR sweep against upstream: no record with a change; separate state folder per binary.
- [ ] Same inputs outside the described mode: output equal to base.
- [ ] Timing at 1x and 2x, best of 3: no superlinear growth, at most about 5% added on the normal path.
- [ ] Design, Clutter and Practice sweep done; cheap notes fixed, the rest declined with a written reason.
- [ ] Linters and formatter clean; every doc and comment claim traced to code; no stale upstream assertion.
- [ ] Every in-contract reference fix has a fair hidden test and a kept wrong version.
- [ ] Our own SQ review ran on this exact hash, with executed attempts; no residual inside a promise in the hand-over;
      the accepted-by-the-site list is untouched.
