# Setting up olympus-flow on a new machine (Windows Git Bash, macOS or Linux)

Everything the workflow uses, installed once. After this, `bash ~/OSS/shipd/dedup-sync.sh pull` keeps the skill,
tools, playbooks and memory the same on every machine.

## 1. Programs (each must work from the shell)
| Program | Check | Why |
|---|---|---|
| git, bash, python3 (or python) | `git --version; python3 --version` | all tools |
| GitHub CLI, logged in | `gh auth status` | hunt (stars, issues, PRs), novelty searches |
| Docker, running | `docker version` (Apple silicon: Rosetta/amd64 emulation on) | proof.py, batteries (images are linux/amd64) |
| Node + npm | `npm --version` | the Olympus CLI |
| Olympus CLI, logged in | `npm install -g @shipd-ai/olympus-cli; olympus auth login; olympus auth status` | paste, pull results, watcher |
| Codex CLI, logged in, GPT Sol 6.1 | `codex exec --skip-git-repo-check -m gpt-6.1-sol "Reply with exactly: OK"` | every replica check, hunt lane, 2 solvers |
| Claude Code (`claude`) | `claude --version` | in-process lanes, 1 Opus solver |
| claude2 = a second Claude account | config dir `~/.claude-cli` (or set `CLAUDE2_CONFIG_DIR`); `CLAUDE_CONFIG_DIR=~/.claude-cli claude --version` | second-account lanes, 1 Opus solver, load split |

## 2. Workspace and sync (private repo okayyyyarchna-art/Olympus-Kit)
```
mkdir -p ~/OSS && cd ~/OSS
git clone <Olympus-Kit url> shipd-tmp && mkdir -p shipd && cp shipd-tmp/dedup-sync.sh shipd/ && rm -rf shipd-tmp
bash ~/OSS/shipd/dedup-sync.sh init <Olympus-Kit url>   # one time; makes ~/OSS/shipd track the shared files
bash ~/OSS/shipd/dedup-sync.sh pull                     # loads skills (olympus-flow), agents, memory, tools, playbooks
```
The pull installs `~/.claude/skills/olympus-flow/` and the memory notes. Afterwards pull every few prompts; push only
when the user asks (`bash ~/OSS/shipd/dedup-sync.sh push`).
A machine with its own fresh memory sets `export OLYMPUS_SYNC_MEMORY=0` (shell profile): it then syncs skills, tools
and playbooks but never sends or loads memory.

## 3. Shared tools the skill calls (synced under ~/OSS/shipd/tools)
`codex_job.sh` (Codex jobs; `CODEX_MODEL`, `CODEX_ONE_OFF_EFFORT`), `check_codex_brief.sh` (neutral wording),
`neutralize_for_codex.py`, `claude2_run.sh` (Windows) / `claude2_run_mac.sh` (macOS), `dockrun.py` (Docker slot
lock, Windows and macOS), `replay_patches.sh` (batteries, solver grading, agent-patch replays).

## 4. Self-check (2 minutes)
```
cd ~/.claude/skills/olympus-flow/tools
python3 precheck.py --help >/dev/null 2>&1 || true        # loads
bash -n round.sh replica.sh solvers.sh hunt.sh watch.sh pull.sh
python3 ~/OSS/shipd/tools/dockrun.py version --format '{{.Server.Version}}'   # Docker through the lock
olympus problems mine | head -3                           # CLI login
```

## 5. Evidence behind the rules (not needed to run, read when a rule is questioned)
`~/OSS/shipd/playbooks/olympus-flow-evidence/`: MAP.md (16-task history), the platform's own check outputs (digests),
failures, prechecks, agent-run notes. `CALIBRATION.md` in this skill records how the local checks matched the
platform.
