# Lane C: difficulty retro for docker proxy, turso, elio, swift

Read-only. Sources: `olympus problems download` (description, test.patch, solution.patch, metadata), `olympus runs view`, and for every non-stale completed run the `testLog` and `evalResult` artifacts (52 runs). I also read one failing trajectory per task (docker rd7cse2h05, turso rd7dxvkf80, elio rd70dnrf2v, swift rd74yhxrvs) and the passer's `solutionPatch` for each task. Repos were shallow-cloned at the pinned commits for the primitive grep. "Final runs" means the latest re-eval round, which is what the platform scores. Guesses are marked as guesses.

Platform outcome (from `runs view` criteria): all four are rated `hard`.
- docker: 1/16 (Orion 1/8, Vega 0/4, Nova 0/4). 93 new tests.
- turso: 1/12 (Vega 1/4). 61 new tests.
- elio: 1/12 (Orion 1/4). 41 new tests.
- swift: 1/12 (Orion 1/4). 10 new tests, each covering many scenarios.

How each final number came about:
- docker: the suite was the same 93 tests from the first rollout. The re-evals only fixed a URI-encoding mock in the test helper, which had failed 9 baseline tests in some runs.
- turso: the first rollout had 60 tests and Vega solved 2/4. The re-eval added 1 test (`matview-not-in-negated-in-spelling`), which brought it to 1/4.
- elio: the first rollout had 40 tests; Orion solved 4/4 and Vega 2/4 (both Vega passes were overridden as regressions). The re-eval added 1 test (`file_renamed_in_duplicate_finder_is_selected_under_its_new_name`), which brought Orion to 1/4.
- swift: four rollouts.
  - 6 tests: Vega 4/4, Orion 3/4.
  - Re-eval with the cleanup-failure and version-id checks: Orion 1/4. Platform TQ rejected the version-id check as unstated.
  - New description on 6 tests: Orion 4/4.
  - 8 tests, then 10: Orion 1/4.

So three of the four tasks became hard only through tests added after the first rollout. Docker was hard on its first suite.

---

## 1. Docker proxy (google/oss-rebuild @ 3b628aeb)

### Q1. Hard points (final round, 15 failing runs)
Failing-test counts across the final runs, from the testLog `--- FAIL` lines:

| test | fails | family split | in description? |
|---|---|---|---|
| TestDirectoryListedOnlyForAFileTheContainerRemovedIsLeftOut | 8 | Orion 6, Vega 1, Nova 1 | **Implied**: neighbour of the named rule "hide the directory ... unless the container changed its mode". The directory was listed before the start only because of a child that was later removed. |
| TestLinkedDirectoryReplacedBeforeAnyReadKeepsTheTruststoreHidden | 8 | Vega 4, Nova 4 | **Implied**: symlink sentence is named; the symlink being replaced between write and read is lifecycle |
| TestRemovedDirectoryStaysReported | 8 | Vega 4, Nova 3, Orion 1 | **Implied**: the sticky rule ("once ... we detect that on a read") is named; a deletion seen as a 404 on a directory archive is a neighbour of the exception |
| TestCustomFilesWrittenThroughTwoPathsAreBothWrittenAndHidden | 6 | Orion 2, Vega 2, Nova 2 | **Repo-only**: two `customFiles` keys that resolve to one file. Base appends each entry (docker.go:684-718), so deduplicating them is a regression (verdict FAIL_REGRESSION on Orion #2). |
| TestContainerFileWhereALinkedDirectoryWasIsReported | 6 | Nova 4, Vega 2 | Implied (alias lifecycle) |
| TestTruststoreWrittenThroughTwoPaths{ReturnsContent..., StaysHidden...} | 5 + 5 | Vega 3, Nova 2 | Implied (multiplicity: one physical file reached by two paths) |
| TestProxyCertificateWhereALinkedDirectoryWasStaysHidden | 4 | Vega 2, Nova 2 | Implied |
| TestDeletionFoundByADirectoryArchiveStaysReported | 4 | Vega 3, Nova 1 | Implied (a tracked file missing from a directory tar) |
| TestChangesBeforeALaterFirstWriteAreReported | 3 | Orion 3 | **Named** ("even if it did so before we first wrote under it"). The trap is that the first start can stop early (ErrorOnExisting), so the first write happens on a later start. |
| TestDirectoryModesAreComparedWithTheImage | 1 | Nova | Implied (an unchanged image directory with mode 0700) |

Why they failed, from evalResult reasoning:
- Orion: identity and aliases were right. Orion missed directory provenance: it treated every directory in the pre-start `/changes` snapshot as permanently changed (rd763td7tj, filesystem.go:144). It also took that snapshot only once, at the first start (rd7cse2h05, files.go:66).
- Vega and Nova keyed writes by the requested path, or resolved the real path lazily at read time (rd75n8eb80 conceal.go:168; rd71f6xa32 tracking.go:154/214). They also returned non-200 archive responses without marking the tracked descendants as changed (rd7627d0bj archive.go:24).

### Q2. Obvious design vs correct design
- **Obvious design:** extend the existing `patch{Before,After}` / `patchSet` per container (docker.go:353-404) into a write ledger. Look files up by the path the proxy wrote to, and filter the three read endpoints. For directories, use the `/changes` list taken at the first start as the record of "changed before us".
- The docker trajectory rd7cse2h05 shows this plan at step 15: "per-file snapshots, canonical path resolution, and directory provenance".
- **Where it diverges from the reference (pristine.go, 1294 new lines):**
  - (a) The reference records each write under its real location, resolved at write time through parent symlinks (`realPath`, `resolveDir`).
  - (b) A 404, or an entry missing from a directory archive, marks every tracked descendant as changed for good (`noteRemoved`).
  - (c) A directory's own change is decided by comparing its mode with the image (`changedItself`, `withImage`, `imageDirModes`), not by the fact that it was listed before the start (`settlePreStart`).
  - The passer (Orion #1, rd78aq17d6) did the same three things: `ResolvePath` added to dockerfs, `loadDirectoryModes` plus `inspectContainer`, and `observeWrites`.

### Q3. Choke points
- **Write side:**
  - Entry points: start, restart and unpause, all through `patchTruststoreBefore` (`getActionType`, docker.go:327-345).
  - Each write goes through `dockerfs.Filesystem.WriteFile` (dockerfs.go:222). Callers: `createFile` (docker.go:129; cert, JKS, new bazelrc, new custom file), direct `dfs.WriteFile` (bazelrc append and custom overwrite/append, docker.go:675/702/705) and `truststorePatch.Apply` (docker.go:735).
  - So writes share one site, but only the callers know the "before" state.
- **Read side:** three endpoints with **no** interception at base: `GET /changes`, `GET /archive`, `HEAD /archive` (stat header). docker.go:15-19 lists `/changes` and `/archive` as "TODO: Unimplemented". Each needs its own filter: a JSON list, a tar-stream rewrite (hardlinks, PAX) and a header rewrite.
- **Verdict: many.** No single site covers the read side, and there are three read entry points plus restart.

### Q4. Prewritten primitives
- **Partial:**
  - `patch.Before/After` plus `Revert`, which refuses on an "out of band change" (docker.go:353-396). This already computes "what the file held before we wrote it" and "still as we left it" for the truststore.
  - `OpenAndResolve` (dockerfs.go:139) resolves symlinks, but only at the leaf, not parent directories.
- **No primitive for the hard points:** parent-symlink identity at write time, sticky deletion, and directory own-mode against the image (the reference adds `withImage`).
- The partial primitive made the easy part easy. Every run reached at least 83/93. The traps sat in the neighbours the primitive does not reach.

### Q5. Design spread
- Every run built read-side masking over a ledger: one architecture, which splits on three independent choices:
  - (1) identity: requested path vs real path at write time;
  - (2) deletion seen on a read: sticky or not;
  - (3) directory provenance: pre-start snapshot vs image mode.
- Orion runs mostly got (1) and (2) right and failed only on (3). Orion #1b (rd70qv9yw1) and #11 (rd763td7tj) failed exactly one test, `TestDirectoryListedOnlyForAFileTheContainerRemovedIsLeftOut`.
- **The separating case was image-mode provenance.** The passer compared directory modes with the image. The near-passers trusted the pre-start `/changes` listing.

### Q6. Source of difficulty
- **Primary: multiplicity of independent neighbours of named rules.** Three separate state models (alias identity, sticky deletion, directory provenance), each tested along several lifecycles.
- **Secondary:** lifecycle/ordering (first write on a later start; symlink replaced between write and read), plus one repo-only regression (two custom-file keys).

### Q7. Gate check
- **(a)** Many read entry points and no interception at base: passes.
- **(b)** The partial primitive covers only the base value, not the hard points: passes, with a caution.
- **(c)** The obvious design fails at least 2 fair cases on different paths: passes (Orion fails directory provenance, Vega/Nova fail aliases and deletions).
- **(d)** Three independent axes: passes.
- **The gate would have rated it hard. Correct (1/16).**
- **Caveat:** the hardness comes from stacking roughly 10 trap families into 93 tests, and the FP check came back "Passed with caveats". The gate needs a cap on how many independent trap families one task may stack, or SQ/FP exposure grows with each one.

---

## 2. turso (tursodatabase/turso @ 6ef5e7b8)

### Q1. Hard points (final round, 11 failing runs)
testLog lists no names (it is truncated), so the counts come from evalResult:

| test | fails | in description? |
|---|---|---|
| matview-not-in-compound-number-text | 10/11 | **Implied neighbour of a named rule.** The description names "type affinity should work like a normal NOT IN too, even through a subquery made only of UNIONs" and gives the case example only ('A' vs 'a' under NOCASE). The failing case is the type analogue: under TEXT comparison affinity, a UNION must not merge integer 1 and real 1.0 before the comparison. |
| matview-not-in-negated-in-spelling | 9/11 | **Not named** (the Vega #6 evalResult says `was_mentioned_in_description: false`). This is an equivalent spelling, `NOT (x IN (SELECT ...))`. |
| matview-not-in-compound-types | 4/11 (all Nova) | Implied: ordinary IN takes affinity from the rightmost arm (`select_result_columns`, plan.rs:548); Nova used `compound_column_affinity` across all arms (plan.rs:65) |
| matview-not-in-intersect-case-variants | 3/11 | Implied: the collation override was dropped for a whole prefix that contains INTERSECT |

Representative evalResult reasoning:
- rd7dxvkf80: "build_plan_dag_node ... reads the ephemeral index's collations but ignores its affinity_str".
- rd7baepzk8: "find_not_in_terms only matches a top-level SubqueryResult with not_in: true".

### Q2. Obvious design vs correct design
- **Obvious design:** copy the existing positive-IN to semi-join rewrite (`try_rewrite_in`, unnest.rs:273) and the NOT EXISTS anti-join. Make NOT IN a NULL-aware anti-join. For compounds, keep the existing deduplicating SetOp and pass the NOT IN collation into it. The turso trajectory shows this plan at step 20: "Found the existing semi/anti join maintenance ...".
- **Divergence:**
  - The reference rewrites UNION to UNION ALL ahead of the anti-join, so that the final comparison, with its affinity and collation, decides membership (`match_compound_to_not_in`, `keeps_duplicates_equal`, `split_by_intersect_collation`).
  - It also unwraps `Unary(Not, ...)` in `find_in_term` (solution.patch around line 1093).
  - The ordinary planner gets this right by applying affinity when values are inserted into the ephemeral index (compound_select.rs:343-346). The IVM SetOp path has no such step.

### Q3. Choke points
- **Entry points:** CREATE MATERIALIZED VIEW, and INSERT/UPDATE/DELETE on the outer table or any table in the subquery, inside or outside a transaction.
- All of them run the plan compiled by `plan_view`, then `unnest_select_subqueries` (vdbe_maintenance/plan.rs:1044, rewrite call at :1060). The single rejection is at plan.rs:251-252 (`unsupported("subqueries")`).
- **Verdict: one site covers every entry point.** An agent who edits the rewrite gets every DML path right; no run failed a transaction or DML-path test.
- The "many" here is subquery shapes (straight vs correlated, compound arms, nested NOT IN, spellings), not entry points.

### Q4. Prewritten primitives
**Yes, several:**
- `try_rewrite_in` (unnest.rs:273) and `try_rewrite_exists` (unnest.rs:246) give the semi-join and anti-join pattern.
- `find_in_term` (unnest.rs:1348-1349) carries the comment "IN under OR and NOT IN stay as subqueries". It is also the trap, because it matches only a direct `SubqueryResult`.
- `in_subquery_side_collation` (collate.rs:414) computes the collation for NOT IN.
- IN comparison affinity is computed at subquery.rs:999-1019.
- It was still hard because no primitive applies the comparison affinity *before* compound deduplication in the IVM path. The one that does is in the regular emitter (compound_select.rs:343-346), and agents reused the IVM SetOp instead.

### Q5. Design spread
Three designs:
- (1) anti-join plus deduplicating SetOp with a collation override (most runs; fails number-text);
- (2) the same with all-arm `compound_column_affinity` (Nova; also fails compound-types);
- (3) UNION to UNION ALL plus rightmost-arm affinity (the reference and the passer, Vega #5 rd74tmn1tg).

How the passers were separated:
- **number-text separated design (3) from the rest.** The memory notes record this as the "binary dial": 0/13 on wip17.
- **negated-in-spelling, added at re-eval, separated Vega #5 from Vega #6.** Vega #6 failed only that test. It was found by mining the agents' own tests (olympus-turso-task1-learnings.md, step 3).

### Q6. Source of difficulty
- **Primary: a neighbour state of a named rule** in an intermediate stage. Equality used for deduplication differs from equality used for the final comparison.
- **Secondary: wording** (an unnamed equivalent spelling). Plus a repo-only convention (rightmost arm).

### Q7. Gate check
- **(a)** One site covers everything: **red flag, wrong here.**
- **(b)** Primitives exist (semi-join and anti-join rewrite, collation helper, IN affinity): **red flag, wrong here.**
- **(c)** The obvious design fails number-text, the spelling and compound-types (different neighbours): passes.
- **(d)** Three designs: passes.
- **The gate would have rated it too easy.** (a) and (b) measure entry-point breadth and do not see semantic depth inside the one site.
- **Check that would have caught it:** an "intermediate-semantics probe". When the promise is "behave like normal X", list every stage between input and the final comparison that merges, deduplicates or normalizes, and check whether it uses the same equality as the final comparison. Add an "equivalent-spelling probe": does the parser produce other ASTs for the same predicate?

---

## 3. elio (elio-fm/elio @ 49889695)

### Q1. Hard points (final round, 11 failing runs, from evalResult and testLog)

| test | fails | in description? |
|---|---|---|
| renames::file_renamed_in_duplicate_finder_is_selected_under_its_new_name | 8/11 (Orion 3, Vega 4, Nova 1) | **Covered by the general sentence** ("rename/move ... while you are in elio", "last file selected"), but Duplicate Finder is **not named**. The named routes are rename, bulk, editor, cut/paste and drag-and-drop. The rename site (duplicate_finder.rs:149) is discoverable only in the repo. Added at re-eval. |
| during_pastes::paste_cancelled_while_running_keeps_history_where_items_ended_up and moves_on_both_sides_of_a_cancel_are_followed_in_order | 4 and 3 | Implied ("only the ones that were moved should be affected"). **Lifecycle:** cancel, then start a new paste; the old result is dropped by the stale-token guard. |
| during_pastes::folder_you_are_in_moved_by_a_paste_started_elsewhere_stays_reachable and opening_a_folder_while_a_paste_moves_it_opens_it_at_its_new_path | 2 and 3 | Implied (live cwd/entries and pending load during a move) |
| renames::renaming_the_folder_you_are_in_keeps_forward_to_folders_inside_it | 1 | Named ("rename the folder your currently in") |

Why they failed:
- Duplicate Finder: the remap helper updated history and view memory, not the live listing behind the overlay, and `close_duplicate_finder` only refreshes the preview (rd70dnrf2v, rd7ex7aesw). Orion #6 (rd7azxk4n4) built `new_path.join("")`, which gives a trailing slash.
- Cancel: moves were applied behind `paste_job_is_current` (file_operation_results.rs:82-84). Starting a new paste increments the token, so completed moves are dropped (rd704bpb58, rd7ex8rjwr).

### Q2. Obvious design vs correct design
- **Obvious design:** record (old, new) pairs at each named rename/move site. Add one helper that rebases history back/forward entries and `directory_view_memory`. Apply paste moves where paste results are applied today.
- The elio trajectory rd70dnrf2v shows this at step 24: "Traced all rename entry points ... Moves need explicit success mappings captured before mutation".
- **Divergence:**
  - The reference keeps an ordered move log that is consumed independently of whether the paste result is still current (`background_job_processing.rs`, `scheduler.rs`).
  - It updates live entries, cwd and pending loads, and reloads the folder behind Duplicate Finder.
  - The passer (Orion #8, rd7bpecmxg) applies `build.path_changes` **before** the stale-token guard and routes Duplicate Finder through the same `apply_internal_path_changes`.

### Q3. Choke points
**Entry points:**
- (1) single rename: `confirm_rename`, rename.rs:113 (`fs::rename`);
- (2) bulk rename and (3) editor bulk rename: both through `apply_rename_plan` / `apply_rename_ops`, editor_bulk_rename.rs:255/421;
- (4) Duplicate Finder rename: duplicate_finder.rs:149 (its own `fs::rename`);
- (5) cut/paste and (6) drag-and-drop: both through the paste worker, copy_move.rs:256 (`ClipOp::Cut => fs::rename`). Its result is applied in `apply_paste_job_result` (file_operation_results.rs:82), behind `paste_job_is_current` (copy_move.rs:153).

**State to update:** `DirectoryHistory.back/forward` (directory_loading.rs:29-31), `directory_view_memory`, live cwd/entries, and `pending_load`.

**Verdict: many.** Four distinct mutation sites and an async result path. No one site covers them.

### Q4. Prewritten primitives
- **No path-rebase helper** at base (no `rebase`, `remap` or `relocat` functions).
- **Partial helpers that exist:**
  - `PasteBuild.destination_paths`, "Destination paths actually written by the completed paste/drop" (job_results.rs:226-227). This covers "use the new name" for conflicts.
  - `duplicate_rename_pairs` from bulk renames (editor_bulk_rename.rs:257-260) and `apply_duplicate_rename_pairs` (duplicate_finder.rs:372).
  - `current_directory_escape_for_paths` (directory_loading.rs:93-99), which is for deletions.
- **Traps in the nearest pattern:**
  - `PushCurrent` clears Forward (directory_loading.rs:122-129), which Nova #4 fell into.
  - The stale-token guard (file_operation_results.rs:82-84), which every cancel failure fell into.

### Q5. Design spread
- One family: per-site pairs plus a rebase helper. The variants are completeness choices: the live listing, and whether moves are applied before or after the freshness guard.
- The reference (independent move log) and the passer (apply before the guard) are two genuinely different ways to handle the cancel case.
- **What separated them:**
  - On the first 40-test suite, Orion was 4/4. Its four runs already handled the cancel case; Vega's runs did not (Vega #9/#12 summaries: "completed moves are forgotten when a cancelled paste is superseded").
  - **The re-eval Duplicate Finder test separated Orion #8 from Orion #5/#6/#7.** Orion #8 updated the live listing; the others did not, and #6 also had the trailing-slash bug.

### Q6. Source of difficulty
- **Primary: an unnamed second code path** (Duplicate Finder rename, covered by the general sentence) combined with live-view state.
- **Secondary: lifecycle.** A freshness guard drops a result that carries irreversible facts.

### Q7. Gate check
- **(a)** Many sites: passes.
- **(b)** No rebase primitive: passes.
- **(d)** Spread: passes.
- **(c)** **Would have failed**, had the spike been run on the first test suite: the obvious per-site design passed all 40 first-suite tests for Orion (4/4).
- **(a) and (b) over-rated the seam.** Agents enumerate named sites well. Difficulty appeared only after an unnamed site and a guard-lifecycle case were added.
- **Check that would have caught it:** split the entry points into named vs unnamed-but-covered, and require at least one covered entry point the description does not name. Add a freshness-guard check: grep for guards that drop results (token/generation checks) on the path that carries the promised fact.

---

## 4. swift (openstack/swift @ 6adb10d7), finalizing review

### Q1. Hard points (final round, 11 failing runs)

| test | fails | in description? |
|---|---|---|
| TestCreateOnlyS3Writes::test_racing_s3_writes_leave_nothing_of_the_refused_one | 11/11 (Orion 3, Vega 4, Nova 4) | **Named rule, implied neighbour.** "If a write returns 412 it should not leave any artifacts behind" is named. The failing sub-case is the race run while object-server DELETE is unavailable: cleanup fails, and the run answers 412 anyway (Vega/Nova). Orion instead raced past a HEAD preflight. |
| TestCreateOnlySwiftWrites::test_racing_swift_writes_leave_nothing_of_the_refused_one | 3 (all Orion) | Named (concurrency sentence). The Orion runs stripped If-None-Match after a HEAD preflight (rd71bkahse, rd74yhxrvs: object_versioning.py:513/580). |
| TestCreateOnlyS3Writes::test_existing_key_is_refused_with_412_and_bucket_unchanged | 9 (Vega 4, Nova 4, Orion 1) | Named rule ("current object, then 412"). The failing sub-case is a create-only CompleteMultipartUpload re-sent after it completed. The `already_uploaded_s3_etag` fast path (multi_upload.py:765-771) returns 200 without reaching any destination PUT, so it is a **second code path that is discoverable only in the repo**. |
| test_absent_key... / test_key_whose_latest_version_is_a_delete_marker... | 1 (Nova #2) | Named. Nova #2 missed the source HEAD in `check_copy_source` (s3request.py:1700). |

### Q2. Obvious design vs correct design
- **Obvious design (Orion):** "Native storage checks already enforce create-only; middleware must preserve the condition and reject before side-effecting version writes" (trajectory rd74yhxrvs, plan at tool call 25). That means a HEAD preflight, then removing If-None-Match before the version write and the symlink publish. This is a check-then-act design and it loses the race.
- **Second obvious design (Vega/Nova):** keep the condition on the symlink and roll the version back on 412, but never check whether the DELETE succeeded (`_delete_version` only logs; rd7cd4kge5 object_versioning.py:598-641).
- **Reference:** keep the condition on the final symlink PUT and drop it only from the private version write. On a late 412, delete the version and return 412 only if the delete succeeded, otherwise 503. Separately, raise 412 when a completed upload is completed again (`not is_marker and is_create_only(req)`, solution multi_upload.py hunk at line 672).
- The passer (Orion #11, rd77cwy35p) is the same design, line for line in spirit.

### Q3. Choke points
- **Entry points and their sites:**
  - S3 PutObject: s3api, then proxy, then object_versioning `handle_put` (object_versioning.py:549) when the bucket is versioned.
  - S3 CopyObject: `check_copy_source` source HEAD (s3request.py:1700), then copy middleware `_get_source_object` (copy.py:393).
  - S3 CompleteMultipartUpload: multi_upload.py:765-771 fast path.
  - Swift PUT and COPY/X-Copy-From: copy.py.
  - Bulk extract-archive: bulk.py subrequest PUT.
  - Legacy versioned containers: `handle_obj_versions_put`, then `_copy_current` (legacy.py:476/437).
  - New versioning: `_copy_current` (object_versioning.py:494), `_put_versioned_obj_from_client` (381), `_put_symlink_to_version` (443).
- **Verdict: many**, about seven sites. On unversioned containers, plain PUT is already covered by the object server.

### Q4. Prewritten primitives
- **Yes, for the core:**
  - The object server enforces `If-None-Match: *` atomically (obj/server.py:866-869).
  - The proxy maps any 412 from a backend putter (obj.py:727).
  - So a plain create-only PUT already works at base. That is why the first 6-test version was Vega 4/4, Orion 3/4.
- Agents did trace all the paths: rd74yhxrvs passed every multi-path scenario.
- What stayed hard is not computed by any primitive:
  - the window between the irreversible version write and the conditional symlink commit;
  - the state where the rollback itself fails;
  - the fast path that returns success without writing.

### Q5. Design spread
Three designs:
- (1) preflight and strip the condition (Orion #9/#10/#12);
- (2) conditional commit plus unchecked rollback (all Vega and Nova);
- (3) conditional commit, checked rollback, 503 when the rollback fails (the reference and Orion #11).

The multipart fast path is an independent axis. Orion mostly fixed it (#10 and #12 pass that test); every Vega and Nova run missed it.

**What separated the passer:** the deletes-unavailable sub-case of the race test (design 3) together with the multipart retry. History from the run summaries:
- 10-29 re-eval: "cleanup failure must not answer 412" took Vega from 4/4 to 0/4.
- 11-01: the HEAD-preflight race took Orion #9/#10/#12 down; Orion #11 stayed.

### Q6. Source of difficulty
- **Primary: a neighbour state of an exception** (the rollback after a refused write itself fails), plus **lifecycle/concurrency** (check-then-act around an irreversible step).
- **Secondary: a short-circuit second code path** (the completed-upload fast path).

### Q7. Gate check
- **(a)** About seven sites: passes, but **misleading**. The first rollout (6 tests) was Vega 4/4, Orion 3/4: agents enumerate the sites easily.
- **(b)** The object server primitive: **red flag, correct.** The core was easy.
- **(c)** On the final cases the obvious designs fail at least 2 fair cases (race, cleanup failure, multipart retry): passes, but only for cases found after the first rollout.
- **(d)** Three designs: passes.
- **The stage-0 gate could have rated this seam either way.** (b) correctly predicted an easy core. The real hard points (irreversible step before the conditional commit, rollback failure, success fast path) are not in the gate.
- **Checks that would have caught them:**
  - "irreversible-step-before-commit": list the side effects that happen before the condition is enforced, then ask what the response is when the undo fails;
  - "short-circuit success grep": paths that return 2xx without reaching the enforcement site.
- **Caveat from the notes (olympus-swift-rescope-20261029.md):** do not escalate this lever into a distributed-consistency promise. Concurrency claims in an eventually consistent store kept producing new SQ Highs.

---

## Verdicts

**Docker proxy.** Hard from the first rollout (1/16) because the seam stacks three independent state models: alias identity at write time, sticky deletion seen on a read, and directory provenance against the image. Each is tested through several lifecycles behind three read endpoints that base never intercepts. The base `patch{Before,After}` primitive made the shallow part easy (every run reached at least 83/93) and left every neighbour open. Orion failed on directory provenance, Vega/Nova on aliases and deletions; the lone passer compared directory modes with the image. The gate would have called it hard. The risk is trap stacking (93 tests, FP "passed with caveats"), not under-difficulty.

**turso.** One choke site and rich primitives (semi-join and anti-join rewrites, collation and affinity helpers), yet 1/12. The difficulty is an intermediate stage, compound deduplication, that uses a different equality than the promised NOT IN comparison: integer 1 vs real 1.0 under TEXT affinity. An unnamed equivalent spelling (`NOT (x IN ...)`) was added at re-eval to split the last two passers. Gate checks (a) and (b) would both have raised false red flags. The missing check is a semantic-layering probe inside the single site.

**elio.** Many sites and no rebase primitive, so the gate would rate it hard, but the first 40-test suite was Orion 4/4: agents enumerate named rename and move routes reliably. It became 1/12 only when the re-eval added an unnamed-but-covered route: a Duplicate Finder rename, where the selection must follow in the live listing behind the overlay. A cancel-then-new-paste lifecycle case, where the existing stale-token guard drops completed moves, had already sunk Vega. The gate over-rated the seam. It needs a named-vs-unnamed entry-point check and a freshness-guard check.

**swift.** The core create-only behaviour is already enforced atomically by the object server, so the first rollout was easy (Vega 4/4, Orion 3/4), and gate check (b) was right. Final hardness (1/12) came from three cases: the window between the irreversible version write and the conditional symlink commit (Orion's preflight design loses the race); the state where the rollback DELETE fails (Vega/Nova answer 412 anyway); and the completed-upload fast path that returns 200 without writing. None of these is in the stage-0 gate. The lever must stay a deterministic local behaviour, not a distributed-consistency promise.

## Summary table

| task | hard point | source | choke points one/many | primitive yes/no | obvious design fails? | design spread | gate verdict |
|---|---|---|---|---|---|---|---|
| docker proxy (1/16) | directory provenance (pre-start listing vs image mode); alias identity at write time through replaced symlinks; deletion seen on a read is sticky; two custom-file keys for one file | multiplicity of neighbours of named rules + lifecycle; one repo-only regression | many: 3 read endpoints never intercepted; writes share `WriteFile` but callers own the "before" state | partial: `patch.Before/After` + `Revert` (docker.go:353-396); none for the hard points | yes: Orion fails provenance, Vega/Nova fail aliases and deletions (83-92/93) | one architecture, 3 independent axes; passer separated by image-mode provenance | gate says hard: **correct**; add a cap on stacked trap families |
| turso (1/12) | UNION dedup merges 1 and 1.0 before the TEXT NOT IN comparison; `NOT (x IN ...)` spelling; rightmost-arm affinity | neighbour state of a named rule in an intermediate stage; unnamed equivalent spelling | **one** (`unnest_select_subqueries`, plan.rs:1044/1060) | **yes**: `try_rewrite_in`, NOT EXISTS anti-join, `in_subquery_side_collation`, IN affinity (subquery.rs:999-1019) | yes: number-text fails in 10/11, spelling in 9/11 | 3 designs; number-text separated UNION ALL from dedup, spelling split the last two | (a)+(b) red-flag it as easy: **wrong**; needs a semantic-layering probe |
| elio (1/12) | Duplicate Finder rename leaves the live selection stale; a cancelled paste's completed moves are dropped by the stale-token guard; moved current folder | unnamed second code path + live-view state; lifecycle (freshness guard) | many: 4 mutation sites + async paste/drop result | no rebase helper; partial `destination_paths`, `duplicate_rename_pairs` | **no on the first suite** (Orion 4/4 on 40 tests); yes after re-eval | 1 family + completeness variants; 2 cancel designs (move log vs apply before guard); DF test separated the passer | (a)+(b) say hard: **over-rated**; needs a named-vs-unnamed entry-point check and a freshness-guard check |
| swift (1/12, in review) | late 412 must undo its version and answer non-412 if the undo fails; HEAD preflight loses the race; re-sent completed multipart returns 200 | neighbour state of an exception (rollback fails) + concurrency/lifecycle; short-circuit second path | many: about 7 middleware sites | **yes**: object server atomic If-None-Match (obj/server.py:866-869) | first suite: no (Vega 4/4); final: yes (3 failure designs) | 3 designs + independent multipart axis; cleanup-failure check + multipart fast path separated the passer | (b) correctly flagged an easy core; final hard points not in the gate; needs irreversible-step and fast-path checks |

## Checks our workflow is missing

1. **Named vs unnamed entry points (stage 0).** From the repo grep, list every site that performs the promised mutation or read (every `fs::rename`, subrequest PUT, endpoint). Mark the ones the description names. Agents reliably cover named sites (elio first suite: Orion 4/4; swift first suite: Vega 4/4). Require at least one fair, covered-but-unnamed site, such as elio's Duplicate Finder or swift's multipart fast path. Otherwise "many choke points" does not mean hard.
2. **Short-circuit success grep.** Look for paths that answer success before reaching the shared enforcement site: idempotent-retry fast paths (swift multi_upload.py:765-771), matchers that accept only one AST shape (turso unnest.rs:1349), early-return caches. Each is a candidate hard point that the choke-point map hides.
3. **Freshness-guard and async-lifecycle check.** Grep for token, generation or "is current" guards on the result path (elio file_operation_results.rs:82-84). If an irreversible fact such as a completed move rides on a result the guard can drop, that is a lifecycle hard point.
4. **Semantic-layering probe at a single choke site.** When the promise is "work like the normal X", list each intermediate merge, dedup or normalize stage and compare its equality with the final comparison's (turso SetOp dedup vs NOT IN affinity). This replaces the automatic red flag from gate checks (a) and (b) when one site covers everything: turso had one site plus primitives and was 1/12.
5. **Identity-timing probe.** Is identity (path, key, file) resolved when it is recorded or when it is used? Can the namespace change in between (a docker symlink replaced, an elio folder moved mid-paste)? Two plausible timings mean a design-spread axis.
6. **Exception-neighbour probe.** For every "must not leave X / must not show Y" promise, ask what happens when the undo or cleanup itself fails, or when the evidence arrives as an error (swift DELETE unavailable; docker deletion seen as a 404 on a directory archive). These were the decisive cases in swift and the commonest Vega/Nova misses in docker.
7. **Equivalent-spelling probe.** For parser or grammar seams, list synonyms that reach different ASTs (`NOT (x IN ...)` vs `x NOT IN ...`). This found turso's final split, but only after the rollout, by mining the agents' own tests.
8. **Obvious-design spike must run before the first rollout, on cases planned at stage 0.** In three of four tasks the decisive test was added at re-eval (elio +1, turso +1, swift 6 to 8 to 10). Stage 0 should name at least 2 such fair, unnamed or neighbour cases up front from checks 1-7, rather than discovering them by mining near-passers.
9. **Refine gate checks (a) and (b) to be advisory, not vetoes.** A primitive or a single site is a red flag only if it also already handles the neighbours (swift: right; turso: wrong). Many sites is a green flag only if some are unnamed or carry lifecycle state (elio: wrong as stated).
10. **Trap-stack cap.** Count independent trap families per task. Docker had about 10 families in 93 tests and an FP result of "passed with caveats". Each extra family adds FP/SQ exposure without being needed for the gate: one deep family plus one neighbour sufficed for turso, elio and swift.
