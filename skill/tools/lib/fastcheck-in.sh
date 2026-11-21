#!/bin/bash
# fastcheck-in.sh <part> <args...>: the container side of fastcheck.sh. Mounts: /s = the task folder, read-only
# (pkg/test.patch, pkg/solution.patch, eval/wrong/kept, profile.json); /kit = the kit's tools folder, read-only;
# /o = the output folder. /app = the repository of the image.
#   snapshot <TS>                    root: apply the tests, run base mode on the clean repository, keep the result
#   twouser <tag> <TS> <SOL> <0|1>   root in the snapshot: swap in changed hidden tests; uid 1000: apply the solution,
#                                    new mode, then base mode (the after run, when 1; a failing case re-runs alone x3)
#   light <tag>                      uid 1000 in the task image: T1 on the clean repository, lint, kept wrong versions
#   odduid <tag>                     a uid with no passwd entry: new mode with the solution
part=$1; shift
set -u
G=(git -c 'safe.directory=*')
LEAVES="python3 /kit/lib/junit_leaves.py"
bad=0
now() { date +%s; }
profile() { # profile <dotted.key>: a string of /s/profile.json, or nothing
  python3 - "$1" <<'EOF' 2>/dev/null
import json, sys
d = json.load(open("/s/profile.json"))
for k in sys.argv[1].split("."):
    d = d.get(k, {}) if isinstance(d, dict) else {}
print(d if isinstance(d, str) else "")
EOF
}
case $part in
snapshot)
  TS=$1
  cd /app && "${G[@]}" apply /s/pkg/test.patch || { echo "   TEST APPLY FAILED"; exit 1; }
  chmod +x test.sh
  mkdir -p /snap && cp /s/pkg/test.patch /snap/test.patch && sha256sum test.sh | cut -c1-64 > /snap/testsh.sha
  t0=$(now); ./test.sh base --output_path /snap/base.xml > /snap/base.log 2>&1; rc=$?
  echo "   baseline (root, clean repository + tests, base mode): exit $rc in $(( $(now) - t0 ))s"
  cp /snap/base.xml "/o/base-$TS.xml" 2>/dev/null || { echo "   no baseline report"; exit 1; }
  $LEAVES /snap/base.xml list-fails | head -12 | sed 's/^/   FAIL /'
  exit $rc ;;
twouser)
  TAG=$1; TS=$2; SOL=$3; NEED=$4
  cd /app || exit 1
  if ! cmp -s /snap/test.patch /s/pkg/test.patch; then
    "${G[@]}" apply -R /snap/test.patch && "${G[@]}" apply /s/pkg/test.patch || { echo "   TEST SWAP FAILED"; exit 1; }
    chmod +x test.sh
    [ "$(sha256sum test.sh | cut -c1-64)" = "$(cat /snap/testsh.sha)" ] || { echo "   test.sh differs from the snapshot's: take a new snapshot"; exit 1; }
    echo "   root swapped in the hidden tests of $TAG"
  fi
  id -u 1000 > /dev/null 2>&1 || { groupadd -g 1000 model && useradd -m -u 1000 -g 1000 -s /bin/bash model; } || exit 1
  u=$(id -nu 1000)
  as() { su "$u" -s /bin/bash -c "cd /app && $1"; }
  as "git -c safe.directory=/app apply /s/pkg/solution.patch" > /tmp/apply.log 2>&1; rc=$?
  echo "   solution apply (uid 1000): exit $rc"; [ $rc -eq 0 ] || { head -5 /tmp/apply.log; exit 1; }
  t0=$(now); as "./test.sh new --output_path /tmp/new.xml" > /tmp/new.log 2>&1; rc=$?
  echo "   new mode with the solution (uid 1000): exit $rc in $(( $(now) - t0 ))s"
  cp /tmp/new.xml "/o/new-$TAG.xml" 2>/dev/null || { echo "   no new-mode report"; exit 1; }
  $LEAVES /tmp/new.xml pass | sed 's/^/   /'; [ "${PIPESTATUS[0]}" -eq 0 ] && [ $rc -eq 0 ] || bad=1
  if [ "$NEED" = 1 ]; then
    t0=$(now); as "./test.sh base --output_path /tmp/after.xml" > /tmp/after.log 2>&1; rc=$?
    echo "   after run: base mode with the solution (uid 1000): exit $rc in $(( $(now) - t0 ))s"
    if [ $rc -eq 0 ]; then
      cp /tmp/after.xml "/o/after-$TS-$SOL.xml"
    else
      bad=1; cp /tmp/after.xml "/o/after-$TS-$SOL.failed.xml" 2>/dev/null
      ONE=$(profile commands.one); MOD=$(profile toolchain.module)
      [ -n "$ONE" ] || echo "   profile.json names no one-test command (commands.one): failing cases not re-run alone"
      $LEAVES /tmp/after.xml list-fails | head -10 | while IFS=$'\t' read -r cls name; do
        [ -n "$ONE" ] || { echo "   FAIL $cls $name"; continue; }
        pkg=${cls#"$MOD"/}; cmd=${ONE//NAME/$name}; cmd=${cmd//PACKAGE/$pkg}
        for i in 1 2 3; do as "$cmd" > /tmp/retry.log 2>&1; echo "   RETRY alone $i/3 ($cmd): exit $?"; done
      done
    fi
  else
    echo "   after run: saved result of test.sh $TS + solution $SOL is used"
  fi
  exit $bad ;;
light)
  TAG=$1
  export HOME=/tmp
  rm -rf /tmp/w && cp -a /app /tmp/w && cd /tmp/w || exit 1
  "${G[@]}" apply /s/pkg/test.patch || { echo "   TEST APPLY FAILED"; exit 1; }
  chmod +x test.sh
  t0=$(now); ./test.sh new --output_path /tmp/t1.xml > /tmp/t1.log 2>&1; rc=$?
  echo "   T1: clean repository + tests, new mode: exit $rc (want nonzero) in $(( $(now) - t0 ))s"
  $LEAVES /tmp/t1.xml fail | sed 's/^/   /'; [ "${PIPESTATUS[0]}" -eq 0 ] && [ $rc -ne 0 ] || bad=1
  "${G[@]}" apply /s/pkg/solution.patch || { echo "   SOLUTION APPLY FAILED"; exit 1; }
  LINT=$(profile commands.lint)
  if [ -n "$LINT" ]; then
    t0=$(now); bash -c "$LINT" > /tmp/lint.log 2>&1; rc=$?
    echo "   lint ($LINT): exit $rc in $(( $(now) - t0 ))s"; tail -5 /tmp/lint.log | sed 's/^/      /'; [ $rc -eq 0 ] || bad=1
  else
    echo "   lint: profile.json names no commands.lint (not run)"
  fi
  if ls /s/eval/wrong/kept/*.py > /dev/null 2>&1; then
    CMD=""; [ -f /s/eval/wrong/kept/cmd.txt ] && CMD=$(head -1 /s/eval/wrong/kept/cmd.txt)
    t0=$(now); python3 /kit/wrong_versions.py /s/eval/wrong/kept /tmp/w ${CMD:+--cmd "$CMD"} | sed 's/^/   /'
    [ "${PIPESTATUS[0]}" -eq 0 ] || bad=1
    echo "   kept wrong versions in $(( $(now) - t0 ))s"
  else
    echo "   kept wrong versions: none in eval/wrong/kept"
  fi
  exit $bad ;;
odduid)
  TAG=$1
  export HOME=/tmp
  cd /app && "${G[@]}" apply /s/pkg/test.patch /s/pkg/solution.patch || { echo "   APPLY FAILED (is /app writable for every user?)"; exit 1; }
  chmod +x test.sh
  t0=$(now); ./test.sh new --output_path /tmp/n.xml > /tmp/n.log 2>&1; rc=$?
  echo "   new mode with the solution as uid $(id -u) (no passwd entry): exit $rc in $(( $(now) - t0 ))s"
  $LEAVES /tmp/n.xml pass | sed 's/^/   /'; [ "${PIPESTATUS[0]}" -eq 0 ] && [ $rc -eq 0 ] || bad=1
  exit $bad ;;
*) echo "unknown part $part" >&2; exit 2 ;;
esac
