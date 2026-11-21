#!/usr/bin/env python3
"""Make the build checklist get applied rule by rule (prompts/apply-build-checklist.md).

usage: checklist_gate.py sheet <task-dir>
       checklist_gate.py check <task-dir> --through 5|7|8
sheet writes <task>/eval/checklist-run.md, one row per rule of build-checklist.md, and keeps rows already filled.
check fails on a blank row, a row with no real location, an NA without a reason, and a Blueprint cell that is blank or
closed without a test, a quoted sentence or a proof. It shows the work was recorded; a reviewer checks it is true.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys

CHECKLIST = Path(__file__).resolve().parents[1] / "build-checklist.md"
ROW_ID = r"\b[CPVFM]\d{2,}\b"
LOCATOR = re.compile(ROW_ID + r"|[\w./-]+\.[a-z]{1,8}\b|\b[Tt]est\w+")
PLACEHOLDER = {"", "fill", "todo", "tbd", "?", "-"}
AXES = ("Entry point", "Change kind or mode", "Copy or data state", "Lifecycle edge", "Expected result")


def rules(text):
    found, counts, section, current = [], {}, 0, None
    for line in text.splitlines():
        heading = re.match(r"## (\d+)\. ", line)
        if line.startswith("## "):
            section, current = int(heading[1]) if heading else 0, None
            if section == 10:
                found.append({"section": 6, "id": "10.1", "text": "Never list: nothing in section 10 was done"})
            continue
        if not 1 <= section <= 8:
            continue
        start = re.match(r"(?:- |\d+\. |  - )(.*)", line)
        if start:
            counts[section] = counts.get(section, 0) + 1
            current = {"section": section, "id": f"{section}.{counts[section]}", "text": start[1]}
            found.append(current)
        elif current and line.startswith(" ") and line.strip():
            current["text"] += " " + line.strip()
        else:
            current = None
    return found


def key(rule):
    return hashlib.sha256(rule["text"].encode()).hexdigest()[:8]


def cells(line):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def table_rows(text):
    return [row for row in (cells(line) for line in text.splitlines() if line.lstrip().startswith("|"))
            if row and not set(row[0]) <= set("-: ")]


def section_text(text, title):
    match = re.search(rf"^## {re.escape(title)}.*?(?=^## |\Z)", text, re.M | re.S)
    return match[0] if match else ""


def sheet_path(task):
    return task / "eval/checklist-run.md"


def read_sheet(path):
    rows = {}
    for row in table_rows(path.read_text(encoding="utf-8")):
        if len(row) >= 2 and row[0] != "Rule":
            # A stray | splits a cell: the row has more than 7 cells (BACKLOG 167). The check names the count; the
            # sheet command folds the surplus back into Note and writes every | as \|.
            values = (row[4:7] + ["", "", ""])[:3]
            if len(row) > 7:
                values[2] = " | ".join(row[6:])
            rows[row[1]] = {"id": row[0], "status": values[0], "where": values[1], "note": values[2], "cells": len(row)}
    return rows


def make_sheet(task):
    data = CHECKLIST.read_bytes()
    path = sheet_path(task)
    old = read_sheet(path) if path.exists() else {}
    lines = ["# Build checklist, applied rule by rule", "",
             f"checklist sha256: {hashlib.sha256(data).hexdigest()}", "",
             "Status: APPLIED (Where = ledger row, test or file:line) or NA (Note = why it cannot apply to this task).", "",
             "| Rule | Key | Stage | What the rule says (read it in full in build-checklist.md) | Status | Where | Note |",
             "|---|---|---|---|---|---|---|"]
    found = rules(data.decode("utf-8"))
    for rule in found:
        previous = {k: v.replace("|", "\\|") for k, v in old.get(key(rule), {}).items() if isinstance(v, str)}
        summary = rule["text"][:100].replace("|", "\\|")
        lines.append(f"| {rule['id']} | {key(rule)} | {rule['section']} | {summary} | {previous.get('status', '')} "
                     f"| {previous.get('where', '')} | {previous.get('note', '')} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{path}: {len(found)} rules, {sum(key(r) in old for r in found)} kept from the earlier sheet")
    blanked = [rule["id"] for rule in found if key(rule) not in old]
    if old and blanked:
        print("blank rows (rule text changed or rule new since the earlier sheet): " + ", ".join(blanked))
    return 0


def package_file(task, *names):
    for folder in (task / "pkg", task):
        for name in names:
            if (folder / name).exists():
                return folder / name
    return None


def flat(text):
    return " ".join(text.split())


def check_sheet(task, through):
    path, problems = sheet_path(task), []
    if not path.exists():
        return [f"{path} is missing: run the sheet command"], {}
    if f"checklist sha256: {hashlib.sha256(CHECKLIST.read_bytes()).hexdigest()}" not in path.read_text(encoding="utf-8"):
        problems.append("the checklist changed since this sheet was made: run the sheet command again")
    rows, ledger_ids, counts = read_sheet(path), set(), {"APPLIED": 0, "NA": 0}
    ledger = task / "ledger.md"
    if ledger.exists():
        ledger_ids = {row[0].split()[0] for row in table_rows(ledger.read_text(encoding="utf-8"))
                      if re.fullmatch(ROW_ID, row[0].split(" ")[0] if row[0] else "")}
    for rule in rules(CHECKLIST.read_text(encoding="utf-8")):
        if rule["section"] > through:
            continue
        row = rows.get(key(rule))
        if row is None:
            problems.append(f"rule {rule['id']}: no row in the sheet")
        elif row["cells"] != 7:
            problems.append(f"row {rule['id']} has {row['cells']} cells, expected 7 (a | in a cell? write it as \\| or rerun the sheet command)")
        elif row["status"] == "NA":
            counts["NA"] += 1
            if len(row["note"]) < 15:
                problems.append(f"rule {rule['id']}: NA needs a reason in Note")
        elif row["status"] == "APPLIED":
            counts["APPLIED"] += 1
            if not LOCATOR.search(row["where"]):
                problems.append(f"rule {rule['id']}: Where must name a ledger row, a test or a file, not {row['where']!r}")
            for cited in re.findall(ROW_ID, row["where"]):
                if cited not in ledger_ids:
                    problems.append(f"rule {rule['id']}: {cited} is not a row of ledger.md")
        else:
            problems.append(f"rule {rule['id']}: not filled")
    return problems, counts


def check_blueprint(task, through):
    ledger = task / "ledger.md"
    if not ledger.exists():
        return [f"{ledger} is missing: copy ledger-template.md"]
    text = ledger.read_text(encoding="utf-8")
    blueprint = table_rows(section_text(text, "Blueprint"))
    if not blueprint or blueprint[0][:2] != ["Cell", "Contract"] or len(blueprint) < 2:
        return ["ledger.md has no filled Blueprint table"]
    problems, names, covered = [], {row[0] for row in blueprint[1:]}, set()
    description = package_file(task, "description.md", "task.md")
    wording = flat(description.read_text(encoding="utf-8")) if description else ""
    patch_file = package_file(task, "test.patch")
    patch = patch_file.read_text(encoding="utf-8", errors="replace") if patch_file else ""
    for row in blueprint[1:]:
        label = f"blueprint {row[0]}"
        if len(row) != 8:
            problems.append(f"{label}: expected 8 columns")
            continue
        covered.update(re.findall(r"\bC\d{2,}\b", row[1]))
        for name, value in zip(("Contract", *AXES), row[1:7]):
            if value.lower() in PLACEHOLDER:
                problems.append(f"{label}: {name} is blank")
        kind, _, rest = row[7].partition(" ")
        if kind == "TESTED":
            test = rest.split(" ")[0]
            if not test:
                problems.append(f"{label}: TESTED needs a test name")
            elif through >= 7 and test not in patch:
                problems.append(f"{label}: {test} is not in test.patch")
        elif kind == "OUT":
            quote = re.search(r'"([^"]+)"', rest)
            if quote:
                if flat(quote[1]) not in wording:
                    problems.append(f"{label}: the quote is not in the description")
            elif not (rest.startswith("unreachable") and LOCATOR.search(rest)):
                problems.append(f'{label}: OUT needs "a quoted sentence" or: unreachable <file:line>')
        elif kind == "SAME":
            target, _, reason = rest.partition(" ")
            if target not in names or target == row[0]:
                problems.append(f"{label}: SAME must name another cell")
            if len(reason) < 10:
                problems.append(f"{label}: SAME needs the reason this cell behaves like {target}")
        else:
            problems.append(f"{label}: Disposition must be TESTED, OUT or SAME")
    for row in table_rows(section_text(text, "Contract and meanings")):
        if re.fullmatch(r"C\d{2,}", row[0]) and row[-1] != "OUT" and row[0] not in covered:
            problems.append(f"contract {row[0]}: no Blueprint cell")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("sheet", "check"))
    parser.add_argument("task", type=Path)
    parser.add_argument("--through", type=int, choices=(5, 7, 8), default=5)
    args = parser.parse_args()
    if args.command == "sheet":
        return make_sheet(args.task)
    problems, counts = check_sheet(args.task, args.through)
    problems += check_blueprint(args.task, args.through)
    for problem in problems:
        print(f"- FAIL: {problem}")
    print(f"rules through step {args.through}: {counts.get('APPLIED', 0)} APPLIED, {counts.get('NA', 0)} NA")
    print("CHECKLIST GATE " + ("FAIL" if problems else "PASS"))
    return int(bool(problems))


if __name__ == "__main__":
    sys.exit(main())
