# Tests, harness, test.sh, Dockerfile (S3)

Platform view: verifyFairness labels each test Prompt-stated / Repo-discoverable / Standard external semantics (or
unfair) with concerns internal_coupling / timing_sensitivity / overfit_single_point; Auto Review T1-T8 promotes a
coverage gap to High when a realistic wrong design passes; verifyFlakiness runs 6 x unsolved + 6 x solved;
verifySolution runs as a uid without a passwd entry (`offlineUidPassed`) and through Harbor.

## 1. Test design
- One or more tests per requirement row of the variant table. Name tests after the outcome
  (`test_a_time_just_after_a_message_<hash>`); add a 4-6 char hash suffix to every test name and test file name
  (predictable names fail a precheck; helper names collide with solver code).
- Two-sided boundaries: too early / exactly / too late (or never); below / at / above. A test that only checks one
  side lets a wrong design pass (AR T3/T4).
- Assert the observable outcome the sentence names: final state, emitted records, returned status, what a fresh
  reader sees. Never private fields, internal call order, mock call targets, log text, exact messages (unless stated).
- Non-empty guards and exact cardinality (`assert items` before `all(...)`; window v24 `all([])` was an AR High).
- When the sentence promises two effects (both errors reported, rollback and 412), assert both.
- Multiplicity: at least one test with several users of one resource (two readers of one topic, two writers of one
  key) whenever the sentence covers it (T11 AR High: same-topic mixed-policy fan-out untested).
- Every stated mode through its real path (threaded producer through the real ThreadedProducer, not a replaced
  send_soon: T5 AR tests band 1).
- A test that starts a lifecycle completes it (on_rebalance_start -> end).
- No wall-clock windows deciding an outcome: events, futures, explicit handshakes; keep only an outer timeout.
- Never test what the description leaves open or what you contested.

## 2. Harness
- Real framework objects end to end (app, worker, consumer, store, table); fake only the network edge at its
  connection layer (broker at create_conn, HTTP at the transport), with the real library's state objects inside
  (aiokafka SubscriptionState / TransactionManager; FakeKafka lacking `_txn_manager` gave FAIL_TEST_BROKEN).
- Fake every construction path solvers can use (app.producer and transport.create_producer).
- Before calling an event impossible, trace it through the real classes per mode (task 5 called late acks impossible
  twice and was wrong twice). The harness must not produce events the real framework rules out.
- No short framework timers (faust 0.2 s commit interval -> livelock check CancelledError).
- Fail-safe reporting: a collection/build/timeout failure becomes a named failing JUnit case with the diagnostic.

## 3. test.sh contract (templates/README.md: one accepted test.sh per language)
- `bash test.sh --output_path <xml> base|new`. base = the existing tests that guard the touched code (include the
  lifecycle test files of anything you change; dropping app/test_base.py was an AR T1 High); new = only the added
  test files.
- Grades in a scratch copy with the base-commit test files and pytest/go config restored, plus the hidden test files
  (agents edit graded tests: PASS_CHEATED on 4 tasks). Deselect only base tests every correct solution must break,
  by exact node id (pytest --deselect is a prefix match: use the full id), each with a comment naming why.
- Hard timeout below the platform kill (~600 s); clean `new` run under 300 s.
- No process words anywhere in test.patch ("graded", "hidden", "platform", "solver", "reference": AR Tests 0/3).
- Mode 100755 for test.sh in the patch.

## 4. Dockerfile (templates/README.md)
- `FROM public.ecr.aws/d3j8x8q7/olympus-base-<lang>:latest` (every accepted package).
- Builds from the checked-out repo context (the platform deletes .dockerignore and builds at the pinned commit).
- Pins every dependency to exact versions that resolve offline later; Python: editable install of the repo (or a
  documented test invocation); faust: Cython build of the extensions.
- Never runs tests (even `go test -run '^$'` failed a precheck).
- Base commit = upstream tip at S0 ("image failed to rebuild from your committed source" = upstream moved: re-base).

## 5. From the other machine's tasks (platform-recorded)
- One focused test per requirement sentence, named after it; it loops the full scope the sentence names (every
  route x setup). TQ coverage maps sentence -> test by name; big mixed tests get "partial".
- No conditional oracle (`if status == 412: assert ...`): every check unconditional or bounded. No permissive status
  sets ("200 or 412" was a High). Assert the exact resulting state.
- Public API surfaces (typings, ESM/browser builds, CLI) are stated surfaces: untested typings drew 3 x T4 High.
- Every reference hunk is executed by some test; a hunk you can remove with no test failing is a T4 finding.
- test.sh exports its own toolchain env; the platform runs it without the image ENV (turso: T6 Blocker, 2176 failures
  as uid 4242).
- After applying the patches as root, run once as another uid: patched files become root 0644 (build EACCES); remove
  generated outputs before rebuilding them in test.sh. Re-eval agent patches carry no dist/: tests that read generated
  output rebuild it in test.sh.
- Before keeping an assertion ask: if a strong run fails only this, would the run judge call it a missed requirement
  (a sentence says it) or FAIL_TEST_MISMATCH (agentBlameUnfair)? The second is an unfair test.
- Run the suite 6 x unsolved + 6 x solved once before the first paste (the platform's verifyFlakiness method; two
  tasks failed it).
- Run test.sh once with a clean environment as a numeric uid (`env -i PATH=/usr/bin:/bin` as uid 1000): it must set
  everything it needs itself (turso T6).
- Grep the repository's own tests before pinning a value; where the repo pins another answer and the description is
  silent, accept both (swift TQ FAIL 1/11 -> PASS).
- Do not change or remove existing tests in test.patch (it cost Code Quality 2/3 on turso); deselect by exact id with
  a reason instead.
- JUnit testcase ids stay the same across runs (a parser that varied them failed Verify Flakiness).
