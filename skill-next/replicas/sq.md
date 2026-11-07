# Replica: solution quality (site check "solutionQuality")

Read `common.md` first. You judge `solution.patch` (read the full code in `repo/`) against the description.
Your job is to find the defect the site's reviewer will find. The site reports High issues on many packages that
looked complete; a package that "traces cleanly" on its main path is the usual case for those findings. Confirming
the design is not the task; trying to break each promise is.

## Procedure (do every step, in order; the output needs the tables)

### Step 1: promise list
Split the description into promises (one observable outcome each, scope sentences included).

### Step 2: branch inventory of the changed code
For every function the patch adds or changes, list every early return, guard, `if`/`else` branch, `try/except`,
callback registration point and loop exit. For each branch write: the condition, and what happens to the state a
promise talks about when that branch is taken (is the change applied, kept for later, dropped, or left unresolved?).
A branch that silently drops or forgets promised state is a defect candidate.

### Step 2b: exit-after-mutation table
For every early return, `continue`, `break`, raise or guard in the changed functions: list the state the function
has ALREADY changed above that exit in the same call (an entry removed from a tracking map, a counter moved, a flag
set, an item popped). If the exit then drops the promised effect (the change is neither applied, nor kept for later,
nor reported), that is a defect candidate even when the exit "looks like a normal no-op". Example shape: an entry is
removed from pending tracking, then a guard returns because the owner changed, and the accepted change is lost.

### Step 2c: mode x failure-path matrix
Rows: every mode/driver/store/producer variant the description covers (e.g. threaded and plain, each store backend,
compiled twin). Columns: success, refusal/error raised before a handle or future exists, refusal after, timeout,
cancellation. Cell: the function and line that handles it in that mode. A failure handled in one mode but not in a
sibling mode (the handler exists only on one path) is a defect candidate.

### Step 3: break attempts (at least 12, at least 2 per promise)
Build counter-scenarios from these axes and trace each through the real code with file:line:
- lifecycle edge while work is in flight: start, stop, rebalance/revoke/assign, restart, reload, cancel; an answer or
  callback arriving after the edge, ownership or state changing between an action and its acknowledgement;
- failure of each external call: rejected, raised before a handle/future/callback exists, timed out, partial;
- every mode the description covers through its real path: each driver/backend/store, threaded vs plain, compiled
  twins of changed Python;
- concurrency: two users of one resource; a stale completion after a newer one;
- value shapes the promise covers: empty, zero, null, non-text bytes, large (fixed caps), sampled comparisons;
- excluded or "as today" shapes: does base behaviour stay unchanged?
- every backend/driver/engine the repository SHIPS, even ones the description does not name: build a capability row
  per backend (transaction, savepoint, locking read, how values are compared). A read followed by a separate unlocked
  write is a High; on a backend without transactions every check must run before the first write;
- existing code the patch now reaches with new rows or value kinds (a base query or predicate builder used in a new
  way), engine by engine;
- generated or shipped artifacts (bundles, dist, typings, other entry points) rebuilt from the changed source;
- cost on large user input: time and memory of every new loop over user data (no O(n*m) over two user collections);
- user data that looks like internals: special keys (`__proto__`), in-band markers or sentinels, null vs missing.
Each attempt: `{promise, scenario (inputs + steps), trace (file:line chain), result: holds | breaks, why}`.

### Step 4: decide
A broken attempt on a realistic input on a real path is a finding. Write its strongest disproof and check it in code
(common.md rule 3). Drop the finding when any of these holds:
- it needs behaviour the description leaves open, or depends on one of two readings of a sentence;
- the solution does what the repository already does today for the equivalent plain case, and the description asks
  for that ("like it does now", "the same preview it would normally get", "keeps current behaviour");
- the input is outside the setup or scope the description states.
If your disproof holds, the finding is gone; do not override a disproof you verified.

### Step 5: code quality
Repository patterns and layering; configured linters/type checker would pass (Optionals narrowed); bounded work where
the repository is bounded; every new doc/comment claim true through the real caller; no misleading leftover comments
in touched methods; no comment addressed to a grader; every hunk needed.

## Scoring (calibrated on the site's outputs)
- Each criterion: 3 `Fully Met` (no issue), 2 `Partially Met` (one Medium, or one Low in code quality), 1 `Not Met`
  (any High, or two or more Mediums). Seen on the platform for both machines' tasks.
- severity `high` = a stated promise fails on a realistic input on a real path; `medium` = the promise holds but with
  a material weakness (performance against repo norms, a rare but valid input class, a heuristic edge); `low` =
  style.
- verdict `FAIL` if any criterion scores 1; otherwise `PASS`. At most 6 issues, most severe first.

## Output schema (JSON)
```
{"promises": [str],
 "branchInventory": [{"function": str, "branch": str, "effectOnPromisedState": str, "candidate": bool}],
 "exitAfterMutation": [{"function": str, "exit": str, "stateAlreadyChanged": str, "promisedEffectKept": bool}],
 "modeFailureMatrix": [{"mode": str, "success": str, "errorBeforeHandle": str, "errorAfter": str, "timeout": str, "cancel": str}],
 "breakAttempts": [{"promise": str, "scenario": str, "trace": str, "result": "holds|breaks", "why": str}],
 "solution_comprehensiveness": {"score": 1-3, "max_score": 3, "level": str, "reasoning": str},
 "code_quality": {"score": 1-3, "max_score": 3, "level": str, "reasoning": str},
 "issues": [{"criterion": "comprehensiveness|quality", "severity": "high|medium|low", "title": str,
             "detail": str, "evidence": str, "failingCase": str, "disproofTried": str}],
 "verdict": "PASS|FAIL", "summary": str, "overall_feedback": str}
```
`evidence` quotes the description sentence the issue breaks (comprehensiveness) or the repository convention with
path:line (quality).
