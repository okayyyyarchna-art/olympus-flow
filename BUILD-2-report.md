Verdict: PARTIAL LOCAL QUALIFICATION - Go passes 17 checks; Python final replay blocked by lost image; 59 offline tests pass; TypeScript UNPROVEN.

Built pinned repository discovery, adapter profiles with file:line evidence and explicit open decisions,
self-contained language templates, and the locked offline adapter self-check. Only the deliverables below
and `.build2/` scratch were edited. The instructed Docker wrapper also creates its shared
`skill-next/tools/lib/.docker.lock` runtime file. No protected package folder, shared playbook, or external
installation was edited. No push or `docker rm`, `rmi`, or prune command was run.

## Created or changed files

```
BUILD-2-report.md
skill-next/PIPELINE.md
skill-next/TOOLS.md
skill-next/tools/repo_init.py
skill-next/tools/repo_check.py
skill-next/scripts/test_repo_init.py
skill-next/templates/go/Dockerfile
skill-next/templates/go/test.sh
skill-next/templates/go/README.md
skill-next/templates/go/recipe.json
skill-next/templates/python/Dockerfile
skill-next/templates/python/test.sh
skill-next/templates/python/README.md
skill-next/templates/python/recipe.json
skill-next/templates/typescript/Dockerfile
skill-next/templates/typescript/test.sh
skill-next/templates/typescript/README.md
```

## Validation

| Check | Result and evidence |
|---|---|
| Offline unit suite | PASS, 59 tests; `.build2/unit-suite.log` and `unit-suite-exit.json`. `GIT_CEILING_DIRECTORIES` points at `.build2` so certify's Git parser really runs outside a repository. |
| Go init, exact requested Vet pin | Generated `.build2/vet/profile.json` and `init/`; explicit `vet-wip02` recipe settings are in `.build2/vet-settings.json`. |
| Go self-check | PASS, 17/17, exit 0; 92 baseline tests passed. `.build2/vet/check/results.json`, `offline-base.xml`, `build-proof.log`, and per-probe XML/log/timing records. |
| Python init, exact Faust task-12 URL/pin | Generated `.build2/faust/profile.json` and `init/`; explicit `faust-task12-wip15` recipe settings are in `.build2/faust-settings.json`. |
| Python self-check | Final replay exit 1: ten required checks plus the runner hash guard passed; six remaining checks are uncertified after Docker exit 125 and image disappearance. Baseline: 958 passed, 3 exact skips. Earlier 16-probe PASS is historical (`.build2/faust-first-all-pass.json`). Current results: `.build2/faust/check/results.json`; image availability: `.build2/image-availability.json`. |
| TypeScript | UNPROVEN, as requested. Vitest draft only; Jest is discovered but needs its own qualified execution adapter. |
| Other languages | Rust fixture discovery passes; execution remains explicitly OPEN. No Rust execution template was requested. |

Run with `OLYMPUS_MACHINE=windows-asus`. `repo_check.py` uses `proof.py --build-only`, turns off that
tool's automatic builder prune, and routes every Docker operation through the existing lock with one slot.
For build-only, the checker reconstructs the exported `test.patch` with `git apply` in a fresh pinned
clone, invokes it in the literal H4 container, and passes its XML/exit/IDs to `proof.inspect_junit`.
This avoids proof's image-to-Windows recursive permission pass; that pass failed before execution at
`internal/plugins/controls/malware` (`.build2/vet-windows-preparation-failure.log`). The offline unit
suite also proves patch reconstruction preserves runner bytes and leaves the pinned base clean.
Exact base-skip IDs are checked against successful native discovery; parametrized IDs need not
appear in the provisional static inventory. The fresh-profile unit regression covers this case.
The provisional new-ID file is unused by build-only; it never certifies feature tests. Native base IDs are
qualified after the image builds and before base execution. Generated runner patches preserve mode 100755.
The checker records every required step, including NOT EXECUTED failures after a blocking error.
A seventeenth check verifies the final runner SHA-256 still matches the executed probes.
Python report-loss probes delete, truncate or corrupt native XML after real execution. Go's native
format is stdout JSON; its report-loss probes drop or corrupt the normalized result boundary after
real execution. Injected runner files and raw logs are retained, so these simulations are distinguishable
from the real production/test-build failures and the deliberately timed-out subprocess.

Development attempts are retained: `.build2/vet-first-build-failure.log` records the checksum-placeholder
rendering bug, now fixed and covered by a fresh-clone rendering test. `.build2/vet-build-timeout.log`
records the earlier 660-second image-build watchdog. Its tracked Docker client was stopped after the
wrapper exited; supervision now stops the entire tracked process tree, with a real timeout unit test.
Image builds now have a separate 3600-second watchdog. A later cold 600-second enumeration timeout
is retained as `.build2/vet-600-discovery-timeout.log`; subsequent checks reuse that exact image's
retained build cache. The cache is validated against its image identity and native test results
are never cached. These failed attempts are not successful smoke proof.

One Go replay passed nine required checks plus the final runner hash guard, then host disk exhaustion
prevented writing the next receipt. The exact failure is retained in `.build2/vet-disk-full-results.json`
and `vet-disk-full-console.log`; unexecuted checks remained FAIL. Only obsolete owned working clones
were removed (paths recorded in `reclaimed-scratch-files.txt`). The earlier large Python error XML was
losslessly gzipped, with its original SHA-256 in `compressed-receipts.json`. The stopped Docker engine
was restarted, and files inside two obsolete task-created Go cache volumes were cleared after validating
their Go-cache signatures; volume objects were retained. `cache-file-reclaim.log` records this action.
Own check directories now enable NTFS compression for subsequent scratch files. No resource-removal
or prune command was used. The final replays below determine the result, not that interrupted attempt.

## Final execution identities

Go: `olympus-proof:3f59c4ca59b35547a36c203e17c936d3c0c9471546ad0ffe74e8e79ffdb07874`; last inspected image ID `sha256:59b61c77fd85248a09a966b9d6efcbe6ff839ce1fed61df580c6d3de28828485`. Final runner SHA-256: `c43c6769f3d6d9c29e079e0d2d94b29456d996d3c5d0617560a5c87186a8c041`.

Discovery 169.5s; offline baseline 213.8s; explicit H4 repeat 143.9s. Complete timings are in `.build2/final-evidence.json`.

Python: `olympus-proof:e6d882563842d3d5a51511d33eef1fe5d2026ea0f3449b352641e00b4ce9c584`; last inspected image ID `sha256:acde272d24ffa01b8e2c15b14bf421999d959723f64ff3d4c53dc3d4fee048aa`. Final runner SHA-256: `68e26db1e5719d5b410782a64c60e1c4dae6c4c31b073212282fbcaaadef87bc`.

Discovery 53.6s; offline baseline 57.3s; explicit H4 repeat 62.8s. Complete timings are in `.build2/final-evidence.json`.

The Go final replay uses the retained cache for that exact image. The separately retained cold
baseline passed all 92 IDs without a shared volume. Negative production/test compilation probes
require changed source to fail; Go test-result caching is disabled. Python positive executions
rebuild and verify the compiled twins. Final runner hash guards match the executed probes.

The fresh Python run proved native-ID qualification, baseline, one-ID/list behavior, source
authority, literal H4, test-build failure and zero selection. Its watchdog container then returned
Docker exit 125 with unexpected EOF and no marker. A focused retry could not locate the image;
both its tag and recorded IDs were absent. No image-removal/prune command was issued by this task.
The cause of the image disappearance is unverified. Read-only recovery found 22 of its 27 referenced
OCI blobs; five were unavailable (`.build2/oci-recovery-missing.json`). No recovery archive was loaded.
The already-built image must be restored before completing watchdog/report/converter/collection replay.
No second image build was run,
preserving the brief's one-build restriction. These outstanding checks are not reported PASS.

## Differences from the examples

Complete byte comparisons and unified diffs are retained as `.build2/{vet,faust}-comparison.json` and
`.build2/{vet,faust}-{Dockerfile,test.sh}.diff`. Neither generated Dockerfile is byte-identical to its
example, so the accepted Vet image tag was not reused as proof.

* Both Dockerfiles add the profile's literal platform, omit comments and record resolved base digests
  through proof. No test runner is called during image construction. Go preserves the release URL,
  checksum, module download, production build and test-dependency enumeration; it explicitly fixes
  PATH/toolchain/workspace. Matching `-trimpath`/`-buildvcs=false` flags allow content-based build-cache
  reuse across unique scratch paths. Its prepared build cache is writable in each container's private
  layer; module inputs remain uid-readable. The checker alone shares a separate image-seeded cache
  volume for the exact image identity, including retries, retaining its metadata and disabling
  test-result caching with `-count=1`. Permission scans modify only unreadable source/dependency
  paths, rather than making candidate source world-writable. Python preserves the
  accepted direct dependency-install block and SCM version; it additionally asserts Python 3.12.13 and
  prepares uid-readable access. The recipes provision CI's Go linter with published checksums, and
  Python's pinned black/isort/flake8/mypy versions. Other repositories supply `development_install`.
* Both runners use strict argument parsing, absolute resolution of relative output paths, a literal
  cleared outer environment, owned writable HOME/cache/temp/source, offline dependencies and a watchdog.
  Mode and output path are explicit (except list/discovery); the old Go default mode, `--mode` and
  hyphenated output aliases are removed. Python additionally accepts `--output_path=...`. Repeated
  output options and abbreviated options fail. They fail closed when the pristine commit is missing.
  Upstream tests, helpers, fixtures and grading
  configuration are restored before setup, then mode-specific author overlays are applied. New feature
  files stay out of base mode; intentional base edits have a separate `base_hidden_paths` list. Candidate
  production is retained; generated binaries/import shadows are removed. Restore settings cannot name
  inventoried production or escape the repository.
* Go replaces text scraping/go-junit-report with native JSON events and a strict stdlib JUnit writer.
  IDs name stable top-level Test/Fuzz-seed/Example functions; dynamic subtests contribute to their parent.
  The Vet recipe retains the candidate CLI/internal production build and the four accepted base packages.
  Python collects canonical/node IDs with a small plugin, rebuilds Cython twins and verifies imports load
  from candidate scratch. It uses the accepted base selectors and retains the previously deselected
  seek-to-committed regression when running pristine base source.
* Reporting predeclares and reconciles every ID, retains process status and completed cases, and names
  missing affected IDs with real diagnostics for setup/build/collection/timeout/report failures. New skips
  fail; base skips need exact reasons. Missing/empty/malformed XML, duplicates, unexpected/missing IDs and
  converter failure fail. Converter fallback independently escapes named errors. List and exact-one-ID
  interfaces and per-command phase exit records are added. The original task-specific feature tests
  are not copied into a new task;
  new selectors/IDs/overlays remain OPEN until its author supplies them.

The Python baseline is 958 passed plus three pre-existing upstream skips, all retained by exact ID:
`TestProducer::test__new_producer__using_settings[expected_args0]` is inapplicable to pinned aiokafka 0.14;
the two `Test_VEP_no_recent_response`/`Test_VEP_no_response_since_start::test_timed_out` cases already
carry SOURCE BUG skips at the pin. `recipe.json` records source lines and active replacement checks.
No new regression was deselected.

Additional development failures are retained: initial Go discovery exhausted the `/tmp` tmpfs while
copying the warmed cache, and Windows blocked two quarantined fixtures. A disk-backed copy then left too
little watchdog time. The final design uses `/var/tmp` scratch, reads grading files directly from Git
instead of copying their mutable Windows paths, and uses a writable container-local Go cache. Python's
first import probe selected an unused examples package; selection based on imported source and a regression
test corrected it. A later cold Go discovery exhausted the 420-second watchdog without a compiler
diagnostic (`.build2/vet-420-discovery-timeout.log`). The Vet recipe now allows 600 seconds, below the
recorded 688-second bound; the outer local watchdog is 660 seconds. An obsolete in-memory Go checker
was stopped after seven cold checks passed because its injection anchor predated the final runner.
Its receipt is `.build2/vet-cold-partial.json`; it is partial proof, not a full PASS. These attempts are
not counted as passing evidence. No image/volume removal or prune command was issued by this builder.

The readable scratch-file inventory is `.build2/file-manifest.txt`. It includes generated profiles,
runner/patch exports, retained clones, proof metadata, per-probe logs/XML/timings, comparison artifacts
and development-attempt receipts. Removed clone paths are recorded separately; unreadable remnants
from older Docker-written preparations appear in `file-manifest-unreadable.json`. These scratch
artifacts are intentionally uncommitted.
Concurrent edits to other construction cards were preserved and are outside this task.

## Remaining author decisions

The complete, per-value reasons are in each generated profile's `open` array. For Go, choose affected
packages, build tags/workspace and helper/config ownership; verify release checksums for other toolchains
and install or verify declared lint/format tools. For Python, choose an exact runtime, resolve complete
test/development dependency pins and plugins, review shared manifests/compiled twins, and justify any
exact optional-backend skips. The guarded Faust recipe supplies its accepted direct pins, not a generic
lockfile for other projects. For TypeScript, verify the proposed platform base, exact Node/package-manager
and locked reporter versions, native ID/name filtering, exports/compiled output and multi-project behavior.

The current Go open fields are `helpers.shared`, `selectors.base`, `selectors.new`,
`expected.new`, `restore`, and `platform`. Python additionally retains `dependencies`,
`frameworks`, and `locks`, without `helpers.shared`. The recipe chooses the example base selectors;
the author still reviews their suitability for the new task. Native qualification establishes the
observed baseline IDs, while complete dependency/plugin compatibility and immutable indirect pins
remain distinct decisions. `.build2/final-evidence.json` preserves each full reason verbatim.

Every language still needs the feature contract, new tests/IDs/selectors/overlays, task-specific four-cell
and stability proof, current platform criteria and the human's platform image-build result. Local base
adapter qualification never marks the full package or platform build verified.
