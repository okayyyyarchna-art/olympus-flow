#!/usr/bin/env python3
"""Discover a pinned repository and render a fail-closed repository adapter.

repo_init.py URL COMMIT TASK [--settings choices.json] [--render-only [--force]]
TASK is a folder name under the machine profile's paths.tasks_root, or a path (it holds a separator or is absolute).
Settings are explicit author choices, never inferred facts. Run repo_check.py next.
"""
import argparse
import ast
import base64
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I drops the script folder
from machine import load, machine_dir, profile_path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates"
FLAGGED_WORDS = Path(__file__).resolve().parent / "lib/check_codex_brief.sh"
# The generated-output patterns the runner's candidate copy drops; a tracked file matching one is listed in
# profile keep_tracked so the runner keeps it (BACKLOG 141: pmg tracks a go:embed .o object).
GENERATED_PATTERNS = (".git", "__pycache__", "*.pyc", "*.so", "*.pyd", "*.o", "*.a", ".pytest_cache", "build", "dist", "node_modules")


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, encoding="utf-8").strip()


def task_dir(argument, machine):
    """A bare TASK name lives under paths.tasks_root; a path (separator or absolute) is taken as given (BACKLOG 116/136)."""
    if os.path.isabs(argument) or "/" in argument or "\\" in argument:
        task = Path(argument).expanduser().resolve()
    elif re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", argument) and argument not in (".", ".."):
        task = (Path(machine["paths"]["tasks_root"]) / argument).resolve()
    else:
        raise ValueError(f"TASK {argument!r} is neither a folder name (letters, digits, . _ -) nor a path")
    for root in (Path(__file__).resolve().parents[1], machine_dir().parent):
        if task == root or root in task.parents:
            raise ValueError(f"task folder {task} is inside the Olympus Flow folder {root}; "
                             "use a name under paths.tasks_root or a path outside it")
    return task


def flagged_word(name):
    """The word of NAME that lib/check_codex_brief.sh flags (Codex refuses briefs naming it), or None (BACKLOG 165)."""
    match = re.search(r"^words='([^']+)'", FLAGGED_WORDS.read_text(encoding="utf-8"), re.M)
    if not match:
        raise ValueError(f"{FLAGGED_WORDS} has no words='...' list")
    found = re.search(match[1], name, re.I)
    return found[0] if found else None


def go_imports(text):
    found = set(re.findall(r'^\s*import\s+(?:[\w.]+\s+)?"([^"]+)"', text, re.M))
    for block in re.findall(r"^\s*import\s*\((.*?)^\s*\)", text, re.M | re.S):
        found.update(re.findall(r'"([^"]+)"', block))
    return found


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
               "build_system": [], "expected": {"base": [], "new": []}, "new_native_ids": {},
               "selectors": {"base": [], "new": []}, "skip_allowlist": {},
               "hidden_paths": [], "base_hidden_paths": [], "setup_commands": [], "setup_imports": [],
               "env": {}, "reporter": "adapter-stdlib-1", "timeout": 420,
               "qualified": False, "tests": [], "fixtures": [], "config": [],
               "production": [], "helpers": [], "compiled_twins": [], "dependency_manifests": [], "patterns": {},
               "keep_tracked": sorted(n for n in names if any(fnmatch.fnmatchcase(part, pattern)
                                                               for part in PurePosixPath(n).parts for pattern in GENERATED_PATTERNS))}

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
        elif re.search(r"(^|/)(testutil|testutils|testhelpers|__mocks__)/", name):
            profile["helpers"].append(name)
        elif re.search(r"(^|/)(conftest\.py|pytest\.ini|tox\.ini|noxfile\.py|setup\.cfg|pyproject\.toml|package\.json|(?:vitest|vite|jest|babel|eslint|prettier|webpack|rollup|next|nuxt)\.config\.[cm]?[jt]s|tsconfig[^/]*\.json|Makefile|\.tool-versions|\.nvmrc)$|^\.github/workflows/", name):
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
    note("dockerignore", ".dockerignore", r"\S")
    tool_versions = dict(re.findall(r"^(\S+)\s+(\S+)\s*$", texts.get(".tool-versions", ""), re.M))
    if "go.mod" in texts:
        profile["language"] = "go"
        profile["package_manager"] = "go modules"
        profile["build_system"] = ["go"]
        profile["frameworks"] = ["testing"]
        note("frameworks", "go.mod", r"^(module |go )")
        for dependency, framework in (("stretchr/testify", "testify"), ("onsi/ginkgo", "ginkgo"), ("onsi/gomega", "gomega")):
            if dependency in texts["go.mod"]:
                profile["frameworks"].append(framework)
                note("frameworks", "go.mod", re.escape(dependency))
        version = re.search(r"^toolchain go(\S+)|^go (\S+)", texts["go.mod"], re.M)
        profile["toolchain"] = {"version": next(x for x in version.groups() if x) if version else None,
                                "module": re.search(r"^module\s+(\S+)", texts["go.mod"], re.M)[1]}
        helper_dirs = {str(Path(name).parent).replace("\\", "/") for name in profile["helpers"]}
        for name in profile["production"]:
            if name.endswith(".go") and re.search(r'^\s*(?:import\s+)?"testing"', texts.get(name, ""), re.M):
                directory = str(Path(name).parent).replace("\\", "/")
                if not directory.startswith("internal/"):
                    unresolved("helpers.shared", f"{directory} production imports testing; explicitly classify public testing APIs versus grading helpers.")
                else:
                    helper_dirs.add(directory)
                    note("helper_roles", name, r'"testing"')
        for directory in helper_dirs:
            members = [name for name in profile["production"] if str(Path(name).parent).replace("\\", "/") == directory]
            profile["production"] = [name for name in profile["production"] if name not in members]
            profile["helpers"].extend(members)
        shared = set()
        for name in profile["helpers"]:
            directory = str(Path(name).parent).replace("\\", "/")
            imported = '"' + profile["toolchain"]["module"] + '/' + directory + '"'
            if any(imported in texts.get(production, "") for production in profile["production"]):
                shared.add(directory)
        for directory in shared:
            members = [name for name in profile["helpers"] if str(Path(name).parent).replace("\\", "/") == directory]
            profile["helpers"] = [name for name in profile["helpers"] if name not in members]
            profile["production"].extend(members)
            unresolved("helpers.shared", f"{directory} is imported by production; preserve candidate source and design a grading authority boundary explicitly.")
        # A package imported only by test code (outside its own directory) is a grading helper: pinned through
        # restore_paths so a candidate cannot weaken the retained tests by editing it (BACKLOG 160/222).
        module = profile["toolchain"]["module"]
        imports = {name: go_imports(text) for name, text in texts.items() if name.endswith(".go")}
        folder = lambda name: PurePosixPath(name).parent.as_posix()
        helper_dirs = {folder(name) for name in profile["helpers"]}
        moved = True
        while moved:
            moved = False
            for package in sorted({folder(name) for name in profile["production"] if name.endswith(".go")}):
                path = module + ("/" + package if package != "." else "")
                importers = sorted(name for name, found in imports.items() if path in found and folder(name) != package)
                if importers and all(name.endswith("_test.go") or folder(name) in helper_dirs for name in importers):
                    members = [name for name in profile["production"] if folder(name) == package]
                    profile["production"] = [name for name in profile["production"] if name not in members]
                    profile["helpers"].extend(members)
                    helper_dirs.add(package)
                    line = next((i for i, text in enumerate(texts[importers[0]].splitlines(), 1) if '"' + path + '"' in text), 1)
                    profile["evidence"].setdefault("helper_roles", []).append({"location": f"{importers[0]}:{line}",
                        "text": f"{package} is imported only by test code ({', '.join(importers)}); pinned as a helper through restore_paths"})
                    moved = True
        explicit = re.search(r"^toolchain go(\S+)", texts["go.mod"], re.M)
        if explicit:
            profile["toolchain"]["version"] = explicit[1]
        elif tool_versions.get("golang"):
            profile["toolchain"]["version"] = tool_versions["golang"]
        if not re.fullmatch(r"\d+\.\d+\.\d+", profile["toolchain"]["version"] or ""):
            unresolved("toolchain.version", "The Go minimum version is not an exact release archive pin; select a verified patch release.")
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
        for lock, manager in (("uv.lock", "uv"), ("poetry.lock", "poetry"), ("pdm.lock", "pdm"), ("Pipfile.lock", "pipenv")):
            if lock in names:
                profile["package_manager"] = manager
                break
        profile["build_system"] = ["PEP 517" if "pyproject.toml" in texts else "setuptools"]
        profile["frameworks"] = ["pytest"] if any("pytest" in t for n, t in texts.items() if n in profile["config"] or "requirements" in n) else []
        for name in profile["tests"]:
            for framework in ("pytest", "unittest"):
                if re.search(r"^(?:from|import) " + framework + r"\b", texts.get(name, ""), re.M):
                    if framework not in profile["frameworks"]:
                        profile["frameworks"].append(framework)
                    note("frameworks", name, r"^(?:from|import) " + framework + r"\b")
        profile["commands"] = {"build": "python -m pip install --no-build-isolation --no-deps -e .",
                               "fetch": "python -m pip install -r requirements/test.txt",
                               "enumerate": "python -m pytest --collect-only -q",
                               "one": "python -m pytest FILE::CLASS::TEST", "junit": "pytest --junitxml=report.xml"}
        profile["commands"]["fetch"] = {"pip": "python -m pip install -r requirements/test.txt",
            "uv": "uv sync --frozen --all-extras", "poetry": "poetry install --sync",
            "pdm": "pdm sync --frozen-lockfile", "pipenv": "pipenv sync --dev"}[profile["package_manager"]]
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
        if re.fullmatch(r"\d+\.\d+\.\d+", tool_versions.get("python", "")):
            profile["toolchain"]["version"] = tool_versions["python"]
        else:
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
        profile["reporter_versions"] = {name: deps[name] for name in profile["frameworks"]}
        profile["toolchain"] = {"version": texts.get(".nvmrc", "").strip().lstrip("v") or tool_versions.get("nodejs") or data.get("engines", {}).get("node")}
        if not re.fullmatch(r"\d+\.\d+\.\d+", profile["toolchain"]["version"] or ""):
            unresolved("toolchain.version", "Node engine ranges and aliases are not exact runtime pins; select a verified patch release.")
        if not re.fullmatch(r"(?:npm|pnpm)@\d+\.\d+\.\d+", str(profile["package_manager"])):
            unresolved("package_manager.version", "Qualify an exact npm/pnpm version from the image or install a pinned package manager.")
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
        unresolved("new_native_ids", "Collect the feature ID/native-selector map on a successful reference before new/base execution.")
    else:
        profile["language"] = "unsupported"
        unresolved("adapter", "No qualified template for detected languages; author a repository-native adapter before execution.")
    for field in ("tests", "fixtures", "helpers", "config", "production", "compiled_twins", "locks", "dependency_manifests"):
        profile["evidence"][field] = [{"location": n + ":1", "text": "tracked source inventory"} for n in profile[field]]
    profile["patterns"] = {"tests": [r"(^|/)(tests?|__tests__)/", r"_test\.go$", r"(^|/)test_[^/]+\.py$", r"\.(test|spec)\.[jt]sx?$"],
                           "fixtures": [r"(^|/)(testdata|fixtures?|__snapshots__)/"],
                           "production": "tracked language sources outside the discovered grading inventory; review shared helpers/config"}
    for key in profile["expected"]:
        profile["expected"][key] = sorted(set(profile["expected"][key]))
    if "Makefile" in names:
        profile["build_system"].append("make")
    for key, value in profile["commands"].items():
        if not value:
            unresolved("commands." + key, "No repository-native command was found; choose and qualify one before construction.")
    if not profile["frameworks"]:
        unresolved("frameworks", "No native framework was confidently identified from tracked manifests, imports or CI.")
    if not profile["locks"]:
        unresolved("locks", "No dependency lockfile found; author must supply reproducible build/test/development pins.")
    unresolved("selectors.base", "Whole-repository defaults are provisional; author must identify affected regressions and offline exclusions.")
    unresolved("selectors.new", "No feature contract or author tests were provided; configure hidden_paths, selectors.new and expected.new.")
    unresolved("expected.new", "No successful feature-test discovery exists yet; never infer new IDs from a failing build.")
    unresolved("restore", "Review test/helper/config ownership; shared build manifests may also contain candidate production choices.")
    if ".dockerignore" in names:
        unresolved("dockerignore", "Review context exclusions; if .git is excluded, provision verified pristine tests before offline execution.")
    unresolved("platform", "Allowed base, network/source rules, watchdog and human platform build result require current platform evidence.")
    return profile


def apply_settings(profile, settings):
    allowed = {"selectors", "expected", "hidden_paths", "skip_allowlist", "env", "setup_commands",
               "setup_imports", "dependency_install", "toolchain", "build_commands", "restore_paths", "timeout",
               "go_sha256", "development_install", "package_manager_install", "evidence", "recipe"}
    allowed.add("build_environment")
    allowed.add("new_native_ids")
    allowed.add("production_probe")
    allowed.add("reporter_versions")
    allowed.add("base_hidden_paths")
    allowed.update(("helpers", "production", "config", "tests", "fixtures", "keep_tracked"))
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


def derive_new_native_ids(profile):
    """Map expected.new to native selectors (BACKLOG 146): Go ImportPath::Test -> [package, name]; Python canonical
    IDs -> pytest node IDs through the hidden/test files; anything else stays OPEN under new_native_ids."""
    expected = profile["expected"]["new"]
    if not expected or "new_native_ids" in profile.get("author_overrides", []):
        return
    language, ids, unresolved = profile["language"], {}, []
    files = set(profile.get("hidden_paths", [])) | set(profile["tests"])
    for key in expected:
        classname, sep, name = key.rpartition("::")
        if language == "go" and classname:
            ids[key] = [classname, name]
        elif language == "python" and classname:
            parts = classname.split(".")
            cut = next((n for n in range(len(parts), 0, -1) if "/".join(parts[:n]) + ".py" in files), None)
            if cut is None:
                unresolved.append(key)
            else:
                ids[key] = "::".join(["/".join(parts[:cut]) + ".py", *parts[cut:], name])
        else:
            unresolved.append(key)
    profile["open"] = [row for row in profile["open"] if row["field"] != "new_native_ids"]
    if unresolved:
        profile.pop("new_native_ids", None)  # a half-derived map would only move the failure into test.sh new
        profile["open"].append({"field": "new_native_ids", "reason": f"{language}: no native selector derivable for "
                                + ", ".join(unresolved[:5]) + "; set new_native_ids in --settings (Go: ID -> [package, name]; "
                                "Python: ID -> pytest node ID; the hidden file must be in hidden_paths)."})
    else:
        profile["new_native_ids"] = ids


def render(task, profile, force=False):
    init = task / "init"
    init.mkdir(exist_ok=True)
    record = init / ".rendered.json"
    rendered = json.loads(record.read_text(encoding="utf-8")) if record.exists() else {}

    def emit(name, body):
        # Never overwrite a file that differs from this renderer's own last output (BACKLOG 136): the author may
        # have placed the platform-accepted Dockerfile or edited test.sh. --render-only --force rewrites it.
        path, data = init / name, body.encode("utf-8")
        if path.exists() and not force and hashlib.sha256(path.read_bytes()).hexdigest() != rendered.get(name):
            print(f"kept hand-edited init/{name} (differs from the last render; repo_init.py --render-only --force rewrites it)", flush=True)
            return
        path.write_bytes(data)
        rendered[name] = hashlib.sha256(data).hexdigest()
        record.write_text(json.dumps(rendered, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    profile["adapter"] = {"pristine_restore_source": "git archive " + profile["identity"]["commit"],
                          "hidden_overlay": "explicit hidden_paths after pristine restoration",
                          "rebuild": "discard generated binaries/C twins; run setup_commands and setup_imports against candidate scratch",
                          "loaded_source": "source-relative copy; Cython import paths asserted inside candidate scratch",
                          "expected_id_paths": {"base": "init/base-ids.json", "new": "init/new-ids.json"},
                          "scratch": "/var/tmp/repo-adapter-*", "docker_lock": "tools/lib/.docker.lock relative to skill installation"}
    language = profile["language"]
    template = TEMPLATES / language
    if not template.is_dir():
        emit("Dockerfile", "FROM {{qualified_language_adapter}}\n")
        emit("test.sh", "#!/bin/sh\necho 'unsupported adapter: see profile.json open list' >&2\nexit 2\n")
        return
    recipe_path = template / "recipe.json"
    recipe = json.loads(recipe_path.read_text()) if recipe_path.exists() else {}
    if recipe and profile.get("recipe") == recipe.get("name"):
        if profile["identity"]["commit"] != recipe["commit"] or profile["identity"]["repository_url"].removesuffix(".git").rstrip("/") != recipe["repository_url"]:
            raise ValueError("proven recipe does not match repository and commit")
        apply_settings(profile, {k: v for k, v in recipe["settings"].items() if k not in profile.get("author_overrides", [])})
        profile["evidence"]["recipe"] = recipe["evidence"]
        if re.fullmatch(r"\d+\.\d+\.\d+", profile["toolchain"].get("version", "")):
            profile["open"] = [row for row in profile["open"] if row["field"] != "toolchain.version"]
    profile.setdefault("helpers", [])
    profile.setdefault("restore_paths", sorted(set(profile["tests"] + profile["fixtures"] + profile["helpers"] + profile["config"])))
    validate(profile)
    # Restore only declared grading paths. Their production ownership must be reviewed.
    version = profile["toolchain"].get("version") or "NOT_VERIFIED"
    if language == "go":
        profile["reporter_versions"] = {"go_json": version, "junit_adapter": "stdlib-1"}
    elif language == "python":
        pinned = re.search(r"\bpytest==([0-9.]+)", profile.get("dependency_install", ""))
        if "reporter_versions" not in profile.get("author_overrides", []):
            profile["reporter_versions"] = {"pytest_junit": pinned[1] if pinned else None,
                                            "junit_adapter": "stdlib-1"}
    manager = str(profile["package_manager"])
    manager_install = "npm install --global " + manager if re.fullmatch(r"(?:npm|pnpm)@\d+\.\d+\.\d+", manager) else "true"
    for field, missing, reason in (
        ("go_sha256", language == "go" and not profile.get("go_sha256"), "Verify the release checksum before building the literal Go archive URL."),
        ("development_tools", "development_install" not in profile, "Confirm discovered native lint/format/type tools exist in the resolved base or install exact versions."),
    ):
        if missing and not any(row["field"] == field for row in profile["open"]):
            profile["open"].append({"field": field, "reason": reason})
    # The runner's adapter fields only; {{profile_json}} is the readable form, {{profile_b64}} the older template's.
    embedded = {**{k: profile[k] for k in
                   ("identity", "language", "toolchain", "tests", "restore_paths", "hidden_paths", "selectors",
                    "expected", "skip_allowlist", "env", "setup_commands", "setup_imports", "timeout", "frameworks")},
                "identity": {"commit": profile["identity"]["commit"]},
                "native_ids": profile.get("native_ids", {}), "helpers": profile["helpers"],
                "new_native_ids": profile.get("new_native_ids", {}),
                "base_hidden_paths": profile.get("base_hidden_paths", []),
                # The current runtime calls the overlays overlay_paths; the older one hidden_paths. Carry both.
                "overlay_paths": profile["hidden_paths"], "base_overlay_paths": profile.get("base_hidden_paths", []),
                "keep_tracked": profile.get("keep_tracked", []),
                "fixtures": profile["fixtures"]}
    values = {"platform": profile["environment"]["platform"], "toolchain_version": version,
              "go_sha256": profile.get("go_sha256", "NOT_VERIFIED"),
              "dependency_install": profile.get("dependency_install", "echo 'dependency pins NOT VERIFIED' >&2 && exit 2"),
              "development_install": profile.get("development_install", "true"),
              "package_manager_install": profile.get("package_manager_install", manager_install),
              "build_environment": profile.get("build_environment", "ENV PIP_DISABLE_PIP_VERSION_CHECK=1"),
              "fetch_command": profile.get("commands", {}).get("fetch", "false"),
              "build_commands": profile.get("build_commands", "go build ./... && go list -deps -test ./... > /dev/null"),
              # the readable profile carries the current runtime's key names only: "hidden_paths" is a process word
              # that precheck.py flags in test.sh (#152); the older template still gets both spellings through base64
              "profile_json": json.dumps({k: v for k, v in embedded.items()
                                          if k not in ("hidden_paths", "base_hidden_paths")}, indent=2, sort_keys=True),
              "profile_b64": base64.b64encode(json.dumps(embedded, sort_keys=True).encode()).decode()}
    def fill(body):
        return re.sub(r"\{\{([a-z0-9_]+)\}\}", lambda m: str(values[m[1]]), body)
    for name in ("Dockerfile", "test.sh"):
        body = (template / name).read_text(encoding="utf-8")
        if name == "Dockerfile":
            # The platform's precheck wants the bare FROM line; proof.py passes --platform to docker build.
            body = re.sub(r"^(\s*FROM\s+)--platform=\{\{platform\}\}\s+", r"\1", body, flags=re.M | re.I)
        body = fill(body)
        if name == "Dockerfile":
            joined = re.sub(r"\\\s*\n", " ", body)
            # Owner rule (dockerfile.md E4, precheck.py): no comments except one reason block right above a RUN.
            lines = body.splitlines()
            for i, line in enumerate(lines):
                comment = line.lstrip().startswith("#") and not line.lstrip().startswith("# syntax=")
                if comment and not (i and lines[i - 1].lstrip().startswith("#")):
                    after = next((k for k in range(i, len(lines)) if not lines[k].lstrip().startswith("#")), None)
                    if after is None or not lines[after].lstrip().upper().startswith("RUN "):
                        raise ValueError(f"generated Dockerfile line {i + 1}: a comment that is not a reason block right above a RUN")
            if re.search(r"(?:^RUN\s+|&&\s*|;\s*|\|\s*)(?:python[0-9.]*\s+-m\s+)?(?:go test|pytest|cargo test|npm test|vitest run|jest|tox)\b", joined, re.M):
                raise ValueError("generated Dockerfile invokes a test runner in RUN")
        emit(name, body)
    (init / "test.sh").chmod(0o755)
    for mode in ("base", "new"):
        (init / (mode + "-ids.json")).write_text(json.dumps(profile["expected"][mode], indent=2) + "\n", encoding="utf-8")


def save(task, profile, force=False):
    derive_new_native_ids(profile)
    render(task, profile, force)
    profile["environment"]["watchdog"] = f"NOT VERIFIED; local {profile['timeout']} seconds below proof.py's 688-second bound"
    (task / "profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")


def validate(profile):
    if type(profile["timeout"]) is not int or not 0 < profile["timeout"] < 688:
        raise ValueError("adapter timeout must be positive and below 688 seconds")
    for mode, ids in profile["expected"].items():
        if not isinstance(ids, list) or any(not isinstance(key, str) or not key for key in ids) or len(set(ids)) != len(ids):
            raise ValueError("expected." + mode + " must contain unique nonempty ID strings")
    overlays = profile["hidden_paths"] + profile.get("base_hidden_paths", [])
    for name in profile["restore_paths"] + overlays + profile.get("keep_tracked", []):
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or ".git" in path.parts or "\\" in name or re.match(r"^[A-Za-z]:", name):
            raise ValueError("grading path escapes repository: " + name)
    overlap = set(profile["production"]) & set(profile["restore_paths"] + overlays)
    if overlap:
        raise ValueError("grading restore/overlay would replace candidate production: " + ", ".join(sorted(overlap)))
    if not isinstance(profile["skip_allowlist"], dict) or any(not isinstance(reason, str) or not reason.strip() for reason in profile["skip_allowlist"].values()):
        raise ValueError("base skips require exact ID-to-reason entries")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("commit")
    parser.add_argument("task", help="folder name under the machine profile's paths.tasks_root, or a path")
    parser.add_argument("--settings", type=Path)
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--force", action="store_true", help="with --render-only: rewrite a hand-edited init/Dockerfile or init/test.sh")
    args = parser.parse_args()
    try:
        machine = load()
        task = task_dir(args.task, machine)
        flagged = flagged_word(task.name)
        if flagged:
            raise ValueError(f"task name {task.name!r} contains {flagged!r}, a word lib/check_codex_brief.sh flags: "
                             "every replica brief names the task path and Codex refuses it; choose another name")
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
            if profile["language"] == "go":
                profile["env"]["GOMAXPROCS"] = str(machine["parallel"]["battery_workers"])
        if args.settings:
            settings = json.loads(args.settings.read_text(encoding="utf-8"))
            profile["author_overrides"] = sorted(set(profile.get("author_overrides", [])) | set(settings))
            apply_settings(profile, settings)
        if profile["language"] == "go":
            profile["env"].setdefault("GOMAXPROCS", str(machine["parallel"]["battery_workers"]))
        save(task, profile, args.force)
        print(f"task: {task}\nprofile: {task / 'profile.json'}; language: {profile['language']}; open: {len(profile['open'])}")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"repo_init: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
