#!/usr/bin/env bash
# Any Codex job (normal mode; sandbox only for solvers - user 2026-10-18) from a brief (replica checks through replica.sh, repo-hunt lanes, solves through solvers.sh).
#   bash tools/lib/codex_job.sh <task-dir> <job-name> <brief.md> [effort, ignored: the rule decides] [kind]
# Replica checks go through tools/replica.sh, which calls this script with kind judge.
# Report: <task-dir>/eval/codex/<job-name>.md (console log .log). Codex runs in its normal (config) mode with network;
# the prompt limits its writes to the report and _cx probes. Solver clones are made by solvers.sh.
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../machine.sh" || exit 2
T=$(cd "$1" && pwd); name="$2"; brief="$3"; effort="${4:-}"; kind="${5:-review}"  # review | build | search | judge
# Model and effort come from the owner rules, not from the caller (BACKLOG #191: replica checks ran on another model for
# 10 hours because a caller passed one). Every Codex job runs on GPT Sol 6.1 (2026-10-28) at medium effort, whatever the
# kind (owner 2026-11-19: "medium ... for any work except in solver"). Solver runs and length spikes, which solvers.sh
# starts with the job name "solve", run at xhigh: the platform's Orion is Codex CLI on GPT Sol 6.1 at xhigh (owner
# 2026-11-18), and the local solve is its stand-in (difficulty.md section 2).
rule_model=gpt-6.1-sol
if [ "$name" = solve ]; then rule_effort=xhigh; else rule_effort=medium; fi
# CODEX_ONE_OFF_MODEL: only when the user asks for another model for one job. CODEX_MODEL may only repeat the rule model.
model="$rule_model"
if [ -n "${CODEX_ONE_OFF_MODEL:-}" ]; then model="$CODEX_ONE_OFF_MODEL"; echo "one-off model: $model (user request)" >&2
elif [ -n "${CODEX_MODEL:-}" ] && [ "$CODEX_MODEL" != "$rule_model" ]; then
  echo "CODEX_MODEL=$CODEX_MODEL refused: Codex jobs run on $rule_model; set CODEX_ONE_OFF_MODEL only when the user asks" >&2; exit 2
fi
model_args=(-m "$model")
# CODEX_ONE_OFF_EFFORT: another effort for one job, when the user asks or replica.sh sets a check's effort.
if [ -n "${CODEX_ONE_OFF_EFFORT:-}" ]; then effort="$CODEX_ONE_OFF_EFFORT"; echo "one-off effort: $effort" >&2
else
  [ -z "$effort" ] || [ "$effort" = "$rule_effort" ] || echo "effort $effort -> $rule_effort (owner rule for a $kind job)" >&2
  effort="$rule_effort"
fi
[ -f "$brief" ] || { echo "brief not found: $brief" >&2; exit 2; }
command -v "$OLYMPUS_CODEX_BIN" >/dev/null || { echo "codex CLI not found" >&2; exit 2; }
out_dir="$T/eval/codex"; mkdir -p "$out_dir"; out="$out_dir/$name.md"
if [ "$kind" = search ]; then
# search: a repository study (seam search) that reads ONLY its brief. The Olympus skills and the memory files carry
# wording that OpenAI's safety filter flags, which ended two Codex search jobs on 2026-10-24 with no report.
prompt="You are a research assistant (Codex) working for the coordinator (main Claude). Task folder: $T.
Your instructions are in this brief; read it first and do exactly what it asks: $brief
Everything you need is in that brief and the shared brief it names. Do not open, read or load any skill files
(nothing under $OLYMPUS_CODEX_HOME/skills) and no memory files. Skip faust/auth.py, faust/transport/drivers/aiokafka.py
and the broker connection settings: they are out of scope. You may create ONLY the deliverables the brief names (plus small check
scripts under your lane folder with a _cx suffix); never edit the repository checkout or any package folder.
Return the same report as your final answer."
elif [ "$kind" = judge ]; then
# judge: a TQ/SQ/Auto Review that reads ONLY its brief and the criteria file the brief names (plain wording), for the
# same reason as search: the skills and memory files carry wording the safety filter flags.
prompt="You are an independent reviewer (Codex) working for the coordinator (main Claude); nobody else's verdicts bind you.
Task folder: $T. Your instructions are in this brief; read it first and do exactly what it asks: $brief
Everything you need is in that brief and the files it names. Do not open, read or load any skill files
(nothing under $OLYMPUS_CODEX_HOME/skills) and no memory files. Verify every claim by file:line or a check run, and
mark the rest NOT VERIFIED. You may read anything in the task folder; run check builds in Docker one container at a
time through \"$PY\" \"$(machine_host "$OLYMPUS_LIB/dockrun.py")\" run ...; write ONLY
the report files the brief names, at exactly those paths and names (no suffix added), plus check files under the
task's eval/ folder with a _cx suffix; never edit package folders (wip*/),
repo/, base-clean/ or solveN/; never docker rm/rmi/prune or stop containers you did not start.
Return only your report (Markdown), starting with a one-line Verdict."
elif [ "$kind" = build ]; then
prompt="You are a builder (Codex) working for the coordinator (main Claude). Task folder: $T.
Your instructions are in this brief; read it first and do exactly what it asks: $brief
You may create and edit ONLY the files and folders the brief names as deliverables (plus scratch files under your
working folder); never edit these folders of the task folder: $T/wip*/, $T/submit*/, $T/sample*/, $T/repo/,
$T/base-clean/, $T/solveN/ (only those exact paths; a working folder the brief names is yours to edit); Docker one
container at a time via the dockrun.py lock; never docker rm/rmi/prune. When done, return a short report (Markdown)
starting with a one-line Verdict that lists every file you created or changed."
else
prompt="You are an independent reviewer (Codex) next to two Claude reviewers; nobody else's verdicts bind you.
Task folder: $T. Your instructions are in this brief; read it first and follow it: $brief
Verify every claim (probe or file:line) and mark the rest NOT VERIFIED. Rules: you may read anything, run probes and Docker, and write ONLY your report plus probe files under the task's eval/ folder with a _cx suffix; never edit package folders (wip*/ submit*/ sample*/), repo/, base-clean/ or solveN/; Docker one container at a time via \"$PY\" \"$(machine_host "$OLYMPUS_LIB/dockrun.py")\" run ...; never docker rm/rmi/prune or stop containers you did not start.
Return only your report (Markdown), starting with a one-line Verdict."
fi
# Time box (2026-11-07: a product build ran 3h20m and filled the disk with cold images). CODEX_TIME_BOX_MIN
# overrides the 120 min default; the brief gets the box and a Docker budget so the job plans for both.
box="${CODEX_TIME_BOX_MIN:-120}"
prompt="$prompt
Time box: finish and write your report within $box minutes; report what is NOT VERIFIED instead of running past it. Docker budget: build at most one new image, reuse existing images, and check free disk space (at least the machine floor, 12 GB by default) before any build."
echo "Codex job $name -> $out (model $model, effort $effort, time box $box min)"
# The final answer goes to $out.final; it replaces $out only when Codex did not write a longer report there itself
# (2026-11-05: a brief named $out as the deliverable and the short final answer overwrote the full report).
timeout -k 60 "${box}m" "$OLYMPUS_CODEX_BIN" exec --sandbox danger-full-access --skip-git-repo-check -C "$T" ${model_args[@]+"${model_args[@]}"} -c model_reasoning_effort="\"$effort\"" -o "$out.final" "$prompt" \
  < /dev/null > "$out.log" 2>&1
rc=$?
if [ -s "$out.final" ] && { [ ! -s "$out" ] || [ "$(wc -c < "$out.final")" -ge "$(wc -c < "$out")" ]; }; then cp "$out.final" "$out"; fi
if [ $rc -eq 124 ]; then echo "codex job hit the $box min time box; see $out.log" >&2; fi
if [ $rc -ne 0 ] || [ ! -s "$out" ]; then echo "codex job failed (rc=$rc); see $out.log" >&2; exit 1; fi
echo "Report: $out"; grep -m1 -i '^verdict' "$out" || true
