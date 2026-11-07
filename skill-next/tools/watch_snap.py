"""Print one line per platform item (checks, precheck stages, runs) from `olympus problems view --json` on stdin."""
import json
import sys

try:
    d = json.load(sys.stdin)
except Exception:  # noqa: BLE001
    print("ERROR")
    sys.exit()
c = d.get("checks") or {}
active = 0
lines = []
for k, v in (c.get("dynamicChecks") or {}).items():
    if k.startswith("_") or not isinstance(v, dict):
        continue
    o = v.get("output") or {}
    verdict = o.get("verdict") or (o.get("evaluation") or {}).get("verdict") or o.get("outcome") or ""
    if v.get("status") in ("pending", "running"):
        active += 1
    lines.append(f"check|{k}|{v.get('status')}|{verdict}|{v.get('completedAt')}")
for s in c.get("stages") or []:
    for x in s.get("checks") or []:
        lines.append(f"pre|{s.get('stageId')}/{x.get('name') or x.get('key')}|{x.get('status')}")
# readiness criteria carry the Scope Gate (not in stages/dynamicChecks); "pending" there also means "not run yet",
# so only running/queued counts as active
for x in (c.get("readiness") or {}).get("criteria") or []:
    if x.get("status") in ("running", "queued", "in_progress"):
        active += 1
    lines.append(f"ready|{x.get('id')}|{x.get('status')}|{x.get('verdict') or ''}")
runs = (d.get("runs") or {}).get("agentRuns") or []
runs = runs if isinstance(runs, list) else list(runs.values())
for r in runs:
    if r.get("status") in ("pending", "running"):
        active += 1
    verdict = r.get("verdict") or (r.get("output") or {}).get("verdict") or ""
    lines.append(f"run|{r.get('id')}|{r.get('status')}|{verdict}")
for line in sorted(set(lines)):
    print(line)
print(f"ACTIVE|{active}")
