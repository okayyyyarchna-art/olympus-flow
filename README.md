# Olympus Flow

New here? Start with [GETTING-STARTED.md](GETTING-STARTED.md).

Olympus Flow packages the challenge workflow, review prompts, agents and portable
tools. Rules, playbooks and prompts are shared; the machine layer is per machine.
Keep local settings in `machine/local.json` (gitignored), or select a profile with
`OLYMPUS_MACHINE`.

Install Git, Bash, Python 3, Docker Desktop, GitHub CLI, the Olympus CLI, Claude Code
and Codex first. Authenticate the CLIs separately. The installer copies `skill/` to
`~/.claude/skills/olympus-flow/`, agents to `~/.claude/agents/`, and profiles into the
installed skill. It prints a file diff summary before writing. It refuses to replace
different existing files unless `--force` is present. An existing source
`machine/local.json` is preserved; otherwise the named profile creates it.

On Windows, run in Git Bash from the checkout:

```bash
cp machine/windows.example.json machine/local.json
# Edit machine/local.json for your workspace and installed CLI paths.
bash install.sh --dry-run
bash install.sh
python skill/tools/machine.py get docker.slots
```

Use Docker Desktop's WSL2 backend with about 4 GB allocated. The example profile
uses two Docker slots and amd64 flags. MSYS conversion and Windows process-tree
termination are enabled only for this OS.

On an Apple Silicon Mac, run from Bash or invoke Bash from zsh:

```bash
cp machine/mac.example.json machine/local.json
# Edit machine/local.json for your workspace and installed CLI paths.
bash install.sh --dry-run
bash install.sh
python3 skill/tools/machine.py get docker.native_platform
```

Allocate the profile's Docker memory in Desktop and enable amd64 emulation for final
proofs. Install GNU coreutils for `timeout` (`brew install coreutils`); ensure its
`gnubin` directory is on PATH so the existing timeout flags work. Background solves
have separate process groups on macOS/Linux; `stop_solves.sh` stops those groups.
Configure a second Claude account under `paths.claude2_config_dir`, or omit it and
select solves with `SOLVERS="1 3 4"`.

To create another profile, copy the closest example and adjust its OS, executables,
paths, Docker resources and parallelism. See [the profile schema](machine/schema.md)
for required keys and optional legacy path overrides. `OLYMPUS_MACHINE` accepts a
name or path; absent that, the loader requires `machine/local.json`. Paths passed
through this environment variable should be absolute when launching nested jobs.
The shell loader makes the selected path absolute for its children.

Tools live in `skill/tools/`; internal helpers live in `skill/tools/lib/`. For example:

```bash
export OLYMPUS_MACHINE=windows.example  # or mac.example / an absolute profile path
python skill/tools/proof.py /path/to/base /path/to/pkg --build-only
python skill/tools/proof.py /path/to/base /path/to/pkg --final --stability
DOCKRUN_SLOTS=1 python skill/tools/lib/dockrun.py run --rm --network none IMAGE COMMAND
```

Daily proofs use the native platform. Final and stability invocations use amd64
throughout, with a separate cache tag from arm64 daily images. The tools do not
configure Docker Desktop's memory. `parallel.battery_workers` is exported for
external batteries; this product does not contain a battery launcher.

Use `--force --dry-run` to review an upgrade, then `--force` to apply it. `install.sh
--home /scratch/home` supports an isolated installation check. Installing the product
does not copy or migrate existing task repositories, shared lists, memory or CLI
credentials.
