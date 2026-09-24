#!/usr/bin/env python3
"""Keep student worksheet buttons and teacher response-route panels correct.

Runs AFTER any week builder (body-only or not). Two jobs, both idempotent and
body-only (no publication field is ever sent):

1. STUDENT pages: every worksheet button listed in
   build/google_docs/student_worksheet_docs.json must open that worksheet's
   own Google Doc (/copy). Exit-ticket buttons keep the per-day Doc from
   build/google_docs/student_response_route_registry.json. Any drift is
   repaired by rewriting the anchor's href (label and style untouched).

2. TEACHER facilitator guides: a "Student response routes" panel is inserted
   (or replaced) between CCE_RESPONSE_ROUTES markers right after the first
   heading. It lists, for that day, the Google Doc route (student copy link +
   teacher edit link) for each worksheet and the exit ticket, the printable
   PDF previews in Canvas, and the OneNote route status, plus the one-line
   instruction for retargeting the student button.

Usage:
  python3 build/canvas/apply_response_routes.py --dry-run [--weeks 1SW-Wk2,1SW-Wk3] < token
  python3 build/canvas/apply_response_routes.py --apply  [--weeks ...]         < token
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
WD_PATH = ROOT / "build/google_docs/student_worksheet_docs.json"
REG_PATH = ROOT / "build/google_docs/student_response_route_registry.json"
ONENOTE_PATH = ROOT / "build/google_docs/student_onenote_routes.json"  # optional; {day_key: url}
# Canvas strips HTML comments, so the panel is identified by its id attribute.
PANEL_ID = "cce-response-routes"
PANEL_RE = re.compile(r'<div[^>]*id="cce-response-routes"[^>]*>.*?</div>', re.S)
LEGACY_PANEL_RE = re.compile(r'<div style="border:1px solid #c9d1d9;border-left:5px solid #1f617a;[^"]*">(?:(?!<div).)*?Student response routes for Day(?:(?!<div).)*?</div>', re.S)
START = ""
END = ""
ANCHOR_RE = re.compile(r"<a\b([^>]*?)href=\"([^\"]+)\"([^>]*)>(.*?)</a>", re.S)


def api(c, m, p, **kw):
    r = c.request(m, f"{BASE}/api/v1{p}", **kw)
    r.raise_for_status()
    return r.json() if r.content else None


def paged(c, p, params=None):
    out, url, q = [], f"{BASE}/api/v1{p}", {"per_page": 100, **(params or {})}
    while url:
        r = c.get(url, params=q)
        r.raise_for_status()
        out += r.json()
        url = r.links.get("next", {}).get("url")
        q = None
    return out


def norm_text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip().lower()


SLIDES_PATH = ROOT / "build/slides/slides_registry.json"


def build_index():
    wd = json.load(open(WD_PATH))["docs"]
    slides = json.load(open(SLIDES_PATH))["days"] if SLIDES_PATH.exists() else {}
    reg = json.load(open(REG_PATH))["routes"]
    onenote = json.load(open(ONENOTE_PATH)) if ONENOTE_PATH.exists() else {}
    by_day = {}
    for r in reg:
        by_day[r["day_key"]] = {
            "day_key": r["day_key"],
            "week": f"{r['six_weeks']}SW-Wk{r['week']}",
            "day": r["day"],
            "teacher_url": r["canvas"]["source_course"]["teacher"]["url"],
            "student_url": r["canvas"]["source_course"]["student"]["url"],
            "exit_doc_id": r["google_doc"]["id"],
            "exit_doc_title": r["google_doc"].get("live_title") or r["title"],
            "response_role": r.get("response_role", "standard"),
            "worksheets": [],
            "onenote_url": onenote.get(r["day_key"]),
            "slides": slides.get(r["day_key"]),
        }
    for w in wd:
        seen = set()
        for u in w["used_by"]:
            if u["day_key"] in seen:
                continue
            seen.add(u["day_key"])
            by_day[u["day_key"]]["worksheets"].append({
                "slug": w["slug"], "title": w["title"], "doc_id": w["doc_id"],
                "copy_url": w["copy_url"], "edit_url": w["edit_url"],
                "anchor_text": u["anchor_text"], "canvas_file_id": w["canvas_file_id"],
                "shared_days": sorted({x["day_key"] for x in w["used_by"]}),
            })
    return by_day


def course_pdf_index(c):
    """display_name -> newest live file id (re-uploads change ids); plus exit-ticket ids per day."""
    files = paged(c, f"/courses/{COURSE_ID}/files", {"content_types[]": "application/pdf"})
    by_name, exits = {}, {}
    for f in sorted(files, key=lambda x: x.get("updated_at") or "", reverse=True):
        by_name.setdefault(f["display_name"], f["id"])
        m = re.match(r"^(\d)sw-wk(\d+)-day(\d)-.*\.pdf$", f["display_name"])
        if m:
            exits.setdefault(f"{m.group(1)}SW-Wk{m.group(2)}-Day{m.group(3)}", f["id"])
    return by_name, exits


def panel_html(day, exit_pdf_id):
    rows = []
    for w in day["worksheets"]:
        shared = ""
        if len(w["shared_days"]) > 1:
            days = ", ".join(f"Day {k[-1]}" for k in w["shared_days"])
            shared = f" <em>(same Doc on {days}; students keep one copy)</em>"
        pdf = f'<a href="/courses/{COURSE_ID}/files/{w["canvas_file_id"]}/preview">PDF</a>' if w.get("canvas_file_id") else "PDF not in Canvas"
        rows.append(
            f"<li><strong>{html.escape(w['title'])}</strong>{shared}: student button “{html.escape(w['anchor_text'])}” → "
            f'<a href="{w["copy_url"]}">Google Doc (make a copy)</a> · <a href="{w["edit_url"]}">teacher master</a> · {pdf}</li>'
        )
    exit_pdf = f' · <a href="/courses/{COURSE_ID}/files/{exit_pdf_id}/preview">PDF</a>' if exit_pdf_id else ""
    if day["response_role"] == "alternate":
        if day["exit_doc_id"] not in {w["doc_id"] for w in day["worksheets"]}:
            rows.append(
                f"<li><strong>Optional alternate to the lesson's response home</strong>: "
                f'<a href="https://docs.google.com/document/d/{day["exit_doc_id"]}/copy">Google Doc (make a copy)</a> · '
                f'<a href="https://docs.google.com/document/d/{day["exit_doc_id"]}/edit">teacher master</a>{exit_pdf}</li>'
            )
    else:
        rows.append(
            f"<li><strong>Exit ticket</strong>: "
            f'<a href="https://docs.google.com/document/d/{day["exit_doc_id"]}/copy">Google Doc (make a copy)</a> · '
            f'<a href="https://docs.google.com/document/d/{day["exit_doc_id"]}/edit">teacher master</a>{exit_pdf}</li>'
        )
    sl = day.get("slides")
    if sl:
        parts = []
        if sl.get("gslides_url"): parts.append(f'<a href="{sl["gslides_url"]}">Google Slides</a>')
        if sl.get("canvas_file_id"): parts.append(f'<a href="/courses/{COURSE_ID}/files/{sl["canvas_file_id"]}/download?download_frd=1">PowerPoint (.pptx)</a>')
        if sl.get("pptx_drive_url"): parts.append(f'<a href="{sl["pptx_drive_url"]}">PowerPoint on Drive</a>')
        rows.append(f"<li><strong>Slides for Day {day['day']}</strong>: " + " · ".join(parts) + " (teacher deck; speaker notes carry the pacing)</li>")
    if day.get("onenote_url"):
        onenote = f'<a href="{day["onenote_url"]}">OneNote page</a> (copy the CCE Work section into your class notebook, then point the student button here)'
    else:
        onenote = "OneNote route not built yet for this day. When the CCE Work template page exists it will be listed here."
    return (
        f'<div id="{PANEL_ID}" class="cce-response-routes" style="border:1px solid #c9d1d9;border-left:5px solid #1f617a;border-radius:6px;padding:12px 16px;margin:12px 0;background:#f6f8fa">'
        f'<p style="margin:0 0 6px;font-weight:700;color:#1f617a">Student response routes for Day {day["day"]}</p>'
        f'<p style="margin:0 0 6px">{"Use the lesson’s workbook or packet response home. The Google Doc here is an alternate, not extra work." if day["response_role"] == "alternate" else "Students see one button per worksheet and one for the exit ticket. The default target is the Google Doc make-a-copy link."} Printable PDFs and the OneNote route are here for teachers who use them.</p>'
        f'<ul style="margin:0 0 6px 18px">{"".join(rows)}</ul>'
        f'<p style="margin:0 0 6px"><strong>OneNote:</strong> {onenote}</p>'
        f'<p style="margin:0;font-size:0.92em;color:#444">To change a route for your students: edit the Student Guide, select the button named above, and replace only its link (keep the label). Never send students to a different document than the one the label names.</p>'
        f"</div>"
    )


def upsert_panel(body, panel):
    if PANEL_RE.search(body):
        return PANEL_RE.sub(lambda m: panel, body, count=1)
    if LEGACY_PANEL_RE.search(body):
        return LEGACY_PANEL_RE.sub(lambda m: panel, body, count=1)
    m = re.search(r"</h[12]>", body)
    if m:
        return body[: m.end()] + panel + body[m.end():]
    return panel + body


def fix_student_anchors(body, day):
    changes = []
    want = {norm_text(w["anchor_text"]): w["copy_url"] for w in day["worksheets"]}

    def repl(m):
        pre, href, post, label = m.groups()
        key = norm_text(label)
        if key in want and "docs.google.com" in href and href != want[key]:
            changes.append((label.strip(), href, want[key]))
            return f'<a{pre}href="{want[key]}"{post}>{label}</a>'
        return m.group(0)

    return ANCHOR_RE.sub(repl, body), changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--weeks", default="", help="comma list like 1SW-Wk2,1SW-Wk3 (default all)")
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        ap.error("pass --dry-run or --apply")
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    weeks = {w.strip() for w in a.weeks.split(",") if w.strip()}
    idx = build_index()
    report = {"student_fixed": [], "student_ok": 0, "teacher_panels": 0, "errors": []}
    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=120) as c:
        pdf_by_name, exit_pdfs = course_pdf_index(c)
        for day in idx.values():
            for w in day["worksheets"]:
                w["canvas_file_id"] = pdf_by_name.get(f"{w['slug']}.pdf", w.get("canvas_file_id"))
        for key, day in sorted(idx.items()):
            if weeks and day["week"] not in weeks:
                continue
            # student
            try:
                page = api(c, "GET", f"/courses/{COURSE_ID}/pages/{day['student_url']}")
            except httpx.HTTPStatusError as e:
                report["errors"].append(f"{key} student GET {e.response.status_code}")
                continue
            body = page.get("body") or ""
            new_body, changes = fix_student_anchors(body, day)
            if changes:
                report["student_fixed"].append({"day": key, "changes": changes})
                if a.apply:
                    api(c, "PUT", f"/courses/{COURSE_ID}/pages/{day['student_url']}", data={"wiki_page[body]": new_body})
            else:
                report["student_ok"] += 1
            # teacher
            try:
                tpage = api(c, "GET", f"/courses/{COURSE_ID}/pages/{day['teacher_url']}")
            except httpx.HTTPStatusError as e:
                report["errors"].append(f"{key} teacher GET {e.response.status_code}")
                continue
            tbody = tpage.get("body") or ""
            new_tbody = upsert_panel(tbody, panel_html(day, exit_pdfs.get(key)))
            if new_tbody != tbody:
                report["teacher_panels"] += 1
                if a.apply:
                    api(c, "PUT", f"/courses/{COURSE_ID}/pages/{day['teacher_url']}", data={"wiki_page[body]": new_tbody})
            print(f"{key}: student {'FIXED '+str(len(changes)) if changes else 'ok'}; teacher panel {'updated' if new_tbody != tbody else 'unchanged'}", flush=True)
    print(json.dumps({k: (v if k != "student_fixed" else len(v)) for k, v in report.items()}, indent=1))
    Path(ROOT / ".tmp").mkdir(exist_ok=True)
    (ROOT / ".tmp" / "apply_response_routes_report.json").write_text(json.dumps(report, indent=1))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
