# Review: the new task-construction skill after the owner's decisions

Review C:/Users/ASUS/OSS/olympus-product/skill-next/ (SKILL.md, PIPELINE.md, description.md, tests.md, harness.md,
solution.md, dockerfile.md, gates.md, rollout.md, TOOLS.md, ledger-template.md, stuck-prompts.md, scripts/, tools/)
and C:/Users/ASUS/OSS/olympus-product/machine/*.json. Do not edit any file except your report.

The owner's decisions it must reflect (check each):
1. Machine-specific limits (container slots, memory, cleanup permission, paths) come only from the machine profile;
   no rule file states a machine limit as universal.
2. No local blind solves. Flow: first draft (description locked, tests and reference built from the construction
   cards) -> the owner runs the platform checks and a 2-2-2 rollout -> meanwhile the builder keeps closing gaps
   (sweeps, replica rounds, repair) without waiting -> rollout results are pulled, every patch joins the permanent
   false-pass corpus, and rollout.md orders the shaping levers.
3. description.md is the description rulebook and the only source of truth for descriptions; every description is
   under 250 site words.
4. Tools are product tools listed in TOOLS.md and read the machine profile.
5. Time boxes per stage; an overrun triggers a progress report, never a skipped gate.
6. The stuck-prompts playbook and the tracked-jobs rule are linked from SKILL.md.
Priority of the platform checks the skill must secure: Auto Review, then false pass, then Solution Quality, then Task
Quality.

Report in C:/Users/ASUS/OSS/olympus-product/REVIEW-4-report.md:
- Each decision: reflected / partly / not, with file:line.
- Contradictions between files (for example a card still describing local solves, a word limit other than 250, a
  machine limit in a rule file, a step that waits for the rollout).
- Steps a builder could not follow as written (missing input, unclear order, a reference to a file that does not
  exist).
- Run `python -B -m unittest discover -s skill-next/scripts -p test_certify.py`, `bash -n` on every .sh and
  `python -m py_compile` on every .py under skill-next/, and report the results.
- A verdict: ready for a dry walk / needs the listed edits first.
Quote file:line for every claim.
