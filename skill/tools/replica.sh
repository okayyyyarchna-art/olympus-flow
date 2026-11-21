#!/usr/bin/env bash
# Run one platform-replica check with Codex (GPT Sol 6.1, medium effort; owner 2026-11-14, back from GPT Sol 6).
#   bash replica.sh <task-dir> <fairness|sq|dq|ar|verify|fp-audit|ref-audit> [tag] [--validate-only] [--alone] [--site <file>]...
# Task dir: pkg/{description.md,test.patch,solution.patch,Dockerfile} (directory contract; files at the task root
# are used when pkg/test.patch is missing), repo/ (pinned commit + both patches),
# optional runs/<id>/{verdict.txt,solution.patch}. Output: <task-dir>/eval/replica/<check>-<tag>.json (+ .md summary).
# --alone (ar only, BACKLOG #221): run the Auto Review without the fairness, sq and dq outputs of the tag (the judge
# does their parts itself, replicas/ar.md "Alone mode"); --site <file> adds the site's own check results as evidence.
# Model (owner 2026-11-14): every check runs on GPT Sol 6.1 at MEDIUM effort (GPT Sol 6 from 2026-11-13 accepted a defect that 6.1 found, BACKLOG 157). "The model is not the check": the
# hardness comes from the prompts, schemas, break-attempt tables, two sq runs, the verify pass and the knowledge
# catalogs. Override only for an experiment: REPLICA_MODEL / REPLICA_EFFORT. ar and verify read earlier outputs of
# the same tag, so they run last (round.sh orders them).
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
source "$OLYMPUS_LIB/inputs.sh"
[ "$#" -ge 2 ] || { echo "usage: replica.sh <task-dir> <check> [tag] [--validate-only] [--alone] [--site <file>]..." >&2; exit 2; }
T=$(cd "$1" && pwd); check="$2"; tag="${3:-r1}"
here=$(cd "$(dirname "$0")/.." && pwd)
validate=""; alone=""; site_files=""
if [ "$#" -ge 3 ]; then shift 3; else shift "$#"; fi
while [ "$#" -gt 0 ]; do
  case "$1" in
    --validate-only) validate=1 ;;
    --alone) alone=1 ;;
    --site) [ "$#" -ge 2 ] && [ -f "$2" ] || { echo "--site needs an existing file" >&2; exit 2; }; site_files="$site_files $2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done
[ -z "$alone" ] || [ "$check" = ar ] || { echo "--alone applies to the ar check only" >&2; exit 2; }
case "$check" in
  fairness|sq|dq|ar|verify|fp-audit|ref-audit) ;; *) echo "unknown check $check" >&2; exit 2 ;;
esac
model="${REPLICA_MODEL:-gpt-6.1-sol}"; effort="${REPLICA_EFFORT:-medium}"
# Every check runs at medium, the strict false-pass audits (fp-audit, ref-audit) too: owner 2026-11-19, "medium ... for
# any work except in solver" (ends the 2026-11-06 high exception for those two).
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
[ -z "$validate" ] || exit 0
out="$T/eval/replica"; mkdir -p "$out/prompts"
cp "$here/replicas/common.md" "$here/replicas/$check.md" "$out/prompts/" || exit 2
kbl=""; for k in $kb; do
  cp "$here/replicas/knowledge/$k.md" "$out/prompts/kb-$k.md" || exit 2
  kbl="$kbl $out/prompts/kb-$k.md"
done
P="$T/pkg"; [ -f "$P/test.patch" ] || P="$T"
desc="$P/description.md"; [ -f "$desc" ] || desc="$P/task.md"
others=""
if [ "$check" = ar ] && [ -z "$alone" ]; then
  for c in fairness sq dq; do
    require_files "$out/$c-$tag.json" || exit 2
    others="$others $out/$c-$tag.json"
  done
fi
alone_note=""
if [ -n "$alone" ]; then
  alone_note="Run alone (ar.md, Alone mode): no fairness, solution-quality or description replica ran on these bytes; do their
parts yourself from the package and the repository (coverage of each stated requirement, S1 on every real path, P1-P6).
A family without runs in the runs folder is not counted against the package."
fi
site_note=""; [ -z "$site_files" ] || site_note="- the site's own check results on these bytes (evidence, not verdicts):$site_files"
if [ "$check" = verify ]; then
  for f in "$out/sq-${tag}a.json" "$out/sq-${tag}b.json" "$out/fairness-$tag.json" "$out/dq-$tag.json" "$out/ar-$tag.json"; do
    require_files "$f" || exit 2
    others="$others $f"
  done
  for f in "$out/ref-audit-${tag}ra.json" "$out/ref-audit-${tag}rb.json"; do
    [ ! -f "$f" ] || others="$others $f"
  done
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
$site_note
$alone_note
Time box: 40 minutes. Write the report with what is NOT VERIFIED when the box ends, and stop every shell or loop you
started before you finish.

Finding identities for verification: source is the exact report filename without .json.
Use SQ title, AR claim, fairness requirement (coverage) or test name (fairness/concerns),
DQ quote, and reference-audit promise as the finding id. Dispose of every finding at
every severity, including DQ comments and reference-audit gaps when supplied. Each
KEEP/DROP needs evidence; each DROP needs a supported dropReason. Missing dispositions
and every unresolved in-scope finding block the checkpoint, including Medium and Low.

Write the JSON result to: $out/$check-$tag.json
Return a short Markdown summary as your final answer (verdict line first).
EOF
bash "$OLYMPUS_LIB/check_codex_brief.sh" "$brief" "$out/prompts/common.md" "$out/prompts/$check.md" $kbl >/dev/null \
  || { echo "brief has flagged words; reword before launch" >&2; exit 3; }
rm -f "$out/$check-$tag.json" "$out/$check-${tag}_cx.json"
# Every review lane carries a 40 min box (owner 2026-11-19, BACKLOG #186) unless the caller sets one.
CODEX_TIME_BOX_MIN="${CODEX_TIME_BOX_MIN:-40}" CODEX_MODEL="$model" CODEX_ONE_OFF_EFFORT="$effort" bash "$OLYMPUS_LIB/codex_job.sh" "$T" "replica-$check-$tag" "$brief" "$effort" judge
rc=$?; [ "$rc" = 0 ] || exit "$rc"
cp -f "$T/eval/codex/replica-$check-$tag.md" "$out/$check-$tag.md" 2>/dev/null || true
# codex judge mode asks for a _cx suffix on files it writes; accept that name too
[ -s "$out/$check-$tag.json" ] || { [ -s "$out/$check-${tag}_cx.json" ] && mv -f "$out/$check-${tag}_cx.json" "$out/$check-$tag.json"; }
[ -s "$out/$check-$tag.json" ] && echo "OK $out/$check-$tag.json" || { echo "no JSON written" >&2; exit 1; }
