Verdict: the checklist already covers most of what the 9 accepted packages do; 15 generic patterns sharpen it (2 are new), and 6 lines are stricter than anything the platform required (keep 2 as house rules, make 4 conditional).

# Checklist gap study: 9 accepted packages vs build-checklist.md (design-session lane, oss70)

Method: three read-only agents walked the checklist against 3 packages each (task.md, test.patch, solution.patch,
Dockerfile, view.json extracted by script); I grouped their findings. Line numbers are patch-file lines ("~" =
approximate, from the agents' reading). Short names:

| short | id | package |
|---|---|---|
| WIN | kh7dhbz3xacbq8sabp3jeknda18g21m4 | faust windowed table expiry |
| BUF | kh7ephrm9ghwxpqwpws23j89b18g7jvb | faust commits with buffered changelog |
| EOS | kh73rbw2dez349t18dh4jzqb658g8xz6 | faust exactly-once changelog offsets |
| RUN | kh70afkwq3q1ha6zh6j1grgy7n8gchz4 | faust streams that start/stop at run time |
| SBY | kh7dvvpbmrbz4c4k3n6t1k4etn8gq1rr | faust standby promotion |
| VIS | kh7bfzrhqdc4m97ez8gspb9hw98gtx2v | faust table visibility after a rebalance |
| DKR | kh7d92724bxpen4jfa3gmx09a58gsj6n | oss-rebuild (Go) docker proxy file changes |
| TUR | kh717sntzsjbhhmm8grsw7g3r18gys98 | turso (Rust) NOT IN in materialized views |
| ELI | kh7aemqd7daac1c9fy2xcdte3h8h0vty | elio (Rust) history after rename or move |

Platform results: AR 3/3/3 on 8 of 9 (WIN's latest AR was revision_requested, tests band 1, two Highs, yet accepted
by the human reviewer); SQ 3/3 with no issues on all 9; TQ 8/8 on all 9; 0 unfair tests on all 9.

## 1. Checklist walk (per section; SHOWN / NOT NEEDED / MISSING-BUT-ACCEPTED)

| Section | WIN | BUF | EOS | RUN | SBY | VIS | DKR | TUR | ELI |
|---|---|---|---|---|---|---|---|---|---|
| 2 obligations, keep-behaviour coupled to a base-failing case | S | S | S (526-554) | S (1027) | S (736) | S (904) | S (~2186) | S | S (~1126) |
| 3.1 entry points | S (stop/revoke 1512) | S (393-957) | S (478-680) | S | S | S (accessors 759-812) | S (1259, 1714) | S (~53) | S (420-584) |
| 3.2 stores/formats | S (memory+rocksdb 653) | NN | partial (no fresh store; platform suggestion) | NN | S (232-271) | S | S (~1960, ~2855) | S (~1246) | NN |
| 3.3 modes/siblings | S (641) | excluded by text | S | S (Python+compiled 851) | S | S (917) | S (1459) | S (~921) | S (~956) |
| 3.4 transitions | S | S (491-535) | S (725-984) | S (1983-2649) | S (914-1169) | S (1468-1498) | S (1537-2095) | S (~608-2037) | S (44-310) |
| 3.5 faults | NN (out of scope) | S, wider (462-489, 848) | S (632-722) | S (2572) | - | - | S (~1835) | S (rollback) | S (~743) |
| 4 discriminators | S (705, 1413) | S (407-424) | S (880-892) | S (2185-2461) | S (783-839) | S (1344, 1442) | S (~1856-2858) | S (148-1794) | S (~1373-1515) |
| 5 base-test restore, fail if missing | M (none) | M (none) | M (none) | M (none) | M (warn fallback 61-72) | M (warn fallback) | M (none) | M (none) | M (none) |
| 5 predeclared ids / failure table | M (one synthetic case) | M | M | M | M | M | S (~3166-3200) | S (~2429-2479) | S (~1909) |
| 5 one obligation per test | S | S | S | M (869-921) | M (884-910) | S | S | M (long scripts) | S |
| 5 timeout under platform kill | M (1500 s) | M (1500) | M (1500) | M (1500) | M (1500) | M (1500) | M (10 min) | M (3600) | M (3000) |
| 5 hash-suffixed test files | S | S | S | S | S | S | S | M | M |
| 6 tests: effect at the sink | S | S | S (788-805) | S | S | S | S (~2140) | S | S |
| 6 ref 7: CHANGELOG/docs | S (sol 8-16) | M | S (sol 9-13) | S (sol 1-55) | S | M | header TODO only | S (3 doc layers) | M |
| 6 ref 8: own regression test | M | M | M | M | M | M | M | M | M |
| Never: no internal pins | M (on_recovery_completed 1594, fairness "internal_coupling", fair) | S (removed call-count pins) | M (active_offsets 802, private attrs 337) | S | M (waits on standby_offsets 503) | M (_current_event 653) | S | S | nuance (crate-internal API at base) |

S = shown, NN = not needed, M = missing but accepted. Section 7/8 are process steps: view.json shows verifyTests
100% fail on base, offline-uid PASS (except TUR: offlineUidPassed=false, still accepted) and stable flakiness runs.

## 2. Generic patterns (ranked by packages)

### P1. Every harness failure is a named failing case (9/9)
- **Rule:** a missing report, zero cases, a timeout, a build/compile failure and a reporter failure each become an
  explicit failing JUnit case carrying the log tail, and the runner's real exit status survives every pipe. When the
  ids cannot be predeclared, one synthetic case per mode (e.g. `harness/new`) is enough; a timeout is appended as its
  own case to the partial report.
- **Evidence:** faust template in WIN/BUF/EOS/RUN/SBY/VIS (`PIPESTATUS[0]`, `tests="0"` -> synthetic case; RUN
  `harness/time_limit` 144-166, `setup/build_ext` 168-190); DKR per-declared-id build failure + "no tests ran" guards
  (~3166-3200); TUR skipped = failure, runner-nonzero guard (~2469-2479); ELI `cargo_test_incomplete` (~1913), a
  result reported twice fails if either failed (~1895). AR praised it as "fail-safe rather than masking" on 7 packages.
- **Step:** 5, SHARPENS "Predeclare the expected test ids; one failure table" (allow the synthetic case, add timeout
  and duplicate-result rows).
- **Protects:** T8, verify.

### P2. Fixture values that identify, and one identity under two names (7/9)
- **Rule:** make every fixture value tell the wrong rule apart by itself: injective values (each item a distinct
  total), content that names its own item (a file holds its own path), falsy-but-present values (0, "", [], null),
  near-miss decoys for every matching rule (prefix siblings, one character off, other case), and the same entity
  reached through two names (alias, link, short and full id, equivalent spelling of the same construct, the same
  source on both sides).
- **Evidence:** VIS injective totals (1442), delete then 0 (935); ELI content-as-identity (362-364, ~684), prefix
  sibling (~1515), swap a<->b (~1373); RUN decoy names `xorders-eu`, `AUDIT` (2243-2461); WIN falsy 0/[]/"" (1413-1449)
  and the AR Medium for the missing JSON null; DKR id by name/short/full//v1.43 (1259, 1714), sibling with shared
  prefix (~2022), two write paths to one file (~1856); TUR same table on both sides (~554), `NOT (x IN ...)` (~53,
  AR: discoverable). Fairness praised ELI's content-based discovery and its prefix "negative control".
- **Step:** 4, SHARPENS "Choose fixture values that separate the classes" and the Multiplicity axis ("two sources
  that share a name or identity key").
- **Protects:** T3, FP, T4.

### P3. Expected values come from what happened or from a system of record, plus invariants (6/9)
- **Rule:** where the outcome depends on an allowed choice, derive the expectation from the observed winner or from
  an independent record of the system (the log, the planner's state, the system's own recomputation), and add a
  global invariant checked at the end of every test (each item exactly once across owners; every persisted value was
  committed; the result equals a recomputation from scratch).
- **Evidence:** EOS `(committed,) = cluster.committed` (718-721), `check_persisted_offsets()` after every test
  (361-365, fairness "useful co-assertion"); VIS oracle from `Changelog.latest()` + assignor (269-298, AR praised),
  `Counter` conservation (880-884); SBY `assert_balanced`, furthest-along invariant (650-686); WIN cluster-wide close
  list (187-283); TUR `@verify-materialized-views` (line 10) plus explicit rows; DKR endpoints agree (~2700). Platform
  suggestion on WIN: an independent before/at/after oracle (its test reused production's `window.stale`, 1352).
- **Step:** 4, SHARPENS "Derive the expected values from the visible fixture data, with an oracle independent of the
  reference's private algorithm".
- **Protects:** T3, T5, T2.

### P4. Unpromised parts are left free on purpose, with the allowed set written at the assertion (6/9)
- **Rule:** at every assertion with an unpromised part, accept the allowed set explicitly (membership, sorted
  compare, `None or <=`) and say so in a comment; leave the failure surface (raise vs a false return vs a logged
  error) free unless the text fixes it, and grade only the effect.
- **Evidence:** RUN raising message excluded (2734), "how its stop call ends is up to the worker" (2157), `None or <=`
  (2639); BUF `commit_or_fail` accepts a raise or False (385-390); EOS commit helper swallows the exception (486-488);
  SBY `ahead in (0, 1)`, tie as membership (735); DKR allowed readings in comments (~2700); ELI two allowed locations
  (~280). Fairness praised these as avoiding order assumptions.
- **Step:** 6 tests, SHARPENS "Allow unpromised extra metadata" and "One-line reading risk".
- **Protects:** T5, T7.

### P5. Fakes are built on the real dependency and only add observation (5/9)
- **Rule:** build each fake by subclassing or composing the dependency's real classes or state machine, so illegal
  call orders and bad arguments fail as in production; add only observation hooks; keep the real async boundary
  (acknowledge a loop turn later, deliver queued sends in order); name in a docstring the real behaviour each fake
  mirrors, including documented quirks.
- **Evidence:** EOS on aiokafka `TransactionManager` (125-240), MemoryStore subclass (286-301), docstrings (108-118);
  RUN subclasses `SubscriptionState` (344-406), real `TypeError`/`ValueError` (564-592); VIS ack via `call_soon`
  (453-479); WIN FIFO future (109-134); DKR stateful daemon model with the overlay's "modified" quirk (384-990).
- **Step:** 5, SHARPENS "For every fake, a capability table".
- **Protects:** T5, FP.

### P6. Base tests that pin old behaviour or internal calls are rewritten, not only deselected (5/9)
- **Rule:** when a base test pins an internal call or the old behaviour, rewrite or loosen it in place into a
  behaviour assertion (or let mocks answer idempotent reads, compare decoded URLs), with a comment naming the hidden
  test that now covers it; when a base test must be deselected, a hidden test pins the new behaviour on the same input.
- **Evidence:** BUF rewrote `flush.assert_called_once_with` pins (115-166); RUN edits with a comment per hidden test
  (211-249); DKR mocks answer repeated reads, `requestKey` decodes (171-334); TUR converted the rejection test into a
  feature test (2210-2253); VIS guarded exact-text mock repair in the scratch copy (85-145). Platform suggestion on
  RUN: a focused test for the deselected base test's behaviour.
- **Step:** 5, SHARPENS "Exact deselects with a reason for base tests that fail on a correct design".
- **Protects:** T1, S2, T5.

### P7. Assert the scenario exists before the outcome: non-empty quantifiers, discovered cases (4/9)
- **Rule:** every `all`/`any`/filtered-list assertion also asserts a non-empty, exact count; a case picked from live
  state or a dry run of the real planner asserts that it was found; a setup helper fails if its own precondition did
  not happen.
- **Evidence:** WIN AR High T3/T4: `all(close == ... for close in others)` passes on empty (1406-1408); SBY
  `next(...)` + `assert scenario is not None` (947-963); VIS `planned_roles` asserts each role exists (1169-1197);
  DKR `start()` fails if the proxy did not patch (1066-1083).
- **Step:** 4, SHARPENS "Assert that the scenario really happened before asserting the outcome".
- **Protects:** T3.

### P8. Design-free waits: adaptive gates and clock jumps (4/9)
- **Rule:** a gate releases a held step only if it has not finished, then the test asserts only the end state, so a
  waiting and a non-waiting design both pass; to prove "no matter how long", jump the controlled clock (monotonic and
  wall together) far ahead instead of waiting; a mid-state may be tolerant while the end state is strict.
- **Evidence:** WIN adaptive gate (982-989, 1290); BUF one-year jump (346-383, fairness praised); VIS `loop.time` +1
  day (516-522); ELI tolerant mid-state, strict Back chain (~66). Fairness `timing_sensitivity` concerns on wall-time
  deadlines in WIN, SBY, VIS, ELI (concern, not unfair).
- **Step:** 6 tests + 5, SHARPENS "Test setup is design-free" and "No elapsed wall time as proof".
- **Protects:** T2, T5.

### P9. Faults include foreign errors and cancellation at each stage (4/9)
- **Rule:** inject, per stage of the pipeline, the dependency's own error, a foreign exception type, a refusal, and a
  cancellation of the caller separately from a cancellation of the underlying work; one knob per stage; "keeps
  failing" is checked by triggering twice.
- **Evidence:** BUF knobs `hold/hold_ack/reject/refuse` (210-235), `TypeError` (848), caller vs delivery cancellation
  (427-489; AR: agents "treated the caller-facing future as authoritative"); EOS fenced/failed/aborted/nth commit
  (632-999); ELI source removed, cancel mid-paste (~743, ~238); RUN processor raises (2572).
- **Step:** 3.5, SHARPENS "which dependency fails, what may remain".
- **Protects:** S1, T4.

### P10. Tests cannot hang the run: watchdogs and full teardown (4/9)
- **Rule:** a synchronous algorithm that may cycle runs under a thread/process watchdog that fails with a diagnostic;
  teardown releases every held gate, cancels leftover tasks and routes background crashes to the test output.
- **Evidence:** SBY `finishing()` watchdog (622-643, AR praised; near-miss runs did cycle), task cancel (552-604); BUF
  teardown releases gates (363-367); ELI Drop guard + watchdog (188-232); EOS `report_crash` (304-306).
- **Step:** 5, SHARPENS "End every lifecycle a test starts" and "Bounded watchdogs ... are fine".
- **Protects:** T8, T2.

### P11. Excluded modes keep the old path behind an explicit gate; unsupported siblings fail loudly (3/9)
- **Rule:** in the reference, a mode the text excludes keeps its exact old code path behind one explicit check
  (stated in a comment), and a sibling driver the feature does not support fails with a clear error that names the
  supported one, never a silent partial behaviour.
- **Evidence:** BUF gate (sol 161-200), SQ praised "preserves the old behavior for the explicitly excluded ...
  branches"; WIN `_follows_ownership` "keep expiring exactly as they always have"; RUN confluent `NotImplementedError`
  (sol 2597-2625), SQ accepted it as in scope.
- **Step:** 6 reference, NEW (next to reference 2-3).
- **Protects:** S1, S2, SQ.

### P12. Repeat the trigger (3/9)
- **Rule:** for every "once", "keeps", "stays" or "fails" promise, run the trigger one more time and assert no second
  effect, the same failure, or the unchanged state.
- **Evidence:** WIN `await c.expire()` twice (670-671); BUF flush twice for "keeps raising"; ELI Back fails twice with
  cwd unchanged (~1138-1146).
- **Step:** 4, SHARPENS "Regeneration and cleanup ... repeated with the same and with an empty configuration".
- **Protects:** T3.

### P13. Every observer of one state is checked, and each one is the first to look (3/9)
- **Rule:** list every read surface of the same state (accessors, endpoints, views, commands) and check them in one
  helper; vary which observer acts first after the change; where the value itself is the implementation's choice,
  assert that all observers agree.
- **Evidence:** VIS accessor matrix keys/items/values/len/in/[]/get inside and outside an event (759-812, AR praised
  "read-surface breadth"); DKR HEAD-first / archive-first / changes-first (~2195-2566), GET == HEAD == /changes
  (~2700, fairness praised); WIN worker order reversed (775, 1397).
- **Step:** 3.1, SHARPENS "Entry points".
- **Protects:** T4, S1.

### P14. Hidden tests compile at base and fail per id on behaviour (2/9)
- **Rule:** write the hidden tests against API that exists at the base commit (an external test package, or tests
  added only in new mode in a scratch copy), so the base run fails each id for its behaviour, not as one build
  failure.
- **Evidence:** DKR external package importing only exported API (all 93 compile at base); ELI `#[path] mod` appended
  only in new mode (1756-1760).
- **Step:** 5, NEW (the failure table handles a build failure; this avoids it).
- **Protects:** T8, verify.

### P15. Base mode runs the tests of every edited file and its neighbours (1/9 + an AR High)
- **Rule:** base mode includes the existing tests of every production file the reference edits and of every test
  file the reference or test.patch changes, plus the sibling areas the reference touches.
- **Evidence:** WIN AR High T1: base mode left out `tests/unit/app/test_base.py` while the reference edits that
  lifecycle code (sol 537+); TUR base mode runs the optimizer sibling corpora (~2290-2356).
- **Step:** 5, SHARPENS "base mode = the base-commit tests of every package the change can affect".
- **Protects:** T1, S2.

## 3. Checklist lines no accepted package needed (possible over-requirements)
| Line | Accepted packages | Recommendation |
|---|---|---|
| 6 ref 8 "The reference carries its own regression test" | 0/9; SQ noted "no author-side tests" on TUR/ELI without penalty | Make conditional: only when the repo's REVIEW.md/CONTRIBUTING asks for it (the vet task-2 penalty came from such a rule) |
| 5 "Restore the base-commit test files ... fail (not warn) if the base commit is missing" | 0/9 fail; 6 no restore, 3 warn | Keep as a house anti-cheat rule; mark "not required by the platform" |
| 5 "test.sh timeout under the platform kill" | 0/9 (1500-3600 s); their clean runs were short (52-268 s on SBY/VIS/RUN) | Keep (revised after reading the Codex lane): a test.sh whose own timeout is above the platform kill writes no partial report when a run hangs (task 11: no junit after 688 s); the accepted packages only show that short runs never hit it |
| 5 "One scenario or test per independent obligation" | RUN/SBY/TUR chained and passed TQ 8/8 | Keep as a house rule for re-eval analysis; not a platform requirement |
| 5 "Predeclare the expected test ids" | Python 6/9 used one synthetic case | Allow the synthetic per-mode case (P1) |
| 6 ref 7 "docs/glossary/CHANGELOG consistent" | 5/9 added docs; 4 did not, unflagged | Conditional on a repo convention (keep "consistent if touched") |
| Never "Pin ... internal maps" | 4/9 wait on or read internal state; fairness "Repo-discoverable" | Sharpen: never GRADE an internal; a harness wait or a setup hook on repo-visible state is acceptable |

Platform warnings present on accepted packages: Harbor "NOT offline-buildable" (all 9) and TUR offlineUidPassed=false
were accepted; they are not evidence that those checks can be ignored on new tasks.

## 4. Agree / disagree with the Codex lane (codex.md, read after sections 1-3 were written)

Same pattern, both lanes (merge as one rule):
| Codex | This report | Note |
|---|---|---|
| 1 nonempty outcomes before universal assertions | P7 | same evidence (WIN AR High, DKR start(), SBY/VIS discovered cases) |
| 2 equivalent representations and aliases | P2 (second half) | I also fold identifying fixture values into it |
| 6 separate lifecycle completion signals in fakes | P5 + P9 | same BUF/EOS evidence |
| 7 permanent clock jump (Codex: 1 package) | P8 | I count 2 (BUF one year, VIS `loop.time` +1 day) |
| 8 hidden tests compiled in private scope via a scratch tree | P14 | I add DKR's external-package variant; both say "compile at base" |

Codex has, I missed (agree, add them):
- **Codex 3, partial completion graded per item** (EOS, BUF, ELI, DKR): when a batch fails or is cancelled midway,
  assert which item effects completed. Stronger than my P9, which only covers injecting the faults.
- **Codex 4, structural cardinality variation** (SBY, EOS, RUN artifacts plus two platform coverage suggestions: 4+
  tables on SBY, 7 partitions on VIS). This is the best-supported gap: the platform asked for it twice. I saw the
  suggestions but did not make them a pattern.
- **Codex 5, ambient inputs normalized** (ELI umask/XDG/TMPDIR/editor, VIS PYTHONHASHSEED, RUN scratch build). I had
  the evidence but not the pattern; agree, including its caveat that a fixed seed is not all-seed correctness.
- **Over-requirements:** the hash-suffix line (TUR and ELI use descriptive names and kept tests band 3) -> "unique and
  in the repo's convention"; the PR/diff change-kind row and the resumed-header row -> "where that surface exists".

I have, Codex does not (keep):
- **P1** fail-safe harness (9/9, praised by AR on 7): Codex treats it as already covered; the checklist's predeclared-id
  wording does not allow the synthetic per-mode case that 6 accepted packages use, so it needs the sharpening.
- **P6** rewrite or loosen pinning base tests instead of only deselecting (5/9, plus a platform suggestion on RUN).
- **P3** system-of-record oracles and end-of-test invariants, **P4** unpromised parts left free with a comment, **P10**
  watchdogs and teardown, **P11** excluded modes behind a legacy gate / unsupported siblings fail loudly (SQ praised
  both), **P12** repeat the trigger, **P13** every observer checked and each one first.
- **P15** base mode per edited file: Codex classes WIN's miss as "existing rule not executed". Agree on the cause, but
  the wording "every package the change can affect" let it through, so sharpen it to "every edited file".

Disagree:
- **Timeout line:** Codex keeps it as NOT VERIFIED; I first wrote "drop the bound". Codex is right: I revised my row to
  keep it (a timeout above the platform kill loses the partial report).
- **Internal state in the harness:** Codex calls EOS's private-map read a local review question; I propose the
  checklist say explicitly that a harness wait on repo-visible state is acceptable while grading an internal is not,
  because 4 accepted packages do the former and fairness rated them "Repo-discoverable". Owner's call.
- **Regression test in the reference:** both say conditional; Codex counts 8/9 without one (WIN only adapts mocks), I
  wrote 0/9 adding a reference-owned test. Same conclusion.
