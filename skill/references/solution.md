# Reference solution (S2): what platform SQ and AR S1-S4 read

Platform SQ output: comprehensiveness x/3 + code quality x/3, issues with `evidence` = the description sentence the
issue breaks. Every recorded High built a concrete scenario on a real path the hidden tests did not reach. Our
history: every caveat, residual or "the repo does the same" kept inside a promise came back as SQ 1/3-2/3 or AR High.

## 1. Build
- Smallest design that meets every sentence on every IN path, in the repository's own patterns and layering.
- Unsupported OUT modes are refused at start with a clear error (or left byte-for-byte as base), never half-built.
- No code for excluded scope (AR finding on T2/T7).
- Docs/CHANGELOG only where the repo does it for every feature; every doc claim true through the real caller.
- No comments addressed to a grader, no "XXX"/TODO left in touched methods; remove misleading base comments inside
  methods you change (T5 SQ false finding came from one).

## 2. Sweeps (table in eval/gates.md; each row: path, what happens, test that covers it)
Core, every task:
1. Modes and drivers: every implementation the feature enables, through its real path (threaded and plain, every
   store, compiled twins of changed Python).
2. Callers: every caller of each changed function, including startup, shutdown, recovery and standby paths.
3. Lifecycle with work in flight: start, stop, rebalance, restart, reload, cancel; a callback, send or iteration that
   finishes after the edge (SQ Highs: an answer after the partition left; a send failing before its future exists).
4. Failures: each external call rejected, raised before a handle exists, timed out, partial; no partial write left.
5. Values a sentence covers: empty, zero/falsy, null vs missing, non-text bytes, large (no fixed caps).
6. Default path and excluded shapes: plain default case and every OUT/"as today" shape behave as base.

Only if the repo has it:
- Several backends/engines: capability matrix (transaction, savepoint, locking read, comparator exactness); a read
  then an unlocked write is a High.
- Generated or shipped artifacts (dist, bundles, typings, other entry points): rebuild at the pin (byte-identical),
  then with the solution, and include them.
- Concurrent users of one resource (same key, topic, partition, file): two at once.
- Loops over user data: time and memory at 10k+ items (script, not reading); dense inputs terminate (T9 livelock).
- User JSON/objects: special keys (`__proto__`), in-band markers, true vs 1, numbers as text.

## 3. Quality bar
- The repo's CI linters and type checker at the pinned versions pass on touched files (narrow Optionals before use).
- Bounded work where the repo is bounded (initial reads, previews).
- Every hunk mapped to a sentence or plumbing for one (hunk table).
- Run the base suite with the solution: no new failures except the deselected pins, each explained.

## 4. Fixing a platform SQ finding (loop that took orange-orm from repeated FAILs to 3/3 + 3/3)
- Keep `eval/platform-sq-ledger.md`: every platform SQ finding (runs that raised it, severity, real or misread,
  status) and every design the platform accepted. Never redesign an accepted part; re-verify every ledger row on the
  new package before each paste.
- Reproduce first. Misread -> one plain comment at the line it misread, no new code. Not reproducible -> no change.
- Smallest fix (5-15 lines per finding, repo helpers, no new modules). Keep fixes for anything the platform itself
  flagged, even if no sentence names that case.
- Do not refactor code the platform rated Code Quality 3/3; shrink diff context instead (`git diff -U1`).
- Local findings outside every description sentence are Low and get no code (they grew one patch ~300 lines that the
  platform then flagged).
- Keep each guarantee in the layer where the repository makes it exact (swift: storage-layer fixes drew SQ 1/3 about
  5 times, the middleware-only solution got 3/3).
