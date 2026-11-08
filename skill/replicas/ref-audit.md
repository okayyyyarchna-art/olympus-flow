# Replica: strict audit of the REFERENCE solution (user strategy 2026-11-06)

Read `common.md` first. Input: the description, the test patch, the reference solution patch, and the repository with
both patches applied. Treat the reference exactly as a strict false-pass auditor treats a passing agent run, with no
better solution to compare against: your only yardstick is the description. Question: is there any legal, realistic
input on which the reference breaks a stated promise? Every such input is a gap in the reference AND a missing test.

## Procedure
1. List the description's promises, one observable outcome each, scope sentences included. Quote each.
2. For each promise, list every real path the promise covers in this repository: every entry point (commands, saved
   inputs, file formats), every store, every mode the setup names, every kind of finding or record that reaches the
   code, empty and boundary inputs, re-runs and repeated application. Trace the reference on each path with file:line.
3. For each path, build the smallest realistic input that makes the reference break the promise. Run it when you can
   (a test or a CLI call in the repository); otherwise trace it fully and mark it NOT VERIFIED.
4. For each promise also check the tests: name the wrong implementation that would still pass every current test on
   that promise (multiplicity, ordering, partial paths, first/last, empty, repeated runs).

## A promise is BROKEN only if ALL hold
- the input is legal, in scope and realistic for the users the description speaks for;
- the reference's output contradicts the quoted sentence on its only reading;
- the failing case is concrete and traced (reproduced when possible).
Style, hardening, contrived inputs and behaviour no sentence states are notes, never BROKEN.

## Output schema (JSON)
```
{"promises": [{"promise": str, "paths": [str], "verdict": "HOLDS|BROKEN",
  "failingCase": str | null, "trace": str | null, "reproduced": bool,
  "testToAdd": str | null,
  "wrongImplementationThatPassesTests": str | null}],
 "summary": str}
```
`testToAdd`: for a BROKEN promise, one test on the quoted sentence that the reference fails today and a fixed
reference passes. For a HOLDS promise with a `wrongImplementationThatPassesTests`, the test that fails that wrong
implementation while the reference passes it. Never propose weakening a test.

Independence: do not open other reviewers' reports (eval/sweep-*, eval/claude2/, eval/replica/ other than your own output, eval/codex/, eval/triage-*) before writing your own result.
