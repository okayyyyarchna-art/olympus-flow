#!/usr/bin/env python3
"""Fail-closed checkpoint gates. Usage: summarize.py <reports-dir> <tag>
--declare writes the checkpoint's required reports; --ref-audits adds two audits.
--merge-sq writes a finding union with source IDs, retaining both independent samples.
An explicit --checkpoint JSON names the evidence required for the checkpoint.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


KINDS = {"fairness", "sq", "dq", "ar", "verify", "ref-audit"}
SEVERITIES = {"high", "medium", "low", "major", "minor"}
FAIRNESS = {"Prompt-stated", "Repo-discoverable", "Standard external semantics", "Unfair"}
KEPT = {"solution_high", "solution_medium", "tests_gaps", "tests_unfair", "description_major"}


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=object_pairs,
                       parse_constant=lambda value: require(False, f"invalid JSON constant: {value}"))
    require(isinstance(value, dict) and value, f"empty/non-object report: {path}")
    return value


def write(path, value):
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(path)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def rows(report, key, nonempty=False):
    value = report.get(key)
    require(isinstance(value, list) and (value or not nonempty), f"invalid/missing {key}")
    require(all(isinstance(row, dict) for row in value), f"invalid {key} row")
    return value


def score(value):
    return type(value) is int and 1 <= value <= 3


def strings(value, nonempty=False):
    return isinstance(value, list) and (bool(value) or not nonempty) and all(text(v) for v in value)


def declaration(tag, audits=False):
    specs = [("fairness", tag), ("sq", tag + "a"), ("sq", tag + "b"),
             ("dq", tag), ("ar", tag), ("verify", tag)]
    if audits:
        specs += [("ref-audit", tag + "ra"), ("ref-audit", tag + "rb")]
    return {"checkpoint": tag, "reports": [
        {"kind": kind, "file": f"{kind}-{sample}.json", "source": f"{kind}-{sample}"}
        for kind, sample in specs]}


def validate(kind, report):
    for field in {"sq": ("summary", "overall_feedback"), "fairness": ("taskSummary", "overall"),
                  "dq": ("summary",), "ar": ("summary", "authorGuidance"),
                  "verify": ("summary",), "ref-audit": ("summary",)}[kind]:
        require(text(report.get(field)), f"missing/invalid {field}")
    if kind in ("sq", "fairness", "dq"):
        require(report.get("verdict") in ("PASS", "FAIL"), "missing/invalid verdict")
    if kind == "sq":
        require(strings(report.get("promises"), True), "invalid/missing promises")
        for key, fields in (("branchInventory", ("function", "branch", "effectOnPromisedState")),
                            ("exitAfterMutation", ("function", "exit", "stateAlreadyChanged")),
                            ("modeFailureMatrix", ("mode", "success", "errorBeforeHandle", "errorAfter", "timeout", "cancel")),
                            ("breakAttempts", ("promise", "scenario", "trace", "result", "why"))):
            for row in rows(report, key, key in ("modeFailureMatrix", "breakAttempts")):
                require(all(text(row.get(field)) for field in fields), f"invalid {key} row")
        for key in ("solution_comprehensiveness", "code_quality"):
            require(isinstance(report.get(key), dict) and score(report[key].get("score")),
                    f"missing/invalid {key}.score")
            require(report[key].get("max_score") == 3 and text(report[key].get("level"))
                    and text(report[key].get("reasoning")), f"invalid {key} details")
        for issue in rows(report, "issues"):
            require(text(issue.get("title")) and issue.get("severity") in SEVERITIES
                    and issue.get("criterion") in ("comprehensiveness", "quality")
                    and all(text(issue.get(field)) for field in ("detail", "evidence", "failingCase", "disproofTried")),
                    "invalid SQ issue")
    elif kind == "fairness":
        for row in rows(report, "requirements", True):
            require(text(row.get("requirement")) and text(row.get("sourceQuote"))
                    and row.get("covered") in ("yes", "partial", "no")
                    and strings(row.get("coveringTests")), "invalid requirement")
        for row in rows(report, "tests", True):
            require(text(row.get("name")) and row.get("fairness") in FAIRNESS
                    and strings(row.get("concerns")) and text(row.get("evidence"))
                    and text(row.get("verifies")), "invalid test")
        for row in rows(report, "coverageSuggestions"):
            require(text(row.get("requirement")) and text(row.get("suggestion"))
                    and row.get("sourceIfAdded") in ("Prompt-stated", "Repo-discoverable", "Would need prompt edit"),
                    "invalid coverage suggestion")
        require(type(report.get("unfairTestCount")) is int, "missing unfairTestCount")
        require(report["unfairTestCount"] == sum(t["fairness"] == "Unfair" for t in report["tests"]),
                "unfairTestCount contradicts tests")
    elif kind == "dq":
        for row in rows(report, "comments"):
            require(text(row.get("quote")) and row.get("severity") in SEVERITIES
                    and type(row.get("presentationOnly")) is bool, "invalid DQ comment")
        count = report.get("requirementCount")
        require(isinstance(count, dict) and type(count.get("count")) is int and count["count"] >= 0
                and type(count.get("blocking")) is bool, "invalid requirementCount")
        require(strings(report.get("requirements"), True), "invalid DQ requirements")
        basis = report.get("verdictBasis")
        require(isinstance(basis, dict) and all(type(basis.get(k)) is int and basis[k] >= 0
                                              for k in ("majors", "minors")), "invalid verdictBasis")
        criteria = rows(report, "taskCriteria", True)
        require(len(criteria) == 8 and {r.get("id") for r in criteria} == {f"{i:02}" for i in range(1, 9)}
                and all(r.get("verdict") in ("PASS", "FAIL") and text(r.get("note")) for r in criteria),
                "invalid taskCriteria")
        prechecks = report.get("prechecks")
        require(isinstance(prechecks, dict)
                and all(type(prechecks.get(k)) is bool for k in ("ascii", "noUrls"))
                and type(prechecks.get("words")) is int and prechecks["words"] >= 0
                and prechecks.get("categorySuggested") in ("bugfix", "feature_request"), "invalid prechecks")
    elif kind == "ar":
        for key in ("description", "tests", "solution"):
            require(isinstance(report.get(key), dict) and score(report[key].get("band")), f"invalid AR {key}")
            require(text(report[key].get("confidence")) and text(report[key].get("reasoning")),
                    f"invalid AR {key} details")
        require(report.get("outcome") in ("approved", "revision_requested"), "invalid AR outcome")
        for row in rows(report, "issues"):
            require(text(row.get("claim")) and row.get("severity") in SEVERITIES
                    and text(row.get("category")) and isinstance(row.get("evidence"), dict)
                    and row["evidence"], "invalid AR issue")
    elif kind == "verify":
        kept = report.get("kept")
        require(isinstance(kept, dict) and set(kept) == KEPT
                and all(type(v) is int and v >= 0 for v in kept.values()), "invalid kept counts")
        bands = report.get("bandsAfterVerification")
        require(isinstance(bands, dict) and all(score(bands.get(k)) for k in ("description", "tests", "solution")),
                "invalid verified bands")
        for row in rows(report, "verdicts"):
            require(text(row.get("source")) and text(row.get("id")) and text(row.get("evidence"))
                    and row.get("severity") in SEVERITIES
                    and row.get("decision") in ("KEEP", "DROP"), "invalid verification disposition")
            if row["decision"] == "DROP":
                require(row.get("dropReason") in ("reading", "today", "scope", "realism", "code", "duplicate", "combination"),
                        "DROP lacks a supported reason")
    elif kind == "ref-audit":
        for row in rows(report, "promises", True):
            require(text(row.get("promise")) and row.get("verdict") in ("HOLDS", "BROKEN", "NOT VERIFIED"),
                    "invalid reference promise")
            require(strings(row.get("paths"), True) and type(row.get("reproduced")) is bool,
                    "invalid reference paths/reproduction")


def findings(kind, report):
    found = set()
    if kind in ("sq", "ar"):
        found.update(row["title" if kind == "sq" else "claim"] for row in report["issues"])
    elif kind == "fairness":
        found.update(r["requirement"] for r in report["requirements"] if r["covered"] != "yes")
        found.update(t["name"] for t in report["tests"] if t["fairness"] == "Unfair" or t["concerns"])
        found.update(s["requirement"] for s in report["coverageSuggestions"]
                     if s["sourceIfAdded"] != "Would need prompt edit")
    elif kind == "dq":
        found.update(row["quote"] for row in report["comments"])
    elif kind == "ref-audit":
        found.update(r["promise"] for r in report["promises"]
                     if r["verdict"] != "HOLDS" or r.get("wrongImplementationThatPassesTests"))
    return found


def merge_sq(folder, tag):
    folder = Path(folder)
    samples = []
    union = {}
    for suffix in ("a", "b"):
        path = folder / f"sq-{tag}{suffix}.json"
        report = read(path)
        validate("sq", report)
        source = path.stem
        samples.append((source, report, hashlib.sha256(path.read_bytes()).hexdigest()))
        for index, issue in enumerate(report["issues"]):
            key = json.dumps(issue, sort_keys=True)
            merged = union.setdefault(key, {**issue, "sources": []})
            merged["sources"].append({"source": source, "id": issue["title"], "index": index})
    merged = {"issues": list(union.values()),
              "sourceReports": [{"source": s, "sha256": h} for s, _, h in samples],
              "verdict": "PASS" if all(r["verdict"] == "PASS" for _, r, _ in samples) else "FAIL"}
    for key in ("solution_comprehensiveness", "code_quality"):
        merged[key] = {"score": min(r[key]["score"] for _, r, _ in samples)}
    write(folder / f"sq-{tag}.json", merged)
    return merged


def gate(folder, manifest):
    require(text(manifest.get("checkpoint")), "checkpoint identity missing")
    specs = rows(manifest, "reports", True)
    for kind, minimum in (("fairness", 1), ("sq", 2), ("dq", 1), ("ar", 1), ("verify", 1)):
        require(sum(spec.get("kind") == kind for spec in specs) >= minimum,
                f"checkpoint must require {minimum} {kind} report(s)")
    reports = []
    sources = set()
    files = set()
    for spec in specs:
        kind, filename, source = spec.get("kind"), spec.get("file"), spec.get("source")
        require(kind in KINDS and text(filename) and Path(filename).name == filename
                and text(source) and source not in sources and filename not in files,
                "invalid/duplicate report declaration")
        sources.add(source)
        files.add(filename)
        report = read(Path(folder) / filename)
        try:
            validate(kind, report)
        except ValueError as exc:
            raise ValueError(f"{filename}: {exc}") from exc
        reports.append((source, kind, report))
    pending = {(source, ident) for source, kind, report in reports for ident in findings(kind, report)}
    decisions = {}
    problems = []
    for source, kind, report in reports:
        if kind == "verify":
            if any(report["kept"].values()):
                problems.append(f"{source}: kept in-scope findings")
            if any(value != 3 for value in report["bandsAfterVerification"].values()):
                problems.append(f"{source}: verified bands must all be 3")
            for row in report["verdicts"]:
                key = (row["source"], row["id"])
                require(key in pending, f"unexpected verification ID: {key}")
                require(key not in decisions, f"duplicate verification ID: {key}")
                decisions[key] = row["decision"]
        elif kind == "dq":
            if (report["verdict"] != "PASS" or report["requirementCount"]["blocking"]
                    or any(r["verdict"] != "PASS" for r in report["taskCriteria"])
                    or not report["prechecks"]["ascii"] or not report["prechecks"]["noUrls"]
                    or report["prechecks"]["words"] >= 250):
                problems.append(f"{source}: DQ/task/precheck failure")
        elif kind == "sq":
            for field, criterion in (("solution_comprehensiveness", "comprehensiveness"), ("code_quality", "quality")):
                if report[field]["score"] < 3 and not any(i["criterion"] == criterion for i in report["issues"]):
                    problems.append(f"{source}: unexplained {field} score")
            if report["verdict"] == "FAIL" and not report["issues"]:
                problems.append(f"{source}: unexplained SQ failure")
        elif kind == "ar":
            for field, prefix in (("description", "P"), ("tests", "T"), ("solution", "S")):
                if report[field]["band"] < 3 and not any(i["category"].startswith(prefix) for i in report["issues"]):
                    problems.append(f"{source}: unexplained {field} band")
            if report["outcome"] != "approved" and not report["issues"]:
                problems.append(f"{source}: unexplained AR rejection")
        elif kind == "fairness" and report["verdict"] != "PASS" and not findings(kind, report):
            problems.append(f"{source}: unexplained fairness failure")
    for key in sorted(pending):
        if decisions.get(key) != "DROP":
            problems.append(f"unresolved finding [{key[0]}] {key[1]}")
    return problems, sorted(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("tag")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--declare", action="store_true")
    parser.add_argument("--ref-audits", action="store_true")
    parser.add_argument("--merge-sq", action="store_true")
    args = parser.parse_args()
    try:
        path = args.checkpoint or args.folder / f"checkpoint-{args.tag}.json"
        if args.declare:
            args.folder.mkdir(parents=True, exist_ok=True)
            audits = args.ref_audits
            if path.exists():
                previous = read(path)
                require(previous.get("checkpoint") == args.tag, "checkpoint tag mismatch")
                audits = audits or any(r.get("kind") == "ref-audit" for r in rows(previous, "reports", True))
            write(path, declaration(args.tag, audits))
            print(f"Declared required reports: {path}")
            return 0
        if args.merge_sq:
            merge_sq(args.folder, args.tag)
            return 0
        manifest = read(path) if path.exists() else declaration(args.tag, args.ref_audits)
        require(manifest.get("checkpoint") == args.tag, "checkpoint tag mismatch")
        problems, union = gate(args.folder, manifest)
        print(f"# Checkpoint {args.tag}\n")
        print("Required reports: " + ", ".join(r["file"] for r in manifest["reports"]))
        for source, ident in union:
            print(f"- finding [{source}] {ident}")
        for problem in problems:
            print(f"- FAIL: {problem}")
        print("\nGATE " + ("FAIL" if problems else "PASS"))
        return int(bool(problems))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"GATE FAIL: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
