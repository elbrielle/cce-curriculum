#!/usr/bin/env python3
"""Report-only audit of Canvas guide templates against the CCE module-authoring harness.

Usage: /usr/bin/python3 build/canvas/audit_module_language.py wk1 wk2 [--out path.md]
Checks: student banned list, teacher banned list, outage/absence logic on student pages,
structure caps (today-you-will, steps, done-when), at-a-glance presence, notebook job
count, implementer narration, em dashes, AI-cliche vocabulary, image count.
Harness: build/codex-skills/cce-module-authoring/SKILL.md
"""
import html, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "build/canvas/templates"

STUDENT_BANNED = [
    (r"\bprovisional\b", "teacher logic: provisional"),
    (r"\bcatch[- ]up\b", "teacher logic: catch-up"),
    (r"\bfixed (value )?list\b", "teacher fallback: fixed list"),
    (r"\bverif(y|ication)\b", "implementer: verification"),
    (r"\brecop(y|ied|ying)\b", "implementer: recopy"),
    (r"\bautosave\b", "obsolete autosave test"),
    (r"\bdistribut(e|ed|ion)\b", "OneNote mechanics: distribute"),
    (r"content library", "OneNote mechanics: Content Library"),
    (r"table cell|1\s*[x×]\s*1", "OneNote mechanics: table cell"),
    (r"\btemplate\b", "implementer: template"),
    (r"\bmodule\b", "implementer: module"),
    (r"\bembed(ded)?\b", "implementer: embed"),
    (r"\bpublish(ed)?\b", "implementer: publish"),
    (r"\broutes?\b", "teacher logic: route"),
    (r"\bfallback\b", "teacher logic: fallback"),
    (r"unavailable|not working|is down|cannot load|won't load|will not load", "outage logic on student page"),
    (r"\bTEKS\b|\b\d{3}\.\d+\b|\(d\)\(\d\)", "TEKS code in student text"),
    (r"\bCore [A-Z]\b", "internal lesson code"),
    (r"\bminors?\b|\bmajors?\b", "gradebook admin"),
    (r"\bMr\.? Lucero\b|\bMs\.? Lucero\b|\bLucero\b", "teacher name on shared material"),
    (r"\bminutes?\s*\d+\s*[-–]\s*\d+|\bminute \d+\b", "timing language"),
    (r"\bteacher will\b|\byour teacher (may|might|will decide)\b", "teacher move narrated to students"),
]
TEACHER_BANNED = [
    (r"this guide contains the full lesson", "artifact narration"),
    (r"speaker notes include", "artifact narration"),
    (r"default copies", "build artifact language"),
    (r"native\s+1\s*[x×]\s*1|table cell", "OneNote mechanics in lesson guide"),
    (r"without a separate verification|recopying step", "implementer residue"),
    (r"view distributed pages", "OneNote mechanics"),
    (r"\bpage id\b|\bmodule id\b|\bfile id\b|\bAPI\b|\bHTML\b|\bJSON\b", "implementer talk"),
    (r"\bCore [A-Z]\b", "internal lesson code"),
    (r"\bClassLink\b", "obsolete sign-in route"),
    (r"\bautosave\b", "obsolete autosave test"),
]
AI_CLICHE = [
    (r"\b(dive|diving) (in|into)\b", "cliche"), (r"\bunlock(s|ed|ing)?\b", "cliche"), (r"\bempower(s|ed|ing|ment)?\b", "cliche"),
    (r"\bjourney\b", "cliche"), (r"\bdelve\b", "cliche"), (r"\bleverage\b", "cliche"), (r"\bseamless(ly)?\b", "cliche"),
    (r"\brobust\b", "cliche"), (r"\bharness\b", "cliche"), (r"\bfoster(s|ed|ing)?\b", "cliche"), (r"\bnavigate\b", "cliche"),
    (r"\belevate\b", "cliche"), (r"\bcrucial\b", "cliche"), (r"\bnot (just|only) [^.]{3,40}, but\b", "negative parallelism"),
    (r"\bconsider (using|trying|asking)\b", "hedged instruction"), (r"\byou might (want to|try)\b", "hedged instruction"),
]
AT_A_GLANCE = ["objective", "demonstration of learning|DOL|exit evidence|you are done when", "workbook|FYF|pp\\.", "H&L|Hats|Xello|platform", "notebook|journal|OneNote", "slides|presentation|PowerPoint", "scaffold|differentiation|word bank|support", "exit ticket|exit evidence|demonstration"]

def text_of(path):
    s = path.read_text()
    imgs = len(re.findall(r"<img\b", s, re.I))
    details = re.findall(r"<details.*?</details>", s, re.S | re.I)
    body = re.sub(r"<(style|script).*?</\1>", "", s, flags=re.S | re.I)
    body = html.unescape(re.sub(r"<[^>]+>", "\n", body))
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    return s, lines, imgs, details

def scan(lines, patterns):
    hits = []
    for i, l in enumerate(lines, 1):
        for pat, why in patterns:
            if re.search(pat, l, re.I):
                hits.append((i, why, l[:110]))
    return hits

def count_block(lines, header_pat, stop_pat=r"^(\d+\.|[A-Z][^.]{0,40}$)"):
    for i, l in enumerate(lines):
        if re.search(header_pat, l, re.I):
            n = 0
            for m in lines[i + 1:]:
                if re.match(stop_pat, m) and not m.lower().startswith(("open", "use", "write", "return", "complete", "in ", "choose", "read", "save", "find", "sign")):
                    break
                n += 1
            return n
    return None

def audit_week(wk):
    out = [f"# Module language audit: {wk}\n", "Report only. Harness: `build/codex-skills/cce-module-authoring/SKILL.md`.\n"]
    files = [TPL / f"{wk}-teacher.html"] + [TPL / f"{wk}-day{d}-student.html" for d in range(1, 6)]
    summary = []
    for f in files:
        if not f.exists():
            out.append(f"## {f.name}\nMissing.\n"); continue
        raw, lines, imgs, details = text_of(f)
        role = "teacher" if "teacher" in f.name else "student"
        out.append(f"## {f.name}  ({len(lines)} text lines, {imgs} img tags, {len(details)} details blocks)\n")
        if role == "student":
            hits = scan(lines, STUDENT_BANNED)
            steps = len([l for l in lines if re.match(r"^\d+\.\s", l)])
            tyw = count_block(lines, r"^today you will")
            done = count_block(lines, r"^you are done when")
            absent = [l for l in lines if re.search(r"absent|unavailable|not working", l, re.I)]
            em = [l for l in lines if "—" in l]
            out.append(f"- numbered steps: {steps} (cap 7); today-you-will bullets: {tyw} (cap 4); done-when checks: {done} (cap 3)")
            if absent: out.append(f"- absence/outage block present: `{absent[0][:90]}`")
            if em: out.append(f"- em dashes in student text: {len(em)}")
            ai = scan(lines, AI_CLICHE)
            out.append(f"- student banned-list hits: {len(hits)}; AI-cliche hits: {len(ai)}")
            for i, why, l in hits: out.append(f"  - L{i} [{why}] {l}")
            for i, why, l in ai: out.append(f"  - L{i} [{why}] {l}")
            summary.append((f.name, len(hits), len(ai), steps, done, bool(absent), imgs))
        else:
            bs = ROOT / f"build/canvas/build_{wk}.py"
            if bs.exists():
                src = bs.read_text()
                strs = re.findall(r'"((?:[^"\\]|\\.){40,})"', src)
                extra = []
                for t in strs:
                    if "\n" in t or re.search(r"await |api\(|raise |import |\{[a-z_]+\[", t) and not re.search(r"[a-z]{4,} [a-z]{4,} [a-z]{4,}", t): continue
                    if t.startswith("{") or re.search(r"Expected one|Refusing|preflight|invariant|did not remain|drifted", t): continue
                    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
                    extra += [x.strip() for x in re.split(r"(?<=[.!?])\s+", t) if x.strip()]
                lines = lines + extra
                out.append(f"- teacher text also pulled from {bs.name}: {len(extra)} sentences")
            hits = scan(lines, TEACHER_BANNED + [(r"embedded|response home|digital location|response route|licensed visuals", "implementer phrasing")])
            ai = scan(lines, AI_CLICHE)
            glance = [p for p in AT_A_GLANCE if not any(re.search(p, l, re.I) for l in lines[:40])]
            stems = [l for l in lines if re.search(r"____", l)]
            em = [l for l in lines if "—" in l]
            out.append(f"- at-a-glance elements missing from the first 40 lines: {glance if glance else 'none'}")
            out.append(f"- notebook stems (____) on teacher page: {len(stems)}")
            if em: out.append(f"- em dashes: {len(em)}")
            out.append(f"- teacher banned-list hits: {len(hits)}; AI-cliche hits: {len(ai)}")
            for i, why, l in hits: out.append(f"  - L{i} [{why}] {l}")
            for i, why, l in ai: out.append(f"  - L{i} [{why}] {l}")
            summary.append((f.name, len(hits), len(ai), None, None, None, imgs))
        out.append("")
    out.insert(2, "| page | banned hits | cliche hits | steps | done-when | absence block | img tags |\n|---|---|---|---|---|---|---|\n" + "\n".join(f"| {n} | {b} | {a} | {s if s is not None else ''} | {d if d is not None else ''} | {'yes' if ab else ('' if ab is None else 'no')} | {im} |" for n, b, a, s, d, ab, im in summary) + "\n")
    return "\n".join(out)

if __name__ == "__main__":
    argv = sys.argv[1:]; outp = None
    if "--out" in argv:
        i = argv.index("--out"); outp = Path(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if not a.startswith("--")]
    report = "\n\n".join(audit_week(w) for w in args)
    if outp: outp.parent.mkdir(parents=True, exist_ok=True); outp.write_text(report); print(f"wrote {outp}")
    else: print(report)
