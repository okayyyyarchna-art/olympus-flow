# Machine profile

Profiles are JSON objects. Select one with `OLYMPUS_MACHINE=/absolute/path/profile.json`
or a name such as `windows-asus` or `mac.example`. A path is relative to the caller's
working directory; names are resolved in the product's `machine/` directory. Without
that variable the loader requires `machine/local.json`. Missing or invalid profiles
fail before a tool starts work. There is no implicit Windows fallback.

| Key | Value |
| --- | --- |
| `os` | `windows`, `macos` or `linux` |
| `shell` | shell executable, normally `bash`; tools require Bash even if the login shell is zsh |
| `python` | Python 3 executable name or absolute executable path |
| `home` | home directory; `~` expands to the current user's home |
| `paths.tasks_root` | challenge workspace root |
| `paths.work_root` | root containing `proof-work/`, `proof-ctx/`, `.round-slots/` and, by default, `solvers/` |
| `paths.seams_root` | seam workspace; hunt clones go under `work/<repo>/` |
| `paths.codex_home` | Codex config and session root; exported as `CODEX_HOME` |
| `paths.claude_bin` | Claude executable name or absolute path |
| `paths.claude2_config_dir` | optional second Claude config root; omit to disable that account |
| `paths.codex_bin` | Codex executable name or absolute path |
| `docker.slots` | positive integer, maximum simultaneous locked Docker commands |
| `docker.native_platform` | `linux/amd64` or `linux/arm64`, used for daily proof runs |
| `docker.final_platform` | must be `linux/amd64`, used for `--final` and `--stability` proof runs |
| `docker.memory_gb` | positive integer describing Docker Desktop's allocation; configure Desktop separately |
| `docker.min_free_gb` | number; free disk (GB) below which dockrun refuses build, buildx, pull, load and import (default 12); `DOCKRUN_MIN_FREE_GB` overrides it for one job |
| `parallel.battery_workers` | positive integer exported for battery launchers |
| `parallel.review_lanes` | positive integer, default maximum concurrent replica rounds |
| `parallel.solvers` | positive integer, default solve count; 1=main Claude, 2=claude2, 3 onward=Codex |
| `parallel.stability_parallel` | boolean; run stability cells concurrently within Docker's slot limit |

All listed fields except `claude2_config_dir` are required. Directory and executable
paths may begin with `~/`, expanded using the profile's `home`. Use absolute paths
or `~/` for directories, and forward slashes on Windows. A Python executable must
already be available to bootstrap the loader; set `OLYMPUS_BOOTSTRAP_PYTHON` when
neither `python3` nor `python` on PATH is suitable.

Optional path keys preserve existing workspace layouts:

| Key | Default |
| --- | --- |
| `paths.solver_root` | `<work_root>/solvers`; each clone is `vp-<task>-<solve>-<run>/work` |
| `paths.shared_root` | `<home>/OSS/shipd`; shared novelty lists |
| `paths.coordinator_root` | `<home>/OSS`; review cwd shared with the coordinator |
| `paths.claude_config_dir` | `<home>/.claude`; main transcript root |
| `paths.memory_dir` | `<claude_config_dir>/projects/<encoded coordinator_root>/memory` |

The memory project key replaces each nonalphanumeric character except `-` with `-`.
Set `memory_dir` explicitly when Claude's existing project key differs in case or
encoding. The Windows profile retains the existing key and home-level solver clones.

Existing per-run controls remain: `DOCKRUN_SLOTS`, `ROUND_SLOTS`, `SOLVERS`,
`SOLVE_TIMEOUT_MIN`, `SOLVE_PATH`, `CLAUDE2_CONFIG_DIR`, model and effort overrides.
`DOCKRUN_SLOTS=1` limits verification to one container. `proof.py --work-root DIR`
redirects its scratch files for an isolated check without changing the profile.
The Docker lock is `skill/tools/lib/.docker.lock`; every cooperating caller must use
the same installed helper. Architecture-specific daily images append `-arm64` to
the cache tag, leaving the Windows and final amd64 image tags unchanged.
