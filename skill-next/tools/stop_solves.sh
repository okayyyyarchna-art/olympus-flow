#!/usr/bin/env bash
# Stop every solve of one task with its whole process tree (codex/claude children included).
#   bash stop_solves.sh <task-dir>
# solvers.sh writes each solve's pid to <task>/solves/s<n>/pid; killing only the solvers.sh wrapper (e.g. TaskStop)
# leaves the children running.
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/machine.sh" || exit 2
T=$(cd "$1" && pwd)
for f in "$T"/solves/s*/pid; do
  [ -f "$f" ] || continue; pid="$(tr -d '\r\n ' < "$f")"; [[ "$pid" =~ ^[1-9][0-9]*$ ]] || continue
  if [ "$OLYMPUS_OS" = windows ]; then taskkill //PID "$pid" //T //F >/dev/null 2>&1 && echo "stopped $(dirname "$f") (tree $pid)"
  else kill -TERM -- "-$pid" && echo "stopped $(dirname "$f") (tree $pid)"; fi
  rm -f "$f"
done
