import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("precheck", Path(__file__).parents[1] / "tools/precheck.py")
precheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(precheck)


class DescriptionLimit(unittest.TestCase):
    def test_boundaries_and_platform_ceiling(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            pkg = Path(tmp)
            for name in ("test.patch", "solution.patch"):
                (pkg / name).write_text("")
            for words, status in ((249, "PASS"), (250, "FAIL"), (251, "FAIL"), (1001, "FAIL")):
                with self.subTest(words=words):
                    # Exercise the actual CLI check, including both hyphen and slash splitting.
                    (pkg / "description.md").write_text("a-b/c " + "word " * (words - 3))
                    output = io.StringIO()
                    precheck.results.clear()
                    with patch.object(sys, "argv", ["precheck", tmp]), contextlib.redirect_stdout(output):
                        with self.assertRaises(SystemExit):
                            precheck.main()
                    lines = output.getvalue().splitlines()
                    self.assertTrue(next(x for x in lines if "must be under 250" in x).startswith(status))
                    self.assertTrue(next(x for x in lines if "platform ceiling" in x).startswith(
                        "FAIL" if words > 1000 else "PASS"))


if __name__ == "__main__":
    unittest.main()
