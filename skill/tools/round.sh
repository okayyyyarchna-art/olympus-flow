#!/usr/bin/env bash
# Tracked: round.sh <task> <tag> --check fairness|sq-a|sq-b|dq|ar|verify|ref-audit-a|ref-audit-b|gate
# Convenience aggregate: round.sh <task> [tag] [checks...] waits for every child, serially.
# A check left out of the aggregate reuses the newest round's reports with the same input bytes (sq and dq: solution +
# description; fairness: tests + description). With none to reuse the round stops before spending anything.
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
input_key() {  # input_key <task> <sq|dq|fairness>: hash of the files that check reads
  local P="$1/pkg" desc other
  [ -f "$P/test.patch" ] || P="$1"
  desc="$P/description.md"; [ -f "$desc" ] || desc="$P/task.md"
  case "$2" in fairness) other="$P/test.patch";; *) other="$P/solution.patch";; esac
  [ -f "$desc" ] && [ -f "$other" ] || return 1
  "$PY" -c 'import hashlib, sys; print(hashlib.sha256(b"".join(open(f, "rb").read() for f in sys.argv[1:])).hexdigest())' "$desc" "$other"
}
reuse_reports() {  # reuse_reports <out> <kind> <tag> <key>: copy the reports of the newest round with this key
  local out="$1" kind="$2" tag="$3" key="$4" mark old s usable samples=("")
  [ "$kind" != sq ] || samples=(a b)
  while IFS= read -r mark; do
    [ "$(cat "$mark")" = "$key" ] || continue
    old=${mark##*/inputs-"$kind"-}; old=${old%.txt}
    usable=1
    for s in "${samples[@]}"; do [ -s "$out/$kind-$old$s.json" ] || usable=0; done
    [ "$usable" = 1 ] || continue
    if [ "$old" != "$tag" ]; then
      for s in "${samples[@]}"; do cp -f "$out/$kind-$old$s.json" "$out/$kind-$tag$s.json" || return 1; done
      echo "reusing $kind reports of round $old (same input bytes)"
    fi
    printf '%s\n' "$key" > "$out/inputs-$kind-$tag.txt"
    return 0
  done < <(ls -t "$out"/inputs-"$kind"-*.txt 2>/dev/null)
  return 1
}
requested() {  # requested <kind>: is this check in the round? (reads main's checks)
  local k
  for k in "${checks[@]}"; do case "$k" in "$1"|"$1"-a|"$1"-b) return 0;; esac; done
  return 1
}
main() {
  [ "$#" -ge 1 ] || return 2
  local T tag c check sample report rc failed=0
  T=$(cd "$1" && pwd) || return 2; tag="${2:-r1}"
  shift; [ "$#" = 0 ] || shift
  local checks=() aggregate=1
  if [ "${1:-}" = --check ]; then
    aggregate=0
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
  local kind key missing=()
  for kind in fairness sq dq; do
    key=$(input_key "$T" "$kind") || key=""
    if requested "$kind"; then
      [ -z "$key" ] || printf '%s\n' "$key" > "$out/inputs-$kind-$tag.txt"
    elif [ "$aggregate" = 1 ]; then
      { [ -n "$key" ] && reuse_reports "$out" "$kind" "$tag" "$key"; } || missing+=("$kind")
    fi
  done
  [ "$aggregate" = 0 ] || requested ar || [ -s "$out/ar-$tag.json" ] || missing+=(ar)
  if [ "${#missing[@]}" -gt 0 ]; then
    echo "round $tag stopped before running: no reports to use for: ${missing[*]}. Add them to this round." >&2
    return 2
  fi
  local audits=()
  for c in "${checks[@]}"; do case "$c" in ref-audit-*) audits=(--ref-audits);; esac; done
  "$PY" "$OLYMPUS_TOOLS/summarize.py" "$out" "$tag" --declare "${audits[@]}" || return 2
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
      local statuses=("${PIPESTATUS[@]}")
      rc=${statuses[0]}
      [ "${statuses[1]}" = 0 ] && [ -s "$out/summary-$tag.md" ] || rc=1
    else
      report="$out/$check-$sample.json"
      rm -f "$report" "$out/$check-${sample}_cx.json"
      if [ "$check" = ar ] || [ "$check" = verify ]; then
        if ! "$PY" "$OLYMPUS_TOOLS/summarize.py" "$out" "$tag" --merge-sq; then
          failed=1; continue
        fi
      fi
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
