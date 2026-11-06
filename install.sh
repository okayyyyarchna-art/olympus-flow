#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
py="${OLYMPUS_BOOTSTRAP_PYTHON:-$(command -v python3 || command -v python)}"
"$py" - "$root" "$@" <<'PY'
import argparse
import difflib
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1])
sys.path.insert(0, str(root / "skill/tools"))
from machine import load, profile_path

ap = argparse.ArgumentParser(description="Install Olympus Flow; existing different files need --force.")
ap.add_argument("--profile", help="profile name or JSON path (required if machine/local.json is missing)")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--force", action="store_true")
ap.add_argument("--home", type=Path, default=Path.home(), help="installation home (default: current user's home)")
args = ap.parse_args(sys.argv[2:])
local = root / "machine/local.json"
try:
    selected = local if local.exists() else profile_path(args.profile)
    load(str(selected))
except ValueError as exc:
    ap.error(str(exc))
target = args.home.expanduser().resolve() / ".claude"
skill = target / "skills/olympus-flow"
files = []
for src in sorted((root / "skill").rglob("*")):
    if src.is_file() and "__pycache__" not in src.parts and src.name != ".docker.lock":
        files.append((src, skill / src.relative_to(root / "skill")))
for src in sorted((root / "agents").glob("*.md")):
    files.append((src, target / "agents" / src.name))
for src in sorted((root / "machine").glob("*")):
    if src.is_file() and src.name != "local.json":
        files.append((src, skill / "machine" / src.name))
if not local.exists():
    files.append((selected, local))
files.append((selected, skill / "machine/local.json"))
changes, conflicts = [], []
for src, dst in files:
    new = src.read_bytes()
    if dst.exists():
        old = dst.read_bytes()
        if old == new:
            continue
        delta = list(difflib.ndiff(old.decode("utf-8", "replace").splitlines(),
                                 new.decode("utf-8", "replace").splitlines()))
        plus = sum(s.startswith("+ ") for s in delta)
        minus = sum(s.startswith("- ") for s in delta)
        print(f"CHANGE {dst} (+{plus}/-{minus} lines)")
        conflicts.append(dst)
    else:
        print(f"ADD    {dst} ({len(new)} bytes)")
    changes.append((src, dst))
print(f"Diff summary: {len(changes)} files, {len(conflicts)} existing files differ.")
sys.stdout.flush()
if conflicts and not args.force:
    print("Existing files require --force; no files will be written.")
    sys.exit(0 if args.dry_run else 2)
if args.dry_run:
    print("Dry run: no files written.")
    sys.exit(0)
for src, dst in changes:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    shutil.copymode(src, dst)
print(f"Installed Olympus Flow at {skill}")
PY
