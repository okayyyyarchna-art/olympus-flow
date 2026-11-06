"""Readable digest of `olympus problems view --json` files (read-only data from the platform).

Usage: python digest.py <platform-data dir> <out dir>
Writes one <out>/<id10>-<slug>.md per challenge plus <out>/INDEX.md.
"""
import glob
import json
import os
import re
import sys


def txt(x, n=None):
    s = "" if x is None else str(x)
    return s if n is None else s[:n]


def runs_of(d):
    r = (d.get("runs") or {}).get("agentRuns") or []
    return r if isinstance(r, list) else list(r.values())


def check_section(key, v):
    o = v.get("output") or {}
    ev = o.get("evaluation") or {}
    out = [f"### {key}: {v.get('status')} / {o.get('verdict') or ev.get('verdict')}" + (" (stale)" if v.get("stale") else "")]
    if v.get("error"):
        out.append(f"- error: {v['error']}")
    if key == "autoReview":
        out.append(f"- outcome: {o.get('outcome')}; scope: {(o.get('effectiveScope') or {}).get('verdict')}")
        for part in ("description", "tests", "solution"):
            p = o.get(part) or {}
            out.append(f"- **{part}** band {p.get('band')} ({p.get('confidence')}): {txt(p.get('reasoning'))}")
            for f in p.get("findings") or p.get("issues") or []:
                out.append(f"  - finding: {json.dumps(f, ensure_ascii=False)}")
        out.append(f"- summary: {txt(o.get('summary'))}")
        out.append(f"- authorGuidance: {txt(o.get('authorGuidance'))}")
        out.append(f"- otherNotes: {txt(o.get('otherNotes'))}")
        extra = {k: o[k] for k in o if k not in ("description", "tests", "solution", "summary", "authorGuidance",
                                                   "otherNotes", "outcome", "effectiveScope", "completed",
                                                   "executionTimeSeconds", "otherNotesTags")}
        if extra:
            out.append(f"- other fields: {json.dumps(extra, ensure_ascii=False)[:3000]}")
    elif key == "taskQuality":
        for c in ev.get("criteria") or []:
            out.append(f"- [{c.get('verdict') or c.get('result') or c.get('status')}] **{c.get('name') or c.get('criterion') or c.get('id')}**: {txt(c.get('reasoning') or c.get('explanation'))}")
        out.append(f"- summary: {txt(ev.get('summary'))}")
    elif key == "solutionQuality":
        for part in ("solution_comprehensiveness", "code_quality"):
            p = ev.get(part) or {}
            out.append(f"- **{part}** {p.get('score')}/{p.get('max_score')} {p.get('level')}: {txt(p.get('reasoning'))}")
        for i in ev.get("issues") or []:
            out.append(f"  - issue: {json.dumps(i, ensure_ascii=False)}")
        out.append(f"- overall: {txt(ev.get('overall_feedback'))}")
    elif key == "descriptionQuality":
        out.append(f"- requirementCount: {json.dumps(ev.get('requirementCount'), ensure_ascii=False)}")
        out.append(f"- verdictBasis: {json.dumps(ev.get('verdictBasis'), ensure_ascii=False)}")
        for c in ev.get("comments") or []:
            out.append(f"  - comment: {json.dumps(c, ensure_ascii=False)}")
        out.append(f"- summary: {txt(ev.get('summary'))}")
        rest = {k: ev[k] for k in ev if k not in ("requirementCount", "verdictBasis", "comments", "summary", "verdict")}
        if rest:
            out.append(f"- other: {json.dumps(rest, ensure_ascii=False)[:2000]}")
    elif key == "verifyFairness":
        out.append(f"- message: {txt(o.get('message'))}; unfair: {o.get('unfairTestCount')}")
        out.append(f"- taskSummary: {txt(o.get('taskSummary'))}")
        reqs = o.get("requirements") or []
        out.append(f"- requirements extracted: {len(reqs)}")
        for r in reqs:
            out.append(f"  - {json.dumps(r, ensure_ascii=False)}")
        for t in o.get("tests") or []:
            fair = t.get("fair", t.get("verdict"))
            if fair not in (True, "fair", "FAIR"):
                out.append(f"  - UNFAIR test: {json.dumps(t, ensure_ascii=False)}")
        out.append(f"- tests judged: {len(o.get('tests') or [])}")
        for c in o.get("coverageSuggestions") or []:
            out.append(f"  - coverage suggestion: {json.dumps(c, ensure_ascii=False)}")
        out.append(f"- overall: {txt(o.get('overall'))}")
    elif key in ("verifyTests", "verifySolution", "verifyBuild", "verifyFlakiness"):
        keep = {k: o[k] for k in o if k not in ("passToPassTests", "failToPassTests", "harborTaskFiles", "completed")}
        out.append(f"- {json.dumps(keep, ensure_ascii=False)[:1500]}")
    else:
        out.append(f"- {json.dumps(o, ensure_ascii=False)[:4000]}")
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    os.makedirs(dst, exist_ok=True)
    index = ["| id | status | ver | title | AR (D/T/S) | TQ | SQ | DQ | fairness reqs | rollout | runs |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in sorted(glob.glob(os.path.join(src, "view-*.json"))):
        d = json.load(open(f, encoding="utf-8-sig"))
        lv = d.get("latestVersion") or {}
        checks = d.get("checks") or {}
        dc = checks.get("dynamicChecks") or {}
        runs = runs_of(d)
        title = d.get("title") or ""
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:40].strip("-") or "untitled"
        name = f"{d['_id'][:10]}-{slug}.md"
        L = [f"# {title}", "", f"- id {d['_id']}, status **{d.get('status')}**, version v{lv.get('version')}"
             f" ({'locked' if lv.get('isLocked') else 'unlocked'}), category {lv.get('category')}, difficulty {lv.get('difficulty')}",
             f"- repo {lv.get('githubRepoUrl')} @ {lv.get('githubCommitHash')}", ""]
        if lv.get("description"):
            words = len(re.split(r"[\s\-/]+", lv["description"].strip()))
            L += [f"## Description ({words} site words)", "", lv["description"].strip(), ""]
        L.append("## Readiness")
        rd = checks.get("readiness") or {}
        for c in rd.get("criteria") or []:
            L.append(f"- [{c.get('status')}] {c.get('label')}: {c.get('detail') or ''}")
        L += ["", "## Prechecks"]
        for s in checks.get("stages") or []:
            L.append(f"- {s.get('stageName') or s.get('stageId')}: {s.get('status')}")
            for c in s.get("checks") or []:
                L.append(f"  - [{c.get('status')}] {c.get('name') or c.get('key')}: {txt(c.get('message'))}")
        L += ["", "## Quality checks"]
        flags = {k: v for k, v in dc.items() if k.startswith("_") and v not in (None, False)}
        if flags:
            L.append(f"- flags: {json.dumps(flags)}")
        for k, v in dc.items():
            if not k.startswith("_") and isinstance(v, dict):
                L += check_section(k, v)
        L += ["", "## Rollout criteria"]
        crit = (d.get("runs") or {}).get("criteria") or {}
        for c in crit.get("criteria") or []:
            L.append(f"- [{c.get('status')}] {c.get('label')}: {c.get('detail') or ''} (target: {c.get('description') or ''})")
            if c.get("guidance"):
                L.append(f"  - guidance: {c['guidance']}")
        L.append(f"- computedDifficulty: {crit.get('computedDifficulty')}")
        L += ["", "## Runs", "", "| solver | eval | verdict | status | stale | seq len | fault | env blocker | summary |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(runs, key=lambda r: (bool(r.get("stale")), r.get("createdAt") or 0)):
            o = r.get("output") or {}
            L.append("| {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r.get("taskAgentCodename") or r.get("taskAgentType"), r.get("evalAgentCodename") or r.get("evalAgentType"),
                r.get("verdict") or o.get("verdict"), r.get("status"), "stale" if r.get("stale") else "",
                o.get("sequenceLength"), txt(r.get("fault"), 60), txt(o.get("environmentBlocker"), 60),
                txt(o.get("summary"), 300).replace("|", "/").replace("\n", " ")))
        L += ["", "## Reviews"]
        for rv in d.get("reviews") or []:
            L.append(f"- {rv.get('outcome')} (v{rv.get('versionNumber')}), quality {rv.get('overallQuality')}, bands {json.dumps(rv.get('fieldBands'))}")
            L.append(f"  - feedback: {txt(rv.get('feedback'))}")
            rest = {k: rv[k] for k in rv if k not in ("feedback", "fieldBands", "otherNotes", "outcome", "overallQuality", "versionNumber", "reviewerName", "submittedAt")}
            if rest:
                L.append(f"  - other: {json.dumps(rest, ensure_ascii=False)[:1500]}")
        open(os.path.join(dst, name), "w", encoding="utf-8").write("\n".join(L) + "\n")

        def v(k):
            o = (dc.get(k) or {}).get("output") or {}
            return o.get("verdict") or (o.get("evaluation") or {}).get("verdict") or (dc.get(k) or {}).get("status") or ""
        ar = (dc.get("autoReview") or {}).get("output") or {}
        bands = "/".join(str((ar.get(p) or {}).get("band", "")) for p in ("description", "tests", "solution")) if ar else ""
        fr = len(((dc.get("verifyFairness") or {}).get("output") or {}).get("requirements") or [])
        ps = next((c.get("detail") for c in crit.get("criteria") or [] if c.get("id") == "passStructure"), "")
        index.append(f"| {d['_id'][:10]} | {d.get('status')} | v{lv.get('version')} | [{title[:50]}]({name}) | {bands} | {v('taskQuality')} | {v('solutionQuality')} | {v('descriptionQuality')} | {fr or ''} | {ps} | {len(runs)} |")
    open(os.path.join(dst, "INDEX.md"), "w", encoding="utf-8").write("\n".join(index) + "\n")


if __name__ == "__main__":
    main()
