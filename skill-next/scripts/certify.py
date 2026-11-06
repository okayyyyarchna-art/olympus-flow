#!/usr/bin/env python3
"""Read-only artifact fingerprints and JUnit integrity checks; not a semantic judge."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


class Invalid(ValueError):
    """The supplied evidence does not satisfy the mechanical contract."""


def require(condition, message):
    if not condition:
        raise Invalid(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(paths, metadata=None):
    files = {}
    for path in paths:
        path = Path(path)
        key = path.as_posix()
        require(key not in files, f"duplicate input path: {key}")
        files[key] = digest(path.read_bytes())
    require(files, "no fingerprint inputs")
    inputs = {"files": files, "metadata": metadata,
              "checker_sha256": digest(Path(__file__).read_bytes())}
    return {"key": digest(canonical(inputs).encode()), "inputs": inputs}


def patch_paths(data):
    # --numstat validates unified-diff syntax without modifying files or the index.
    result = subprocess.run(["git", "apply", "--numstat", "-z", "--"],
                            input=data, capture_output=True, check=False)
    require(result.returncode == 0,
            "malformed patch: " + result.stderr.decode("utf-8", errors="replace"))
    paths = []
    for record in result.stdout.decode("utf-8").split("\0"):
        if not record:
            continue
        parts = record.split("\t", 2)
        require(len(parts) == 3 and parts[2], "unsupported numstat path record")
        name = parts[2]
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts and ".git" not in path.parts
                and "\\" not in name and not re.match(r"^[A-Za-z]:", name),
                f"unsafe patch path: {name}")
        require(name not in paths, f"repeated patch path: {name}")
        paths.append(name)
    require(paths, "empty patch")
    return paths


def package_check(folder):
    folder = Path(folder)
    blobs = {}
    for name in ("description.md", "test.patch", "solution.patch", "Dockerfile"):
        data = (folder / name).read_bytes()
        require(data.strip(), f"empty artifact: {name}")
        require(b"\r" not in data and b"\0" not in data, f"CR/NUL bytes in {name}")
        require(not data.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM in {name}")
        data.decode("utf-8")
        blobs[name] = data
    tests = patch_paths(blobs["test.patch"])
    solution = patch_paths(blobs["solution.patch"])
    require("test.sh" in tests, "test.patch must include test.sh")
    overlap = set(tests) & set(solution)
    require(not overlap, "test/solution path overlap: " + ", ".join(sorted(overlap)))
    patch = blobs["test.patch"].decode("utf-8")
    section = re.search(r"(?ms)^diff --git a/test\.sh b/test\.sh\n.*?(?=^diff --git |\Z)", patch)
    require(section is not None, "test.sh must use a normal git diff header")
    modes = re.findall(r"^(?:new file mode|new mode) (\d+)$", section[0], re.M)
    require(not modes or modes[-1] == "100755", "test.sh must be executable (100755)")
    require("deleted file mode" not in section[0], "test.sh is deleted")
    description = blobs["description.md"].decode("utf-8")
    words = len([word for word in re.split(r"[\s\-/]+", description.strip()) if word])
    review = ["Apply both patches on pristine pin and inspect resulting modes/source.",
              "Semantic quality, ASCII policy and current platform limits require separate checks."]
    if not modes:
        review.append("No mode change recorded: verify test.sh inherits 100755 at the pin.")
    return {"mechanical": "PASS", "sha256": {k: digest(v) for k, v in blobs.items()},
            "site_style_words": words, "test_paths": tests, "solution_paths": solution,
            "review": review}


def id_set(values, label, allow_empty=False):
    require(isinstance(values, list), f"{label} must be a JSON array")
    require(all(isinstance(v, str) and v.strip() == v and v for v in values),
            f"{label} contains an empty or invalid ID")
    require(allow_empty or values, f"{label} is empty")
    require(len(set(values)) == len(values), f"duplicate {label}")
    return set(values)


def local_tag(element):
    return element.tag.rsplit("}", 1)[-1]


def inspect_junit(data, expected, expect, exit_code, allowed_skips=()):
    expected = id_set(expected, "expected IDs")
    allowed_skips = id_set(list(allowed_skips), "allowed skips", allow_empty=True)
    require(allowed_skips <= expected, "skip allowlist contains unexpected IDs")
    require(expect in ("pass", "fail"), "expect must be pass or fail")
    require(not (expect == "fail" and allowed_skips), "fail expectation cannot allow skips")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise Invalid(f"invalid JUnit XML: {exc}") from exc
    require(local_tag(root) in ("testsuite", "testsuites"), "invalid JUnit root")
    rows = {}
    element_results = {}
    for case in root.iter():
        if local_tag(case) != "testcase":
            continue
        name, classname = case.get("name", ""), case.get("classname", "")
        require(name.strip(), "nameless test case")
        key = f"{classname}::{name}" if classname else name
        require(key not in rows, f"duplicate result ID: {key}")
        outcomes = [child for child in case if local_tag(child) in ("failure", "error", "skipped")]
        kinds = {local_tag(child) for child in outcomes}
        require(len(kinds) <= 1, f"contradictory result types: {key}")
        status = next(iter(kinds), "pass")
        if status in ("failure", "error"):
            diagnostic = " ".join(child.get("message", "") + " " + "".join(child.itertext())
                                  for child in outcomes)
            require(diagnostic.strip(), f"missing failure diagnostic: {key}")
        rows[key] = status
        element_results[id(case)] = status
    require(rows, "zero test cases")
    require(set(rows) == expected,
            f"ID mismatch: missing={sorted(expected-set(rows))}, extra={sorted(set(rows)-expected)}")
    # Verify optional aggregate counts, including nested suites and namespaced XML.
    for suite in root.iter():
        if local_tag(suite) not in ("testsuite", "testsuites"):
            continue
        statuses = [element_results[id(case)] for case in suite.iter()
                    if local_tag(case) == "testcase"]
        counts = {"tests": len(statuses), "failures": statuses.count("failure"),
                  "errors": statuses.count("error"), "skipped": statuses.count("skipped")}
        for attr, actual in counts.items():
            if attr in suite.attrib:
                try:
                    declared = int(suite.get(attr))
                except ValueError as exc:
                    raise Invalid(f"noninteger aggregate {attr}") from exc
                require(declared == actual, f"aggregate {attr}: declared {declared}, actual {actual}")
    if expect == "pass":
        require(exit_code == 0, f"pass XML with failing process exit {exit_code}")
        require(all(status == "pass" or (status == "skipped" and key in allowed_skips)
                    for key, status in rows.items()), "failure/error/unapproved skip in pass cell")
    else:
        require(exit_code != 0, "failure XML with zero process exit")
        require(all(status in ("failure", "error") for status in rows.values()),
                "base new-mode cell contains a pass or skip")
    return {"mechanical": "PASS", "expect": expect, "exit_code": exit_code,
            "results": dict(sorted(rows.items())),
            "limitation": "Does not prove actual execution, genuine diagnostics or intended failure causes."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    package = commands.add_parser("package")
    package.add_argument("folder", type=Path)
    identity = commands.add_parser("fingerprint")
    identity.add_argument("files", nargs="+", type=Path)
    identity.add_argument("--metadata", type=Path)
    junit = commands.add_parser("junit")
    junit.add_argument("report", type=Path)
    junit.add_argument("--ids", required=True, type=Path)
    junit.add_argument("--expect", choices=("pass", "fail"), required=True)
    junit.add_argument("--exit-code", type=int, required=True)
    junit.add_argument("--allow-skips", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "package":
            result = package_check(args.folder)
        elif args.command == "fingerprint":
            metadata = json.loads(args.metadata.read_text(encoding="utf-8")) if args.metadata else None
            result = fingerprint(args.files, metadata)
        else:
            ids = json.loads(args.ids.read_text(encoding="utf-8"))
            skips = json.loads(args.allow_skips.read_text(encoding="utf-8")) if args.allow_skips else []
            require(isinstance(skips, list), "allowed skips must be a JSON array")
            result = inspect_junit(args.report.read_bytes(), ids, args.expect, args.exit_code, skips)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (Invalid, OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"mechanical": "FAIL", "reason": str(exc)}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
