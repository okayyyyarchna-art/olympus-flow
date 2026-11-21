# Seam search: {REPO} ({LANG}), read-only

Goal: find 5-8 candidate tasks (bug fixes or feature requests) in the repository at {CLONE} (default branch
{BRANCH}, commit {COMMIT}). Each candidate is a change an engineer would make in this repository, which we can later
build with a reference solution and offline tests. Do not edit the repository; write only your report.

## Already taken (exclude these and anything that overlaps them)
{EXCLUDE}

## What makes a good candidate
1. One clear feature or bug in stateful or rule-evaluating code. The change crosses 3-30 production files along the
   value's real path (files a correct change must touch, never padding), about 15-20 of them changed.
2. 1-2 hard points (two moderate ones preferred over one extreme): each is one deep rule a test can check exactly,
   whose stated consequences meet other subsystems (ordering, scope of failure, identity, lifecycle with work in
   flight, partial or missing data, output in more than one format, a second source of truth that must agree). No
   broad "everything must stay consistent" contracts. No unrelated hard points.
3. Testable offline through the real code (the repository's own test setup and fixtures); no network, no live
   services, no timing races.
4. Novel: no merged or open PR implements it, no issue declines it, the README/docs do not say it is unsupported.
   Search issues and PRs in every state (`gh issue list -R {REPO} --state all --search ...`,
   `gh pr list -R {REPO} --state all --search ...`) and `git log -S` for the key symbol. List the searches.
5. Fits the repository's direction (README, docs, contributing guides).
6. Deep and unhinted: the answer is not visible from the surface (the symptom site, the nearest helper and the files
   the requirement's words grep to do not decide it; the solver traces the value across subsystems first); no TODO,
   comment, doc or README line, issue text, test name or existing helper states or already computes the fix; at least
   two materially different fair designs pass.
7. Long: an engineer new to the repository must read 80+ files across 3+ packages, or trace several large files end
   to end, before the first correct edit; and something they can run (the repository's tests, a command's output, a
   saved file read back) keeps failing until the design is right. Give that reading chain as file:line and name the
   loop. A change whose fix sits in one module, or that nothing in the repository can show wrong, does not qualify.
8. Bounded: every universal word the task will need (every, any, each, all pairs, any output) has an axis the
   repository defines with few members or one code path that treats all members alike; name the axis and its size.

Do not build or run anything from the repository unless your environment explicitly allows offline test runs; give a
bug's reproduction as the exact test you would write plus the code path that proves it by reading, marked NOT RUN.

## For each candidate (fixed schema)
```
## <title in user words>
- kind: bugfix | feature_request
- files (3-30 production, the value's real path): <paths>
- core outcome: <one sentence>
- hard points (1-2) and their stated consequences (3-4 total): <consequence> | <subsystem pair> | <how a test checks it>
- out of scope (scope sentence candidates): <list>
- novelty searches: <queries and result counts, issue/PR numbers seen>
- offline test plan: <real objects used, fixtures>
- reproduction (bugs): <test or command, output or NOT RUN with the code path>
- risks: <anything undiscoverable, timing-dependent, very broad, or a design choice the description would have to invent>
- depth: <file:line trace a solver must follow; why the symptom site and the nearest helper do not decide it>
- length: <files to read before the first correct edit (count, packages) | files to change | layers crossed | the loop that keeps failing>
- universal words: <word -> axis -> members (count) -> one code path or not>
- repo hints checked: <TODO / doc / comment / test-name / helper searches and their result>
- fair designs (>= 2): <design A> | <design B>
- score: consequences independent (0-2) + offline real-code testability (0-2) + novelty (0-2) + size 3-30 files (0-2) + depth (0-2) + length (0-2)
```
Rank by score. Cite file:line for every claim about current behaviour. Mark anything unchecked NOT VERIFIED. End with
a 5-line summary naming your top 3.
