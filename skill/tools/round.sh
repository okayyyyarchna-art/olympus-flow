#!/usr/bin/env bash
# S5 replica round (all checks on GPT Sol 6.1 medium): fairness, sq twice (the site SQ samples a different angle per run),
# dq in parallel, then ar, then verify on all findings. About 25-30 min wall.
#   bash round.sh <task-dir> [tag] [checks...]     default checks: fairness sq dq ar (S6b gate runs, tags g1 and g2)
# optional ref-audit runs twice (tags <tag>ra, <tag>rb); S5 sweep.sh already runs it, so it is not a default here
# Targeted re-run after a fix (S6): bash round.sh <task> r2 sq ar   (solution changed)
#                                    bash round.sh <task> r2 fairness ar (tests changed)
# Expects <task-dir>/pkg/{description.md,test.patch,solution.patch,Dockerfile} (or those at the task root) and repo/ (pinned commit + both patches).
set -uo pipefail
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
PY="$(command -v python || command -v python3)"  # macOS has only python3
T=$(cd "$1" && pwd); tag="${2:-r1}"; shift 2 2>/dev/null || shift $#
checks=("$@"); [ ${#checks[@]} -gt 0 ] || checks=(fairness sq dq ar)
R="$(cd "$(dirname "$0")" && pwd)/replica.sh"
mkdir -p "$T/eval/replica"; log="$T/eval/replica/round-$tag.log"; : > "$log"
# machine-wide limit: at most ROUND_SLOTS (default 2) replica rounds at once across all sessions (Codex rate limits)
slots="$HOME/OSS/shipd/.round-slots"; mkdir -p "$slots"; slot=""
while [ -z "$slot" ]; do
  for i in $(seq 1 "${ROUND_SLOTS:-2}"); do
    if mkdir "$slots/$i" 2>/dev/null; then slot="$slots/$i"; echo "$T $tag $$" > "$slot/owner"; break; fi
    # a slot left by a dead round (owner pid gone) is freed
    pid=$(awk '{print $3}' "$slots/$i/owner" 2>/dev/null); [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null && rm -rf "${slots:?}/$i"
  done
  [ -n "$slot" ] || { echo "waiting for a free replica-round slot..." >&2; sleep 30; }
done
trap 'rm -rf "${slot:?}"' EXIT
want() { local c; for c in "${checks[@]}"; do [ "$c" = "$1" ] && return 0; done; return 1; }
pids=()
if want fairness; then bash "$R" "$T" fairness "$tag" >> "$log" 2>&1 & pids+=($!); fi
if want sq; then
  bash "$R" "$T" sq "${tag}a" >> "$log" 2>&1 & pids+=($!)
  bash "$R" "$T" sq "${tag}b" >> "$log" 2>&1 & pids+=($!)
fi
if want dq; then bash "$R" "$T" dq "$tag" >> "$log" 2>&1 & pids+=($!); fi
if want ref-audit; then
  bash "$R" "$T" ref-audit "${tag}ra" >> "$log" 2>&1 & pids+=($!)
  bash "$R" "$T" ref-audit "${tag}rb" >> "$log" 2>&1 & pids+=($!)
fi
for p in "${pids[@]}"; do wait "$p"; done
# ar reads <check>-<tag>.json; give it the sq run with more issues under the plain tag
out="$T/eval/replica"
if want sq; then
  "$PY" - "$out" "$tag" <<'EOF'
import json, os, shutil, sys
out, tag = sys.argv[1], sys.argv[2]
best = None
for t in (tag + "a", tag + "b"):
    p = os.path.join(out, f"sq-{t}.json")
    if os.path.exists(p):
        try:
            n = len(json.load(open(p, encoding="utf-8")).get("issues") or [])
        except Exception:
            continue
        if best is None or n > best[0]:
            best = (n, p)
if best:
    shutil.copy(best[1], os.path.join(out, f"sq-{tag}.json"))
EOF
fi
if want ar; then bash "$R" "$T" ar "$tag" >> "$log" 2>&1; fi
# second pass: a fresh verifier keeps or drops every sq/fairness/ar finding (calibration 2026-11-05: deep sq and ar
# find the real Highs and also reading-dependent / combination corners; the verifier removes the latter)
bash "$R" "$T" verify "$tag" >> "$log" 2>&1
"$PY" "$(dirname "$0")/summarize.py" "$T/eval/replica" "$tag" | tee "$T/eval/replica/summary-$tag.md"
}
main "$@"; exit $?
