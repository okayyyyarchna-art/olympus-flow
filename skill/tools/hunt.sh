#!/usr/bin/env bash
# S0 when the user gives a repository: eligibility facts, clone at the tip and one shared brief. It prints the
# Codex and second-account lane commands; the coordinator starts them and the in-process lane at once, then decides
# with hunt.md (part B).
#   bash hunt.sh <github-url-or-owner/repo> ["already taken: one line per task to exclude"]
# Output: $OLYMPUS_SEAMS_ROOT/work/<repo>-<yyyymmdd>/ (clone, brief.md, eval/facts.txt)
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
src="${1#https://github.com/}"; src="${src%.git}"; src="${src%/}"
exclude="${2:-none}"
name="${src##*/}"
# one folder per hunt: an earlier clone may back a task's git worktree (vet base/), so it is never reused
W="$OLYMPUS_SEAMS_ROOT/work/$name-$(date +%Y%m%d)"; mkdir -p "$W/eval"
here="$(cd "$(dirname "$0")/.." && pwd)"

# eligibility (platform repo rules): 500+ stars, recent commit, permissive licence, not on our lists
gh repo view "$src" --json stargazerCount,licenseInfo,pushedAt,defaultBranchRef,primaryLanguage,isArchived \
  -q '"stars \(.stargazerCount) | licence \(.licenseInfo.spdxId // "see LICENSE") | pushed \(.pushedAt) | branch \(.defaultBranchRef.name) | \(.primaryLanguage.name) | archived \(.isArchived)"' \
  | tee "$W/eval/facts.txt"
merged=$(gh api "search/issues?q=repo:$src+is:pr+is:merged+merged:>$(date -d '-1 year' +%F 2>/dev/null || date -v-1y +%F)&per_page=1" -q .total_count 2>/dev/null)
echo "merged PRs last 12 months: ${merged:-?} (faust ~73; much higher = more novelty risk)" | tee -a "$W/eval/facts.txt"
for l in DISALLOWED-REPOS.csv REJECTED-REPOS.md already_built_locally.md; do
  [ -f "$OLYMPUS_SHARED_ROOT/$l" ] || echo "LIST MISSING: $OLYMPUS_SHARED_ROOT/$l (the platform's list from the owner, or your own owner/repo lines); the list rule is NOT checked" | tee -a "$W/eval/facts.txt"
done
grep -i -h "$src" "$OLYMPUS_SHARED_ROOT/DISALLOWED-REPOS.csv" "$OLYMPUS_SHARED_ROOT/REJECTED-REPOS.md" \
  "$OLYMPUS_SHARED_ROOT/already_built_locally.md" 2>/dev/null | sed 's/^/ON A LIST: /' | tee -a "$W/eval/facts.txt"

[ -d "$W/repo/.git" ] || git clone -q "https://github.com/$src.git" "$W/repo"
branch=$(git -C "$W/repo" rev-parse --abbrev-ref HEAD); commit=$(git -C "$W/repo" rev-parse HEAD)
lang=$(gh repo view "$src" --json primaryLanguage -q .primaryLanguage.name 2>/dev/null)

"$PY" - "$here/templates/hunt-brief.md" "$W/brief.md" "$src" "$lang" "$W/repo" "$branch" "$commit" "$exclude" <<'EOF'
import sys
tpl, out, repo, lang, clone, branch, commit, exclude = sys.argv[1:9]
s = open(tpl, encoding="utf-8").read()
for k, v in {"{REPO}": repo, "{LANG}": lang, "{CLONE}": clone, "{BRANCH}": branch, "{COMMIT}": commit[:12],
             "{EXCLUDE}": exclude}.items():
    s = s.replace(k, v)
open(out, "w", encoding="utf-8", newline="\n").write(s)
EOF
bash "$OLYMPUS_LIB/check_codex_brief.sh" "$W/brief.md" >/dev/null || { echo "brief has flagged words; reword the exclude line" >&2; exit 3; }

# The three lanes run at the same time, each as the coordinator's own tracked background call (vet 2026-11-13: run
# here one after the other, the claude2 lane waited the whole Codex lane for nothing; neither lane uses Docker).
rm -f "$W/eval/codex/hunt.md" "$W/eval/claude2/hunt-free.md"
echo "prepared: $W (brief.md, eval/facts.txt, repo at $commit)"
echo "start these two as separate tracked background calls, and the in-process lane (read-only) with the same brief:"
echo "  bash \"$OLYMPUS_LIB/codex_job.sh\" \"$W\" hunt \"$W/brief.md\" medium search   # -> $W/eval/codex/hunt.md"
echo "  bash \"$OLYMPUS_LIB/claude2_run.sh\" free \"$W\" hunt \"$W/brief.md\" high       # -> $W/eval/claude2/hunt-free.md"
echo "  in-process lane report -> $W/eval/inprocess-hunt.md"
}
main "$@"
