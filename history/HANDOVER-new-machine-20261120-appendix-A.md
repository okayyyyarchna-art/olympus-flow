# Appendix A: scripts of the fast hand-over check (as used on vet 6)

These are the working scripts from the origin machine, for a Go repository whose task image has the repository at
/app. Paths, the image name, the test file pattern (`*_test.go`), the hidden test file names and the Go commands are
specific to that task: adapt them. `dockrun.py` is a small wrapper around `docker run` that takes a lock so only
`DOCKRUN_SLOTS` heavy containers run at once; plain `docker run` works when nothing else is running. The eval folder
is mounted read-only at /s, the output folder at /o. Patches are named eval/test-<tag>.patch and eval/ref-<tag>.patch.

Use: `run.sh <tag> snapshot` once per test.sh, then `run.sh <tag>` for every hand-over.

## fast/fp.py (the three fingerprints)

```python
"""fp.py <tag>: the three fingerprints the fast hand-over check keys on, printed as `TS HT SOL`.

TS  = test.sh as eval/test-<tag>.patch adds it (base mode runs no added test file, so the clean-repo base run
      depends on test.sh alone);
HT  = the hidden test files of that patch;
SOL = eval/ref-<tag>.patch.
"""
import hashlib
import pathlib
import re
import sys

ev = pathlib.Path(__file__).resolve().parents[1]
tag = sys.argv[1]
test = (ev / f"test-{tag}.patch").read_bytes()
parts = re.split(rb"(?m)^(?=diff --git )", test)
runner = [p for p in parts if p.startswith(b"diff --git a/test.sh ")]
hidden = [p for p in parts if p and not p.startswith(b"diff --git a/test.sh ")]
assert len(runner) == 1, "test.sh is not in the test patch exactly once"
for p in hidden:
    name = p.split(b"\n", 1)[0].decode()
    assert name.endswith("_test.go"), f"the test patch holds a file that base mode may run or read: {name}"


def h(chunks):
    return hashlib.sha256(b"".join(chunks)).hexdigest()[:12]


print(h(runner), h(hidden), h([(ev / f"ref-{tag}.patch").read_bytes()]))
```

## fast/run.sh (the orchestrator)

```bash
#!/bin/bash
# run.sh <tag> [snapshot]: the hand-over checks of eval/test-<tag>.patch + eval/ref-<tag>.patch, each run only when
# its inputs changed.
#   baseline (root, clean repo + tests, base mode)   depends on test.sh           -> snapshot image olympus-snap:<TS>
#   after run (uid 1000, solution, base mode)         depends on test.sh, solution -> out/after-<TS>-<SOL>.xml
#   new mode with the solution, T1, lint, kept wrong  depend on the hidden tests   -> run every time
# `run.sh <tag> snapshot` takes the baseline snapshot (once per test.sh). The verdict is the platform's verifySolution
# set check over the three junit files. A full cold two-user run (eval/harbor-replay.sh) is repeated only when
# test.sh itself changes.
tag=$1
T=<TASK_DIR>
IMG=olympus-proof:3c622cf9f19988922dfaadc6dfd50a9198a24dc64b5e8d2e059a558f14adf120
DR="<KIT_DIR>/tools/lib/dockrun.py"
EV='<TASK_DIR>/eval'
OUT="$T/eval/fast/out"; mkdir -p "$OUT"
read -r TS HT SOL < <(python "$T/eval/fast/fp.py" "$tag" | tr -d '\r') || exit 2
[ -n "$SOL" ] || { echo "no fingerprints"; exit 2; }
SNAP="olympus-snap:$TS"
echo "== $tag: test.sh $TS, hidden tests $HT, solution $SOL  $(date +%H:%M)"
if [ "${2:-}" = snapshot ]; then
  docker rm -f "snap-$TS" > /dev/null 2>&1
  MSYS_NO_PATHCONV=1 python "$DR" run --name "snap-$TS" --network none -v vetgo0:/tmp/gocache -v "$EV:/s:ro" -v "$EV\\fast\\out:/o" "$IMG" bash /s/fast/snapshot-in.sh "$tag" "$TS"; rc=$?
  if [ $rc -eq 0 ]; then docker commit "snap-$TS" "$SNAP" > /dev/null && echo "snapshot $SNAP taken"; fi
  docker rm -f "snap-$TS" > /dev/null 2>&1
  exit $rc
fi
docker image inspect "$SNAP" > /dev/null 2>&1 || { echo "no baseline snapshot for test.sh $TS: run.sh $tag snapshot (once per test.sh)"; exit 3; }
need_after=1; [ -f "$OUT/after-$TS-$SOL.xml" ] && need_after=0
t0=$(date +%s)
MSYS_NO_PATHCONV=1 python "$DR" run --rm --network none -v vetgo1000:/tmp/gocache -v "$EV:/s:ro" -v "$EV\\fast\\out:/o" "$SNAP" bash /s/fast/twouser-in.sh "$tag" "$TS" "$SOL" "$need_after"
echo "-- two-user part: $(( $(date +%s) - t0 ))s"
t1=$(date +%s)
MSYS_NO_PATHCONV=1 python "$DR" run --rm --network none --user 1000:1000 -e HOME=/tmp -v vetgo1000:/tmp/gocache -v "$EV:/s:ro" "$IMG" bash /s/fast/light-in.sh "$tag"
echo "-- light part: $(( $(date +%s) - t1 ))s"
t2=$(date +%s)
# the hidden tests with the solution as a user id that has no account record and no warm cache
MSYS_NO_PATHCONV=1 python "$DR" run --rm --network none --user 12345:12345 -e HOME=/tmp -v "$EV:/s:ro" "$IMG" bash -c "cd /app && export HOME=/tmp GOCACHE=/tmp/gocache && git -c safe.directory=/app apply /s/test-$tag.patch /s/ref-$tag.patch && ./test.sh new --output_path /tmp/n.xml > /tmp/n.log 2>&1; echo \"new as uid 12345: exit \$?\"; python3 /s/tqv3/leaves.py /tmp/n.xml reference"
echo "-- odd-user part: $(( $(date +%s) - t2 ))s"
if [ -f "$OUT/after-$TS-$SOL.xml" ]; then
  python "$T/eval/junit-sets.py" "$OUT/base-$TS.xml" "$OUT/new-$tag.xml" "$OUT/after-$TS-$SOL.xml"
else
  echo "VERDICT FAIL: the after run did not pass (see the RETRY lines)"
fi
echo "== total $(( $(date +%s) - t0 ))s  $(date +%H:%M)"
```

## fast/snapshot-in.sh (in the container, as root: the baseline of the clean repository)

```bash
#!/bin/bash
# snapshot-in.sh <tag>: runs as root in the task image. The platform's first verifySolution step: root applies the
# tests and runs base mode on the clean repository. The container is then committed as the baseline snapshot of this
# test.sh, so later checks start from the state root left (file owners, restored fixtures) without running it again.
tag=$1
set -u
cd /app && git apply "/s/test-$tag.patch" || { echo "TEST APPLY FAILED"; exit 1; }
chmod +x test.sh
mkdir -p /snap && cp "/s/test-$tag.patch" /snap/test.patch && sha256sum test.sh | cut -c1-64 > /snap/testsh.sha
start=$(date +%s)
./test.sh base --output_path /snap/base.xml > /snap/base.log 2>&1; rc=$?
echo "baseline (root, clean + tests, base): exit $rc in $(( $(date +%s) - start ))s"
grep -E '^\s*--- FAIL|^FAIL' /snap/base.log | head
cp /snap/base.xml "/o/base-$2.xml" 2>/dev/null
exit $rc
```

## fast/twouser-in.sh (in the snapshot: root swaps the hidden tests, uid 1000 applies the solution and runs new, then base)

```bash
#!/bin/bash
# twouser-in.sh <tag> <TS> <SOL> <need_after 0|1>: runs as root in the baseline snapshot of this test.sh. The rest of
# the platform's verifySolution: root has applied the tests and run base mode (the snapshot); uid 1000 applies the
# solution, runs new mode, then base mode again. Changed hidden tests are swapped in by root first. The after run is
# left out when its result for this test.sh + solution is already saved (it runs no hidden test).
tag=$1; TS=$2; SOL=$3; need_after=$4
set -u
cd /app || exit 1
if ! cmp -s /snap/test.patch "/s/test-$tag.patch"; then
  git apply -R /snap/test.patch && git apply "/s/test-$tag.patch" || { echo "TEST SWAP FAILED"; exit 1; }
  chmod +x test.sh
  [ "$(sha256sum test.sh | cut -c1-64)" = "$(cat /snap/testsh.sha)" ] || { echo "test.sh differs from the snapshot's: take a new snapshot"; exit 1; }
  echo "root swapped in the hidden tests of $tag"
fi
id 1000 >/dev/null 2>&1 || { groupadd -g 1000 model 2>/dev/null; useradd -u 1000 -g 1000 -m model 2>/dev/null; }
u=$(id -nu 1000)
as() { su "$u" -s /bin/bash -c "cd /app && HOME=/tmp GOCACHE=/tmp/gocache $1"; }
as "git -c safe.directory=/app apply /s/ref-$tag.patch" > /tmp/apply.log 2>&1; echo "solution apply (uid 1000): exit $?"; head -5 /tmp/apply.log
start=$(date +%s)
as "./test.sh new --output_path /tmp/new.xml" > /tmp/new.log 2>&1; echo "new (uid 1000): exit $? in $(( $(date +%s) - start ))s"
cp /tmp/new.xml "/o/new-$tag.xml"
grep -E '\.go:[0-9]+:[0-9]+: ' /tmp/new.log | sort -u | head -8
if [ "$need_after" = 1 ]; then
  start=$(date +%s)
  as "./test.sh base --output_path /tmp/after.xml" > /tmp/after.log 2>&1; rc=$?
  echo "after: base (uid 1000): exit $rc in $(( $(date +%s) - start ))s"
  grep -E '^\s*--- FAIL|^FAIL' /tmp/after.log | head
  if [ $rc -ne 0 ]; then
    # a failing case is run again alone, three times, to tell a wall-clock failure under load from a real one
    for pkg in $(grep -E '^FAIL\s' /tmp/after.log | awk '{print $2}' | grep / | sort -u); do
      for name in $(awk -v p="$pkg" '/^--- FAIL: /{n=$3} /^FAIL\t/{ if ($2==p) print n }' /tmp/after.log | sed 's#/.*##' | sort -u); do
        as "go test -count=3 -run '^$name\$' $pkg" > /tmp/retry.log 2>&1; echo "RETRY alone x3 $pkg $name: exit $?"
      done
    done
    cp /tmp/after.xml "/o/after-$TS-$SOL.failed.xml"
  else
    cp /tmp/after.xml "/o/after-$TS-$SOL.xml"
  fi
else
  echo "after: base: saved result of test.sh $TS + solution $SOL is used"
fi
```

## fast/light-in.sh (as uid 1000: clean-repository failures, format, vet, lint, kept wrong versions)

```bash
#!/bin/bash
# light-in.sh <tag>: runs as uid 1000 in the task image with the warm cache. The checks that depend on the hidden
# tests: every leaf fails on the clean repository and none is skipped; format, vet and lint of the changed Go files;
# each kept wrong version fails the test it names (only that test function runs), and each control passes it.
tag=$1
set -u
export HOME=/tmp GOCACHE=/tmp/gocache GOLANGCI_LINT_CACHE=/tmp/gocache/lint GOFLAGS=-buildvcs=false
G=(git -c safe.directory=*)
rm -rf /tmp/w && cp -a /app /tmp/w && cd /tmp/w || exit 1
"${G[@]}" apply "/s/test-$tag.patch" || { echo "TEST APPLY FAILED"; exit 1; }
start=$(date +%s)
./test.sh new --output_path /tmp/t1.xml > /tmp/t1.log 2>&1; echo "T1 clean + tests, new: exit $? (want 1) in $(( $(date +%s) - start ))s"
python3 /s/tqv3/leaves.py /tmp/t1.xml base
grep -E '\.go:[0-9]+:[0-9]+: ' /tmp/t1.log | sort -u | head -5
"${G[@]}" apply "/s/ref-$tag.patch" || { echo "REF APPLY FAILED"; exit 1; }
CHANGED=$(cat "/s/test-$tag.patch" "/s/ref-$tag.patch" | grep '^diff --git' | sed 's#.* b/##' | grep '[.]go$' | sort -u)
# shellcheck disable=SC2086
echo "gofmt: $(gofmt -l $CHANGED | wc -l) unformatted of $(echo "$CHANGED" | wc -l) changed Go files"
# shellcheck disable=SC2086
gofmt -l $CHANGED | head -5
DIRS=$(for f in $CHANGED; do echo "./$(dirname "$f")/"; done | sort -u)
start=$(date +%s)
# shellcheck disable=SC2086
go vet $DIRS > /tmp/vet.log 2>&1 && echo "go vet: ok in $(( $(date +%s) - start ))s" || { echo "go vet: FAILED"; head -10 /tmp/vet.log; }
start=$(date +%s)
# shellcheck disable=SC2086
golangci-lint run --new-from-rev=HEAD --timeout 15m $DIRS > /tmp/lint.log 2>&1; echo "lint: exit $? in $(( $(date +%s) - start ))s"; tail -6 /tmp/lint.log
"${G[@]}" add -A > /dev/null && "${G[@]}" -c user.name=check -c user.email=check@example.com commit -qm "$tag" > /dev/null
start=$(date +%s)
for s in /s/wrong/kept/*.py; do
  k=$(basename "$s" .py)
  kind=$(python3 -c "import runpy,sys; print(runpy.run_path(sys.argv[1], run_name='x')['KIND'])" "$s")
  expect=$(python3 -c "import runpy,sys; print(runpy.run_path(sys.argv[1], run_name='x').get('EXPECT',''))" "$s")
  [ "$kind" = held ] && { echo "kept $k: held, not run"; continue; }
  python3 "$s" > /tmp/apply.log 2>&1 || { echo "kept $k: APPLY FAILED: $(tail -1 /tmp/apply.log)"; "${G[@]}" checkout -- .; continue; }
  top=${expect%%/*}
  if [ -n "$top" ]; then
    pkg=$(dirname "$(grep -l "^func $top(" internal/engine/prscan_prs9_test.go internal/overview/prscan_prs9_test.go internal/plugins/sinks/cyclonedx/prscan_prs9_test.go internal/cmd/report/prscan_prs9_test.go internal/plugins/controls/lockfile/prscan_prs9_test.go | head -1)")
    go test -count=1 -run "^$top\$" "./$pkg/" > /tmp/k.log 2>&1; rc=$?
  else
    go test -count=1 -run 'Prs9$' ./internal/engine/ > /tmp/k.log 2>&1; rc=$?
  fi
  fails=$(grep -E -- '--- FAIL' /tmp/k.log | awk '{print $3}' | sort -u | tr '\n' ' ' | cut -c1-200)
  verdict=BAD
  if [ "$kind" = wrong ] && [ $rc -ne 0 ] && echo "$fails" | grep -qF "$expect"; then verdict=ok; fi
  if [ "$kind" = control ] && [ $rc -eq 0 ]; then verdict=ok; fi
  echo "kept $k ($kind): $verdict; exit $rc; failing: $fails"
  grep -E 'build failed|\.go:[0-9]+:[0-9]+:' /tmp/k.log | head -2
  "${G[@]}" checkout -- . ; "${G[@]}" clean -fdq
done
echo "kept wrong versions in $(( $(date +%s) - start ))s"
echo "== light done"
```

## junit-sets.py (the Verify Solution set check over the three JUnit files)

```python
#!/usr/bin/env python3
"""junit-sets.py <baseline.xml> <new.xml> <after.xml>: the set checks of the platform's verifySolution.

baseline = base mode with the tests applied and no solution; new = new mode with the solution; after = base mode
with the solution. It fails when the baseline has a failure, a new case does not pass, a new case is also a
baseline case, an after case is in neither the baseline pass set nor the new set and is not skipped
(after_extras_not_skipped), or a baseline pass does not pass in the after run.
"""
import sys
import xml.etree.ElementTree as ET


def cases(path):
    out = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        cid = tc.get("classname", "") + "." + tc.get("name", "")
        if tc.find("failure") is not None or tc.find("error") is not None:
            out[cid] = "fail"
        elif tc.find("skipped") is not None:
            out[cid] = "skip"
        else:
            out[cid] = "pass"
    return out


base, new, after = (cases(p) for p in sys.argv[1:4])
p2p = {i for i, s in base.items() if s == "pass"}
bad = 0


def report(title, ids):
    global bad
    print(f"{title}: {len(ids)}")
    for i in sorted(ids)[:20]:
        print("  -", i)
    bad += len(ids)


print(f"baseline {len(base)} cases: pass {len(p2p)} skip {sum(s == 'skip' for s in base.values())}")
print(f"new {len(new)} cases; after {len(after)} cases")
report("baseline failures", {i for i, s in base.items() if s == "fail"})
report("new cases not passing", {i for i, s in new.items() if s != "pass"})
report("new cases that the baseline also has", set(new) & set(base))
report("after extras (not p2p, not f2p, not skipped)",
       {i for i, s in after.items() if s != "skip" and i not in p2p and i not in new})
report("p2p cases not passing in the after run", {i for i in p2p if after.get(i) != "pass"})
print("VERDICT", "PASS" if bad == 0 else "FAIL")
sys.exit(1 if bad else 0)
```

## tqv3/leaves.py (counts the leaves of a JUnit file)

```python
"""leaves.py <junit.xml> <label>: count the junit leaves of a test.sh run and list the ones that pass (label base) or
fail (label reference), with the skipped ones."""
import sys
import xml.etree.ElementTree as ET

path, label = sys.argv[1], sys.argv[2]
cases = list(ET.parse(path).getroot().iter("testcase"))
bad = lambda c: c.find("failure") is not None or c.find("error") is not None
skip = [c.get("name") for c in cases if c.find("skipped") is not None]
fail = [c.get("name") for c in cases if bad(c)]
passed = [c.get("name") for c in cases if not bad(c) and c.find("skipped") is None]
print(f"{label}: {len(cases)} leaves, {len(passed)} pass, {len(fail)} fail, {len(skip)} skipped")
for n in (passed if label == "base" else fail)[:20]:
    print(f"   {'PASSES ON BASE' if label == 'base' else 'FAILS'}: {n}")
for n in skip[:5]:
    print(f"   skipped: {n}")
```

## make-patches.sh (builds the two patches from the working tree)

```bash
#!/bin/bash
# make-patches.sh <tag>: writes eval/test-<tag>.patch and eval/ref-<tag>.patch from the repo working tree.
# Solution = every changed path except the hidden test files and the two fixtures antivirus removed.
set -e
T=<TASK_DIR>; cd "$T/repo"
# New files must be intent-to-add, or git diff leaves them out.
git ls-files --others --exclude-standard | xargs -r git add -N
tfiles="internal/cmd/report/prscan_prs9_test.go internal/engine/prscan_prs9_test.go internal/overview/prscan_prs9_test.go internal/plugins/sinks/cyclonedx/prscan_prs9_test.go internal/plugins/controls/lockfile/prscan_prs9_test.go test.sh"
files=$(git status --short | awk '{print $2}' | grep -v -x -F -e test/acceptance/scripts/controls/agent-config/hidden-task.txtar -e test/evasion/cases/variants/polinrider-os-task.txtar $(for f in $tfiles; do echo "-e $f"; done))
git diff HEAD --binary -- $tfiles > "$T/eval/test-$1.patch"
git diff HEAD --binary -- $files > "$T/eval/ref-$1.patch"
echo "test files: $(grep -c '^diff --git' "$T/eval/test-$1.patch")  solution files: $(grep -c '^diff --git' "$T/eval/ref-$1.patch")"
```

## wrong/kept/saveduse-integrity.py (a kept wrong version (template))

```python
"""Platform TQ 2026-11-20 (2): two manifests that differ only in the integrity hash of a package keep no fields of their own, so a report read back shows one hash for both."""
KIND = 'wrong'
EXPECT = 'TestSavedReportShowsEachManifestAsTheScanSawItPrs9'
EDITS = [('report/report.go', ' && u.Integrity == v.Integrity &&', ' &&')]


def main():
    for path, old, new in EDITS:
        with open(path, encoding="utf-8", newline="") as f:
            src = f.read()
        assert src.count(old) == 1, (path, src.count(old))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src.replace(old, new, 1))


if __name__ == "__main__":
    main()
```
