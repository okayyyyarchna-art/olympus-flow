# Replica: solution quality (site check "solutionQuality")

Read `common.md` first. You judge `solution.patch` (read the full code in `repo/`) against the description.
Your job is to find the defect the site's reviewer will find. The site reports High issues on many packages that
looked complete; a package that "traces cleanly" on its main path is the usual case for those findings. Confirming
the design is not the task; trying to break each promise is.

## Procedure (do every step, in order; the output needs the tables)
The builder's four lists (sq-once.md section 1: promise x path grid, decision rows, rejection ledger, touched-site
ledger) are the cells to enumerate; derive your own from the package, never from the builder's copy.

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

### Step 2d: three sweep tables
Counter pairing: every increment -> its decrement on every path. Interface implementations: every driver or store
implementing a hook the patch relies on honours every parameter. Dynamic-state caches: every cache derived from a set
that can now shrink is rebuilt at a safe point. (faust task 7: 2 High and 1 Medium that three local reviews missed.)

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
- documented limits inside a promise: grep the patch's docs, CHANGELOG and comments for "unless", "except", "may", "not
  supported"; each is a quotable gap unless a sentence excludes it;
- stubs and no-ops reachable from the public API (an abstract default that silently does nothing should raise);
- cleanup that awaits before the error arrives; context-local state when the user works in a helper task; exception
  chains that carry an error the user already handled;
- one-way flags: every flag the patch clears is re-armed on the normal path; process-global flags reset per run;
- a hold or deferral installed before user code shows how it reads needs a release for every excluded shape;
- user data that looks like internals: special keys (`__proto__`), in-band markers or sentinels, null vs missing;
- sibling forms that the tool or format defines inside a universal word (vet task 6: Terraform builds its lock from
  *.tf and *.tf.json, the reference paired *.tf only; npm lockfile versions 1, 2 and 3; a build tool that uses one of
  two files): each form is a promise cell;
- a second pass over the same input (a pre-walk): every side effect of the first pass (diagnostics, counts, recorded
  fields) still happens once;
- shared code paths: run the same input outside the described mode; a changed output is scope growth unless a
  sentence asks for it;
- constants at a real limit (link counts, path lengths): compare with the platform the grader runs (Linux 40, 4096);
- the same logic written twice (a site Design note on vet task 6).
Each attempt: `{promise, scenario (inputs + steps), trace (file:line chain), result: holds | breaks, why}`.
Unit tests that solution.patch adds are not graded; never count them as proof that a promise holds.

### Step 3b: execute (mandatory; 2026-11-19, vet task 6 platform SQ FAIL on an alias path)
The site's SQ runs real inputs: it builds a repository, runs the CLI and reports the wrong output. A static trace is a
hypothesis, not a result.
- Execute at least 6 break attempts in the task image with a real CLI or engine run on a built input, and every attempt
  whose result depends on the filesystem, paths, links, users, line ends or the OS. Record the command and the output.
- For code that handles paths or links, always include: a target reached through a linked ancestor folder (as /tmp
  names /private/tmp on macOS); absolute link texts written through that alias and through the real path; a link
  checked out as a text file; a CRLF checkout; a non-root user.
- Every wrong-output finding an earlier lane reported (Auto Review, TQ, SQ) is executed before it is dropped,
  whatever its severity label.
- An unchanged-input run per input shape of the touched axis (vet task 6: link target kind file, folder, dangling,
  outside, times every file name an extractor checks for) with a change that edits only an unrelated file: the
  expected output is no record with a change; compare with the base tool on the same tree (a regression against
  upstream is blocking at the site every time).
- For every write the reference removes or makes conditional, one executed input per reader of that write in other
  packages (grep Stat, Open, ReadDir, lookups): the site blocked on an extractor that relied on a link text the
  reference stopped writing.
- A PASS needs every executed attempt to hold. An attempt that could not run (no Docker slot, build error) is NOT
  VERIFIED, and so is the verdict: never PASS on static traces alone.

### Step 4: decide
A broken attempt on a realistic input on a real path is a finding. Write its strongest disproof and check it in code
(common.md rule 3). Drop the finding when any of these holds:
- it needs behaviour the description leaves open, or depends on one of two readings of a sentence;
- the solution does what the repository already does today for the equivalent plain case, and the description asks
  for that ("like it does now", "the same preview it would normally get", "keeps current behaviour");
- the input is outside the setup or scope the description states.
If your disproof holds, the finding is gone; do not override a disproof you verified.

### Step 5: the site's non-blocking notes (Design / Clutter / Practice)
The site writes several of these on every package (vet task 6: 9 on fx8, 6 on fx9, 3 and 4 on fx22e), and it repeats
them until they are fixed. Sweep the whole patch for each label:
- Design: a list or rule kept in two places that the repository's AGENTS.md wants in one (a pair table next to the
  extractors' own lists); a component redoing work another layer already does (a control re-diffing entries the
  engine diffed); the base ref opened several times.
- Clutter: code that only tests call; two doc paragraphs for one function; a stored-format version that jumps by more
  than one; narrating or leftover comments; a forwarder that adds nothing; an unreachable fallback.
- Practice: a loop over repeated user data that is quadratic (measure it on a large input and quote the times); a
  value re-parsed on every call; an error dropped without a log; a caller's slice sorted in place.
Also check: configured linters pass; every new doc or comment claim is true through the real caller; no comment
addressed to a grader; every hunk needed.

## Verdict (the site's current format, seen since 2026-11-18)
- Output: "SUMMARY: Found N blocking issues and M non-blocking issues." The site prints no scores.
- Blocking, two kinds seen so far:
  - wrong output: an executed, realistic input breaks a description sentence, vet's behaviour before the change that
    the description keeps, or a documented contract. Report it as Input (the repository you built), Command, Expected
    output, Received, Why (quote the description and name the code path), Suggested change (file:line);
  - cost on the normal path: a measured slowdown on an ordinary input (vet task 6 fx8: a full scan of a 4000-entry
    lockfile 1.34x slower was blocking).
- Non-blocking: the Design / Clutter / Practice notes of Step 5, and a measured cost only on an extreme input (the
  site: "ordinary lockfiles do not feel it").
- verdict `FAIL` if any issue is blocking; any number of notes still passes. Fix the cheap notes anyway.
- The score fields stay for the tooling: a criterion scores 1 with a blocking issue in it, 2 with notes only, 3 with
  none. Severity: blocking = `high`; a note = `low`, or `medium` for a measured cost. At most 8 issues, blocking first.

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
             "blocking": bool, "kind": "wrong-output|normal-path-cost|design|clutter|practice",
             "detail": str, "evidence": str, "failingCase": str, "disproofTried": str, "suggestedChange": str}],
 "verdict": "PASS|FAIL", "summary": str, "overall_feedback": str}
```
`evidence` quotes the description sentence the issue breaks (comprehensiveness) or the repository convention with
path:line (quality). For a wrong output, `failingCase` holds Input, Command, Expected output and Received. `summary`
starts with "Found N blocking issues and M non-blocking issues."
