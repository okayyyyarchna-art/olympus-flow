#!/usr/bin/env python3
"""Load the selected machine profile. CLI: machine.py get <dotted.key>."""
import json
import os
from pathlib import Path
import shlex
import sys

# Task repositories keep Linux line endings whatever the user's Git default is: CRLF breaks patches and Linux scripts.
os.environ.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.autocrlf", GIT_CONFIG_VALUE_0="false")


def machine_dir():
    tools = Path(__file__).resolve().parent
    for candidate in (tools.parent / "machine", tools.parent.parent / "machine"):
        if candidate.is_dir():
            return candidate
    raise ValueError("machine directory missing; reinstall Olympus Flow")


def profile_path(profile=None):
    selected = profile or os.environ.get("OLYMPUS_MACHINE")
    root = machine_dir()
    if not selected:
        path = root / "local.json"
    else:
        path = Path(selected).expanduser()
        if not path.is_file() and path.name == str(path):
            path = root / (selected if selected.endswith(".json") else selected + ".json")
    if not path.is_file():
        raise ValueError(f"machine profile not found: {path}; set OLYMPUS_MACHINE to a profile path or name, "
                         "or run install.sh --profile <name> to create machine/local.json")
    return path.resolve()


def load(profile=None):
    path = profile_path(profile)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("os", "shell", "python", "home"):
            if not isinstance(data[key], str) or not data[key]:
                raise ValueError(f"{key} must be a nonempty string")
        if data["os"] not in ("windows", "macos", "linux"):
            raise ValueError("os must be windows, macos or linux")
        for key in ("tasks_root", "work_root", "seams_root", "codex_home", "claude_bin", "codex_bin"):
            if not isinstance(data["paths"][key], str) or not data["paths"][key]:
                raise ValueError(f"paths.{key} must be a nonempty string")
        for section, keys in (("docker", ("slots", "memory_gb")),
                              ("parallel", ("battery_workers", "review_lanes", "solvers"))):
            for key in keys:
                value = data[section][key]
                if type(value) is not int or value < 1:
                    raise ValueError(f"{section}.{key} must be a positive integer")
        if type(data["parallel"]["stability_parallel"]) is not bool:
            raise ValueError("parallel.stability_parallel must be true or false")
        if type(data["docker"]["cleanup_allowed"]) is not bool:
            raise ValueError("docker.cleanup_allowed must be true or false")
        if data["docker"]["final_platform"] != "linux/amd64":
            raise ValueError("docker.final_platform must be linux/amd64")
        if data["docker"]["native_platform"] not in ("linux/amd64", "linux/arm64"):
            raise ValueError("docker.native_platform must be linux/amd64 or linux/arm64")
        data["home"] = str(Path(data["home"]).expanduser()).replace("\\", "/")
        home = data["home"]
        paths = data["paths"]
        for key, value in paths.items():
            if not isinstance(value, str):
                raise ValueError(f"paths.{key} must be a string")
            if value == "~" or value.startswith("~/"):
                paths[key] = home + value[1:]
        paths.setdefault("solver_root", paths["work_root"] + "/solvers")
        paths.setdefault("shared_root", home + "/OSS/shipd")
        paths.setdefault("coordinator_root", home + "/OSS")
        paths.setdefault("claude_config_dir", home + "/.claude")
        paths.setdefault("claude2_config_dir", "")
        project = paths["coordinator_root"].replace("\\", "/")
        project_key = "".join(c if c.isalnum() or c == "-" else "-" for c in project)
        paths.setdefault("memory_dir", paths["claude_config_dir"] + "/projects/" + project_key + "/memory")
        return data
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid machine profile {path}: {exc}") from exc


def slot_limit(limit, override=None):
    if override is None:
        return limit
    if not isinstance(override, str) or not override.isascii() or not override.isdecimal() or int(override) < 1:
        raise ValueError("slot override must be a positive integer")
    return min(limit, int(override))


def exports(data):
    result = {"OLYMPUS_OS": data["os"], "OLYMPUS_SHELL": data["shell"], "PY": data["python"],
              "OLYMPUS_HOME": data["home"]}
    result.update({"OLYMPUS_" + k.upper(): v for k, v in data["paths"].items()})
    result.update({"OLYMPUS_" + k.upper(): v for k, v in data["docker"].items()})
    result.update({"OLYMPUS_" + k.upper(): v for k, v in data["parallel"].items()})
    return result


def main():
    try:
        data = load()
        if sys.argv[1:] == ["shell"]:
            print("export OLYMPUS_MACHINE=" + shlex.quote(str(profile_path()).replace("\\", "/")))
            for key, value in exports(data).items():
                if isinstance(value, bool):
                    value = str(value).lower()
                print(f"export {key}={shlex.quote(str(value))}")
        elif len(sys.argv) == 3 and sys.argv[1] == "get":
            value = data
            for key in sys.argv[2].split("."):
                value = value[key]
            print(json.dumps(value) if isinstance(value, (dict, list, bool)) else value)
        else:
            raise ValueError("usage: machine.py get <dotted.key> | shell")
    except (ValueError, KeyError) as exc:
        print(f"machine: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
