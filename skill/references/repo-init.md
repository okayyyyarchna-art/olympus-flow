# Repo initialization (S0-init): make the workflow work for any language and any repo

DRAFT 2026-11-07, for review with the user before it becomes a FLOW stage.

Runs once per task, right after the repo and commit are chosen and before the Dockerfile gate (S0b). It discovers how
this repo is built and tested, writes `<task>/profile.json`, generates the Dockerfile and test.sh from the platform
rules, and proves them with a self-check. Every later tool (precheck, tests_lint, solvers, battery, proof) reads
profile.json instead of assuming a language. A language seen for the first time also gets a template saved under
`templates/<language>/` so the next task in it starts from a proven base.

## The prompt (give it to me or a Codex build lane, fill <...>)
```
Initialize the task workflow for <repo URL> at commit <full sha>, task folder <task dir>, machine profile
<machine profile path>. Work only in <task dir>/base (a clean checkout) and <task dir>/init/. Do not edit base/.

1. Discover, with evidence (file:line for every claim):
   - languages and their share; the build system and package manager; the exact toolchain version the repo pins
     (go.mod, .nvmrc / package.json engines, pyproject requires-python, rust-toolchain, .tool-versions);
   - the test framework(s), how upstream CI runs them (read .github/workflows and Makefile/justfile/scripts), the CI
     linters and formatters and their exact commands;
   - how to list the test ids, run one test id, and produce JUnit XML (pytest --junitxml, go test + go-junit-report,
     vitest/jest junit reporter, cargo nextest --junit; name the reporter and its version);
   - which paths are test code, fixtures and production code (patterns), and which base tests are slow, flaky, need the
     network, or pin internal calls (run the base suite once to find them).
2. Choose the environment: a platform base image that already carries the pinned toolchain (olympus-base-<language>),
   else an explicit, checksum-verified toolchain install from a literal versioned URL. Fetch every dependency at build
   time so the container works fully offline (go mod download, npm ci, pip install -e . with the test extras, cargo
   fetch). Platform rules: no test runner in any RUN line, no implicit toolchain switch, literal versioned URLs, no
   comments, files readable by any uid.
3. Generate test.sh (base and new modes) to the platform contract:
   - base mode runs the base-commit tests that the change could affect; new mode runs only the hidden tests;
   - the base-commit test files are restored inside a scratch copy (or via the language's overlay mechanism), so an
     agent's edits to tests never count;
   - JUnit at --output_path; a build or compile failure is reported as named failing test cases with the compiler
     output; zero selected tests is a failure;
   - it sets its own environment (works as a uid with no passwd entry and an empty env), finishes in < 300 s, exact
     deselects (with a comment) for base tests that fail on a correct design or need the network.
4. Write <task>/profile.json (schema below) and init/report.md (every decision with its evidence).
5. Self-check, each must pass: the image builds once (proof.py --build-only); base mode passes offline; one test id
   runs alone; a forced compile error gives a named failing case; a simulated agent edit that skips a test is undone
   by the restore step; base mode passes as uid 12345 with env -i; the test listing matches the JUnit ids.
6. If <language> has no folder under templates/, save the Dockerfile and test.sh as templates/<language>/ with the
   placeholders marked.
```

## profile.json (what every tool reads)
```json
{
  "repo": "https://github.com/<owner>/<name>", "commit": "<sha>",
  "language": "go | python | typescript | rust | ...", "toolchain": "<exact version>",
  "base_image": "<image>@<digest>", "package_manager": "<npm | pip | go | cargo | ...>",
  "build": "<command>", "lint": ["<CI linter commands>"], "format_check": ["<commands>"],
  "test": {
    "framework": "<pytest | go test | vitest | ...>", "list": "<command that prints test ids>",
    "run_one": "<command with {id}>", "junit": "<command or reporter>", "id_format": "<example id>",
    "restore": "<overlay | copy | ...>", "deselects": ["<id: reason>"]
  },
  "paths": {"test": ["<glob>"], "fixtures": ["<glob>"], "production": ["<glob>"]},
  "limits": {"new_mode_seconds": 300}
}
```

## What changes in the tools (planned, after review)
- precheck.py: language rules come from a table keyed by profile.language (Go toolchain lines, Python editable install,
  Node lockfile, ...); the platform-generic rules stay as they are.
- tests_lint.py and solvers.sh (production-only filter): test/production paths from profile.paths.
- battery: one generic tool that applies each variant, runs test.sh, and compares per-test-id results from the JUnit
  (no task-specific test-name filters).
- proof.py: already generic (Dockerfile + test.sh + JUnit); reads limits from the profile.
- Dockerfile memory notes per repo become templates per language plus profile evidence.

## Smoke test before relying on it
Run the init prompt and the tools on two repos with already-accepted tasks in other languages (one Python, e.g.
faust; one TypeScript or another language when available) and compare the generated Dockerfile/test.sh and the
self-check with the accepted packages. Anything that breaks is fixed in the tools, not patched per task.
