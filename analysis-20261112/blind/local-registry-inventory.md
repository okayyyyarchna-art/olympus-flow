# Decision inventory: local vs registry lookup (safedep/vet @ 0fbe25b2)

Requirement: look up every package version that some manifest installs from the registry, even when another
manifest has it as a local package; a version that is only local is not looked up; also for continued scans.

Paths are relative to `claude-code/challenges/cc-vet-local-registry/base`.

## How the code works today (cited)
- A package row is per manifest (`vet_scan_manifest_packages`, keyed `(manifest_id, pkey)`), and the `local` mark lives
  only in that row's JSON (`internal/state/scanfile.go:70-77`, `:355-359`, `:413-419`). Enrichment data is stored once
  per pkey (`internal/state/scanfile.go:63-69`, `:742-766`) and joined back into every manifest's row
  (`internal/state/query.go:70-72`).
- The enrich stage pages distinct pkeys with `PackagesToEnrich`, which picks ONE representative row per pkey: the row
  of the manifest whose id sorts first (`internal/state/query.go:408-414`, subquery `ORDER BY manifest_id LIMIT 1` at
  `:412`).
- `enrichBatch` skips any row that is not `Checkable()` (`!Local && version != ""`) for a registry enricher and records
  it as `EnrichmentOK` (`internal/engine/enrich.go:177-181`, `model/package.go:107-109`).
- `ok` and `not_found` count as done forever for that pkey (`internal/state/query.go:404-407`, `:428-432`). A continued
  scan re-extracts changed files (`internal/engine/extract.go:35-65`) and then only enriches pkeys without such a
  status.
- Core bug: if the first-sorting manifest has the version as local, the version is recorded `ok` without a lookup, so
  `vuln` never sees an Insight (`internal/plugins/controls/vuln/vuln.go:44-50`).

## Decisions

| # | Decision | Nearest repo idiom or helper (file:line) and what it would decide | Right or wrong for the requirement (one concrete input where the two differ) | Kind | Fair route |
|---|---|---|---|---|---|
| 1 | Where to decide "registry or local" for a pkey that several manifests carry | `PackagesToEnrich` representative row `ORDER BY manifest_id LIMIT 1` (`internal/state/query.go:410-412`) plus per-row `Checkable()` (`internal/engine/enrich.go:179`, `model/package.go:109`). Copying it keeps the per-row answer | This is the reported bug, and the fix site is obvious. Input: manifest A (id sorts first) has npm `foo@1.0.0` as a workspace member, and B's package-lock installs `foo@1.0.0` from the registry. Today: no lookup. Correct: one lookup. Any obvious fix (prefer a non-local row, or "any non-local row exists") gets the single-scan case right | none (core site) | Requirement sentence 2; the one `PackagesToEnrich` call (`internal/engine/enrich.go:148`) |
| 2 | Continued scan: what to store for a pkey skipped as local-only, and whether that stored status still counts once a registry row appears | Skip writes `Status: EnrichmentOK` (`internal/engine/enrich.go:180`). The `enriched` filter treats `ok` as done forever (`internal/state/query.go:431-432`). The existing test pins "each package gets a result" for uncheckable packages (`internal/engine/enrich_test.go:21-44`, assertion at `:40`), so an implementer keeps writing `ok`. The only re-try idiom is for failures (`internal/engine/enrich.go:16-18`) | **Wrong.** Run 1: A has `foo@1.0.0` local only (B absent, or B at `foo@2.0.0`); the scan is interrupted after foo's batch (the `interrupt` helper, `internal/engine/interrupt_test.go:29-46`). Then B is added or edited so it installs `foo@1.0.0` from the registry, and the scan continues. With the row-selection fix only, foo@1.0.0 still has insights=`ok` from run 1, so it is never looked up and its advisory is missing. Correct: looked up in run 2. Needs a distinct "skipped/local" status that counts as done only while no registry row exists, or no stored status for skips | K5 (decision taken at an earlier run's moment) | Requirement: "This also applies to continued scans." Re-extraction on continue: `internal/engine/extract.go:39-43`, `:63`. Failed-batch re-try comment: `internal/engine/enrich.go:16-18` |
| 3 | Which rows count as "some manifest installs it": in pull-request mode, the REMOVED rows of the base side | Delta mode stores base-only packages as rows with `Change=REMOVED` in the same table. Removed manifests keep the base package objects, Local included (`internal/engine/delta.go:350-366`). Packages removed inside a modified manifest are rebuilt as `&model.Package{ID, Direct, Dev, Change: REMOVED}`, which **drops `Local`** (`internal/engine/delta.go:258-262`). Both natural fixes, "prefer a non-local row" and "EXISTS non-local row", count that REMOVED row as a registry install | **Wrong.** `--base-ref` scan. Base: B lists `foo@1.0.0` (from the registry, or as a workspace member that the diff turns into Local=false). Head: B no longer has foo, and A adds `foo@1.0.0` as a local package (ADDED, so `introducedFilter` lets the pkey through, `internal/state/query.go:434-440`). Naive fix: foo@1.0.0 is looked up, its Insight joins A's local row, and `vuln` reports an introduced advisory on A (`internal/engine/delta.go:381-393`). Correct: only local at head, so no lookup and no advisory. Fix: ignore `change = 'REMOVED'` rows when deciding | K3 (base side of the comparison) + K4 (diff drops Local) | Requirement: "some manifest *installs*", and "a version that is only a local package is not looked up". Repo: `ChangedOnly` already excludes REMOVED (`internal/state/query.go:243-245`); the removed-row construction is visible at `internal/engine/delta.go:255-262` |
| 4 | Identity used to group rows across manifests | Every query groups by `pkey = ID.Key()` (`internal/state/scanfile.go:409`, `internal/state/query.go:412`) | Right: the normalised key joins differing raw spellings of the same version | none | `model/package_version.go:136-137` |
| 5 | Which enrichers the rule applies to | `!e.Local` exempts enrichers that call no registry (codeusage) (`internal/engine/enrich.go:179`, `internal/engine/engine.go:60-62`, `internal/plugins/enrichers/enrichers.go:104-106`) | Right if the branch is kept: registry enrichers (insights, malysis, actionrefs) all go through the same check | none | Same lines |
| 6 | Second callers of the selection logic | `PackagesLacking` uses the same representative-row pattern (`internal/state/query.go:370-379`) but only tests call it (`internal/state/query_test.go:154`). `enrichPrior` builds `&model.Package{ID}` with no Local mark (`internal/state/query.go:465-491`), so it always looks up the previous versions | No observable difference for the requirement. The single production path is `enrichWith` → `enrichBatch` (`internal/engine/enrich.go:148-162`) | none | n/a |
| 7 | Where to keep a per-row "local" flag if the fix filters in SQL | Idiom: "Rows hold the record JSON next to the columns that queries filter on" (`internal/state/scanfile.go:30-32`). A new statement must be appended at the end (`internal/state/migrations_test.go:11-13`), and the format must be raised when old files become unreadable (`internal/state/scanfile.go:21-25`). Alternatives need no schema change (filter in Go, or one query per local pkey) | The comments steer to the right answer. An old-format stopped scan simply starts again (`internal/state/store.go:123`). Not wrong-by-default | none | Same comments |
| 8 | Cache interaction | Cache lookup is per pkey and runs only on `todo`, after the skip (`internal/engine/enrich.go:185-192`). Local skips never reach the cache | Right as is | none | n/a |
| 9 | After the fix, should the LOCAL manifest's row also show the advisory? | Enrichment is per pkey and joined into every row (`internal/state/query.go:70-72`, `internal/state/scanfile.go:355-356`). `vuln` has no Local check (`internal/plugins/controls/vuln/vuln.go:44-50`), so the advisory appears on both A and B | The requirement does not decide this. It speaks about lookup, not about reporting per manifest. Not counted. Risk if hidden tests count findings per manifest | ambiguous (K5) | None in the requirement |
| 10 | Continued scan, reverse direction: run 1 looked foo@1 up (B had it from the registry); B is then removed, and only A's local foo@1 remains | Stored enrichment stays in `vet_scan_packages` (`internal/state/scanfile.go:742-766`); `deleteManifestsTx` deletes no enrichment (`internal/state/scanfile.go:530-541`). A's local row then carries the stale Insight and `vuln` reports it. The repo idiom for other data is "a continued scan holds the data of its last run only" (`internal/state/scanfile.go:672-685`) | The requirement says it is "not looked up". Run 2 makes no call, but the old data is still reported. Whether that breaks "not looked up" is ambiguous. Not counted. Risk if a test checks findings | ambiguous (K6) | Weak: the Replace* comment only |

## Result

**GREEN**: 2 wrong-by-default decisions, of different kinds and on different paths, each with a fair route.

Wrong-by-default:
- #2 K5, `internal/engine/enrich.go:180` + `internal/state/query.go:431-432` (test pin `internal/engine/enrich_test.go:40`): the version is local-only in run 1, which is interrupted after its batch; a second manifest then installs it from the registry and the scan continues. The stale `ok` skip status blocks the lookup.
- #3 K3+K4, `internal/engine/delta.go:258-262` / `:350-366` with `internal/state/query.go:412`: `--base-ref` scan where the base had `foo@1` in B (registry, or local with Local dropped by the diff) and the head adds `foo@1` only as local in A. The REMOVED row counts as a registry install, so a lookup happens and an advisory is reported on a local-only version.

Rated none:
- #1 core representative-row fix (`internal/state/query.go:412`): the obvious fix is right for a single scan.
- #4 identity by `pkey` (`internal/state/scanfile.go:409`): right.
- #5 `!e.Local` enricher exemption (`internal/engine/enrich.go:179`): right if kept.
- #6 `PackagesLacking` (tests only) and `enrichPrior` (`internal/state/query.go:370-379`, `:465-491`): no observable effect.
- #7 schema column, migration order and format bump (`internal/state/scanfile.go:21-32`, `internal/state/migrations_test.go:11-13`): the comments lead to the right answer.
- #8 cache (`internal/engine/enrich.go:185-192`): unaffected.

Ambiguous, not counted: #9 (an advisory also shown on the local manifest's row) and #10 (stale Insight reported after the registry manifest leaves a continued scan).
