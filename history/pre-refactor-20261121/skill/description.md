# Description rulebook: the only source of truth for task descriptions

The description is the exam question. The tests grade it, the reference answers it, the platform checks that the
three match. A good one is short, in the owner's own words, has one reading per consequential clause, and every
tested outcome can be derived from it plus the repository. Difficulty is designed in the tests (the code paths the
outcomes run through), never in ambiguous words.

**Evidence rule:** only tasks submitted on or after 2026-10-16 set rules (the platform added the requirement-count and
AI/plagiarism checks on 2026-10-14). Older tasks are historical mechanisms only. Agents improve with every submission,
so the newest verified accepted texts set the bar. Audits: vet eval/desc-audit-A.md, desc-audit-B.md,
desc-history-digest.md, desc-recipe-astra.md; decisions: olympus-product TRIAGE-desc-astra.md.

## 0. Policy and states (owner rules)
| State | What may change | Exit |
|---|---|---|
| PRE-LOCK | anything; every check in section 3 runs here | the lock (section 3 step 11) |
| LOCKED, before v1 | the text changes only through a stage-7 round's fix batch (PIPELINE.md Confirmation schedule item 4): word-reach check, fairness replica on the tests, unit count, and the owner approves the new words; other findings change tests and the reference inside the stated sentences | the v1 paste |
| LOCKED, from v1 on | nothing in the text; findings change tests and the reference inside the stated sentences | the platform rollout result |
| OWNER EXCEPTION | one change (section 5b), only when the owner asks for it. The builder never proposes, drafts or lists one. Usually not needed: a text that is imperfect but whose effect tests can absorb stays (vet) | locked for good |
| REDESIGN | outside the band and no allowed lever works: the builder names the one blocker and proposes the smallest new version that clears it (new lock, fresh rollout); the owner approves it. A task is never retired: the flow ends only with an accepted task. A known false pass is never released to reach the band | owner approves the redesign |
Hard limits: at most **9 requirement units** (target 5-8); about **250 site words is guidance**, not a limit; the
owner writes the final words.

## 1. Sentence rules (the checklist and the prompts refer to these IDs)
**Precedence: the deletion test decides first.** Delete the sentence (or clause). If the remaining text plus a repo
line you can quote still decides the outcome one way, the sentence is a hint: it goes. It stays only when deleting it
leaves two readings with different observable results that the repo does not settle; then keep the fewest, most
general words that settle it, never the name of a hard point or an implied case. R7, R11, R16 and section 3 steps 5-7
never override it (vet direct-deps: boundary sentences written under R11/R16 made every decision for the agents, and
the trajectories read them as a checklist; vet task 2: words naming the PR base took the next rollout to 4/4).
| ID | Rule | Evidence |
|---|---|---|
| R1 | Every sentence is an **outcome** (observable result), a **scope** line, or an **anchor** (the exact public name an outcome attaches to); plus at most one true line of context or symptom that carries no promise | accepted texts since 16 Oct; context is not a requirement in the reading audits or DQ |
| R2 | No direction: no where/how/why, no narration that names a place, mechanism or cause. A symptom story with the observable is fine | vet wip01 direction lines (their removal coincided with the drop from 3/4; tests also changed, so the effect is confounded); turso "We currently support IN, EXISTS and NOT EXISTS" points at the code to extend |
| R3 | No instructions to the solver ("go through every file") | producer-flush (pre-16-Oct, historical): the only description issue any check raised (AR description band 2) |
| R4 | An example is allowed only to disambiguate behaviour or scope; never a list of hidden traps or a debugging checklist | docker proxy AR called its boundary examples necessary; a full corner list is the hint (faust-window, historical) |
| R5 | Count independently testable obligations honestly; group related clauses in one sentence when clearer; an "also / even when / instead" clause or a parenthetical that carries an outcome counts; never merge or reword to dodge the count | task 12 carries earliest/latest/datetime in one sentence; elio and task 11 failed TPQ on outcome-carrying parentheticals |
| R6 | One reading per consequential clause; use the repo's own term for each state | vet "did not run" (vet prints it for outages) -> 3 sweeps and a re-lock; "turned off" is the repo's word |
| R7 | Every normative promise (outcome, preservation, rejection) has a test; every test traces to a sentence or to a repo line cited at the assertion (build-checklist.md, the second-reading row). An implied case is traced to the repo, never by adding a sentence | the FP rule: an untested promise makes a passer that misses it a false pass |
| R8 | Every obligation is required-explicit, required-implied, or unspecified; "unnamed" is not "unrequired": an implied consequence of a stated invariant is required | topic-start's drop list would have released false passes |
| R9 | Never excuse a reference gap in the text | task 5: SQ read the excuse as a requirement |
| R10 | Every claim about current behaviour, API names and paths is true at the pin (source-checked) | docker "/export and /commit already hide these writes" was false -> major |
| R11 | For each boundary decide: outside the feature (no promise), preserve current behaviour (measured on base), or must reject (a requirement). Name a boundary only when the deletion test keeps it; do not catalogue unreachable or unsupported things; silence excludes nothing | task 5's exclusion read in reverse; turso's catalogue cost TPQ count; topic-start's missing tables exclusion |
| R12 | Depth, not breadth: one coherent objective, one hard invariant through several modules | elio's "every kind elio knows" contract: endless findings |
| R13 | The owner's own words; never fabricate anecdotes, typos or errors to look authored | model drafts were flagged by the AI check; owner texts passed |
| R14 | The sample's promises are the final contract; narrow or widen only before the lock | topic-start's late narrowing invalidated earlier runs |
| R15 | No URI schemes; the category follows the semantic change (the precheck's shape check is a warning) | prechecks; standby and turso are feature requests with bug-story openings |
| R16 | Clarifications are not hints: the exact words that close a two-meaning gate are allowed when the deletion test keeps them, direction never | "the **whole** app should fail" (task 12), "**If writing the copy fails**" (task 11), "a check that was **turned off**", "from that run only, **not the ones saved with the scan**" (vet) |

## 1b. Sentence roles, with real examples
Belongs when it carries needed meaning:
- Direct public ask: "Add start_from to app.topic()."
- Outcome with a precise boundary: "the first message greater than or equal to that time".
- Whole-system consequence: "the whole app should fail with ImproperlyConfigured instead of reading it".
- Short observed symptom: "When you press forward it will give you Cannot open .../old: Not found."
- Scope that changes applicability: "This only needs to be implemented on the aiokafka transport and for apps that
  dont have tables."
- Identity analogy: "The warning should name the suppression the same way the expired warning does."
- Explicit freedom: "If both are equal it does not matter which one receives it."
- Required preservation: "Topics that dont specify this ... will continue to use consumer_auto_offset_reset."
Never, in these roles: a solver instruction ("go through the entire repository"); an excuse ("I don't expect that one
to be handled"); an unrequested trim ("has not expired and"); an ambiguous state word ("a check that did not run"); a
false causal link ("so we never commit ..." where "and" is meant); a parenthetical smuggling a requirement past the
count; an unbounded parity umbrella ("a file elio knows how to display"); an unverified claim about base behaviour; a
loose example that changes the rule ("ex: app.log.1").

## 2. Where difficulty comes from (designed before writing a word)
- Good difficulty: a STATED outcome reached through a path a quick solver does not test: another entry point (a saved
  report, a second command), a second code path, ordering, lifecycle (restart, rebalance, stop), multiplicity, a saved
  format variant, an older input shape the repo documents. vet: report show of a saved PR scan, first match through
  package rules, an unrelated failing check, an older report without a check list, a mistyped id.
- Bad difficulty: a word with two readings (breaks the reference and fairness, separates nobody), an undiscoverable
  timing window, an unrelated subsystem, an unstated performance limit, missing tools.
- The seam's difficulty is seen in the solver runs after the lock ([difficulty.md](difficulty.md) section 2: 3 + 3
  local solves, 2 + 2 platform runs). The text adds no difficulty and removes none: it states the
  requirement.
- Trap inventory, qualitative: list each trap a solver must clear and mark it explicit or implied; do not stack two
  unnamed traps on one path; every implied consequence that is required gets a test (R8). Planning rates live only in
  the ledger's difficulty section (profiles.md); they never decide a sentence: the rollout measures.
- Target spread (owner 2026-11-09; a behavioural suggestion, never a gate): hard points that some agents solve, not
  all and not none. Prefer two hard points on different paths, each a little easier than extreme, over one extreme
  point that runs all clear or all miss (vet task 2 had one: 0/4 local solves, then Orion 4/4 and Nova 4/4 once
  wording named it). Neither is named in the text. An all-pass or all-fail rollout is still fine: rollout.md routes
  both.

## 3. Procedure (order fixed by the owner 2026-11-07)
**A. I scan before the owner sees the draft** (the draft handed over already passes every check):
1. **Decide the problem**: one observable objective at the pin, its public entry points and supported domain, and the
   three-way decision of R11 for every boundary. No undecided public behaviour may reach the lock.
2. **Obligation ledger** (eval/description_facts.md): each atomic obligation with its future wording, observable
   result, category (explicit / implied, R8), grounding (sentence, or repo behaviour with file:line), planned
   assertion, and the plausible partial implementation it rejects. At most 9 units (R5).
3. **Feasibility gate**: a disposable reference spike proves the hard path with the real interfaces; sketch one
   materially different valid design; run the base suite against the spike to find base tests that pin internals.
   If the hard path cannot be built or tested fairly, narrow the problem now. No difficulty gate (owner 2026-11-16):
   difficulty is seen in the solver runs after the lock (difficulty.md section 2).
4. **Variant table** per obligation: every shape a user can hit, marked TESTED, EXCLUDED (named boundary) or OUT
   (unreachable, with the evidence). TESTED only if a careful agent finds it from the text + repo.
   For every exception sentence ("if X, do not Y") list the states next to X that are not X: unknown, missing,
   failed, partial, older. Agents over-apply exceptions: on vet 15 of 16 platform runs treated an unknown check id
   as a check that was turned off. Each such neighbour that is TESTED is an implied trap; mark it, and never put two
   of them on one path (section 2: vet stacked the unknown id and the older report on one path, 0/16).
5. **Draft** from R1-R16, precise outcome words at the first draft.
   Name an entry-point family once ("a pull request scan", not each command that reaches it): every named command became
   its own requirement. When the DQ replica's count equals the number of tested outcomes, stop rewording.
6. **Word reach**: grep docs, code comments, configuration and diagnostic/error texts for every key word; every state
   the repo names with it is TESTED or the word changes. Scope words (only, any, always, every, all) and exclusions
   get a second-reading check in both directions.
   Entry-point words ("run", "save", "skip rule", a method name) cover every documented way the repo does that thing:
   list them all (edsl: "running the survey" = survey.run and survey.run_async, docs surveys.mdx:147; "skip rule" =
   add_skip_rule and add_rule(..., before_rule=True) with its own destination, CLI --destination). For each one, run
   the scenario WITHOUT the change at the pin: wherever it already behaves differently from the others, or already
   breaks the promise with no edit at all, decide it at once (R11) with a scope sentence ("only what add_question
   changes", "run_async is not covered") or a narrower word. For such an entry point (and only there; every other
   second reading follows step 7), never adjudicate it as "accept both / tests avoid it":
   reviewers read the sentence literally on every path, each round adds a test for a pre-existing engine defect, and
   the task drifts away from its seam (edsl-survey-insert: 14 of 50 cases ended up testing run_async, navigator and
   scheduling bugs that exist without any insertion; owner narrowed the tests back after the lock).
7. **Reading audit, two independent lanes** (Codex GPT Sol 6.1 high + Claude; the draft and the pinned repo only,
   never the reference) **and adjudication**: for every second reading record the separating input (one input, two
   different outputs), the strongest repo evidence for or against it, and the disposition: reword (the fewest words
   that leave one reading), a deliberate scope choice, or tests that accept both behaviours. A reword never names a
   hard point or an implied case from the ledger; when only such a sentence would remove the second reading, the
   disposition is a general sentence the repo makes discoverable, or tests that accept both (vet dev-only d2: four
   rewords named four corners). A DQ pass is not proof of one reading.
8. **Counts and checks, with evidence types**: the DQ replica runs with the real (or planned) test.patch, precheck.py,
   and the checklist in section 4. Record each result as TEXT-ONLY, STATIC (aligned with tests), EXECUTED or
   PLATFORM; no local check certifies AI detection, plagiarism or the platform's requirement count. Before the owner
   sees the draft: every sentence passes the deletion test, and a grep of the draft for the words of each entry in
   the ledger's "Hard points (not named)" list finds none (a hit goes back to step 7).

**B. The owner humanizes** the scanned draft, given the compact fact ledger and the precision points. The hand-over
lists the meaning each sentence must keep, never named corners or hard points as words to keep.

**C. I re-check the owner's text, then we lock:**
9. **Counterexample diff**: every obligation and every known separator (including untested variants and
   applicability), under my draft and under the owner's text; check quantifiers, negation, pronouns, tense,
   connectives (so, and, because, then) and exact output boundaries. Any unrequested change goes back to the owner as
   a concrete case, to fix in their own words.
10. **Word reach and reading check on every changed word**; DQ replica and precheck.py on the exact bytes; when
    tests exist, the fairness replica on them against the new text (vet direct-deps v8: skipped, and platform
    verifyFairness flagged an implied assertion).
11. **Lock** together with the owner. Lock record: hash, pinned commit, category, the test/reference snapshot
    reviewed, the count method and result, and the external checks still NOT VERIFIED. Before the lock the owner gets
    the **lock report** without asking (vet task 2: the owner had to ask for each part): (a) the unit count, mine and
    the DQ replica's; (b) one row per sentence: obligation, the test that checks it, and the hard point behind it
    (implied cases listed apart); (c) the difficulty check: per hard point, the words that would give its cause away,
    grepped in the text and absent, and what the text must reveal because it is the requirement; (d) what stays NOT
    VERIFIED until the platform (its own extraction and DQ, the real difficulty). The locked text goes to the
    build (tests and reference by the construction cards). Right after the lock, 3 + 3 local solves start and the owner runs 2 Orion + 2 Vega on
    the locked text, in parallel, while the build goes on at stage 4 (difficulty.md section 2); then the checks and the rest of the rollout on v1 (PIPELINE.md stage 7b).

## 4. Checklist before the lock (all yes, or a named external check marked NOT VERIFIED)
- [ ] one coherent objective; every boundary decided three-way (R11, R12)
- [ ] at most 9 requirement units, counted honestly (R5); short (about 250 site words as guidance)
- [ ] every sentence is an outcome, a scope line or an anchor, plus at most one true context line (R1)
- [ ] no direction, no solver instruction, no excuse, no trap list, no URI scheme (R2-R4, R9, R15)
- [ ] every sentence passes the deletion test; no word of a hard point or implied case in the text (section 1, step 8);
      purely stated requirements, no hints (owner 2026-11-15)
- [ ] every normative promise has a planned test; preservation sentences are tested or removed together with their
      assertions; every assertion traces to a sentence or quoted repo behaviour (R7)
- [ ] every obligation categorized explicit / implied; implied required consequences have planned tests (R8)
- [ ] every claim about current behaviour, names and paths source-checked (R10)
- [ ] feasibility gate done: hard path proven by a spike, a valid alternative sketched, base pins found (step 3)
- [ ] every key word grepped; the repo's own term; every second reading adjudicated with its separating input (R6,
      steps 6-7)
- [ ] the difficulty is in a stated path, not a word; no two unnamed traps stacked (section 2)
- [ ] every exception sentence has its non-exempt neighbours (unknown, missing, failed, partial, older) in the
  variant table, each marked; no two implied ones on one path (step 4)
- [ ] DQ replica run with the real test.patch; precheck.py clean; evidence types recorded (step 8)
- [ ] after the owner's rewrite: the counterexample diff shows no unrequested change (step 9)
- [ ] the sample's promises equal the locked promises (R14)

## 5. After the lock
The text is fixed (state LOCKED; before v1 only a stage-7 round's fix batch may change it, section 0). Findings from sweeps, false-pass audits and the platform rollout change tests and
the reference inside the stated sentences, through gates.md Repair. A finding that needs a new promise is reported
to the owner, and enters the text only through the OWNER EXCEPTION or REDESIGN state. What the calibration rollout
shows about the text (a missed reading, a hint, a gap) updates this rulebook for the next task, not this text.
- Runs failing a hard point is the task working, not a wording problem, whether the runs are local or on the
  platform. Wording that names a case the runs are failing is the hint that makes the task too easy (vet task 2).
- Every test added after the lock quotes the sentence that literally covers its path; check this before each paste.
  A test with no such sentence is dropped. The sentence is not added (vet task 2: tests grew past the text after
  sweep 1, and the fix went into the text).

## 5b. One description change (OWNER EXCEPTION), only when the owner asks
The goal is a text written right at the lock, and most tasks need no change. Sometimes one is needed, once. It comes
only from the owner asking: the builder never proposes, drafts or lists a change.
- **When the owner asks, report first, then do it if they still want it:** (1) which rollout runs it would change, and
  whether runs of two or more families took the same other reading that a reading audit accepts (on vet the text
  excluded "unknown id = turned off", so that convergence was fair difficulty and the text stayed); (2) whether tests
  or the reference could absorb it instead; (3) whether the wording names a case the runs are failing.
- **Built once, from all the evidence:** every ambiguity and hint the rollout, the sweeps, the replicas and the FP
  audits found goes into this one change; nothing is left for a later one. Before the owner writes the words: steps
  4-8 on the changed sentence, a reading audit of the whole new text, a replay of every rollout patch under the new
  reading, and a prediction per family.
- **Then:** the owner writes the line, steps 9-11 (the fairness replica included), lock for good, a fresh rollout
  (the old runs saw another text).
  No second change exists.
- **Rulebook repair:** name the rule that should have caught it at the first lock and sharpen it (or add one), so
  the next task is written right at once.

## 6. Rollout levers, description side (the order of use is rollout.md)
- First classify the evidence (rollout.md step 1): eligible runs only, per-family denominators; a re-evaluation of one
  trajectory adds no run; incomplete or contaminated runs are counted apart.
- Test-side levers, any time through Repair: a discriminator for an implied variant of a stated rule (turso Vega 2/4 ->
  1/4, elio Orion 4/4 -> 1/4, swift -> Orion 1/4, vet older-report and typo tests); fixing an assertion only when it
  pins unsupported behaviour (never because a case is rare or unnamed); dropping a test only when its case is
  unspecified (R8), with the list of wrong designs the drop would release.
- Too easy after rollout.md levers 1-5: stay in tests (prompts/calibrate-one-passer.md). A text change happens only if
  the owner asks (section 5b): remove the wording that gave the path, or deepen or add a requirement (word reach,
  reading audit and DQ replica first). Then a fresh rollout: replaying old patches checks compatibility only, it
  cannot measure a new wording. Text hints overshoot (elio 0/4 -> Orion 4/4, swift 4/4, turso 4/4, vet task 2 Orion
  4/4 and Nova 4/4), which is why text levers come last.
- Too hard after rollout.md levers 1-5: no text change under the lock; the REDESIGN state (owner decision).

## 7. Evidence: descriptions since the new checks (submitted on or after 2026-10-16)
"Reqs" is the platform's verifyFairness extraction (our own ledger count can differ). Status: A = accepted,
F = finalizing review, L = local only.
| Submitted | Task | Status | Narration | Direction hints | Corner list | Reqs | Result |
|---|---|---|---|---|---|---|---|
| 21 Oct | live readers | A | 9 | 2 | 7 | 15 | Vega 1/6 |
| 22 Oct | docker proxy | A | 4 | 5 | 5 | 9 | Orion 1/8 |
| 23 Oct | standby (task 9) | A | 4 | 2 | 0 | 9 | Vega 1/5 |
| 24 Oct | table visibility (task 10) | A | 6 | 2 | 1 | 9 | Vega 1/4 |
| 26 Oct | turso NOT IN | F | 3 | 3 | 1 | 10 | Vega 1/4 |
| 27 Oct | elio history | F | 6 | 2 | 4 | 2 (10 by our count) | Orion 1/4 |
| 1 Nov | dead-letter (task 11) | local record | 2 | 1 | 1 | 8 | Orion 1/4, genuine FP |
| 2 Nov | swift writes | F | 1 | 0 | 0 | 6 | Orion 1/4 |
| 3-4 Nov | topic start (task 12) | F | 0 | 0 | 0 | 8 | Orion 1/4, FP passed with caveats |
| 6 Nov | vet (ours) | L | 1 (context) | 0 | 0 | 6 | no rollout yet |
The trend: direction hints went from 2-5 per text to 0 and narration and corner lists to 0-1, while the November
tasks reached the band through tests with the text frozen. This is an observed trend, not a measured cause.

Example (task 12: 113 words; 8 units by platform extraction, 7 by our count):
```
Add start_from to app.topic().  When we are given a partition of that topic that we have no committed offset for as a
consumer group we should start from the beginning of the partition if earliest, the end if latest and if a datetime
then the first message greater than or equal to that time.

Topics that dont specify this, including the repartition topics created by group_by(), will continue to use
consumer_auto_offset_reset. If agents/streams that read from a topic dont all have the same start_from then the whole
app should fail with ImproperlyConfigured instead of reading it. This only needs to be implemented on the aiokafka
transport and for apps that dont have tables.
```

What cost the most rounds (prevented at S1): late scope cuts (each a DQ check plus a fresh rollout; the variant table
and R11 find them); the description used as the calibration lever (task 11: 15 edits); requirement-count failures
from an added clause or parenthetical; humanize passes that changed meaning (task 11 "so" -> GPT 0/8); imprecise
outcome words ("the app" -> "the whole app"); a broad contract (elio); a two-reading word as the difficulty lever (vet).

## 8. Prompts
Draft prompt (fill <...>):
```
Write the task description for <seam> in <repo> at <commit>. Inputs: the obligation ledger (each obligation with its
observable result, category explicit/implied, grounding and the partial implementation it rejects) and the boundary
decisions (outside / preserve / reject). Follow rules R1-R16 of the description rulebook. For every sentence output:
its kind (outcome / scope / anchor / context), the obligations it carries, the repo states each key word covers (grep
evidence with file:line), and any second reading with its separating input.
```
Reading audit prompt (2 independent lanes, before the lock; the draft and the pinned repo only):
```
Read only <task>/pkg/description.md and the repo at <path>. For each sentence: list every reading a careful developer
could take, and every repository state or input each key word covers (grep docs, code comments, configuration,
diagnostic and error texts; cite file:line). Mark a sentence AMBIGUOUS when two readings give different observable
results; for each, give the separating input, the strongest repository evidence for and against each reading, and
your proposed disposition (reword without naming a corner / scope choice / accept both). Do not open any other file
of the task folder.
```
