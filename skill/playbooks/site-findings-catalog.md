# Site findings catalog (platform verdicts pasted 2026-09-26 .. 2026-10-04)

Purpose: every finding the platform raised on our challenge work, abstracted so a reviewer can hunt for the same
violation in a new task before pasting. Source: user-pasted platform output in the OSS session transcripts (main
sessions only; subagent transcripts hold no site output), plus `burrow-config-reload/STATUS.md`,
`burrow-config-reload/eval/review-triage-wip11.md`, `burrow-snapshot-v30-final/eval/site-findings.md` and the
per-repo playbooks. Exact reruns of one report are counted once (noted `xN`).

Tasks covered (8):
- **rdb-diff**: HDT3213/rdb RDB diff (task 034).
- **silences**: linkedin/Burrow notification silences.
- **snapshot**: linkedin/Burrow #781 storage snapshot/restore.
- **reload**: linkedin/Burrow #751 SIGHUP config reload (current task).
- **kscb**: google/kube-startup-cpu-boost NamespaceStartupCPUBoost (task 037).
- **fake-gcs**: fsouza/fake-gcs-server #1040 data protection (similarity gate only).
- **openfermion**: honeycomb lattice (similarity gate only).
- **hatchet**: retry-after (an SQ report the user pasted asking "is this our one?"; kept for the pattern).

Check names used below: **TQ** = Test Quality; **SQ** = Solution Quality; **AR** = Auto Review (multi-agent,
rubric T1-T8 / S1-S4 / P1-P4); **HR** = human reviewer revision; **FP** = false-positive panel (adjudicator +
judges); **VS** = Verify Solution; **VF** = Verify Flakiness; **PRE** = precheck gates ("Problem and tests are
good quality", "Problem description contains only necessary information", "Problem and tests are aligned");
**DQ/TPQ** = Description / Task Prompt Quality; **RUN** = per-run verdict (Test Broken / Test Mismatch);
**SIM** = similarity (plagiarism) gate.

Severity column: blocker/High/Medium/Low as the site printed it; `unfair` for TQ unfair tests; `adv` for TQ
advisory partials; `FAIL`/`WARN` for gates.

---

## 1. Findings by task

Family codes (section 2): CON concurrency/in-flight, COV coverage hole, CLN stale cleanup/lifecycle,
HAR harness/base/timing, DSC description, PIN unfair pinning, DEC lenient decoding, CFG validation boundary,
CMP wrong measure/compare, LNT lint/convention, IDN identity collision, OPS ops/process.

### 1.1 rdb-diff (6)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 1 | PRE tests-quality | coverage | WARN | first-class feature named in the description has no test | stream diff, hash field-expiry, stdout without -o, -expire/-size filters untested | COV |
| 2 | PRE necessary-info | desc | WARN | description states defaults the repo already implies | "writing to stdout without -o", "read with this package's decoder", "empty path is an error" | DSC |
| 3 | PRE aligned | interface | WARN | test pins a literal token the text only names in prose | text says "sorted set", test expects type "zset" | PIN |
| 4 | VS | harness | FAIL | new test package compiled/ran in base mode, so it is neither p2p nor f2p | `diff_5bb924 [build failed]` in the run without solution.patch | HAR |
| 5 | VS | harness | FAIL | reference fails its own new tests on the platform image | TestDiffBinaryEverywhere/BinaryStrings fail with solution applied | HAR |
| 6 | TQ | adv | adv | output normalized before comparison makes a literal-format promise non-discriminating | JSON unmarshaled before compare, so `\u00XX` escape spelling never enforced; CLI flags untested | COV |

### 1.2 silences (56)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 7 | SQ | Comp | High | validation done on one endpoint but not its sibling | list `?cluster=unknown` returns 200; only create calls clusterExists | CFG |
| 8 | SQ | Code | High | new exported symbols without doc comments against enabled revive `exported` | Silence/SilenceStore/... undocumented; MarshalJSON comment displaced onto UnmarshalText | LNT |
| 9 | SQ | Code | Medium | persistence error swallowed on some mutations, success reported | `_ = store.save()` in Update/Remove | CLN |
| 10 | SQ | Comp | High | decoder accepts trailing data after the first JSON value | `{"cluster":"known","duration":"1h"} trailing` creates a silence | DEC |
| 11 | SQ | Comp | Medium | "matches all" pattern is not truly universal | empty group compiled to `.*` misses names with `\n` (needs `(?s:.*)`) | CMP |
| 12 | SQ x2 | Comp | High | lifecycle marker cleared on an intermediate transition | WARN muted, ERR clears SilencedBy, OK sends a noisy close | CLN |
| 13 | SQ x2 | Code | High | doc comment names the wrong identifier (revive exported) | `// Match ...` sits above `Matching` | LNT |
| 14 | SQ | Code | High | new mutable state written under a read lock in a concurrent handler | SilencedBy map written under cluster RLock, `concurrent map writes` | CON |
| 15 | SQ (PASS) | Comp | Medium | top-level JSON `null` decoded into a struct is accepted | PUT body `null` = 200 no-op update | DEC |
| 16 | SQ (PASS) | Code | Medium | store returns shallow copies that alias internal slices | callers mutate `Statuses[0]` outside the lock | CON |
| 17 | SQ | Code | High | repeated literal against enabled goconst (min-occurrences 3) | "silence not found" x3 in handlers | LNT |
| 18 | SQ | Comp | High | explicit null treated as "field omitted" | `{"until":null}` PUT = 200; `duration`+`until:null` POST accepted | DEC |
| 19 | TQ | unfair x4 | unfair | response envelope stated for one verb pinned on others | detail GET / PUT must return object under top-level `silence` (text said POST only) | PIN |
| 20 | TQ | unfair | unfair | test pins an eager-initialization lifecycle choice | Start must leave app.Silences non-nil after return | PIN |
| 21 | TQ | unfair | unfair | rule scoped to one verb asserted on another | "exactly one of duration/until" stated for POST, test demands 400 on PUT | PIN |
| 22 | TQ | unfair | unfair | unstated transactional guarantee pinned | failed Add must leave no in-memory entry (rollback never stated) | PIN |
| 23 | TQ | unfair x3 | unfair | explicit-empty vs omitted JSON members pinned | `statuses`/`comment` keys must exist when empty (`omitempty` equally valid) | PIN |
| 24 | TQ | unfair | unfair | query-parameter spelling not stated | test uses `?group=`, text said "groupname" | PIN |
| 25 | TQ | unfair | unfair | persistence encoding pinned | on-disk bytes must satisfy json.Valid; format never stated | PIN |
| 26 | TQ | unfair | unfair | "malformed file" built from format-specific bytes | `{not json` must fail load; corrupt an implementation-written file instead | PIN |
| 27 | TQ | adv | adv | suite-wide internal coupling and wall-clock tolerances | notifier tests call private checkAndSendResponseToModules; 1-5 s windows | HAR |
| 28 | AR Tests | T3 | High | assertion accepts two statuses where the spec distinguishes them | missing-cluster POST may return 404 or 400; spec says bad input = 400 | COV |
| 29 | AR Tests | T4 | Medium | alternate input form tested on create only | PUT never exercises absolute `until` | COV |
| 30 | AR Tests | T3 | Medium | response-shape key not required (conflicts with #23) | POST reply may omit `statuses` | COV |
| 31 | AR Tests | T4 | Medium | replace-with-nonempty branch untested | PUT `statuses:["ERR"]` could store empty and pass | COV |
| 32 | AR Sol | S2 | High | suppressing delivery also skipped per-module reset bookkeeping | quiet recovery leaves LastNotify, send-once blocks next incident | CLN |
| 33 | AR Sol | S1 | High | validation placed in a lower layer than the contract allows | store Add rejects zero Until; contract says "accepts any Until" | CFG |
| 34 | AR Tests / HR | T3/T4 | High | fixtures inject the dependency, so production wiring is never exercised | every test assigns App.Silences; nothing runs Start with it nil | COV |
| 35 | AR Tests / HR | T3/T4 | High | error branch of a loader untested | LoadSilenceStore on malformed existing file never asserted to error | COV |
| 36 | AR Sol / HR | S1 | High | stateless re-match on recovery ignores what actually muted the incident | WARN-only silence, OK not listed, orphan close sent | CLN |
| 37 | AR Tests | T3/T4 | High | test inputs cannot tell "muted this incident" from "some live silence covers it" | wrong impl suppresses every OK close while any covering silence lives | COV |
| 38 | AR Desc | P4 | Low | one sentence packs endpoint scope, restrictions and shapes | semicolon-heavy API sentence | DSC |
| 39 | AR Desc x2 | P4 | Medium | subtle lifecycle rules in pronoun-heavy nested sentences | "While one applies ... one recovering meanwhile ..." | DSC |
| 40 | AR Tests x2 | T3/T4 | Medium | accepted value only round-tripped, never applied at runtime | `statuses:["OK"]` serialized but no OK-only silence evaluated | COV |
| 41 | AR Tests x2 | T3/T4 | Medium | ordering promise checked only after the function returns | Start init "before running" observed after Start returned | COV |
| 42 | AR Tests / HR | T3/T4 | High | concurrency promise tested by an outcome that races cannot change | all-silenced burst asserts 0 notifications; no -race, no state check | COV |
| 43 | AR Tests / HR | T2 | Medium | fixed polling deadline plus unsynchronized reads | TestStart_SilencesUsableWhileRunning 500 x 10 ms poll | HAR |
| 44 | AR Tests | T3/T4 | High | failure path asserts the error but not the state | failed Add still visible in List (after #22, text was changed to state rollback) | COV |
| 45 | AR Tests / HR x2 | T2 | Medium | test sleeps until a real deadline passes | `time.Sleep(time.Until(until)+1s)` in two expiry tests | HAR |
| 46 | AR Tests | T3/T4 | High | a later operation's flush masks a missing save | DELETE saves the map, hiding an Update that never persisted | COV |
| 47 | AR Tests | T3/T4 | High | state transition entered mid-lifecycle untested | open ERR, later WARN-only silence mutes, OK must close quietly | COV |
| 48 | AR Tests / HR | T3/T4 | High | cleanup hook of a new metric never exercised | consumer delete must drop `burrow_kafka_consumer_silenced` | COV |
| 49 | AR Tests | T3/T4 | High | visibility rule enforced in one surface only; a real passer proved it | list returns raw GetAll incl. expired; 2 passers | COV |
| 50 | HR | T3/T4 | Medium | "always new" promise tested only from the empty case | Add given ID "caller" may keep it | COV |
| 51 | HR | T3/T4 | Medium | clear-to-empty update untested | PUT `{"comment":""}` must clear | COV |
| 52 | HR | T3/T4 | Medium | metric reset path untested | gauge 1 must drop to 0 after silence removed | COV |
| 53 | HR | S1 | High | only one of several overlapping causes remembered | single SilencedBy ID; deleting it while another muting silence lives sends close | CLN |
| 54 | HR | S4 | Low | guard inside a loop reads as per-item but is whole-loop | `if silenced { break }` first statement in module loop | LNT |
| 55 | PRE necessary-info | desc | WARN | error returns, examples and type qualifiers flagged as defaults | "also returns an error", `like "2h"`, "must never crash", `string` qualifiers | DSC |
| 56 | PRE necessary-info | desc | WARN | redundant restatement of a rule already given elsewhere | "and doesn't show up anywhere"; clause after race-free | DSC |
| 57 | DQ x2 | desc | FAIL | description too prescriptive (cannot be contested) | implementation-shaped sentences; rewrite as behavior | DSC |
| 58 | RUN | Test Mismatch | FAIL | phrase with two readings; verifier picks one | "no longer used and shown": expired silences listed vs hidden (49/51) | DSC |
| 59 | FP/agent | edge | n/a | underspecified status on a corner op | DELETE of ended silence: ours 404, 3 passers 200; ruled underspecified | PIN |
| 60 | FP | upheld | High | whole-name regex built on leftmost-first first match | pattern `orders` OR `orders-eu` vs name `orders-eu` fails (FindStringIndex) | CMP |
| 61 | FP | upheld | Medium | new map mutated in a goroutine-per-response path | MutedSilences write, `fatal error: concurrent map writes` 3/3 | CON |
| 62 | FP | note | n/a | agent-run blind spot (not a defect report) | 7/10 runs rejected omitted `group` (empty = all) | DSC |

### 1.3 snapshot (37)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 63 | SQ x2 | Comp | High | metric series removed only when the whole entity disappears, not on partial shrink | retained topic loses partition 1; its gauges stay | CLN |
| 64 | SQ x2 | Code | Low | new source file without the package's license header | core/internal/storage/snapshot.go | LNT |
| 65 | SQ x2 | Comp | High | cache delete is not a barrier against in-flight work | miss computes old status, stores it after invalidation | CON |
| 66 | SQ | Comp | High | handler skips "incomplete" items, so old series are never overwritten | 1-of-5 history after PUT keeps old offset/status gauges | CLN |
| 67 | SQ (PASS) | Code | Low | raw-write path bypasses the shared response helper | GET export skips CORS header from writeResponse | LNT |
| 68 | SQ | Comp | High | sentinel zero treated as "expired" by an unchanged lazy path | owner-only group (lastCommit 0) purged on first read | CLN |
| 69 | SQ | Comp | Medium | document accepted with a required member missing | `{"version":1}` = 200 empty restore | DEC |
| 70 | SQ | Comp | High | global replace routed like one ordinary request in a hashed worker pool | restore on random worker; delayed commit recreates replaced group | CON |
| 71 | SQ | Comp | High | nested null decoded as zero value and applied | `{"clusters":{"alpha":null}}` erases alpha, 200 | DEC |
| 72 | SQ | Comp | High | startup reconciliation not ordered against ingestion on another worker domain | topic delete runs after a fresh commit was stored | CON |
| 73 | AR Sol | S1 | High | internally inconsistent document accepted, later read panics | commits for a partition with empty broker history | DEC |
| 74 | AR Sol x6 | S1 | High | in-flight scrape republishes series deleted by the operation | /metrics holds old status, Set() after PUT cleanup (6 gauge lines) | CON |
| 75 | SQ-style | S1 | High | cleanup keyed on entities still present misses lazily-expired ones | topic_partition_status left when its group expired before PUT | CLN |
| 76 | AR Tests x3 | T1 | High | base mode excludes existing tests of the very function the task modifies | 3 maybeUpdateMetadataAndDeleteTopics tests excluded | HAR |
| 77 | AR Tests x2 | T3/T4 | High | directional rule tested only on one side | shrink and equal tested, growth never; `!=` impl passes | CMP |
| 78 | AR Tests x2 | T3/T4 | Medium | fixture correlates two ordering keys | Order and Timestamp rise together, so sort-by-timestamp passes | COV |
| 79 | AR Tests x2 | T2 | Medium | unbounded wait on the wall clock | loop until Unix second changes | HAR |
| 80 | AR Tests x2 | T8 | Medium | base harness ignores package-discovery failure | `go list ./...` exit status discarded | HAR |
| 81 | TQ | unfair | unfair | status code pinned for an unenumerated rejection; repo precedent differs | unknown `mode=` must be 400; repo uses 404 for unknown enum | PIN |
| 82 | TQ x2 | unfair | unfair | malformed-input cases depend on an undocumented schema | top-level null/array, numbers turned to "x" | PIN |
| 83 | TQ | adv | adv | suite-wide port bind-close-rebind TOCTOU; new-mode file list incomplete | start5ad239; topic_refresh test not selected | HAR |
| 84 | TQ x3 | adv | adv | "including on failure" promise has no failure-path test | sidecar files after failed write | COV |
| 85 | TQ | adv | adv | "valid json in our format" stays partial | can't be fully covered without pinning format | DSC |
| 86 | PRE tests-quality | behavior | FAIL | test drives unexported method and internal flags | topic_refresh test pokes maybeUpdateMetadataAndDeleteTopics | HAR |
| 87 | PRE tests-quality | sanity | FAIL | test.sh new_files omits one new test file | base runs it, new mode skips it | HAR |
| 88 | PRE tests-quality | sanity | FAIL | checker rejects a flag it believes unsupported | `go test -skip` flagged; use a positive -run list | HAR |
| 89 | PRE tests-quality | consistency | FAIL | description sentence contradicts a test | "leaving other clusters alone" vs full import empties others | DSC |
| 90 | PRE tests-quality | coverage | WARN | failure-path promise asserted only on success | "never leave other files behind, even if it fails" | COV |
| 91 | PRE necessary-info | desc | WARN | conventions, prefaces and 400-on-invalid flagged as filler | "usual error and message JSON", "restart must be invisible" | DSC |
| 92 | DQ | tone x3 | FAIL | literary/figurative sentences hide independent rules | "comes back exactly as it was, down to every entry" | DSC |
| 93 | TPQ | directive_list | FAIL | endpoint-by-endpoint imperative chain (major) | "A POST to /v3/admin/storage/snapshot writes the file immediately." ... | DSC |
| 94 | RUN | Test Broken | FAIL | unchanged baseline test incompatible with required new behavior | Kafka refresh test hangs on StorageFetchTopics (env blocker: verifier) | HAR |
| 95 | FP | upheld | High | count derived from a filtered subset | len(leader-reachable partitions) vs cap: leader loss deletes topic | CMP |
| 96 | FP | upheld | Medium | ordering applied per bucket instead of globally | merge sorts commits per partition, not by Order across doc | CMP |
| 97 | FP | upheld | Medium | restored marker recomputed instead of restored verbatim | lastCommit = max(saved, newest offset) revives expired group | CMP |
| 98 | FP | upheld | High | one-shot flag shared across instances | global StorageNeedsTopicRefresh cleared by first cluster | IDN |
| 99 | FP | upheld | High | (same as #65) in-flight evaluation repopulates cache | caching.go invalidateCache without RWMutex | CON |

### 1.4 snapshot FP continued and misc (4)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 100 | FP | upheld (7195) / overruled (3410) | High | magic key in decoder collides with a legal user name | cluster named `clusters` unwrapped as envelope, history lost | IDN |
| 101 | FP | upheld | High | import pre-filters by stored state instead of replaying normal ingest rules | merge drops owner of a group whose commit is expired | CLN |
| 102 | FP | upheld | High | restore-only flag never cleared after normal activity | keepUncommitted keeps group forever after first commit | CLN |
| 103 | FP | upheld | Medium | cache invalidation scoped to entities still in storage | lazily-expired group keeps cached 200 after PUT | CLN |

### 1.5 reload (30)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 104 | SQ | Comp | High | entries filtered by a marker key before validation, so malformed ones pass | `[cluster.bad]` without class-name skipped, reload accepted | CFG |
| 105 | SQ | Comp | High | change detection ignores referenced/derived config | `[client-profile.prod]` edit does not restart its clusters | CFG |
| 106 | SQ | Code | High | global config replaced while unlocked readers run | notifier reads viper during ReadConfig | CON |
| 107 | SQ | Code | Low | exported doc comment contradicts new behavior | Start says any signal exits | LNT |
| 108 | SQ | Comp | High | validation on the live global mutates layers the rollback does not restore | SASL PLAIN `viper.Set` override survives rejected file | CFG |
| 109 | SQ | Comp | High | rule applied to some sections but not all the text covers | notifier group-allowlist regex not validated on reload | CFG |
| 110 | SQ (PASS) | Comp | Medium | accumulated defaults make absence look like presence | file without `[storage]` rejected after explicit one | CFG |
| 111 | SQ (PASS) | Comp | Medium | list and detail endpoints use different existence checks | removed cluster still 200 at `/v3/kafka/<c>` (viper.IsSet sees defaults) | CLN |
| 112 | SQ | Comp | High | key captured at start reused after a valid rename | `[storage.old]` -> `[storage.new]` keeps old intervals | CFG |
| 113 | SQ | Comp | High | library Reset clears state the next call needs | viper.Reset drops config type, every reload fails | CFG |
| 114 | SQ | Comp | High | (as #65) in-flight evaluation re-caches after forget | `go getConsumerStatus` stores after cache.Delete | CON |
| 115 | SQ | Comp | High | async consumer dereferences an entry another path deleted | notifier `nc.clusters[c]` nil after cluster removal | CON |
| 116 | SQ | Code | Medium | new error string capitalized against enabled revive error-strings | `errors.New("Error starting " + ...)` | LNT |
| 117 | AR Sol x6 | S1 | High | (as #74) in-flight scrape recreates series after DeleteClusterMetrics | prometheus.go:127-150 | CON |
| 118 | AR Sol | S2 | Medium | defaults written after the protecting lock is released | Configure SetDefault after reload unlock races /v3/config | CON |
| 119 | AR Tests | S1 x2 | High | generation token sampled after enumeration | scrape lists groups, then samples gen; deletion between slips through | CON |
| 120 | AR Sol | S1 | High | baseline re-read from disk instead of captured running state | file swapped before Start disables reload forever | CFG |
| 121 | AR Sol | S1 | High | cleanup of a removed entity misses one subsystem | re-added cluster reuses notifier incident state ("start fresh") | CLN |
| 122 | AR Tests | T3/T4 | High | cached state of a retained entity not asserted after its config changes | changed cluster may drop cached status and metrics and pass | COV |
| 123 | AR Tests | T4 | Medium | stated side effect of rejection (log) not asserted | rejected file must log an error | COV |
| 124 | AR Tests | T2 | High | base mode runs a racy upstream test | zookeeper TestCoordinator_mainLoop lost wakeup, 10 m timeout | HAR |
| 125 | AR Tests | T3/T4 | High | rejection matrix omits one section type; a real passer proves it | notifier `group-allowlist="["` accepted by an all-green run | COV |
| 126 | VF | flaky x5 | FAIL | unsolved-state results differ per run | map-ordered subtests + Fatalf on parent t | HAR |
| 127 | TQ | adv | adv | regex, log and "all info kept" promises partly untested | allowlist regex, log line, changed cluster all info | COV |
| 128 | TQ | adv | adv | suite-wide 15 s polling, fixed sleeps, exact request counts | quiescence inferred from 0.5/2.5 s sleeps | HAR |
| 129 | FP | upheld x2 | High | global config reset without synchronization lets a rejected file apply intermittently | viper.Reset + MergeConfigMap; RejectedFile fails ~25% | CON |
| 130 | FP | upheld (1 of 4) | Medium | (as #105) client-profile not in fingerprint | Nova 3 on wip12 batch | CFG |
| 131 | FP (own replay) | upheld | High | candidate exposed through global readers before validation | /v3/config serves rejected file mid-check (2 FPs, rollout58) | CON |
| 132 | own audit | S3/S4 | n/a | cleanup revert re-broke a probe-justified hunk | reverting SASLHandshakeFirst lost SASL creds in fingerprint | OPS |
| 133 | triage | T1 | High | entry point wiring never exercised | main.go SIGHUP path untested; fixed with real-binary test | COV |

### 1.6 kscb (14)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 134 | SQ | Comp | High | priority re-resolved on every event instead of keeping current owner | later pod event double-tracks pod in namespace and regular boost | CLN |
| 135 | SQ | Code | Low | insertion shifts an existing comment onto the new declaration | `// Name returns ...` above NewNamespaceStartupCPUBoost | LNT |
| 136 | SQ | blocker x2 | blocker | wrong solution.patch pasted | patch touched core/... (Burrow) in kscb repo | OPS |
| 137 | SQ (PASS) | Comp | Medium | metric identity labels collide across two kinds allowed to share a name | same-name regular and namespace boost share series | IDN |
| 138 | SQ | Comp | High | transfer accounting derived from a state the source already left | reverted pod handed off counts total 0 (BOOST_ON_RESTART) | CLN |
| 139 | AR Desc | P4 | Medium | one long sentence compresses several rules | handoff, accounting, restart-retention, expiry | DSC |
| 140 | AR Tests | T3/T4 | High | deletion assertion passes if the series is recreated at zero | namespace metrics deleted vs reset to 0 | COV |
| 141 | AR Tests | T4 | High | controller registration untested (struct tested directly) | SetupWithManager + cmd/main.go wiring omitted, all pass | COV |
| 142 | AR Tests | T4 | High | webhook registration untested | webhook.Setup registers only the old kind | COV |
| 143 | AR Tests | T4 | High | install artifacts untested | CRD/RBAC/webhook/Helm unchanged, all pass | COV |
| 144 | AR Tests | T3/T4 | Medium | one-item fixtures cannot tell per-pod from per-container counts | two one-container pods | COV |
| 145 | AR Tests | T4 | Medium | combination of two tested branches untested | reverted handoff to a regular receiver | COV |
| 146 | AR Tests / TQ | T2 | Low | wall-clock polling in informer tests | 5 s deadlines in synchronizer tests | HAR |
| 147 | rollout | unfair fail | n/a | asserted a side effect on an object that no longer exists | refresh request for a deleted boost (unobservable) | PIN |

### 1.7 other tasks (3)
| # | Check | Item | Sev | Pattern (abstract) | Concrete example | Fam |
|---|---|---|---|---|---|---|
| 148 | SQ (hatchet) | Comp+Code | High | generated code hand-edited out of sync with its source | sqlc `$6::integer[]` vs `bigint[]`, large durations fail | OPS |
| 149 | SIM (fake-gcs) | derivative | WARN | same idea and surfaces as an older submission | soft delete + restore endpoint (conf 0.91) | OPS |
| 150 | SIM (openfermion) | derivative | WARN | same concrete core as an older submission | honeycomb lattice + Kitaev model | OPS |

Totals: **150 findings** (several rows aggregate exact reruns or 6-line metric families), **8 tasks**.

---

## 2. Pattern families (most frequent first)

Ranked by site instances (a row marked xN counts N); rows = distinct catalog entries.

| Rank | Family | Instances | Rows | Row numbers |
|---|---|---|---|---|
| 1 | COV coverage hole lets a realistic wrong impl pass (T3/T4) | 39 | 34 | 1,6,28-31,34,35,37,40-42,44,46-52,78,84,90,122,123,125,127,133,140-145 |
| 2 | CON in-flight async work / unsynchronized shared state | 27 | 16 | 14,16,61,65,70,72,74,99,106,114,115,117-119,129,131 |
| 3 | HAR harness, base mode, timing, flakiness (T1/T2/T8, VS, VF, PRE) | 22 | 17 | 4,5,27,43,45,76,79,80,83,86-88,94,124,126,128,146 |
| 4 | CLN stale cleanup / lifecycle state not reset or not kept | 18 | 16 | 9,12,32,36,53,63,66,68,75,101-103,111,121,134,138 |
| 5 | DSC description style, defaults, ambiguity, contradictions | 16 | 14 | 2,38,39,55-58,62,85,89,91-93,139 |
| 6 | PIN TQ unfair: pinned an unstated choice | 14 | 13 | 3,19-26,59,81,82,147 |
| 7 | CFG validation / rollback boundary incomplete | 11 | 11 | 7,33,104,105,108-110,112,113,120,130 |
| 8 | LNT enabled-linter and repo-convention violations | 11 | 9 | 8,13,17,54,64,67,107,116,135 |
| 9 | CMP wrong measure or comparison | 7 | 6 | 11,60,77,95-97 |
| 10 | DEC lenient input decoding | 6 | 6 | 10,15,18,69,71,73 |
| 11 | OPS process slips | 5 | 5 | 132,136,148-150 |
| 12 | IDN identity / name collision | 3 | 3 | 98,100,137 |

### F1. COV: coverage hole lets a wrong impl pass
Abstract: a stated promise has no assertion that fails for the cheapest plausible wrong implementation. Recurring
sub-shapes:
- failure path asserts the error but not the resulting state (#44, #46, #84);
- test fixtures inject what production must wire (#34, #41, #133, #141-143);
- inputs correlate two variables, so the wrong key also passes (#37, #78, #144);
- a value is round-tripped but never exercised at runtime (#40);
- a combination of two separately tested branches is never exercised (#47, #145);
- a cleanup hook of new state is never driven (#48, #140).

How to hunt:
- For every promise sentence, write the one-line lazy wrong implementation and point to the assertion that kills it.
- After every failure-path assert, assert the state too.
- Run one test with the fixture's injection removed.
- Vary the second key (order vs timestamp, per pod vs per container).
- Check the AR "Wrong impl caught" against a real passer's patch.

### F2. CON: in-flight async work / shared state races
Abstract: an operation deletes or invalidates state while work started earlier (goroutine per request, scrape
handler, hashed worker, notifier refresh) still holds old data and writes it back. Or new mutable state sits under a
read lock or a global config singleton. SQ and AR raise this as S1 High every time and give a concrete pause/resume
interleaving.

How to hunt:
- List every `go` launch, worker-pool hash route and metrics scrape that reads the state being removed.
- For each one, ask: if it read before the delete and writes after, what is visible once the operation returns?
- Use a generation token taken BEFORE enumeration, or a barrier/RWMutex that drains in-flight work.
- Never mutate new maps under RLock.
- Never swap global config while readers are unlocked.
- Run the hidden suite and a probe under -race.

### F3. HAR: harness, base mode, timing, flakiness
Abstract:
- base mode excludes tests of the very function you modify (T1);
- base mode runs a racy upstream test (T2);
- `go list` or build failures are masked (T8);
- new files leak into base or are missing from the new list (VS, PRE);
- tests sleep on wall clocks or poll fixed deadlines (T2);
- subtest order or parent `Fatalf` makes the unsolved state differ per run (VF).

How to hunt:
- Diff the base-mode exclusion list against the functions solution.patch touches.
- Run the unsolved suite 3x and require identical IDs and statuses.
- grep for `time.Sleep`, `time.Until` and fixed poll budgets.
- Check that `go list` and build exit codes propagate.
- Confirm every new test file is in new_files.
- Avoid `-skip` (the precheck model rejects it).

### F4. CLN: stale cleanup / lifecycle state
Abstract: cleanup fires only on whole-entity removal, not on partial shrink, replacement or lazy expiry. Or a
lifecycle marker is cleared too early (escalation), kept too long (restore-only flag), or re-derived statelessly
(re-matching the current status). Re-added entities inherit old state from one subsystem.

How to hunt:
- For each new or removed entity, enumerate every subsystem that caches it (storage, evaluator cache, metrics,
  notifier, HTTP detail endpoints) and check each one is cleared.
- Test shrink, replace-with-fewer and lazily-expired variants.
- Walk a WARN -> ERR -> OK style state machine with overlapping causes.

### F5. DSC: description style and ambiguity
Abstract:
- dense, literary or pronoun-heavy sentences (P4, DQ tone);
- endpoint-by-endpoint imperatives (TPQ directive_list major);
- "too prescriptive" (uncontestable);
- restating defaults (error returns, 400 on bad input, usual envelope);
- phrases with two readings ("used and shown", "groupname");
- a sentence contradicting a test.

How to hunt:
- Read each sentence as a maintainer issue.
- Split compound rules.
- Delete anything the repo already implies.
- For each noun phrase, ask what a solver would name the key.
- Grep the tests for every literal the text implies.

### F6. PIN: TQ unfair pinning
Abstract: a test asserts a representation the text never assigns:
- response envelope on other verbs;
- `omitempty` presence;
- query-key spelling;
- file encoding;
- status code for an unlisted rejection;
- eager initialization;
- rollback atomicity;
- top-level JSON shape;
- a side effect on a deleted object.

TQ runs a "refutation battery" (repo grep for a same-form precedent). If it finds none, the test is unfair.

How to hunt:
- For every exact literal or shape in an assertion, find a prompt quote or a repo precedent at a file:line.
- Otherwise state it in the text or assert only non-success plus unchanged state.
- Corrupt implementation-written files rather than hand-made bytes.

### F7. CFG: validation / rollback boundary
Abstract: candidate validation skips some sections, entries or dependent sections (client-profile, notifier), runs
on the live global and leaves overrides/defaults behind, reuses a key captured at start, or relies on library state
that Reset wipes.

How to hunt:
- Audit every global write (`viper.Set`, `SetDefault`) on the validate path.
- Validate in an isolated instance.
- Include referenced sections in fingerprints.
- Test rename, removal-of-optional-section and malformed-entry-without-marker cases.

### F8. LNT: linters and conventions
Abstract: enabled golangci rules caught as High Code Quality:
- revive `exported` (missing or misplaced doc comment);
- revive `error-strings` (capitalized);
- goconst (3x literal).

Also: a license header missing on a new file, a raw write bypassing the shared response helper (CORS), and stale
doc comments.

How to hunt:
- Run `golangci-lint` with the repo config on the diff.
- grep new `errors.New("[A-Z]`.
- Count repeated literals.
- Check comment placement after insertions.
- Diff new-file headers against siblings.

### Smaller families
- **DEC (lenient decoding)**: trailing data, top-level or nested `null`, missing required members, null treated as
  omission. Hunt: decode into raw first; require an object; `DisallowUnknownFields`; a second Decode must return EOF.
- **CMP (wrong measure)**: len vs cap, `!=` vs `<`, max vs verbatim, per-bucket vs global sort, leftmost-first
  regex, `.` without `(?s)`. Hunt: for every comparison of counts, orders or patterns, write the boundary input.
- **IDN (identity)**: shared labels across kinds, global one-shot flags across instances, magic keys colliding with
  user names. Hunt: two same-named objects of different kinds, two clusters, a user value equal to a format keyword.
- **OPS**: wrong patch pasted, hand-edited generated code, a cleanup revert without re-running its probe, similarity
  with older submissions.

---

## 3. Cross-check tensions (same item, different checks)
- **Rollback of a failed mutation**: TQ ruled it unfair (#22); AR then demanded it as T3/T4 High (#44). Fix: state
  it in the text, then test it.
- **Empty optional JSON keys**: AR T3 Medium wanted `statuses` present (#30); TQ ruled presence unfair (#23).
  Prefer TQ: assert values, not key presence.
- **Notifier regex on reload**:
  - SQ High demanded it (#109);
  - AR T3/T4 High demanded a test (#125);
  - FP overruled it as "prompt names only cluster/consumer/storage".
  - The SQ/AR side won the gate.
- **Trailing JSON**: SQ High (#10) demanded rejection; the FP adjudicator overruled a judge because the repo's own
  setLogLevel is lax. A solution must still reject it.

## 4. FP panel tendencies

### Upheld as false positive
These are usually "verdict changed by panel evidence" and always come with a probe the reference passes and the
candidate fails:
- concurrency crash or race in a path the feature adds (#61, #129, #99);
- data loss in exactly the scenario the feature exists for: restart invisibility, leader election, multi-cluster
  restart (#95, #98, #102);
- explicit ordering words violated: "oldest commit first" (#96);
- "match the whole name" violated by a regex implementation detail (#60);
- import that bypasses normal ingest rules (#101), and cache invalidation scoped too narrowly (#103);
- name collision losing state (#100, upheld once at high confidence, overruled once);
- a rejected config observable or applied mid-check (#131).

### Overruled as underspecified or not prompt-grounded
These usually show as "Genuine pass, judge dissent":
- case-insensitive status input; rejecting inert statuses (STOP/STALL/REWIND);
- stricter-than-prompt JSON validation (trailing data when a repo handler is equally lax, null to zero, `{}`
  rejection, nested null broker topic);
- HTTP code for corner ops: DELETE of expired = 200, persistence failure = 404;
- NOTFOUND wildcard display; existence check via config vs storage; zero-config cluster;
- resource leaks (sarama client not closed); reflecting unreloaded sections in /v3/config;
- client-profile restart (overruled 4 times, upheld once);
- notifier regex validation (overruled);
- transient visibility windows that self-heal;
- max-duration re-checked on comment-only PUT.

### Reading the panel
- Judge #2 dissents on most passes. Only the adjudicator verdict counts.
- "Nova N" in the report is NOT the zip's Nova_Nova_N; match runs by the code the panel quotes.
- An adjudicator note of "worth fixing" on a genuine pass is a free hint for the next hidden test. Add it only if a
  mutant proves a wrong solution passes AND a prompt sentence covers it.

## 5. Pre-paste hunting checklist (one line per family)
1. COV: for each promise, name the lazy wrong impl and the assertion that kills it; check failure paths assert state.
2. CON: list async readers of every removed or invalidated thing; probe a pause/resume interleave; run -race.
3. HAR: run the unsolved suite 3x for identical results; base exclusions vs touched functions; no sleeps on deadlines.
4. CLN: for every remove, replace, shrink or expire, check storage, cache, metrics, notifier and detail endpoints.
5. DSC: narrative prose, no restated defaults, one reading per noun, no sentence contradicting a test.
6. PIN: every asserted literal has a prompt quote or a repo file:line precedent.
7. CFG: validate in isolation; include dependent sections; test rename, removal and marker-less entries.
8. LNT: golangci-lint with the repo config on the diff; lower-case errors; doc comments; license headers.
9. DEC: trailing data, null, nested null, missing members, unknown fields, both-of-exclusive-fields.
10. CMP / IDN: boundary inputs for every comparison; same-name objects across kinds and instances.

## Platform FP panel, Burrow #751 rollout 61 (2026-10-04) — calibration data
- Judges re-run the HIDDEN tests with -count>1 and -race. A candidate whose shipped test flakes (~50%, reference 0%) is
  upheld as FP (zip10: TestReload_ChangedClusterKeepsWhatItStored).
- Judge-c probe styles seen: referenced client-profile change restarts dependents; untouched-section values (HTTP
  defaults) survive reload; in-flight evaluation repopulating a just-forgotten cache entry (TOCTOU); SIGTERM dropped behind
  a pending SIGHUP on a 1-slot channel; stale /v3/config after reload; data races in module-map swap.
- Upheld (zip10): hidden-test flake + races + several prompt-grounded discriminators together.
- Overruled (zip4, twice): client-profile restart (section-granular rule), HTTP defaults (out of scope), TOCTOU cache race
  (no concurrency contract in prompt). Adjudicator: "the reference being more robust does not make them required".
- Our auditor found two zip4 issues the platform never probed in 2 FP runs: crash under 9 readers x 200 reloads
  (concurrent map read/write) and SIGTERM lost after HUP,HUP,TERM. Treat such findings as RISK with an estimated
  upheld-probability, not as a definite FP; a test that kills the only genuine passer gives 0/10.

---

## Part 2: how to think

Part 2 drew on these sources (all read-only):
- **Platform reports in the 15 main transcripts.** Every Auto Review "Failing case / Wrong impl caught / Promise cited /
  Load-bearing check" block, every SQ "Evidence" line, the TQ refutation batteries and every FP adjudication.
- **Local reviewer reports** among the 707 subagent transcripts: about 80 are review-type agents, and the final
  reports of the ones run just before each paste were read. They cover Agent A/B, cold readers, SQ/TQ judges, FP
  hunters and auditors. Also the prompt of the 391-agent snapshot gap-hunt workflow.
- **51 eval-result.json files** under shipd/runs and burrow-config-reload/eval/rollout58-61.
- **The 62 Downloads/agent-runs zips**, read in place with no extraction, so every task's rollouts count. That gives
  302 unique runs after deduping by run ID.
- **STATUS.md and review-triage-wip11.md.**
- **paste-cache** (2 files): unrelated Java test code, no platform output.

### A. Platform reasoning method

**A.1 Evidence the platform cites** (Auto Review and SQ findings; most findings cite more than one kind):
| Evidence kind | What it proves | Approx. count |
|---|---|---|
| Promise quote | the behavior is required (every finding starts here) | all |
| `test_name:` line | the exact assertion or fixture that is too weak, or that masks production wiring | ~30 |
| `repo_line:` line | the production sink where the wrong behavior becomes observable (Notify, metric `Set`, `[len-1]`, map deref, `SetDefault`) | ~25 (12 are metric `Set` lines) |
| `artifact_line:` | a line from a rollout artifact: an all-green agent's patch, junit_base.xml, evaluation_result.json | ~6 |
| `.golangci.yml` + Makefile lines | an enabled lint rule the new code breaks | 5 |
| Reference behavior | "the reference would pass the demanded check" (proves the gap is fair to close) | most T3/T4 |

**A.2 The chain they write, every time**
- **Test findings**:
  1. Quote the promise.
  2. Name the cheapest realistic wrong implementation.
  3. Point at the line that cannot see it: the test ends after `assert.Error`, the fixture assigns the field, or the
     accepted set includes the wrong value.
  4. Show the reference passes the demanded check.
  5. Give a deterministic failing case.
- **Solution findings**:
  1. Quote the promise.
  2. Pick a production sink line.
  3. Construct the input or interleaving that reaches it with stale or absent state.
  4. State the observable harm.
  5. Sketch the fix.
- **TQ unfair tests**:
  1. Quote the pinned literal.
  2. Run a repo grep "refutation battery" for a same-form precedent.
  3. If there is none, name an equally valid alternative. The test is then unfair.

**A.3 Hunting moves** (each lists the catalog rows it reproduces)
| # | Move | Steps | Rows |
|---|---|---|---|
| H1 | Orphan-hunk scan | 1) List every hunk in solution.patch, including one-line additions to existing cleanup or registration hooks. 2) For each, find the hidden test that fails if the hunk is deleted. 3) No test + a promise = T3/T4 gap. No test + no promise = scope creep. | 40, 48, 125, 141-143 |
| H2 | All-green diff | 1) For every PASS run in the rollout zip, diff its patch against the reference, promise by promise. 2) Probe each reference behavior the passer lacks. 3) A fair failing probe means both an FP-panel risk and a T3/T4 gap ("this exact pattern passed all 51 hidden tests"). | 49, 125 |
| H3 | Fixture-masking check | 1) grep test helpers for assignments to the new production field or for direct construction (App.Silences =, direct reconciler or webhook structs). 2) Find a test that drives the real entry point (Start, main, SetupWithManager, webhook.Setup) with the field unset. 3) None means the wiring promise is untested. | 34, 41, 133, 141, 142 |
| H4 | Accepted-set read | For each assertion, list every output it accepts. Examples: `Contains([]int{400,404})`; `Empty(m["k"])`, which also passes on a missing key; a metric helper summing only matching labels, where deleted = reset to 0; `>=` request counts a partial restart also meets. Name a wrong output inside the set. | 28, 30, 140 |
| H5 | Failure-path post-state | 1) After every asserted error or rejection, check that the state is asserted too: List empty, file and config unchanged, log line emitted. 2) In multi-step persistence tests, reload after each mutation, before a later mutation flushes everything. | 35, 44, 46, 123 |
| H6 | Decorrelate fixtures | When a promise names a key or unit (Order vs Timestamp, containers vs pods, muted-by vs merely covering, OK-only), check whether the fixtures move the alternative in lockstep. If so, invert it. | 37, 40, 78, 144 |
| H7 | Directional boundaries | For "fewer", "older", "longer than", test `<`, `=` and `>`, and write the `!=` or `<=` mutant. Count with the real measure (cap, not the len of a filtered slice). | 77, 95 |
| H8 | Feature x lifecycle cross-product | 1) Rows = features and modes (status filter, send-once, send-close, BOOST_ON_RESTART, regular vs namespace receiver). 2) Columns = events (open, escalate, mute later, recover, remove, re-add, hand off). 3) Mark the covered cells and probe the empty ones first. | 32, 36, 47, 53, 138, 145 |
| H9 | Sink-backward trace | 1) List the sinks new state reaches: send/Notify, metric `Set`, `[len-1]`, map lookup + deref. 2) For each, build the state that reaches it stale or absent: nil map entry, empty slice, old start time. | 36, 73, 115, 121 |
| H10 | Async interleaving script | 1) List concurrent producers: go-per-request evaluations, the /metrics scrape loop, hashed storage workers, the notifier refresh tick, unlocked readers of global config. 2) For each delete, invalidate or replace, write "producer reads old -> operation returns -> producer writes". 3) Every writer line is its own finding. 4) Fix with a token taken BEFORE enumeration or with a draining barrier, and prove it with a forced-pause probe. | 65, 70, 72, 74, 99, 114, 117-119, 129, 131 |
| H11 | Lock audit | For each new field or map, list the writers, readers and locks held. Flag: writes under RLock, maps shared by per-module goroutines, slices leaked by shallow copy, global swaps while unlocked readers run. | 14, 16, 61, 106, 118 |
| H12 | Lint-rule diff | 1) Read .golangci.yml (linters, revive rules, goconst thresholds) and the Makefile lint target, then run it on the diff. 2) grep added lines for `errors.New("[A-Z]`, undocumented exported declarations, comments displaced by insertion, literals repeated at or above the threshold, and new files without the license header. | 8, 13, 17, 64, 116, 135 |
| H13 | Global-state rollback audit | 1) List every process-global write on the validate and reject path: `viper.Set`, `SetDefault`, `Reset` clearing the config type, metric registration. 2) Run reject -> correct -> reload and check each layer. 3) Rename or remove optional sections. 4) Check whether the baseline is captured state or a re-read from disk. | 108, 110, 112, 113, 120 |
| H14 | Dependency closure | For every change-detection or identity computation, list everything the module reads: referenced client-profile/tls/sasl sections, kind, cluster. Probe by editing only the referenced section, or by creating same-name objects of two kinds. | 98, 105, 130, 137 |
| H15 | Sentinel trace | List the sentinels the feature introduces or restores (lastCommit 0, zero Until, empty group = all, nil vs [] history). Trace each through the existing consumers: lazy-expiry purge, matchers, completeness checks. | 11, 66, 68 |
| H16 | Removal matrix | For each removal kind (removed, shrunk, replaced with fewer entries, lazily expired, filtered out, removed then re-added), check storage, the evaluator cache, metric series, notifier incident state and detail endpoints, and whether the re-added entity really starts fresh. | 63, 66, 75, 103, 111, 121 |
| H17 | Decoder probe set (solution) | Send these to every decode path: null, top-level array, trailing data, nested null, a missing required member, `{"x":null}`, numbers as strings, unknown fields. The reference must reject what the text calls invalid. Tests may pin only the format-agnostic cases. | 10, 15, 18, 69, 71, 73 |
| H18 | Base-run forensics | 1) Exclusions in test.sh base vs the functions solution.patch touches. 2) junit_base and environment_assessment of every rollout run. 3) The unsolved run must report one failed case per new test, never a `[build failed]` pseudo-test. 4) `go list` and build exit codes must propagate. | 4, 76, 80, 94, 124 |
| H19 | Sibling symmetry | When a check or convention is applied in one handler (clusterExists on create, writeResponse + CORS, the error envelope), check that every sibling route of the feature applies it too. | 7, 67 |
| H20 | Refutation battery (TQ) | 1) Every literal, shape or status a test pins needs a prompt quote or a repo precedent at file:line. 2) Otherwise assert only non-success + unchanged state, or state it in the text. 3) Re-run after every description edit. | 19-26, 81, 82 |

Frequency: H10 and H1-H5 produced most High findings. H12 and H13 produced most of the "easy" SQ FAILs.

### B. Our blind spots (last local review before a paste vs what the platform found after it)

**rdb-diff**
- **Last review**: final review plus byte-rule mutant review (2026-09-26 23:17-23:34Z). They checked exit codes and
  pass counts.
- **Platform found after (VS FAIL x2)**:
  - The unsolved run reported one `[build failed]` pseudo-test, so the new tests were in neither p2p nor f2p.
  - 2 F2P failures from mojibake in non-ASCII literals.
- **Why missed**: nobody compared the JUnit test-ID sets the checker uses. The copy path was outside every lens.
- **Check**: H18, plus an ASCII-only patch, `LC_ALL=en_US.UTF-8 pbcopy` and a hash after pasting.

**silences, round 1**
- **Last review**: Agent A, Agent B, cold reader (tests only; 2026-09-28 ~00:30Z).
- **Platform found after**:
  - SQ: list filter 200 not 404, revive exported, swallowed save errors.
  - AR: startup wiring untested, malformed-file error untested, S1 orphan close.
- **Why missed**:
  - No SQ lens and no linter.
  - Agent A marked startup wiring UNCOVERED and Agent B called the error path "fine". The gap was seen but downgraded.
  - Nobody walked the status filter x quiet-recovery state machine.
- **Check**: H12, H19, H3, H5, H8. Severity = "can a realistic wrong impl pass", not our guess.

**silences, round 2**
- **Last review**: no concurrency lens; test.sh had no -race.
- **Platform found after**: SQ: the incident map was written under RLock (`concurrent map writes`), which the FP panel
  also upheld on a passer.
- **Why missed**: nobody listed per-response goroutines.
- **Check**: H11, -race in the harness.

**silences, round 3**
- **Last review**: adversarial test auditors (09-30 13:14Z), run on the earlier text.
- **Platform found after**: TQ FAIL x2, 6 unfair assertions (empty keys present, `?group=`, json.Valid, `{not json`).
- **Why missed**: the user's humanized rewrite after the review dropped "with those keys", "json" and "group".
- **Check**: H20 re-run on every description diff.

**silences, round 4**
- **Last review**: rollout zips 49/50 were available.
- **Platform found after**: SQ: explicit null treated as omitted. AR: expired silences still listed; 2 real passers
  returned GetAll.
- **Why missed**: the passers were never diffed against the reference. The null-vs-absent probe was never run.
- **Check**: H2, H17.

**snapshot, round 1**
- **Last review**: Agent A, Agent B, 2 cold readers (tests only).
- **Platform found after**, 6 SQ FAILs in 13 h:
  - partition-shrink and incomplete-history series;
  - in-flight evaluation re-caches;
  - owner-only purge, which our own fix exposed;
  - `{"version":1}` accepted;
  - a commit landing after PUT across workers.
- **Why missed**:
  - No SQ lens.
  - Cleanup was checked only for whole-entity removal.
  - The fix was not traced through existing consumers of the restored sentinel.
  - I declined an earlier "tests use one storage worker" finding ("my miss, not missing context").
- **Check**: H16, H10, H15. Never decline a concurrency finding about the reference just because no fair test exists.

**snapshot, round 2**
- **Last review**: FP hunters on two passers (09-29 21:30 and 23:06Z).
- **Platform found after** (AR):
  - T1: base excluded tests of the touched function (3 versions).
  - S1 x6: scrape race.
  - S1: inconsistent document panics.
  - T3/T4: partition growth; Order and Timestamp correlated.
  - T2: unbounded wait.
  - T8: `go list` status discarded.
- **Why missed**:
  - We excluded the upstream tests to keep a hanging design green.
  - /metrics was not on the producer list.
  - Nobody checked cross-member invariants.
- **Check**: H18, H10, H9, H6, H7.

**snapshot, round 3**
- **Last review**: the gap-hunt workflow (391 agents) with an "accepted by design" list that included "races with
  in-flight work" and "JSON leniency".
- **Platform found after**:
  - TQ FAIL, 2 unfair, after the tests were rolled back to v23 (undoing the v28 guard).
  - SQ: `{"clusters":{"alpha":null}}` erases a cluster.
  - SQ: startup reconciliation races a fresh commit.
- **Why missed**:
  - A rollback reintroduced a fixed issue.
  - FP leniency ("acceptable for a candidate") was applied to our reference.
  - Exclusions meant for the test hunt leaked into the solution review.
- **Check**: replay fixed findings after any rollback; run H17 on the reference; keep the SQ lens separate, with no
  "accepted by design" list.

**kscb, round 1**
- **Last review**: Agent A, Agent B, 2 cold readers (tests only).
- **Platform found after**: SQ: a pod double-tracked after a regular boost registers.
- **Why missed**: no SQ lens. Ownership vs priority was not traced on later events.
- **Check**: H8, H9.

**kscb, round 2**
- **Last review**: local SQ judge scored 3/3 at 02:15Z.
- **Platform found after**: SQ FAIL 02:46Z: a BOOST_ON_RESTART handoff leaves total at 0.
- **Why missed**: nobody enumerated the README modes as an axis.
- **Check**: H8, with a mode axis.

**kscb, round 3**
- **Last review**: n/a.
- **Platform found after**: SQ blocker, wrong solution.patch pasted (Burrow files).
- **Why missed**: process slip.
- **Check**: verify the repo path and hash before pasting.

**kscb, round 4**
- **Last review**: Agent A's matrix of 20 promises, built only from description sentences.
- **Platform found after** (AR T4):
  - SetupWithManager and webhook.Setup registration untested;
  - manifests/Helm untested;
  - metric deletion not discriminating;
  - single-container fixtures.
- **Why missed**: obligations that come from repo conventions had no rows.
- **Check**: H1, H3, H4, H6.

**reload, round 1**
- **Last review**: no local SQ review before the first SQ run (blind solvers only).
- **Platform found after**, 4 SQ FAILs:
  - class-name skip, client-profile and notifier viper race;
  - `viper.Set` override survives a rejected file ("audit missed viper.Set");
  - notifier regex not validated;
  - storage rename ("I had judged renames out of scope").
- **Why missed**: no SQ lens. Nobody enumerated the validation boundary across all sections. We narrowed the scope
  ourselves.
- **Check**: H13, H14, H19.

**reload, VF**
- **Last review**: the proof matrix compared counts, not IDs.
- **Platform found after**: VF FAIL, 5 flaky subtests in the unsolved state.
- **Why missed**: map-ordered subtests plus `Fatalf` on the parent `t`.
- **Check**: H18; run the unsolved state 3x and require identical IDs.

**reload, round 2**
- **Last review**: full review at 16:40Z (3 SQ, cold reader, FP auditor; triage S1-S13, T1-T11).
- **Platform found after**:
  - S1 x6: scrape race;
  - S2: SetDefault after unlock;
  - viper config type lost after Reset (our S6 fix caused it);
  - TQ 1/3: cached state and error log not asserted;
  - in-flight evaluation re-caches;
  - notifier nil deref.
- **Why missed**:
  - The scrape race and the in-flight cache were snapshot site findings 4 days earlier, but reviewers never got past
    findings.
  - A fix added a library-state dependency.
  - The TQ partial was deferred.
  - The notifier was not in the removal matrix.
- **Check**: feed this catalog to every reviewer (H10, H16); re-probe alternate config forms after each fix; treat TQ
  partials as AR T3/T4.

**reload, round 3**
- **Last review**: SQ and TQ reviewers (00:26-00:39Z). The final SQ reviewer predicted PASS. No report ran golangci-lint.
- **Platform found after**:
  - AR T2: flaky zookeeper base test. A rollout-60 judge had already reported the 10-minute timeout.
  - S1: baseline re-read in main.go. We had found it and dropped it as a "library-only residual".
  - SQ: error-strings in code our S2 fix added.
  - T3/T4: notifier regex untested. We had deleted that case for FP safety (triage T5).
  - S1: a re-added cluster keeps its notifier incident.
- **Why missed**:
  - Nobody scanned the run judges' `environment_assessment`.
  - We dropped a High ourselves.
  - The linter was never run.
  - We deleted a test for a behavior SQ requires.
  - Notifier state was not checked on remove and re-add.
- **Check**: H18, H12, H16. Keep a test for every behavior SQ demands, and fix the description instead of deleting.

**B.2 Why we missed things (tally across 5 tasks)**
| Cause | Times | Findings it let through |
|---|---|---|
| No local SQ lens before the first SQ run | 4 of 4 multi-module tasks | ~14 first-round SQ FAILs |
| Linter never run (0 local reviewer reports mention golangci-lint) | every task | 6 lint findings |
| A known site pattern from an earlier task was not reapplied (scrape race, in-flight cache, revive rules) | 3 families | ~10 |
| Finding seen locally but downgraded, declined, deferred or dropped as residual | 5 | wiring, error path, worker barrier, cached state, main.go TOCTOU |
| Our own fix introduced the next finding | 4 | owner-only purge, viper type, error-strings, SASL fingerprint after a "cleanup" revert |
| Description edited after the last review | 2 rewrites | 6 TQ-unfair assertions |
| A test was deleted or rolled back | 2 | notifier regex gap; "x"-numbers guard lost |
| Exclusions meant for the test hunt applied to solution review | 1 workflow | nested null, startup race |
| Platform-side artifacts not scanned (JUnit IDs, run-judge env flags, passer patches) | 3 | build-failed pseudo-test, zookeeper T2, expired-list gap |
| Promise matrix built only from description sentences (no mode or wiring axes) | 2 | BOOST_ON_RESTART, registration and manifests |
| Copy/paste process | 2 | mojibake, wrong patch |

### C. Agent failure anatomy (302 unique runs, 79 pass, 223 fail)
| Task | Runs | Pass | Top failure kinds (failing runs whose judge reason names it; keyword count, about +-3) |
|---|---|---|---|
| ftpserver discord backend (pre-rdb) | 66 | 8 | Malformed 429 body read as `retry_after=0` instead of the RetryDelay fallback ("unreadable" vs "unparseable" conflated): 54. Extra `Sleep(0)` pacing call: 14. Default http.Client follows 307/302 redirects: 9. Root-path normalization hangs MkdirAll: 3. `+123` accepted by ParseInt: 2. |
| rdb AOF->RDB + rdb-diff | 8 | 2 | Encoding edge (listpack int13 count, HFE relative values, set listpack rule): 5. Boundary validation (int64 overflow clamp, stream ID order, empty AOF): 3. |
| silences | 91 | 25 | Whole-name regex via the leftmost first match: 24. Omitted `group` rejected (empty = all): 15. Silence not applied to OK: 15. Concurrent-burst race or notifications: 13. Expired still listed: 10. send-once reset skipped on quiet recovery: 9. HTTP/metrics silence copied from the evaluator field: 7. Numeric statuses accepted: 4. Removing the muting silence keeps the close quiet: 3. |
| snapshot | 85 | 24 | Merge replays empty owners as owner events, leaving invalid groups: ~33. Explicit `mode=replace` accepted: ~28. Expiry from the max offset timestamp instead of the stored last commit: ~15. Empty history rebuilt as a nil-filled ring: 11. Ring cursor or trim wrong after an intervals change: ~10. Admin success response not in the repo envelope: 7. Leaderless partition counted wrongly: 3. Merge not globally oldest-first: 3. |
| kscb | 5 | 3 | Old winner not refreshed on delete: 1. Handoff reactivates a reverted restart pod: 1. |
| reload | 40 | 11 | One resize helper for broker (points at newest) and consumer (points at next) rings: 15. Candidate visible to config readers before validation: ~11. Re-reading global viper keeps old defaults, so removed modules stay: ~9. Changed cluster loses stored or cached state: 6. Invalid file accepted: 3. Unchanged modules restarted: 2. Reload wired only into a new entry point: 1. |

**Cross-task failure families (what actually discriminates)**:
Counts are failing runs; a run can fall into several families.
1. **Presence vs value and error-class conflation**: unparseable vs unreadable 429 (54), omitted vs empty group (15),
   zero meaning "none" (Sleep(0) 14, zero Until 1). About 85 runs.
2. **Library defaults left untouched**: regexp leftmost-first (24), http.Client redirects (9), ParseInt `+` (2),
   viper ReadConfig keeping defaults (~9). About 45.
3. **Re-implementing an existing pipeline instead of feeding it**: merge owner events (~33), expiry signal (~15),
   ring cursor/trim after restore (~10). About 60.
4. **One helper reused across structures with different invariants**: broker vs consumer ring pointer (15),
   nil-filled rings (11). About 26.
5. **Enumerated or explicit-only rules**: `mode=replace` (~28), numeric statuses (4), invalid-file list (3).
   About 35.
6. **Lifecycle and visibility windows**: OK suppression (15), candidate exposed mid-validation (~11), expired still
   visible (10), quiet-recovery reset (9), muting silence removed (3). About 48.
7. **Wiring through the wrong source**: evaluator field instead of the store (7); reload only in a new API (1).
   About 8.

**Judge flags on failing runs**:
- The failed requirement was "mentioned in the description" in about 94% of cases (209 of ~222).
- It was "inferable from the codebase" in 56 of 72 silences, 52 of 61 snapshot and 27 of 29 reload runs, but only
  10 of 56 discord runs.
- It was rarely inferable from existing tests (0 to 20 per task).

So the discriminators are stated-but-subtle rules, which is fair difficulty.

**Panel labels** (Auto Review "What the runs showed"):
- **subtle but fair**: leftmost regex (8 runs over 3 reviews), remembering only the muting silence's end time (4),
  send-once reset (6), OK under a concurrent burst (2), expiry from the max timestamp (6), nil-filled histories (3),
  leader count (3), `mode=replace` (2), shared ring resize (5), validating after exposing the config (2), reverted-pod
  handoff (1), old-winner refresh (1), empty-comment PUT (1), persisted statuses not loadable (1).
- **genuinely hard**: restarting a changed cluster while keeping its stored and evaluator state (2); an incompatible
  Add signature plus rejected omitted groups (1).
- **shared blind spot**: omitted group rejected (7), silence state taken from the evaluator field (3), every
  serialized partition replayed as an owner event (5), rereading or diffing viper treated as reconciliation (3).

**Run judges' environment flags** (6 runs) each foreshadowed a site finding or a fix:
- the harness prefix guard scanning solver tests;
- a stale baseline Kafka test (later the snapshot T1 finding);
- a verifier coupled to the internal ConsumerGroupStatus shape;
- expiry visibility ambiguous (x2, later TQ/AR);
- a flaky zookeeper baseline (later the reload T2 finding).

Scan `environment_assessment` before every paste.

**Test-design implications**:
- Keep tests on families 1-6. That is where 10-30% of strong agents fail fairly.
- Basic CRUD, registration and happy paths never separate agents.
- A "shared blind spot" label is a warning: if 7 of 10 runs fail one rule, re-read the sentence for a second reading
  before keeping it.

### D. FP adjudication table (31 adjudications: silences 9, snapshot 12, reload 10; 15 upheld, 16 genuine)
Counts are probe claims: one adjudication can carry several. Each upheld adjudication is counted once, under its main
reason; the client-profile row also counts 2 secondary reasons inside multi-reason upholds.
| Probe type | Upheld | Overruled | Upheld example | Overruled example |
|---|---|---|---|---|
| Core-scenario data loss or wrong state (restart, import, handoff) | 6 | 1 | len of leader-reachable partitions deletes a restored topic during a leader election | changed-cluster drop that self-heals (the hidden test is flaky for the reference too) |
| Concurrency with a functional consequence (crash, hidden test flakes, rejected config applied) | 4 | 0 | viper.Reset race makes RejectedFile fail ~25% (reference 8/8) | n/a |
| Concurrency seen only by -race, or a TOCTOU interleaving without contract words | 0 | 3 | n/a | "no concurrency contract in the prompt" (in-flight cache, reload) |
| Explicit semantic words ("whole name", "oldest first", "rather than any evaluation cached before it") | 3 | 0 | leftmost-first alternation; per-partition merge sort; in-flight cache after PUT (snapshot) | n/a |
| Name or identity collision | 1 | 1 | cluster named `clusters` unwrapped and lost on restart | same collision judged "not prompt-required" in another batch |
| Dependent or referenced config (client-profile) | 3 | 5 | "credential rotation is the motivating scenario" | "prompt reconciliation is section-granular" |
| Stricter input validation than stated (trailing JSON, null to 0, `{}`, lowercase or inert statuses) | 0 | 7 | n/a | "repo handler setLogLevel is equally lax"; "stricter contract than the prompt" |
| Status code or display for corner states (DELETE expired, persistence-failure code, NOTFOUND wildcard, zero-config cluster) | 0 | 6 | n/a | "underspecified edge, defensible reading" |
| Out-of-scope surfaces (HTTP defaults, unreloaded sections in /v3/config, notifier regex, storage rename, max-duration recheck) | 0 | 5 | n/a | "HTTP server is outside the prompt's scope" |
| Resource hygiene (sarama client not closed) | 0 | 1 | n/a | "quality gap, not prompt-required" |
| Lost exit signal (SIGTERM behind a pending SIGHUP) | 1 (in a multi-reason uphold) | 0 | rollout 61 zip10 | n/a |

**Calibration rules**:
- An uphold needs all of:
  - the adjudicator re-ran the probe and it discriminates (candidate FAIL, reference PASS);
  - a quoted sentence or the feature's core scenario covers it;
  - an observable consequence.
- "Verdict changed by panel evidence" means a judge's probe flipped the adjudicator.
- The same probe type can split across batches (client-profile 3:5, `clusters` key 1:1). Estimate P(upheld) and do not
  treat a probe as a certain FP.
- Concurrency is upheld only when the race breaks a stated behavior or makes a hidden test flaky.

## Faust task 7 (live readers), 2026-10-18/19: every platform finding -> the sweep that now catches it
| Check | Finding (what the platform saw) | Sweep that catches it (agent files) |
|---|---|---|
| Auto Review T5 | hidden fake Kafka clients lacked public assignment/pause/resume (one run failed 36 of 40 on AttributeError) | fake completeness vs the installed library (TQ, AR) |
| Auto Review T4 | the second public transport (confluent) untested; pattern readers x backpressure untested | backend coverage; feature x invariant matrix (TQ, AR) |
| Auto Review S1 | tracking state set only on a transition (a topic acks=False from the start) | initial-state sweep (SQ, AR) |
| FP panel | inline regex flags crashed the combined subscription regex; cancel acked unfinished work (`except BaseException: ack`) | FP probe patterns: inline flags, group names, cancel on named exception paths (FP, TQ, AR) |
| Codex FP | pattern stream started during a rebalance never subscribed; confluent paused records lost | removed-tests check plus variant probes (FP) |
| Codex AR | stop while a processor is busy stalls the others; fakes lack getmany | busy lifecycle (SQ, AR); fake completeness |
| SQ (wip30) | confluent fetch gate skipped when nothing is fetched; rebalance race during the resubscribe delay | named-scope completeness; debounce and race windows (SQ, AR) |
| TQ (wip35) | 6 tests asserted `topics.crashed`, an internal field: "not fair" | internal-field assertion sweep (TQ, AR) |
| TQ partials | subscription-only checks for named variants | outcome per named variant (TQ, AR) |
| SQ (wip35) | judge read `Channel.put` (broadcast) where `Topic.put` overrides it: false High | static-misread sweep: call the concrete target explicitly (SQ, AR) |

| Codex final AR (wip36) | flow fixture `await fun()` rejected a sync `call_thread`; a cancelled supervised actor acked unfinished work through its restart reservation | fake dispatch semantics; supervised cancel in busy lifecycle (TQ, SQ, AR) |
| Platform AR + Vega FAIL_TEST_BROKEN (wip39) | the double modelled SubscriptionState with its own `_kind`, so a driver reading `_subscription_type` crashed; the cancel test asserted no commit, not `message.acked` | fake state fields (subclass the real class); assert the promised state, not a proxy (TQ, AR) |
| Codex + claude2 T1-T8 (wip44) | a real-class subclass with an empty native assignment (paused_partitions raised); a false test.sh coverage claim; immediate batch hand-out pinned | populate native state; grep-verify deselection comments; now-or-later delivery (TQ, AR) |
| Prechecks 'No URLs' (wip42+ desc) | `kafka://` in the description's scoping line counted as a URL | never write URI schemes in descriptions; name the transport (desc) |
Process lessons:
- Finish every review and test change BEFORE the one description edit.
- Hints only for corners no run solves.
- Scope a backend out explicitly rather than half-support it.
