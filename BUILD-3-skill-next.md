# Build task 3: a fresh task-construction skill (co-architect assignment)

You and Claude are the two architects of a product: a pipeline that builds coding tasks for an evaluation platform.
The owner watches. Build the NEW skill from the evidence below; it replaces the current one when approved. Write only
inside C:/Users/ASUS/OSS/olympus-product/skill-next/ (create it) plus BUILD-3-report.md in the repo root; commit with
`git -c user.name=olympus -c user.email=olympus@local commit`. Do not edit anything else.

## The product goal
Every task the pipeline builds (a task description, hidden tests with test.sh, a reference solution, a Dockerfile)
passes the platform's checks the first time, in this priority order:
1. Auto Review (tests rules T1-T8, solution rules S1-S4, description band),
2. the false-pass review (no solver run may pass the hidden tests while missing a stated requirement; one false pass
   fails the whole task),
3. Solution Quality (comprehensiveness, code quality),
4. Task Quality (per-test fairness, requirement coverage),
and lands in the rollout target (one model family in (0, 25%] of runs, the others at 0) while every tested outcome
stays derivable from the description plus the repository.

## The design principle
Correctness must come from HOW each artifact is written, not from repeated review runs. Model review runs are slow and
their results vary run to run. Turn everything the evidence teaches into written construction rules, templates,
deterministic checks and ordered steps that work for ANY repository and ANY language. Keep a model run only where a
written rule cannot decide (name each such point and say why). The owner's planned review stays as a final
confirmation: three review sweeps of two lanes, two independent false-pass auditors per passing run, two
platform-style replica rounds; your design should make those confirm, not discover.

## Evidence (the dataset; read all of it)
- The current workflow and everything learned this week: C:/Users/ASUS/.claude/skills/olympus-flow/ (FLOW.md,
  references/*.md, especially description-playbook.md, build-checklist.md, repo-init.md, stuck-prompts.md; replicas/;
  tools/; templates/).
- Today's task, end to end: C:/Users/ASUS/OSS/claude-code/challenges/cc-vet-unused-suppression/ (flow-status.md,
  wip01/ and wip02/ packages, eval/ including workflow-changes.md, triage-*.md, replica/, battery-*.log,
  variants-final.log, description-*.md, reading-audit-*.md, and the studies checklist-cx.md, checklist-review-astra.md,
  desc-recipe-astra.md, workflow-smooth-astra.md, workflow-smooth-claude.md, check-optimize-cx.md,
  checklist-evidence-platform.md, checklist-evidence-accepted.md, desc-history-digest.md, desc-audit-A.md,
  desc-audit-B.md), and C:/Users/ASUS/OSS/claude-code/challenges/shadow-2lane/.
- Past tasks: C:/Users/ASUS/OSS/shipd/workspace/claude-code/challenges/ (wipNN packages, eval/) and the lesson index
  C:/Users/ASUS/.claude/projects/c--Users-asus-OSS/memory/MEMORY.md with the files it lists. Treat old rules as
  evidence of what happened, not as binding: this is a fresh design.
- The platform, READ-ONLY through the Olympus CLI (`olympus problems mine --json`, `problems view <id> --json`,
  `checks view <id> --json`, `runs show ...`; run `--help` first). Never create, edit, submit, run checks or start
  rollouts. Weight tasks submitted on or after 2026-10-16 most; agents improve with every submission.

## What to build in skill-next/
1. SKILL.md: what the skill does, when it is used, the stage order, and where each instruction file applies.
2. PIPELINE.md: the stages from a chosen repository to a handed-over package, each with inputs, outputs, its gate
   (deterministic where possible), and the points where the human acts (writes the final description words, builds
   the Dockerfile on the platform, runs the platform checks and rollouts).
3. One instruction file per artifact, each written as ordered construction steps plus a pre-submit self-check whose
   items map to the platform rules in the priority order above:
   - description.md (writing the task description),
   - tests.md (hidden tests and fixtures),
   - harness.md (test.sh, base and new modes, restoring upstream tests, JUnit, offline and unknown-uid runs),
   - solution.md (the reference solution),
   - dockerfile.md (building the environment for any language).
4. gates.md: for Auto Review, false-pass, Solution Quality and Task Quality in that order, the exact self-check the
   pipeline runs before hand-over, what is deterministic, what needs a model run, and how a failure is repaired
   (including the step after every fix that re-checks false-pass risk).
5. The artifact the builder fills while writing (one ledger template) and any templates/scripts that turn rules into
   deterministic checks (describe them precisely; implement small ones if cheap).
6. BUILD-3-report.md: the evidence behind each rule (file:line or check text), what you dropped from the current
   workflow and why, what you kept, the model-run points that remain and why, and open questions for the owner.
Keep every file short enough to be read before its stage. Language- and repository-independent. Quote evidence;
mark anything unverified as NOT VERIFIED.
