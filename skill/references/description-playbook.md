# Description playbook (S1): hard, solvable, locked once

The description is the exam question. The tests grade it, the reference answers it, the platform checks that the
three match. A good one is short, in the user's voice, has one reading per sentence, and every tested outcome can
be derived from it plus the repo. Difficulty is designed in the tests (the code paths the outcomes run through), not
in words. Budget: one lock. One more change is allowed after the first solve batch when the task is too easy or
unsolvable (section 6), and that change is the last.

**Evidence rule:** only tasks submitted on or after 2026-10-16 count. The platform added the "too many requirements"
and AI/plagiarism checks on 2026-10-14, so older accepted texts never faced them. Agents also improve with every
submission, so the most recent accepted texts set the bar (section 7). Per-task audits: vet task
eval/desc-audit-A.md, eval/desc-audit-B.md, eval/desc-history-digest.md.

## 1. What a description is
Every sentence is one of three kinds, nothing else:
- **Outcome**: an observable, tested result, one per sentence.
- **Scope**: the named inclusions and exclusions, up front ("This only needs to be implemented on the aiokafka
  transport and for apps that dont have tables").
- **Anchor**: the exact public name the outcome attaches to (`app.topic()`, `consumer_auto_offset_reset`,
  `ImproperlyConfigured`, "the same way the expired warning does"). Anchors are names, not mechanisms.
One short line of context or symptom in the user's voice is allowed ("We currently have many suppressions ... We
would like vet to tell us about these.").

| Rule | Evidence (submitted on or after 2026-10-16) |
|---|---|
| No direction: no where/how/why, no bug narration that names a place, mechanism or cause | vet wip01: three direction lines ("Currently if another suppression is before it in the list ...") -> 3/4 solves; removed -> ~1/4. turso "We currently support IN, EXISTS and NOT EXISTS in materialized views" points at the code to extend |
| No corner lists | docker proxy 5 corners, live readers 7; November texts 0 |
| No meta-instructions to the solver ("go through every file") | producer-flush opening: the only description issue any check raised (AR description band 2) |
| Target 5-8 requirements (user 2026-11-07: 6-8 is fine; the platform accepts up to ~9 and blocks at ~10+: elio 13, turso 16); count with the DQ replica before the lock | accepted since 2026-10-16: swift 6, vet 6, dead-letter 8, topic start 8 |
| One sentence = one outcome; "also / even when / instead" clauses and a parenthetical carrying an outcome each count | elio and task 11: one parenthetical rule -> "too many requirements" |
| Every sentence has ONE reading; prefer the repo's own term for a state | vet "did not run" (vet prints it for outages) -> 3 sweeps and a re-lock; "turned off" = the repo's word |
| Tested or deleted: every sentence tested, every test traced to a sentence | FP official definition |
| Never excuse a reference gap in the text | task 5: SQ read the excuse as a requirement |
| Depth, not breadth: one hard invariant through several modules | elio's broad "every kind" contract: endless findings |
| User's own words (AI detector) | model-written drafts flagged; user texts passed |
| Sample (Scope Gate) promises: narrowing later is accepted, widening is the risk | tasks 11, 12, turso, swift narrowed after the sample and were accepted |
| No URI schemes; bug-report shape -> Bugfix, "Add support for ..." -> Feature Request | prechecks |

**Clarifications are not hints.** The only text help the recent accepted descriptions carry is the exact word that
closes a gate with two meanings: "the **whole** app should fail" (task 12), "**If writing the copy fails**" (task 11),
"a check that was **turned off**" and "the policy warnings from that run only, **not the ones saved with the scan**"
(vet). Find these gates before the lock (word-reach + reading audit), and close them with a word, never with direction.

## 2. Where difficulty comes from (design it before writing a word)
Classify every trap a solver must clear: explicit clause ~1.0; named scoped-out ~0.9; unnamed but scoped ~0.4; latent
upstream bug ~0.12-0.3; unnamed cross-subsystem interaction ~0-0.05 (Orion profile). Target 0.15-0.25 for the in-band
family. These numbers drift upward as agents improve: re-calibrate on the newest rollouts.
- Good difficulty = a STATED outcome reached through a path a quick solver does not test: another entry point (a saved
  report, a second command), a second code path, ordering, lifecycle (restart, rebalance, stop), multiplicity, a saved
  format variant, an older input shape the repo documents. vet: report show of a saved PR scan, first match through
  package rules, an unrelated failing check, an older report without a check list, a mistyped id.
- Bad difficulty = a word with two readings (breaks the reference and fairness, separates nobody), an undiscoverable
  timing window, an unrelated subsystem, two stacked unnamed traps (0%).
- Named vs implied: solvers do the named variants and skip the implied ones; keep ONE implied trap for the band and
  catch it with a test.
- Local vs platform: platform agents are stronger (local 1/4 -> Orion ~3/4 on task 12). Local 0/4 is not a reason for
  hints; local 3-4/4 is a too-easy alarm.

## 3. S1 procedure (artifacts in eval/; order fixed by the user 2026-11-07)
**A. I scan before the user sees the draft** (the draft handed over must already pass every check):
1. **Facts list** (eval/description_facts.md): the 5-8 tested outcomes. For each: the code path, the entry points it
   covers, the natural wrong implementation a quick solver writes, the trap class. Gate: at least 2 outcomes carry a
   non-obvious path; no two-reading trap.
2. **Variant table** per outcome: every shape a user can hit. Mark each TESTED, EXCLUDED (named in the scope line) or
   OUT. Discoverability filter: TESTED only if a careful agent finds it from the text + repo.
3. **Draft** in the user's voice from section 1's three kinds; precise outcome words at the first draft.
4. **Word-reach check** per sentence: grep docs, code comments and diagnostic/error texts for each key word; every
   state the repo names with it is TESTED or the word changes. Scope words (only, any, always, every, all) and
   exclusions get a second-reading check in both directions.
5. **Reading audit** (2 independent lanes: Codex GPT high + Claude, on claude2 when an in-process lane is busy;
   prompt in section 8). Any second reading -> close it with a word now.
6. **Count**: DQ replica lands on the facts-list count +-1. Precheck.py clean. Checklist (section 4) all yes.

**B. The user humanizes** the scanned draft in their own words (AI detector).

**C. I re-check the user's text, then we lock:**
7. **Behaviour diff**: each tested case, result under my draft and under the user's text; every pronoun, referent,
   connective (so, because, then) and time qualifier checked against the tests. Any change not asked for -> I report
   it, the user fixes it in their words.
8. **Word-reach + reading check on every changed word**, DQ replica again, precheck.py.
9. **Lock** together with the user: record the hash. Start the one solve batch (2 Opus + 2 GPT) in the background.

## 4. Checklist before the lock (all yes)
- [ ] every sentence is an outcome, a scope line or an anchor (plus at most one line of context)
- [ ] 5-8 units, each tested; no sentence without a test; no test without a sentence
- [ ] no direction (where/how/why), no corner list, no excuse, no meta-instruction, no URI scheme
- [ ] every key word grepped; repo's own term; one reading per sentence (reading audit clean)
- [ ] scope words and exclusions second-read both ways; every unreachable variant named in the scope line
- [ ] at least 2 outcomes run through a non-obvious path; no two-reading trap; no stacked unnamed traps
- [ ] behaviour diff for every rewrite; after the user's rewrite every pronoun, referent, connective and time
      qualifier re-checked against the tests

## 5. After the lock
- The solve batch is an alarm: too easy (3-4/4 clean passers, FP-audited DESERVED) or unsolvable (0/4 with the misses
  on a word, not on a path). Otherwise its findings change tests inside the stated sentences.
- Sweep/FP findings that need a new promise go through triage first; a new promise is the last lever (section 6).
- Platform re-eval: tests may be added or dropped.

## 6. Calibration levers, in priority order (all stay available; use the next one only when the one before fails)
**Too easy** (a family above 25%, or two families in band; FP-audit the passers first: false passes are test gaps):
1. Remove any word that gives direction: read the passers' trajectories, find the sentence that told them the path
   (vet: three direction lines removed, 3/4 -> ~1/4; swift: per-check list and race hint removed).
2. Add a test discriminator on an unnamed variant of a stated rule (turso Vega 2/4 -> 1/4, elio Orion 4/4 -> 1/4, swift
   -> Orion 1/4, vet older-report and typo tests). Text unchanged; the finest control.
3. Deepen a stated outcome's path inside the same sentence (another entry point, a saved format).
4. Add a requirement (sqlite, standby, window worked; costs TPQ count and new FP surface; vet "did not run" broke the
   reference when the word had two readings). Run word-reach + reading audit on it first.

**Too hard** (all families 0%):
1. Read every trajectory; rank the closest runs; classify each miss: a two-meaning word (close it with the exact
   word), an undiscoverable quirk, a genuine mistake (keep).
2. Narrow the scope with a named exclusion (task 12 tables, task 11 confluent, turso grouped subqueries).
3. Drop the test of an unnamed corner that the closest runs miss (platform re-eval; task 12 lookup race).
4. One precise observable phrase inside an existing sentence (producer-flush "when the whole app is shutting down
   after a message was lost": 0/12 -> Orion 1/6). Replay the stored patches against it before pasting: hint sentences
   overshoot ("the Orion dial is binary": elio 0/4 -> Orion 4/4, swift 4/4, turso 4/4).
5. Remove the test AND its promise (the outcome is not reachable).

After any text change: behaviour diff, word-reach and reading audit on the changed sentence, DQ replica, lock for
good.

## 7. Accepted descriptions since the new checks (submitted on or after 2026-10-16)
| Submitted | Task | Narration | Direction hints | Corner list | Reqs (platform) | Result |
|---|---|---|---|---|---|---|
| 21 Oct | live readers | 9 | 2 | 7 | 15 | Vega 1/6 |
| 22 Oct | docker proxy | 4 | 5 | 5 | 9 | Orion 1/8 |
| 23 Oct | standby (task 9) | 4 | 2 | 0 | 9 | Vega 1/5 |
| 24 Oct | table visibility (task 10) | 6 | 2 | 1 | 9 | Vega 1/4 |
| 26 Oct | turso NOT IN | 3 | 3 | 1 | 10 | Vega 1/4 |
| 27 Oct | elio history | 6 | 2 | 4 | 2 (10 by our count) | Orion 1/4 |
| 1 Nov | dead-letter (task 11) | 2 | 1 | 1 | 8 | Orion 1/4, genuine FP |
| 2 Nov | swift writes | 1 | 0 | 0 | 6 | Orion 1/4 |
| 4 Nov | topic start (task 12) | 0 | 0 | 0 | 8 | Orion 1/4, genuine FP |
| 6 Nov | vet (ours) | 1 (context) | 0 | 0 | 6 | local 0/4 |

**The trend:** direction hints went from 2-5 per text to 0, narration and corner lists to 0-1, and every task still
landed at ~1/4 in one family. The November tasks reached the band through tests (discriminators on unnamed
variants), with the text frozen. Write for the newest row, not the oldest.

Example (task 12, 113 words, 8 requirements):
```
Add start_from to app.topic().  When we are given a partition of that topic that we have no committed offset for as a
consumer group we should start from the beginning of the partition if earliest, the end if latest and if a datetime
then the first message greater than or equal to that time.

Topics that dont specify this, including the repartition topics created by group_by(), will continue to use
consumer_auto_offset_reset. If agents/streams that read from a topic dont all have the same start_from then the whole
app should fail with ImproperlyConfigured instead of reading it. This only needs to be implemented on the aiokafka
transport and for apps that dont have tables.
```

**What cost the most rounds (prevent at S1):** late scope cuts (each = DQ + fresh rollout; the variant table finds
them at S1); the description used as the calibration lever (task 11: 15 edits); requirement-count failures from an
added clause or parenthetical; humanize passes that changed meaning (task 11 "so" -> GPT 0/8); imprecise outcome
words ("the app" -> "the whole app"); a broad contract (elio); a two-reading word as the difficulty lever (vet).

## 8. Prompts
Draft prompt (fill <...>):
```
Write the task description for <seam> in <repo> at <commit>. Inputs: the facts list (5-8 tested outcomes with their
code paths and the wrong implementation a quick solver writes). Every sentence is an outcome, a scope line or an
anchor (the exact public name the outcome attaches to), plus at most one line of context in plain user words. No
where/how/why, no bug narration with its cause, no corner lists, no excuses, no instructions to the solver, no URI
schemes. Use the repo's own term for every state (grep it). For every sentence output: its kind, the outcomes it
carries, the repo states each key word covers (grep evidence), and any second reading.
```
Reading audit prompt (2 independent lanes, before the lock):
```
Read only <task>/pkg/description.md and the repo at <path>. For each sentence: list every reading a careful developer
could take, and every repository state or input that each key word covers (grep docs, code comments, diagnostic and
error texts; cite file:line). Mark a sentence AMBIGUOUS when two readings lead to different observable results, and
give the input that separates them. Do not open any other file of the task folder.
```
