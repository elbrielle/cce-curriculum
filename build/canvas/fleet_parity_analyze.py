#!/usr/bin/env python3
"""Compare a fleet course dump against the source course (98060) dumps.

For every CCE page (student-*/teacher-* and the other source pages), classify:
  same_as_prefix   fleet body == source body BEFORE the 2026-09-14 fix (safe to update)
  same_as_current  fleet body == source body now (already updated)
  teacher_edited   fleet body differs from both (do not touch; flag)
  missing          page exists in source, not in fleet
Also: modules in fleet not in source (teacher-created; never touched), module
order/name differences (report only), and source files missing from the fleet
by display_name.

Normalization before comparison: strip verifier query strings, replace
/courses/<id>/ with /courses/X/, replace /files/<id> with /files/N, drop the
response-routes panel, collapse whitespace, strip HTML comments.

Usage: fleet_parity_analyze.py <fleet_dump_dir> <prefix_source_dump_dir> <current_source_dump_dir> --out report.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PANEL_RE = re.compile(r'<div[^>]*id="cce-response-routes"[^>]*>.*?</div>', re.S)


def norm(h: str) -> str:
    h = h or ""
    h = PANEL_RE.sub("", h)
    h = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    h = re.sub(r"[?&]verifier=[A-Za-z0-9_-]+", "", h)
    h = re.sub(r"https?://learn\.irvingisd\.net", "", h)
    h = re.sub(r"/courses/\d+/", "/courses/X/", h)
    h = re.sub(r"/files/\d+", "/files/N", h)
    h = re.sub(r"/(assignments|quizzes|discussion_topics|modules|module_item_redirect)/\d+", r"/\1/N", h)
    h = re.sub(r"/pages/[A-Za-z0-9_-]+", "/pages/P", h)
    h = re.sub(r"data-api-returntype=\"[^\"]*\"", "", h)
    h = re.sub(r"<a([^>]*?)\s(class|title)=\"[^\"]*\"", r"<a\1", h)
    h = re.sub(r"data-api-endpoint=\"[^\"]*\"", "", h)
    h = re.sub(r"\s+(/?>)", r"\1", h)  # Canvas rewrites `loading="lazy" >` as `loading="lazy">`
    h = re.sub(r"\s+", " ", h)
    return h.strip()


def load_pages(d: Path):
    return {p["url"]: p for p in json.load(open(d / "pages.json"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fleet"); ap.add_argument("prefix"); ap.add_argument("current"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fleet, pre, cur = load_pages(Path(a.fleet)), load_pages(Path(a.prefix)), load_pages(Path(a.current))
    cls = {}
    for url, sp in cur.items():
        fp = fleet.get(url)
        if fp is None:
            cls[url] = "missing"; continue
        nf, npre, ncur = norm(fp["body"]), norm(pre.get(url, {}).get("body", "")), norm(sp["body"])
        if nf == ncur:
            cls[url] = "same_as_current"
        elif nf == npre:
            cls[url] = "same_as_prefix"
        else:
            cls[url] = "teacher_edited"
    fleet_only_pages = sorted(set(fleet) - set(cur))
    fm = json.load(open(Path(a.fleet) / "modules.json")); sm = json.load(open(Path(a.current) / "modules.json"))
    sm_names = {m["name"] for m in sm}
    fleet_only_modules = [m["name"] for m in fm if m["name"] not in sm_names]
    order_diff = [m["name"] for m in fm if m["name"] in sm_names] != [m["name"] for m in sm if m["name"] in {x["name"] for x in fm}]
    # module item titles differing (renamed/reordered items) per shared module
    item_diffs = {}
    sm_by = {m["name"]: m for m in sm}
    for m in fm:
        s = sm_by.get(m["name"])
        if not s: continue
        ft = [i["title"] for i in m["items"]]; st = [i["title"] for i in s["items"]]
        if ft != st:
            item_diffs[m["name"]] = {"fleet_only": sorted(set(ft) - set(st)), "source_only": sorted(set(st) - set(ft)), "reordered": sorted(ft) == sorted(st)}
    ff = {f["display_name"] for f in json.load(open(Path(a.fleet) / "files.json"))}
    sf = {f["display_name"] for f in json.load(open(Path(a.current) / "files.json"))}
    missing_files = sorted(sf - ff)
    from collections import Counter
    rep = {
        "fleet": a.fleet, "counts": dict(Counter(cls.values())), "pages": cls,
        "fleet_only_pages": fleet_only_pages, "fleet_only_modules": fleet_only_modules,
        "module_order_differs": order_diff, "module_item_diffs": item_diffs,
        "source_files_missing_in_fleet": missing_files,
    }
    Path(a.out).write_text(json.dumps(rep, indent=1))
    print(a.fleet, rep["counts"], "fleet-only modules:", fleet_only_modules, "item diffs:", len(item_diffs), "missing files:", len(missing_files))


if __name__ == "__main__":
    main()
