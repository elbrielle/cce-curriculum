"""Dump Canvas course 98060 (modules, items, pages, assignments, files, quizzes, discussions) to JSON + per-page HTML/TXT for grep auditing."""
from pathlib import Path
import json, os, re, sys, html
import httpx

SCRATCH = str(Path(__file__).resolve().parents[2] / ".tmp" / "fleet-dumps"); Path(SCRATCH).mkdir(parents=True, exist_ok=True)
TOKEN = sys.stdin.readline().strip()
BASE = "https://learn.irvingisd.net/api/v1"
import sys
COURSE = int(sys.argv[1])
OUT = os.path.join(SCRATCH, f"canvas-{COURSE}")
os.makedirs(OUT, exist_ok=True)
c = httpx.Client(headers={"Authorization": f"Bearer {TOKEN}"}, timeout=60)

def paged(path, params=None):
    out, url, q = [], f"{BASE}{path}", {"per_page": 100, **(params or {})}
    while url:
        r = c.get(url, params=q); r.raise_for_status(); out += r.json()
        url = r.links.get("next", {}).get("url"); q = None
    return out

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:90]

modules = paged(f"/courses/{COURSE}/modules", {"include[]": "items"})
for m in modules:
    if "items" not in m or m.get("items_count", 0) > len(m.get("items") or []):
        m["items"] = paged(f"/courses/{COURSE}/modules/{m['id']}/items")
json.dump(modules, open(f"{OUT}/modules.json", "w"), indent=1)

pages = paged(f"/courses/{COURSE}/pages", {"include[]": "body"})
full = []
os.makedirs(f"{OUT}/pages", exist_ok=True)
for p in pages:
    body = p.get("body")
    if body is None:
        body = c.get(f"{BASE}/courses/{COURSE}/pages/{p['url']}").json().get("body") or ""
    p["body"] = body
    full.append(p)
    open(f"{OUT}/pages/{p['url']}.html", "w").write(f"<!-- title: {p['title']} | published: {p['published']} | url: {p['url']} -->\n{body}")
    txt = re.sub(r"<[^>]+>", " ", body); txt = html.unescape(re.sub(r"\s+", " ", txt))
    open(f"{OUT}/pages/{p['url']}.txt", "w").write(f"# {p['title']} | published={p['published']}\n{txt}")
json.dump(full, open(f"{OUT}/pages.json", "w"), indent=1)

assignments = paged(f"/courses/{COURSE}/assignments")
json.dump(assignments, open(f"{OUT}/assignments.json", "w"), indent=1)
os.makedirs(f"{OUT}/assignments", exist_ok=True)
for a in assignments:
    body = a.get("description") or ""
    open(f"{OUT}/assignments/{a['id']}-{slug(a['name'])}.html", "w").write(f"<!-- {a['name']} | published: {a['published']} -->\n{body}")
    txt = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
    open(f"{OUT}/assignments/{a['id']}-{slug(a['name'])}.txt", "w").write(f"# {a['name']} | published={a['published']}\n{txt}")

files = paged(f"/courses/{COURSE}/files")
json.dump(files, open(f"{OUT}/files.json", "w"), indent=1)
folders = paged(f"/courses/{COURSE}/folders")
json.dump(folders, open(f"{OUT}/folders.json", "w"), indent=1)
try:
    quizzes = paged(f"/courses/{COURSE}/quizzes"); json.dump(quizzes, open(f"{OUT}/quizzes.json", "w"), indent=1)
except Exception as e: print("quizzes", e)
try:
    disc = paged(f"/courses/{COURSE}/discussion_topics"); json.dump(disc, open(f"{OUT}/discussions.json", "w"), indent=1)
except Exception as e: print("discussions", e)

print(f"modules={len(modules)} items={sum(len(m['items']) for m in modules)} pages={len(pages)} assignments={len(assignments)} files={len(files)} folders={len(folders)}")
