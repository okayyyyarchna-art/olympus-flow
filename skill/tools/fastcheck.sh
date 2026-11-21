#!/usr/bin/env bash
# fastcheck.sh <task-dir> <image> <tag>: the hand-over check of a package, each part run only when its inputs
# changed (BACKLOG #204). <task-dir>/pkg holds test.patch and solution.patch; <task-dir>/eval/wrong/kept the kept
# wrong versions (run by wrong_versions.py; an optional cmd.txt there is the test command they run with);
# <task-dir>/profile.json (repo_init) may name a lint command (commands.lint) and the one-test command (commands.one,
# NAME and PACKAGE placeholders). <image> is the task image of proof.py (/app = the clean repository). <tag> names
# this run's files under <task-dir>/eval/fast/out and its log lines.
# Fingerprints (lib/patch_fp.py): TS = test.sh as test.patch adds it, HT = the hidden tests, SOL = solution.patch.
#   baseline: root applies the tests and runs base mode on the clean repository  depends on TS       -> snapshot
#             image olympus-snap:<TS>, taken once per test.sh
#   after run: uid 1000 applies the solution after root's run, base mode         depends on TS, SOL -> out/after-<TS>-<SOL>.xml
#   every time: new mode with the solution as uid 1000 and as a uid with no passwd entry; T1 on the clean repository
#   (every leaf fails, none skipped); lint; the kept wrong versions; the verifySolution set check (junit_sets.py)
#   over baseline, new and after. A failing after-run case is re-run alone three times before anything else repeats.
# One container at a time (DOCKRUN_SLOTS=1), each under 20 minutes. Container-side steps: lib/fastcheck-in.sh.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/machine.sh" || exit 2
[ $# -eq 3 ] || { echo "usage: fastcheck.sh <task-dir> <image> <tag>" >&2; exit 2; }
TASK=$1; IMG=$2; TAG=$3
PKG="$TASK/pkg"; OUT="$TASK/eval/fast/out"; mkdir -p "$OUT" || exit 2
read -r TS HT SOL < <("$PY" "$OLYMPUS_LIB/patch_fp.py" "$PKG/test.patch" "$PKG/solution.patch" | tr -d '\r')
[ -n "${SOL:-}" ] || exit 2
SNAP="olympus-snap:$TS"
# host-form paths for Python: with MSYS_NO_PATHCONV=1 (needed so the -v mounts stay untouched) Git Bash no longer
# converts /c/... for a Windows python, so every path Python gets goes through machine_host
DR=(env DOCKRUN_SLOTS=1 DOCKRUN_TIMEOUT=1200 "$PY" "$(machine_host "$OLYMPUS_LIB/dockrun.py")")
[ "$OLYMPUS_OS" != windows ] || DR=(env MSYS_NO_PATHCONV=1 "${DR[@]}")
OUT_HOST=$(machine_host "$OUT")
MOUNTS=(-v "$(machine_host "$TASK"):/s:ro" -v "$(machine_host "$OLYMPUS_TOOLS"):/kit:ro" -v "$(machine_host "$OUT"):/o")
IN=/kit/lib/fastcheck-in.sh
BAD=0; T0=$(date +%s)
echo "== $TAG: test.sh $TS, hidden tests $HT, solution $SOL  $(date +%H:%M)"
step() { # step <name> <command...>: one container; prints its line with the result and the duration
  local name=$1 t0 rc; shift; t0=$(date +%s)
  "$@"; rc=$?
  printf -- '-- %s: %s in %ss\n' "$name" "$([ $rc -eq 0 ] && echo ok || echo "FAIL (exit $rc)")" "$(( $(date +%s) - t0 ))"
  [ $rc -eq 0 ] || BAD=1
  return $rc
}
if docker image inspect "$SNAP" > /dev/null 2>&1; then
  echo "-- baseline: snapshot $SNAP of test.sh $TS reused"
else
  docker rm -f "snap-$TS" > /dev/null 2>&1
  if step "baseline (root, clean repository + tests, base mode)" \
       "${DR[@]}" run --name "snap-$TS" --network none "${MOUNTS[@]}" "$IMG" bash $IN snapshot "$TS"; then
    docker commit "snap-$TS" "$SNAP" > /dev/null && echo "   snapshot $SNAP taken"
  fi
  docker rm -f "snap-$TS" > /dev/null 2>&1
  [ $BAD -eq 0 ] || { echo "== VERDICT FAIL for $TAG: the baseline failed"; exit 1; }
fi
NEED_AFTER=1; [ -f "$OUT/after-$TS-$SOL.xml" ] && NEED_AFTER=0
step "two-user (uid 1000 applies the solution after root's run; new mode$([ $NEED_AFTER = 1 ] && echo ', after run' || echo '; after run saved'))" \
  "${DR[@]}" run --rm --network none "${MOUNTS[@]}" "$SNAP" bash $IN twouser "$TAG" "$TS" "$SOL" "$NEED_AFTER"
step "light (T1 on the clean repository, lint, kept wrong versions; uid 1000)" \
  "${DR[@]}" run --rm --network none --user 1000:1000 -e HOME=/tmp "${MOUNTS[@]}" "$IMG" bash $IN light "$TAG"
step "new mode with the solution as uid 12345 (no passwd entry)" \
  "${DR[@]}" run --rm --network none --user 12345:12345 -e HOME=/tmp "${MOUNTS[@]}" "$IMG" bash $IN odduid "$TAG"
if [ -f "$OUT/after-$TS-$SOL.xml" ]; then
  "$PY" "$(machine_host "$OLYMPUS_TOOLS/junit_sets.py")" "$OUT_HOST/base-$TS.xml" "$OUT_HOST/new-$TAG.xml" "$OUT_HOST/after-$TS-$SOL.xml" | sed 's/^VERDICT/-- junit sets:/'
  [ "${PIPESTATUS[0]}" -eq 0 ] || BAD=1
else
  echo "-- junit sets: not judged, the after run of test.sh $TS + solution $SOL did not pass (see the RETRY lines)"; BAD=1
fi
echo "== VERDICT $([ $BAD -eq 0 ] && echo PASS || echo FAIL) for $TAG in $(( $(date +%s) - T0 ))s  $(date +%H:%M)"
exit $BAD
