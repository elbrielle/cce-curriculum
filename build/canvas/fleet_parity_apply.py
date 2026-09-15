#!/usr/bin/env python3
"""Fleet parity: push the source course's current page bodies into a teacher's
course without touching anything the teacher owns.

Rules (owner decision 2026-09-15):
  * Only page bodies/titles are written. No module, item, assignment, quiz,
    file-lock, or publication write. Modules the teacher created and any
    reorganization stay exactly as they are.
  * A page is written only when its current fleet body equals the source
    body BEFORE the 2026-09-14 fix (same_as_prefix), or when it is explicitly
    allow-listed (stale bulk imports). Pages that differ otherwise are
    reported as teacher_edited and skipped.
  * Links are remapped into the fleet course: /courses/<id>/, files by
    display_name (same folder path first), assignments/quizzes/discussions by
    title, pages by slug (or by module-item position when the source renamed
    the page and the fleet module still points at the old slug).
  * Regenerated PDFs listed in --reupload are uploaded into the same folder
    path in the fleet course (overwrite) before bodies are written.

Usage:
  python3 build/canvas/fleet_parity_apply.py --course 97813 \
      --source-dump <dir of 98060 current dump> --prefix-dump <dir of 98060 pre-fix dump> \
      --fleet-dump <dir of fleet dump> [--allow stale.json] [--reupload a.pdf,b.pdf] [--apply] < token
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
from collections import defaultdict
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://learn.irvingisd.net"
SOURCE_ID = 98060
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleet_parity_analyze import norm, PANEL_RE  # noqa: E402


def norm_keep_panel(h):
    """norm() strips the response-routes panel; the unchanged test must keep it."""
    panels = PANEL_RE.findall(h or "")
    return norm(h) + "|" + "|".join(norm_panel(x) for x in panels)


def norm_panel(x):
    """Canvas rewrites panel links on save (verifier tokens, data-api-* attributes); ignore that noise."""
    import re as _re
    x = _re.sub(r"[?&]verifier=[A-Za-z0-9_-]+", "", x)
    x = _re.sub(r'\s*data-api-(?:endpoint|returntype)="[^"]*"', "", x)
    x = x.replace("https://learn.irvingisd.net", "")
    x = _re.sub(r"/courses/\d+/", "/courses/X/", x); x = _re.sub(r"/files/\d+", "/files/N", x)
    return _re.sub(r"\s+", " ", x)


def api(c, m, p, **kw):
    r = c.request(m, f"{BASE}/api/v1{p}", **kw); r.raise_for_status()
    return r.json() if r.content else None


def paged(c, p, params=None):
    out, url, q = [], f"{BASE}/api/v1{p}", {"per_page": 100, **(params or {})}
    while url:
        r = c.get(url, params=q); r.raise_for_status(); out += r.json()
        url = r.links.get("next", {}).get("url"); q = None
    return out


def folder_path_of(folders_by_id, folder_id):
    f = folders_by_id.get(folder_id)
    return f["full_name"] if f else ""


def build_maps(src, fleet):
    """Return id/slug maps from the two dumps."""
    sfolders = {f["id"]: f for f in src["folders"]}
    ffolders = {f["id"]: f for f in fleet["folders"]}
    src_file = {f["id"]: (f["display_name"], folder_path_of(sfolders, f["folder_id"])) for f in src["files"]}
    fleet_by_name = defaultdict(list)
    for f in fleet["files"]:
        fleet_by_name[f["display_name"]].append((folder_path_of(ffolders, f["folder_id"]), f["id"], f.get("updated_at") or ""))
    def file_map(sid):
        name, path = src_file.get(sid, (None, None))
        if not name or name not in fleet_by_name:
            return None
        cands = fleet_by_name[name]
        same = [c for c in cands if c[0] == path]
        pick = sorted(same or cands, key=lambda c: c[2], reverse=True)[0]
        return pick[1]
    def by_title(src_list, fleet_list):
        f_by = defaultdict(list)
        for x in fleet_list:
            f_by[x.get("name") or x.get("title")].append(x["id"])
        return {x["id"]: (f_by.get(x.get("name") or x.get("title")) or [None])[0] for x in src_list}
    assign_map = by_title(src["assignments"], fleet["assignments"])
    quiz_map = by_title(src.get("quizzes", []), fleet.get("quizzes", []))
    disc_map = by_title(src.get("discussions", []), fleet.get("discussions", []))
    # pages: identity if slug exists, else module-item position match
    fleet_slugs = {p["url"] for p in fleet["pages"]}
    page_map = {}
    fmods = {m["name"]: m for m in fleet["modules"]}
    for sm in src["modules"]:
        fm = fmods.get(sm["name"])
        if not fm:
            continue
        s_pages = [i for i in sm["items"] if i["type"] == "Page"]
        f_pages = [i for i in fm["items"] if i["type"] == "Page"]
        # match by title first, then by (subheader order) position among Page items
        f_by_title = {i["title"]: i["page_url"] for i in f_pages}
        for idx, si in enumerate(s_pages):
            if si["page_url"] in fleet_slugs:
                page_map[si["page_url"]] = si["page_url"]
            elif si["title"] in f_by_title:
                page_map[si["page_url"]] = f_by_title[si["title"]]
            elif idx < len(f_pages) and f_pages[idx]["page_url"] not in page_map.values():
                # same position in the same module: treat as the renamed page
                page_map[si["page_url"]] = f_pages[idx]["page_url"]
    for p in src["pages"]:
        if p["url"] in fleet_slugs:
            page_map.setdefault(p["url"], p["url"])
    return file_map, assign_map, quiz_map, disc_map, page_map


def transform(body, course_id, file_map, assign_map, quiz_map, disc_map, page_map, report):
    b = body or ""
    b = re.sub(r"[?&]verifier=[A-Za-z0-9_-]+", "", b)
    b = b.replace(f"https://learn.irvingisd.net/courses/{SOURCE_ID}/", f"/courses/{SOURCE_ID}/")
    def sub_file(m):
        new = file_map(int(m.group(1)))
        if new is None:
            report["unmapped_files"].add(int(m.group(1))); return m.group(0)
        return f"/files/{new}"
    b = re.sub(r"/files/(\d+)", sub_file, b)
    def sub_obj(kind, mp):
        def _s(m):
            new = mp.get(int(m.group(1)))
            if new is None:
                report[f"unmapped_{kind}"].add(int(m.group(1))); return m.group(0)
            return f"/{kind}/{new}"
        return _s
    b = re.sub(r"/assignments/(\d+)", sub_obj("assignments", assign_map), b)
    b = re.sub(r"/quizzes/(\d+)", sub_obj("quizzes", quiz_map), b)
    b = re.sub(r"/discussion_topics/(\d+)", sub_obj("discussion_topics", disc_map), b)
    def sub_page(m):
        slug = m.group(1); new = page_map.get(slug)
        if new is None:
            report["unmapped_pages"].add(slug); return m.group(0)
        return f"/pages/{new}"
    b = re.sub(r"/pages/([A-Za-z0-9_-]+)", sub_page, b)
    b = b.replace(f"/courses/{SOURCE_ID}/", f"/courses/{course_id}/")
    b = re.sub(r'data-api-endpoint="[^"]*"', "", b)
    return b


def upload_pdf(c, course_id, local: Path, folder_path: str):
    init = api(c, "POST", f"/courses/{course_id}/files", data={"name": local.name, "parent_folder_path": folder_path, "on_duplicate": "overwrite"})
    r = c.post(init["upload_url"], data=init["upload_params"], files={"file": (local.name, local.read_bytes(), mimetypes.guess_type(local.name)[0] or "application/pdf")}, follow_redirects=True)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--course", type=int, required=True)
    ap.add_argument("--source-dump", required=True); ap.add_argument("--prefix-dump", required=True); ap.add_argument("--fleet-dump", required=True)
    ap.add_argument("--allow", default=None, help="JSON list of fleet page slugs to overwrite even though they differ (stale bulk imports)")
    ap.add_argument("--reupload", default="", help="comma list of PDF display names to upload from docs/resources/worksheets")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    token = sys.stdin.readline().strip()
    def load(d):
        d = Path(d)
        return {k: json.load(open(d / f"{k}.json")) for k in ("pages", "modules", "files", "folders", "assignments", "quizzes", "discussions") if (d / f"{k}.json").exists()}
    src, pre, fleet = load(a.source_dump), load(a.prefix_dump), load(a.fleet_dump)
    allow = set(json.load(open(a.allow))) if a.allow else set()
    report = {"course": a.course, "written": [], "skipped_teacher_edited": [], "skipped_missing": [], "unchanged": [], "renamed_targets": {}, "uploaded": [],
              "unmapped_files": set(), "unmapped_assignments": set(), "unmapped_quizzes": set(), "unmapped_discussion_topics": set(), "unmapped_pages": set()}
    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=120) as c:
        # 1. re-upload regenerated PDFs so the file map can see them
        if a.reupload:
            sfolders = {f["id"]: f for f in src["folders"]}
            src_by_name = {f["display_name"]: f for f in src["files"]}
            for name in [n.strip() for n in a.reupload.split(",") if n.strip()]:
                sf = src_by_name.get(name)
                if not sf:
                    continue
                path = sfolders[sf["folder_id"]]["full_name"]
                local = ROOT / ("docs/resources/slides" if name.endswith(".pptx") else "docs/resources/worksheets") / name
                if a.apply:
                    up = upload_pdf(c, a.course, local, path)
                    report["uploaded"].append({"name": name, "id": up.get("id"), "folder": path})
                else:
                    report["uploaded"].append({"name": name, "folder": path, "dry_run": True})
        # always map against the LIVE fleet file list (re-uploads change ids)
        fleet["files"] = paged(c, f"/courses/{a.course}/files")
        fleet["folders"] = paged(c, f"/courses/{a.course}/folders")
        file_map, assign_map, quiz_map, disc_map, page_map = build_maps(src, fleet)
        fleet_pages = {p["url"]: p for p in fleet["pages"]}
        pre_pages = {p["url"]: p for p in pre["pages"]}
        # 2. pages: every source page that is module-linked in the source, plus student-/teacher- pages
        linked = {i["page_url"] for m in src["modules"] for i in m["items"] if i["type"] == "Page"}
        targets = [p for p in src["pages"] if p["url"] in linked or p["url"].startswith(("student-", "teacher-"))]
        for sp in sorted(targets, key=lambda p: p["url"]):
            fslug = page_map.get(sp["url"])
            if not fslug or fslug not in fleet_pages:
                report["skipped_missing"].append(sp["url"]); continue
            fp = fleet_pages[fslug]
            if fslug != sp["url"]:
                report["renamed_targets"][sp["url"]] = fslug
            new_body = transform(sp["body"], a.course, file_map, assign_map, quiz_map, disc_map, page_map, report)
            nf, ncur = norm(fp["body"]), norm(new_body)
            if norm_keep_panel(fp["body"]) == norm_keep_panel(new_body) and fp["title"] == sp["title"]:
                report["unchanged"].append(fslug); continue
            npre = norm(pre_pages.get(sp["url"], {}).get("body", ""))
            if nf != npre and nf != norm(sp["body"]) and fslug not in allow:
                report["skipped_teacher_edited"].append(fslug); continue
            report["written"].append(fslug)
            if a.apply:
                api(c, "PUT", f"/courses/{a.course}/pages/{fslug}", data={"wiki_page[title]": sp["title"], "wiki_page[body]": new_body})
    for k in list(report):
        if isinstance(report[k], set):
            report[k] = sorted(report[k])
    summary = {k: (len(v) if isinstance(v, list) else v) for k, v in report.items() if k != "course"}
    print(json.dumps({"course": a.course, "apply": a.apply, **summary}, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
