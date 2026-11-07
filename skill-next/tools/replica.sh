#!/usr/bin/env bash
# Run one platform-replica check with Codex (GPT Sol 6.1, medium effort; user rule 2026-11-05).
#   bash replica.sh <task-dir> <fairness|sq|dq|ar> [tag]
# Task dir: pkg/{description.md,test.patch,solution.patch,Dockerfile} (directory contract; files at the task root
# are used when pkg/test.patch is missing), repo/ (pinned commit + both patches),
# optional runs/<id>/{verdict.txt,solution.patch}. Output: <task-dir>/eval/replica/<check>-<tag>.json (+ .md summary).
# Model (user rule 2026-11-05): every check runs on GPT Sol 6.1 at MEDIUM effort. "The model is not the check": the
# hardness comes from the prompts, schemas, break-attempt tables, two sq runs, the verify pass and the knowledge
# catalogs. Override only for an experiment: REPLICA_MODEL / REPLICA_EFFORT. ar and verify read earlier outputs of
# the same tag, so they run last (round.sh orders them).
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
source "$OLYMPUS_LIB/inputs.sh"
[ "$#" -ge 2 ] || { echo "usage: replica.sh <task-dir> <check> [tag] [--validate-only]" >&2; exit 2; }
T=$(cd "$1" && pwd); check="$2"; tag="${3:-r1}"
here=$(cd "$(dirname "$0")/.." && pwd)
case "$check" in
  fairness|sq|dq|ar|verify|fp-audit|ref-audit) ;; *) echo "unknown check $check" >&2; exit 2 ;;
esac
model="${REPLICA_MODEL:-gpt-6.1-sol}"; effort="${REPLICA_EFFORT:-medium}"
# strict false-pass audits (passers and the reference) run at HIGH effort (user rule 2026-11-06)
case "$check" in fp-audit|ref-audit) effort="${REPLICA_EFFORT:-high}" ;; esac
# knowledge catalogs (every way the site passed or failed packages, 2026-11-05): which check reads which
case "$check" in
  sq|verify|fp-audit|ref-audit) kb="solution tests" ;; fairness) kb="tests" ;; dq) kb="description" ;; ar) kb="solution tests description" ;;
esac
# calibration baselines: a marker <task-dir>/../.no-kb-<tag> runs this tag without the catalogs (before/after tests)
[ -f "$T/../.no-kb-$tag" ] && kb=""
case "$tag" in *[ab]) [ -f "$T/../.no-kb-${tag%?}" ] && kb="" ;; esac
inputs=("$here/replicas/common.md" "$here/replicas/$check.md")
for k in $kb; do inputs+=("$here/replicas/knowledge/$k.md"); done
require_files "${inputs[@]}" || exit 2
[ "${4:-}" != --validate-only ] || exit 0
out="$T/eval/replica"; mkdir -p "$out/prompts"
cp "$here/replicas/common.md" "$here/replicas/$check.md" "$out/prompts/" || exit 2
kbl=""; for k in $kb; do
  cp "$here/replicas/knowledge/$k.md" "$out/prompts/kb-$k.md" || exit 2
  kbl="$kbl $out/prompts/kb-$k.md"
done
P="$T/pkg"; [ -f "$P/test.patch" ] || P="$T"
desc="$P/description.md"; [ -f "$desc" ] || desc="$P/task.md"
others=""
latest() {  # this tag's result for a check, else its newest result (checks not re-run keep their last result)
  if [ -f "$out/$1-$tag.json" ]; then echo "$out/$1-$tag.json"; else ls -t "$out/$1-"*.json 2>/dev/null | grep -v -E -- "-[^/]*[ab]\.json$" | head -1; fi
}
if [ "$check" = ar ]; then
  for c in fairness sq dq; do f="$(latest $c)"; [ -n "$f" ] && others="$others $f"; done
fi
if [ "$check" = verify ]; then
  for f in "$out"/sq-"$tag"?.json; do [ -f "$f" ] && others="$others $f"; done
  for c in sq fairness ar; do f="$(latest $c)"; [ -n "$f" ] && others="$others $f"; done
fi
brief="$out/brief-$check-$tag.md"
cat > "$brief" <<EOF
# Replica check: $check (tag $tag)

Instructions: read $out/prompts/common.md, then $out/prompts/$check.md, and follow them exactly.
Knowledge (read before judging; every pattern the site has used to pass or fail packages, with its PASS side and
severity calibration; use it to know what to look for AND what the site accepts):$kbl

Task files:
- description: $desc
- test patch: $P/test.patch
- solution patch: $P/solution.patch
- Dockerfile: $P/Dockerfile (may be missing)
- repository with both patches applied: $T/repo/
- agent runs: $( [ -d "$T/runs" ] && echo "$T/runs/" || echo "none" )
- other replica outputs to use: ${others:-none}

Write the JSON result to: $out/$check-$tag.json
Return a short Markdown summary as your final answer (verdict line first).
EOF
bash "$OLYMPUS_LIB/check_codex_brief.sh" "$brief" "$out/prompts/common.md" "$out/prompts/$check.md" $kbl >/dev/null \
  || { echo "brief has flagged words; reword before launch" >&2; exit 3; }
CODEX_MODEL="$model" CODEX_ONE_OFF_EFFORT="$effort" bash "$OLYMPUS_LIB/codex_job.sh" "$T" "replica-$check-$tag" "$brief" "$effort" judge
rc=$?; [ "$rc" = 0 ] || exit "$rc"
cp -f "$T/eval/codex/replica-$check-$tag.md" "$out/$check-$tag.md" 2>/dev/null || true
# codex judge mode asks for a _cx suffix on files it writes; accept that name too
[ -s "$out/$check-$tag.json" ] || { [ -s "$out/$check-${tag}_cx.json" ] && mv -f "$out/$check-${tag}_cx.json" "$out/$check-$tag.json"; }
[ -s "$out/$check-$tag.json" ] && echo "OK $out/$check-$tag.json" || { echo "no JSON written" >&2; exit 1; }
