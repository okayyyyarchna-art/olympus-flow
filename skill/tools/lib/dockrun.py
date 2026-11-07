"""Run docker within the machine profile's shared slot limit.

usage: MSYS_NO_PATHCONV=1 python eval/dockrun.py run --rm ... <image> <cmd...>
Waits for a free slot (DOCKRUN_SLOTS, default from machine profile; set 1 while solvers run), then runs ``docker <args>``.
Slot 0 is the byte the earlier one-slot version locked, so a run still waiting from that version keeps its turn.
"""
try:
    import msvcrt
except ImportError:  # macOS / Linux
    msvcrt = None
    import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from machine import load, slot_limit

try:
    machine = load()
    SLOTS = slot_limit(machine["docker"]["slots"], os.environ.get("DOCKRUN_SLOTS"))
except ValueError as exc:
    sys.exit(f"machine: {exc}")
cleanup = any(arg in ("prune", "rm", "rmi") for arg in sys.argv[1:3])
if cleanup and machine["docker"]["cleanup_allowed"] is not True:
    sys.exit("machine profile forbids Docker cleanup")
env = dict(os.environ)
if machine["os"] == "windows":
    env["MSYS_NO_PATHCONV"] = "1"
# Disk floor before anything that adds images or layers: C: reached 0 GB on 2026-11-07 (product builds plus build
# cache), Docker died mid-proof. DOCKRUN_MIN_FREE_GB overrides the 20 GB default.
if sys.argv[1:2] and sys.argv[1] in ("build", "buildx", "pull", "load", "import"):
    import shutil
    need = float(os.environ.get("DOCKRUN_MIN_FREE_GB", "20"))
    free = shutil.disk_usage(os.path.expanduser("~")).free / 2**30
    if free < need:
        sys.exit(f"dockrun: {free:.1f} GB free, below the {need:g} GB floor: prune old images and build cache "
                 "(docker system df), compact the Docker disk, or set DOCKRUN_MIN_FREE_GB")
# One lock file per machine, shared by every copy of this script (task tools and product tools), so all Docker
# jobs on the machine share the same slots.
lock = os.environ.get("DOCKRUN_LOCK") or os.path.join(os.path.expanduser("~"), ".olympus", "docker.lock")
os.makedirs(os.path.dirname(lock), exist_ok=True)
with open(lock, "a+") as f:
    slot = None
    while slot is None:
        for candidate in range(SLOTS):
            try:
                f.seek(candidate)
                if msvcrt:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.lockf(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB, 1, candidate)
                slot = candidate
                break
            except OSError:
                continue
        if slot is None:
            time.sleep(1)
    try:
        code = subprocess.call(["docker", *sys.argv[1:]], env=env)
    finally:
        f.seek(slot)
        if msvcrt:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.lockf(f.fileno(), fcntl.LOCK_UN, 1, slot)
sys.exit(code)
