#!/usr/bin/env bash
# Replay the reference and every staged agent patch against a package's test.patch, using the package's own test.sh.
# usage: replay_patches.sh <pkg-dir> <clean-repo-dir> <image> <patches-dir> [mode]
#   <pkg-dir>      holds test.patch and solution.patch (the candidate you are about to paste)
#   <clean-repo-dir> a git clone of the pinned commit (only read; copied inside the container)
#   <image>        the package image (deps installed; network not needed)
#   <patches-dir>  *.patch files from stage_agent_runs.py --out
#   [mode]         test.sh mode to run: new (default) or base
# Prints "<name>: <passed>/<total> new" plus the failing test names. Language-agnostic: parses the JUnit XML that
# test.sh writes. Works from macOS bash and Windows Git Bash (MSYS_NO_PATHCONV + cygpath -m).
set -uo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../machine.sh" || exit 2
pkg="$1"; repo="$2"; img="$3"; patches="$4"; mode="${5:-new}"
# a git worktree (base/) has a .git FILE pointing outside the mount: replay a real clone of the same commit instead
if [ -f "$repo/.git" ]; then
  tmp="$(mktemp -d)"; c="$(git -C "$repo" rev-parse HEAD)"
  git clone -q --no-checkout "$repo" "$tmp/r" && git -C "$tmp/r" checkout -q "$c" || { echo "clone of $repo failed" >&2; exit 2; }
  repo="$tmp/r"; trap 'rm -rf "$tmp"' EXIT
fi
host() { if [ "$OLYMPUS_OS" = windows ]; then machine_host "$(cd "$1" && pwd)"; else (cd "$1" && pwd); fi; }
inner='
set -u
cp -r /repo /tmp/r && cd /tmp/r
run() { n=$1; f=$2
  git checkout -q . && git clean -qfd
  git apply /pkg/test.patch && git apply "$f" 2>/dev/null || { echo "$n: APPLY FAIL"; return; }
  timeout -k 30 1800 bash test.sh --output_path /tmp/out.xml '"$mode"' > /tmp/log 2>&1
  python3 - "$n" <<PY
import sys, xml.etree.ElementTree as ET
n = sys.argv[1]
try:
    root = ET.parse("/tmp/out.xml").getroot()
except Exception as exc:
    print(f"{n}: NO JUNIT ({exc})"); raise SystemExit
cases = list(root.iter("testcase"))
bad = [c.get("name") for c in cases if c.find("failure") is not None or c.find("error") is not None]
print(f"{n}: {len(cases) - len(bad)}/{len(cases)} '"$mode"'")
for b in bad: print(f"      FAILED {b}")
PY
}
run reference /pkg/solution.patch
for f in /patches/*.patch; do run "$(basename "$f" .patch)" "$f"; done
'
# Through the machine profile's shared Docker slot lock.
"${OLYMPUS_DOCKER_ENV[@]}" "$PY" "$(machine_host "$OLYMPUS_LIB/dockrun.py")" run --rm --network none \
  -v "$(host "$pkg")":/pkg:ro -v "$(host "$repo")":/repo:ro -v "$(host "$patches")":/patches:ro \
  --entrypoint bash "$img" -c "$inner"
