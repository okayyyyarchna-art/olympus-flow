# Getting started with Olympus Flow

Olympus Flow is a Claude Code skill that builds a coding task for the Olympus (Shipd) platform: it finds a deep seam
in a repository, writes the description, hidden tests, reference solution and Dockerfile, proves them by execution,
and pastes the draft to the platform. You stay in charge of everything that spends platform tokens or finalizes the
task.

What the platform accepts today (2026-11-21, its own words are in [skill/platform.md](skill/platform.md)): at least 4
runs per agent family; Nova never solves it; Orion solves it in at least one run and at most 25%; Vega in at most 25%;
Orion's solving runs average at least 256K tokens of sequence length (the passing run compacted once); no run flags
the task unfair or broken; cheat rate under 20%; no environment blocker. Every quality check (Task Prompt Quality,
Verify Tests, Verify Solution, Verify Flakiness, Reward Hacking, Category Alignment, Solution Quality, Test Quality; and the Task Quality criteria of the task record) must pass. Names on the
platform: Test Quality = verifyFairness, Task Prompt Quality = descriptionQuality, Task Quality = taskQuality. The workflow designs for an Orion pass of 300K+ from the seam pick and measures it before the lock.

## 1. What you need
- Git, Bash (Git Bash on Windows), Python 3, Docker Desktop, the GitHub CLI.
- Claude Code, signed in.
- Codex CLI, signed in. It runs the platform-replica checks (GPT Sol 6.1 at medium effort) and the local solves and
  length spikes (GPT Sol 6.1 at xhigh, the platform's Orion stand-in).
- Olympus CLI (`@shipd-ai/olympus-cli`), signed in (`olympus auth status`; the login expires: when it says
  `NoAuthProvider`, log in again, or paste and download the run zips yourself until you do).
- Disk: at least 12 GB free at all times (the profile's `docker.min_free_gb`), 15 GB before a proof or fast-check run; a task image can reach about 8 GB.
- Optional: a second Claude account, set as `paths.claude2_config_dir` in the profile (a separate config folder,
  e.g. `~/.claude-cli`, signed in on its own; the kit's launcher `tools/lib/claude2_run.sh` uses it). It gives an
  independent second review lane and the second Claude solve; without it both run on the main account.

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
(`bash install.sh --profile windows.example` when you skipped the `local.json` copy.)
Check it:
```bash
python skill/tools/machine.py get docker.slots
python -B -m unittest discover -s skill/scripts -p 'test_*.py'
```
The first prints your slot count; the second runs the kit's unit tests. Restart Claude Code so it picks up the skill.
To upgrade later, use `bash install.sh --force`.

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
| 0 Find and qualify | Picks the repository, commit and seam; writes the length design (what a solver must read before its first correct edit, the loop that keeps failing) and the test-grid budget | Confirm the pick; check submission counts on the platform |
| 0b, 1 Environment | Writes the Dockerfile and runner from the platform-accepted examples | Build the Dockerfile on the platform |
| 1b Sample | Pastes a basic draft | Run prechecks and the Scope Gate. A reject ends this candidate |
| 2 Define meaning, measure length | Lists the requirements, drafts the description, runs two local Codex solves of the draft (the length spike): their mean sequence length must reach 300K, else the seam is deepened and the sample re-pasted | Review the facts; decide after two short spikes (runner-up seam or redesign) |
| 3 Wording and lock | Re-checks your text and gives a lock report (with the spike result), pastes the locked text | **Write the final description in your own words** (or say "keep the draft"), then run 2 Orion + 2 Vega on it; Claude starts 3 + 3 local solves at the same time and keeps building |
| 4, 5 Tests, reference | Applies the [build checklist](skill/build-checklist.md) rule by rule through [its prompt](skill/prompts/apply-build-checklist.md); writes the [tq-once](skill/tq-once.md) lists and kept wrong versions before the tests, the [sq-once](skill/sq-once.md) lists before the reference | Read its report of any rule marked not applicable |
| 6, 6a Executed closure, audit | Runs the fast check (cells, two-user replay, kept wrong versions, mutant sweep, timing, lint), then one reference audit | Nothing |
| 7, 7b One replica round, v1 | Runs one round of platform replicas (Test Quality, Solution Quality, description, Auto Review, verify), one fix batch, one verification round; pastes v1 | Run the checks in the order it names (prechecks, Scope Gate, Task Prompt Quality, Verify Tests, Verify Solution, Verify Flakiness, Reward Hacking, Category Alignment, Solution Quality, Test Quality last), the re-eval of the four stage-3 runs, then 2 Orion + 2 Vega + 4 Nova |
| 8, 8b Rollout, v2 | Reads every run (verdict, sequence length, compaction), audits every passer, shapes the tests, pastes v2 when the criteria are not met | Run the re-eval it names; decide on any description change it reports (it never proposes one) |
| 9, 10 Freeze, submit | Final fast check and hand-over with the criteria table | Run final checks and Trial QA, then lock and submit |

Claude pastes drafts but never runs platform checks, rollouts, lock or submit, and never pastes while a platform run
or check is active. Local work has a target of 3-5 hours per task, plus platform waits and the solver runs; expect
your first tasks to take longer. A platform finding is answered by reproducing it (a kept wrong version or an
executed input), fixing the whole class once and re-running the fast check, not by another review round.

## 5. Prompts for common situations
Say these in the same Claude Code session.

| What happened | Say | Claude follows |
|---|---|---|
| A platform check finished | `Results are in. Pull the platform state and classify every finding.` | [platform.md](skill/platform.md) |
| Test Quality or Solution Quality blocked | `Reproduce each item, sweep its class, fix once, fast check, and tell me which checks the fix reopens.` | [tq-once.md](skill/tq-once.md), [sq-once.md](skill/sq-once.md), PIPELINE "Version bookkeeping" |
| The rollout finished | `Rollout is done. Pull every run, give me the criteria table, and shape the task.` | [rollout.md](skill/rollout.md) |
| Every run fails | `Every run failed. Follow the near-miss route and name the one blocker.` | [near-miss-release.md](skill/near-miss-release.md), [study prompt](skill/prompts/near-miss-study.md) |
| Too many runs pass | `Too many runs pass. Calibrate down to one Orion passer.` | [calibrate-one-passer.md](skill/prompts/calibrate-one-passer.md) |
| The passing Orion run is too short | `The pass is under 256K. Give me the options with their costs.` | [difficulty.md](skill/difficulty.md) section 7, [rollout.md](skill/rollout.md) lever 6 |
| Fair task or environment blocker failed | `Read every run's evalResult and blame flag, then tell me what the judge needs to see.` | [rollout.md](skill/rollout.md) step 1 |
| A false-positive check failed | `Replay the panel's probes on the reference and audit the passer with the three columns.` | [rollout.md](skill/rollout.md) lever 2 |
| A stage keeps looping | `We are stuck. Read the stuck prompts and name the one blocker and the smallest redesign.` | [situations.md](skill/situations.md), last part |
| The checklist looks skipped | `Run the apply-build-checklist prompt and show me the gate output.` | [apply-build-checklist.md](skill/prompts/apply-build-checklist.md) |
| Something has a known answer | `Check the situations table for this.` | [situations.md](skill/situations.md) |
| You want one description change after the lock | `I want to change the description once. Tell me what it would change first.` | [description.md](skill/description.md) section 5b |

Claude will not propose a description change on its own after the lock. Runs failing a hard point means the task is
working; a passing run that is too short means the seam was too shallow, which only a description change or more
runs can fix.

## 6. Where everything is
| Path | What it holds |
|---|---|
| [skill/SKILL.md](skill/SKILL.md) | Entry point, and which file to read at each stage |
| [skill/PIPELINE.md](skill/PIPELINE.md) | Every stage, its exit gate, the review schedule, time boxes, the pre-paste gate |
| [skill/hunt.md](skill/hunt.md), [problem-design.md](skill/problem-design.md), [seam-bank.md](skill/seam-bank.md), [difficulty.md](skill/difficulty.md), [profiles.md](skill/profiles.md) | Finding and sizing a seam; the length spike; how the platform agents behave |
| [skill/description.md](skill/description.md) | Description rulebook and prompts |
| [skill/build-checklist.md](skill/build-checklist.md), [tests.md](skill/tests.md), [tq-once.md](skill/tq-once.md), [solution.md](skill/solution.md), [sq-once.md](skill/sq-once.md), [harness.md](skill/harness.md), [dockerfile.md](skill/dockerfile.md) | How to build each part and pass each platform check once |
| [skill/gates.md](skill/gates.md), [skill/replicas/](skill/replicas/) | Proof gates and the platform-replica check prompts |
| [skill/rollout.md](skill/rollout.md), [platform.md](skill/platform.md), [near-miss-release.md](skill/near-miss-release.md) | Platform work, criteria, reading a rollout |
| [skill/prompts/](skill/prompts/), [situations.md](skill/situations.md) | Situation prompts |
| [skill/playbooks/](skill/playbooks/) | Findings catalog and example sections used by the review agents |
| [skill/templates/](skill/templates/) | Language templates and platform-accepted example packages |
| [skill/tools/](skill/tools/), [TOOLS.md](skill/TOOLS.md) | Scripts |
| [agents/](agents/) | Review agents installed into Claude Code |
| [machine/](machine/) | Machine profiles |
| [BACKLOG.md](BACKLOG.md) | Workflow changes, done and open |
| [history/](history/) | Earlier build logs, hand-overs and superseded card versions |

## 7. If something fails at setup
- `machine: ...` error: `machine/local.json` is missing or a field is wrong. See [schema.md](machine/schema.md).
- `dockrun: ... below the ... GB floor`: free disk space, or lower `docker.min_free_gb` in your profile.
- Docker errors: start Docker Desktop and retry.
- The skill is not found: re-run `bash install.sh` and restart Claude Code.
- `olympus` prints `NoAuthProvider`: log in again; Claude cannot read or paste platform state until then.
