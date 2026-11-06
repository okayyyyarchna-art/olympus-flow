# flow-status: <task name>

Repo: <owner/repo> @ <tip sha>  |  seam: <one line>  |  category: <bugfix|feature_request>
Platform id: <none yet>  |  started: <YYYY-MM-DD HH:MM>

| Stage | Status | Start | End | Gate result | Artifacts (sha256 first 12) |
|---|---|---|---|---|---|
| S0 Pick | TODO | | | | design.md |
| S0b Dockerfile (user builds on platform) | TODO | | | precheck Dockerfile=, local build-only=, platform build= | Dockerfile |
| S1-A Scan before hand-over: facts list, variant table, draft, word-reach, reading audit x2, DQ count, precheck, checklist | TODO | | | facts=, reach=, audit cx=, audit claude=, DQ count=, checklist= | eval/description_facts.md, eval/reading-audit-*.md |
| S1-B User humanizes the scanned draft | TODO | | | received= | pkg/description.md |
| S1-C Re-check the user's text: behaviour diff, word-reach on changed words, DQ replica, precheck -> LOCK together | TODO | | | diff cases=, changed words=, DQ=, LOCKED desc= | eval/behaviour-diff.md |
| S1b Sample (Scope Gate) | TODO | | | prechecks=, scopeGate= | platform id |
| S1c Behaviour diff on every later rewrite (the one allowed change; shown to user) | TODO | | | changed cases= | eval/behaviour-diff.md |
| S1d 4 solves launched at the description lock | TODO | | | solvers.sh started= | solves/ |
| S2 Reference | TODO | | | sweeps=, lint= | solution.patch |
| S3 Tests + harness | TODO | | | tests=, modes= | test.patch, Dockerfile |
| S4 Deterministic gates | TODO | | | precheck=, proof x2=, uid=, time=, valid=/, wrong=/ | eval/gates.md |
| S5 Sweep 1 (subagent round, all files, no gate) | TODO | | | gaps=, ref-broken=, unfair=, fixed= | eval/sweep-s1-*.md |
| S5b Sweep 2 (fresh scan after fixes, no gate) | TODO | | | gaps=, fixed= | eval/sweep-s2-*.md |
| S5c Solves graded + strict FP audit on every passer (HIGH) + findings closed | TODO | | | passers=/4, deserved=, closed= | eval/replica/fp-audit-*.json |
| S6 Fix batch | TODO | | | findings=, fixed=, contested=, r2= | eval/decisions.md |
| S6b Pre-hand-over safety net: 1 sweep + 2 gate runs + strict FP audit on passers; misses added to sweep-brief | TODO | | | sweep=, g1=, g2=, fp=, brief additions= | eval/replica/summary-g*.md |
| S7 Freeze | TODO | | | wipNN= | wipNN/ |
| S8 Platform P1-P5 | TODO | | | prechecks=, quality=, rollout N/O/V=, FP= | eval/platform/ |

Next action: <one line, always kept current>
Rule: read this table BEFORE every stage change and work the first open row; a cheaper check never replaces a named row (row stays open, tell the user).
