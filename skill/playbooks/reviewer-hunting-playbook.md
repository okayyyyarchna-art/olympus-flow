# Reviewer hunting playbook (give this to every local SQ/TQ/AR/FP reviewer)
Evidence and row numbers: site-findings-catalog.md (Part 1 rows #1-#150, Part 2 sections A-D).
Rule zero: think like the platform. For every finding, give:
- the promise quote;
- the cheapest realistic wrong implementation;
- the line that cannot see it (`test_name`, `repo_line` or `artifact_line`);
- proof that the reference passes the demanded check;
- a deterministic failing case.
Severity = "can a realistic wrong impl pass or a user observe harm", never our own guess.

## 1. Hunting moves (run all that apply; the top 10 produced most High findings)
1. ORPHAN HUNK: delete each reference hunk in a copy (also one-liners in existing cleanup/registration hooks).
   If no hidden test fails and a promise covers it, it is a T3/T4 gap. If no promise covers it, it is scope creep.
2. ASYNC SCRIPT: list concurrent producers (go-per-request evaluation, /metrics scrape, hashed workers, notifier tick,
   unlocked config readers). For each delete or invalidate, write: producer reads old -> op returns -> producer
   writes. Each writer line is its own S1. Fix with a token taken BEFORE enumeration, or a draining barrier.
3. ALL-GREEN DIFF: diff every PASS run in the rollout zip against the reference, promise by promise. Probe what the
   passer lacks. A fair failing probe is both an FP risk and a test gap.
4. FIXTURE MASK: grep test helpers for assignments to the new production field or direct construction. Is there a
   test that drives Start/main/SetupWithManager/webhook.Setup with it unset? If not, the wiring is untested.
5. ACCEPTED SET: for each assertion, list every output it accepts (`Contains{400,404}`; `Empty(m[k])` with the key
   missing; a metric helper where deleted == reset to 0; `>=` counts). Name a wrong output inside the set.
6. FAILURE POST-STATE: after every asserted error, assert the state too (store, file, config, log line).
   Reload after each persisted mutation, before a later mutation flushes everything.
7. CROSS-PRODUCT: rows = features and modes (from the description AND the README/config: send-once, BOOST_ON_RESTART,
   kinds). Columns = lifecycle events (open, escalate, mute later, recover, remove, re-add, hand off). Probe the empty
   cells first.
8. SINK TRACE: from each sink new state reaches (send/Notify, metric Set, [len-1], map lookup+deref, SetDefault),
   build the stale or absent state that reaches it.
9. REMOVAL MATRIX: for removed, shrunk, replaced-with-fewer, lazily expired, filtered, removed-then-re-added: check
   storage, evaluator cache, metric series, notifier incident state and detail endpoints, and that a re-add starts
   fresh.
10. LINT DIFF: run golangci-lint with the repo config on the diff (revive exported/error-strings, goconst thresholds).
    grep `errors.New("[A-Z]`, undocumented exports, comments displaced by an insertion, license headers.
11. ROLLBACK AUDIT: list every process-global write on the validate/reject path (viper.Set, SetDefault, Reset losing
    the config type). Run reject -> correct -> reload, rename or remove optional sections, and check whether the
    baseline is captured state or re-read from disk.
12. DECORRELATE: when a promise names a key or unit (Order vs Timestamp, containers vs pods, muted-by vs covering),
    invert the dimension the fixtures move in lockstep.
13. DIRECTIONAL: test <, = and > for every "fewer/older/longer". Write the != mutant. Count with the real measure
    (cap, not the len of a filtered slice).
14. DEPENDENCY CLOSURE: change-detection and identity must include referenced sections (client-profile/tls/sasl) and
    the kind. Probe by editing only the referenced section, or by creating same-name objects of two kinds.
15. SENTINEL TRACE: follow lastCommit 0, zero Until, empty group = all, nil vs [] through every existing consumer
    (lazy expiry, matchers, completeness checks).
16. DECODER SET (solution side): null, top-level array, trailing data, nested null, missing member, {"x":null},
    numbers as strings, unknown fields. The reference must reject what the text calls invalid.
17. BASE FORENSICS: base exclusions vs the functions you touch (never exclude those). Read junit_base and
    environment_assessment of every rollout run. The unsolved run reports one failed case per new test, with no
    `[build failed]` pseudo-test.
18. SIBLING SYMMETRY: a check or convention used by one handler (clusterExists, writeResponse+CORS, the error envelope)
    must be used by every sibling route.
19. REFUTATION BATTERY (TQ): every pinned literal needs a prompt quote or a repo file:line precedent. Otherwise assert
    only non-success + unchanged state.
20. IN-FLIGHT WRITE RACE (harness): a barrier that returns when the process TAKES a signal (unbuffered send, "settle")
    leaves that reload running. A test that rewrites the file next can race its read: a truncated TOML file is valid
    and empty, so every module is removed (Burrow #751: about 1 flake per 100-300 runs under load, seen only with -count and
    CPU load). Writes must be atomic (temp file + rename). Probe: loop the suite under 2 load containers, --cpus=1.
21. ACCIDENTAL PASS: a "restarted on change" assertion also passes an impl that restarts on ANY first reload.
    Send SIGHUP for the unchanged file first and assert nothing restarted, then make the change (Nova_8 passed
    the consumer profile tests this way).
22. BARRIER MASKING: a barrier that works by sending the trigger again (settle = one more SIGHUP) gives a solution
    that applies only part of a change per trigger a free second pass. Check the first positive effect with
    eventually BEFORE the barrier; use the barrier only to guard negative checks (nothing restarted, quiet windows)
    or before publishing new input. Burrow #751: a mutant skipping module changes whenever storage changed passed
    until the settle was moved.
23. RACE TESTS NEED A MEASURED CATCH RATE: for each async race (scrape vs delete, in-flight cache vs forget), run the
    no-fence mutant >=5 times. Widen the window (many topics/groups, more concurrent readers) until it is caught
    every time, or report it as not reliably testable instead of shipping a weak test. #751: the metrics fence went
    from 1/5 to 5/5 with 30 topics; the evaluator fence stayed at 0/10 because cache hits leave nothing in flight.
24. SIGNAL WIRING (binary): the common wrong main.go adds SIGHUP to the existing 1-slot exit channel; a TERM
    arriving while a reload runs and a second SIGHUP waits is dropped by os/signal. Make the reload slow on purpose
    (a cluster on a broker with 1s latency), send HUP, wait 200ms, send HUP and the stop signal, and expect an exit.

## 2. Blind-spot checks before every paste (each one missed real findings in Part 2 B)
- [ ] An SQ reviewer ran BEFORE the first SQ check. We skipped this on 4 of 4 tasks and got ~14 first-round FAILs.
- [ ] golangci-lint ran on the final diff. 0 local reviews ever ran it; 6 site lint findings.
- [ ] The reviewer got this playbook + catalog. The scrape race and in-flight cache recurred 4 days apart on Burrow.
- [ ] After EVERY fix (even a "cleanup" revert), re-run lint, the probe that justified the old code, and alternate
      inputs (extensionless config, env-only, other modes). 4 findings were caused by our own fixes.
- [ ] No local finding was downgraded, declined, deferred or dropped as "residual" without a platform-style severity
      test. 5 of them came back as High.
- [ ] Description changed since the last review? Diff old vs new. Re-run move 19 for every dropped load-bearing phrase
      ("with those keys", "json", "group"). 6 unfair assertions came from this.
- [ ] No test was deleted or rolled back for a behavior SQ demands. Fix the wording instead. Replay the list of fixed
      site findings after any rollback.
- [ ] Solution review uses NO "accepted by design" list. Exclusions that keep tests fair do not excuse the reference
      (nested null, startup race).
- [ ] Platform artifacts scanned: JUnit test-ID sets of both states, run-judge environment flags, every passer's patch.
- [ ] The promise matrix has mode and wiring rows (README modes, registration, manifests, entry points), not only
      description sentences.
- [ ] Paste hygiene: ASCII-only test.patch, `LC_ALL=en_US.UTF-8 pbcopy`, repo path + SHA checked.

## 3. FP calibration (31 platform adjudications: 15 upheld, 16 genuine)
UPHELD when the adjudicator re-ran a probe (candidate FAIL, reference PASS) AND it hits one of:
- data loss or wrong state in the core scenario: restart, import, handoff (6/7);
- concurrency with a functional effect: crash, hidden test flaky vs the reference, rejected config applied (4/4);
- explicit words violated: "whole name", "oldest first", "rather than any evaluation cached before it" (3/3).
OVERRULED ("not prompt-grounded", "underspecified", "out of scope"):
- stricter validation than stated, including trailing JSON when the repo itself is lax (0/7);
- corner status codes or display: DELETE of expired, NOTFOUND wildcard (0/6);
- surfaces the feature does not reload or own (0/5);
- races seen only by -race, or a TOCTOU without contract words (0/3);
- resource leaks (0/1).
COIN FLIPS (estimate P(upheld), never call them certain):
- referenced client-profile restart (3 up / 5 down);
- name collision with a format key (1/1).
Reading the panel:
- Judge #2 dissents on most passes. Only the adjudicator counts.
- "verdict changed by panel evidence" = a judge probe flipped it.
- Panel "Nova N" != zip Nova_Nova_N. Match runs by the code the panel quotes.
- A test that kills the only genuine passer gives 0/10. Weigh FP risk against the pass-rate target.
Agent failures that discriminate fairly (Part 2 C; 223 failing runs):
- presence-vs-value and error-class conflation (~85);
- re-implementing an existing pipeline instead of feeding it (~60);
- lifecycle and visibility windows (~48);
- library defaults (~45);
- explicit-only enumerations (~35);
- one helper reused across different invariants (~26).
If 7 of 10 runs fail one rule ("shared blind spot"), re-read that sentence for a second reading before keeping it.

## 4. Report format (one block per finding)
`[check/rubric item] [severity] location` | promise quote | wrong impl caught | failing case | load-bearing line |
reference passes? | fix sketch. Group repeats by family (a 6-line metric family = 6 findings).

## Codex G1 lessons (kscb trial, 2026-10-05)
- Replacing an unfair test means DELETING the old one; adding a stronger test leaves the old false-negative risk.
- Run the harness environment literally: /app mounted READ-ONLY (`-v tree:/app:ro`, chmod a+rX only). A world-writable
  tree hid a base-mode bug (mv of new test files failed silently, base ran the new tests).
- Decorrelate fixtures: partially boosted pods (counts vs container count), both same-name kinds in one operation,
  multiple validation causes/warnings (first-only shortcuts).
- No t.Run subtests in compiled packages that use the per-name build-failure fallback (same names before/after).
- Test helpers that re-implement external tools (Helm) must accept every valid solution or be dropped.
