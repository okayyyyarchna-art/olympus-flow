---
name: olympus-task-construction
description: Construct an Olympus or Shipd coding-task package from a chosen repository and pinned commit, including its description, hidden tests, test.sh, reference solution, environment and hand-over evidence. Use for building or repairing a task; not for standalone read-only package reviews or repository hunting.
---

# Construct a task from its contract

This is a proposed replacement skill, not an installed workflow. Follow the current
assignment's file boundaries and platform permissions. Old task notes are evidence,
not authority to change a contract, run paid jobs, or modify a frozen package.

The objective, in order, is clean Auto Review (T1-T8, S1-S4 and description), no false
passes, full Solution Quality, and fair, complete Task Quality. The rollout target
is exactly one model family in `(0, 25%]`, with the others at zero. Quality is never
traded for that distribution. First-time success and the distribution remain
**NOT VERIFIED** until the relevant platform results exist.

Start with [PIPELINE.md](PIPELINE.md). Copy [ledger-template.md](ledger-template.md)
into the task's permitted working folder. Fill it as you construct the artifacts;
it is the single contract, path, discriminator, harness and evidence inventory.
Planned coverage is not executed proof. An in-scope omission blocks hand-over.

Read the following card immediately before its stage; the cards are ordered
construction instructions, not a list of reviews to run after writing:

| Stage | Read |
|---|---|
| Environment qualification | [dockerfile.md](dockerfile.md), then [harness.md](harness.md) |
| Contract and human wording | [description.md](description.md) |
| Hidden tests and fixtures | [tests.md](tests.md), [harness.md](harness.md) |
| Reference implementation | [solution.md](solution.md) |
| Proof, every repair, confirmation, hand-over | [gates.md](gates.md) |
| Platform rollout results | [rollout.md](rollout.md) |
| Stuck, looping, or unsure which fix path | [stuck-prompts.md](stuck-prompts.md) |

The build-time [evidence report](../BUILD-3-report.md) maps the rule IDs to current
observations, historical incidents and proposed controls; it is not needed to run
the skill. Do not infer a universal threshold from one accepted example.

Keep the description fixed after lock. Implement and test every promised path;
never invent a hidden requirement to reject a particular solver. Keep real upstream
regressions and allow valid alternative designs. A reference defect and a false
pass can coexist; agreement with the reference is not the definition of correctness.

Use [scripts/certify.py](scripts/certify.py) for byte fingerprints, structural package
checks and strict JUnit reconciliation. It cannot decide fairness, completeness,
authorship, or platform acceptance. Its command contract is in [gates.md](gates.md).
Tools live in [tools/](tools/) and read the machine profile (machine/*.json) for every
machine-specific value; [TOOLS.md](TOOLS.md) lists what exists and what is being built.
Every long job runs as its own tracked background command. [description.md](description.md)
is the description rulebook and its only source of truth (every description under 250
site words).
