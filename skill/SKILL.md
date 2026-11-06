---
name: olympus-flow
description: End-to-end local Olympus (Shipd) task factory - pick a seam, design the problem, write description + reference + tests + Dockerfile, verify with deterministic gates and platform-replica checks (Codex, GPT Sol 6.1 medium), paste the draft via the Olympus CLI (the user runs checks and rollouts), then fix platform findings automatically. Use for every new Olympus task and every platform finding.
---

# Olympus flow (local platform replica)

One pass, about 2 hours, at most 3. No user questions except physical help (CLI login, Docker down) and the
description rewrite (S1: I scan a draft fully, the user humanizes it in their own words, I re-check it, we lock together; references/description-playbook.md section 3).
Every step has a pass bar; a failed bar has one prescribed action (see `references/situations.md`).
Built from 16 tasks of history (MAP.md, 2026-11-05) and the platform's own check outputs pulled with the CLI.

## Read order
1. `FLOW.md` - the stages, time boxes, gates. Follow it top to bottom.
2. The reference for the stage you are in (table below). Read each once per task.
3. `references/situations.md` whenever something fails: find the row, do the action, nothing else.

| Stage | Reference |
|---|---|
| S0 pick, S1 design | `references/hunt.md`, `references/problem-design.md`, `references/seam-bank.md` |
| S1 description | `references/description.md` |
| S1b sample (Scope Gate, every task) | `references/platform.md` P1 |
| S2 reference solution | `references/solution.md` |
| S3 tests, harness, test.sh, Dockerfile | `references/tests-harness.md` |
| S0b Dockerfile first | `FLOW.md` S0b row, `templates/accepted/` |
| S4 gates, S5/S5b sweeps, S5c solves + FP audit, S6 fixes, S6b safety net | `references/checks.md`, `replicas/sweep-brief.md` |
| S7-S9 platform | `references/platform.md` |

## Ten rules that override everything (each cost us a task, a rollout or a day)
1. **Quality first.** The reference is the most correct implementation of every stated promise on every real path.
   Never weaken it, never align it to a passer, never keep a known gap inside a promise.
2. **A reproduced finding inside a stated promise is fixed in code or the promise is cut (before lock). Never kept.**
   57 platform findings were visible locally and kept as "residual/Low/risk"; every one came back.
3. **Description is designed once: draft lock at S1, final lock at S4.** Every task then passes the S1b sample
   (Scope Gate) before S2. Between the locks only the two solver alarms may change one sentence (FLOW); after the final
   lock only tests and solution move. A change after the lock costs ~84 tokens (DQ + fresh rollout) and voids every run.
4. **Every sentence is a requirement for the platform**, scope and exclusion sentences included. Each one has a
   discriminating test or is cut.
5. **1-2 hard points, each one deep rule an oracle can check;** difficulty comes from its 3-4 STATED consequences
   where it meets other subsystems, never from hidden corners, unrelated traps or injected-timing races.
6. **Tests assert stated outcomes only**, through the real framework objects and every stated mode's real code path.
7. **test.sh grades with the base-commit tests restored**, exact deselects only for base tests every correct solution
   must break (each named in a comment). Read junit-baseline of every valid design.
8. **Codex replicas decide locally, every check on GPT Sol 6.1 at medium effort** (user rule 2026-11-05). The model is
   not the check: hardness comes from the platform-schema prompts, break-attempt tables, two SQ runs, the verify pass
   and the knowledge catalogs. One round, then a targeted re-run only for the checks a fix touched.
9. **Never act on an unreproduced finding; never test what you contested.** Contest with base evidence.
10. **Never drop or loosen the test of a stated promise to release a passer.** At re-eval only unstated, late-added
    corners may go.

## Running 2-3 sessions in parallel
- One task per session, each in its own task folder; never two sessions on one task folder.
- Only the workflow-design session changes this skill, its tools or the shared catalogs. A task session that finds a
  workflow problem writes it in its flow-status ("workflow issue: ...") and tells the user; it does not edit the skill.
- Shared machine resources are limited by locks, so sessions wait instead of failing: Docker through `dockrun.py`
  (2 containers machine-wide), replica rounds through `round.sh` (2 rounds machine-wide, `ROUND_SLOTS`).
- Memory: task sessions write only task-specific notes; shared rules change only from the design session.
- Platform: each session pastes only its own challenge and runs its own `watch.sh` for that challenge id.

## Directory contract (one task)
```
<challenges>/<task>/
  flow-status.md        # stage table, timestamps, gate results (templates/flow-status.md)
  design.md             # S1 output: seam, inventory, boundary list, variant table, wrong-design list
  pkg/                  # the package being built: description.md test.patch solution.patch Dockerfile
  repo/                 # pinned commit, working tree for development
  base/                 # pristine pinned commit (git worktree), never edited
  variants/             # valid-*.patch and wrong-*.patch for the batteries
  eval/                 # gate logs, replica outputs (eval/replica/*.json), decisions.md
  wipNN/                # frozen copies of pkg/ at each hand-over (never edited after)
```

## Tools
- `tools/precheck.py <pkg>`: deterministic platform prechecks (seconds).
- `tools/tests_lint.py <pkg> <repo>`: deterministic checks for the platform's recurring test findings (seconds).
- `tools/proof.py <base> <pkg> [--stability]`: every Docker proof in one command (build, base/new with and without the
  solution, timing, uid without passwd + `env -i`, optional 6+6 stability), through the Docker slot lock.
- `tools/replica.sh <task-dir> fairness|sq|dq|ar|verify|ref-audit|fp-audit [tag]`: one Codex replica (GPT Sol 6.1 medium).
- `tools/sweep.sh <task-dir> [tag]`: one gap sweep (S5 s1, S5b s2, S6b s3) (claude2 auto-reviewer + sq-judge, 2 GPT ref-audit;
  in-process auto-reviewer + tq-judge lanes started alongside with the Agent tool; brief `replicas/sweep-brief.md`).
- `tools/round.sh <task-dir> g1|g2`: the platform-style gate runs, only in S6b before a hand-over (fairness + sq x2 + dq
  in parallel, then ar, then verify).
- `tools/hunt.sh <repo> ["taken tasks"]`: S0 for a given repo: facts, clone, shared brief, Codex + claude2 hunt lanes.
- `tools/solvers.sh <task-dir>`: too-easy alarm, 4 blind solves (2 Opus: this account + claude2; 2 GPT Sol 6.1 via Codex)
  started at the S1 lock, graded at S4 with `replay_patches.sh`.
  Stop them only with `tools/stop_solves.sh <task-dir>` (kills each solve's whole process tree; stopping
  solvers.sh alone leaves codex/claude running).
- `tools/pull.sh <challenge-id> <out-dir>`: read-only platform state (checks, runs, digest) via the CLI.
- `tools/watch.sh <challenge-id> <task-dir>`: read-only watcher after each paste; exits when the user's runs finish, then S9.
- Shared, in `~/OSS/shipd/tools/`: `replay_patches.sh` (batteries and agent patches), `dockrun.py` (Docker slot
  lock), `codex_job.sh`, `check_codex_brief.sh`.
