# Build task 2: repository initialization for any language

Work only inside C:/Users/ASUS/OSS/olympus-product (git repo with its own identity; commit per logical step) and
scratch folders under C:/Users/ASUS/OSS/olympus-product/.build2/. Do not touch C:/Users/ASUS/.claude or
C:/Users/ASUS/OSS/shipd.

## Contract
The construction cards are the contract: skill-next/harness.md (H1-H6), skill-next/dockerfile.md (E1-E5),
skill-next/PIPELINE.md stages 0-1, skill-next/ledger-template.md (Identity and Repository adapter profile sections).
Every machine-specific value (paths, Docker slots, platform) comes from the machine profile through
skill-next/tools/machine.py / machine.sh; use machine/windows-asus.json here.

## Build
1. `skill-next/tools/repo_init.py <repo-url> <commit> <task-dir>`:
   - clone and check out the pinned commit into <task-dir>/base (clean);
   - discover with file:line evidence: languages, build system and package manager, pinned toolchain (go.mod,
     .nvmrc / package.json engines, pyproject / setup.cfg, rust-toolchain, .tool-versions), test framework(s), how CI
     runs tests, linters and formatters (.github/workflows, Makefile, package.json scripts, tox/nox), how to list test
     ids, run one id and produce JUnit, and the test / fixture / production path patterns;
   - write <task-dir>/profile.json (the ledger's adapter-profile fields) with an `open` list for every value it could
     not decide, each with the reason;
   - generate <task-dir>/init/Dockerfile and <task-dir>/init/test.sh from skill-next/templates/<language>/, filling
     the placeholders from profile.json; dockerfile.md and harness.md are hard constraints (no test runner in a RUN
     line, pinned toolchain, literal versioned URLs, no comments; base/new modes, base-commit tests restored, every
     failure mode a named failing JUnit case, the literal platform environment).
2. `skill-next/tools/repo_check.py <task-dir>`: the H6 self-check, PASS/FAIL per step, exit 1 on any FAIL: image builds
   once (through proof.py --build-only); base mode passes offline; one test id runs alone; a forced production
   compile/import error gives named failing cases with the real diagnostic; a simulated agent edit that skips a test
   is undone by the restore step; base mode passes as uid 12345 with a cleared environment, cwd / and read-only /app;
   the listed ids match the JUnit ids. Containers through the profile's dockrun lock, one at a time.
3. Templates, each with `{{placeholder}}` markers and a README naming the task that proved it:
   - skill-next/templates/go/ from the vet package (proven): C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/wip02/Dockerfile
     and the test.sh inside wip02/test.patch;
   - skill-next/templates/python/ from faust task 12 (platform-accepted):
     C:/Users/ASUS/OSS/shipd/workspace/claude-code/challenges/cc-faust-topic-start/wip15/ (Dockerfile, test.patch with
     its test.sh, repo_url.txt, base_commit.txt);
   - skill-next/templates/typescript/ from the cards only (npm ci / pnpm install --frozen-lockfile at build time, a
     vitest or jest JUnit reporter), marked UNPROVEN until a task passes the platform with it.
4. Unit tests for the discovery logic (fixture repos built in a temp dir, one per language) under skill-next/scripts/,
   runnable offline with `python -B -m unittest discover -s skill-next/scripts -p "test_*.py"`.

## Smoke tests (report each, with evidence)
- Go: repo_init.py on https://github.com/safedep/vet at 7574fa1dd338d9543da1c1b33c7c7c4b9633a81f into
  .build2/vet; compare the generated Dockerfile and test.sh with the vet wip02 files (same build steps, restore and
  JUnit behaviour; list and explain every difference); run repo_check.py (the image
  olympus-proof-cc-vet-unused-suppression:4aea4557e1d5 may be reused only if the generated Dockerfile is
  byte-identical to wip02's; otherwise one build).
- Python: the same for faust task 12 (repo_url.txt + base_commit.txt of wip15) against its accepted Dockerfile and
  test.sh.
Then add a row `0b Repository init` to skill-next/PIPELINE.md pointing to repo_init.py and repo_check.py, and update
skill-next/TOOLS.md. Change nothing else in the cards.

## Report
BUILD-2-report.md in the repo root: what was built, the smoke-test results with evidence, what a model still has to
decide per language (the profile's open list), and anything not done with the reason. No personal data or secrets in
any file; sparse comments in the style of the existing tools.
