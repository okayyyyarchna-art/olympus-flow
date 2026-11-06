#!/usr/bin/env bash
# Any Codex job (normal mode; sandbox only for solvers - user 2026-10-18) from a brief (FP second opinion, repo-hunt lane, gap analysis) - the G1/G2/G3 gates stay in
# codex_review.sh.
#   bash ~/OSS/shipd/tools/codex_job.sh <task-dir> <job-name> <brief.md> [effort]
# Report: <task-dir>/eval/codex/<job-name>.md (console log .log). Codex runs in its normal (config) mode with network;
# the prompt limits its writes to the report and _cx probes. Solvers (eval/solve.sh, gpt_solve_in_image.sh) stay sandboxed.
set -uo pipefail
T=$(cd "$1" && pwd); name="$2"; brief="$3"; effort="${4:-high}"; kind="${5:-review}"  # review | build | search | judge
# CODEX_MODEL: optional model for this job (e.g. gpt-5.6-terra, the platform's TQ/SQ/DQ model); default = config model
model_args=(); [ -n "${CODEX_MODEL:-}" ] && model_args=(-m "$CODEX_MODEL")
# CODEX_ONE_OFF_EFFORT: only when the user asks for another effort for one job (the rule stays HIGH)
if [ -n "${CODEX_ONE_OFF_EFFORT:-}" ]; then effort="$CODEX_ONE_OFF_EFFORT"; echo "one-off effort: $effort (user request)" >&2
elif [ "$effort" != high ]; then echo "effort $effort -> high (user rule 2026-10-28: Codex GPT Sol 6.1 HIGH only)" >&2; effort=high; fi
[ -f "$brief" ] || { echo "brief not found: $brief" >&2; exit 2; }
command -v codex >/dev/null || { echo "codex CLI not found" >&2; exit 2; }
out_dir="$T/eval/codex"; mkdir -p "$out_dir"; out="$out_dir/$name.md"
if [ "$kind" = search ]; then
# search: a repository study (seam search) that reads ONLY its brief. The Olympus skills and the memory files carry
# wording that OpenAI's safety filter flags, which ended two Codex search jobs on 2026-10-24 with no report.
prompt="You are a research assistant (Codex) working for the coordinator (main Claude). Task folder: $T.
Your instructions are in this brief; read it first and do exactly what it asks: $brief
Everything you need is in that brief and the shared brief it names. Do not open, read or load any skill files
(nothing under C:/Users/ASUS/.codex/skills) and no memory files. Skip faust/auth.py, faust/transport/drivers/aiokafka.py
and the broker connection settings: they are out of scope. You may create ONLY the deliverables the brief names (plus small check
scripts under your lane folder with a _cx suffix); never edit the repository checkout or any package folder.
Return the same report as your final answer."
elif [ "$kind" = judge ]; then
# judge: a TQ/SQ/Auto Review that reads ONLY its brief and the criteria file the brief names (plain wording), for the
# same reason as search: the skills and memory files carry wording the safety filter flags.
prompt="You are an independent reviewer (Codex) working for the coordinator (main Claude); nobody else's verdicts bind you.
Task folder: $T. Your instructions are in this brief; read it first and do exactly what it asks: $brief
Everything you need is in that brief and the files it names. Do not open, read or load any skill files
(nothing under C:/Users/ASUS/.codex/skills) and no memory files. Verify every claim by file:line or a check run, and
mark the rest NOT VERIFIED. You may read anything in the task folder; run check builds in Docker one container at a
time through python C:/Users/ASUS/OSS/shipd/tools/dockrun.py run ...; write ONLY
your report plus check files under the task's eval/ folder with a _cx suffix; never edit package folders (wip*/),
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
Before the brief, read the shared lessons: C:/Users/ASUS/.claude/projects/c--Users-asus-OSS/memory/MEMORY.md (and the memory files it points to that match your job) and your matching skill under ~/.codex/skills (olympus-codex-sq-judge, olympus-codex-tq-judge, olympus-codex-auto-reviewer, olympus-codex-reviewer).
Verify every claim (probe or file:line) and mark the rest NOT VERIFIED. Rules: you may read anything, run probes and Docker, and write ONLY your report plus probe files under the task's eval/ folder with a _cx suffix; never edit package folders (wip*/ submit*/ sample*/), repo/, base-clean/ or solveN/; Docker one container at a time via python C:/Users/ASUS/OSS/shipd/tools/dockrun.py run ...; never docker rm/rmi/prune or stop containers you did not start.
Return only your report (Markdown), starting with a one-line Verdict."
fi
echo "Codex job $name -> $out (typically 5-20 min)"
# The final answer goes to $out.final; it replaces $out only when Codex did not write a longer report there itself
# (2026-11-05: a brief named $out as the deliverable and the short final answer overwrote the full report).
codex exec --sandbox danger-full-access --skip-git-repo-check -C "$T" "${model_args[@]}" -c model_reasoning_effort="\"$effort\"" -o "$out.final" "$prompt" \
  < /dev/null > "$out.log" 2>&1
rc=$?
if [ -s "$out.final" ] && { [ ! -s "$out" ] || [ "$(wc -c < "$out.final")" -ge "$(wc -c < "$out")" ]; }; then cp "$out.final" "$out"; fi
if [ $rc -ne 0 ] || [ ! -s "$out" ]; then echo "codex job failed (rc=$rc); see $out.log" >&2; exit 1; fi
echo "Report: $out"; grep -m1 -i '^verdict' "$out" || true
