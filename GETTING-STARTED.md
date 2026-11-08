# Getting started with Olympus Flow

Olympus Flow is a Claude Code skill that builds a coding task for the Olympus (Shipd) platform: it finds a problem in a
repository, then writes the description, hidden tests, reference solution and Dockerfile, proves them locally, and
pastes the draft to the platform. You stay in charge of everything that spends platform tokens or finalizes the task.

## 1. What you need
- Git, Bash (Git Bash on Windows), Python 3, Docker Desktop, the GitHub CLI.
- Claude Code, signed in.
- Codex CLI, signed in. It runs the sweeps and the platform-replica checks.
- Olympus CLI (`@shipd-ai/olympus-cli`), signed in (`olympus auth status`).
- Disk: at least 12 GB free at all times; a task image can reach about 8 GB.
- Optional: a second Claude account, set as `paths.claude2_config_dir` in the profile. It gives an independent second
  review lane.

## 2. Install
On Windows, first run `git config --global core.autocrlf false`, so repositories you clone for tasks keep Linux line
endings.

Run from a checkout of this repository, in Bash.

Windows:
```bash
cp machine/windows.example.json machine/local.json
```
macOS:
```bash
cp machine/mac.example.json machine/local.json
```
Then edit `machine/local.json` for your paths, Docker memory and number of Docker slots
([field list](machine/schema.md)), and install:
```bash
bash install.sh --dry-run
bash install.sh
```
Check it:
```bash
python skill/tools/machine.py get docker.slots
```
It should print your slot count. Restart Claude Code so it picks up the skill. To upgrade later, use
`bash install.sh --force`.

## 3. Start a task
Open Claude Code in your workspace folder and say one of these:

- You have a repository in mind:
  `Use the olympus-flow skill. Build a new task on <owner/repo>. Start at stage 0 and find the best seam.`
- You have no repository yet:
  `Use the olympus-flow skill. Find me a repository and a seam for a new task.`

Claude reads [PIPELINE.md](skill/PIPELINE.md) and works through the stages below. It stops whenever a step is yours.

## 4. The stages, and who does what
| Stage | Claude does | You do |
|---|---|---|
| 0 Find and qualify | Picks the repository, commit and seam | Confirm the pick; check submission counts on the platform |
| 0b, 1 Environment | Writes the Dockerfile and runner | Build the Dockerfile on the platform |
| 1b Sample | Pastes a basic draft | Run prechecks and the Scope Gate. A reject ends this candidate |
| 2 Define meaning | Lists the requirements and drafts the description | Review the facts |
| 3 Wording and lock | Re-checks your text and gives a lock report | **Write the final description in your own words**, then lock it |
| 4, 5 Tests, reference | Applies the [build checklist](skill/build-checklist.md) rule by rule through [its prompt](skill/prompts/apply-build-checklist.md), then builds both | Read its report of any rule marked not applicable |
| 6, 6a, 6b Proof, audit, v1 paste | Runs the clean-repo proof, audits the reference, pastes v1 | Run a calibration rollout (usually 3 Orion + 3 Vega); the full checks can wait for v2 |
| 7, 7b Confirmation, v2 | Runs the sweep and replica batches, fixes findings, pastes v2 | Re-run the checks it names |
| 8, 8b Rollout, v3 | Reads every run, shapes the tests, pastes v3 | Run the re-eval and the extra runs it names |
| 9, 10 Freeze, submit | Final proof and hand-over | Run final checks, then lock and submit |

Claude pastes drafts but never runs platform checks, rollouts, lock or submit. Local work has a target of 2-4 hours per
task, plus platform waits; expect your first tasks to take longer.

## 5. Prompts for common situations
Say these in the same Claude Code session.

| What happened | Say | Claude follows |
|---|---|---|
| A platform check finished | `Results are in. Pull the platform state and classify every finding.` | [platform.md](skill/platform.md) |
| The rollout finished | `Rollout is done. Pull every run and shape the task.` | [rollout.md](skill/rollout.md) |
| Every run fails | `Every run failed. Follow the near-miss route and name the one blocker.` | [near-miss-release.md](skill/near-miss-release.md), [study prompt](skill/prompts/near-miss-study.md) |
| Too many runs pass | `Too many runs pass. Calibrate down to one passer.` | [calibrate-one-passer.md](skill/prompts/calibrate-one-passer.md) |
| Fair task or environment blocker failed | `Read every run's evalResult and blame flag, then tell me what the judge needs to see.` | [rollout.md](skill/rollout.md) step 1 |
| A false-positive check failed | `Replay the panel's probes on the reference and audit the passer.` | [rollout.md](skill/rollout.md) lever 2 |
| A stage keeps looping | `We are stuck. Read the stuck prompts and name the one blocker and the smallest redesign.` | [situations.md](skill/situations.md), last part |
| The checklist looks skipped | `Run the apply-build-checklist prompt and show me the gate output.` | [apply-build-checklist.md](skill/prompts/apply-build-checklist.md) |
| Something has a known answer | `Check the situations table for this.` | [situations.md](skill/situations.md) |
| You want one description change after the lock | `I want to change the description once. Tell me what it would change first.` | [description.md](skill/description.md) section 5b |

Claude will not propose a description change on its own after the lock. Runs failing a hard point means the task is
working.

## 6. Where everything is
| Path | What it holds |
|---|---|
| [skill/SKILL.md](skill/SKILL.md) | Entry point, and which file to read at each stage |
| [skill/PIPELINE.md](skill/PIPELINE.md) | Every stage, its exit gate, time boxes |
| [skill/description.md](skill/description.md) | Description rulebook and prompts |
| [skill/build-checklist.md](skill/build-checklist.md), [tests.md](skill/tests.md), [solution.md](skill/solution.md), [harness.md](skill/harness.md), [dockerfile.md](skill/dockerfile.md) | How to build each part |
| [skill/gates.md](skill/gates.md), [skill/replicas/](skill/replicas/) | Proof gates and platform-replica checks |
| [skill/prompts/](skill/prompts/), [situations.md](skill/situations.md) | Situation prompts |
| [skill/playbooks/](skill/playbooks/) | Findings catalog and playbooks used by the review agents |
| [skill/templates/](skill/templates/) | Language templates and example packages |
| [skill/tools/](skill/tools/), [TOOLS.md](skill/TOOLS.md) | Scripts |
| [agents/](agents/) | Review agents installed into Claude Code |
| [machine/](machine/) | Machine profiles |
| [BACKLOG.md](BACKLOG.md) | Workflow changes, done and open |

## 7. If something fails at setup
- `machine: ...` error: `machine/local.json` is missing or a field is wrong. See [schema.md](machine/schema.md).
- `dockrun: ... below the ... GB floor`: free disk space, or lower `docker.min_free_gb` in your profile.
- Docker errors: start Docker Desktop and retry.
- The skill is not found: re-run `bash install.sh` and restart Claude Code.
