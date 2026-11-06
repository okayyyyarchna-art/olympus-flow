#!/usr/bin/env bash
# Run one independent job on claude2 (the second Claude install: own account/limit, config ~/.claude-cli,
# same agents + skills via symlinks). Claude (main session) coordinates; claude2 and Codex give independent results.
#
#   bash ~/OSS/shipd/tools/claude2_run.sh <role> <task-dir> <pkg> [brief.md] [effort]
#
# roles (agent definitions in ~/.claude/agents, shared):
#   tq     olympus-tq-judge       (Test Quality judge, T1-T8)            default effort high (user 2026-10-17)
#   sq     olympus-sq-judge       (Solution Quality judge, S1-S4)        default effort high
#   ar     olympus-auto-reviewer  (Auto Review T1-T8 + S1-S4, Pass C)    default effort high
#   fp     olympus-fp-auditor     (FP panel on the passers)              default effort high
#   agentA / agentB               (full-review Agent A / Agent B)        default effort high
#   cold   cold reader: clean checkout + description only, lists ambiguities and its own design (no agent file)
#   free   any job: the brief is the whole instruction (repo hunt lane, gap analysis, probes)
# brief.md: what to review and what is already proven (default <task-dir>/eval/agent-brief-<pkg>.md).
# Report: the job writes <task-dir>/eval/claude2/<pkg>-<role>.md; console log next to it (.log).
# Rules passed to every job: read-only on package folders / repo / base-clean / solveN, probes under eval/ with a
# _c2 suffix, ONE container at a time through dockrun.py, never docker rm/rmi/prune or stop foreign containers.
# Solves on claude2 use eval/solve.sh-style clones: bash ~/OSS/shipd/tools/claude2_solve.sh.
set -uo pipefail
role="$1"; T=$(cd "$2" && pwd); pkg="$3"
brief="${4:-$T/eval/agent-brief-$pkg.md}"; effort="${5:-}"
case "$role" in
  tq) agent=olympus-tq-judge ;; sq) agent=olympus-sq-judge ;; ar) agent=olympus-auto-reviewer ;;
  fp) agent=olympus-fp-auditor ;; cold|free|agentA|agentB) agent="" ;; *) echo "unknown role $role" >&2; exit 2 ;;
esac
# effort (user 2026-10-17, final after trying max): high for every role unless given (max only when asked, e.g. studies)
[ -n "$effort" ] || effort=high
[ -f "$brief" ] || { echo "brief not found: $brief" >&2; exit 2; }
# optional C2_SUFFIX=<tag> keeps parallel runs of one role apart (e.g. 2 FP auditors on one package)
out="$T/eval/claude2"; mkdir -p "$out"; tag="$pkg-$role${C2_SUFFIX:+-$C2_SUFFIX}"
report="$out/$tag.md"; log="$out/$tag.log"
L=$(cd ~/OSS/claude-code/challenges/cc-faust-eos-offsets/eval 2>/dev/null && pwd -W)
rules="Rules: you are an independent reviewer running on a second Claude account; nobody else's verdicts bind you.
Never edit package folders (wip*/ submit*/ sample/), repo/, base-clean/ or solveN/ folders. Write probes only under
eval/ with a _c2 suffix. Docker: one container at a time via: MSYS_NO_PATHCONV=1 python \"$L/dockrun.py\" run --rm
--network none -v \"\$(pwd -W):/s:ro\" <image> bash /s/eval/<script>.sh ; never docker rm/rmi/prune, never stop
containers you did not start. Verify every claim you make (probe or file:line); mark the rest NOT VERIFIED.
NO mutation batteries, mutant sweeps, PYTHONHASHSEED sweeps or repeat runs (user rule 2026-10-18: mutation is
the coordinator's job after all checks): at most one targeted probe per suspected gap, host venv first, Docker
only to confirm (each container <= ~15 min).
When done, write your full report to $report and end with a short summary."
case "$role" in
  cold) task="Cold reader for the package $pkg. Read ONLY the description ($T/$pkg/description.md) and the base
repository ($T/base-clean, read-only). Do not read tests, the solution, eval/ or any other package. List every place
where a careful engineer could read the description two ways, which reading you would implement, and sketch your
design (files, state, the hard corners). Then read the brief for context only AFTER writing that section." ;;
  agentA) task="Full-review Agent A for the package $pkg (task folder $T; brief: $brief). Map EVERY sentence of
description.md to the hidden-test assertions that ground it (file:line), and every assertion back to a sentence.
Report: sentences with no or only partial grounding (each with a mutant of the reference that passes all current tests,
proven in Docker), assertions no sentence entails (unfair risk), and the smallest FAIR test for each real gap." ;;
  agentB) task="Full-review Agent B for the package $pkg (task folder $T; brief: $brief). Be the adversary: build
wrong, partial or hardcoded solutions (start from base-clean in a scratch copy under eval/*_c2) that pass ALL hidden
tests while breaking a description promise. Prove each in Docker (passes the hidden suite, fails the promise in a
probe). Report each with the promise it breaks and the smallest fair test that kills it." ;;
  free) task="Task folder: $T. Your instructions are in this brief; read it and do exactly what it asks (it may be a
build, a study or a hunt - not necessarily a review): $brief" ;;
  *) task="Task folder: $T (work there; use absolute paths). Package under review: $pkg. Read the brief first: $brief" ;;
esac
# Independence (review roles only): write your own verdict BEFORE reading earlier reviews or triage tables named in the
# brief; then add a section "Against earlier decisions" (HOLD/CONCEDE per earlier row you disagree with).
# Shared learning (user 2026-10-17): every role except the cold reader reads the coordinator's memory first.
mem="$HOME/.claude/projects/c--Users-asus-OSS/memory"
case "$role" in cold) ;; *) task="Before anything else read $mem/MEMORY.md and every lesson file it lists that concerns
your role (test quality, solution quality, auto review, FP/passers, hints/calibration, reviewers); they are the
team's accumulated rules and outweigh your defaults.
$task" ;; esac
case "$role" in free) ;; *) task="$task
Independence: form and write your own verdict first, from the package itself. Only then read earlier reviews/triage
tables the brief points to, and add a section 'Against earlier decisions' listing each earlier decision you disagree with." ;; esac
prompt="$task

$rules"
args=(-p "$prompt" --effort "$effort" --permission-mode acceptEdits
      --allowedTools "Bash,Read,Grep,Glob,Write,Edit,Agent" --add-dir "$T" --add-dir "$HOME/.claude/skills")
[ -n "$agent" ] && args+=(--agent "$agent")
# optional model override, e.g. CLAUDE2_MODEL=sonnet (default: the agent file's model, else the CLI default)
# default model (user rule 2026-10-28): Opus 5.5 high for every split job; FP auditors pass Sonnet explicitly
args+=(--model "${CLAUDE2_MODEL:-claude-opus-5-5}")
echo "claude2 $role ($agent, effort $effort) on $pkg -> $report"
# Reviews and studies run from ~/OSS so they load the SAME project memory (MEMORY.md + lesson files) as the
# coordinator; the task folder comes in through --add-dir and absolute paths. (Blind solves never use this script:
# they run from their own clean checkout via claude2_solve.sh, so they see no memory.)
wd="$HOME/OSS"; [ "$role" = cold ] && { wd="$out/cold-cwd"; mkdir -p "$wd"; }  # cold reader: no memory
cd "$wd" && CLAUDE_CONFIG_DIR="$(cygpath -w ~/.claude-cli)" OLYMPUS_WORKER=cli ~/.local/bin/claude.exe "${args[@]}" \
  < /dev/null > "$log" 2>&1
rc=$?
echo "claude2 $role exit=$rc (report: $report)"
[ -s "$report" ] || echo "WARNING: no report written at $report - check $log"
