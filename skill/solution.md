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

## Hard rules (from vet task 6)

- The site's SQ executes inputs: blocking means a wrong output on an executed input or a slowdown on the normal path.
  Design / Clutter / Practice notes are fixed when free, else declined with a written reason the next round copies.
- List every decision point of the patch with the hidden test that fails when only it changes (tq-once.md). A
  constant at a real limit names its source and matches the platform the grader runs (Linux: 40 links, PATH_MAX 4096).
- Sibling forms that the tool or format defines are inside a universal word: Terraform builds its lock from *.tf and
  *.tf.json; npm lockfiles come in versions 1, 2 and 3; a build tool that uses one of two files.
- A second pass over the same input repeats no side effect of the first (diagnostics, counts, recorded fields).
- Shared code paths: run the same input outside the described mode; change that output only if the description asks
  (scope growth is an SQ risk).
- One logic in one place (vet 6 SQ note: the npm entry canonical form was written twice).
- Unit tests added in solution.patch are not graded; keep them compiling, count only hidden tests as coverage.
- Reference scope = test scope: a behaviour the reference implements that no hidden test checks is tested (if a
  sentence states it) or removed (vet 6: an untested deleted-link reader carried a cache bug and a hang finding).
- Before changing an unexported type, field or signature, grep the upstream `*_test.go` (or the language's test
  files) of the package: a white-box upstream test pins it for every solver (vet 6: the engine package stopped
  compiling). A question about the base is answered with a model of the base, never with head state that the change
  may have edited; add a test where the change edits the very state a fallback would read.
- For every write the solution removes or makes conditional (a file, a map entry, a temp-tree entry), grep its
  readers (Stat, Open, ReadDir, lookups) in every package and keep one executed case per reader (vet 6 platform SQ:
  an extractor in another package relied on a link text the solution stopped writing).
- Before promising a "one-line change" to the owner, grep the repository's own tests at the site and at every
  consumer of the changed value, and run a one-minute targeted check (the new test plus the touched packages' tests).
- Walk [sq-once.md](sq-once.md) before buying Solution Quality; mirror an existing mechanism by consuming its
  decisions, not by re-running its rules on other input (count-, order- and state-dependent rules diverge).
