# Build checklist (S2 reference + S3 tests): write it right the first time

This is HOW test.patch (tests + test.sh) and solution.patch are written, not a review after writing. **Start with
[prompts/apply-build-checklist.md](prompts/apply-build-checklist.md): every rule below gets its own row, and a condensed
plan never replaces it.** Walk the eight
steps in order. Steps 1-5 are planning written into one ledger (the task's ledger.md) before code; steps 6-8 build,
prove and review against it. Goal: the first draft passes Auto Review (T1-T8, S1-S4), Task Quality (fairness,
coverage), Solution Quality (comprehensiveness, code quality), the false-pass (FP) panel, the verify checks and the
rollouts, so the review sweep finds what is left instead of rebuilding the coverage. It does not guarantee bands or a
sweep count; it removes the misses we already know.

Shortcuts that cost a task (vet task 2), at every stage: a named artifact is filled in full, never a condensed note; a
check reads the exact bytes it certifies; no claim about a result you have not read; gates run in the stated order, even
under time pressure.

Sources (all on or after 2026-10-16): the vet task (sweeps w1-w3, 7 replica rounds, FP audits, shadow lanes,
batteries 1-18, final-package variants) weighted most; 8 accepted or in-review tasks (faust 9-12, turso, elio, swift,
docker proxy); Codex's own platform-CLI study (vet eval/checklist-cx.md, C01-C31); a GPT-6 Astra review (vet
eval/checklist-review-astra.md, M1-M6, R1-R8); vet eval/checklist-evidence-platform.md (rows A-E) and
eval/checklist-evidence-accepted.md; the vet platform phase (wip02 rollout of 16 runs, wip03 re-eval, platform SQ/AR
notes, FP panel notes; eval/decisions.md); the gap study of the 9 accepted packages after 2026-10-12
(olympus-product eval/checklist-gaps/oss70.md P1-P15, codex.md 1-8); vet task 2 (rollout 1 replay). Rule
definitions: the platform rubric (section 9).

## The ledger (the task's ledger.md, copied from ledger-template.md): one file, each row linked to its contract row
1. Contract: one row per atomic obligation (quote, outcome, allowed readings, exclusions, grounding, status).
2. Paths: entry points, stores and formats, modes and sibling paths, transitions, faults, resource lifetimes.
3. Discriminators: wrong-rule classes, valid alternatives, smallest differing input, killing test, disposition.
4. Fixtures and harness: fake capabilities, expected test ids, environment assumptions, failure branches.
5. Evidence: artifact hashes, commands, run ids, results (NOT RUN until executed), stale marks.
6. Blueprint: every combination of entry point, change kind, copy state and lifecycle edge that differs, each closed
   by a test, a quoted sentence or a named equivalent cell, before any code (the prompt above, step 3).

## 1. Pin inputs and feasibility
- Record the locked description hash, the pinned commit, the image and toolchain identity, and the real grading
  interface: `./test.sh base|new --output_path`, offline, an arbitrary uid without a passwd entry, cleared HOME/env.
- Run the repo's base suite once on the pinned commit: note slow, flaky, network and internal-call tests (C4).
- Read profile.json (language, runner, JUnit, test/production paths) from repo init.

## 2. Atomic obligations and scope (ledger: Contract)
- Split every behavioral sentence into atomic obligations: each verb, subject or kind, condition, quantifier and
  observable effect (M1). One contract row each, with the exact quote, the observable outcome, the allowed readings,
  the exclusions and the grounding (sentence, or repo behaviour quoted with file:line). [T4, TQ, S1]
- Mark each row NAMED (a sentence names the case) or IMPLIED (only the general rule covers it). Two stacked implied
  cases in one script gave 0/16 platform runs on vet; the mark also decides what a re-eval may relax later
  (near-miss-release.md). [T5, FP]
- A row whose path runs in a mode or entry point that no sentence names is HIDDEN, not implied: name the mode in
  the description before the lock (the mode only, no mechanism). After the lock, drop the row. Re-mark every test added
  after the lock before each paste (vet task 2: sweep fixes added pull-request tests to a description that never named pull requests; 4/4
  rollout patches failed only those tests and the general sentences no other). [T5, FP]
- Scope, exclusion and "keeps current behaviour" sentences are obligations too (A7). Couple each keep-behaviour
  assertion to a feature case that FAILS on base, because every new test must fail at the base commit (T1); ordinary
  legacy behaviour stays in base mode (M3). [T1, T4]
- Status per row: COVERED (a test asserts it), OUT (an exact exclusion sentence, or a demonstrated unreachable case),
  OPEN (in scope, not yet covered: blocks completion), NOT VERIFIED (a hypothesis with the probe it needs) (R2). An
  in-scope obligation never becomes "not tested".
- Nothing the reference's own new docs say becomes a requirement: solvers never see them (vet directory order). [T5]

## 3. Paths, transitions and faults (ledger: Paths; one inventory used by the reference AND the tests)
For each obligation, list every materially different value; the reference handles each, and a test reaches each:
1. **Entry points**: the live path, every saved-replay path, the view WITHOUT the feature's flag, sibling commands
   that share the code (vet: scan, report show with and without --policy, endpoint audit). [T4, S1; A6, most frequent
   Tests band 1 cause] Every read surface of one state (accessors, endpoints, views, commands) is checked in one
   helper, each one the first to look after the change in some test; where the value is the design's choice, assert
   that all surfaces agree (P13: accessor matrix, GET == HEAD == /changes). [T4, S1]
2. **Stores and formats**: every store and serialized form read or written, including older shapes the repo still
   reads and optional fields older versions omit (vet: last, .db, JSON, JSONL, older report). Write through the live
   path, save, reload through that form's real reader, assert the same contract (C04). [T4, S1]
   Duplicates inside one file count too: how the parser merges two entries of one key decides the result (vet
   task 2: a yarn.lock with a vendored and a registry entry of one version kept only the first). Test both entry
   orders: one order passes a "first wins" and a "last wins" merge alike (vet task 2 sweep 2). [S1, T3]
   Check whether the saved form tells "absent" from "empty" (Go `omitempty`, a missing JSON key vs null, protobuf
   defaults): on vet an older report and a new scan with every plugin off both save no control list. Absent metadata
   proves nothing; positive evidence in the data (a finding of that check) does. Platform SQ took a point for
   "missing control metadata treated as proof that checks were disabled". [S1, SQ]
3. **Modes and sibling paths**: every mode, driver, transport, fast path, compiled twin, sync/threaded variant; and
   what exists in one mode only (vet: pull-request-only controls must not count as run in a full scan). A diff or
   pull-request mode is crossed with EVERY change kind (added, removed, modified, upgraded) and its side lookups (vet
   task 2: removed rows counted as live copies; the previous version of an upgrade looked up). [S1,
   T4; B1, main SQ 1/3 cause] A side lookup gets the same multiplicity as the main rule: two rows that share it, with
   different answers, in both orders (vet task 2 sweep 2: the base version of two upgrades took the first row's
   locality; 5 of 7 lanes found it, none of the earlier rounds). [S1, T3]
4. **Transitions**: restart, rebalance/reassign, stop/cancel, in-flight work, continue/resume. For every "before",
   "after", "until", "once", "while": the forbidden intermediate state AND the required eventual state; keep an
   observer active through the transition; plan a too-early, a too-late/never and a finite-cap shortcut (M2). For
   asynchronous behaviour, list the causally distinct event orders and accept every allowed winner (C14). [T2, T3, S1]
   Metadata saved at the start of a run (headers, inventories, enabled lists) must stay current after continue/resume
   with a changed configuration; give it a ledger row, COVERED or OUT with the reason, because every review round
   raises it again (vet: raw AR g1/g2 and the SQ replica High on a resumed scan's header). [S1]
5. **Faults**: for every error path that protects a promise, before writing the reference: which dependency fails,
   what may remain, which result is allowed, who releases the resource (C13). Record every resource, cache, lock and
   iterator lifetime and its invalidation (C27). For a rejection or no-change promise, snapshot every visible side
   effect (stored objects, versions, temporary artifacts, unrelated sentinels) before the rejection and compare after
   (C12). [S1, T4] Per stage, inject the dependency's own error, a foreign exception type, a refusal, and a
   cancellation of the caller apart from a cancellation of the underlying work, one knob per stage. When a batch
   fails or is cancelled midway, grade which items completed and which did not, item by item (P9, codex 3). [S1, T4]

## 4. Discriminators and valid alternatives (ledger: Discriminators)
- For each obligation, name every distinct plausible wrong-rule class and every materially different valid
  alternative that could challenge a pin; counts are observations, not gates (R3). Typical classes: collapse any/all,
  wrong key, overwrite instead of accumulate, one path only, special-case the tested instance, delete-all, skip on any
  failure, header/metadata-only, first-only, presence instead of effect. [FP, T3]
- Give each class the smallest differing input, drawn from these axes:
  - **Multiplicity**: two of a kind sharing scope, never one per scope: two items per topic/partition/file, two rules
    each winning a different item, one rule winning then losing, exact duplicates, two instances of every exemption
    (two plugins off), two sources, and two sources that share a name or identity key (vet: two merged policy files
    with one name give one suppression ref; an FP judge probed it, so decide it in the ledger). [T3; A2 T11 High; vet
    r6, G1, G2, m2, FP panel] Vary the structural count too (three or more tables, partitions, manifests or workers
    where the rule spans them): the platform coverage notes asked for it twice (codex 4). [T4, T3]
  - **Same entity, two names**: an alias, a link, a short and a full id, an equivalent spelling of one construct, the
    same source on both sides (P2, codex 2). [T3, FP]
  - **Order and precedence**: two competing eligible items in both orders; the winner and the non-winner asserted;
    "either is fine" asserted as membership in the allowed set. [T3]
    When code picks one item among several (a copy, a row, a manifest) by an internal key, compute that key and build
    the fixture so the WRONG item sorts first (vet task 2: twice a test passed only because the right item happened
    to sort first, so a half fix looked verified: the first fixture, then a removed row tied with a live copy). [T3]
  - **Exemptions**: both sides in the SAME test with exact counts (exempt `not reported` next to non-exempt `reported
    once`), an unrelated failure that must not widen the exemption, an unknown or stale selector. [T3, S1; vet s1 FP,
    typo]
  - **Negative space**: an object that meets an earlier prerequisite but lacks the decisive event (installed package
    with no finding), empty input, nothing to check, no results at all, an empty replacement input (C07). [T3; vet m3,
    r2]
  - **Regeneration and cleanup**: stale results AND a new result of every kind; old removed, new present once,
    unrelated state kept; repeated with the same and with an empty configuration (C11). [T3; vet r1-r4, delete-all, m5]
  - **Repeat the trigger**: for every "once", "keeps", "stays" or "fails" promise, trigger again and assert no second
    effect, the same failure or the unchanged state (P12). [T3]
  - **Kept results by value**: for every result a promise keeps (a finished lookup, a saved verdict, a stored
    record), assert the kept value in the output, not only that the work was skipped; one assertion per kind of kept
    result (vet task 3: an Auto Review High for a call count with no check that a saved malware verdict survived).
    [T4, T3]
  - **Boundaries and caps**: exact equality and the nearest value on each side, zero/empty where valid; a supported
    large input when it exposes an unsupported cap. Never invent a size or performance limit the text does not state.
    [T3; A4, T12 exact-ms]
- Choose fixture values that separate the classes (sum vs max, n vs n+1, 0, delete-then-0, a second match): each value
  identifies its item by itself (distinct totals, content that names its own item), falsy-but-present values (0, "",
  [], null), and near-miss decoys for every matching rule (prefix sibling, one character off, other case) (P2). Derive
  the expected values from the visible fixture data, with an oracle independent of the reference's private algorithm
  (C16); where an allowed choice decides the outcome, read the expectation from the observed winner or the system's
  own record, and add an end-of-test invariant (each item exactly once, equals a recomputation) (P3). [T3, T5]
- Assert that the scenario really happened before asserting the outcome: every all/any/filtered assertion also
  asserts a non-empty exact count, a case picked from live state asserts it was found, a setup helper fails when its
  own precondition did not happen (P7, codex 1; an AR High on an `all()` over an empty list). [T3]
- Valid alternatives are executed, not only listed: every fix design a reviewer, judge or sweep offers as valid becomes
  a valid-design variant that must pass before its finding closes, and every task runs the standard variant "adds a
  config field that only the production builder sets" (vet task 3: a rollout run did exactly that, the hidden helper
  built the config by hand, and the run was blamed on the task). An exact count needs a sentence that says once or
  exactly; otherwise assert presence (vet task 3: a sweep proposed an exact-count pin and, in the same report, a fix
  that fails it). [T5, FP]

## 5. Fixtures, harness and result contracts (ledger: Fixtures and harness)
- Run the real code end to end; stub only the outermost external system, with the repo's own stub where it has one.
  For every fake, a capability table: the methods, state and events a VALID implementation may use, so the fake never
  decides the design (C15: 46 failures on one task from a coordinator the stub omitted). No fake that bypasses a real
  layer (C1). Build a fake on the dependency's real classes or state machine and add only observation hooks, keep the
  real async boundary and separate completion signals, and name the real behaviour (quirks too) it mirrors (P5,
  codex 6). End every lifecycle a test starts: teardown releases held gates, cancels leftover tasks and routes
  background crashes to the output; an algorithm that may cycle runs under a watchdog (C2, P10). [T5, T8]
- Hold a background worker through observable progress on disk (a trailing regular file that moves last), not a named
  pipe: a pipe holds only until open returns, and a valid design that refuses special files fails it (elio: five pipe
  tests rated T5 High). Keep a pipe only when no other deterministic hold exists, behind a guard that cannot hang the
  test binary. [T5, T2]
- Normalize ambient inputs in the runner (umask, XDG/TMPDIR, editor, hash seed, locale); a fixed seed is not
  correctness for all seeds (codex 5). [T2, T6]
- Generate fixtures with live runs (e.g. `stub fail <backend>`); a hand-made fixture copies the production formats and
  counts exactly. [T5; vet hand-made fixture]
- Build configuration the way production does: where the repo has a builder or constructor for the config, options or
  plugin set a test needs, take the object from it and change only the field under test; a hand-built struct needs a
  recorded reason in the ledger (vet task 3: Vega #4 blamed on the task). [T5]
- A stand-in plugin keeps every interface of the real one except the one the test is about. When it must drop one, its
  comment cites the visible precedent by file:line (an existing test that uses the same kind of stand-in) and the code
  that treats it the same way, so every judge sees the argument (vet task 3: two evaluators split on one stand-in
  without UseSource; the one that found the visible precedent called the test fair). [T5]
- test.sh: base mode = the base-commit tests of every file the reference edits, of every test file either patch
  changes, and of their sibling areas (P15: an AR High for a left-out lifecycle test file), plus the upstream tests of
  every public caller of a changed function: grep the tests for each changed function's name outside the selected
  directories (edsl: question.add_question() wraps Survey.add_question; tests/questions/test_Question.py and test_cli
  TestOpen were left out because selectors were chosen by directory, an AR T1 High in the verification batch); new
  mode = only the hidden
  tests; no fail-fast. Pin every input the base tests use: test files, fixtures, testdata, scripts, catalogs, golden
  files and helper code in test-only packages. A compile-time overlay (`go -overlay`) pins only compiled files; data
  read at run time needs a pinned copy of the tree (safe with a read-only /app). Fail (not warn) if the base commit is
  missing; agent test edits never count (C3; a house anti-cheat rule, not a platform requirement; vet task 3: a
  platform AR T1 Medium for acceptance scripts and a catalog read from the working tree). Prove it with
  `proof.py --tamper` on one pinned data file and one pinned helper. [T1]
- Hidden tests compile at the base commit (exported API only, or added in new mode in the scratch copy), so base fails
  each id for its behaviour, not as one build failure (P14, codex 8). [T8, verify]
- A base test that pins an internal call or the old behaviour: rewrite or loosen it in place into a behaviour
  assertion, with a comment naming the hidden test that now covers it; deselect only when that fails, exactly, with a
  reason, and with a hidden test on the same input (P6). Run the base suite against the reference AND each valid
  alternative to find them (C4). [T1, S2]
- Deselecting a base test does not hide the change from Code Quality: if the reference makes an upstream assertion
  stale, keep the public output unchanged and carry the new state elsewhere, or justify the change in the reference
  (faust task 11: Code Quality Medium on a deselected test). [S2, SQ]
- One scenario or test per independent obligation, never several obligations chained in one script: the runner stops
  at the first failing line, so a run's later failures stay hidden. That blinded the vet re-eval analysis (16 runs, one
  visible failure each) and makes the TQ coverage map coarse. [T8, TQ]
- Report only leaf cases: a grouping node that fails whenever a child fails shows as an extra failed test (Go:
  `go-junit-report -subtest-mode exclude-parents` in new mode; check the runner's equivalent for class or suite
  rows). A group's own failure must still fail the run through the build and zero-cases checks. [T8, verify]
- Predeclare the expected test ids; one failure table: trigger (production build failure, test build failure,
  collection failure, timeout, zero selected, missing or empty report, reporter failure, a result reported twice),
  expected ids, raw diagnostic, exit code. A missing or failed id fails under its own id, also on a build failure (C22;
  vet reports one TestAcceptance case); where ids cannot be predeclared, one synthetic failing case per mode carrying
  the log tail is enough, and a timeout is appended to the partial report as its own case (P1: 9/9 accepted, AR
  praised "fail-safe"). The real status survives every pipe and reporter (C21). Stable unique ids; modes never
  merged (C23). [T8, verify]
- The runner sets its own environment: the toolchain paths, writable scratch HOME and caches, no network. The probe
  runs the literal platform environment (offline, arbitrary uid without passwd, cleared HOME/env); never repair the
  environment in the probe except for values the platform supplies (R5). [T6, verify]
- No elapsed wall time as proof of ordering or as a new latency promise; gates or a controlled clock for that.
  Bounded watchdogs that end a hung test with a real diagnostic are fine (R7). A gate releases a held step only if it
  has not finished, then only the end state is asserted, so waiting and non-waiting designs both pass; "no matter how
  long" is proven by jumping the controlled clock (monotonic and wall together) far ahead (P8, codex 7). Clean new run
  < 300 s; test.sh timeout under the platform kill, or a hung run leaves no partial report (C8). [T2, verify]
- Go 1.25+: a test of a shutdown or late-answer path runs the whole harness inside `synctest.Test`. `synctest.Wait()`
  is the idle event (every other goroutine in the bubble durably blocked); it does not advance the clock. A late answer
  is `synctest.Wait(); time.Sleep(30*time.Second); synctest.Wait()` on the fake clock; guard deadlocks with a fake
  `time.After(time.Hour)`. When a library keeps timers after Close, register a one-second sleep in `t.Cleanup` first
  inside the bubble. Mutexes, I/O and channels made outside the bubble are not durable (goka: platform T2 finding, gone
  with the bubble). [T2]
- No leak words (challenge/quest/olympus/Shipd), no process words, no stray build outputs; test files unique and named
  in the repo's convention (a short hash suffix by default); `./test.sh` committed with mode 100755. [prechecks]
- Hidden-test helpers carry the file's hash suffix too (burrow-silences: an unsuffixed helper clashed with solver code
  on 4 of 8 runs). Go: never range over a map to create subtests, and never call Fatalf on a parent t from inside
  t.Run; both change which ids the unsolved state reports from run to run (Burrow #751). [T1, T2, verify]

## 6. Implement tests and reference against the ledger
Tests:
- Assert every promised semantic field, identity, multiplicity and effect. Pin wording, formatting or order only when
  the description or an identified repo convention requires it. Allow unpromised extra metadata; never allow extra
  prohibited results, duplicate effects or stale state (R4). [T7, T3]
- A reported success or diagnostic is not proof of a separately promised state change: assert the effect at its
  observable sink (M1). A recorded request is not the sink either: also assert the data it fetched reaches the
  result (vet task 2 sweep 2: continue tests checked only that the version was asked for). [T3]
- Test setup is design-free: a stop point, a wait or a counter in the setup must not depend on how a valid design
  processes the case (vet task 2: a continuation test stopped on enrich progress, which a valid design never
  reports; stop at a stage boundary instead). [T5]
- Where an optional invalid input competes with existing error behaviour, grade the promised invariant and leave the
  precedence free unless the text or repo fixes it (C31: swift 412-over-413 FAIL_TEST_MISMATCH x5). [T5]
- An assertion with a second reading never stands alone. The same script holds neighbours showing the rule in both
  directions and the no-change cases; a comment directly above the assertion quotes the description sentence and
  states this case only (it prints in the failure log), with no framing word the description lacks; for an implied
  case the comment also gives the repo file:line that decides it and the one-line reasoning from the sentence to
  this outcome (vet direct-deps: platform verifyFairness flagged 3 cases of one implied assertion until the reason
  sat next to it); the test name says
  what is checked. Reword any other comment that reads as a contradicting rule (vet task 2: 5 runs blamed on the task
  became 0 with the same behaviour under test). [T5]
- At every assertion with an unpromised part, accept the allowed set explicitly (membership, sorted compare,
  `None or <=`) and say so in a comment; leave the failure surface (raise, false return, logged error) free unless the
  text fixes it, and grade only the effect (P4). [T5, T7]
- A test that came from a probe pins what the reference happens to do. Before it ships, rewrite it outcome-only: assert
  what the description states, drop author-choice records and fields, and accept every reading a reader marked unclear
  (faust task 7: Test Quality FAIL, 1 of 27 unfair). [T5, T7]
Reference:
1. The change sits in the layer that owns the concern, passes data through existing interfaces and reuses the repo's
   helpers and formats. Read the header comments of every file you edit: they hold local rules (vet task 2: scanfile.go
   "rows hold the record JSON next to the columns that queries filter on" -> a JSON filter cost Code Quality). List
   every caller and consumer of a function whose result changes, and keep or decide each one's contract (vet task 2:
   a new copy rule changed what the local code-usage enricher received; a one-line report merge fix broke the
   report's per-manifest reload, which every verification round then flagged). This holds for "cheap" Low fixes too.
   New interface methods keep unaffected implementations working by the language's own
   mechanism, and any default or fallback is proven safe for its real callers (R6). [S2, S3]
   Correctness never depends on a cross-module call order a reader cannot see in the patch; decide at the owning
   boundary from the event itself (faust task 10: 3 of 5 SQ runs read a store hook as post-write). [S1, SQ]
2. Every path, store, mode, transition and fault in the Paths section is handled, or excluded by a scope sentence.
   [S1; B1, B3]
   Promised entry points leave the same stored state: an asymmetry is never parked as "not observable through the API".
   For every internal sub-request a fix issues, list which handler runs and what it writes (swift: SQ 2/3). [S1]
3. Unknown, stale, optional and unsupported states behave as the contract and the repo's conventions require; trace
   fallback evidence to its authoritative source; an in-scope promise never silently degrades to a no-op (R6; vet
   typo, older report). A mode the text excludes keeps its exact old path behind one explicit check with a comment;
   a sibling driver the feature does not support fails with a clear error naming the supported one (P11: SQ praised
   both). [S1, S2]
   Rejection ledger: every branch that rejects an input -> the input that reaches it -> the sentence that excludes it, or
   proof the base rejects it too. A row with neither: make the shape work, do not narrow it (turso: SQ 1/3 three times).
   When test.patch removes an old-behaviour test, add a positive feature test in the same file. A Medium inside a broad
   promise is not parked because an upstream test pins nearby behaviour until a gated fix was tried and failed (swift
   SQ 1/3). [S1, SQ]
4. No hand-made tables of repository knowledge unless derived from code (vet per-plugin data map). [S1, S4]
5. No kept residuals inside a promise, no excuse sentences; "the repo does the same" is no defense: fix it or cite the
   sentence that excludes it (B5: SQ 1/3-2/3 on 5 tasks). [S1]
6. Every heuristic or threshold has its smallest breaking input in Discriminators (B6). Never weaken the reference to
   keep a passer (B7). Nothing out of scope, no unrequested cleanup or churn. [S1, S3]
   The reference implements the widest literal reading of each promise. Sweep every any/all/every/like in the text: is
   it general, or a hand-picked list or count rule? A heuristic never rejects a case the text names (elio: SQ 1/3). [S1]
7. Code quality the repo enforces: its formatter and CI linters, no dead parameters or unused variables, comments
   that state what the code does, docs/glossary/CHANGELOG consistent with the code when the repo keeps them or the
   change touches them, line width as the file. [S4, SQ]
8. The repo's own review rules (REVIEW.md, CONTRIBUTING, AGENTS.md): read them before writing the reference and
   follow every rule the change touches. The platform SQ applies them (vet task 2: Code Quality 1/3 for no regression
   test, REVIEW.md rule 4; rule 8 asks a user guarantee to bring an acceptance script and a catalog row). When those
   rules ask for it, the reference carries its own regression test in the repo's style, in files the hidden tests do
   not touch; 8 of 9 accepted packages without such a rule had none. [SQ, S2]

## 7. Export and prove (ledger: Evidence)
- Export the patches from explicit paths; check the file list, modes (`test.sh` 100755), applicability in grading
  order on a clean pinned tree, and no test/solution overlap; run through `./test.sh`; record against the exported
  patch hashes (M6). [verify, prechecks]
- Never `git clean` the working tree: it deletes untracked new solution files. Use a disposable copy (Burrow #751).
- The four cells on the pinned source, as the completion gate: base-mode on base PASS, new-mode on base FAIL for every
  expected id, base-mode on the reference PASS, new-mode on the reference PASS, with exit codes, parseable JUnit,
  exact ids and real failure output; no skips or unexplained missing/extra ids. Then every failure branch of the
  harness table separately (M3). [T1, T8, verify]
- Run the wrong-rule variants and the valid alternatives. For each, record the exact diff and its state: APPLIED,
  RESTORED AWAY (the restore step removed it), DID NOT APPLY, EXECUTED; only an executed variant with its intended
  diagnostic counts. Rebuild compiled twins from the candidate source and check which binary/module was loaded (M4).
  [FP]
  Rust: `docker cp` keeps host mtimes, so cargo can skip the build and run the old binary; `touch` every copied source
  first (turso: a false 40/40). Also run one variant carrying several defects at once: a human reviewer builds one with
  about six and shows the suite passes it. Where a sentence says "like X" or "follow X", diff the reference against X.
  [FP]
- Disposition of every survivor: grounded defect -> OPEN until a fair test or a reference fix closes it; valid choice
  -> keep it passing; legitimately OUT -> its exclusion; NOT VERIFIED -> the probe it needs. Never close a finding as
  "already caught" without running its variant (vet: the installed-package design was called caught and was not).

## 8. Review and close
- The sweep reads the ledger as traceable evidence and challenges its premises independently; it does not just
  confirm the builder's decisions.
- Audit the available passing and near-miss solver patches against the contract; reproduce grounded gaps, add the
  smallest discriminator, replay current valid alternatives and passers. Do not launch extra solver batches only to
  feed the ledger (M5).
- Run every false-pass probe on the reference too, as the platform adjudicator does: a probe the reference also fails
  is a reference gap (fix it or record it OUT), not a discriminator. On vet the panel dropped a judge's FP for exactly
  this reason, while local auditors that skipped the step were stricter than the platform. [FP]
- On any edit, mark dependent evidence stale and re-run the affected proof after the repair batch; never treat an old
  PASS or a summary label as current proof (M5).
- After each task, classify every reproduced finding: missing rule, existing rule not executed, unclear wording,
  harness defect, or out-of-scope suggestion; amend or merge the existing rule instead of appending a duplicate; track
  later findings, false alarms and effort per task. The sweep count is decided from that data with the user, not
  from a fixed threshold (R8).

## 9. Rule map (platform rubric, verbatim 2026-10-04)
| Rule | Rubric text (short) | Secured in |
|---|---|---|
| T1 | 100% fail at the base commit, 100% pass after the solution | 2 (keep-behaviour coupling), 5 (restore, deselects), 7 (four cells) |
| T2 | deterministic: no timing, randomness, ordering | 3.4, 5 (no wall time as proof) |
| T3 | strong tests, not permissive | 4 (discriminators), 6 (effect at the sink) |
| T4 | extensive coverage of the behaviour and obvious edge cases | 2 (atomic obligations), 3 (paths), 4 |
| T5 | no unspecified or undiscoverable behaviour | 2 (grounding, no reference-doc rules), 4 (oracle), 5 (fake capabilities), 6 (second reading, competing errors) |
| T6 | no network | 5 (environment) |
| T7 | no over-pinned output | 6 (contract-relative pins) |
| T8 | failure diagnostics intact | 5 (failure table, expected ids, status), 7 |
| S1 | meets all requirements | 2, 3, 6 (reference 2-6) |
| S2 | no regressions, existing patterns | 5 (base mode), 6 (reference 1) |
| S3 | no irrelevant changes | 6 (reference 1, 6) |
| S4 | no AI-generated artifacts | 6 (reference 4, 7) |
| TQ (fairness, coverage) | per-test fairness, requirement coverage | 2, 4, 6 (tests) |
| SQ (comprehensiveness, code quality) | | 3, 6 (reference) |
| FP panel | a pass that misses a stated requirement | 4, 7 (variants, dispositions), 8 |
| Verify | tests fail without / pass with, stable, offline uid | 5, 7 |

## 10. Never (unfair or wasteful)
Pin helper names, call counts, internal maps or file counts (never GRADE an internal; a harness wait or setup hook
on repo-visible state is acceptable, rated "repo-discoverable" on 4 accepted packages); turn a surviving variant into a finding without a
concrete failing scenario; pin behaviour only the reference's own docs state; force a race winner or error precedence
the text does not state; grade unstated sizes, budgets or performance; build the full cross product of the axes (one
case per distinct entry, form and guard, plus the interactions that expose a plausible wrong rule); copy another
task's harness exclusions or fallbacks verbatim (port the intent, prove it here).
