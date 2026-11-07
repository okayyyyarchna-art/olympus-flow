# Go adapter

Recipe origin: `cc-vet-unused-suppression/wip02`, safedep/vet at
`7574fa1dd338d9543da1c1b33c7c7c4b9633a81f`. The supplied Dockerfile and
`test.patch`'s executable runner are the proven examples. This generated adapter
has separate local qualification evidence in `BUILD-2-report.md`; platform reuse
does not transfer from the example to changed bytes.

Set `OLYMPUS_MACHINE` to a machine profile. Run:

```
python -B skill-next/tools/repo_init.py URL FULL_COMMIT TASK --settings choices.json
python -B skill-next/tools/repo_check.py TASK
```

`choices.json` may contain `{"recipe":"vet-wip02"}` for that exact URL/pin.
Other pins require a verified `go_sha256` and explicit affected-package selectors.
Go version comes from `toolchain` or `go` in go.mod. The image installs the literal
versioned release URL, checks its checksum, disables toolchain switching, downloads
modules, builds production and enumerates test dependencies without running tests.
Pin native development tools with `development_install`; a repository requiring
lint tools not already in the base remains OPEN until those are installed.

Canonical IDs are `ImportPath::TestFunction`. Dynamic subtests contribute output
and failure status to their named top-level parent; they are not independently
selectable IDs. `go test -list .` successfully compiles each selected package before
IDs become qualified. Build tags/workspaces and external services need an explicit
adapter choice. There is no automatic skip or exclusion policy.

The runner copies production to unique scratch, discards generated binaries,
restores grading files from the exact commit, and overlays only `hidden_paths`.
Missing history fails closed. No runtime downloads are permitted. Immutable Go
build cache is copied to a writable per-run cache. Completed named results survive
partial runs; missing results become named errors containing the actual diagnostic.

Every template marker is filled from the profile: `platform`, `toolchain_version`,
`go_sha256`, `build_commands`, `development_install`, `profile_b64`. The last marker
embeds only the runner's adapter fields. Unresolved build inputs block repo_check.
Review restore ownership: production files must never enter `restore_paths`.

Generated `init/test.sh` supports mode before/after `--output_path`, `--one ID`,
`--list` and `--discover`. The latter compiles/lists upstream tests without running
them. The author must configure nonempty new IDs, selectors and hidden overlays
before new-mode execution or four-cell package proof. `init/test.patch` is exported
by repo_check with mode 100755; no generated artifact modifies the clean base.
