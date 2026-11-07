# Construct solution.patch

1. **S1 - Plan from the same obligation/path ledger.** Before code, trace each value
   from public entry through clones/derivations, serialization, adapters, storage,
   observation and cleanup. Include supported modes, fast paths, compiled twins and
   old formats. For each resource and error path, record owner, lifetime, invalidation,
   permitted partial effects and release action. No in-scope path becomes optional
   because it is difficult to run locally.
2. **S2 - Put the change in its owning layer.** Reuse repository abstractions and
   authoritative metadata. Propagate new state through existing types, interfaces and
   callers using language-appropriate compatibility. Prove any default/fallback safe
   for actual callers; do not impose one universal fallback rule. Update related docs
   truthfully, but never make those new docs the hidden tests' sole contract source.
3. **S3 - Implement the full state transition.** Check ordinary, empty, unknown,
   stale, optional and supported legacy inputs against the contract and repository.
   Recheck ownership/generation after asynchronous boundaries where relevant. Review
   each exit after mutation, cancellation, retry, callback and cleanup failure. Ensure
   no promised effect silently disappears; pair rejection output with promised state
   preservation. Break each heuristic/threshold with its smallest supported input.
4. **S4 - Keep the patch focused and native.** Map every hunk to an obligation or
   necessary integration/regression preservation. Use the repo's formatter, configured
   lint/type checks and affected upstream regressions. Remove dead code, inaccurate
   comments, debug/process residue and gratuitous cleanup. Do not pad LOC or omit
   necessary work to meet a size estimate. Preserve meaningful errors and lifetimes.
5. **S5 - Prove the exported artifact.** Apply test.patch then solution.patch to a
   fresh pinned tree; inspect path overlap rather than relying on a dirty checkout.
   Solution changes must not weaken grading tests/configuration. Run both modes and
   the independent discriminators, including alternate valid designs. Every discovered
   in-contract reference fix needs its corresponding fair test; "fixed, no test" is
   not closure. Run gates.md Repair even for a small final solution edit.

## Pre-submit self-check, in priority order

| Gate | Evidence required |
|---|---|
| Auto Review S1-S4 | All atomic promises and paths handled (S1); regressions and repository patterns preserved (S2); each hunk necessary (S3); no generated/process artifacts, unexplained defensive code or inconsistent style (S4). |
| False pass | No in-scope reference behavior is left untested; reference and actual passing designs are independently checked against the contract. Do not weaken this patch to preserve a passer. |
| Solution Quality | Comprehensiveness covers paths/modes/faults/resources, not only happy-path test success. Code quality has recorded native checks and no unresolved concrete defect. |
| Task Quality | Tests assert public semantics, not this implementation's helper names, call counts, incidental formatting or private documentation. |

"Upstream also does it", "rare", "not observed by today's tests", or "another judge
passed it" cannot waive a defect inside the promise. A speculative claim still needs
a grounded failing scenario; record NOT VERIFIED until investigated, not a new feature.
