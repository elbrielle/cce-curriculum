#!/usr/bin/env python3
"""Read-only QA for the response-route fix and the truth pass.

Checks, against the live course:
  1. no "HQIM" on any STUDENT or TEACHER page
  2. every worksheet button (student_worksheet_docs.json used_by) opens its own Doc
  3. every teacher guide carries exactly one response-routes panel
  4. publication state of modules, module items, and pages equals a baseline dump
     (modules.json / pages.json from the pre-fix dump) - nothing published or unpublished
  5. a worksheet shared across days points every day at the same Doc

Usage: python3 build/canvas/qa_response_routes.py --baseline .tmp/canvas-dump-20260914 < token
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
COURSE_ID = int(__import__("os").environ.get("CCE_COURSE_ID", "98060"))
ANCHOR_RE = re.compile(r"<a\b[^>]*?href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.S)


def paged(c, p, params=None):
    out, url, q = [], f"{BASE}/api/v1{p}", {"per_page": 100, **(params or {})}
    while url:
        r = c.get(url, params=q); r.raise_for_status(); out += r.json()
        url = r.links.get("next", {}).get("url"); q = None
    return out


def norm(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip().lower()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--baseline", required=True); a = ap.parse_args()
    token = sys.stdin.readline().strip()
    base = Path(a.baseline)
    wd = json.load(open(ROOT / "build/google_docs/student_worksheet_docs.json"))["docs"]
    reg = json.load(open(ROOT / "build/google_docs/student_response_route_registry.json"))["routes"]
    fails, notes = [], []
    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=120) as c:
        pages = paged(c, f"/courses/{COURSE_ID}/pages", {"include[]": "body"})
        by_url = {}
        for p in pages:
            body = p.get("body")
            if body is None:
                body = c.get(f"{BASE}/api/v1/courses/{COURSE_ID}/pages/{p['url']}").json().get("body") or ""
            p["body"] = body; by_url[p["url"]] = p
        modules = paged(c, f"/courses/{COURSE_ID}/modules", {"include[]": "items"})
        for m in modules:
            if len(m.get("items") or []) < m.get("items_count", 0):
                m["items"] = paged(c, f"/courses/{COURSE_ID}/modules/{m['id']}/items")
    # 1
    hq = [(u, p["body"].count("HQIM")) for u, p in by_url.items() if (u.startswith("student-") or u.startswith("teacher-")) and "HQIM" in p["body"]]
    if hq: fails.append(f"HQIM still on {len(hq)} pages: {hq[:10]}")
    # 2 + 5
    day_urls = {r["day_key"]: r["canvas"]["source_course"]["student"]["url"] for r in reg}
    teacher_urls = {r["day_key"]: r["canvas"]["source_course"]["teacher"]["url"] for r in reg}
    exit_docs = {r["day_key"]: r["google_doc"]["id"] for r in reg}
    bad, ok = [], 0
    for w in wd:
        for u in w["used_by"]:
            page = by_url.get(day_urls[u["day_key"]])
            if not page: bad.append((u["day_key"], "student page missing")); continue
            hits = [href for href, label in ANCHOR_RE.findall(page["body"]) if norm(label) == norm(u["anchor_text"])]
            if not hits: bad.append((u["day_key"], u["anchor_text"], "anchor not found")); continue
            if any(w["doc_id"] not in h for h in hits): bad.append((u["day_key"], u["anchor_text"], hits[0][-50:], "expected", w["doc_id"])); continue
            ok += 1
    if bad: fails.append(f"{len(bad)} worksheet buttons wrong: {bad[:12]}")
    notes.append(f"worksheet buttons verified: {ok}")
    # exit-ticket buttons still on their own doc where an exit anchor exists
    wrong_exit = []
    for dk, url in day_urls.items():
        page = by_url.get(url)
        if not page: continue
        for href, label in ANCHOR_RE.findall(page["body"]):
            if "exit ticket" in norm(label) and "docs.google.com" in href and exit_docs[dk] not in href:
                wrong_exit.append((dk, label.strip()[:50], href[-45:]))
    if wrong_exit: fails.append(f"exit-ticket buttons not on their day Doc: {wrong_exit[:10]}")
    # 3
    panels = {dk: by_url[teacher_urls[dk]]["body"].count("Student response routes for Day") if teacher_urls[dk] in by_url else -1 for dk in day_urls}
    off = {k: v for k, v in panels.items() if v != 1}
    if off: fails.append(f"teacher panels != 1 on {len(off)} days: {list(off.items())[:10]}")
    # 4
    bm = {m["id"]: m for m in json.load(open(base / "modules.json"))}
    for m in modules:
        b = bm.get(m["id"])
        if not b: notes.append(f"new module {m['name']}"); continue
        if b["published"] != m["published"]: fails.append(f"module publish drift: {m['name']} {b['published']}->{m['published']}")
        bi = {i["id"]: i for i in b["items"]}
        for it in m["items"]:
            bb = bi.get(it["id"])
            if bb and bb.get("published") != it.get("published"): fails.append(f"item publish drift: {it['title']} {bb.get('published')}->{it.get('published')}")
        if len(m["items"]) != len(b["items"]): fails.append(f"item count drift: {m['name']} {len(b['items'])}->{len(m['items'])}")
    bp = {p["url"]: p for p in json.load(open(base / "pages.json"))}
    for u, p in by_url.items():
        b = bp.get(u)
        if b and b["published"] != p["published"]: fails.append(f"page publish drift: {u} {b['published']}->{p['published']}")
    print("\n".join(notes))
    if fails:
        print("FAIL"); print("\n".join(fails)); return 1
    print("PASS: no HQIM on student/teacher pages; all worksheet buttons correct; one panel per teacher guide; publication state unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
