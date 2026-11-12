---
name: olympus-flow
description: End-to-end Olympus (Shipd) task factory - find a repository and seam (or take the owner's repository), write the description, hidden tests, test.sh, reference solution and Dockerfile from the build checklist, prove them with deterministic gates and platform-replica checks, paste the draft through the Olympus CLI (the owner runs platform checks and rollouts), and shape the task from the platform rollout. Use for every new Olympus task and every platform finding.
---

# Olympus Flow: from a repository to an accepted task

The objective, in order: clean Auto Review (T1-T8, S1-S4 and description), no false passes, full Solution Quality,
fair and complete Task Quality, then the rollout target: exactly one model family in `(0, 25%]`, the others at zero.
Quality is never traded for that distribution. A task is never retired: the flow ends with an accepted task.

Start with [PIPELINE.md](PIPELINE.md) (the stage order, gates, owner actions, paste checkpoints and time boxes).
Copy [ledger-template.md](ledger-template.md) into the task folder and fill it while building: it is the single
contract, path, discriminator, harness and evidence inventory. Planned coverage is not executed proof; an in-scope
omission blocks hand-over.

Read each card right before its stage; the cards are construction instructions, not reviews to run afterwards:
| Stage | Read |
|---|---|
| 0 Find the repository and seam | [hunt.md](hunt.md), [difficulty.md](difficulty.md) (with [profiles.md](profiles.md)), [problem-design.md](problem-design.md), [seam-bank.md](seam-bank.md) |
| 0b-1 Repository init, environment | [dockerfile.md](dockerfile.md), [harness.md](harness.md) |
| 1b Sample, Scope Gate, every paste | [platform.md](platform.md) |
| 2-3 Description and lock | [description.md](description.md) (the only description rulebook), [difficulty.md](difficulty.md) section 3 (spike) |
| 4-5 Tests and reference | [prompts/apply-build-checklist.md](prompts/apply-build-checklist.md), then [build-checklist.md](build-checklist.md), then [tests.md](tests.md), [harness.md](harness.md), [solution.md](solution.md) |
| 6-7 Proof, repair, sweeps, replicas | [gates.md](gates.md), [replicas/](replicas/) |
| 8 Rollout results | [rollout.md](rollout.md), [difficulty.md](difficulty.md) section 5 (reserve), [profiles.md](profiles.md), [platform.md](platform.md), [near-miss-release.md](near-miss-release.md) (owner decision) |
| A trigger with a known answer, or stuck, looping, unsure which fix path | [situations.md](situations.md) |

Fixed rules:
- I paste, the owner runs: platform checks, rollouts, lock and submit are the owner's (platform.md).
- The description is locked at stage 3 for good. The only exit is a change the owner asks for (description.md section
  5b); the builder never proposes one. About 250 site words is guidance; the hard limit is 9 requirement units.
- The build checklist is applied rule by rule through its prompt and gate; a condensed plan never replaces it.
- Keep it simple: one clear step over several clever ones. Add a layer, file, tag or table only when a measured result
  needs it, and remove what no result supports.
- Implement and test every promised path; never invent a hidden requirement to reject a particular solver. Keep real
  upstream regressions and allow valid alternative designs. Agreement with the reference is not correctness.
- No local blind solves unless the owner asks: solver evidence comes from the platform rollout. Every passer of a
  local solve the owner asked for gets its FP audits as soon as grading ends (PIPELINE.md, Confirmation schedule).
- Every long job is its own tracked background command that blocks until it ends (no `&`, no detached shells).
- Codex work runs on GPT Sol 6.1 high; replica checks run on GPT Sol 6 medium (owner 2026-11-13). Briefs use neutral words (`check_codex_brief.sh`).
- Every workflow change found during a task goes into the product's BACKLOG.md in the same reply.

Tools live in [tools/](tools/) and read the machine profile (machine/*.json) for every machine-specific value;
[TOOLS.md](TOOLS.md) lists them. [scripts/certify.py](scripts/certify.py) does byte fingerprints, structural package
checks and strict JUnit reconciliation; it cannot decide fairness, completeness, authorship or platform acceptance.
Accepted package examples (Dockerfile, test.sh) are in [templates/examples/](templates/examples/README.md).
