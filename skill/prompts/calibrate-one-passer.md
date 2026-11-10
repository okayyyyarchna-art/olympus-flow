# Calibrate a too-easy task down to exactly one passer

Use when a rollout has too many deserved passes. Target: exactly one model family solves, at 25% or less of its runs,
the other two at 0%, with Fair task, No environment blockers, Solvable, No cheating, No false positives and
Auto Review 3/3/3 all green, on the EXISTING rollout through a re-eval.

Do not use it when every run fails (use near-miss-release.md). "vet2:" lines are evidence from one task, not guarantees.

Terms. Cell: one test scenario graded on every stored run. Keeper: the one run meant to stay passing. Contested test: a
test that depends on a reading the description does not settle.

## Limits (do not reopen these)
- The description is locked. Do not propose, draft or list a change; one happens only if the owner asks
  (description.md section 5b). Never name a hard requirement on your own. If runs fail it, the task is working.
- No Dockerfile change: it loses the re-eval.
- Keep a platform-approved reference. Change it only under Lever F, and re-run Solution Quality if you do.
- Everything a test, name or comment says must be true. Nothing may mislead a judge about what the test does.
- Lanes: in-process plus claude2. Codex only if the owner names it, or both lanes found nothing.
- Pull platform checks and runs before every paste and every status claim. Nothing is pasted without the owner's go.
- Never retire the task. If stuck, name the one blocker and the smallest redesign.
- Report measured numbers only. Mark anything not run as NOT VERIFIED.

## Step 1: Measure before changing anything
1. Pull every run with `tools/pull.sh <id> <dir> --runs`: folders by run id (labels repeat across batches), verdict,
   label, batch, evalResult reasoning, output.json with the agentBlameUnfair flag, the production patch.
2. Grade every stored run against the current tests locally, cell by cell. Local replay predicted the pass pattern
   exactly on both re-evals of vet2; trust it for who passes, not for how a judge labels a failure.
3. Record who misses what, and whether it is per family (all 4 runs) or per run. A cell every run fails leaves no
   passer. A per-family miss removes a family. Only a per-run miss inside one family can leave one passer.

## Step 2: Search for differences. Run ALL levers: which one works differs per task.
Every candidate becomes a cell run on base, reference and every passer.
Order for speed: first I and J (one reading of each passer; they found both vet3 splits), then C, F and H in
parallel lanes, then A, B, D, E, G. Time-box each grid lever: vet3's 424-cell grid and 13 line rows found no split.
Every lever runs on the passers AND the near-passers (runs failing one or two tests): a near-passer's failure must be
an agent miss, never a task blame (vet3: three runs failing only a hand-built helper were blamed on the task).

Lever I. Dispatch key. For the reference and each passer, write the one line that decides WHICH items the fix applies
to: an interface check, a flag, a registered name, a type switch, a path prefix. Where two keys differ, build the input
that one key selects and the other does not, with real components if the repo has one; a stand-in only under Step 5.7.
  vet3: reference keyed on Whole, Vega #3 on Local, both Orions on the SourceEnricher interface; an enricher registered
  as the code analysis without UseSource split both Orions off.

Lever J. Side effects against a fresh run. For each passer, list what else its approach redoes or touches: re-reading
unchanged inputs, re-saving kept data, re-ordering output, repeating a warning. Then compare the result of the feature's
path (continued, cached, incremental) with a fresh run of the same input, when a sentence promises the same outcome. The
fresh run is the oracle, so no internal detail is asserted.
  vet3: three Vega runs re-extracted unchanged manifests and doubled their warnings; "a continued scan reports an
  unchanged manifest as a new scan does" split them off.

Lever A. Differential grid: take one sentence, list the independent axes of its inputs (for each input source: its
possible states before and after the change, order, count), generate the combinations, and tabulate every build against
the reference.
  vet2: 72 scenarios x 9 builds, 12 disagreements; split all Orion runs off.
  vet3: 424 cells, no split (the passers differ in mechanism, not in reachable inputs: use Levers I and J).

Lever B. Stated-path catalogue. For each sentence, one cell on every other path under the same rule. Find these in the
repo: each entry point and mode, each store or cache, stop-and-resume, retries, ordering and paging, each format or
backend, two of a kind, empty input, and combinations of two modes.
  vet2: 26 cells; removed Orion and Vega, no split inside Nova.

Lever C. Line-by-line, run against run, NOT one common test. Read each production hunk of all passers side by side:
every condition, SQL clause, ordering, map key, early return, status value, merge rule. Each line where two runs differ
is a row and gets an input and a measured cell. Different assertions remove different runs until one remains. Split by
code area across lanes, then one extra lane on only the surviving family against itself. Every batch: when a new
batch brings a passer, that passer goes through Lever C against the current keeper before the keeper is chosen.
  vet2: 3 lanes; 4 different Nova mechanisms, identical on every reachable path.
  vet3: the lane ran before batch 2 arrived, so the new Orion passer was compared only later.

Lever D. Scenarios proposed by Test Quality and Auto Review judges, including their wrong-design variants. Measure each
on the stored runs; many are real coverage and some split families.
  vet2: "continued scan on the upgraded-from version" failed all Orion on the most literal sentence.
  vet3: Codex Auto Review's "a finished malware lookup is not checked" became a kept-value test; the platform's
  graph-warning Medium became a stricter replacement test. Neither split, both closed findings before the paste.

Lever E. Platform and FP panel notes: what they probed, and every coverage suggestion. Check whether the suggested
example reaches the bug before adding it.
  vet2: the suggested Go replacement never becomes a package, so a Gemfile PATH case was used instead.

Lever F. Reference bugs. Search with the reference ALLOWED to fail: where does it break a sentence on a real scan while
some runs are right? If a split exists, fix the reference and add the test. If all runs share the bug, there is no
split; leave it and record it.
  vet2: npm, pnpm, bun and poetry local packages are looked up on the reference and all 8 runs: no split.
  vet3: a second stop before the analysis was a reference gap (one call moved); a partial registry batch was a breach
  every run shares: recorded, no split.

Lever G. Reverse split: a cell the keeper passes and others fail on the opposite expected result, if a sentence supports it.

Lever H. The agents' own tests. Rebuild each run's edited test file from its patch (feature tests only, renamed with
the run id) and run them on every passer and the reference. Filter the results through Step 3.
  turso: found the split after a random battery of 1,400 views showed none.
  vet3: no usable split.

## Step 3: Filter every candidate
Keep a cell only if ALL hold:
- a sentence literally covers the input (quote it);
- the reference passes (after a Lever F fix, if any);
- base fails, or the cell is merged into a step that fails on base;
- some runs fail and the keeper passes;
- it is observable through the real command or the public run path.

Rejected on vet2, check these first: an API no production code calls; a setting no shipped component uses; request
counts when the value is requested at all; raw spelling a stub matches exactly; old scan or cache formats; report
metadata no sentence names; a case where all runs behave alike (removed manifest).

## Step 4: Assemble and pick the keeper
1. First remove whole families with plainly stated cells.
2. Then split inside the last family with the fewest assertions.
3. Re-grade all stored runs after each new cell. Stop at exactly one passer.
4. If only a contested test can split the last family, it may stay, but only with Step 5.
5. The keeper must match the reference on every measured cell.
6. Every new cell also runs the valid-design variants (build-checklist section 4, with the production-builder config
   field): a cell that fails a valid design is a fairness bug, not a split (vet3: valid design V21 added for this).

## Step 5: Write tests a judge can follow
1. A contested assertion ships as a family: neighbours showing the rule in both directions and the no-change cases, in
   one script.
2. A comment directly above each discriminating assertion quotes the description sentence and states this case only. It
   prints in the failure log. Do not state a general rule the reference does not follow.
3. Test names say what is checked.
4. Do not use framing words the description lacks. Reword any other comment that reads as a contradicting rule.
5. Only-failure check: from the replay, list runs whose ONLY failures are contested tests. Give each a failure on a
   plainly stated case where one honestly exists, and warn the owner about the rest.
6. Prefer a user-visible outcome over a call count or an order, and never make a count fail a valid reuse the keeper
   does (vet3: an output-order test was judged blamed on 5 of 5 runs; the same runs failing a doubled warning, 2 of 5).
7. A stand-in fake keeps every interface of the real plugin except the one under test; when it cannot, its comment cites
   the visible precedent by file:line (vet3: two evaluators split on one stand-in; the one that found the visible
   precedent called it fair).
8. Helpers take the configuration from the production builder, so a run that adds a wired field is judged on its
   behaviour (build-checklist section 5; vet3: three runs blamed on the task over a hand-built helper).

  vet2: re-eval 1 had 5 runs blamed on the task. Re-eval 2 had 0, with the same behaviour under test.

## Step 6: Review the exact bytes and estimate labels
1. Verify: base fails all new cases, reference passes, wrong-design variants caught, all stored runs replayed.
2. Verdict judges BEFORE the proof: on every failing run, with the platform's labels and the strongest case against.
   A test judged blamed is changed now, while no proof is running (vet3: two replacements each cancelled a running
   proof). Before accepting a blamed test as a risk, look for a comment-only fix first: cite the visible precedent or
   the code path that makes the case fair; the result of no run changes.
3. Clean-repo proof and precheck.
4. Test Quality, Solution Quality if the reference changed, Auto Review. Fix every High.
5. Do not change the reference to close a Medium unless Lever F applies.
   vet2: a query change closed one Medium and opened a High, because the keeper then differed from the reference.
6. Local judges are a warning, not a stop.

## Step 7: Paste and run in this order
Pull state, paste test.patch only, confirm the download matches, start the watcher. Owner runs: Test Quality, re-eval,
then Auto Review (before the re-eval it only reports no eligible runs), then the FP panel.

## Step 8: Read each label before changing anything
| Result | Check first | Action |
|---|---|---|
| Environment blocker | agentBlameUnfair on each run | On vet2 only blamed runs counted; Git, lint and cache notes did not. Remove the blame; leave the Dockerfile |
| Test broken | Does the test fail for a harness reason? | Fix the harness, or the assertion if it pins unstated behaviour |
| Ambiguous, Undocumented, Test mismatch | The judge's reasoning per run | Step 5; add a plainly stated failure for those runs; do not touch the description |
| Same code, opposite labels | Judge noise | Strengthen the test's explanation; do not redesign |
| FP panel flags the keeper | Replay its probes on the reference | Probes the reference also fails are dropped; otherwise fix with a fair test |

## Options that failed on vet2 (try only if the facts differ)
- Removing the contested test: leaves the family at 4/4.
- A clause in the description naming the case: that is what made the task too easy, and it is never ours to propose.
- Changing the reference to follow one rule: opened a High.
- Dockerfile changes for the environment notes: lose the re-eval and were not needed.
