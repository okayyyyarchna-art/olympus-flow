#!/usr/bin/env bash
# Read-only pull of one challenge's platform state (latest version): checks, runs, criteria, reviews, digest,
# plus each run's solution patch and failing-test lines. Never triggers anything.
#   bash pull.sh <challenge-id> <out-dir> [--runs]
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
export OLYMPUS_NO_UPDATE_CHECK=1
id="$1"; out="$2"; mkdir -p "$out"
here="$(cd "$(dirname "$0")" && pwd)"
olympus problems view "$id" --json > "$out/view-$id.json" || { echo "pull failed (login? olympus auth status)" >&2; exit 1; }
olympus problems version list "$id" --json > "$out/versions-$id.json" 2>/dev/null
"$PY" "$here/digest.py" "$out" "$out/digest" >/dev/null && echo "digest: $out/digest"
if [ "${3:-}" = "--runs" ]; then
  "$PY" - "$out/view-$id.json" <<'EOF' | tr -d '\r' > "$out/runs.txt"
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
r = d["runs"]["agentRuns"]; r = r if isinstance(r, list) else list(r.values())
for x in r:
    if not x.get("stale") and x.get("jobId"):
        print(x["id"], x.get("taskAgentCodename"), x.get("verdict") or (x.get("output") or {}).get("verdict"))
EOF
  while read -r rid fam verdict; do
    d="$out/runs/$rid"; mkdir -p "$d"; echo "$fam $verdict" > "$d/verdict.txt"
    olympus runs artifact "$id" "$rid" --key solutionPatch > "$d/solution.patch" 2>/dev/null
    olympus runs artifact "$id" "$rid" --key testLog > "$d/testlog.txt" 2>/dev/null
    # Go/testscript failure lines first (a run's first failing script line), then the generic tail
    { grep -E -e '--- FAIL|^FAIL|FAIL: |\.txtar:[0-9]+:' "$d/testlog.txt"
      echo "--- other error lines"
      grep -E -i 'FAILED|failures:|panicked|assert|Error' "$d/testlog.txt" | tail -60; } > "$d/failures.txt"
  done < "$out/runs.txt"
  echo "runs: $(wc -l < "$out/runs.txt") in $out/runs/"
fi
# The FP panel's notes (judges, adjudicator) are shown only in the web UI; the CLI has the status alone.
if grep -q '"id": *"noFalsePositives"' "$out/view-$id.json" &&    grep -A3 '"id": *"noFalsePositives"' "$out/view-$id.json" | grep -Eq '"status": *"(warn|fail)"'; then
  echo "FP panel: warn/fail -> ask the owner to paste the panel notes from the web UI"
fi
