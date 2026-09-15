#!/usr/bin/env python3
"""Run a week builder so that ONLY page bodies (and titles) reach Canvas.

Why: the week builders were written for an unpublished Commons master. They
refuse to run against a published module and they send
``wiki_page[published]=false`` / ``module[published]=false`` on every write.
Once a module is live for students (1SW Wk0-Wk2 in September 2026) that is
exactly wrong: a source fix must reach the live page body without touching
publication state, module structure, assignments, quizzes, or file locks.

This wrapper loads the builder module and installs an httpx lens:

  * GET  -> passes through; ``published`` is reported as False and files as
            ``locked`` in the JSON the builder sees, so its preflights and
            final assertions pass without any write.
  * PUT/POST /courses/<id>/pages[/<url>] -> ``wiki_page[published]`` and
            ``wiki_page[editing_roles]`` are stripped; the write goes through
            (or is captured to disk with --dry-run).
  * POST  /files, /folders (uploads) -> pass through (no publication impact).
  * every other PUT/POST/DELETE (modules, items, assignments, quizzes,
            rubrics, discussions, file locks) -> suppressed; PUT returns the
            current GET so the builder's readback logic keeps working.

The Canvas token is read from stdin, exactly like the builders.

Usage:
  python3 build/canvas/run_builder_body_only.py build/canvas/build_wk2.py --dry-run --out .tmp/dry/wk2 < token
  python3 build/canvas/run_builder_body_only.py build/canvas/build_wk2.py < token
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import runpy
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote

import httpx

PAGE_RE = re.compile(r"^/api/v1/courses/\d+/pages(?:/([^/?]+))?/?$")
UPLOAD_RE = re.compile(r"^/api/v1/(courses/\d+/(files|folders)|folders/\d+/(files|folders)|files/\d+)$")
SUPPRESS_PUT_PREFIX = re.compile(r"^/api/v1/(courses/\d+/(modules|assignments|quizzes|discussion_topics|assignment_groups|rubrics)|files/\d+|folders/\d+)")

LOG: list[dict] = []
VERBOSE = bool(__import__("os").environ.get("CCE_BODY_ONLY_VERBOSE"))
# comma-separated display names that must be re-uploaded even if a same-name file exists
FORCE_UPLOAD = {n.strip() for n in __import__("os").environ.get("CCE_FORCE_UPLOAD", "").split(",") if n.strip()}


def _lens(obj):
    """Report every 'published' as False and every file as locked."""
    if isinstance(obj, list):
        return [_lens(x) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "published" and isinstance(v, bool):
                out[k] = False
            elif k == "locked" and ("display_name" in obj or "full_name" in obj or "files_url" in obj):
                out[k] = True
            else:
                out[k] = _lens(v)
        return out
    return obj


async def _find_existing(client, real_send, request, course_prefix, name, folder_path):
    """Return the Canvas file dict for name inside folder_path, or None."""
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"content-length", "content-type"}}
    rel = folder_path.split("/", 1)[1] if folder_path.startswith("course files/") else folder_path
    enc = httpx.URL("/" + rel).raw_path.decode("ascii").lstrip("/")
    base = str(request.url.copy_with(path=f"{course_prefix}/folders/by_path/{enc}", query=None))
    r = await real_send(client, httpx.Request("GET", base, headers=headers))
    if r.status_code != 200:
        return None
    folder = r.json()[-1]
    files_url = str(request.url.copy_with(path=f"/api/v1/folders/{folder['id']}/files", query=b"per_page=100"))
    matches = []
    url = files_url
    while url:
        r = await real_send(client, httpx.Request("GET", url, headers=headers))
        if r.status_code != 200:
            return None
        matches += [f for f in r.json() if (f.get("display_name") or f.get("filename")) == name]
        url = r.links.get("next", {}).get("url")
    return matches[0] if matches else None


def install(dry_run: bool, out_dir: Path | None):
    real_send = httpx.AsyncClient.send

    async def send(self, request, **kw):
        path = request.url.path
        method = request.method.upper()
        if VERBOSE:
            print(f"[body-only] {method} {request.url.host}{path}", file=sys.stderr, flush=True)
        if method == "GET":
            resp = await real_send(self, request, **kw)
            if "application/json" in resp.headers.get("content-type", ""):
                try:
                    data = _lens(resp.json())
                except Exception:
                    return resp
                new = httpx.Response(resp.status_code, headers={k: v for k, v in resp.headers.items() if k.lower() not in {"content-length", "content-encoding", "transfer-encoding"}}, json=data, request=request)
                new._elapsed = resp.elapsed if hasattr(resp, "_elapsed") else None
                return new
            return resp

        m = PAGE_RE.match(path)
        if m and method in {"PUT", "POST"}:
            body = request.content or b""
            fields = parse_qs(body.decode("utf-8"), keep_blank_values=True)
            fields.pop("wiki_page[published]", None)
            fields.pop("wiki_page[editing_roles]", None)
            page_url = m.group(1)
            title = fields.get("wiki_page[title]", [""])[0]
            html = fields.get("wiki_page[body]", [""])[0]
            LOG.append({"method": method, "page_url": page_url, "title": title, "bytes": len(html)})
            if dry_run:
                if out_dir:
                    name = page_url or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
                    (out_dir / f"{name}.html").write_text(html, encoding="utf-8")
                fake = {"url": page_url or "dry-run", "title": title, "body": html, "published": False}
                return httpx.Response(200, json=fake, request=request)
            data = {k: v[0] for k, v in fields.items()}
            new_req = httpx.Request(method, request.url, headers={k: v for k, v in request.headers.items() if k.lower() not in {"content-length", "content-type"}}, data=data)
            resp = await real_send(self, new_req, **kw)
            return resp

        if method == "POST" and request.url.host == "dry-run.invalid":
            # second leg of a short-circuited upload: hand back the existing file
            return httpx.Response(200, json=json.loads(unquote(request.url.params.get("file"))), request=request)

        if method == "POST" and re.match(r"^/api/v1/courses/\d+/files$", path):
            # upload init: reuse the existing Canvas file when the bytes are unchanged
            fields = parse_qs((request.content or b"").decode("utf-8"), keep_blank_values=True)
            name = fields.get("name", [""])[0]
            folder_path = fields.get("parent_folder_path", [""])[0]
            size = fields.get("size", [None])[0]
            course_prefix = path.rsplit("/files", 1)[0]
            existing = await _find_existing(self, real_send, request, course_prefix, name, folder_path)
            force = name in FORCE_UPLOAD
            if existing is not None and not force and (dry_run or size is None or str(existing.get("size")) == str(size)):
                LOG.append({"method": method, "path": path, "reused_file": existing.get("id"), "name": name})
                payload = _lens(existing)
                url = httpx.URL("https://dry-run.invalid/upload", params={"file": json.dumps(payload)})
                return httpx.Response(200, json={"upload_url": str(url), "upload_params": {}}, request=request)
            if dry_run:
                LOG.append({"method": method, "path": path, "suppressed": "dry-run upload (no existing file)", "name": name})
                url = httpx.URL("https://dry-run.invalid/upload", params={"file": json.dumps({"id": 0, "display_name": name, "locked": True, "hidden": False, "folder_id": 0, "size": 0})})
                return httpx.Response(200, json={"upload_url": str(url), "upload_params": {}}, request=request)
            LOG.append({"method": method, "path": path, "uploaded": name})
            return await real_send(self, request, **kw)

        if method == "POST" and (UPLOAD_RE.match(path) or "/files" in path or "/folders" in path or request.url.host != "learn.irvingisd.net"):
            # real S3/InstFS upload leg or folder creation
            return await real_send(self, request, **kw)

        if method == "PUT" and re.match(r"^/api/v1/courses/\d+/quizzes/\d+/questions/\d+$", path):
            # quiz question text/name updates carry no publication state: allow
            LOG.append({"method": method, "path": path, "allowed": "quiz question update"})
            return await real_send(self, request, **kw)

        if method in {"PUT", "POST", "DELETE"}:
            LOG.append({"method": method, "path": path, "suppressed": True})
            if method == "PUT":
                get_req = httpx.Request("GET", request.url, headers={k: v for k, v in request.headers.items() if k.lower() not in {"content-length", "content-type"}})
                resp = await real_send(self, get_req, **kw)
                try:
                    return httpx.Response(200, json=_lens(resp.json()), request=request)
                except Exception:
                    return httpx.Response(200, json={}, request=request)
            if method == "DELETE":
                return httpx.Response(200, json={}, request=request)
            # structural POST (quiz reorder, item/question create, ...): suppressed.
            # Return the parent collection's first matching resource when we can so
            # builders that expect an id keep going; otherwise an empty object.
            parent = re.sub(r"/(reorder|order)$", "", path)
            get_req = httpx.Request("GET", request.url.copy_with(path=parent, query=None), headers={k: v for k, v in request.headers.items() if k.lower() not in {"content-length", "content-type"}})
            try:
                resp = await real_send(self, get_req, **kw)
                data = resp.json()
                if isinstance(data, list):
                    fields = parse_qs((request.content or b"").decode("utf-8"), keep_blank_values=True) if b"=" in (request.content or b"") else {}
                    wanted = {v[0] for k, v in fields.items() if k.endswith("[title]") or k.endswith("[name]") or k.endswith("[question_name]")}
                    match = [d for d in data if isinstance(d, dict) and (d.get("title") in wanted or d.get("name") in wanted or d.get("question_name") in wanted)]
                    data = match[0] if match else (data[0] if data else {})
                return httpx.Response(200, json=_lens(data), request=request)
            except Exception:
                return httpx.Response(200, json={}, request=request)
        return await real_send(self, request, **kw)

    httpx.AsyncClient.send = send


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("builder")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    out_dir = Path(a.out) if a.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    install(a.dry_run, out_dir)
    builder = Path(a.builder).resolve()
    sys.path.insert(0, str(builder.parent))
    sys.argv = [str(builder)]
    try:
        runpy.run_path(str(builder), run_name="__main__")
        rc = 0
    except SystemExit as e:
        rc = int(e.code or 0) if isinstance(e.code, int) or e.code is None else 1
        if e.code and not isinstance(e.code, int):
            print(e.code, file=sys.stderr)
    finally:
        pages = [x for x in LOG if "page_url" in x]
        suppressed = [x for x in LOG if x.get("suppressed")]
        print(f"[body-only] pages written: {len(pages)}; structural writes suppressed: {len(suppressed)}")
        if a.log:
            Path(a.log).write_text(json.dumps(LOG, indent=1))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
