#!/usr/bin/env python3
"""Discover a pinned repository and render a fail-closed repository adapter.

repo_init.py URL COMMIT TASK [--settings choices.json] [--render-only]
Settings are explicit author choices, never inferred facts. Run repo_check.py next.
"""
import argparse
import ast
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from machine import load, profile_path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, encoding="utf-8").strip()


def discover(repo):
    repo = Path(repo)
    names = git(repo, "ls-files").splitlines()
    texts = {}
    for name in names:
        path = repo / name
        if path.is_file() and path.stat().st_size < 500000 and not path.is_symlink():
            try:
                texts[name] = path.read_text(encoding="utf-8")
            except (UnicodeError, OSError):
                pass
    profile = {"languages": [], "evidence": {}, "open": [], "commands": {},
               "locks": [], "frameworks": [], "toolchain": {}, "package_manager": None,
               "build_system": [], "expected": {"base": [], "new": []},
               "selectors": {"base": [], "new": []}, "skip_allowlist": {},
               "hidden_paths": [], "setup_commands": [], "setup_imports": [],
               "env": {}, "reporter": "adapter-stdlib-1", "timeout": 420,
               "qualified": False, "tests": [], "fixtures": [], "config": [],
               "production": [], "compiled_twins": [], "dependency_manifests": [], "patterns": {}}

    def note(field, name, pattern):
        for number, line in enumerate(texts.get(name, "").splitlines(), 1):
            if re.search(pattern, line):
                profile["evidence"].setdefault(field, []).append({"location": f"{name}:{number}",
                                                               "text": line.strip()})

    def unresolved(field, reason):
        profile["open"].append({"field": field, "reason": reason})

    for lang, suffixes in (("go", (".go",)), ("python", (".py", ".pyx")),
                           ("typescript", (".ts", ".tsx", ".js", ".jsx")), ("rust", (".rs",))):
        sample = next((n for n in names if n.endswith(suffixes)), None)
        if sample:
            profile["languages"].append(lang)
            note("languages", sample, r"\S")
            profile["evidence"]["languages"] = profile["evidence"].get("languages", [])[:8]
    for name in names:
        lower = name.lower()
        if re.search(r"(^|/)(tests?|__tests__)/|(^|/)test_[^/]+\.py$|_test\.go$|\.(test|spec)\.[jt]sx?$", name):
            profile["tests"].append(name)
        elif re.search(r"(^|/)(testdata|fixtures?|__snapshots__)/", name):
            profile["fixtures"].append(name)
        elif re.search(r"(^|/)(conftest\.py|pytest\.ini|tox\.ini|noxfile\.py|setup\.cfg|pyproject\.toml|package\.json|[^/]*config\.[cm]?[jt]s|Makefile|\.tool-versions|\.nvmrc)$|^\.github/workflows/", name):
            profile["config"].append(name)
        elif name.endswith((".go", ".py", ".pyx", ".ts", ".tsx", ".js", ".rs")):
            profile["production"].append(name)
        if name.endswith((".pyx", ".pxd")):
            profile["compiled_twins"].append(name)
        if lower.endswith((".lock", "lock.yaml", "lock.json")) or name == "go.sum":
            profile["locks"].append(name)
        if name in ("go.mod", "pyproject.toml", "setup.py", "setup.cfg", "package.json", "Cargo.toml") or "requirements" in name and name.endswith(".txt"):
            profile["dependency_manifests"].append(name)
    # Fixture paths inside tests are inventory members in both roles.
    profile["fixtures"] = [n for n in names if re.search(r"(^|/)(testdata|fixtures?|__snapshots__)/", n)]
    for name in texts:
        if name.startswith(".github/workflows/") or name in ("Makefile", "package.json", "tox.ini", "noxfile.py", "scripts/check"):
            note("ci", name, r"(run:|pytest|unittest|go test|gotestsum|cargo test|vitest|jest|npm |pnpm |tox|nox)")
            note("validation", name, r"(lint|fmt|format|black|ruff|isort|mypy|flake8|gofumpt|golangci|prettier|eslint|tsc|clippy)")
    for name in (".tool-versions", ".nvmrc", "rust-toolchain", "rust-toolchain.toml", "setup.cfg", "setup.py", "pyproject.toml"):
        note("toolchain", name, r"(python|node|go |channel|requires-python|python_requires|build-backend)")
    note("toolchain", ".nvmrc", r"\S")
    if "go.mod" in texts:
        profile["language"] = "go"
        profile["package_manager"] = "go modules"
        profile["build_system"] = ["go"]
        profile["frameworks"] = ["testing"]
        note("frameworks", "go.mod", r"^(module |go )")
        version = re.search(r"^toolchain go(\S+)|^go (\S+)", texts["go.mod"], re.M)
        profile["toolchain"] = {"version": next(x for x in version.groups() if x) if version else None,
                                "module": re.search(r"^module\s+(\S+)", texts["go.mod"], re.M)[1]}
        explicit = re.search(r"^toolchain go(\S+)", texts["go.mod"], re.M)
        if explicit:
            profile["toolchain"]["version"] = explicit[1]
        note("toolchain", "go.mod", r"^(go |toolchain |module )")
        profile["commands"] = {"build": "go build ./...", "fetch": "go mod download",
                               "enumerate": "go test -list . ./...", "one": "go test -run '^NAME$' ./PACKAGE",
                               "junit": "go test -json -> adapter-stdlib-1 JUnit (top-level IDs)"}
        dirs = sorted({str(Path(n).parent).replace("\\", "/") for n in profile["tests"] if n.endswith("_test.go")})
        profile["selectors"]["base"] = ["./" + d if d != "." else "." for d in dirs]
        for n in profile["tests"]:
            if n.endswith("_test.go") and n in texts:
                pkg = str(Path(n).parent).replace("\\", "/")
                pkg = profile["toolchain"]["module"] + ("/" + pkg if pkg != "." else "")
                for match in re.finditer(r"^func (Test\w+)\(\w*\s*\*testing\.T\)", texts[n], re.M):
                    if match[1] != "TestMain":
                        profile["expected"]["base"].append(pkg + "::" + match[1])
        unresolved("go_build_constraints", "Static names are provisional; repo_check must qualify package lists and build tags offline.")
    elif "pyproject.toml" in texts or "setup.py" in texts or any(n.endswith(".py") for n in names):
        profile["language"] = "python"
        profile["package_manager"] = "pip"
        profile["build_system"] = ["PEP 517" if "pyproject.toml" in texts else "setuptools"]
        profile["frameworks"] = ["pytest"] if any("pytest" in t for n, t in texts.items() if n in profile["config"] or "requirements" in n) else []
        profile["commands"] = {"build": "python -m pip install --no-build-isolation --no-deps -e .",
                               "fetch": "python -m pip install -r requirements/test.txt",
                               "enumerate": "python -m pytest --collect-only -q",
                               "one": "python -m pytest FILE::CLASS::TEST", "junit": "pytest --junitxml=report.xml"}
        roots = sorted({n.split('/')[0] for n in profile["tests"] if '/' in n})
        profile["selectors"]["base"] = roots or [n for n in profile["tests"] if n.endswith(".py")]
        for n in profile["tests"]:
            if not n.endswith(".py") or n not in texts:
                continue
            try:
                tree = ast.parse(texts[n])
            except SyntaxError:
                unresolved("collection", f"{n}: source cannot be parsed by the discovery interpreter")
                continue
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                    profile["expected"]["base"].append(n[:-3].replace("/", ".") + "::" + node.name)
                if isinstance(node, ast.ClassDef):
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                            profile["expected"]["base"].append(n[:-3].replace("/", ".") + "." + node.name + "::" + child.name)
        unresolved("toolchain.version", "Python constraints and CI matrices are not an exact patch-version pin; select and verify an image runtime.")
        unresolved("dependencies", "Resolve test extras and development tools; manifest ranges are not immutable dependency pins.")
        unresolved("frameworks", "Confirm pytest compatibility, plugins, parametrized IDs and collection using repo_check.")
    elif "package.json" in texts:
        profile["language"] = "typescript"
        data = json.loads(texts["package.json"])
        profile["package_manager"] = data.get("packageManager", "pnpm" if "pnpm-lock.yaml" in names else "npm")
        profile["build_system"] = ["package.json scripts"]
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        profile["frameworks"] = [f for f in ("vitest", "jest") if f in deps]
        profile["toolchain"] = {"version": texts.get(".nvmrc", "").strip().lstrip("v") or data.get("engines", {}).get("node")}
        note("toolchain", "package.json", r"(engines|node|packageManager)")
        note("frameworks", "package.json", r"(vitest|jest|junit)")
        profile["commands"] = {"build": data.get("scripts", {}).get("build"),
                               "fetch": "pnpm install --frozen-lockfile" if str(profile["package_manager"]).startswith("pnpm") else "npm ci",
                               "enumerate": "jest --listTests (files only); qualify reporter test IDs",
                               "one": "vitest run FILE -t '^NAME$' or jest --runTestsByPath FILE -t '^NAME$'",
                               "junit": "vitest --reporter=junit or jest-junit (locked version required)"}
        profile["selectors"]["base"] = profile["tests"]
        unresolved("typescript_adapter", "UNPROVEN: qualify native enumeration, single-ID filtering, reporter and package-manager version on the platform.")
        unresolved("reporter.version", "Pin the native JUnit reporter in the repository lockfile before qualification.")
    else:
        profile["language"] = "unsupported"
        unresolved("adapter", "No qualified template for detected languages; author a repository-native adapter before execution.")
    for field in ("tests", "fixtures", "config", "production", "compiled_twins", "locks", "dependency_manifests"):
        profile["evidence"][field] = [{"location": n + ":1", "text": "tracked source inventory"} for n in profile[field]]
    profile["patterns"] = {"tests": [r"(^|/)(tests?|__tests__)/", r"_test\.go$", r"(^|/)test_[^/]+\.py$", r"\.(test|spec)\.[jt]sx?$"],
                           "fixtures": [r"(^|/)(testdata|fixtures?|__snapshots__)/"],
                           "production": "tracked language sources outside the discovered grading inventory; review shared helpers/config"}
    for key in profile["expected"]:
        profile["expected"][key] = sorted(set(profile["expected"][key]))
    unresolved("selectors.base", "Whole-repository defaults are provisional; author must identify affected regressions and offline exclusions.")
    unresolved("selectors.new", "No feature contract or author tests were provided; configure hidden_paths, selectors.new and expected.new.")
    unresolved("restore", "Review test/helper/config ownership; shared build manifests may also contain candidate production choices.")
    unresolved("platform", "Allowed base, network/source rules, watchdog and human platform build result require current platform evidence.")
    return profile


def apply_settings(profile, settings):
    allowed = {"selectors", "expected", "hidden_paths", "skip_allowlist", "env", "setup_commands",
               "setup_imports", "dependency_install", "toolchain", "build_commands", "restore_paths", "timeout",
               "go_sha256", "development_install", "package_manager_install", "evidence", "recipe"}
    unknown = set(settings) - allowed
    if unknown:
        raise ValueError("unknown settings: " + ", ".join(sorted(unknown)))
    for key, value in settings.items():
        if key == "evidence":
            profile["evidence"].setdefault("author_choices", []).extend(value)
        elif key in ("selectors", "expected", "toolchain"):
            profile[key].update(value)
        else:
            profile[key] = value


def render(task, profile):
    init = task / "init"
    init.mkdir(exist_ok=True)
    language = profile["language"]
    template = TEMPLATES / language
    if not template.is_dir():
        (init / "Dockerfile").write_text("FROM {{qualified_language_adapter}}\n", encoding="utf-8", newline="\n")
        (init / "test.sh").write_text("#!/bin/sh\necho 'unsupported adapter: see profile.json open list' >&2\nexit 2\n", newline="\n")
        return
    recipe_path = template / "recipe.json"
    recipe = json.loads(recipe_path.read_text()) if recipe_path.exists() else {}
    if recipe and profile.get("recipe") == recipe.get("name"):
        if profile["identity"]["commit"] != recipe["commit"] or profile["identity"]["repository_url"].removesuffix(".git").rstrip("/") != recipe["repository_url"]:
            raise ValueError("proven recipe does not match repository and commit")
        apply_settings(profile, {k: v for k, v in recipe["settings"].items() if k not in profile.get("author_overrides", [])})
        profile["evidence"]["recipe"] = recipe["evidence"]
    profile.setdefault("restore_paths", sorted(set(profile["tests"] + profile["fixtures"] + profile["config"])))
    # Restore only declared grading paths. Their production ownership must be reviewed.
    version = profile["toolchain"].get("version") or "NOT_VERIFIED"
    for field, missing, reason in (
        ("go_sha256", language == "go" and not profile.get("go_sha256"), "Verify the release checksum before building the literal Go archive URL."),
        ("development_tools", "development_install" not in profile, "Confirm discovered native lint/format/type tools exist in the resolved base or install exact versions."),
    ):
        if missing and not any(row["field"] == field for row in profile["open"]):
            profile["open"].append({"field": field, "reason": reason})
    values = {"platform": profile["environment"]["platform"], "toolchain_version": version,
              "go_sha256": profile.get("go_sha256", "NOT_VERIFIED"),
              "dependency_install": profile.get("dependency_install", "echo 'dependency pins NOT VERIFIED' >&2 && exit 2"),
              "development_install": profile.get("development_install", "true"),
              "package_manager_install": profile.get("package_manager_install", "true"),
              "fetch_command": profile.get("commands", {}).get("fetch", "false"),
              "build_commands": profile.get("build_commands", "go build ./... && go list -deps -test ./... > /dev/null"),
              "profile_b64": base64.b64encode(json.dumps({k: profile[k] for k in
                  ("identity", "language", "toolchain", "tests", "restore_paths", "hidden_paths", "selectors",
                   "expected", "skip_allowlist", "env", "setup_commands", "setup_imports", "timeout", "frameworks")}, sort_keys=True).encode()).decode()}
    def fill(body):
        return re.sub(r"\{\{([a-z0-9_]+)\}\}", lambda m: str(values[m[1]]), body)
    for name in ("Dockerfile", "test.sh"):
        (init / name).write_text(fill((template / name).read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    (init / "test.sh").chmod(0o755)
    for mode in ("base", "new"):
        (init / (mode + "-ids.json")).write_text(json.dumps(profile["expected"][mode], indent=2) + "\n", encoding="utf-8")


def save(task, profile):
    render(task, profile)
    (task / "profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("commit")
    parser.add_argument("task", type=Path)
    parser.add_argument("--settings", type=Path)
    parser.add_argument("--render-only", action="store_true")
    args = parser.parse_args()
    try:
        machine = load()
        task = args.task.resolve()
        task.mkdir(parents=True, exist_ok=True)
        base = task / "base"
        if not re.fullmatch(r"[0-9a-fA-F]{40}", args.commit):
            raise ValueError("commit must be a full 40-character hash")
        if args.url.startswith("-"):
            raise ValueError("repository URL cannot be an option")
        if args.render_only:
            profile = json.loads((task / "profile.json").read_text())
            if profile["identity"]["commit"] != args.commit or profile["identity"]["repository_url"] != args.url:
                raise ValueError("render identity mismatch")
        else:
            fresh = not base.exists()
            if fresh:
                subprocess.run(["git", "clone", "--no-checkout", "--", args.url, str(base)], check=True)
            if not fresh and git(base, "status", "--porcelain"):
                raise ValueError("base checkout is dirty; refusing to modify it")
            if git(base, "remote", "get-url", "origin") != args.url:
                raise ValueError("existing base origin differs")
            subprocess.run(["git", "-C", str(base), "checkout", "--detach", args.commit], check=True)
            profile = discover(base)
            profile["identity"] = {"repository_url": args.url, "commit": git(base, "rev-parse", "HEAD"),
                                   "tree": git(base, "rev-parse", "HEAD^{tree}"), "clean": not git(base, "status", "--porcelain"),
                                   "submodules": (base / ".gitmodules").exists(),
                                   "lfs": any("filter=lfs" in (base / n).read_text(errors="replace") for n in git(base, "ls-files", "*.gitattributes").splitlines())}
            profile["environment"] = {"machine_profile": profile_path().name,
                                      "platform": machine["docker"]["final_platform"],
                                      "configured_slots": machine["docker"]["slots"], "effective_slots": 1,
                                      "uid": 12345, "gid": 12345, "passwd_absent": True,
                                      "path": "/usr/local/bin:/usr/bin:/bin", "home": "scratch/home",
                                      "cwd": "/", "mounts": "/app:ro, /tmp:rw, /out:rw", "network": "none",
                                      "watchdog": "NOT VERIFIED; local 420 seconds below proof.py's 688-second bound"}
        if args.settings:
            settings = json.loads(args.settings.read_text(encoding="utf-8"))
            profile["author_overrides"] = list(settings)
            apply_settings(profile, settings)
        save(task, profile)
        print(f"profile: {task / 'profile.json'}; language: {profile['language']}; open: {len(profile['open'])}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"repo_init: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
