# Re-check list: the finding types the platform has raised (walk before every paste)

From the owner's hand-over of 2026-11-20 (history/HANDOVER-new-machine-20261120.md, section 10) and vet task 6. Walk it
on the final tests and solution before every paste, with an executed proof per row; a row without a run is open. The
fast check (`tools/fastcheck.sh`) covers the rows marked F; the rest are read or run by hand and recorded in the ledger.

## Tests
| # | Finding type | Check | Tool |
|---|---|---|---|
| T1 | A wrong solution passes every test | every kept wrong version fails exactly its named leaves, every control passes | F (`tools/wrong_versions.py`) |
| T2 | An exact value where several are right; a pinned unstated count | no leaf failed by every strong stored run; the fairness sentence over every assertion (tq-once.md section 3) | replay of the stored patches |
| T3 | A state no real run builds; a call into internals | list every unexported name and hand-built state the hidden tests use: none | read |
| T4 | A check that is empty when run as root | hidden tests as root: every leaf fails on the clean repository and passes with the solution | F (root baseline) |
| T5 | Skips | zero skipped cases in every JUnit file | F |
| T6 | A real clock or goroutine deadline decides a result | grep the hidden tests for sleeps, timers and deadlines; only `go test -timeout`-style caps remain | read |
| T7 | Operating-system limits assumed | each OS-dependent case behind an OS check | read |
| T8 | Several scenarios without a name in the message; not table-driven where the file's siblings are | read every new test | read |
| T9 | Comments quoting the task text; copied helpers | read every new test; a comment names the sentence or the repository line, never the task | read |
| T10 | A leaf that passes on the clean repository | new mode on the clean repository: every leaf fails | F |
| T11 | Hidden tests stop building after an agent's changes | every stored agent patch through `test.sh new`: 0 build errors (a test file that names a type only the reference adds) | replay |
| T12 | Flaky result | repeated runs across three user ids (root, uid 1000, a uid with no passwd entry); a failing case re-run alone 3 times | F |
| T13 | Verify Solution set rules; /app not writable | the two-user run and the five-set check | F (`tools/junit_sets.py`) |
| T14 | A test-only helper or an importing package left out of base mode | `tools/tests_lint.py` G1 and G2 clean | tests_lint |
| T15 | An upstream wall-clock test fails Verify Flakiness on its own | every W1 candidate measured 30 times on the clean repository; those over their bound on the skip allowlist with the reason | tests_lint W1 |

## Solution
| # | Finding type | Check | Tool |
|---|---|---|---|
| S1 | Wrong output on an input the reviewer builds | the unchanged-input run over every shape of the touched axis; every executed break attempt of sq-once.md holds | run |
| S2 | Regression against upstream at a touched site | the same trees through the clean tool, side by side; every reader of a removed write has an executed case | run |
| S3 | Slower normal path | best-of-3 timing at 1x and 2x input, alone on the slot; no superlinear growth, under about 5% added | run |
| S4 | One rule computed in two places | read the diff | read |
| S5 | Dead code, a repeated literal, a narrating comment, a version that jumps by more than one | read the diff; the repository's linters | lint |
| S6 | An error dropped, a caller's data changed in place | read the diff | read |
| S7 | Behaviour no sentence asks for, or behaviour no hidden test checks | each behaviour maps to a sentence and to a test; the rest is removed | read |
| S8 | A mirrored mechanism with its own budget, order or limit | the new code consumes the existing mechanism's decisions, or a test changes the rule's input and one its order | run |

## Description (only when the text changed, owner-decided)
| # | Finding type | Check |
|---|---|---|
| D1 | A non-ASCII character | a one-line check on the exact bytes |
| D2 | More than 9 requirement units, or a text that reads as separate asks | the unit count, ours and the DQ replica's |
| D3 | A scope word read by its nearest noun leaves a required state unnamed | the word-reach table per sentence |
