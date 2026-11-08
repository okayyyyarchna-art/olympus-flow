import importlib.util
import os
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import machine


def load_proof():
    spec = importlib.util.spec_from_file_location("proof", TOOLS / "proof.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(os.environ, {"OLYMPUS_MACHINE": "windows.example"}):
        spec.loader.exec_module(module)
    return module


class Capacity(unittest.TestCase):
    def test_overrides_only_lower_and_reject_invalid_values(self):
        for limit in (2, 8):
            for value, expected in ((None, limit), ("1", 1), ("999", limit)):
                self.assertEqual(machine.slot_limit(limit, value), expected)
            for value in ("0", "-1", "x", "1.5", ""):
                with self.assertRaises(ValueError):
                    machine.slot_limit(limit, value)

    def test_proof_cleanup_requires_literal_permission(self):
        proof = load_proof()
        for allowed in (False, True):
            with patch.dict(proof.MACHINE["docker"], {"cleanup_allowed": allowed}), patch.object(proof, "docker") as docker:
                proof.cleanup_build_cache()
                self.assertEqual(docker.call_count, int(allowed))

    def test_dockrun_enforces_override_and_blocks_cleanup_before_docker(self):
        with patch.dict(os.environ, {"OLYMPUS_MACHINE": "windows.example", "DOCKRUN_SLOTS": "999"}), \
             patch.object(machine, "load", return_value={"docker": {"slots": 2, "cleanup_allowed": False}}), \
             patch.object(sys, "argv", ["dockrun", "builder", "prune", "-af"]), \
             patch("subprocess.call") as call:
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(TOOLS / "lib/dockrun.py"))
            self.assertIn("forbids Docker cleanup", str(stopped.exception))
            call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
