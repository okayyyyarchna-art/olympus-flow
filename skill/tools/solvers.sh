#!/usr/bin/env bash
# Too-easy alarm (launched at the S1 lock, graded at S4): 4 blind solves of the locked description, run while I build.
#   1 Opus via Claude Code on this account, 1 Opus via Claude Code on claude2 (the platform's Vega shape),
#   2 GPT Sol 6.1 via Codex (Orion's model).
#   bash solvers.sh <task-dir> [title]      stop: bash stop_solves.sh <task-dir> (kills every solve tree)
# Each solver gets a fresh clone of <task-dir>/base (pinned, clean) OUTSIDE the task folder and only
# "# <title>\n\n<description>" (pkg/description.md). No Docker slot is held. SOLVE_PATH=<dir> puts a toolchain (a venv's
# Scripts/bin) first on PATH so solvers can run the repo's tests; SOLVE_TIMEOUT_MIN caps each run (default 90).
# Output: <task-dir>/solves/s<n>/{agent.patch,prod_only.patch,meta.txt}. Grade at S4:
#   bash tools/lib/replay_patches.sh <task>/pkg <task>/base <image> <task>/solves/patches
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
# the whole body is one function: bash reads it completely before running, so editing this file while a run
# is in progress cannot break that run (vet 2026-11-06: an edit mid-run garbled the tail of solvers.sh)
main() {
T=$(cd "$1" && pwd); title="${2:-$(head -1 "$T/pkg/title.txt" 2>/dev/null | tr -d '\r')}"
[ -n "$title" ] || title="$(basename "$T")"
name="$(basename "$T")"; mkdir -p "$T/solves/patches"
prompt="$(printf '# %s\n\n%s\n' "$title" "$(tr -d '\r' < "$T/pkg/description.md")")"
cap="${SOLVE_TIMEOUT_MIN:-90}"; RUN="$(date +%m%d%H%M%S)"
CLAUDE_BIN="$OLYMPUS_CLAUDE_BIN"
C2DIR="${CLAUDE2_CONFIG_DIR:-${OLYMPUS_CLAUDE2_CONFIG_DIR:-}}"
[ -z "$C2DIR" ] || C2DIR="$(machine_config "$C2DIR")"
TIMEOUT_GROUP=(); [ "$OLYMPUS_OS" = windows ] || TIMEOUT_GROUP=(--foreground)

finish() {  # $1 = n, $2 = clone; write agent.patch (all but TASK/eval) and prod_only.patch (no tests)
  local n="$1" R="$2" S="$T/solves/s$1"
  # solver scratch folders (a Go module cache in .scratch on vet 2026-11-06) hit Windows long paths: `git add -A`
  # failed and the patch came out empty with no message. Exclude them, allow long paths, and record any add error.
  local adderr; adderr="$(git -C "$R" -c core.longpaths=true add -A -- . ":(exclude).scratch" ":(exclude).cache" ":(exclude)**/gomodcache/**" ":(exclude)**/node_modules/**" 2>&1 >/dev/null)" ||
    echo "ADD FAILED: $(printf %s "$adderr" | tail -2 | tr "\n" " ")" >> "$S/meta.txt"
  # deletions stay out of the patch: antivirus removes malware-like fixtures from clones, and their deleted contents in
  # agent.patch got the patch file itself blocked (vet 2026-11-06); they are listed in meta.txt instead
  git -C "$R" diff --cached --diff-filter=d -- . ':(exclude)TASK.md' ':(exclude)eval' > "$S/agent.patch"
  echo "deleted_files=$(git -C "$R" diff --cached --name-only --diff-filter=D | tr '\n' ' ')" >> "$S/meta.txt"
  local stray; stray="$(find "$R/.." -maxdepth 2 \( -name '*.patch' -o -name '*.diff' \) -newer "$R/TASK.md" 2>/dev/null | head -3)"
  [ -s "$S/agent.patch" ] || echo "EMPTY patch; patch files the solver wrote instead: ${stray:-none}" >> "$S/meta.txt"
  git -C "$R" reset -q
  "$PY" - "$S/agent.patch" "$S/prod_only.patch" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
parts = re.split(r"(?m)^(?=diff --git )", s)
test = re.compile(r"(^|/)(tests?|testdata)/|_test\.(go|rs)\b|(^|/)test_[^/]*\.py\b| b/test\.sh")
keep = [p for p in parts if p.startswith("diff --git") and not test.search(p.split("\n", 1)[0])]
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("".join(keep))
PY
  cp "$S/agent.patch" "$T/solves/patches/s$n.patch"
  echo "finished=$(machine_date) patch_lines=$(wc -l < "$S/agent.patch")" >> "$S/meta.txt"
}

clone() {  # $1 = n -> prints the clone path
  # One fresh folder per run and solve (vet 2026-11-06): "rm -rf <clone>/.." never worked (rm refuses ".."), so old
  # clones were silently reused; a unique folder can never be stale or shared with another run. The clone is ".../work",
  # not ".../repo": codex_job.sh build mode forbids edits to repo/ folders. Old run folders go at task cleanup.
  local R="$OLYMPUS_SOLVER_ROOT/vp-$name-$1-$RUN/work"
  mkdir -p "$(dirname "$R")"
  if [ -e "$R" ]; then echo "clone folder already exists: $R" >&2; return 1; fi
  git clone -q --no-local "$T/base" "$R" && git -C "$R" remote remove origin || return 1
  printf '%s
' "$prompt" > "$R/TASK.md"
  echo "$R"
}

# each solve's subshell records its pid (the Windows pid under Git Bash): stopping solvers.sh alone leaves the
# codex/claude children running (vet 2026-11-06); tools/stop_solves.sh <task> kills every solve's whole process tree
savepid() {
  if [ "$OLYMPUS_OS" = windows ]; then
    cat "/proc/$BASHPID/winpid" 2>/dev/null > "$1/pid" || echo "$BASHPID" > "$1/pid"
  else
    "$PY" -c 'import os; print(os.getpgid(os.getppid()))' > "$1/pid"
  fi
}

opus() {  # $1 = n, $2 = main|claude2
  local n="$1" S="$T/solves/s$1" R; mkdir -p "$S"; R="$(clone "$n")" || { echo "s$n: no clone, solve skipped" >&2; return 1; }
  echo "solver=opus account=$2 started=$(machine_date) clone=$R" > "$S/meta.txt"
  local cfg=()
  if [ "$2" = claude2 ]; then
    [ -n "$C2DIR" ] || { echo "claude2 needs paths.claude2_config_dir" >&2; return 2; }
    cfg=(env CLAUDE_CONFIG_DIR="$C2DIR")
  fi
  ( savepid "$S"; cd "$R" && ${cfg[@]+"${cfg[@]}"} env PATH="${SOLVE_PATH:+$SOLVE_PATH:}$PATH" timeout "${TIMEOUT_GROUP[@]}" --kill-after=60 "${cap}m" \
      "$CLAUDE_BIN" -p "$prompt" --model opus --effort high --permission-mode acceptEdits \
      --append-system-prompt "Work only inside the repository in your current folder and with the task description you were given. Do not read, search or use any file or folder outside this repository; your work is checked for that, and a solve that leaves the repository is discarded." \
      --allowedTools "Bash,Read,Grep,Glob,Write,Edit" --output-format json < /dev/null > "$S/solve.json" 2> "$S/solve.err" )
  finish "$n" "$R"
}

gpt() {  # $1 = n
  local n="$1" S="$T/solves/s$1" R; mkdir -p "$S"; R="$(clone "$n")" || { echo "s$n: no clone, solve skipped" >&2; return 1; }
  echo "solver=gpt-6.1-sol started=$(machine_date) clone=$R" > "$S/meta.txt"
  cat > "$R/../brief.md" <<EOF
Your working folder is $R. Read TASK.md there: it is a request from the maintainers of this repository. Implement it
in the repository in $R the way a strong contributor would (read the code, change it, add or run tests if useful).
Edit the files in $R directly; your work is collected with git diff in $R, so do not write it as a patch or diff
file and do not work in another folder. Use only the repository in $R and the task in TASK.md: do not read, search or
use any file or folder outside $R; your work is checked for that, and a solve that leaves $R is discarded. When done,
return a short summary of what you changed.
EOF
  ( savepid "$S"; CODEX_MODEL=gpt-6.1-sol timeout "${TIMEOUT_GROUP[@]}" --kill-after=60 "${cap}m" bash "$OLYMPUS_LIB/codex_job.sh" "$R" solve "$R/../brief.md" high build \
      > "$S/solve.log" 2>&1 )
  finish "$n" "$R"
}

# SOLVERS="3 4" re-runs only some solves (1, 2 = Opus main/claude2; 3, 4 = GPT)
# Job control gives each background solve its own process group on POSIX hosts.
[ "$OLYMPUS_OS" = windows ] || set -m
for n in ${SOLVERS:-$(seq 1 "$OLYMPUS_SOLVERS")}; do
  case "$n" in 1) opus 1 main & ;; 2) opus 2 claude2 & ;; *) gpt "$n" & ;; esac
done
wait
# watcher (user rule 2026-11-06): a solve may use only its clone, the task text and the repo; only CLEAN solves count
"$PY" "$OLYMPUS_TOOLS/solve_watch.py" "$T"
echo "solves done: $T/solves (grade only the CLEAN ones, solves/watch.md, with replay_patches.sh; then start the FP audits of every passer at once, PIPELINE.md Confirmation schedule)"
}
main "$@"; exit $?
