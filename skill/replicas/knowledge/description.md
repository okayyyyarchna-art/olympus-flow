# KB lane: description side (DQ, prechecks, AR description band, requirement count, category, scope gate) + rollout signals

Author: claude2 (independent, effort medium), 2026-11-05. The brief asks for `kb/kb-description.md`; my launch rules
say to write only under `eval/`, so the full catalog is here. The coordinator can copy it.

## Sources and conventions
- Read: everything in `kb/src/` and `kb/src/digest/`. Seven parallel readers each took one slice and wrote raw notes
  (verbatim quotes plus line numbers) to `eval/claude2/notes-*_c2.md`. I spot-checked the key quotes against the
  sources (PF:149, PF:166-167, PF:235, PF:358-359, P:22/336/403/428, A:1254/2057/4433, MAP F58/E166/E183/E210,
  CAT:737/752), and all matched.
- Cite keys:
  - `PF:n` = platform-failures-cx.md line
  - `P:n` = platform-prechecks-cx.md
  - `AG:n` = platform-agents-cx.md
  - `MAP Exxx/Fxxx/Uxx` = cx1-review-findings-map-cx.md row
  - `CAT:n` = site-findings-catalog-cx.md
  - `A:n`, `B:n`, `C:n`, `D:n` = ledger-A/B/C/D line
  - `dg:<id>` = digest file `digest/<id>-*-cx.md`
- Task names in examples are only for traceability. The triggers are written to apply to any repository.
- HOLD-OUT honoured. Nothing is cited from:
  - topic-start wip6 (changelog channel agreement, lookup deadline fallback, retention-while-recovering test);
  - dead-letter wip46 (channel never released, on_rebalance_start without end, header prefix filter, Agent.clone);
  - the latest window-expiry Auto Review (empty all(), base-mode lifecycle file, JSON null after tombstone).

  The dead-letter digest dg:kh7dypmge7 is a different draft (mixed-policy findings). I use only its description-side
  lines (DQ PASS, D band 3 praise, prechecks).
- "single-instance" = seen once. Counts are recorded instances across all sources. Where one event appears in several
  sources, it is counted once.

---------------------------------------------------------------------------------------------------------------
## 1. Description Quality (DQ / older "Task Prompt Quality", TPQ)

The DQ verdict has this shape (dg files): `verdictBasis {"majors": n, "minors": n, "dropped": []}` plus
`requirementCount {"mode": "blocking", "blocking": bool}`. Each comment carries `category`, `severity`,
`presentationOnly`, `quote`, `suggestion` and a `testPatchCheck {foundInTestPatch, searchedFor, reasoning}`.

### DQ-1 AI-detection window (category ai_generated)
- check / severity: DQ / major. Blocking: one major fails DQ (dg:kh70pqzsgk majors 1 = FAIL).
- trigger: one sentence that reads machine-written. Two kinds were flagged:
  - an engineer-voice line that names internal config keys in parentheses;
  - a crisp, factual "X currently does Y" opener.

  The suggestion text is always the same boilerplate, so it does not explain the trigger: "This description is too
  prescriptive — focus on behavior instead of implementation details. Write your description like how you would prompt
  an LLM." The testPatchCheck reads "Constructed from an AI-detection window."
- detect locally:
  - Run an AI-text detector sentence by sentence, not on the whole text.
  - Flag sentences with parenthesised config/flag names, "currently treats/does" openers, and polished
    textbook-register sentences.
  - The precheck "doesn't look AI-generated (line wrapping, em-dashes)" is a different detector. It passed 50/50 times
    (P:9), including on both DQ AI FAILs, so passing it proves nothing.
- PASS side: text in the user's own words passed. Examples: the silences 413-word user text (A:1396), the window
  sentence the user humanized (A:1396), and the user-written producer-flush text, "AI 0%" (A:1394). Deleting words
  from a Claude paraphrase did not lower the score: "Claude draft AI 1.0, user paraphrase 0.30, paraphrase trimmed by
  deletions 1.0, blind user text PASS" (A:4736, external).
- examples:
  - swift draft: quote "Our proxy deletes the segments ... (the slo filter has allow_async_delete = false) ..."
    (PF:29-30, dg:kh70pqzsgk).
  - burrow reload v6: "Burrow currently treats SIGHUP as another signal to quit and exits." (PF:166, dg:kh77h1dpdc).
  - burrow silences wip36-38: "AI detector 0.80 blocked Description Quality" (A:66, A:1393; MAP E180).
  - window: "Task Prompt Quality FAILED on AI detection (0.80) for the restored-windows sentence" (A:1393; B:201).
- count: 5 recorded (2 with the DQ comment text, 3 by score only).

### DQ-2 Wording contradicts what the tests assert (category over_specification)
- check / severity: DQ / major, presentationOnly true, foundInTestPatch true. Blocking (it is a major).
- trigger: a blanket sentence that lumps two cases the tests treat differently. Here "removed or replaced → loses data"
  covered both removed entities (tests: start fresh) and changed entities (tests: keep their data). DQ searches the
  test patch by test name (`searchedFor: ChangedClusterKeepsWhatItStored; ChangedNotifierKeepsItsIncident; ...`).
- detect locally:
  - For every verb class in the text (remove / replace / change / re-add), list the tests and their expected outcomes.
  - Any test whose outcome is the opposite of what the sentence says for its class is a finding.
  - Grep test names for nouns the text lumps together.
- PASS side: the earlier v5 text ("Everything that is no longer in the file should lose its data, so it starts fresh
  if it's re-added.") separated removal from change. It was approved with description band 3 (dg:kh77h1dpdc Reviews).
- example: reload v6 "Anything that was removed or replaced loses its data and starts fresh" (PF:167). The suggestion
  was "Clarify the distinction between removal and a settings change ...". The rewrite turned an approved task into a
  DQ FAIL.
- count: 1, single-instance.

### DQ-3 Process directive to the solver (category inferable)
- check / severity: DQ / minor, non-blocking. Auto Review promotes it to P4/P6 Medium, which gives description band 2
  (see AR-D2).
- trigger: instructions about how to work, not what to build. Example: "go through the entire repository and each and
  every file ... Don't start anything before doing this step."
- detect locally: grep for imperative process verbs aimed at the solver ("before working", "go through",
  "read every", "first understand", "don't start").
- PASS side: none of the D3 descriptions contain solver directives (dg A and B notes).
- examples:
  - producer flush (accepted): quote "go through the entire repository and each and every file"; suggestion "Remove the
    demand for an exhaustive file-by-file review ..." (PF:359, dg:kh7ephrm9g).
  - The same directive drew precheck HIGH "process advice, not a requirement" on two other drafts (P:146, P:488, P:508;
    dg:kh70yqhmm2, dg:kh7b3n5g5r). On those DQ passed, so the DQ comment does not fire every time.
- count: 1 DQ comment and 3 precheck hits.

### DQ-4 Requirement count ("There are too many requirements in this task")
- check / severity: DQ/TPQ, `requirementCount.blocking: true`. It shows no count and can fail with 0 majors and
  0 minors.
- trigger: too many independent wanted outcomes. Prose length is not the cause: "Outcome count is distinct from prose
  length." (MAP:509). What counts:
  - each "also X", "even if Y" or "then I want" clause;
  - each sentence that states its own rule;
  - each parenthetical that carries its own outcome;
  - each exclusion or scope-out that carries an outcome;
  - plausibly, each behaviour family the tests check (external A/B, A:3897).

  What does not count: one-word qualifiers and list items (A:56; C:210-211).
- detect locally:
  - Split the text into atomic outcomes the way verifyFairness does (one per rule clause, lists split).
  - Compare against the last text that passed the counter. Any added outcome on a text "at the edge" is a probable
    FAIL.
  - There is no fixed cap: "no universal historical cap assumed" (MAP:460, MAP:540 #20). Observed passes were at
    about 7-10 outcomes and fails at about 13-17. One 10-outcome text passed (elio wip24) and another failed
    (dg:kh7b11f8w5).
- PASS side:
  - Replace many outcomes by ONE oracle sentence and delete the dropped sentences together with their tests: "behave
    as if it was started with the new file" got 17 → 7 and PASS (A:4430-4433; it was a cut, about 8 tests went too).
    Merging sentences or turning one into a clause that keeps its own outcome did not lower the count (other machine:
    osr-proxy 14 pass, 15 fail, 14 pass); folding parts that share one outcome into a list in one sentence does.
  - Use one-word list items in place of parentheticals: "any gz of a dd" PASS (C:118, C:200).
  - Rebuild from the last passing text, "never restructure" (A:548).
  - Join merged sentences with "and", never with a causal "so" (see W-5).
- examples:
  - reload wip54 "About17 requirements failed despite275 words." → "Seven requirements/240 words passed." (MAP E183).
  - elio wip18 "Thirteen outcomes too many." (MAP E207); wip38 "Two outcomes added to passing text." (E209); wip47b
    "Outcome-bearing parenthetical failed count." (E210).
  - dead-letter 10-31 "Outcome-bearing exclusion increased requirement count." (E166). wip41 failed twice, "count failed
    twice", after a scope-out was added (A:2067; C:205; MAP E167).
  - window wip3, about 13 (MAP E017; A:1382).
  - elio gzip draft: "There are too many requirements in this task", rc blocking (PF:235, dg:kh7b11f8w5).
- count: about 12 recorded FAILs across 5 tasks.

### DQ-5 Rule-sheet / directive list / tone (older TPQ categories)
- check / severity: TPQ `directive_list` major; DQ "too prescriptive" and tone FAILs.
- trigger:
  - endpoint-by-endpoint imperative chains ("A POST to /v3/admin/storage/snapshot writes the file immediately. ...");
  - literary or figurative sentences ("comes back exactly as it was, down to every entry");
  - text that "reads as a rule sheet rather than a request" (manager revert note, A:4785).
- detect locally:
  - Count stacked rule sentences ("19 of its 25 sentences are stacked behaviour rules", A:4786).
  - Flag runs of three or more sentences that each start with an HTTP verb, endpoint or API name.
  - Flag figurative wording.
- PASS side: a narrative rewrite ("read, save on demand, import", D:143-150). After it, the next failure was length,
  not presentation (A:1406).
- examples: snapshot v41 TPQ directive_list FAIL (A:1403; CAT:140; D:25). Silences DQ "too prescriptive" x2 (CAT:100;
  D:24, D:145). Snapshot tone FAIL x3 (CAT:139).
- count: 6.

### DQ-6 Minors add up to a FAIL
- check / severity: DQ, presentation-only minors. Three minors = FAIL.
- trigger: sentences compressed to fit a word or count budget, sentences without an explicit subject, and
  rollout-driven clause additions.
- detect locally: after any count-driven merge, re-read each sentence for a missing subject or ambiguous joins.
- examples:
  - mani: "Description Quality FAIL on 3 minor, presentation-only comments: three minors are enough for a FAIL"
    (A:3959; MAP E221).
  - snapshot v19 "DQ 3 presentation minors (sentence splits)" (A:416).
- count: 2. The verdict rule rests on the mani instance only.

### DQ PASS shape (praised wording)
- All D3/DQ-PASS digests had 0 majors and 0 minors. Lengths ran from 114 to 389 site words; voice ranged from an
  informal first-person bug report with typos to a terse feature spec; none used bullets.
- Praise quotes:
  - "concise and focused on the recovery behavior the tests exercise, without unnecessary scaffolding or
    implementation prescriptions" (dg:kh70yqhmm2);
  - "clear account of the failure and the tested consistency requirements without prescribing an implementation or
    relying on templated structure" (dg:kh7b3n5g5r);
  - "concise and behavior-focused; its key requirements align with the hidden tests without unnecessary scaffolding or
    API detail" (dg:kh7dypmge7);
  - "The description clearly states gzip preview parity and the important exclusions; its concrete edge cases are
    supported by the hidden tests." (dg:kh76ppnav0, run-on text still DQ PASS).
- "templated structure" is a named negative.

---------------------------------------------------------------------------------------------------------------
## 2. Prechecks (problem_and_tests stage and others)

Inventory (P:1-19): 18 checks; 16 of them seen about 50 times. Blocking fails turn "Problem Description & Tests" red.
Warnings do not block.

### PC-1 No URLs (sanity check, AI)
- severity: blocking FAIL.
- trigger: any http(s)/www/ftp link, and also any URI scheme such as `kafka://`. The exception is "only for example
  URLs used within the task". The check is stochastic: a line that had passed since wip34 failed when an edit re-ran
  the checks (A:112).
- detect locally: grep `[a-z][a-z0-9+.-]*://`, `http`, `www.`. Name the transport in words instead (A:2801).
- PASS side: "(#751)" with no URL passed sanity, though it drew a HIGH for adding noise (P:432, dg:kh77h1dpdc PC#5).
  Plain "the default aiokafka transport" passed.
- examples:
  - "Found external URL 'https://github.com/linkedin/Burrow/issues/751' ..." (P:403).
  - task 7 wip47: "`kafka://` in the description's scoping line counted as a URL" (MAP E086; CAT:799; B:399-406).
- count: 2.

### PC-2 "valid UTF-8" actually enforces ASCII
- severity: blocking FAIL.
- trigger: any non-ASCII character, such as a curly apostrophe: "Description contains non-ASCII character '’' at
  position 683. Please use only ASCII characters." (P:428).
- detect locally: `grep -nP '[^\x00-\x7F]' description.md`.
- count: 1, single-instance (dg:kh77h1dpdc PC#3).

### PC-3 Category mismatch
- severity: blocking FAIL with a contest path. The message is "Suggested category: bugfix".
- trigger: a text filed as feature_request that frames current behaviour as wrong ("stay reported forever", "only fix
  is a restart", "currently ignores", "The emulator ignores X").
- detect locally:
  - If the opening sentence or any sentence says the present behaviour is broken, the category must be bugfix.
  - Feature Request only fits when the text opens with the ask and does not call today's behaviour wrong (A:2788,
    D:27).
- PASS side: task 8 changed to Bugfix and was accepted (MAP E105, B:121). dg:kh7dypmge7 ("It would be great to have a
  `failure_policy` ...") passed as feature_request.
- examples: burrow rebalance draft (P:22-24) and lambda emulator (P:59-60), both dg:kh70n7s029. fake-gcs v2
  ("currently ignores", A:1638). task 8 sample (B:121).
- count: 4.

### PC-4 Length / word limits (three different gauges)
- Hard cap: "pass ≤1000 words, fail >1000" (45 runs, never failed; P:21).
- Older soft check: "pass ≤200 words, warn 201–400, fail >400" (5 runs; P:17). Its warning was "Description is
  verbose (283 words, over target by 83). Consider trimming to ≤200 words." (P:402). Under this older gauge snapshot
  failed at 406 (A:94).
- Readiness flag: "description over the word limit — trim it and re-run checks", shown even with "5/5 passing".
  - Seen on 4 drafts: kh70n7s029, kh70pqzsgk (precheck 200), kh7b11f8w5 (248) and kh7dypmge7 (233) (PF:13, 31, 239,
    326). All four also carry "some stale".
  - Not shown on accepted tasks of 286-389 site words, nor on kh7b3n5g5r (273 precheck words, not stale).
  - The threshold is NOT VERIFIED. A ~200 cutoff is an inference from one reader and is contradicted by kh7b3n5g5r,
    unless the flag is newer than that draft's last precheck.
- Tokenizer: the site splits on space, "-" and "/" (`/v3/admin/storage/snapshot` = 4 words; 406 vs wc 399; A:94,
  D:152-157). The precheck count runs higher than the "site words" header (211 vs 199, 311 vs 298, 243 vs 229).
- detect locally:
  - Count words with that split rule.
  - Report both counts.
  - Flag anything over 200 as "readiness word-limit risk (threshold unverified)". Never flag it as a fail.

### PC-5 "Problem description contains only necessary information" (AI)
- severity: always a warning, labelled HIGH/MEDIUM/LOW. The boilerplate says "Only high-severity issues are blocking",
  yet in the data HIGH items never blocked. kh70yqhmm2, kh7b3n5g5r, kh75aj75cn and kh76ppnav0 all showed "5/5 passing"
  while carrying HIGHs (dg C and B notes). With no HIGH the header changes to "Optional suggestions — Take or leave
  these" (dg:kh7dypmge7, kh73m6c4c1).
- Kinds of suggestion (P notes 2.9):
  - symptom lists ("motivational noise");
  - workarounds and issue numbers;
  - recaps of current behaviour ("discoverable from the codebase");
  - redundant restatements of the title or a final summary;
  - implied consequences;
  - lead-ins and filler ("That only partly works today:");
  - "as it does now" / obvious-default lines;
  - speculation ("I believe ...");
  - process advice;
  - environment, backend or transport caveats ("With the default aiokafka transport and at-least-once processing,");
  - implementation asides ("Since we pass those to core.Start we should be able to.");
  - long example or method lists;
  - whole out-of-scope sentences (P:579).

  No file-path suggestion is recorded.
- Severity drifts between reruns of the same text (dg:kh73rbw2de: 3 HIGH, then 1).
- CRITICAL calibration: this check routinely asks to delete clauses that DQ, AR and verifyFairness treat as
  load-bearing. Examples:
  - kh73rbw2de's at-least-once line became a covered requirement;
  - kh7b3n5g5r's "as it does now" line was AR's promiseCitation for a T3/T4 High;
  - for kh76ppnav0, AR said "none of those details should be removed";
  - the kh7ephrm9g transport/exclusion sentence was on AR's keep-list: "Keep the explicit scope exclusions".
- detect locally: report these as advisory Low only. Never recommend deleting a clause that a test, a
  verifyFairness requirement or a scope boundary depends on. Recommend deleting pure background, speculation, process
  advice, issue numbers and title restatements.

### PC-6 "Problem and tests are aligned" (AI)
- severity: warning, under the header "Interface information [WARNING]". "Behaviors [OK]" accompanies it.
- trigger: tests pin an interface literal the text does not state. Seen:
  - header order (P:594-595);
  - internal message names (P:54-55);
  - fractional-seconds env values (P:75-76);
  - return signatures and nil semantics (P:220-221);
  - option key names and nested shape (P:331-332);
  - a .svg.gz vs .svgz corner (P:341-342).

  In the older run it was a FAIL: "leap second `23:59:60Z` not covered by 'RFC 3339'" (A:4143).
- Tension: necessary-info asks to cut the same nil sentence that alignment asks to state (P:227 vs P:221). The
  alignment side wins whenever a test pins the literal (see VF-3).
- count: 8.

### PC-7 "Problem and tests are good quality" (AI)
- severity: FAIL or warning.
- triggers:
  - (a) FAIL when stated keep-behaviour sentences have no assertion: "only promotion tested; owner-stays, balance,
    ties, capacity untested" (task 9 sample, A:1851; B:139; MAP E121).
  - (b) FAIL when a description sentence contradicts a test ("leaving other clusters alone" vs a full import that
    empties others, CAT:136).
  - (c) warning when an "even if it fails" clause is asserted only on success (CAT:137).
  - (d) warning when a test is looser than a description word ("right away" vs tests that allow reload, P:357-362).
  - (e) warning on internal coupling, malformed harness, undeclared deps, and "could be clearer and more professional"
    (P:138, P:491).
  - (f) placeholder tests produced the ERROR "fix caching not covered" (A:3913).
- detect locally:
  - Build a sentence → test table.
  - Every sentence, including "stays the same", "keeps working" and "even if it fails", needs a base-failing
    assertion. For keep-behaviour, an assertion that passes on base is acceptable, but it must exist.
- PASS side: "No Test leftoverage [OK]" whenever the text names only public behaviour (P:267).
- count: about 10.

### PC-8 Non-description prechecks (for completeness; owned by the tests lane)
- test-file name collision is a blocking FAIL: names need a random hex suffix; "shipd"/"datacurve" are banned (P:89).
- test.sh needs base and new modes, and a malformed hunk is a FAIL (P:97, P:203).
- `go test` during the docker build is a FAIL (P:178).
- byte-identical test patch counts as plagiarism, a FAIL (P:336).
- plagiarism_review "functionally duplicate" / "same idea" is a warning only (P:350, P:526).
- repo-compliance false FAILs ("No commits in the past year" contradicted; A:1647; MAP E051/E052).
- "repository verification expired" is staleness, not content (PF:2 et al).

---------------------------------------------------------------------------------------------------------------
## 3. Scope Gate and similarity

### SG-1 The repo's own stated non-goal
- severity: Scope Gate REJECTED (off-scope). Reframing did not help ("reframed desc rejected again").
- trigger: the README or docs disclaim the feature: "README.md:187 'does _not_ emulate Lambda's orchestration'"
  (A:1629; D:55-63).
- detect locally: grep README and docs for "does not", "not supported", "out of scope" and "non-goal" near the
  feature's nouns before building.
- count: 1 (rejected twice), single-instance.

### SG-2 Derivative of an existing submission
- severity: similarity verdict DERIVATIVE at 0.87-0.91 (abandoned). At 0.8 after an "Adjacent, Older" sample it was a
  non-blocking Warning (A:120, A:1604; MAP E053; B:57).
- trigger: open-issue magnets that others already submitted. Examples: fake-gcs soft delete 0.91, OpenFermion #665,
  bump-my-version #429 0.87, lol-html #67 (A:1613, A:3196; CAT:212-213).
- PASS side: keep the full solution narrower than the sample. Every sample-first task passed (A:123, A:2309).
- count: 6.

### SG-3 Description re-scope re-runs the Scope Gate
- After a description change the Scope Gate goes stale ("Scope Gate: fail stale — re-run required" on many drafts).
  Narrowing re-scopes passed (window wip4 A:1385; task 9 A:459; standby second scope check B:140).
- Calibrating after the gate forced rescopes (B:426-434). Calibrating before the sample passed scope once.

---------------------------------------------------------------------------------------------------------------
## 4. Auto Review: description band (P-rules)

The mapping is any verified Medium in the description field → band 2; no Medium → band 3. The outcome is still driven
by the tests and solution bands (kh7ephrm9g approved at D2 with quality 2.67 and qualityScore 6; all-3 tasks score 7).

### AR-D1 P4 readability (run-on paragraph, nested parentheticals, pronoun-heavy rules)
- severity: Medium, presentationOnly → band 2. A single packed sentence alone was Low (CAT:81).
- trigger: the whole contract sits in one long paragraph or sentence with nested parentheticals and typos, or subtle
  lifecycle rules sit in pronoun-heavy nested sentences.
- detect locally:
  - Flag a sentence over about 60 words.
  - Flag nested parentheses, or a parenthetical holding more than 2 rules.
  - Flag a paragraph holding more than 4 rules.
  - Flag "one ... one ..." pronoun chains.
- The site's fix is to restructure, not cut: "Split the behavior, precedence rules, update semantics, and exclusions
  into concise sentences or bullets without removing load-bearing detail." (dg:kh76ppnav0)
- PASS side: informal grammar alone is fine: "Informal grammar does not make the required behavior ambiguous"
  (dg C notes E). Typos only cost when combined with one run-on paragraph (dg B notes).
- examples:
  - elio gzip: "the single long paragraph has rough grammar and nested parentheticals, making a complex contract harder
    to scan without creating a material ambiguity. Medium maps this field to band 2." (PF:149).
  - silences: "subtle lifecycle rules in pronoun-heavy nested sentences" P4 Medium x2 (CAT:82).
  - kscb: "one long sentence compresses several rules" P4 Medium (CAT:198).
- count: 4 Medium + 1 Low.

### AR-D2 P4/P6 process or solver directive
- severity: Medium → band 2. It is the promoted form of the DQ-3 minor (AR evidence `artifactFile: descriptionQuality`).
- quote: "that process instruction is disproportionate and prescriptive but does not make the task ambiguous, so the
  verified Medium issue maps to band 2" (PF:358, dg:kh7ephrm9g).
- count: 1, single-instance.

### AR-D3 P4 repeated sentence
- severity: Prompt 2/3.
- quote: "P4: repeated sentence 'Which means we always start at the beginning of the changelog.'" (EOS wip6;
  A:1403; B:68; MAP E047). wip8 got 3/3 with no recorded description fix, because AR samples different angles per run.
- detect locally: look for near-duplicate sentences (shingle overlap of 0.6 or more).
- count: 1, single-instance.

### AR-D4 Description sentences become promises for T3/T4/S1 (cross-lane, description-caused)
- AR quotes description sentences as `promiseCitation`. Umbrella phrases are read at their widest and turn every
  untested sub-path into a High. Examples:
  - "however it halts" (dg:kh7b3n5g5r);
  - "act as they currently do" (dg:kh7dypmge7);
  - "as it does now";
  - "a worker's table" (B:153);
  - "every window ... across the cluster" (A:1372).
- Relaxing a test while the sentence still promises the behaviour → T3/T4 High (silences "not shown", A:4580).
- detect locally: for each umbrella word (however, any, every, all, always, currently, as today), list the concrete
  paths it covers in the repo. Each path needs a test, or the sentence needs narrowing (see W-3).
- count: 8 or more.

### AR-D5 Process wording inside test/script comments (tests lane; listed because it is wording)
- The word "graded" or similar process words in test.sh comments or docstrings → Tests 0/3 Blocker (MAP E091, E246;
  B:108).

### AR description PASS quotes
- "does not prescribe files, helpers, or implementation structure" (all dg A files).
- "natural, behavioral, and self-contained" (dg C).
- "The description is clean, the harness is sound" (PF:318).
- "The description and reference solution are strong" (PF:255).
- AR keep-lists name explicit exclusions and boundary sentences: "Keep the explicit scope exclusions, the statement
  that records added during a flush belong to the next flush, and the persistent-error/shutdown requirements."
  (dg:kh7ephrm9g).

---------------------------------------------------------------------------------------------------------------
## 5. verifyFairness and TQ findings that blame the description

Per-test labels: [Prompt-stated] / [Repo-discoverable] (needs a file:line) / [Standard external semantics]. Concern
tags: timing_sensitivity, internal_coupling, overfit_single_point, brittle_message_matching, environment_assumption.
Tags alone do not make a test unfair. One unfair test fails TQ (1/13, 1/21, 1/27, 1/38, 1/50, 3/49, 3/67; A notes 12).
The digests label every per-test row "UNFAIR test:", but that is a digest artifact. Read the fairness field.

### VF-1 Scope, exclusion, "may", "I believe" and current-behaviour sentences become requirements
- trigger: verifyFairness extracts one requirement per rule clause, each with a `sourceQuote`. Scope or environment
  fragments, exclusions phrased as domain facts, permissive "may" caveats, hedged "I believe" lines and
  current-behaviour sentences are all extracted. Each then shows `covered: no` or `partial` when no test exercises it.
- detect locally:
  - Extract requirements the same way.
  - Every extracted line needs at least one test, or a reason it cannot be tested.
  - Partial coverage never failed a task; it feeds coverage suggestions, and later AR T4 (TQ advisory ≈ AR Medium,
    A:1462, A:2557).
- examples:
  - "[no] Work with at-least-once delivery ... | quote: At least once (not using exactly once). | tests: 0" (PF:399,
    dg:kh70yqhmm2).
  - "[no] Cloudflare D1 is outside the feature ... tests: 0" (PF:454).
  - "[no] A date or JSON value ... may count as changed ... tests: 0" (PF:456).
  - "I believe there is an offset that is persisted ..." → partial (PF:441, dg:kh73rbw2de).
  - kh72y19gr9's "only needs to be implemented on the aiokafka transport and for apps that dont have tables" became a
    requirement covered by all 20 tests (dg A).
  - Not every exclusion is extracted: elio "Not copied ... outside of elio", "(no SetTables)", and the kh7ephrm9g
    exclusion sentence were not (dg A and B). Extraction varies per run: "platform re-splits requirements per run"
    (A:3809; D:236-239).
- count: 10 or more.

### VF-2 Lists split per item; a run-on paragraph collapses into one
- "table, relation or column" became 3 requirements (dg:kh75aj75cn, 24 requirements).
- The elio gzip run-on paragraph became 1 requirement, `partial` (PF:459).
- detect locally: predict the count both ways. A 1-requirement extraction signals AR-D1.

### VF-3 Test pins a literal or format the text never names (grounding words)
- severity: the test is unfair → TQ FAIL.
- trigger: tests pin spellings, encodings, keys, status codes or exception classes that the text does not state and
  the repo does not establish. A humanized rewrite that drops grounding words is the common cause.
- detect locally: diff the old and new description for every literal a test asserts (query params, JSON, key names,
  status codes, header names, error class). Re-run that check after EVERY description edit.
- PASS side: restating the words restored PASS: "TQ PASS 47/47 fair" (A:1244). Exact literals are fair when the repo
  shows precedent (elio labels `archive_formats.rs:69-95`; T4 `res.offset` PF:442-449).
- examples:
  - silences wip46: "?group= spelling ('groupname'), json.Valid file, '{not json' malformed (no JSON stated)" TQ FAIL
    3/49 (A:1244; MAP F24-F26).
  - silences wip42: dropped "with those keys" → TQ FAIL 3/67 (A:1234; CAT:547).
  - unfair-test (desc-blame) list: CAT:63-69 (#19-#26), #81 "unknown `mode=` 400 vs repo 404 precedent", #82, #147.
  - sqlite FAIL_UNDOCUMENTED_REQUIREMENT on an exact exception type (A:4485-4490; dg:kh71zcezmf stale).
- count: about 15 assertions over 6 events.

### VF-4 Unstated rule or side effect co-asserted
- trigger: a test also asserts something the text never asked for. Examples:
  - "unrequested cleanup": "clearing or hiding old data ... not requested" (task 9 wip14, B:142; A:1861);
  - "does not freeze the worker" (B:35);
  - "an unstated membership rule" (B:58);
  - a caplog no-ERROR pin (MAP E036);
  - "Backup responsiveness unstated" (MAP E010).
- detect locally: for each assertion, quote the sentence that grounds it. No sentence means drop the assertion or
  state the behaviour.
- count: 8.

### VF-5 Test name read as a requirement
- "judge misread test_new_owner_does_not_close_while_it_is_still_replaying as pinning a no-close-during-replay timing
  rule" → TQ FAIL 1/38 (A:1453; MAP E030). The fix was to rename the test to the outcome.
- detect locally: test names must describe the asserted outcome only, with no temporal words the text does not have.
- count: 1, single-instance.

### VF-6 Interface lever not named
- A test requiring a new abstract method on a third-party store was "unfair unless the description names it" (task 9
  wip12; A:1889-1894; C:534-541; local judges only).
- count: 1, single-instance, and local only.

### VF-7 "Would need prompt edit" coverage suggestion
- The site flags a deliberately unpinned boundary as unspecified: "If the intended contract includes replaying the
  exact message whose processor raised ... state that explicitly ... The current test deliberately excludes `boom`, so
  this boundary remains unspecified." (PF:5, dg:kh70afkwq3).
- It was accepted as is. Any `sourceIfAdded: "Would need prompt edit"` is advisory, but it tells you the reviewer
  sees a gap.
- count: 1, single-instance.

### VF-8 A fairness tension resolved by stating the behaviour
- Silences: TQ ruled a rollback test unfair (#22); after the text stated rollback, AR then demanded it (#44) (D:182).
  When a behaviour is worth testing, state it in the text and then test it.

---------------------------------------------------------------------------------------------------------------
## 6. Wording readings that cause SQ, AR and rollout findings (description-caused)

### W-1 Two predicates under one negation
- trigger: "no longer used and shown" can be read as not-used-and-not-shown or as not-used-but-shown. "all 10 agents
  read 'still shown' -> 0/10" (A:1254, A:4570). The fix was to delete "and shown", after which AR went 3/3/3 (MAP F58;
  CAT:101).
- Related triggers: negation scope, any/a/all, either, "invalid", units (A:4572).
- detect: for every "not/no/never ... and/or ..." clause, write both readings and check each against the tests.
- count: 1, single-instance, with high impact.

### W-2 Negative exclusion read as a positive requirement
- trigger: an excuse sentence inside a promise. "If a worker abrupt stop before a change even made it to kafka ... I
  don't expect that one to be handled." Platform SQ read it as a must and gave Comp 1/3. Platform TQ read the same
  sentence as "no guarantee" (A:2597; MAP E054; C:257-265).
- fix: write it affirmatively ("...that change shouldn't be there after the restart either.").
- count: 2. The second is the leader temporal phrase (W-6).

### W-3 Broad noun or promise covers every mode, kind or driver the repo ships
- trigger: generic scope words cover modes the reference does not handle. Examples:
  - "every window ... across the cluster" → SQ FAIL x4, one table mode per round (A:1372; MAP E019-E023);
  - "a worker's table" → SetTable (B:153);
  - an untested confluent driver → SQ FAIL x2 (C:247-255);
  - documented caveats (A:3433).
- fix: a positive scope sentence. All of these were accepted:
  - "With the default aiokafka transport and at-least-once processing";
  - "plain tables (no SetTables) plus one GlobalTable";
  - "regular partitioned tables on memory/RocksDB";
  - "for apps that dont have tables".

  Widening the reference instead was DISPROVEN (A:1375).
- detect: enumerate the repo's drivers, transports, table kinds and modes that the feature's code path can reach. Each
  one is either tested or scoped out in the text.
- count: 10 or more.

### W-4 Deciding word with unlisted forms
- "all 7 Orion runs read 'directly' as plain `async for`; all 4 Vega runs included `events()`: family-split =
  ambiguity" (D:204).
- rule: "every deciding word lists concrete forms; no silent includes/excludes" (D:205). Adding the forms later failed
  the count twice (DQ-4), so list them before the lock.
- detect: for each qualifier (directly, normally, usual, supported, valid), list the repo forms it might include.
- count: 1, single-instance.

### W-5 Causal "so" introduced by merging sentences
- "acked once written, SO we never commit..." was read as cause and effect: local GPT 0/8, 4/8 built no commit
  barrier. Changing "so" to "and" was re-accepted (A:2057; C:227-235).
- count: 1, single-instance.

### W-6 Temporal phrase with two readings
- "before another worker can take it over" was read as wait-during-revocation (B:124, B:186; MAP E111). It was fixed
  with stop/leave wording.
- count: 1.

### W-7 Examples and parentheticals become obligations
- SQ cites each example as a requirement:
  - "(or more then 1 combined)" (PF:232);
  - "a picture, db, epub or cbz with a name that says nothing" (PF:233);
  - "the same lines shown before the cut off" → performance Medium (PF:156).
- Example lists also act as hints (A:56, A:3164: corner enumeration → "solved 29/29").
- count: 4.

### W-8 Unbounded quantifier or number
- Examples:
  - "any supported file" with no large-input test → a fixed-cap passer became an FP High (PF:150; A:1975);
  - "'a positive integer' means any size" → FP flag (A:4761);
  - "Any invalid input should be 400" vs JSON null → SQ 1/3 (A:1274).
- detect: bound every number and quantifier, or test at a size above any plausible hard-coded cap.
- count: 4.

### W-9 Hint that describes the computation
- "precise hint 'newest commit in commit order' made 4/5 agents rebuild the value the wrong way" (A:4550; A:1224).
- rule: state the visible outcome, not the computation.
- count: 2.

---------------------------------------------------------------------------------------------------------------
## 7. Rollout signals the final review uses

### R-1 Accepted solve shape
- Exactly one family in (0, 25%], the other two at 0%, at least 4 runs each, Nova average above 400K. Examples:
  - Orion 1/4 (kh72y19gr9, kh7aemqd7d, kh7dgy3tmn);
  - Vega 1/4 (kh717sntzs, kh7bfzrhqd);
  - Orion 1/8 (kh7d92724b);
  - Vega 1/5 (kh7dvvpbmr);
  - Orion 1/9 (kh71zcezmf);
  - Orion 2/8 (window, accepted).

  Sources: AG:34-77; dg A/B.
- Readiness wording: "Solved by one model only: Exactly one of Nova, Orion or Vega solves it, more than 0% and at most
  25% of the time".
- Seq profiles: Orion about 70-240K, Vega about 160-600K, Nova about 0.4-2.5M (AG notes; dg A/B).
- count: 12 tasks.

### R-2 Convergent failure on a stated clause = benign difficulty
- trigger: runs fail on 1-3 corners, each with a literal clause in the text. Near-misses look like 57-60/61 or 46/48.
- Site wording:
  - "Those failures line up with requirements already stated in the task, so the low solve rate is useful difficulty"
    (PF:320);
  - "stated or repository-discoverable" (AG:5, 10, 25, 35, 77, 84);
  - AR cites the exact phrase as proof of no ambiguity: "greater than or equal", "the whole app should fail", "at that
    moment".
- detect: for each convergent failure, find the sentence. If there is none, it is VF-3 or VF-4. If there is one but
  runs read it two ways, it is W-1/W-4. "shared blind spot" label: "if 7 of 10 runs fail one rule, re-read the sentence
  for a second reading" (CAT:737, CAT:752). Failing the same way = ambiguity; failing different ways = keep (A:4222).
- count: 15 or more.

### R-3 Convergence against one test's design = the test is unfair
- "Three implementations also converged on a late-resolution PDF design that your current private-state assertion
  rejects; that convergence supports changing the assertion" (PF:153; AG:60, AG:63).
- It is the only confirmed agent-side unfair flag in the digests.
- count: 1, single-instance.

### R-4 Zero solves = calibration FAIL even when fair
- "none of Nova, Orion, or Vega produced a full solve. Most attempts were very close, but they converged on unsafe
  storage assumptions ... these failures do not indicate that the stated behavior is unfair" → "Solvable: fail 0/23"
  (PF:257, PF:261; AG:66-68). 13/15 runs were at 19/20, on a case derivable only from the umbrella phrase "however it
  halts".
- The site's guidance text: "Consider whether the task is unfair, your description needs more clarity, or your tests
  are too narrow/broad."
- count: 1, single-instance.

### R-5 Run verdicts that blame the description
- FAIL_TEST_MISMATCH with agentBlameUnfair True for unstated contracts:
  - swift "an error-response contract not stated in the prompt";
  - swift "412 rather than ... 413. That error-precedence ... is not documented" (stale rows, dg:kh7dgy3tmn; the tests
    were later removed);
  - silences "tests unfair" from the two-reading phrase (W-1).
- FAIL_UNDOCUMENTED_REQUIREMENT for sqlite null-key TypeError (dg:kh71zcezmf stale).
- Evaluator labels "less explicit" (A:1681) and "undocumented". The Nova evaluator "flags base-bug tests as
  'undocumented' and 'Fair task' fails if ANY run flags the task" (A:4069, external).
- PASS side: FAIL_TEST_BROKEN from incomplete fakes (A:1333; B:252-260) is a harness problem, not the description.
  Run contests were rejected when baseline tests showed the regression (dg:kh7bfzrhqd; AG:45).
- count: 6.

### R-6 False positive tied to wording
- Official rule: a pass that misses any stated requirement is a broken verifier. Fix it by testing the requirement or
  removing it from the description (A:2663).
- Adjudicator uphold conditions:
  - a discriminating re-run;
  - a quoted sentence or core scenario;
  - an observable consequence (CAT:772-780).
- Uphold/overrule rates (D:496-499):
  - upheld: core-scenario data loss 6/7, concurrency with functional effect 4/4, explicit words 3/3;
  - overruled: stricter validation 0/7, corner status codes 0/6, out-of-scope surfaces 0/5.
- FP examples:
  - the 256 MiB-cap passer (PF:150, AR T band 1);
  - topic-start wip12 passers "missed three stated promises", fixed by re-scoping, then "GENUINE PASS" (A:2664, A:1959;
    MAP E177);
  - table visibility Nova "Bulk update escaped takeover visibility tracking" (MAP E134).
- "Passed with caveats" (warn) was still accepted (kh71zcezmf, kh72y19gr9, kh79vwdcg6, kh7d92724b, kh7dgy3tmn; PF:94,
  98, 224, 288, 293).
- count: 12.

### R-7 Shortcut and baseline signals (integrity, not description)
- PASS_SHORTCUT: agents edited graded upstream tests (MAP E009, E031, E060, E114, E145; dg:kh7dypmge7, dg:kh70yqhmm2).
  It counts as a failure.
- Baseline pin: one upstream test blocked 15/22 runs (MAP E176; A:2527).
- Model evidence must identify pools: "The current artifacts redact every model name, so they cannot establish the
  required Nova or Orion/Vega coverage." (PF:48).

### R-8 A description change voids rollouts
- A change costs about 84 tokens (DQ 4 + rollout 80) and invalidates every earlier run (A:336; C:219). Re-eval keeps
  runs only if the description and Dockerfile are unchanged.
- Recorded churn: 17 texts on dead-letter, 14 on SetTable, 7 on live readers (C:134; C:84; B:204).
- An approved text can fail DQ after a rewrite (DQ-2). Humanizing "silently widened/narrowed 3 promises" (C:570-577).
- PASS side: standby, table visibility and EOS were submitted with no description change after rollout, using a fair
  test as the discriminator (B:196, B:588).

---------------------------------------------------------------------------------------------------------------
## 8. PASS patterns (do not raise findings on these)
1. Informal, first-person, typo-laden prose of 114-389 site words with no bullets. DQ PASS 0/0 and D3 ("Informal
   grammar does not make the required behavior ambiguous").
2. One short "what is wrong today" sentence. It is accepted (A:4873), but phrase it so it does not read as AI (DQ-1)
   and pick the right category (PC-3).
3. Naming public API surfaces, config keys and endpoints. AR confirms them "at the pinned commit". This is not
   over-specification.
4. Reference-behaviour pointers ("behave like the RocksDB store", "anything a materialized view already handles", "act
   how it currently does") make detailed tests Repo-discoverable when a file:line backs them.
5. Explicit end-of-text exclusions and positive scope sentences. AR praises them ("clearly excludes threaded,
   transactional, and confluent paths"; "Keep the explicit scope exclusions") and they defuse W-3. They are not a
   precheck problem, even though necessary-info flags them.
6. Allow-either sentences ("either can succeed", "If both are equal it does not matter which one receives it") let
   race tests accept either winner (PF:553).
7. Exact boundary words ("greater than or equal", "at that moment", "the whole app should fail") turn convergent
   misses into benign difficulty.
8. HIGH items in "contains only necessary information" with "5/5 passing" are not blocking in any recorded case.
9. One deep-path phrase ("also when the whole app is shutting down after a message was lost") gave Orion 1/6 genuine
   and AR 3/3 (A:1684; B:48-50).
10. Seven grouped requirements in about 240 words, and 10 split requirements in 262 words (elio wip24), both passed
    the counter.

## 9. Severity calibration
| check | high / blocking | medium | low / non-blocking |
|---|---|---|---|
| DQ | ai_generated major (one major = FAIL); over_specification major even when presentationOnly; too-many-requirements blocking | — | inferable process directive = minor (but 3 minors = FAIL) |
| TPQ (older) | directive_list major; AI score ≥0.8 | — | contested "inferable" comment |
| Prechecks | URL/URI scheme; non-ASCII; category mismatch; name collision; base/new modes; byte-identical plagiarism; keep-behaviour sentences untested; sentence contradicts a test | — | necessary-info HIGH/MED/LOW (never blocked); alignment and quality warnings; plagiarism_review "same idea"; license unrecognised |
| AR description | — | any verified Medium → band 2: P4 run-on/nested readability, P4/P6 process directive, P4 repeated sentence (2/3) | packed single sentence = Low |
| AR tests (desc-caused) | stated promise + no test + wrong passer = T3/T4 High → band 1; relaxed test with promise kept = High; process words in test comments = Blocker 0/3 | single-point advisory / one mode tested = T4 Medium → band 2 | — |
| SQ (desc-caused) | broad promise or example corner violated = High, Comp 1/3 (15 of 16 SQ FAILs = one High, D:399-403) | heuristic miss on a stated example = Medium, 2/3 | — |
| TQ / verifyFairness | 1 unfair test of N = TQ FAIL | partial coverage = suggestion (becomes AR Medium) | concern tags alone |
| Rollout | 0 solves = Solvable FAIL; 2 families >0 or any >25% fails; FP upheld = challenge fails | "Passed with caveats" = accepted | shared blind spot = re-read warning |

## 10. Local DQ/precheck checker: steps (derived from the above)
1. ASCII-only; no `://`, `http` or `www`; no issue URLs (PC-1, PC-2).
2. Category versus voice: does any sentence call today's behaviour wrong? If so, bugfix (PC-3).
3. Word counts on the site tokenizer; report against 1000 (hard) and about 200 (readiness flag, unverified) (PC-4).
4. AI register per sentence; flag config-key parentheticals and "X currently does Y" openers (DQ-1).
5. Requirement extraction (clauses, lists split, scope/exclusion/"may"/"I believe" included). Compare with the last
   passing count; every outcome-bearing parenthetical or added exclusion is a risk (DQ-4, VF-1).
6. Sentence → test table: every requirement, keep-behaviour and "even if it fails" clause has an assertion; no
   sentence contradicts a test; no assertion lacks a grounding sentence or a repo file:line (PC-7, DQ-2, VF-3, VF-4).
7. Two-reading sweep: negation plus conjunction, deciding words, temporal phrases, causal joins, exclusions read as
   must and as may (W-1, W-2, W-4, W-5, W-6).
8. Breadth sweep: umbrella words versus the modes, drivers and kinds the repo ships; numbers and quantifiers bounded
   (W-3, W-8, AR-D4).
9. Presentation: no solver directives, no repeated sentence, no paragraph over about 4 rules, no nested parentheticals
   (DQ-3, AR-D1, AR-D2, AR-D3).
10. Necessary-info suggestions: report as Low; never cut a load-bearing clause (PC-5).

---------------------------------------------------------------------------------------------------------------
## Gaps and items NOT VERIFIED
- The readiness "description over the word limit" threshold is NOT VERIFIED (PC-4). The data only shows it on 4
  stale drafts at 200-248 precheck words, and it is absent on a non-stale 273-word draft.
- No precheck or Scope Gate message states a requirement-count number. The ~7-10 pass / ~13+ fail range is from our
  ledgers, not site text.
- The AI score thresholds (0.80 blocks, 0.30 passes) come from our ledger records; the DQ comment shows no score.
- DQ-6 (three minors = FAIL) and AR-D2/AR-D3 rest on a single instance each.
- I ran no check. This lane is document extraction, so no Docker or host runs were needed.

## Short summary
- **Output:** a catalog of 47 description-side and rollout patterns (DQ-1..6, PC-1..8, SG-1..3, AR-D1..5, VF-1..8,
  W-1..9, R-1..8), plus PASS patterns, a severity table and a 10-step local checker. Raw sliced notes are in
  `eval/claude2/notes-*_c2.md`.
- **Hard description blockers:**
  - a DQ ai_generated major on a single sentence; only user-voice text reliably passes;
  - a DQ over_specification major when wording contradicts what the tests assert;
  - "too many requirements" (outcome count, not length; parentheticals and exclusions count);
  - URLs or URI schemes;
  - non-ASCII characters;
  - category mismatch (bug-report voice means bugfix).
- **Auto Review description band:** any verified Medium gives band 2. The causes seen are a run-on or nested
  paragraph, a solver process directive, and a repeated sentence. Band 2 does not block approval.
- **Biggest calibration hard point:** the "only necessary information" HIGHs never blocked, yet they often target
  load-bearing scope or keep-behaviour clauses that AR and verifyFairness rely on. The local check must not echo them.
- **Main description-caused findings in other checks:**
  - scope, exclusion and "may" sentences counted as requirements;
  - humanized rewrites dropping grounding words (TQ FAIL);
  - two-reading phrases;
  - umbrella words read as every mode or driver;
  - unbounded quantifiers that let capped passers through as false positives.
- **Rollout shape the site accepts:** one family in (0, 25%], the other two at 0%, Nova above 400K. Convergent misses
  on a stated clause count as benign difficulty, while convergence against one test's design counts against the test.
  Zero solves fails calibration even when the task is fair.
