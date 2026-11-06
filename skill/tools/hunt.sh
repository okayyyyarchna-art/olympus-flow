#!/usr/bin/env bash
# S0 when the user gives a repository: eligibility facts, clone at the tip, one shared brief, and two of the three
# hunt lanes (Codex + claude2) in the background. The coordinator starts the third lane (in-process, read-only) with
# the same brief, then decides with references/hunt.md.
#   bash hunt.sh <github-url-or-owner/repo> ["already taken: one line per task to exclude"]
# Output: ~/OSS/shipd/seams/work/<repo>/ (clone, brief.md, eval/codex/hunt.md, eval/claude2/hunt-free.md)
set -uo pipefail
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
PY="$(command -v python || command -v python3)"  # macOS has only python3
src="${1#https://github.com/}"; src="${src%.git}"; src="${src%/}"
exclude="${2:-none}"
name="${src##*/}"; W="$HOME/OSS/shipd/seams/work/$name"; mkdir -p "$W/eval"
here="$(cd "$(dirname "$0")/.." && pwd)"

# eligibility (platform repo rules): 500+ stars, recent commit, permissive licence, not on our lists
gh repo view "$src" --json stargazerCount,licenseInfo,pushedAt,defaultBranchRef,primaryLanguage,isArchived \
  -q '"stars \(.stargazerCount) | licence \(.licenseInfo.spdxId // "see LICENSE") | pushed \(.pushedAt) | branch \(.defaultBranchRef.name) | \(.primaryLanguage.name) | archived \(.isArchived)"' \
  | tee "$W/eval/facts.txt"
merged=$(gh api "search/issues?q=repo:$src+is:pr+is:merged+merged:>$(date -d '-1 year' +%F 2>/dev/null || date -v-1y +%F)&per_page=1" -q .total_count 2>/dev/null)
echo "merged PRs last 12 months: ${merged:-?} (faust ~73; much higher = more novelty risk)" | tee -a "$W/eval/facts.txt"
grep -i -h "$src" "$HOME/OSS/shipd/DISALLOWED-REPOS.csv" "$HOME/OSS/shipd/REJECTED-REPOS.md" \
  "$HOME/OSS/shipd/already_built_locally.md" 2>/dev/null | sed 's/^/ON A LIST: /' | tee -a "$W/eval/facts.txt"

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
bash "$HOME/OSS/shipd/tools/check_codex_brief.sh" "$W/brief.md" >/dev/null || { echo "brief has flagged words; reword the exclude line" >&2; exit 3; }

# lane 1: Codex (GPT Sol 6.1, search mode reads only the brief)
( bash "$HOME/OSS/shipd/tools/codex_job.sh" "$W" hunt "$W/brief.md" high search > "$W/eval/codex-lane.log" 2>&1 & )
# lane 2: claude2 (second Claude account, Opus)
c2="$HOME/OSS/shipd/tools/claude2_run.sh"; [ "$(uname)" = Darwin ] && [ -f "$HOME/OSS/shipd/tools/claude2_run_mac.sh" ] && c2="$HOME/OSS/shipd/tools/claude2_run_mac.sh"
( bash "$c2" free "$W" hunt "$W/brief.md" high > "$W/eval/claude2-lane.log" 2>&1 & )
echo "started: Codex -> $W/eval/codex/hunt.md ; claude2 -> $W/eval/claude2/hunt-free.md"
echo "next: start the in-process lane (read-only) with $W/brief.md, save its report to $W/eval/inprocess-hunt.md"
}
main "$@"; exit $?
