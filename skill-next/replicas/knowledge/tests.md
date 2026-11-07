# Tests-side platform pattern catalog

## Scope, exclusions, and normalization

This catalog covers test fairness, requirement coverage, Task Quality (TQ), Auto Review (AR) Tests T1-T8 and bands, verification checks, and rollout verdicts `FAIL_TEST_BROKEN` / `PASS_SHORTCUT`. It uses only the supplied `src/` sources. It intentionally excludes the three hold-outs named in the shared brief: topic-start wip6, dead-letter wip46, and the latest window-expiry Auto Review. It also does not inspect the out-of-scope repository files or broker settings named in the lane brief.

Two export quirks must be normalized before a local replica consumes the evidence:

- Digest rows are introduced as `UNFAIR test:` even when the JSON field says `"fairness": "Prompt-stated"`, `"Repo-discoverable"`, or `"Standard external semantics"`, and the enclosing result says `unfair: 0`. Trust the JSON field and overall verdict, not the row prefix. [digest/*.md, `verifyFairness` sections]
- The latest Task Quality artifacts contain eight checklist rows, but every row is exported as `[PASS] **None**:`. The official criterion names are therefore not recoverable from these sources. Preserve eight slots, but do not invent official names. [digest/*.md, `taskQuality` sections]

Observed non-hold-out inventory:

- Latest per-test fairness: 581 tests across 17 digests; 490 Prompt-stated, 77 Repo-discoverable, 14 Standard external semantics; zero tests marked unfair by their enclosing latest fairness verdicts. There are 42 advisory concern flags: 14 `internal_coupling`, 13 `timing_sensitivity`, 11 `brittle_message_matching`, two `overfit_single_point`, and two `environment_assumption`. [digest/*.md, excluding the hold-outs]
- Latest requirement coverage: 185 extracted requirements; 159 `yes`, 23 `partial`, three `no`. Twenty suggestions: 13 `not_discriminating`, six `single_point`, one `untested`; 19 have `sourceIfAdded: Prompt-stated`, one says `Would need prompt edit`. [digest/*.md, `verifyFairness` sections]
- Latest Task Quality: all 17 non-hold-out digests with a result say PASS on all eight serialized checklist rows. [digest/*.md, `taskQuality` sections]
- Latest AR Tests bands with usable non-hold-out AR output: eleven band 3, one band 2, three band 1. [platform-failures-cx.md:43-365; corresponding digest `autoReview` sections]
- The full historical finding map classifies 83 stated-requirement coverage gaps (C), 51 unstated requirements (U), 20 internal/mechanism pins (I), 18 nondeterministic/slow tests (N), 13 incomplete-fake/unrealistic-path findings (H), and 21 Docker/build/packaging/JUnit findings (D). These are finding rows, not necessarily distinct checks or tasks. [cx1-review-findings-map-cx.md:453-464]

## Task Quality's eight serialized criteria

The site emits exactly eight checklist results. Because their names are lost as `None`, the local replica should keep the eight result slots and evaluate the dimensions that the summaries repeatedly make explicit, while labeling these as observed dimensions rather than official criterion titles:

1. The task is a substantial engineering change and meets the challenge bar.
2. Scope is focused and bounded rather than an unbounded refactor.
3. Requested behavior is clear and actionable.
4. Outcomes are objective and testable.
5. The statement is self-contained enough to work from the ticket and repository.
6. Repository interfaces/conventions provide sufficient implementation context.
7. Hidden-test expectations align with stated or reasonably inferable behavior and do not pin hidden implementation choices.
8. Difficulty comes from meaningful integration/edge cases rather than ambiguity or harness breakage.

These dimensions are grounded in repeated PASS summaries such as “substantial, actionable engineering challenge with behavior-level acceptance criteria,” “well-scoped, objectively testable,” “sufficient implementation context,” and “hidden tests are fair.” [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:67-76; digest/kh71zcezmf-add-a-sqlite-table-store-sqlite-with-per-cx.md:56-65; digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md:347-356]

Do not collapse this eight-row task-level check into per-test fairness. Historical sources use TQ both for per-test fairness/coverage results and for the task-level eight-row result; retain both layers in the replica.

## Fairness patterns

### TF-01 Unstated literal, status, shape, or encoding pin
- check / rule / site severity: TQ fairness / unfair; AR T5/T3 when the same pin creates a false negative
- trigger (generalized, no task names): A test requires an exact status, query spelling, response envelope, optional-key presence, error text/class, file encoding, line ending, or malformed byte shape that neither the prompt nor a same-form repository precedent fixes.
- how to detect locally: For every exact literal, build a three-column refutation table: prompt quote, repository precedent at file:line, equally valid alternative. If both grounding columns are empty and an alternative passes the behavioral contract, the test is unfair. For malformed persistence, corrupt an implementation-written artifact instead of assuming a hidden format.
- what the site accepted instead (the PASS side): Assert non-success plus unchanged observable state; accept a plausible error family; or add explicit grounding words before testing the literal. A later PASS followed after adding the query spelling/JSON grounding and removing optional-key ambiguity.
- examples: notification-silence history: “query spelling `?group=` was unstated,” “Persistence encoding was pinned to JSON,” and “Optional empty JSON members had to remain present.” [cx1-review-findings-map-cx.md:56-59] Snapshot history: “Unenumerated rejection forced exact HTTP 400” and malformed cases “pinned undocumented schema.” [cx1-review-findings-map-cx.md:113-114] Older reader history: “Final-line-without-LF behavior ungrounded” and “HTTP404 forced into ParseError.” [cx1-review-findings-map-cx.md:396-397]
- count: 14 older PIN instances over 13 catalog rows; the broader historical map has 51 U-class findings. [site-findings-catalog-cx.md:230; cx1-review-findings-map-cx.md:455]

### TF-02 Rule transferred to an unstated verb, mode, or sibling surface
- check / rule / site severity: TQ fairness / unfair
- trigger (generalized, no task names): A sentence scopes a rule to one operation or mode, but tests require it on siblings without a repository-wide contract.
- how to detect locally: Build a requirement-to-surface matrix with the sentence's subject and scope. Mark every tested verb/mode/backend. A cell beyond the stated scope needs an explicit cross-surface rule or repository precedent.
- what the site accepted instead (the PASS side): Keep assertions on the named surface, state that the rule applies to all named siblings, or use outcome-only assertions common to the repository.
- examples: “Envelope promised for POST was pinned on other verbs” and “POST-only exclusivity rule was imposed on PUT.” [cx1-review-findings-map-cx.md:52-54] A transaction test “dictated which transaction in-flight record joined”; changing it to assert the last committed value produced PASS 21/21. [cx1-review-findings-map-cx.md:223; ledger-B-faust-early-cx.md:58-60]
- count: at least six recorded assertions in the two envelope/exclusivity families plus the transaction-membership episode; exact cross-history assertion count is not preserved.

### TF-03 Private state or harness mechanism treated as the contract
- check / rule / site severity: TQ fairness / unfair; AR T5/T7; latest fairness concern `internal_coupling`
- trigger (generalized, no task names): A test inspects a private field, exact queue emptiness, private offset, cleanup key, eager initialization choice, internal session path, or the test harness's own exception instead of the promised result.
- how to detect locally: For each assertion, ask whether a valid implementation can achieve the external result with a different field, call order, session identity, or cleanup mechanism. Replay at least two valid architectures. Flag private/member access unless the repository exposes it as the contract.
- what the site accepted instead (the PASS side): Assert delivery, persisted data, acknowledgement, public ownership, rendering input, or last committed value. The fairness sweep that removed private failure-field and queue-empty assertions later passed 37 fair tests.
- examples: six tests “Assertions inspected internal topic failure field,” followed by “Queue-empty assertion pinned internals.” [cx1-review-findings-map-cx.md:258-260] A cleanup co-assertion required a key to be absent although cleanup was unrequested; dropping it led to PASS 14 fair. [cx1-review-findings-map-cx.md:303] A current PDF test requires `PdfSession.path` itself to contain decompressed bytes, rejecting late source resolution. [digest/kh76ppnav0-preview-gzip-compressed-files-like-the-f-cx.md:276-287]
- count: 20 I-class historical findings; 14 latest non-hold-out `internal_coupling` concern flags. [cx1-review-findings-map-cx.md:456; digest fairness aggregation]

### TF-04 Termination, timing, logging, or side effect not promised
- check / rule / site severity: TQ fairness / unfair or advisory; AR T2 for unstable time dependence
- trigger (generalized, no task names): A test requires normal return rather than cancellation/raise, exact replay timing, absence/presence of a log record, fixed completion time, or a side effect on an object that no longer exists when the prompt specifies only the final behavior.
- how to detect locally: Separate semantic deadlines from test deadlines. Enumerate valid termination modes. Grep the prompt for a log or side-effect promise. Check whether the test name/comment itself introduces a rule not asserted by the body.
- what the site accepted instead (the PASS side): Accept return/cancel/raise where equivalent; use events or virtual time; assert final behavior; remove ungrounded log checks and impossible side effects.
- examples: three stop-path tests “demanded normal return”; accepting return/cancel/raise led to PASS 47/47. [cx1-review-findings-map-cx.md:182; ledger-B-faust-early-cx.md:26] A test name “implied unstated replay timing rule”; it was renamed to describe outcome. [cx1-review-findings-map-cx.md:210] A caplog test “demanded no ERROR records.” [cx1-review-findings-map-cx.md:216] A rollout asserted “a side effect on an object that no longer exists.” [site-findings-catalog-cx.md:206]
- count: at least seven named historical episodes; the N class contains 18 slow/nondeterministic findings, but not all were fairness failures. [cx1-review-findings-map-cx.md:457]

### TF-05 Valid alternative design rejected by a false premise
- check / rule / site severity: TQ fairness / unfair
- trigger (generalized, no task names): Test construction assumes parity between two stores/backends, an exact recovery/reset model, or a framework behavior contradicted by the pinned repository.
- how to detect locally: Reproduce the premise on the base commit and each included implementation. Read the concrete override, not only an abstract/base method. A test is unfair if a valid design supported by the repo fails solely because the fixture assumes the reference's architecture.
- what the site accepted instead (the PASS side): Remove the parity pin, relabel the alternative as valid, or assert the common outcome. Subsequent fairness runs passed after these removals.
- examples: a promoted-standby test “assumed incorrect RocksDB assignment parity”; removing it produced PASS 66/66. [cx1-review-findings-map-cx.md:193] A stop-era test “flipped unfair” despite prior reviews and was removed before later AR 3/3. [cx1-review-findings-map-cx.md:221] A same-version overwrite clause had changing verdicts; final suite passed after the disputed pin was removed. [cx1-review-findings-map-cx.md:195]
- count: at least three named design-premise episodes, plus other U/I findings where detail is not retained.

### TF-06 Advisory concern is not automatically unfair
- check / rule / site severity: latest verifyFairness / PASS with per-test concerns
- trigger (generalized, no task names): A grounded test uses internal instrumentation, bounded polling, existing UI/error wording, a single representative point, or an environment capability. The concern affects robustness/maintainability but does not create an equally valid implementation that fails.
- how to detect locally: First decide grounding and behavioral fairness; then record orthogonal concern flags. Do not turn a concern into an unfair verdict without a concrete valid alternative and failing scenario.
- what the site accepted instead (the PASS side): Prompt-stated, repo-discoverable, or standard-external-semantics tests can pass fairness while carrying concern flags; the overall artifact can still say `unfair: 0`.
- examples: SQLite tests are Prompt-stated yet note `internal_coupling` for recovery state and `timing_sensitivity` for event-loop yields. [digest/kh71zcezmf-add-a-sqlite-table-store-sqlite-with-per-cx.md:66-152] Conditional-write race tests are Prompt-stated while noting `internal_coupling,timing_sensitivity`; they still receive overall fairness PASS. [digest/kh7dgy3tmn-conditional-writes-leave-refused-data-be-cx.md:70-92]
- count: 42 latest concern flags across otherwise fair non-hold-out tests: 14 internal coupling, 13 timing, 11 brittle messages, two single-point overfit, two environment assumptions.

## Requirement coverage and discrimination patterns

### TC-01 Stated requirement has no load-bearing discriminator
- check / rule / site severity: TQ coverage partial/no; AR T3/T4 / usually High when a realistic wrong implementation passes
- trigger (generalized, no task names): The prompt promises behavior but no test fails when that behavior is removed, skip, or replaced with a cheaper wrong implementation.
- how to detect locally: Map every promise to test names, concrete assertion, realistic wrong implementation, and reference pass. Delete or mutate the corresponding solution hunk. A mapping is not covered merely because the code path executes.
- what the site accepted instead (the PASS side): A direct outcome assertion that fails the named wrong implementation while the reference and valid alternatives pass; broad matrices were praised when each difficult composition had such an assertion.
- examples: callback-failure rows assert only “callback failed,” so suppressing the promised producer error passes; AR T3/T4 High and Tests band 1. [digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-cx.md:335-344] A real threaded send/failure path is skipped by a fake override, so omitting the future bridge passes; AR T3/T4 High and band 1. [digest/kh70yqhmm2-settable-members-go-missing-or-come-back-cx.md:226-240]
- count: 83 C-class historical findings; latest requirement review has 23 partial and three no ratings. [cx1-review-findings-map-cx.md:453; digest fairness aggregation]

### TC-02 Public entry point, backend, mode, or artifact omitted
- check / rule / site severity: AR T4 / Medium to High
- trigger (generalized, no task names): Tests cover one public route/transport/config form/runtime build but omit another named or enabled surface, or test a struct directly without registration/wiring/install artifacts.
- how to detect locally: Build a matrix of public entry points, named modes/backends, compiled/generated twins, configuration sources, and deployment artifacts. Cross it with core invariants. Check every cell promised by the statement.
- what the site accepted instead (the PASS side): Cover the second surface or explicitly scope it out in the prompt and remove reference code that claims support. Tests band 3 examples explicitly exercised Python and compiled paths or direct/hosted variants.
- examples: “second public transport untested” and “pattern readers under backpressure untested.” [cx1-review-findings-map-cx.md:249-251] Controller, webhook, and install/Helm wiring were each High T4 findings when only structs were tested. [site-findings-catalog-cx.md:200-202] A direct commit-transaction surface was untested; adding success/failure/fenced tests moved AR from 1/3 to 3/3. [cx1-review-findings-map-cx.md:226]
- count: at least seven named public-surface findings above; exact total is included within the 83 C-class rows.

### TC-03 Feature-by-lifecycle or branch combination missing
- check / rule / site severity: AR T3/T4 / Medium to High; TQ coverage partial
- trigger (generalized, no task names): Individual features and lifecycle events are each tested, but their interaction is not: create/update/remove, open/mute/recover, pause/rebalance, retained/re-added, success/error, or multiple subscribers.
- how to detect locally: Create rows for features/modes and columns for lifecycle states/events. Empty cells are candidates only when the prompt covers both axes and the interaction is reachable. Prefer combinations that a real passer got wrong.
- what the site accepted instead (the PASS side): Tests that compose the axes and assert the final observable state, not just that each isolated branch ran.
- examples: a state entered “mid-lifecycle” was untested, and a recovery visibility rule was checked on one surface only; both were High. [site-findings-catalog-cx.md:90-92] A reverted handoff plus regular receiver was a missing Medium combination. [site-findings-catalog-cx.md:204] Pattern-reader plus backpressure was a High T4 gap. [cx1-review-findings-map-cx.md:251]
- count: at least four explicit examples; many of the 83 C-class findings share this shape.

### TC-04 Fixture masks production wiring or real framework behavior
- check / rule / site severity: AR T3/T4 or T5 / High; rollout `FAIL_TEST_BROKEN`
- trigger (generalized, no task names): A fixture insert the new dependency, replaces the public send/dispatch path, directly constructs a component, or acknowledges immediately, so production startup, registration, buffering, callback, or error propagation never runs.
- how to detect locally: Search helpers for assignment to new production fields, direct constructors, replaced methods, immediate callbacks, and fake-only entry points. Add one test through the real public lifecycle with defaults/unset state.
- what the site accepted instead (the PASS side): Use native dependency state or a thin wrapper; drive the real callback/lifecycle chain; fake only the outer I/O boundary. Fail-safe fixtures must model rejection as well as success.
- examples: every test assigned the application store, so startup wiring with it unset was never exercised. [site-findings-catalog-cx.md:77] A fake acknowledged immediately and left an exactly-once transactional path untested. [cx1-review-findings-map-cx.md:207] Latest SetTable AR found that replacing `send_soon` skip the real threaded queue and failure bridge. [digest/kh70yqhmm2-settable-members-go-missing-or-come-back-cx.md:226-240]
- count: 13 H-class historical findings; fixture masking also contributes C-class findings. [cx1-review-findings-map-cx.md:458]

### TC-05 Weak accepted set, proxy assertion, or vacuous truth
- check / rule / site severity: AR T3/T4 / Medium to High
- trigger (generalized, no task names): An assertion accepts both correct and wrong values, checks absence through a default/empty lookup, uses a proxy the defect does not affect, or applies `all()` to an empty collection.
- how to detect locally: Expand every matcher into its accepted output set. For each member, name whether it violates the promise. Require non-empty preconditions before `all`/`any`; assert the promised state directly.
- what the site accepted instead (the PASS side): Exact behavior when the prompt distinguishes it; explicit key/series absence; direct acknowledgement instead of commit proxy; a guard proving the collection contains the expected subject.
- examples: accepting 400 or 404 when the spec distinguished them was T3 High. [site-findings-catalog-cx.md:71] A metric deletion assertion also accepted recreation at zero; changing to an absence check was the recorded fix. [cx1-review-findings-map-cx.md:162] Cancellation checked “commit proxy, not ack state”; direct ack assertion was added. [cx1-review-findings-map-cx.md:262]
- count: at least three named families; exact assertion count is not retained.

### TC-06 Error asserted without post-state, or later action masks the defect
- check / rule / site severity: AR T3/T4 / High
- trigger (generalized, no task names): A failure-path test checks only the error, not memory/disk/config/log state; or a later operation flushes the correct state and hides that the earlier operation failed to persist.
- how to detect locally: After every rejection, assert all promised state and reload before any later mutating operation. In multi-step tests, snapshot storage after each step.
- what the site accepted instead (the PASS side): Error plus unchanged/rolled-back state, required log, and independent reload immediately after the operation under test.
- examples: “failure path asserts the error but not the state” was High after rollback was stated. [site-findings-catalog-cx.md:87] A later DELETE saved the map and hid a missing Update persistence write. [site-findings-catalog-cx.md:89] Rejected config logging was omitted from the assertion and rated T4 Medium. [site-findings-catalog-cx.md:178]
- count: three explicit catalog findings.

### TC-07 Directional boundary or correlated fixture cannot distinguish the rule
- check / rule / site severity: AR T3/T4 / Medium to High; TQ suggestion `not_discriminating`
- trigger (generalized, no task names): Only one side of `<`, `=`, `>` is tested, or two candidate ordering/count keys move together, so a wrong comparator or wrong measure passes.
- how to detect locally: Test below/equal/above and early/equal/late-or-never. Invert candidate keys (for example, order versus timestamp or pod versus container count). Write the `!=`, `<=`, or alternate-sort wrong variant explicitly.
- what the site accepted instead (the PASS side): Two-sided or three-point fixtures where the correct key and tempting wrong key disagree.
- examples: shrink and equal were tested but growth was not, allowing `!=`; High. [site-findings-catalog-cx.md:124] Order and timestamp rose together, allowing sort-by-timestamp; Medium. [site-findings-catalog-cx.md:125] One-container fixtures could not distinguish pod from container counts; Medium. [site-findings-catalog-cx.md:203]
- count: three explicit older findings; latest fairness reports 13 `not_discriminating` suggestions across broader requirement shapes.

### TC-08 Breadth is sampled at one point
- check / rule / site severity: TQ coverage suggestion `single_point`; AR T4 / often Medium
- trigger (generalized, no task names): A universal/deep/all-types promise is exercised by one depth, one array/object shape, one topology, or one non-default instance.
- how to detect locally: Identify quantifiers (“all”, “every”, “any depth”, “each value”) and vary the axis at least twice. A single point is acceptable only when the requirement itself is singular or repository equivalence proves generality.
- what the site accepted instead (the PASS side): Multiple independent representatives across the promised axis, or narrower wording.
- examples: latest concurrency AR found JSON object properties/nested objects but no JSON array elements; T4 Medium and band 2. [digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md:322-336] Latest suggestions also identify descendant depth and larger table/topology counts as `single_point`. [digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md:417-418; digest/kh7dvvpbmr-when-a-worker-dies-its-partitions-and-st-cx.md:109-110]
- count: six latest `single_point` suggestions; one current AR Medium issue.

### TC-09 Partial/no coverage is advisory unless a wrong implementation is proven
- check / rule / site severity: verifyFairness coverage yes/partial/no; AR may raise to T3/T4
- trigger (generalized, no task names): A requirement is only partly exercised, is an exclusion rather than executable behavior, or would require pinning an unstated interpretation.
- how to detect locally: Record `covered` separately from fairness. For `no`, distinguish an executable positive requirement from an exclusion/permission. raise only with a grounded wrong implementation and load-bearing test.
- what the site accepted instead (the PASS side): Overall fairness PASS can coexist with partial/no coverage and suggestions. If the missing boundary needs a prompt edit, do not add the test first.
- examples: at-least-once redelivery is `no` and suggested as `untested`; XOR against a lagging worker-local view is `partial`. [digest/kh70yqhmm2-settable-members-go-missing-or-come-back-cx.md:263-321] The current stream suite says replaying the exact raising message “Would need prompt edit,” so the boundary remains unspecified. [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:145-146]
- count: 23 partial, three no, 20 suggestions; one suggestion explicitly needs a prompt edit.

## Auto Review Tests T1-T8 patterns

The sources preserve findings for T1, T2, T3, T4, T5, and T8. They do not preserve an independently labeled T6 or T7 finding definition. Do not manufacture one; keep those rules available but return “no recorded example in supplied history” until direct evidence exists.

### AR-01 T1 baseline/regression coverage removed
- check / rule / site severity: AR Tests T1 / High
- trigger (generalized, no task names): Base mode excludes existing tests of the function or behavior changed by the solution, or wholesale deselection removes relevant regressions.
- how to detect locally: Diff solution-touched functions/files against base-mode selected test IDs. Inspect baseline JUnit for every run. Restore upstream tests, then exclude only exact tests proven to pin a required implementation change.
- what the site accepted instead (the PASS side): Base mode retains affected regressions, with exact-ID exclusion and written evidence only for tests every valid solution must change.
- examples: three existing metadata-refresh tests were excluded while that function was modified; AR T1 High x3. [site-findings-catalog-cx.md:123] Ten existing tests were deselected wholesale; the recorded fix was to adapt regressions. [cx1-review-findings-map-cx.md:276]
- count: four recorded T1/regression-removal instances (three repeated findings plus one wholesale-deselection episode).

### AR-02 T2 nondeterminism, wall-clock dependence, or flaky base
- check / rule / site severity: AR Tests T2 / Low, Medium, or High
- trigger (generalized, no task names): Fixed sleeps/poll deadlines, unbounded waits, unsynchronized reads, map/subtest order, or a racy upstream base test can change results.
- how to detect locally: Repeat solved and unsolved states, preserve exact test IDs/statuses, run under scheduler/load variation, and replace timing with a barrier or virtual clock. Inspect environment assessments for base flakes.
- what the site accepted instead (the PASS side): Event/barrier-driven ordering with only an outer deadlock timeout; stable repeated runs in both states.
- examples: fixed polling plus unsynchronized reads was T2 Medium; sleeping through actual expiry was T2 Medium. [site-findings-catalog-cx.md:86-88] An upstream coordinator lost-wakeup caused a 10-minute timeout and was T2 High. [site-findings-catalog-cx.md:179] Informer polling deadlines were T2 Low. [site-findings-catalog-cx.md:205]
- count: 18 N-class historical findings; explicit catalog examples span Low/Medium/High.

### AR-03 T3 assertion strength and directness
- check / rule / site severity: AR Tests T3 / Medium to High
- trigger (generalized, no task names): Assertions accept wrong outputs, inspect a proxy, omit post-state, or do not fail a concrete wrong implementation.
- how to detect locally: Enumerate the assertion's accepted values and run the cheapest wrong wrong variant. Require the exact promised observable when the prompt distinguishes it.
- what the site accepted instead (the PASS side): Direct state/output assertion with a load-bearing wrong-implementation check.
- examples: accepting two statuses was High; optional response-shape key omission was Medium. [site-findings-catalog-cx.md:71-73] A busy-stop proxy hid the wrong acknowledgement due to a head-gap quirk; direct ack discrimination was the fix. [cx1-review-findings-map-cx.md:274]
- count: at least three explicit T3 examples; combined T3/T4 findings are counted under their pattern families rather than double-counted.

### AR-04 T4 missing requirement, variant, surface, or combination
- check / rule / site severity: AR Tests T4 / Medium to High
- trigger (generalized, no task names): A stated branch, alternate form, public surface, backend, build, or interaction is absent.
- how to detect locally: Requirement/public-entry matrix plus a named wrong implementation for each blank cell.
- what the site accepted instead (the PASS side): Add a focused discriminator or narrow the stated scope consistently.
- examples: absolute-time input tested on create but not update was Medium; replace-with-nonempty was Medium. [site-findings-catalog-cx.md:72-74] JSON array elements are the current Medium T4 gap. [digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md:322-336] Real direct commit surface absence was High and drove Tests 1/3 before added tests. [cx1-review-findings-map-cx.md:226]
- count: at least four explicit examples; many combined T3/T4 rows sit within the 83 C-class findings.

### AR-05 T5 unrealistic fake, private representation, or harness path
- check / rule / site severity: AR Tests T5 / Medium to High; may coincide with `FAIL_TEST_BROKEN`
- trigger (generalized, no task names): Hidden doubles omit real public APIs/state, model the wrong internal field, intercept only one construction path, or a test pins a private representation rather than behavior.
- how to detect locally: Compare fake attributes and callback semantics with the installed dependency; instantiate alternative valid architectures; intercept every production construction path; complete every started lifecycle.
- what the site accepted instead (the PASS side): Native library state objects or faithful wrappers; behavior assertions; real lifecycle chain with I/O faked at the boundary.
- examples: missing assignment/pause/resume APIs drew AR T5 and a broken run. [cx1-review-findings-map-cx.md:249] Wrong subscription-state field recurred as AR T5/Test Broken. [cx1-review-findings-map-cx.md:261] Missing coordinator/client/metadata APIs caused another T5/Test Broken finding. [cx1-review-findings-map-cx.md:269]
- count: at least three AR T5 episodes on one task family plus two broken runs in another fake family; 13 H-class findings overall.

### AR-06 T6/T7 no directly labeled historical example
- check / rule / site severity: AR Tests T6/T7 / no supplied direct finding
- trigger (generalized, no task names): Not inferable safely from these exports.
- how to detect locally: Keep the rule slots, but require future site evidence before assigning a finding specifically to T6 or T7. Outcome-versus-mechanism concerns already belong to fairness/T5 in the recorded evidence.
- what the site accepted instead (the PASS side): No site-specific calibration is available.
- examples: The historical notes refer collectively to “T5/T7” for over-pinned assertions but do not preserve separate definitions or a standalone T7 verdict. [ledger-B-faust-early-cx.md:284-288] No direct T6/T7 rule-coded row appears in the consolidated site catalog. [site-findings-catalog-cx.md]
- count: zero directly labeled T6 or T7 findings in the supplied catalog/map.

### AR-07 T8 harness fail-safety and discovery propagation
- check / rule / site severity: AR Tests T8 / Medium; AR Tests 0/3 when harness/process violations are blocking
- trigger (generalized, no task names): Package discovery, compiler, converter, timeout, or missing-report failure is ignored or collapsed into a misleading success/pseudo-test.
- how to detect locally: Force each failure mode. Require nonzero exit plus valid JUnit; propagate discovery/build status; require at least one real testcase; on compile failure emit every new test's stable identity where the verifier compares p2p/f2p.
- what the site accepted instead (the PASS side): Fail-safe harness that synthesizes an explicit failing JUnit case only when no usable report exists, never overwrites genuine failures, and rejects zero activity.
- examples: base harness ignored `go list ./...` exit status; T8 Medium. [site-findings-catalog-cx.md:127] Unknown-uid build and converter failure each contributed to AR Tests 0/3 in older history. [cx1-review-findings-map-cx.md:413-415] Current band-3 reviews praise missing reports, timeouts, build failures, and anomalous exits becoming failures. [digest/kh717sntzs-materialized-views-reject-not-in-subquer-cx.md:34-45]
- count: one explicit T8 catalog finding plus at least two older harness-failure rows; D class has 21 packaging/JUnit findings overall.

### AR-08 Process-language contamination can be a blocker
- check / rule / site severity: AR Tests / Blocker, band 0/3
- trigger (generalized, no task names): Test scripts/comments contain grading-process wording such as “graded,” exposing evaluation mechanics rather than repository behavior.
- how to detect locally: Scan submitted scripts, comments, docstrings, and helper names for grader, hidden, reference, solution, patch, agent, or model language; manually review context.
- what the site accepted instead (the PASS side): Neutral repository/test wording. The next review no longer raised the blocker, though other issues kept the score low.
- examples: “Process wording remained in script comments” produced AR Tests 0/3 Blocker; neutral wording was the recorded fix. [cx1-review-findings-map-cx.md:271] The later notes record the next AR as Tests 1/3 for different reasons. [ledger-B-faust-early-cx.md:391-395]
- count: one direct package episode in this history; the map checklist notes one additional external occurrence. [cx1-review-findings-map-cx.md:542]

## Verification and harness patterns

### VH-01 Wrong pasted Dockerfile or dependency environment
- check / rule / site severity: verifyTests or verifySolution / FAIL
- trigger (generalized, no task names): The platform field contains a default/stale Dockerfile rather than the tested one, changing dependency versions/plugins and causing broad base failures.
- how to detect locally: Hash the pasted field, not only the local file. Rebuild and run base/new in the exact image. Treat a precheck quoting an unexpected template as evidence of a paste mismatch.
- what the site accepted instead (the PASS side): Re-pasting the intended Dockerfile produced a later verify pass.
- examples: SQLite Verify Tests failed because the platform used pytest 9 without pytest-asyncio; re-paste fixed it. [cx1-review-findings-map-cx.md:187; ledger-B-faust-early-cx.md:29] A leader-lifecycle package had 301 failed/23 errored under the default field; re-pasting produced Verify Solution PASS. [cx1-review-findings-map-cx.md:292; ledger-B-faust-early-cx.md:126]
- count: two tasks, one Verify Tests and one Verify Solution failure.

### VH-02 Build-failed pseudo-test breaks p2p/f2p identity
- check / rule / site severity: verifySolution / FAIL; AR T8 / Medium
- trigger (generalized, no task names): A compile/discovery failure is reported as one synthetic `[build failed]` testcase rather than the expected new test identities, so the verifier cannot match before/after states.
- how to detect locally: Force compile failure in unsolved and solved modes; compare JUnit test-name sets. The fallback must not make new tests disappear from both p2p and f2p.
- what the site accepted instead (the PASS side): Emit every new test by name with the compiler output, and propagate the failure.
- examples: RDB history: “Build-failed pseudo-case broke before/after test identity.” [cx1-review-findings-map-cx.md:37] Quamina history: “Single compile-failure pseudo-case broke JUnit identity.” [cx1-review-findings-map-cx.md:417]
- count: two tasks; the same family also produced an AR T8 finding for ignored discovery status.

### VH-03 Reference or new tests fail in the platform image
- check / rule / site severity: verifySolution / FAIL
- trigger (generalized, no task names): The reference patch does not pass its own tests under the actual image because of corrupted literals, copy-path differences, missing dependencies, or platform-only assumptions.
- how to detect locally: Run solution+tests together in a clean image, offline, as root and an arbitrary numeric uid. Inspect the actual failing assertions rather than assuming local success transfers.
- what the site accepted instead (the PASS side): Reference and baseline both pass their required cells; latest PASS artifacts explicitly report `baselinePassed`, `newTestsPassed`, offline uid, and oracle success.
- examples: binary-string tests failed with the reference applied in the platform image. [site-findings-catalog-cx.md:44] Clipboard mojibake caused two f2p failures even though equally corrupted local input/expected could pass. [ledger-D-playbooks-tools-cx.md:319-321]
- count: two recorded reference/environment examples, plus separate uid and timeout families below.

### VH-04 Unknown uid, no passwd record, or writable-path assumption
- check / rule / site severity: verifySolution / FAIL
- trigger (generalized, no task names): Base or tests assume the runtime uid has a passwd entry, HOME, or a writable conventional temp path.
- how to detect locally: Run base and solved cells as an arbitrary numeric uid with no passwd record and offline. Use workspace-owned temp locations and avoid HOME/passwd assumptions.
- what the site accepted instead (the PASS side): Latest verifySolution passes report `offlineUidPassed: true`.
- examples: an Elio package failed because the platform ran base as an unpermissioned uid without a passwd record. [cx1-review-findings-map-cx.md:384; ledger-A-memory-skill-cx.md:2692-2698] An older package's AR Tests 0/3 also records “Unknown uid/no HOME failed test-time build.” [cx1-review-findings-map-cx.md:413]
- count: two recorded uid/environment episodes.

### VH-05 Clean baseline flake or unsolved-state flakiness
- check / rule / site severity: verifyTests or verifyFlakiness / FAIL
- trigger (generalized, no task names): Base passes locally but one clean run flakes, or unsolved subtest order/parent-fatal behavior changes which cases execute and report.
- how to detect locally: Repeat both test-only and solved states; compare exact IDs and statuses, not aggregate totals. Avoid parent `Fatalf` that prevents sibling subtests and map iteration that changes first failure.
- what the site accepted instead (the PASS side): Stable identical unsolved repeats and solved repeats; latest PASS typically reports six runs per state with no flaky tests.
- examples: five unsolved subtests changed due to map order and parent Fatalf; no further failure was recorded after the harness fix. [cx1-review-findings-map-cx.md:155; ledger-D-playbooks-tools-cx.md:303-310] A clean baseline passed 1999/2000 because of a load-timing flake, causing Verify Tests FAIL. [cx1-review-findings-map-cx.md:383]
- count: one five-subtest Verify Flakiness episode plus one baseline Verify Tests flake; one additional Verify Flakiness failure has no preserved cause. [cx1-review-findings-map-cx.md:273]

### VH-06 Test run exceeds the platform budget or emits no XML
- check / rule / site severity: verifyTests / FAIL or stopped run
- trigger (generalized, no task names): New mode runs beyond the platform stop, fixed waits accumulate, or the outer harness does not emit JUnit before termination.
- how to detect locally: Measure clean unsolved and solved duration inside the final image. Bound individual waits with events, keep total below the site budget, and emit a failing report on timeout.
- what the site accepted instead (the PASS side): Shorter per-test bounds and an outer script limit; later runs completed in 259-280 seconds with no further timeout.
- examples: a clean new run stopped after 688 seconds with no XML. [cx1-review-findings-map-cx.md:324; ledger-C-faust-recent-cx.md:409-416]
- count: one recorded platform timeout episode.

### VH-07 Rebuild is not safe from the committed base
- check / rule / site severity: verifyBuild / Rebuild FAIL
- trigger (generalized, no task names): Local cached/no-cache builds pass, but the committed base/pin or upstream state used by the platform no longer rebuilds with the submitted Dockerfile.
- how to detect locally: Rebuild from the exact repository URL and commit in a fresh context; verify the base SHA before paste. Do not rely on a local checkout already containing fetched/generated state.
- what the site accepted instead (the PASS side): Rebase to the upstream tip and rerun proofs; the recorded task fixed three failed Dockerfile variants this way.
- examples: a committed-source rebuild failed despite local builds; “Upstream-tip rebase fixed” it. [cx1-review-findings-map-cx.md:327; ledger-C-faust-recent-cx.md:419-426]
- count: one task with three failed Dockerfile variants.

### VH-08 Encoding corruption changes the actual patch
- check / rule / site severity: verifySolution / FAIL
- trigger (generalized, no task names): Clipboard/locale conversion corrupts non-ASCII bytes while local tests compare equally corrupted inputs and expectations.
- how to detect locally: Hash after paste; validate UTF-8 and inspect byte-sensitive literals in the platform artifact; prefer ASCII encodings for byte fixtures when semantics allow.
- what the site accepted instead (the PASS side): ASCII-only patch transport and post-paste hashes.
- examples: a Mac clipboard under `LC_CTYPE=C` re-encoded UTF-8 and caused Verify Solution failure. [ledger-A-memory-skill-cx.md:2773-2777] The consolidated map records the same as two f2p failures from mojibake. [ledger-D-playbooks-tools-cx.md:319-321]
- count: one task / one Verify Solution episode.

## Agent-run verdict patterns

### RR-01 Graded-test edits produce PASS_SHORTCUT even for substantive solutions
- check / rule / site severity: rollout verdict `PASS_SHORTCUT` / counts as failure
- trigger (generalized, no task names): An agent changes a graded upstream test, mock, fixture, or test configuration and that edit causally changes a failing outcome to pass. It remains a shortcut even if the production patch is substantial and the reference would need a similar fixture update.
- how to detect locally: Restore every graded file/config from the base commit before scoring; rerun. Diff passing agents' test edits and ask whether the pass remaining without them. Exclude only exact base tests proven to pin internals, before rollout.
- what the site accepted instead (the PASS side): Restore upstream tests/config, add exact necessary exclusions, and replay stored patches. Genuine pass rates often fell after shortcut removal.
- examples: one SQLite passer edited an upstream recovery Mock; the outcome was `PASS_SHORTCUT`, then an exact exclusion enabled a later genuine passer. [cx1-review-findings-map-cx.md:189] Three window-expiry Orion runs edited newly graded coupled tests. [cx1-review-findings-map-cx.md:211] Two leader-lifecycle runs edited graded rebalance mocks. [cx1-review-findings-map-cx.md:294] Two later runs edited Mock fixtures. [cx1-review-findings-map-cx.md:325]
- count: five named historical map episodes spanning five task/version rows; the map's workflow checklist says seven task families required this audit. Latest non-hold-out digests contain five individual `PASS_SHORTCUT` rows (four SetTable, one SQLite), all stale. [cx1-review-findings-map-cx.md:524; digest run tables]

### RR-02 Incomplete hidden doubles produce FAIL_TEST_BROKEN
- check / rule / site severity: rollout verdict `FAIL_TEST_BROKEN`; AR T5
- trigger (generalized, no task names): Hidden fakes lack APIs/state present on the real dependency, restore incompatible legacy mocks, or discard necessary fixture repairs, causing otherwise substantive implementations to fail for the harness rather than the task.
- how to detect locally: Compare the double against the installed library/public interface and real construction path. Re-run with native state objects. Separate harness-caused failures from independent genuine failures in the same run.
- what the site accepted instead (the PASS side): Embed/use real dependency state objects and fake only network/I/O boundaries; after one such repair, replay produced a genuine 1/4 pass.
- examples: two transactional runs failed because FakeKafka lacked `_txn_manager`; carrying real transaction-manager state fixed the family. [ledger-B-faust-early-cx.md:64; cx1-review-findings-map-cx.md:224] Live-reader runs failed when fakes lacked assignment/pause/resume or modeled the wrong subscription-state field. [ledger-B-faust-early-cx.md:95-100] Current ownership runs passed all new tests but failed restored legacy Mock fixtures, producing two broken verdicts. [digest/kh7bfzrhqd-after-a-rebalance-our-tables-still-show-cx.md:122-154]
- count: latest non-hold-out digests contain six individual broken rows: one live-reader, two exactly-once, one concurrency/bundle-collection, two ownership/legacy-fixture. Historical summaries specifically count two transaction-fake and two live-reader-fake broken runs. [digest run tables; ledger-D-playbooks-tools-cx.md:260-267]

### RR-03 A broken flag can be overruled when the implementation caused the failure
- check / rule / site severity: rollout contest / broken verdict not upheld
- trigger (generalized, no task names): An agent blames hidden fakes, but the pinned repository accepts the path and the agent introduced stricter preconditions or extra dependencies.
- how to detect locally: Reproduce the failing base tests against the pinned code; identify whether the agent's production change, not the fixture, created the incompatibility. A missing fake field is not enough if the valid repo path never requires it.
- what the site accepted instead (the PASS side): Uphold the failure as an implementation regression when base tests and concrete code establish the valid path.
- examples: ownership contests were overruled where the agent added assignment-state requirements to event-local reads and new metadata dependencies absent from the original path. [digest/kh7bfzrhqd-after-a-rebalance-our-tables-still-show-cx.md, `autoReview` false-positive review reasoning]
- count: two recorded contest adjudications in the current ownership digest.

## PASS patterns

### PASS-01 Grounding sources accepted by fairness

The site explicitly accepts three grounding classes: Prompt-stated, Repo-discoverable, and Standard external semantics. In the non-hold-out latest digests, all 581 judged tests fall into these classes (490/77/14). Regex semantics, partition ordering, public repository contracts, and prompt quotes are accepted when the test's exact outcome follows from them. [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:77-146; digest fairness aggregation]

### PASS-02 Outcome-focused, cross-component matrices

Band-3 reviews praise tests that assert observable routing, persistence, ownership, delivery, acknowledgement, commit state, or layouts across meaningful combinations. Examples include “both Python and compiled conductor paths” and “observable routing, fetch eligibility, delivery, acknowledgement, and commit behavior.” [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:45-56] The SQL suite was accepted for both syntactic spellings, NULL behavior, all change directions, transactions, affinity/collation, duplicates, and compound selects. [digest/kh717sntzs-materialized-views-reject-not-in-subquer-cx.md:34-45]

### PASS-03 Fail-safe harnesses

The site repeatedly praises harnesses where build failure, timeout, missing/empty report, skipped feature tests, reporter/converter failure, nonzero exit, and zero activity become failures rather than passes. A synthetic JUnit failure is accepted only as a fallback when no usable report exists and must not mask real results. [digest/kh717sntzs-materialized-views-reject-not-in-subquer-cx.md:34-45; digest/kh7d92724b-docker-proxy-writes-leftover-through-changes-cx.md:36-48]

### PASS-04 Bounded synchronization without threshold assertions

Bounded waits are accepted when they drive async work but the test does not assert a wall-clock threshold. The live-reader fairness review says event-loop yielding and bounded timeouts are not a per-test fairness problem because they do not assert timing thresholds. [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:146-147] Events, virtual time, and deterministic lifecycle handshakes are the accepted replacement for fixed sleeps. [cx1-review-findings-map-cx.md:521-534]

### PASS-05 Hard but fair agent convergence

Low solve rate is accepted when failures cluster on stated or repository-discoverable boundaries and at least one genuine solution exists. The site calls such convergence “healthy difficulty,” “benign difficulty,” and “genuinely difficult but fair.” [platform-agents-cx.md: sections dated 2026-10-11 through 2026-11-05] Convergence on an unfair private-state assertion instead supports changing the test, as with the PDF session-path case. [platform-agents-cx.md, 2026-10-28]

### PASS-06 Partial coverage can coexist with fairness PASS

Latest fairness artifacts can pass with `partial`/`no` requirements and actionable suggestions. Coverage is advisory until a grounded wrong implementation proves a load-bearing gap. The source-of-addition field prevents converting an unspecified boundary into a hidden requirement; one latest suggestion expressly says “Would need prompt edit.” [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:145-146]

### PASS-07 Band 3 means no kept test/harness issue

The current clean reviews use language such as “No kept test or harness issue exists,” “No materially wrong in-scope implementation that would pass,” and “No concrete false-positive, false-negative, flaky, or harness-masking path.” [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md:45-56; digest/kh71zcezmf-add-a-sqlite-table-store-sqlite-with-per-cx.md:34-45; digest/kh7d92724b-docker-proxy-writes-leftover-through-changes-cx.md:36-48]

## Severity calibration

- AR Tests band 3: clean; no kept issue. Eleven usable non-hold-out latest reviews are band 3.
- AR Tests band 2: a verified Medium issue can reduce the band to 2. The current example is one omitted JSON-array axis while otherwise broad tests remain deterministic and behavior-focused. [digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md:322-336]
- AR Tests band 1: a verified High false-positive/coverage gap or false-negative/unfair pin controls the band even when the rest of the suite and harness are broad and stable. Current examples are the skip real threaded failure path, the callback-plus-write-error gap, and the private PDF session path plus an all-green fixed-size cutoff. [digest/kh70yqhmm2-settable-members-go-missing-or-come-back-cx.md:226-240; digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-cx.md:335-344; digest/kh76ppnav0-preview-gzip-compressed-files-like-the-f-cx.md:276-287]
- AR Tests band 0/3: a Blocker can come from test artifact/process contamination even before behavioral coverage is weighed; the recorded “graded” comment episode was 0/3. [cx1-review-findings-map-cx.md:271]
- High T3/T4: an explicit promise is untested and a realistic wrong implementation or all-green passer proves it; examples include missing wiring, missing failure post-state, missing cleanup, and one-sided directional rules. [site-findings-catalog-cx.md:77-92,123-125,177-180]
- Medium T3/T4: an alternate input form, one branch/combination, a correlated fixture, or one breadth axis is omitted, without evidence of core task failure. [site-findings-catalog-cx.md:72-74,83-84,125,178,203-204]
- T2 High/Medium/Low follows consequence and reproducibility: a 10-minute flaky base timeout was High; fixed polling/sleeps or unbounded wall-clock waits were Medium; ordinary five-second polling was Low. [site-findings-catalog-cx.md:86-88,126-127,179,205]
- TQ unfair is effectively gating regardless of a separate severity word: one unfair assertion has failed a TQ run; multiple assertions produce counts such as 3/42, 1/21, or six unfair. Repairs ground the assertion or remove it, then rerun. [cx1-review-findings-map-cx.md:182,223,258]
- Verify checks are binary gates: wrong image, build identity, baseline flake, offline uid, timeout/no XML, mojibake, or reference failure each produces FAIL despite otherwise good task quality.
- `PASS_SHORTCUT` counts as failure even when all tests pass and the production implementation is substantive; causality of the graded-file edit is the key. [ledger-A-memory-skill-cx.md:169-177]
- `FAIL_TEST_BROKEN` requires the harness/double, not the agent's design, to be the dominant cause. Mixed runs can have both broken-test failures and genuine misses; contests must separate them. [digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md: run table; digest/kh7bfzrhqd-after-a-rebalance-our-tables-still-show-cx.md: run table and contest reasoning]

## Local replica decision sequence

1. Normalize exporter quirks and remove hold-out versions.
2. For each test, decide grounding class and fairness before recording advisory concerns.
3. Extract each requirement and label yes/partial/no independently of fairness.
4. For each covered requirement, name the exact assertion and cheapest realistic wrong implementation.
5. Audit public surfaces, feature/lifecycle combinations, failure post-state, boundaries, and fixture masking.
6. Audit base selection (T1), stability (T2), assertion directness (T3), missing variants (T4), fake realism/public behavior (T5), and harness fail-safety (T8); report no calibrated example for T6/T7 rather than guessing.
7. Grade the most severe kept test issue into the AR band: clean=3, Medium=2, High=1, Blocker=0.
8. Run clean base, test-only, solved new/base, repeated solved/unsolved, offline, root, and arbitrary-uid cells; validate JUnit identities and total time.
9. Restore graded files/config before scoring runs; classify causal edits as `PASS_SHORTCUT`.
10. Compare hidden doubles with real dependencies and adjudicate `FAIL_TEST_BROKEN` against pinned repository behavior.
