---
name: olympus-flow
description: End-to-end Olympus (Shipd) task factory - find a repository and a deep seam sized for the platform's long-solve gate, write the description, hidden tests, test.sh, reference solution and Dockerfile from the build checklist, close every cell by execution, run one platform-replica round, paste the draft through the Olympus CLI (the owner runs platform checks and rollouts), and shape the task from the rollout. Use for every new Olympus task and every platform finding.
---

# Olympus Flow: from a repository to an accepted task

The target is the platform's rollout criteria (platform.md has the exact text, read from the platform on 2026-11-21):
at least 4 completed runs per family; Nova 0 passes; Orion solves at least one run and at most 25% (1 of 4); Vega at
most 25%; the passing Orion runs average at least 256K tokens of sequence length, which means the passing run
compacted once; no run flags the task unfair or broken; cheat rate under 20%; no environment blocker. Every task is
designed for an Orion pass of 300K or more from the seam pick on (problem-design.md section 2): length is designed at
stage 0 and measured at stage 2, never added to a finished task. Quality is never traded for the distribution: each
platform quality check (Task Prompt Quality, Verify Tests, Verify Solution, Verify Flakiness, Reward Hacking, Category
Alignment, Solution Quality, Test Quality) passes on evidence we executed ourselves first. A task is never retired: the
flow ends with an accepted task.

Start with [PIPELINE.md](PIPELINE.md) (the stage order, gates, owner actions, paste checkpoints and time boxes).
Copy [ledger-template.md](ledger-template.md) into the task folder and fill it while building: it is the single
contract, path, discriminator, harness and evidence inventory. Planned coverage is not executed proof; an in-scope
omission blocks hand-over.

Read each card right before its stage; the cards are construction instructions, not reviews to run afterwards:
| Stage | Read |
|---|---|
| 0 Find the repository and seam | [hunt.md](hunt.md), [problem-design.md](problem-design.md) (section 2: the length design; section 7: the test-grid budget), [seam-bank.md](seam-bank.md), [difficulty.md](difficulty.md) section 1, [profiles.md](profiles.md) |
| 0b-1 Repository init, environment | [dockerfile.md](dockerfile.md), [harness.md](harness.md) |
| 1b Sample, Scope Gate, every paste | [platform.md](platform.md) |
| 2-3 Description, length spike, lock | [description.md](description.md) (the only description rulebook), [difficulty.md](difficulty.md) sections 2-3 (the length spike before the lock, the solver runs after it) |
| 4-5 Tests and reference | [prompts/apply-build-checklist.md](prompts/apply-build-checklist.md), then [build-checklist.md](build-checklist.md), then [tests.md](tests.md) with [tq-once.md](tq-once.md), [solution.md](solution.md) with [sq-once.md](sq-once.md), [harness.md](harness.md) |
| 6-7 Executed closure, one replica round | [gates.md](gates.md), [tq-once.md](tq-once.md), [sq-once.md](sq-once.md), [replicas/](replicas/) |
| 8 Rollout results | [rollout.md](rollout.md), [platform.md](platform.md), [difficulty.md](difficulty.md) section 6 (reserve), [profiles.md](profiles.md), [near-miss-release.md](near-miss-release.md) (owner decision) |
| A trigger with a known answer, or stuck, looping, unsure which fix path | [situations.md](situations.md) |

Fixed rules:
- I paste, the owner runs: platform checks, rollouts, lock and submit are the owner's (platform.md). Never paste while
  a platform run or check is active.
- The description is locked at stage 3. The builder never changes it and never proposes a change; a finding on the
  text goes to the owner, who decides (description.md sections 0 and 5b). About 250 site words is guidance; the hard
  limit is 9 requirement units.
- Length before width: a seam is picked for how much code a solver must read and trace before its first correct
  edit, and the stage-2 length spike must reach a mean of 300K (difficulty.md section 2). A short spike means a
  deeper seam, never more rules.
- The build checklist is applied rule by rule through its prompt and gate; a condensed plan never replaces it.
- Closure is executed, not reviewed: every decision point of the reference has a kept wrong version the hidden tests
  catch, every mutant survivor a reason, every promise an executed input, the normal path a timing (tq-once.md,
  sq-once.md, `tools/fastcheck.sh`). Model reviews run once per point of the Review schedule (PIPELINE.md), each lane
  time-boxed; a fix never starts a review round.
- Keep it simple: one clear step over several clever ones. Add a layer, file, tag or table only when a measured result
  needs it, and remove what no result supports.
- Implement and test every promised path; never invent a hidden requirement to reject a particular solver. Keep real
  upstream regressions and allow valid alternative designs. Agreement with the reference is not correctness.
- Solver runs: the stage-2 length spike (2 Codex GPT Sol 6.1 solves at xhigh, the Orion stand-in) and, right after
  the lock, 3 Opus + 3 GPT local solves next to the owner's 2 Orion + 2 Vega platform runs, all in parallel; the build
  never waits for them. Every local passer gets its FP audits as soon as grading ends (PIPELINE.md, Confirmation
  schedule).
- Models: Codex runs GPT Sol 6.1 at medium effort for every job and check; only solver runs and spikes run at xhigh
  (Orion's effort). Claude reviewer agents run Opus 5.5 at medium; Claude solves run Opus 5.5 at high. A second Claude account (`paths.claude2_config_dir`; "claude2" in tool and
  folder names) is optional: it gives an independent reviewer lane and the second Claude solve; without it the kit
  runs those on the main account. Briefs use neutral words (`check_codex_brief.sh`). Every review lane carries a
  40-minute time box.
- Every check status names the version hash it graded; a change says which platform checks it reopens
  (PIPELINE.md, Version bookkeeping).
- Every long job is its own tracked background command that blocks until it ends (no `&`, no detached shells).
- Every workflow change found during a task goes into the product's BACKLOG.md in the same reply.

Tools live in [tools/](tools/) and read the machine profile (machine/*.json) for every machine-specific value;
[TOOLS.md](TOOLS.md) lists them. [scripts/certify.py](scripts/certify.py) does byte fingerprints, structural package
checks and strict JUnit reconciliation; it cannot decide fairness, completeness, authorship or platform acceptance.
Accepted package examples (Dockerfile, test.sh) are in [templates/examples/](templates/examples/README.md).
