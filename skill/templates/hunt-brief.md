# Seam search: {REPO} ({LANG}), read-only

Goal: find 5-8 candidate tasks (bug fixes or feature requests) in the repository at {CLONE} (default branch
{BRANCH}, commit {COMMIT}). Each candidate is a change an engineer would make in this repository, which we can later
build with a reference solution and offline tests. Do not edit the repository; write only your report.

## Already taken (exclude these and anything that overlaps them)
{EXCLUDE}

## What makes a good candidate
1. One clear feature or bug in stateful or rule-evaluating code. The change crosses 2-4 production files.
2. 1-2 hard points (two moderate ones preferred over one extreme): each is one deep rule a test can check exactly, whose stated consequences meet other subsystems
   (ordering, scope of failure, identity, lifecycle with work in flight, partial or missing data, output in more than
   one format). No broad "everything must stay consistent" contracts. No unrelated hard points.
3. Testable offline through the real code (the repository's own test setup and fixtures); no network, no live
   services, no timing races.
4. Novel: no merged or open PR implements it, no issue declines it, the README/docs do not say it is unsupported.
   Search issues and PRs in every state (`gh issue list -R {REPO} --state all --search ...`,
   `gh pr list -R {REPO} --state all --search ...`) and `git log -S` for the key symbol. List the searches.
5. Fits the repository's direction (README, docs, contributing guides).

Do not build or run anything from the repository unless your environment explicitly allows offline test runs; give a
bug's reproduction as the exact test you would write plus the code path that proves it by reading, marked NOT RUN.

## For each candidate (fixed schema)
```
## <title in user words>
- kind: bugfix | feature_request
- files (2-4 production): <paths>
- core outcome: <one sentence>
- hard points (1-2) and their stated consequences (3-4 total): <consequence> | <subsystem pair> | <how a test checks it>
- out of scope (scope sentence candidates): <list>
- novelty searches: <queries and result counts, issue/PR numbers seen>
- offline test plan: <real objects used, fixtures>
- reproduction (bugs): <test or command, output or NOT RUN with the code path>
- risks: <anything undiscoverable, timing-dependent, very broad, or a design choice the description would have to invent>
- score: consequences independent (0-2) + offline real-code testability (0-2) + novelty (0-2) + size 2-4 files (0-2)
```
Rank by score. Cite file:line for every claim about current behaviour. Mark anything unchecked NOT VERIFIED. End with
a 5-line summary naming your top 3.
