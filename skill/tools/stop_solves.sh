#!/usr/bin/env bash
# Stop every solve of one task with its whole process tree (codex/claude children included).
#   bash stop_solves.sh <task-dir>
# solvers.sh writes each solve's pid to <task>/solves/s<n>/pid; killing only the solvers.sh wrapper (e.g. TaskStop)
# leaves the children running.
set -uo pipefail
T=$(cd "$1" && pwd)
killtree() {  # macOS/Linux: children first, then the process
  local c; for c in $(pgrep -P "$1" 2>/dev/null); do killtree "$c"; done; kill -TERM "$1" 2>/dev/null
}
for f in "$T"/solves/s*/pid; do
  [ -f "$f" ] || continue; pid="$(tr -d '\r\n ' < "$f")"; [ -n "$pid" ] || continue
  if command -v taskkill >/dev/null 2>&1; then taskkill //PID "$pid" //T //F >/dev/null 2>&1 && echo "stopped $(dirname "$f") (tree $pid)"
  else killtree "$pid" && echo "stopped $(dirname "$f") (tree $pid)"; fi
  rm -f "$f"
done
