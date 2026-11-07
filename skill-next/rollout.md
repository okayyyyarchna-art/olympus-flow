# Shaping the task from platform rollout results

The owner runs a 2-2-2 rollout (two runs per model family) once every platform check
passes. Until then the builder keeps closing gaps; nothing waits for the rollout.

1. Pull every run read-only (problem view, runs show/artifact). Record per run: family,
   eligibility (complete, clean, current version), per-test result vector, patch.
2. Add every patch to the permanent false-pass corpus (replayed after every later fix).
3. Classify each run: deserved pass, false pass, near miss (fails only a few related
   assertions), environment/harness failure, genuine miss.
4. Levers in priority order; use the next only when the one before cannot apply:
   1. Harness or environment defect (a valid design failed for a reason outside the
      contract): repair the harness and re-classify.
   2. Every passing run: two independent false-pass auditors; reproduce each
      NOT_DESERVED in a container; a confirmed false pass gets the smallest fair test
      (gates.md Repair).
   3. A near miss that fails an assertion pinning unstated behaviour: fix the unfair
      assertion (never remove the promise).
   4. Too easy with deserved passes: add a grounded discriminator for an unnamed variant
      of a stated rule (tests.md T2).
   5. Too hard with valid near misses: more runs on unchanged files before any change.
   6. Too easy after levers 1-4: the owner's single allowed description change (remove
      the wording that gave the path), with a fresh rollout.
5. Every change goes through gates.md Repair; target: one family in (0, 25%], the
   others at 0, with no false pass.
