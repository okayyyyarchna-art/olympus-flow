# Decision inventory: finding.introduced_by (safedep/vet @ 2eb6e8e0)

Requirement: a finding on a package that is not a direct dependency lists the direct dependencies that pull the
package in. Policy rules read the list as `finding.introduced_by`. When the list is empty, or vet can't be sure it
is complete, the field is not set.

Repository: `C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-direct-deps/base`. All paths below are relative to it.

## Background facts (cited)

- `model.Graph` is per manifest. Its roots are documented as "the direct dependencies" (model/graph.go:8-9,
  model/graph.go:58-61, docs/glossary.md:95-96). An **open node** "may depend on any package"
  (model/graph.go:10-12, docs/glossary.md:104-106).
- `PathTo` gives one shortest path from a root (model/graph.go:138-170). `PathFrom` gives one shortest path and
  "only the paths of known edges" (model/graph.go:172-216). `MayReach` also counts a path through an open node
  (model/graph.go:214-241). `Parents` lists one level of parents (model/graph.go:113-123).
- Lockfile graphs come from the extractor. In them a root and `Package.Direct` match: a package with no parent, or
  one that is marked direct, becomes a root and gets `Direct = true` (internal/plugins/extractors/scalibr/convert.go:206-229).
- A manifest with no extractor graph gets its graph from a `plugin.Grapher`, the codeusage enricher
  (internal/engine/extract.go:347-366). That graph is a graph of imports for go.mod and for Python manifests
  (internal/plugins/enrichers/codeusage/modgraph.go:35-45). Its roots are the modules that the code imports
  (modgraph.go:230-244, pygraph_cgo.go:186-197). Graphers are the only code that calls `MarkOpen`
  (modgraph.go:247, pygraph_cgo.go:182, pygraph_cgo.go:201).
- go.mod is a lockfile-kind manifest (internal/plugins/extractors/scalibr/kind.go:42) with no extractor edges, so
  `Package.Direct` stays false for every package (convert.go:117-126). The golden output shows `toml`, a direct
  require in testdata/go/go.mod, as `"direct": false` (internal/plugins/extractors/scalibr/testdata/golden/go.json:32).
  A manifest-kind file such as requirements.txt marks every package direct (convert.go:119-125).
- The engine sets fields that a control cannot set: `Attack` (evaluate.go:110) and `Reach` (finding/finding.go:36-38,
  evaluate.go:64-65). Findings are stored as JSON (internal/state/scanfile.go:662-672). A saved report holds no graph
  (model/manifest.go:83-84 `json:"-"`, internal/reportdoc/doc.go:213-217). `vet report show --policy` re-gates the
  saved findings with `Finalize` (internal/runner/saved.go:207-218).
- The policy input comes from a JSON round trip (internal/policy/input.go:160-176). "An optional field that has no
  value is absent: test it with has()" (input.go:12-13). An absent key does not match and raises no error
  (internal/policy/cel.go:164-185). A fail rule that errors fails the gate as broken (finding/finding.go:349-351).

## Decisions

| # | Decision | Nearest repo idiom or helper (file:line) and what it would decide | Right or wrong for the requirement (one concrete input where the two differ) | Kind | Fair route |
|---|---|---|---|---|---|
| 1 | Where to compute the list, and where to keep it | Engine-owned finding fields: `Reach` is set in `evaluateManifest` after the control runs (internal/engine/evaluate.go:54-70, finding/finding.go:36-38). It is stored with the finding JSON (scanfile.go:662-672) and read back by the saved-report path (reportdoc/doc.go:221-238). Copying this gives a `Finding` field set in the engine. | Right. Computing the list inside the policy input from `m.Graph` would fail on `vet report show --policy report.json`, because a saved report has no graph (manifest.go:83-84, reportdoc/doc.go:213-217). That is not the nearest idiom, though. `FindingInput` fields all copy from `f` (input.go:101-105). | none | The requirement says "Such a finding should list". Also finding.go:36-38. |
| 2 | Which helper answers "which direct dependencies pull it in" | `Reach.Via` and `pathFromImported` give one shortest path from a package the code imports (finding/finding.go:129-131, internal/engine/reach.go:193-200, reach.go:328-339). `PathTo` and `PathFrom` also give one path (graph.go:138-212). Copying any of these gives at most one entry. With `Via`, that entry is the first imported package, which can be a transitive package. | Wrong. Input: package-lock.json with roots `express` and `koa`, both depending on `qs`, and a vulnerability finding on `qs`. Right: `[express, koa]`. With a one-path helper: `[express]`. If the code imports `body-parser` (transitive) and it leads to `qs`, `Via[0]` gives `body-parser`, which is not a direct dependency. | K1 | The requirement says "list the direct dependencies" (plural, all of them). `Roots()`/`Parents()` (graph.go:103-123) and `MayReach` for each root (graph.go:217) sit in the same file. |
| 3 | Which findings and which scans get the list (caller context) | `setReach`, the sibling that writes the dependency path, runs only when `r.reach.Status == ReachComputed` and `f.Family == FamilyVulnerability` (reach.go:85-94). Reach is not computed with `--reach off`, with no source directory (reach.go:33-41), or when codeusage is off or unavailable (internal/runner/runner.go:495-503). `reachOf` returns nil when `p.Usage == nil` (reach.go:118-120). Putting the new code inside or beside `setReach` with its guard gives the list only on vulnerability findings, and only in a scan that traces code. | Wrong. Input: package-lock.json with `express -> qs`. Run (a) a malware, cooldown or license finding on `qs`, or (b) `vet scan --reach off` with a vulnerability on `qs`. Right: `introduced_by = [express]` in both. Copied guard: absent. | K2 | The requirement says "a finding on a package" and names no family or reach mode. `annotateUsage` (evaluate.go:64, evaluate.go:173-195) is the sibling that runs for every family. |
| 4 | What counts as a "direct dependency", for the gate and for the list entries | Two nearby identities. (a) `Package.Direct` / `Subject.Package.Direct` (finding/finding.go:266, finding/build.go:42, policy/input.go:45, license.go:149-151). go.mod never sets it (convert.go:117-126, golden go.json:32). A Grapher graph never updates it (extract.go:347-366). (b) `Graph.Roots()` (graph.go:103-106). In a Python graph of imports, roots are only the imported distributions, while requirements.txt marks every package direct (convert.go:119-125, pygraph_cgo.go:186-197). Each identity alone is wrong on one path. | Wrong. Input A: go.mod plus a module graph where main imports `A` and `B`, `B` imports `A`, and `A` imports `T`. Finding on `T`: right `[A, B]`. With (a) alone: absent, because no package is `Direct`. Finding on `A`: right is absent, because `A` is a root. Gating on `Direct=false` and listing roots gives `[B]` (or `[A, B]`). Input B: requirements.txt listing `requests` and `urllib3`, where only `requests` is imported and imports `urllib3`. Finding on `urllib3`: right is absent, because it is declared direct. With (b) alone: `[requests]`. Right rule: direct = `p.Direct` or a graph root. | K5 | docs/glossary.md:95-96 and graph.go:8-9,58 ("roots are the direct dependencies"). golden go.json:32 shows that Go packages are never `Direct`. convert.go:119-125 for manifest kinds. |
| 5 | When the list is "not sure to be complete" (open nodes) | A reverse walk over `Parents()`, or `PathFrom` for each root, follows known edges only (graph.go:113-123, graph.go:214-216). Copying either sets a partial list when an open node can also lead to the package. | Wrong. Input: a Go graph of imports with roots `A` (open: no source on disk, modgraph.go:244-247) and `B`, and a known edge `B -> T`. Finding on `T`. Right: absent, because `A` may import `T`. Known-edge walk: `[B]`. The over-cautious variant, "any open node means absent", is also wrong. With a single root `A`, `A -> T` known and `A -> O` with `O` open, the right answer is `[A]`, since no unlisted root can reach `O`. Right rule: absent when a root that is not listed `MayReach`es the package. | K6 | The requirement says "or vet can't be sure the list is complete". `MayReach` doc (graph.go:214-216) and glossary:104-106. The same PathFrom-then-MayReach pattern is in reach.go:308-313. |
| 6 | How "not set" reaches the rule (intermediate JSON step) | `FindingInput` fields have no `omitempty` (input.go:21-32). The list fields next to them, `Licenses` and `Vulnerabilities`, are always present as `[]` (input.go:54, 62, 130). `activation()` turns the struct into a JSON map (input.go:160-176). Copying the sibling style gives a present `null` or `[]` key on every finding. | Wrong. Input: a finding on a direct dependency, with rule `!has(finding.introduced_by)`. Right: it matches. With a present key: `has()` is true, so it does not match. A fail rule `"express" in finding.introduced_by` errors on `null` and fails the gate as broken (finding.go:349-351). Absent, it does not match (cel.go:164-185). | K4 | The requirement says "it should not be set". input.go:12-13 says "absent: test it with has()". Optional siblings use pointers with `omitempty` (input.go:58-64). |
| 7 | Findings that a second path creates: policy package rules | Package-rule findings are built in `Finalize` with `finding.ForPackage` (internal/policy/finalize.go:101-170). That runs after `evaluateManifest` and outside it, the only place where the engine adds its fields. Copying the engine idiom gives these findings no list. | Wrong (medium confidence). Input: package-lock.json with `express -> qs` and a policy package rule `warn` with `when: package.name == "qs"`. The live scan's `Finalize` store loads the graph (internal/state/query.go:19-20, 54-92). Right: the `policy` finding on `qs` has `introduced_by = [express]`. Engine-only: absent. (Re-gating a saved report has no graph, so absent is correct there.) | K3 | "When vet reports a finding on a package...". `git grep "ForPackage("` finds finalize.go:165. |
| 8 | Which manifest's graph | `plugin.State.Dependents` yields one level of parents "in any manifest" (internal/state/query.go:276-293, plugin/plugin.go:107). Used recursively, it would mix lockfiles: `qs` under `express` in a/package-lock.json and under `webpack` in b/ would list both on a's finding. | Not counted. Copying it would be wrong, but it is not the nearest code. Every graph reader in the engine uses the per-manifest `m.Graph` (reach.go:193-213, reach.go:286-315). | none | Findings are per manifest (finding/build.go:34-50). |
| 9 | Form and order of the entries | `Reach.Via` holds PURLs (finding.go:129-131, reach.go:383-389). `Roots()` sorts by package key (graph.go:103-106, 247-255). | No requirement word decides it. PURL plus key order is the repo idiom. Test risk only: a test that pins names or PURL-string order would pin something the requirement does not state. | none | finding.go:129-131 |
| 10 | Manifest with no graph and a non-direct package | `importReach` gives `ReachNoGraph` when `m.Graph == nil` (reach.go:206-207). | Right: absent ("can't be sure"). Applies to a go.mod with no source on disk, image or installed manifests (never direct, no edges, convert.go:117-126), and to state that has no graph rows (query.go:166-170). | none | reach.go:206-207 |
| 11 | SBOM manifests | CycloneDX packages have no edges and are all direct (convert.go:119-125, scalibr/testdata/golden/cdx.json:20). | Right: never set. | none | — |
| 12 | Pull request mode and the base side | Removed manifests are not evaluated (evaluate.go:40-45). Only base and removed manifests drop their graph (delta.go:362, basecache.go:106). Findings keep only introduced packages (evaluate.go:60, delta.go:377-399). | Right: the head graph decides. | none | — |
| 13 | Continued scan and revived artifacts | The scan file persists roots, test roots, open nodes, the imports flag and edges (scanfile.go:434-467), and `Manifest` reloads them (query.go:54-170). | Right: the graph that evaluate reads is complete. | none | — |
| 14 | Finding id | `computeID` hashes control, subject, package key, path and discriminator only (finding/build.go:50, build.go:109-114). | Right: setting the list after construction keeps the id. | none | — |
| 15 | Test roots | `Roots()` includes test roots (graph.go:63-68). `reach.go:209` joins prod and test. | Right: a test-only direct import is still direct. | none | — |
| 16 | A package that is a root and also has parents (lockfiles) | `graphOf` makes every root `Direct` (convert.go:223-226), so `Subject.Package.Direct` decides it. | Right on the lockfile path: absent. The Go path is row 4. | none | — |
| 17 | Cycles | `PathFrom` and `MayReach` keep a seen set (graph.go:177-209, 219-238). | Right if those helpers are reused. | none | — |

## Result

**GREEN.** Six wrong-by-default decisions, of six different kinds, on different paths: helper choice, caller
guard, direct identity, open-node completeness, absence in the policy input, and policy package-rule findings.
Rows 3, 4 and 5 are the strongest. Rows 2, 6 and 7 are medium confidence: a strong implementer may avoid them, but
copying the nearest code does not.

Wrong-by-default decisions:
- K1, internal/engine/reach.go:193-200 / model/graph.go:138-212 (one-path helpers `Reach.Via`, `PathTo`, `PathFrom`). Separating input: roots `express` and `koa` both pull `qs`. Right `[express, koa]`. Copied: `[express]`.
- K2, internal/engine/reach.go:85-94 (`setReach` guard: reach computed and vulnerability family). Separating input: a malware or cooldown finding on transitive `qs`, or `--reach off`. Right `[express]`. Copied: absent.
- K5, finding/finding.go:266 + scalibr/convert.go:117-126 vs model/graph.go:103 (`Package.Direct` vs graph roots). Separating input: go.mod graph of imports main->A->T. Right `[A]`. `Direct`-only: absent. requirements.txt `urllib3` imported only via `requests`: right absent, roots-only `[requests]`.
- K6, model/graph.go:113-123 / 214-216 (known-edge walk ignores open nodes). Separating input: Go roots `A` (open) and `B`, `B -> T`. Right: absent. Copied: `[B]`.
- K4, internal/policy/input.go:21-32, 54, 62, 130, 160-176 (no `omitempty`, always-present lists, JSON activation). Separating input: rule `!has(finding.introduced_by)` on a direct-dependency finding. Right: match. Copied: no match.
- K3, internal/policy/finalize.go:101-170 (package-rule findings made outside `evaluateManifest`). Separating input: package rule on transitive `qs` in a live scan. Right `[express]`. Engine-only: absent.

Decisions rated none:
- Row 1, where to keep: a `Finding` field set by the engine and stored as JSON (finding.go:36-38, scanfile.go:662-672).
- Row 8, which manifest: the engine reads `m.Graph`, not the cross-manifest `Dependents` (reach.go:193-315; trap at state/query.go:276).
- Row 9, entry form and order: PURLs in key order (finding.go:129-131). Not stated by the requirement, so a test risk only.
- Row 10, no graph means absent (reach.go:206-207).
- Row 11, SBOM: all direct, no edges (convert.go:119-125).
- Row 12, pull request mode and base side: the head graph decides (evaluate.go:40-45, 60).
- Row 13, continued or revived scan: the graph is persisted in full (scanfile.go:434-467, query.go:54-170).
- Row 14, finding id unchanged (build.go:50, 109-114).
- Row 15, test roots are roots (graph.go:63-68).
- Row 16, lockfile root that also has parents is direct (convert.go:223-226).
- Row 17, cycles: the reused helpers keep seen sets (graph.go:177-238).
