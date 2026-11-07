#!/usr/bin/env bash
# Tracked: round.sh <task> <tag> --check fairness|sq-a|sq-b|dq|ar|verify|ref-audit-a|ref-audit-b|gate
# Convenience aggregate: round.sh <task> [tag] [checks...] waits for every child, serially.
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
main() {
  [ "$#" -ge 1 ] || return 2
  local T tag c check sample report rc failed=0
  T=$(cd "$1" && pwd) || return 2; tag="${2:-r1}"
  shift; [ "$#" = 0 ] || shift
  local checks=()
  if [ "${1:-}" = --check ]; then
    [ "$#" = 2 ] || return 2
    checks=("$2")
  else
    [ "$#" -gt 0 ] || set -- fairness sq dq ar
    for c in "$@"; do
      case "$c" in sq) checks+=(sq-a sq-b);; ref-audit) checks+=(ref-audit-a ref-audit-b);; *) checks+=("$c");; esac
    done
    checks+=(verify gate)
  fi
  local R="$OLYMPUS_TOOLS/replica.sh" out="$T/eval/replica"
  local capacity
  capacity=$("$PY" -c 'import sys; sys.path.insert(0, sys.argv[1]); from machine import slot_limit; print(slot_limit(int(sys.argv[2]), sys.argv[3] or None))' "$OLYMPUS_TOOLS" "$OLYMPUS_REVIEW_LANES" "${ROUND_SLOTS:-}") || return 2
  for c in "${checks[@]}"; do
    case "$c" in
      sq-a|sq-b) check=sq;; ref-audit-a|ref-audit-b) check=ref-audit;;
      fairness|dq|ar|verify) check="$c";; gate) continue;; *) echo "unknown check: $c" >&2; return 2;;
    esac
    bash "$R" "$T" "$check" "$tag" --validate-only || return 2
  done
  mkdir -p "$out"
  # Capacity comes from the machine profile.
  local slots="$OLYMPUS_WORK_ROOT/.round-slots" slot="" pid i
  mkdir -p "$slots"
  while [ -z "$slot" ]; do
    for i in $(seq 1 "$capacity"); do
      if mkdir "$slots/$i" 2>/dev/null; then slot="$slots/$i"; echo "$$" > "$slot/owner"; break; fi
      pid=$(cat "$slots/$i/owner" 2>/dev/null)
      [ -z "$pid" ] || kill -0 "$pid" 2>/dev/null || rm -rf "${slots:?}/$i"
    done
    [ -n "$slot" ] || sleep 2
  done
  trap 'rm -rf "${slot:?}"' EXIT
  for c in "${checks[@]}"; do
    sample="$tag"; check="$c"
    case "$c" in
      sq-a) check=sq; sample="${tag}a";; sq-b) check=sq; sample="${tag}b";;
      ref-audit-a) check=ref-audit; sample="${tag}ra";; ref-audit-b) check=ref-audit; sample="${tag}rb";;
    esac
    if [ "$c" = gate ]; then
      "$PY" "$OLYMPUS_TOOLS/summarize.py" "$out" "$tag" | tee "$out/summary-$tag.md"
      rc=${PIPESTATUS[0]}
    else
      report="$out/$check-$sample.json"
      rm -f "$report" "$out/$check-${sample}_cx.json"
      bash "$R" "$T" "$check" "$sample" > "$out/$check-$sample.log" 2>&1
      rc=$?
      [ -s "$report" ] || { echo "missing or empty report: $report" >&2; rc=1; }
    fi
    [ "$rc" = 0 ] || failed=1
  done
  rm -rf "${slot:?}"; trap - EXIT
  return "$failed"
}
main "$@"; exit $?
