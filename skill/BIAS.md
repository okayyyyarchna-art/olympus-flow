# Bias check: read at every stage exit, before any paste, and when tempted to "save time"

Shortcuts always cost more later (vet task 2: a condensed plan instead of the ledger tables -> a v1 with 4 reference
breaks, 1 unfair test, platform SQ FAIL, a full fix batch). At every stage exit write one line in the task's
eval/decisions.md: `bias check <stage>: B1..B12 walked; <any item that applied and what I did>`.

## Our priorities (decided with the owner; they decide every conflict)
1. Quality over pass rate: no known gap inside a stated promise at a paste; widest literal reading in the reference.
2. Platform check order: Auto Review -> false pass -> Solution Quality -> Task Quality.
3. The description is locked at stage 3; only the extreme-case final change (description.md 5b) can touch it.
4. Never retire a task; the flow ends with an accepted task.
5. The workflow's named steps are not optional, and none is replaced by a cheaper one.
6. Keep it simple: every step earns its place, but a step the workflow names is never "simplified away".
7. I paste, the owner runs platform checks and rollouts; every paste is verified by download and notified.

## Biases I have shown (each with the check that stops it)
| ID | Bias (where it cost us) | Check before moving on |
|---|---|---|
| B1 | Substituting a condensed note for a named artifact (vet2: build-plan.md instead of the ledger Paths x change kinds and Discriminators tables) | Every table the stage card names is filled; no "Fill" left in the ledger sections of this stage |
| B2 | Feeding a check the wrong input (vet2: DQ replica on the sample sketch, not the planned reference) | Name the exact inputs of every check and confirm they are the current, planned files |
| B3 | Stating a fact I did not read (vet2: "EnrichCounts uses the same rule" was false; sibling paths listed from memory) | Every claim about code has a file:line I opened in this stage |
| B4 | One instance per requirement (vet2: one package, one ecosystem in continuation; platform "single point") | Each obligation has at least two identities / two ecosystems / both orders where they can differ |
| B5 | Testing the happy entry point only (vet2: PR "adds" tested, PR "removes"/"moves"/"upgrades" not) | Each entry point is crossed with every change kind and lifecycle edge in the Paths table |
| B6 | A test that rejects a valid design (vet2: continuation stop tied to enrich progress) | For each test, name one valid alternative design and confirm the test setup does not depend on it |
| B7 | Speed over gate order because the owner is away or a checkpoint is near | The gate order of PIPELINE.md is followed even when nobody is watching; a missed step is reported, not hidden |
| B8 | Trusting a tool I have not run end to end (vet2: six proof.py defects surfaced one run at a time) | A tool version new to this machine gets a smoke run on a known-good package first |
| B9 | Asking the owner for what the workflow already decides, or making the owner ask for reports the workflow defines (lock report, triage table) | Deliver the defined report unasked; ask only real decisions |
| B10 | Keeping a known gap as "residual" or "parity with base" | A finding inside a stated promise is fixed or cited to the excluding sentence; never kept silently |
| B11 | Claiming done without the evidence (old PASS, summary labels) | Every "done/pass" names the current artifact hash and the log line |
| B12 | Fixing findings one at a time as they arrive | Collect all lanes, triage once (accept/reject with reason), fix the class in one batch |

New bias found in a task: add a row here in the same reply (BACKLOG rule), with where it cost us.
