# Build task 1: machine profile + portable tools (Windows behaviour unchanged)

Work only inside C:/Users/ASUS/OSS/olympus-product (a git repo; commit when done, one commit per logical step, author
already configured per commit with `git -c user.name=olympus -c user.email=olympus@local commit`). Do not touch
C:/Users/ASUS/.claude or C:/Users/ASUS/OSS/shipd: the live copies stay as they are.

## Goal
The same workflow runs on this Windows laptop (Git Bash + Docker Desktop on WSL2, 3-5 GB for Docker, 2 container
slots) and on a Mac (48 GB, Apple Silicon, zsh/bash, Docker Desktop, 6-8 slots), chosen by one machine profile file.
With the Windows profile, every tool must behave exactly as today.

## What to build
1. `machine/schema.md` + `machine/windows-asus.json` (today's values) + `machine/mac.example.json`. Fields:
   - `os` (windows|macos|linux), `shell`, `python`, `home`;
   - `paths`: `tasks_root` (C:/Users/ASUS/OSS/claude-code/challenges), `work_root` (proof-work, proof-ctx, solver clones),
     `seams_root`, `codex_home`, `claude_bin`, `claude2_config_dir` (optional), `codex_bin`;
   - `docker`: `slots`, `native_platform` (linux/amd64 on Windows, linux/arm64 on Apple Silicon), `final_platform`
     (always linux/amd64), `memory_gb`;
   - `parallel`: `battery_workers`, `review_lanes`, `solvers`, `stability_parallel` (true|false).
2. `skill/tools/machine.py` (loader: `python machine.py get <dotted.key>` prints a value; importable `load()`), and
   `skill/tools/machine.sh` (sourced by the bash tools; exports the needed values). Profile selection: env
   `OLYMPUS_MACHINE` (path or name), else `machine/local.json`, else fail with a clear message.
3. Refactor every tool under `skill/tools/` and `skill/tools/lib/` to read machine-specific values from the profile
   instead of hard-coded paths: proof.py (dockrun path, proof-work, proof-ctx, platform per run: `native_platform` for
   day-to-day cells, `final_platform` for the stability/final cells), solvers.sh (claude/claude2/codex binaries, clone
   roots, cygpath only when os=windows), stop_solves.sh (stopping a whole process tree: the Windows tree-stop command on windows, a
   process-group stop on macos/linux), solve_watch.py (transcript roots), replica.sh / round.sh / sweep.sh / watch.sh / pull.sh / the repository-search launcher
   (helper paths -> skill/tools/lib), lib/codex_job.sh, lib/claude2_run.sh, lib/replay_patches.sh, lib/dockrun.py
   (slot count from the profile; MSYS/cygpath handling only when os=windows).
4. `install.sh`: copies `skill/` to `~/.claude/skills/olympus-flow/` and `agents/*.md` to `~/.claude/agents/`, writes
   `machine/local.json` from a named profile if missing; `--dry-run` prints what it would do. Never overwrites a file
   without `--force`; prints a diff summary first.
5. `README.md`: what the product is, how to install on a new machine (Windows and macOS), how to write a machine
   profile, and the one rule: rules/playbooks/prompts are shared, the machine layer is per machine.

## Constraints
- With `OLYMPUS_MACHINE=machine/windows-asus.json`, behaviour must equal today's: same commands, same paths, same
  Docker flags. Show this: for each refactored tool, a before/after of the exact command lines it would run (dry run or
  echo mode), or a direct run where cheap.
- Verification to run and report: `bash -n` on every .sh; `python -m py_compile` on every .py; `python
  skill/tools/precheck.py C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/pkg --category
  feature_request` and `tests_lint.py` with the same args as the live copies (output identical); `proof.py ...
  --build-only` against the vet task with the Windows profile (it must reuse the image
  olympus-proof-cc-vet-unused-suppression:4aea4557e1d5 and pass base). Use at most ONE Docker container at a time
  through the lib dockrun.py.
- No personal data in any file (no email addresses, tokens, account names beyond the Windows user folder already in
  the profile). No secrets. Keep comments sparse and in the style of the existing tools.
- Do not change any rule text in FLOW.md or references/ except paths that moved (helpers now in skill/tools/lib).

## Report
Write BUILD-1-report.md in the repo root: what changed per file, the before/after command evidence, verification
outputs, and anything you could not make portable (with the reason).
