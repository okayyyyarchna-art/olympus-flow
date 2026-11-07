# Replica: description quality (site check "descriptionQuality") + task criteria ("taskQuality")

Read `common.md` first. You judge the description text; use test.patch only to see which sentences the tests rely on.

## Part A: description comments
Find passages in these categories (the site's categories):
- `ai_generated` (major): text that reads machine-written or prescriptive: mechanism and configuration details instead
  of behaviour (configuration flag values, a description of how the current code handles an internal signal or
  call), rule-sheet lists, uniform polished cadence, em-dashes, hard line wrapping. The site's advice: focus on behaviour,
  write it like a user prompting an engineer.
- `over_specification` (major or minor): a sentence that dictates implementation or blurs two cases the tests treat
  differently.
- `inferable` (minor): process instructions or facts any engineer infers ("go through every file").
- `ambiguity` (major): a sentence with two readings that lead to different tested outcomes.
- `missing_information` (major): a tested outcome that no sentence states and the repository does not reveal.
For each comment: `{category, severity, presentationOnly, quote, suggestion, testPatchCheck: {foundInTestPatch,
searchedFor, reasoning}}`. A sentence the tests rely on stays (presentation suggestions only).

## Part B: requirement count ("There are too many requirements in this task")
Count requirement UNITS (method measured on 24 descriptions with known verdicts): one unit per stated observable
outcome under one condition; per exception with its own outcome; per keep-as-is sentence; per transport or
entry-point sentence; per scope-out; per permission; outcomes per strategy or mode separately; a list inside one
sentence is one unit; not counted: symptom, motive, history, examples restating a unit. <= 14 units passed 8 of 8,
>= 19 failed 5 of 5, 15-18 mixed. Report the unit list and count; `blocking: true` at >= 19, and at 15-18 when the
text also reads as separate asks (below). Also list the distinct wanted behaviours as information. The site's blocking decision is NOT a number: it passed one coherent change described with many details
(24 extracted requirements, 13 by our count) and failed a text of 10 that asked for many separate behaviours. Set
`blocking: true` when the text reads as a list of separate asks rather than one change: several independent use cases
or features, each with its own rule set (e.g. per-file-type rules, per-route rules, per-mode rules listed one after
another), typically 8 or more such independent asks. A single feature whose sentences all refine the same rule or the
same mechanism is not blocking, however many details it has.

## Part C: task criteria (each PASS/FAIL with one line)
01 authentic engineering work; 02 reasonable formatting and presentation; 03 clearly describes what to build/fix;
04 the challenge is fair; 05 self-contained (not a repo-wide refactor); 06 not trivial or too easy; 07 success
objectively verifiable; 08 long-horizon and system-level.

## Part D: prechecks the site runs on the text
Also report as `ai_generated` risk: backticks or code formatting, semicolons, more than about 0.9 commas per 20 words,
"Should ..." directive lists, file or function names, model-like polish (every passing locked text avoided these).
ASCII only (curly quotes fail); no URLs or `scheme://` strings; hard cap 1000 words; category: a text describing wrong
current behaviour is a bugfix, a text opening with an ask for new behaviour is a feature request.

## Output schema (JSON)
```
{"comments": [...], "requirements": [str], "requirementCount": {"count": int, "blocking": bool},
 "verdictBasis": {"majors": int, "minors": int},
 "taskCriteria": [{"id": "01".."08", "verdict": "PASS|FAIL", "note": str}],
 "prechecks": {"ascii": bool, "noUrls": bool, "words": int, "categorySuggested": "bugfix|feature_request"},
 "verdict": "PASS|FAIL", "summary": str}
```
verdict FAIL when any non-presentation major comment exists or the requirement count is blocking.
