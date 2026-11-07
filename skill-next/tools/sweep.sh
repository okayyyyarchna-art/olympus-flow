#!/usr/bin/env bash
# Tracked: sweep.sh <task> <tag> --lane ar|sq|ref-a|ref-b (one blocking job and report).
# Convenience aggregate: sweep.sh <task> [tag] runs all lanes serially and waits for every child.
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
source "$OLYMPUS_LIB/inputs.sh"
main() {
  [ "$#" -ge 1 ] || return 2
  local T tag brief lane report rc failed=0
  T=$(cd "$1" && pwd) || return 2; tag="${2:-s1}"
  shift; [ "$#" = 0 ] || shift
  local lanes=(ar sq ref-a ref-b)
  if [ "$#" -gt 0 ]; then
    [ "$#" = 2 ] && [ "$1" = --lane ] || return 2
    lanes=("$2")
  fi
  require_files "$OLYMPUS_TOOLS/../replicas/sweep-brief.md" || return 2
  for lane in "${lanes[@]}"; do
    case "$lane" in
      ar|sq) ;;
      ref-a|ref-b) bash "$OLYMPUS_TOOLS/replica.sh" "$T" ref-audit "sw${tag}${lane#ref-}" --validate-only || return 2;;
      *) echo "unknown lane: $lane" >&2; return 2;;
    esac
  done
  mkdir -p "$T/eval/claude2" "$T/eval/replica"
  for lane in "${lanes[@]}"; do
    brief="$T/eval/sweep-brief-$tag-$lane.md"
    { cat "$OLYMPUS_TOOLS/../replicas/sweep-brief.md"; printf '\nTask folder: %s\n' "$T"; } > "$brief"
    bash "$OLYMPUS_LIB/check_codex_brief.sh" "$brief" >/dev/null || return 3
    case "$lane" in
      ar|sq)
        report="$T/eval/claude2/pkg-$lane-sweep-$tag.md"; rm -f "$report"
        C2_SUFFIX="sweep-$tag" bash "$OLYMPUS_LIB/claude2_run.sh" "$lane" "$T" pkg "$brief" high > "$T/eval/claude2/sweep-$tag-$lane.log" 2>&1
        rc=$?;;
      ref-*)
        report="$T/eval/replica/ref-audit-sw${tag}${lane#ref-}.json"; rm -f "$report"
        bash "$OLYMPUS_TOOLS/replica.sh" "$T" ref-audit "sw${tag}${lane#ref-}" > "$T/eval/sweep-$tag-$lane.log" 2>&1
        rc=$?;;
    esac
    [ -s "$report" ] || { echo "missing or empty report: $report" >&2; rc=1; }
    [ "$rc" = 0 ] || failed=1
  done
  return "$failed"
}
main "$@"; exit $?