# Solution-side platform pattern catalog (SQ and AR S1--S4)

## Scope and reading rule

This catalog covers the platform's reference-solution judgments: SQ
comprehensiveness/code quality, Auto Review solution bands and S1--S4, plus
claims that the record says were contested or not reproduced.  It is an
evidence catalog, not a list of hypothetical bugs.  Counts are recorded site
instances (where the source says `xN`, that multiplicity is retained); `NR`
means the historical record does not identify a version or later rerun.  The
three hold-out cases named in `brief-kb-common.md` are deliberately absent:
topic-start wip6, dead-letter wip46, and the latest window-expiry AR.

Sources used throughout are the permitted source tree only.  `cx1-review-
findings-map-cx.md` is abbreviated **Map**; `site-findings-catalog-cx.md` is
**Catalog**; digest examples name their file in full.  Quoted fragments are
verbatim site/history wording (apart from ellipses).

### SQ-01 Contract surface was implemented only on the obvious path
- check / rule / site severity: SQ comprehensiveness, normally High; AR S1
  High where the missed surface invalidates an explicit promise.
- trigger: a new rule is applied to the main API, transport, mode, direction,
  or lifecycle path but a sibling entry point, fast path, derived form, or
  supported configuration surface skip it.
- how to detect locally: turn every promise into a matrix of entry points,
  modes, before/after states, and positive/negative directions.  Trace each
  matrix cell to its concrete call site; a finding requires a stated cell that
  reaches old behavior or no behavior, not merely an untested implementation
  preference.
- what the site accepted instead (the PASS side): an end-to-end trace through
  every declared path, including explicit handling of unsupported paths.  The
  conditional-write solution is praised for covering "the relevant write
  paths" and keeping conditions on copy destinations; the live-reader
  solution is accepted because the driver limitation does not contradict its
  stated default-transport scope.  Sources:
  `digest/kh7dgy3tmn-conditional-writes-leave-refused-data-be-cx.md`,
  `digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md`.
- examples: snapshot v2, "Partial partition shrink left stale metric series"
  (**Map**, F63); reload wip5, "Change detection omitted referenced
  configuration sections" (**Map**, F105); T7 wip30, "Empty-fetch path
  skipped second-transport gate" (**Map**, E073); T10 wip22, "Fast paths
  skip served-partition gate" (**Map**, E130).
- count: at least 9 recorded instances (F63, F66, F104--05, F109, E073--74,
  E130, plus the repeated-mode aggregates E020--23 and E068).

### SQ-02 State transition, ownership, and cleanup are incomplete
- check / rule / site severity: SQ comprehensiveness High; AR S1 High; AR S2
  High where notification/reset bookkeeping is lost.
- trigger: a transition removes, replaces, reassigns, recovers, expires, or
  hands off an entity, but a marker, metric, retained value, ownership record,
  or reset state is cleared too early, not cleared, or reconstructed from the
  wrong state.
- how to detect locally: build a before/during/after transition table.  Try
  replacement, partial shrink, revoke/reassign, recovery, retry, expiration,
  and return-to-owner.  Inspect every dependent subsystem (storage, cache,
  metrics, notification, iterator/reader) for both removal and re-add.
- what the site accepted instead (the PASS side): ownership is carried through
  assignment, visibility, recovery, and iteration; shutdown waits for the
  state it needs.  The table-rebalance PASS explicitly says the patch traces
  "assignment, store visibility, recovery, and ongoing iteration"; the
  failed-group-table PASS keeps a table open until outstanding answers arrive.
  Sources: `digest/kh7bfzrhqd-after-a-rebalance-our-tables-still-show-cx.md`,
  `digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-cx.md`.
- examples: silences, "Intermediate transition cleared the marker needed for
  quiet recovery" (SQ Comp High x2, **Map**, F12); snapshot v2, "Partial
  partition shrink left stale metric series" (F63); kscb v4, "Restart-mode
  handoff derived accounting from already-left source state" (E138); AR S2
  silences, "suppressing delivery also skipped per-module reset bookkeeping"
  (**Catalog**, row 32).
- count: 18 recorded Catalog CLN-family instances; solution records include
  F9, F12, F32, F36, F53, F63, F66, F68, F75, F101--03, F121, F134, F138.

### SQ-03 In-flight work can overwrite cleanup or use retired state
- check / rule / site severity: SQ comprehensiveness High or code quality
  High; AR S1 High (including the site's repeated six-line metric findings);
  AR S2 Medium when the race is a secondary default/configuration effect.
- trigger: deletion, replacement, cache invalidation, reload, or rebalance is
  considered complete while an earlier async read, callback, scrape, send, or
  worker can still publish old state, dereference a removed entry, or act on a
  stale generation.
- how to detect locally: pause a pre-operation worker immediately before its
  writeback/commit, execute the invalidating operation, then resume it.  Check
  that the old result cannot reappear, and that a removed object cannot be
  dereferenced.  Require a lock, generation/epoch check, join, or equivalent
  ordering barrier that covers the final publication, not only the initial
  lookup.
- what the site accepted instead (the PASS side): reference patches that
  synchronize ownership/lifecycle state rather than simply deleting a map
  entry.  The snapshot PASS says workers are paused before shared-state reads
  or replacement and evaluator invalidation is synchronized with in-flight
  queries; the Docker proxy PASS uses a "per-container synchronized ledger."
  Sources: `digest/kh79vwdcg6-persist-in-memory-storage-across-restart-cx.md`,
  `digest/kh7d92724b-docker-proxy-writes-leftover-through-changes-cx.md`.
- examples: snapshot v3 + FP, "In-flight evaluation repopulated invalidated
  cache" (SQ High x2, **Map**, F65); snapshot AR S1, "In-flight scrape
  recreated deleted metric series" (x6, F74); reload, "Global config replaced
  while unlocked readers ran" (SQ CQ High, F106); reload AR S2, "defaults
  written after the protecting lock is released" (**Catalog**, row 118).
- count: 27 Catalog CON-family instances; the recurrent solution pattern is
  explicitly counted as SQ x2/AR S1 x6 in both snapshot and reload history.

### SQ-04 Validation and reload boundaries are not atomic or complete
- check / rule / site severity: SQ comprehensiveness High; AR S1 High for an
  accepted invalid document/baseline, and code quality High when global
  readers can observe a partly-installed configuration.
- trigger: validation filters or omits a declared category, validates against
  mutable live state, mutates a layer rollback does not restore, mistakes
  defaults for explicit configuration, or compares only direct rather than
  derived/referenced settings.
- how to detect locally: enumerate every config section and indirect
  dependency; run malformed, removed, renamed, and dependent-only changes.
  Snapshot the running configuration, attempt a rejected reload, and prove
  every public reader still sees exactly the old configuration.  Then run a
  valid rename/removal/re-add and verify all keys are freshly resolved.
- what the site accepted instead (the PASS side): validation/reconciliation is
  explicit and in-place.  The reload digest credits "rejected configurations
  are restored" and the stale SQ report still praises its "configuration
  validation and in-place storage reconciliation" except for the proven race.
  Source: `digest/kh77h1dpdc-reload-cluster-consumer-and-storage-sett-cx.md`.
- examples: reload wip5, "Marker-less malformed config entries skipped
  validation" (SQ Comp High, **Map**, F104); reload wip5, "Change detection
  omitted referenced configuration sections" (F105); reload wip10, "Renamed
  storage module reused startup-captured root" (F112); reload AR S1,
  "baseline re-read from disk instead of captured running state" (**Catalog**,
  row 120).
- count: at least 12 solution-side records (F7, F33, F104--05, F108--10,
  F112--13, F120, E184--86; repeated adjudications are not inflated).

### SQ-05 Decoder accepts syntactically or semantically invalid input
- check / rule / site severity: SQ comprehensiveness High for trailing data,
  explicit/null nested values, or internally inconsistent state; Medium for a
  missing required member.  AR S1 High when later code panics from accepted
  inconsistency.
- trigger: decoding accepts a prefix only, maps null/absence to a zero value,
  omits required fields, or accepts cross-field data that downstream code
  assumes is consistent.
- how to detect locally: test trailing bytes, top-level null/array/scalar,
  nested null, omitted required members, duplicate/ambiguous envelopes, and
  inconsistent references.  After a successful decode, run ordinary later
  reads/operations; a real finding is acceptance that violates the written
  input contract or produces an invalid internal state.
- what the site accepted instead (the PASS side): strict representation and
  semantic validation before state is applied.  The snapshot PASS calls out a
  snapshot "strictly decoded before wrong-variant"; the conditional-write
  PASS handles the post-check race by rolling back a new version before
  returning the rejection.  Sources: `digest/kh79vwdcg6-persist-in-memory-
  storage-across-restart-cx.md`,
  `digest/kh7dgy3tmn-conditional-writes-leave-refused-data-be-cx.md`.
- examples: silences, "Decoder accepted trailing JSON data" (SQ Comp High,
  **Map**, F10); silences wip49, "Explicit null was treated as field omission"
  (F18); snapshot v29, "Nested null erased cluster state" (F71); snapshot AR
  S1, "Inconsistent accepted document later caused panic" (F73).
- count: 7 recorded instances (F10, F15, F18, F69, F71, F73, plus the related
  envelope collision F100); F15 is a historical SQ PASS, not a reproduced
  site finding, so it is calibration-only.

### SQ-06 Identity, ownership, and comparison keys collapse distinct things
- check / rule / site severity: SQ comprehensiveness High or Medium; solution
  PASS review must not flag a collision merely because labels or names look
  similar.
- trigger: identity is computed from an incomplete key, a current owner is
  re-resolved instead of retained, a historical value is recomputed rather
  than preserved, or a broad pattern/metric key collides across kinds.
- how to detect locally: construct same-name/different-kind, renamed,
  overlapping-pattern, stale-versus-current-owner, and reordered-history
  cases.  Compare keys at every storage, cache, metric, and handoff boundary.
- what the site accepted instead (the PASS side): a complete semantic identity
  and explicit distinction between kinds.  The Docker proxy PASS compares
  content, type, permissions, and ownership; the group-table PASS tracks
  accepted values per key and ordering rather than one global result.  Sources:
  `digest/kh7d92724b-docker-proxy-writes-leftover-through-changes-cx.md`,
  `digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-cx.md`.
- examples: kscb, "Same-name objects of different kinds shared metric
  identity" (SQ Comp Medium, **Map**, F137); kscb, "Later event double-tracked
  pod instead of preserving current owner" (F134); silences FP upheld,
  "whole-name regex built on leftmost-first first match" (**Catalog**, row
  60); snapshot FP, "one-shot flag shared across instances" (**Map**, F98).
- count: at least 6 directly recorded identity/comparison records (F11, F60,
  F95--98, F100, F134, F137--38); the Catalog's IDN family reports 4 rows and
  4 instances, while the overlap/ownership cases are catalogued under CLN/CMP.

### SQ-07 Durability and acknowledgement order is wrong at lifecycle edges
- check / rule / site severity: SQ comprehensiveness 1--2/3, often High;
  AR S1 when a policy/barrier promise is violated.
- trigger: a send/ack/error/revoke/shutdown path advances durable/local state
  before the required external acknowledgement, loses an accepted result after
  ownership changes, or fails to settle a future so rollback never runs.
- how to detect locally: make a scenario table for send-before-future-error,
  accepted-then-revoked, manual-ack-before-copy, cancellation, stop-before-
  first-iteration, and shutdown with buffered work.  Use the repository's
  real producer/buffer where the contract depends on framework timing.
- what the site accepted instead (the PASS side): state is tracked from handoff
  through acknowledgement and shutdown.  The buffered-commit PASS says the
  consumer flushes before commit and shutdown drains records before client
  close; the table-write PASS keeps outstanding answers in the lifecycle.
  Sources: `digest/kh7ephrm9g-commits-go-ahead-even-when-buffered-chan-cx.md`,
  `digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-cx.md`.
- examples: T5 wip11, "Durable state advanced before producer
  acknowledgement" (SQ CQ 2/3, **Map**, E055); T5 wip17--18, "Refused change
  remained live across rebalance" (SQ Comp 1/3, E057); T11 wip35, "Explicit
  ack plus await committed before copy" (SQ Comp 1/3 High, E150); T11 wip37,
  "Manual ack could precede copy" (SQ Comp 2/3, E153).
- count: at least 10 specific solution records (E011, E037--40, E054--57,
  E061--62, E149--53); several are a single shared timing/hold class, not
  independent design requirements.

### SQ-08 Equivalent implementation paths drift apart
- check / rule / site severity: SQ comprehensiveness or code quality; High
  when the drift leaves a supported runtime path wrong, Medium/2 of 3 when
  excluded or stale implementation state remains.
- trigger: a change updates one of generated/source, compiled/interpreted,
  synchronous/threaded, primary/secondary transport, or normal/fast paths but
  not its behavioral twin.
- how to detect locally: inventory all declared equivalents from build config
  and call graph.  Run or statically compare each twin with the same contract
  table; check generated artifacts against their source rather than editing
  generated output by hand.
- what the site accepted instead (the PASS side): twins and public interfaces
  are deliberately updated together.  The live-reader PASS says Python and
  Cython hot paths/interfaces are updated; the concurrency-strategy PASS says
  generated bundles track source changes.  Sources:
  `digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md`,
  `digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md`.
- examples: T7 wip47, "Compiled ack twin retained old behavior" (SQ FAIL,
  **Map**, E087); T7 wip56, "Inlined compiled ack failed to release hold"
  (SQ High, E100); T11 wip21--22, "Enabled transport lacked generation
  identity for barrier" (SQ FAIL twice, E136); hatchet, "generated code
  hand-edited out of sync with its source" (SQ Comp+Code High, **Catalog**,
  row 148).
- count: 6+ recorded twin/generated-path instances (E066, E083, E087, E100,
  E136--38, Catalog 148); E083 is an excluded-scope cleanup finding and is
  retained only as a general path-parity signal.

### SQ-09 A correct result is obtained only after unacceptable foreground work
- check / rule / site severity: SQ code quality Medium (2/3) when the defect
  is a material responsiveness/performance concern rather than a wrong final
  result.
- trigger: an interactive or cancellable path performs whole-input processing
  before returning a usable partial result, despite an existing bounded or
  streaming path establishing the expected responsiveness.
- how to detect locally: compare time to first useful output/cancellation with
  the analogous normal path using a large valid input.  Verify whether a full
  traversal is semantically necessary before the first result.
- what the site accepted instead (the PASS side): substantial decompression
  work is acceptable when it preserves correctness and cache/refresh
  semantics; it is not accepted as an excuse to block the first preview.
  The latest gzip SQ report gives comprehensiveness 3/3 while awarding code
  quality 2/3 solely for full-stream foreground decode.  Source:
  `digest/kh76ppnav0-preview-gzip-compressed-files-like-the-f-cx.md`.
- examples: gzip preview latest, "Text previews wait for a full gzip decode
  before rendering" (SQ quality Medium, same digest); older gzip, "Same-size/
  same-time replacement retained stale preview" (SQ Comp 2/3 Medium,
  **Map**, E194).
- count: 2 directly recorded solution-side instances; this is a
  single-instance severity pattern for foreground latency.

### SQ-10 Code quality is checked against actual repository conventions
- check / rule / site severity: SQ code quality High for enabled lint/doc
  violations or unsafe concurrent wrong-variant; Medium for swallowed errors and
  error-string rules; Low for headers, displaced comments, and contradictory
  docs.
- trigger: newly introduced code violates a configured formatter/linter/type
  convention, makes a false public comment, swallows an error, leaves stale
  assertions/docs, or mutates shared state without the lock discipline the
  repository requires.
- how to detect locally: read configured quality gates, then inspect only new
  and adjacent changed code for exported API docs, comment attachment, error
  propagation, headers, literals, formatting/type rules, and synchronized
  wrong-variant.  Run the configured gate when it is available; do not infer a
  violation from a style preference absent from configuration.
- what the site accepted instead (the PASS side): focused changes using local
  abstractions, documented exported API where needed, no unrelated/debug/
  generated churn, and no visible configured-gate violation.  This wording is
  repeated in the Docker proxy, SQLite store, materialized-view, and
  conditional-write SQ PASS reports.  Sources: `digest/kh7d92724b-docker-
  proxy-writes-leftover-through-changes-cx.md`,
  `digest/kh71zcezmf-add-a-sqlite-table-store-sqlite-with-per-cx.md`,
  `digest/kh717sntzs-materialized-views-reject-not-in-subquer-cx.md`,
  `digest/kh7dgy3tmn-conditional-writes-leave-refused-data-be-cx.md`.
- examples: silences, "Exported symbols lacked required documentation" (SQ CQ
  High, **Map**, F8); silences, "Persistence errors were swallowed while
  reporting success" (SQ CQ Medium, F9); snapshot, "New file omitted package
  license header" (SQ CQ Low x2, F64); reload, "Capitalized new error violated
  enabled lint rule" (SQ CQ Medium, F116).
- count: 20 lint/type/docs CQ records in **Map**'s class L; Catalog examples
  show High (F8/F13/F17), Medium (F9/F116), and Low (F64/F107/F135).

### SQ-11 Reference artifact is the wrong change, or changes beyond scope
- check / rule / site severity: SQ blocker for a wrong solution patch; High
  for generated-source divergence; code quality 2/3 when a patch changes an
  excluded mode; not a correctness finding where the site has no contract
  evidence.
- trigger: the submitted patch targets a different repository/task, manually
  diverges from generated source, or alters explicitly excluded behavior while
  implementing the requested feature.
- how to detect locally: verify patch root, repository identity, changed-file
  inventory, and generated-file provenance before semantic review.  Diff the
  excluded modes against baseline and verify that any changed behavior is
  required by a shared integration point.
- what the site accepted instead (the PASS side): task-focused production and
  documentation files, with generated bundles only when they correspond to
  source changes.  The concurrency-strategy PASS explicitly accepts generated
  bundles that "track the source changes."
- examples: kscb, "Burrow solution patch pasted into kscb" (SQ Blocker x2,
  **Map**, F136); hatchet, "generated code hand-edited out of sync with its
  source" (**Catalog**, row 148); T2 v10, "Watermark implementation changed
  excluded modes" (SQ CQ 2/3, **Map**, E025); T7 wip42, "Excluded
  second-transport patterns still drew quality finding" (E083).
- count: 4 distinct recorded artifact/scope instances (F136, Catalog 148,
  E025, E083), with F136 explicitly rerun twice.

### SQ-12 A reported issue is contested or not reproduced
- check / rule / site severity: contested SQ/AR claims are not defects until
  the alleged code path and contract premise are reproduced.  They must not
  lower a local score merely because a reviewer asserted them.
- trigger: the report follows a base method rather than an override, claims a
  line/type/regex/framework behavior absent from the submitted code, or
  assumes behavior that the baseline itself does not have.
- how to detect locally: reproduce the exact stated scenario against the
  concrete dispatch target and baseline/reference semantics.  Quote the
  contract and show the observation.  If the premise fails, record it as
  contested with evidence; do not apply a speculative fix.
- what the site accepted instead (the PASS side): concrete trace evidence and
  restrained scope.  Multiple later digest SQ PASS reports use the language
  "no definite gap" / "no concrete defect" rather than treating complexity as
  proof.  Sources: `digest/kh7d92724b-docker-proxy-writes-leftover-through-
  changes-cx.md`, `digest/kh7aemqd7d-back-forward-history-and-remembered-
  sele-cx.md`.
- examples: T7 wip35, "Judge used base broadcast method despite override"
  (SQ false High, **Map**, E079); T7 wip56, "Iterable typing allegation did
  not reproduce" (SQ false typing claim, E101); T7 wip56 rerun, "Nested-regex
  allegation did not reproduce" (SQ contested Medium, E103); T11 wip39,
  "Judge required take decode error to abrupt stop unlike base" (AR contested
  High, E155).
- count: at least 8 explicit contested/not-reproduced solution claims (E019,
  E063, E079, E101--03, E108, E131, E155); they are calibration examples, not
  true-finding counts.

## PASS patterns

1. **End-to-end contract coverage earns 3/3.**  The site accepts solutions
   that connect input, state, recovery/shutdown, and public output rather than
   solve a single happy path.  The table-write review says the patch handles
   "multiple outstanding writes per key" and shutdown; the SQLite review says
   it covers lifecycle, recovery, exactly-once, and overlapping-name paths.
   Sources: `digest/kh7b3n5g5r-failed-group-table-writes-stay-in-the-pr-
   cx.md`, `digest/kh71zcezmf-add-a-sqlite-table-store-sqlite-with-per-cx.md`.
2. **A large patch is not itself a quality problem.**  It passes when each
   changed layer is necessary and connected: the live-reader review calls a
   broad patch "task-focused," and the concurrency review accepts a large
   patch with named helpers and comments.  Sources: `digest/kh70afkwq3-
   streams-that-start-or-stop-while-the-wor-cx.md`,
   `digest/kh75aj75cn-concurrency-strategies-act-on-the-whole-cx.md`.
3. **Explicit exclusions and unsupported branches may remain unchanged.**
   The accepted live-reader solution leaves a non-default transport unsupported
   because that does not contradict the stated scope; the buffered-commit
   solution preserves excluded modes' prior path.  Sources:
   `digest/kh70afkwq3-streams-that-start-or-stop-while-the-wor-cx.md`,
   `digest/kh7ephrm9g-commits-go-ahead-even-when-buffered-chan-cx.md`.
4. **Concurrency is accepted when final publication is coordinated.**  The
   snapshot PASS pauses workers and synchronizes cache invalidation; the
   Docker proxy PASS uses synchronized per-container state.  Source files as
   in SQ-03.  A local reviewer should look for an actual stale-write
   interleaving, not report a generic "race" from asynchronous code.
5. **Existing abstractions and localized changes are strong CQ evidence.**
   PASS reports repeatedly credit reuse of table/store, filesystem/proxy,
   planner, or middleware abstractions and task-local files, while rejecting
   unrelated/debug/generated churn.  Examples: Docker proxy, materialized
   views, conditional writes (sources in SQ-10).
6. **Configured gates—not taste—define convention defects.**  PASS reports
   explicitly inspect project gates (for example rustfmt/clippy, flake8/mypy,
   ESLint) and say "no visible configured-gate violation."  Do not raise a
   lint/S4-like issue without the gate or a repository convention.
7. **Score 2/3 can coexist with broad correctness.**  The gzip review assigns
   comprehensiveness 3/3 and code quality 2/3 for one material foreground
   latency concern; the stale reload report assigns comprehensiveness 1/3 but
   still credits broad, readable, in-scope work.  Sources:
   `digest/kh76ppnav0-preview-gzip-compressed-files-like-the-f-cx.md`,
   `digest/kh77h1dpdc-reload-cluster-consumer-and-storage-sett-cx.md`.

## Severity calibration

| Situation | Platform calibration | Evidence |
|---|---|---|
| A stated behavior has a reproducible counterexample that loses data, accepts invalid state, leftover stale observable state, or lets retired work publish | SQ Comp High / AR S1 High; 1/3 where the gap is material despite broad work | F10, F12, F63, F65, F70--74, F104--05; E150; **Map** |
| A missing path is real but principally a bounded semantic edge or required field | SQ Comp Medium; often 2/3 rather than failure of all work | F11, F69, F110--11, F137; E194; **Map** |
| The final behavior is correct but an interactive path blocks on avoidable whole-input work | SQ Code Quality Medium / 2 of 3 | gzip full-decode finding, `digest/kh76ppnav0-preview-gzip-compressed-files-like-the-f-cx.md` |
| An enabled lint/type/doc rule is violated | High if it affects exported docs, concurrency, or repeated configured lint; Medium for error handling/string rule; Low for header/comment/docs mismatch | F8/13/14/17 High; F9/116 Medium; F64/107/135 Low; **Map** |
| Wrong repository patch or source/generated divergence | SQ blocker (wrong patch) or High (generated divergence) | F136; Catalog 148 |
| An AR solution defect reintroduces deleted state or accepts invalid state | S1 High; six repeated output lines remain one race class with multiplicity | Catalog rows 73--74, 117, 120--21 |
| A secondary synchronization/default bookkeeping concern with otherwise sound design | AR S2 Medium/High, depending on whether it suppresses required future behavior | Catalog row 32 (High) and row 118 (Medium) |
| No reproduced contract breach; issue rests on a mistaken dispatch/baseline/type premise | contested/not reproduced; do not deduct | E079, E101--03, E155, **Map** |

No permitted source records an AR solution-side S3 finding.  The only S4
solution-like record is a human-review low-severity loop-guard readability
finding (Catalog row 54), not an Auto Review solution-band precedent.  The
local replica should therefore reserve S3/S4 labels for their rubric meanings
and avoid inventing a historical threshold.
