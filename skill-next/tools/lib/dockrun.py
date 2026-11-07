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
lock = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".docker.lock")
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
