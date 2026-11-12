# Difficulty retro: questions (same for every task)

Goal: learn what made each task hard (or easy) for the platform's agents, so the workflow can judge a seam BEFORE
building it. Work from evidence (file:line, run id, test name); mark guesses as guesses.

Per task:
1. Hard point(s): which hidden tests did failing runs miss, and why (from the failing runs' test results and, where
   available, trajectories or summaries)? Note whether the missed case was named in the description, implied, or
   discoverable only from the repo.
2. Obvious design vs correct design: what did most agents build first (follow the description's words and the
   repo's nearest pattern), and where exactly did it diverge from the reference?
3. Choke points: list the entry points that had to honour the promise and the code site each goes through. Did one
   shared site cover all of them (an agent editing that one site gets every path right)?
4. Prewritten primitives at the base commit: did the repo already contain a function or pattern that computes the
   hard point (grep the base; cite file:line)? If yes, why was it still hard (or was it not)?
5. Design spread: how many genuinely different designs did the passing / near-passing runs build, and what case
   separated the final passer(s) from the rest during calibration (which test, which design choice)?
6. Source of difficulty: wording (a named corner), a second code path, a neighbour state of an exception,
   lifecycle/ordering/concurrency, multiplicity, an older saved format, an upstream regression, environment, other.
7. Gate check: would this stage-0 gate have rated the seam hard enough, and if not, what check would have?
   (a) choke-point map: one site covers all entry points = red flag; (b) primitive grep: a helper already computes a
   hard point = red flag; (c) obvious-design spike: the obvious design must fail >= 2 fair cases on different paths
   or neighbours; (d) design spread: the repo must leave >= 2 plausible different designs at the seam.

End with: a one-paragraph verdict per task, then a table (task | hard point | source | choke points one/many |
primitive yes/no | obvious design fails? | design spread | gate verdict), then the checks our workflow is missing.
