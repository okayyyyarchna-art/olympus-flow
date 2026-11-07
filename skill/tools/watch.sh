#!/usr/bin/env bash
# Read-only watcher for one pasted challenge. Polls the platform every N seconds and exits (waking the coordinator)
# when the user's runs have finished something new: a quality check, a precheck stage, or rollout runs, with nothing
# still pending/running. Prints what changed and whether anything failed. Never triggers anything.
#   bash watch.sh <challenge-id> <task-dir> [interval-seconds=300] [max-hours=12]
# Optional (the owner reports results by default): run it in the background when the owner asks; when it exits: pull.sh, then stage 8 (platform.md).
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
export OLYMPUS_NO_UPDATE_CHECK=1
id="$1"; T="$2"; iv="${3:-300}"; maxh="${4:-12}"
here="$(cd "$(dirname "$0")" && pwd)"
st="$T/eval/platform"; mkdir -p "$st"
snap() {  # one line per item: kind|key|status|verdict ; plus ACTIVE|n (pending/running)
  olympus problems view "$id" --json 2>/dev/null | "$PY" "$here/watch_snap.py"
}
base="$st/watch-base.txt"
[ -s "$base" ] || snap > "$base"
end=$((SECONDS + maxh * 3600))
while [ $SECONDS -lt $end ]; do
  sleep "$iv"
  now="$(snap)"
  echo "$now" | grep -q '^ERROR' && continue
  active="$(echo "$now" | grep '^ACTIVE|' | cut -d'|' -f2)"
  changes="$(diff <(grep -v '^ACTIVE' "$base") <(echo "$now" | grep -v '^ACTIVE') | grep '^>' || true)"
  if [ -n "$changes" ] && [ "${active:-1}" = "0" ]; then
    echo "$now" > "$base"
    echo "CHANGED (all user runs finished):"; echo "$changes" | sed 's/^> /  /'
    if echo "$changes" | grep -q -i -E '\|(fail|failed|FAIL|warning|revision_requested|reject|rejected)|FAIL_|PASS_CHEATED'; then
      echo "RESULT: something failed -> pull.sh + S9 loop"
    else
      echo "RESULT: all new results passed"
    fi
    echo "NEXT: handle this batch, then restart: bash $0 $id $T $iv $maxh (more results, e.g. the Scope Gate, come later)"
    exit 0
  fi
done
echo "watch timed out after ${maxh}h with no finished change"
}
main "$@"; exit $?
