#!/usr/bin/env bash
# S5 gap sweep (user rule 2026-11-06): ONE review round that must find every gap at once, all lanes in parallel.
#   bash sweep.sh <task-dir> [tag]
# Lanes started here (background, independent): claude2 olympus-auto-reviewer + olympus-sq-judge with the shared sweep
# brief, and 2 GPT Sol 6.1 HIGH reference auditors (ref-audit). The coordinator starts the in-process lanes at the same
# time with the Agent tool: olympus-auto-reviewer and olympus-tq-judge, each told to follow replicas/sweep-brief.md.
# Then: merge every report, dedupe, reproduce, fix ALL gaps in one batch, prove each new test with a battery variant.
# The platform-shaped replica round (round.sh) runs once afterwards only as the final gate.
set -uo pipefail
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
T=$(cd "$1" && pwd); tag="${2:-s1}"; here=$(cd "$(dirname "$0")/.." && pwd)
brief="$T/eval/sweep-brief-$tag.md"; mkdir -p "$T/eval/claude2"
{ cat "$here/replicas/sweep-brief.md"; printf '\nTask folder: %s\n' "$T"; } > "$brief"
bash "$HOME/OSS/shipd/tools/check_codex_brief.sh" "$brief" >/dev/null || { echo "brief has flagged words" >&2; exit 3; }
C2_SUFFIX="sweep-$tag" bash "$HOME/OSS/shipd/tools/claude2_run.sh" ar "$T" pkg "$brief" high > "$T/eval/claude2/sweep-$tag-ar.log" 2>&1 &
C2_SUFFIX="sweep-$tag" bash "$HOME/OSS/shipd/tools/claude2_run.sh" sq "$T" pkg "$brief" high > "$T/eval/claude2/sweep-$tag-sq.log" 2>&1 &
bash "$here/tools/replica.sh" "$T" ref-audit "sw${tag}a" > "$T/eval/sweep-$tag-ref-a.log" 2>&1 &
sleep 2; bash "$here/tools/replica.sh" "$T" ref-audit "sw${tag}b" > "$T/eval/sweep-$tag-ref-b.log" 2>&1 &
echo "sweep $tag started: claude2 ar + sq, ref-audit sw${tag}a + sw${tag}b; start the in-process lanes now (auto-reviewer, tq-judge)"
wait
echo "sweep $tag lanes done: eval/claude2/pkg-*-sweep-$tag.md, eval/replica/ref-audit-sw${tag}*.json"
}
main "$@"; exit $?
