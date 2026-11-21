# Co-architect review of skill-next (Claude, 2026-11-07)

Reviewed: skill-next/ at commit d95f773 (Astra GPT-6, max), plus BUILD-3-report.md.

## Keep as written
- Structure: SKILL.md -> PIPELINE.md (stages 0-9) -> one construction card per artifact (D1-D7, T1-T6, H1-H6,
  S1-S5, E1-E5), each ending in a self-check in the owner's priority order (Auto Review, false pass, SQ, TQ).
- gates.md: G0 evidence prerequisites (four cells, exported patches), G1 Auto Review rule by rule (D = deterministic,
  J = judgement), G2 false-pass (variant execution states, two auditors, reproduction), G3 SQ, G4 TQ incl. the eight
  taskQuality fields; the Repair card after every fix with the FP re-check at step 3.
- One ledger template; NOT VERIFIED discipline; contract-relative output pins; capability tables for fakes; the
  literal-environment harness probe; "fixed, no test" is never closure.
- scripts/certify.py: package structure, fingerprints, strict JUnit reconciliation.

## Fixed during review
- certify.py `package` reported every real package as "empty patch" and its own test errored: `git apply` ignores
  paths outside the current subdirectory when run inside a repository. It now runs from a neutral directory
  (commit b9e662f); 10/10 tests pass; the vet wip02 package checks correctly.

## Changes I propose (for the owner's decision)
1. Machine specifics are written as universal rules: "one container at a time", "never docker rm/rmi/prune", the
   `codex_review.sh` route, the dockrun lock path. They belong in the machine profile (Windows: 2 slots, the owner
   granted Docker cleanup on this machine; Mac: 6-8 slots).
2. Solver source: PIPELINE keeps a local blind batch "if authorized". Per the owner's decision, default = no local
   solves; the platform 2-2-2 rollout (after every check passes) supplies the solver patches, every platform patch joins
   the permanent false-pass corpus, and a rollout-shaping card orders the levers: harness repair -> FP audit of passers
   -> unfair assertions -> grounded new test -> more runs -> the owner's single too-easy description change.
3. Word count: D6 says historical cap 400 (<= 390). The platform now reports maxWords=1000 (vet precheck 206/1000).
   Read the current limit from the precheck; keep "short" as guidance only.
4. Tools: the draft leaves the repository adapter, battery/corpus runner, scheduler and review launcher as
   "task-specific". They should be product tools, carried from the current skill or built next: repo_init (build task
   2), a generic corpus runner (variant states + JUnit ids), proof.py (four cells + stability, exists), precheck.py
   (platform precheck replica, exists), the evidence manifest / FP barrier.
5. Time boxes per stage (owner target 2-4 h): add numbers; an overrun triggers a progress report, never a skipped gate.
6. Link the stuck-prompts playbook and the tracked-jobs rule from SKILL.md (operational rules the draft only implies).

## Next steps
1. Owner decides 1-6.
2. Apply the accepted changes in skill-next/ (me, reviewed by Codex).
3. Dry walk: run the new skill's cards against an already-accepted task (faust task 12) and today's vet package, and
   note every card step that does not fit.
4. Install from the product repo when the owner approves.
