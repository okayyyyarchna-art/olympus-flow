# Go adapter

Two runners exist for a Go package. Copy the first unless the repository cannot be expressed with it:

1. **The bash runner of the accepted Go packages**: `templates/examples/accepted/test.sh.go-oss-rebuild` and
   `templates/examples/in-review/test.sh.go-vet-pr-accuracy` (the most complete one: pinned test files through
   `go test -overlay`, test-only helper packages in the PINNED regex, skipped base tests in BASE_SKIP with the reason
   next to it, acceptance scripts restored from the pinned commit). Plain bash, `go test -v` text on stdout, JUnit
   through go-junit-report. This is the proven route for the platform's verifySolution Harbor oracle: every package
   that passed the oracle used it.
2. **The generated adapter** (`templates/go/test.sh`, rendered by repo_init.py): Python inside a bash heredoc, a
   readable JSON profile, fail-closed JUnit with predeclared IDs. UNPROVEN on the Harbor oracle: cc-pmg-cooldown failed
   verifySolution three times with it (BACKLOG #156, #158, #159; the platform-side cause is unconfirmed). It is the
   fallback for a repository the bash runner cannot express. It now prints the decoded `go test` text and accepts the
   oracle's call shapes, but no package has passed the oracle with it yet.

Both accept `[--output_path <junit.xml>] [--mode] <base|new>` in any order: the mode defaults to base, --output_path is
optional (the adapter then writes the JUnit file to a scratch path and prints `JUnit report: <path>`), and a malformed
or unknown argument exits 2. The adapter also takes `--one ID`, `--list` and `--discover` for repo_check.py.

## Dockerfile

`templates/go/Dockerfile` starts with the bare `FROM public.ecr.aws/d3j8x8q7/olympus-base-go:latest` (the platform
rejects `--platform=`; the local proof passes the platform to docker build itself), keeps `/usr/local/sbin:/usr/sbin:/sbin`
in PATH (the platform's verify image step runs groupadd/useradd), and ends with `chmod -R a+rwX /app` plus the caches
test.sh writes (the Harbor oracle applies solution.patch in /app as uid 1000). Comments: none, except one block right
above each RUN that deviates from the base image, stating why. The template carries that block for the Go reinstall
(the platform AI precheck failed vet's reinstall without it); a real `development_install` that installs a tool needs
its own block, added in pkg/Dockerfile. `python -B tools/precheck.py pkg` checks these rules on a package that holds
only the Dockerfile.

## Rendering

Markers: `toolchain_version`, `go_sha256`, `build_commands`, `development_install` in the Dockerfile; `profile_json`
in test.sh (a readable, indented JSON object; the template no longer reads the older `profile_b64` marker). The
rendered profile uses neutral names: `overlay_paths` (the added test files, overlaid in new mode) and
`base_overlay_paths` (intentional base-mode test/config edits); `restore_paths` and `helpers` name the pinned files.
repo_init's profile.json and settings keep their names `hidden_paths`/`base_hidden_paths`; only the rendered test.sh
carries the overlay names (the base64 form of the older template carries both). `keep_tracked` lists tracked files
of the pinned commit that match a generated-output pattern (*.o, *.a, *.so, *.pyd, *.pyc, build/, dist/,
__pycache__/, .pytest_cache/, node_modules/; pmg's go:embed .o object, #141): the runner copies them and the folders
above them although the pattern would drop them. The JSON sits in a raw triple-double-quoted Python string
(`r"""..."""`): valid JSON never holds three consecutive double quotes (a quote inside a string is always escaped),
so no profile value can end the string early; the earlier `r'''...'''` form broke on a value containing `'''`.
No process word (grading, hidden paths, pristine, solver) may appear in test.sh: `precheck.py pkg` fails on them with
the line, and `precheck.py pkg --test-sh templates/go/test.sh` checks the template itself.

Set `OLYMPUS_MACHINE` to a machine profile. Run:

```
python -B tools/repo_init.py URL FULL_COMMIT TASK --settings choices.json
python -B tools/repo_check.py TASK
```

`choices.json` may contain `{"recipe":"vet-wip02"}` for that exact URL/pin (recipe origin `cc-vet-unused-suppression/wip02`,
safedep/vet at `7574fa1dd338d9543da1c1b33c7c7c4b9633a81f`). Other pins require a verified `go_sha256` and explicit
affected-package selectors. The Go version comes from `toolchain` or `go` in go.mod. The image installs the literal
versioned release URL, checks its checksum, disables toolchain switching, downloads modules, builds production and
enumerates test dependencies without running tests. Pin native development tools with `development_install`; a
repository requiring lint tools not already in the base remains OPEN until those are installed.

## Base mode: what must be in it

Run `python -B tools/tests_lint.py pkg base` before every paste (base = the clean checkout at the pinned commit). It
reads the base-mode packages from test.sh (BASE_PKGS / the `base)` arms of the bash runner, `selectors.base` of the
adapter profile) and the import graph of the base checkout (`go list` when a Go toolchain is on PATH, else a regex
parse of the import lines, said in a NOTE line):

- G1: every package that only `_test.go` files import, used by a base-mode package, must be pinned (PINNED regex plus
  the directory in the restore list for the bash runner; `restore_paths` or `helpers` in the adapter). vet 6 missed
  graphtest (#222), pmg missed cloudpolicytest (#160).
- G2: a changed package and every package that imports it must run in base mode when it has tests, or be left out
  with a reason line in test.sh: `# base skip: <package dir> <reason>` (#197).
- W1: base-mode tests with an upper wall-clock bound (`assert.Less(t, time.Since(...))`, elapsed comparisons,
  sub-second timeouts), a root skip (`os.Geteuid() == 0` then `t.Skip`) or a `user.Current()` lookup are printed as
  skip allowlist candidates, never a failure: measure each on the clean repository, then skip it in base mode with the
  reason (BASE_SKIP in the bash runner, `skip_allowlist` in the adapter). The platform runs base mode 12 times, as
  root and as uid 1000 (#213, #155).

## Adapter details (generated test.sh)

Canonical IDs name top-level Test, Fuzz-seed and Example functions as `ImportPath::Function`. Dynamic subtests
contribute output and failure status to their named top-level parent; they are not independently selectable IDs.
`go test -list .` compiles each selected package before IDs become qualified. Build tags/workspaces and external
services need an explicit adapter choice. There is no automatic skip or exclusion policy.

The runner copies production to unique scratch, discards generated binaries, restores the pinned files from the exact
commit (`restore_paths`), overlays `overlay_paths` in new mode and `base_overlay_paths` in base mode, runs
`go test -json`, prints the decoded text output (so `--- PASS:` / `--- FAIL:` lines reach stdout) and writes the JUnit
report from the events. Missing history fails closed. No runtime downloads are permitted. The prepared Go build cache
(/opt/adapter-gocache) is writable in each container's private layer, separate from the immutable module inputs;
`-count=1` disables test-result caching. Completed named results survive partial runs; missing results become named
errors containing the actual diagnostic. The Vet recipe allows 600 seconds below the recorded 688-second bound. The
author configures nonempty new IDs, selectors and overlays before new-mode execution or the four-cell proof.
`init/test.patch` is exported by repo_check with mode 100755; no generated artifact modifies the clean base.
