#!/usr/bin/env bash
# repo_traits.sh <repo dir>: the gnmi-fingerprint metrics for a Go repository (Go only)
d="$1"; cd "$d" || exit 1
src=$(find . -name '*.go' ! -name '*_test.go' ! -path './vendor/*' ! -name '*.pb.go' ! -path '*/proto/*')
pk=$(printf '%s\n' $src | xargs -n1 dirname | sort -u | wc -l | tr -d ' ')
loc=$(cat $src 2>/dev/null | grep -cv '^\s*\(//.*\)\?$')
ifs=$(grep -h -E '^type [A-Z][A-Za-z0-9]* interface' $src | awk '{print $2}' | sort -u)
nif=$(printf '%s\n' $ifs | grep -c .)
# exported interfaces whose method set nothing in the repo (non-test) appears to implement: crude = interface name never
# used as an assignment target/var type outside its own declaration AND first method name never defined as a method elsewhere
unimpl=""
for i in $ifs; do f=$(grep -l -E "^type $i interface" $src | head -1); m=$(awk "/^type $i interface/{f=1;next} f&&/^}/{exit} f&&/^\t[A-Z][A-Za-z0-9]*\(/{sub(/^\t/,\"\");sub(/\(.*/,\"\");print;exit}" "$f"); [ -z "$m" ] && continue; n=$(grep -h -E "^func \([a-z]+ \*?[A-Za-z0-9]+\) $m\(" $src | wc -l | tr -d ' '); [ "$n" = 0 ] && unimpl="$unimpl $i"; done
nowv=$(grep -h -E '^\s*(var\s+)?(Now|now|timeNow|nowFunc|clock)\s*=\s*time\.Now' $src | wc -l | tr -d ' ')
seams=$(grep -h -E 'io\.Reader|io\.Writer|http\.RoundTripper|func\(\) time\.Time|context\.Context' $src | wc -l | tr -d ' ')
stubs=$(grep -n -i -E 'unimplemented|not implemented|not supported|TODO' $src | grep -v -i 'Unimplemented[A-Z]' | wc -l | tr -d ' ')
hostt=$(grep -l -E 'net\.Listen\(|ListenAndServe|grpc\.NewServer|net\.Dial\(' $(find . -name '*_test.go') 2>/dev/null | wc -l | tr -d ' ')
tt=$(find . -name '*_test.go' ! -path './vendor/*' | wc -l | tr -d ' ')
c12=$(git log --since=2025-10-06 --oneline -- $(printf '%s\n' $src | head -500) 2>/dev/null | wc -l | tr -d ' ')
deps=$(grep -c '^\s' go.mod 2>/dev/null)
echo "pkgs=$pk srcLOC=$loc ifaces=$nif unimpl_ifaces=[$unimpl ] Now_vars=$nowv io/ctx_seams=$seams stub_lines=$stubs host_tests=$hostt/$tt src_commits_12m=$c12 go.mod_lines=$deps"
