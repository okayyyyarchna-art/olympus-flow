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
  PYTHONIOENCODING=utf-8 "$PY" - "$out/view-$id.json" "$out/runs" <<'EOF' | tr -d '\r' > "$out/runs.txt"
import json, os, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
r = d["runs"]["agentRuns"]; r = r if isinstance(r, list) else list(r.values())
for x in r:
    if not x.get("stale") and x.get("jobId"):
        verdict = x.get("verdict") or (x.get("output") or {}).get("verdict")
        # output.environmentBlocker.agentBlameUnfair is the blame flag, also when the evalResult artifact is empty
        os.makedirs(os.path.join(sys.argv[2], x["id"]), exist_ok=True)
        with open(os.path.join(sys.argv[2], x["id"], "output.json"), "w", encoding="utf-8") as f:
            json.dump(x.get("output") or {}, f, indent=2)
        o = x.get("output") or {}
        # sequenceLength (sum of window peaks) and compacted (one compaction = the 256K bar) per run, "-" when absent
        # every empty value prints "-": `IFS=$'\t' read` below collapses consecutive tabs, so an empty verdict (a run
        # still in progress) would shift the later columns into the wrong variables
        print("\t".join("-" if v in (None, "") else str(v) for v in (x["id"], x.get("taskAgentCodename"), verdict,
                                                                     x.get("label"), x.get("batchTag")))
              + "\t" + "\t".join("-" if o.get(k) is None else str(o.get(k)) for k in ("sequenceLength", "compacted")))
EOF
  # Folders are keyed by run id: labels such as "Orion #6" repeat across batches (vet task 3).
  while IFS=$'\t' read -r rid fam verdict label batch seqlen compacted; do
    d="$out/runs/$rid"; mkdir -p "$d"
    printf '%s %s\nlabel: %s\nbatch: %s\nsequenceLength: %s\ncompacted: %s\n' "$fam" "$verdict" "$label" "$batch" "$seqlen" "$compacted" > "$d/verdict.txt"
    olympus runs artifact "$id" "$rid" --key solutionPatch > "$d/solution.patch" 2>/dev/null
    # The evaluator's verdict file: its agent_blame_unfair decides the Fair task and environment-blocker gates.
    olympus runs artifact "$id" "$rid" --key evalResult > "$d/evalResult.json" 2>/dev/null
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
