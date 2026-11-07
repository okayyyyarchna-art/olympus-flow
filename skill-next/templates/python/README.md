# Python adapter

Recipe origin: platform-accepted Faust task 12, `cc-faust-topic-start/wip15`,
faust-streaming/faust at `ca53750fdea332cdf5ac7088afc525691556c167`.
`recipe.json` preserves its exact dependency-install block and affected regression
selectors. Accepted status belongs to the original package; see `BUILD-2-report.md`
for the generated adapter's separate local results.

Use the same commands as the Go README, with `{"recipe":"faust-task12-wip15"}`
in explicit settings for the exact repository/pin. This recipe asserts Python
3.12.13, the locally inspected platform-base runtime. The pin's >=3.10 constraint
is not itself an exact interpreter pin. A different base runtime fails the build.

The template markers are `platform`, `toolchain_version`, `dependency_install`,
`development_install`, `build_environment`, `profile_b64`. For a different
repository, supply its own
exact dependency/test/development pins and setup commands; the Faust dependency
recipe is guarded by URL and commit and is never silently reused elsewhere.
Native lint/type tools are discovered from CI; unprovisioned development tools
remain an author decision, not a claim of complete solver tooling.

Pytest collection records canonical `classname::name` IDs and node IDs, including
parametrized cases. `--one` selects the exact collected node ID. Native xunit1 JUnit
is reconciled against the predeclared inventory; reporter/process failure, unknown
or duplicate IDs, inventory drift and unapproved skips fail. Base skip permission
is an exact ID-to-reason map; new skips always fail. No legacy task-specific
deselection is copied: a valid current base regression must remain selected.

Candidate code is copied to writable scratch. Tests, fixtures and grading config
are restored from the pinned commit before collection or setup. Shared manifests
need an ownership review in `restore_paths`. Hidden overlays are explicit files.
`hidden_paths` is new-mode-only; `base_hidden_paths` names intentional base-mode
edits. New feature files are kept out of base-mode compilation/collection.
Stale extensions and generated C twins are removed. Faust's extensions rebuild
from candidate pyx source and their imports must resolve inside candidate scratch.
The clean base checkout and image never receive solver edits.

An initialized repository has no feature contract. `selectors.new`, `expected.new`
and `hidden_paths` remain OPEN until an author provides the feature tests. A base
adapter check does not certify new/base failure, reference proof or platform build.
