#!/usr/bin/env python3
"""Asset helpers for CCE decks.

  crop  IN OUT x0 y0 x1 y1 [--box bx0 by0 bx1 by1] [--scale 0.5]
        Crop a region of an image; optionally draw a pink box (the CCE "look here" mark) around a sub-region
        given in the ORIGINAL image's coordinates.
  element HTML OUT "css selector or text=..." [--pad 16] [--box "selector or text=..."]
        Render a local HTML page (a Canvas student page fetched by fetch_pages.py) with Playwright and
        screenshot one element at 2x, optionally boxing a descendant element.
  fetch  COURSE_ID SLUG OUT.html   (token on stdin)
        Fetch a Canvas page body, inline its Canvas file images, wrap it in a Canvas-like stylesheet.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import os
import re
import sys
from pathlib import Path

PINK = (215, 26, 101)
CSS = """<style>body{margin:0;background:#fff;font-family:'Lato',Arial,Helvetica,sans-serif;font-size:16px;color:#2d3b45;line-height:1.5}
.wrap{width:1000px;padding:24px 32px}h1.t{font-size:32px;font-weight:400;margin:0 0 20px;border-bottom:1px solid #c7cdd1;padding-bottom:8px}
h2{font-size:22px;font-weight:700}h3{font-size:18px}a{color:#0374b5}img{max-width:100%}</style>"""


def crop(a):
    from PIL import Image, ImageDraw
    im = Image.open(a.inp)
    x0, y0, x1, y1 = a.region
    out = im.crop((x0, y0, x1, y1))
    if a.box:
        d = ImageDraw.Draw(out)
        bx0, by0, bx1, by1 = a.box
        d.rectangle((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0), outline=PINK, width=a.width)
    if a.scale and a.scale != 1:
        out = out.resize((int(out.width * a.scale), int(out.height * a.scale)), Image.LANCZOS)
    out.save(a.out, quality=95)
    print(a.out, out.size)


async def _element(a):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1064, "height": 900}, device_scale_factor=2)
        await pg.goto("file://" + str(Path(a.html).resolve()))
        await pg.wait_for_timeout(300)
        el = pg.locator(a.selector).first
        bb = await el.bounding_box()
        pad = a.pad
        clip = {"x": max(0, bb["x"] - pad), "y": max(0, bb["y"] - pad), "width": bb["width"] + 2 * pad, "height": bb["height"] + 2 * pad}
        if a.box:
            inner = await pg.locator(a.box).first.bounding_box()
            await pg.evaluate(
                """([x,y,w,h]) => { const d=document.createElement('div'); d.style.cssText=`position:absolute;left:${x-8}px;top:${y-8}px;width:${w+16}px;height:${h+16}px;border:5px solid #D71A65;border-radius:4px;box-sizing:border-box;z-index:9999;pointer-events:none`; document.body.appendChild(d); }""",
                [inner["x"], inner["y"], inner["width"], inner["height"]],
            )
        await pg.screenshot(path=a.out, clip=clip, full_page=True)
        await b.close()
    print(a.out, clip)


def fetch(a):
    import httpx
    tok = sys.stdin.readline().strip()
    c = httpx.Client(headers={"Authorization": f"Bearer {tok}"}, timeout=60)
    base = "https://learn.irvingisd.net"
    p = c.get(f"{base}/api/v1/courses/{a.course}/pages/{a.slug}").json()
    body = p["body"]

    def repl(m):
        fid = m.group(1)
        r = c.get(f"{base}/api/v1/courses/{a.course}/files/{fid}").json()
        data = c.get(r["url"], follow_redirects=True).content
        return f'src="data:{r["content-type"]};base64,{base64.b64encode(data).decode()}"'

    body = re.sub(r'src="[^"]*?/files/(\d+)/preview[^"]*"', repl, body)
    Path(a.out).write_text(f"<!doctype html><html><head><meta charset=utf-8>{CSS}</head><body><div class=wrap><h1 class=t>{p['title']}</h1>{body}</div></body></html>")
    print(a.out, p["title"])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("crop"); c.add_argument("inp"); c.add_argument("out"); c.add_argument("region", type=int, nargs=4)
    c.add_argument("--box", type=int, nargs=4); c.add_argument("--scale", type=float, default=1.0); c.add_argument("--width", type=int, default=6)
    e = sub.add_parser("element"); e.add_argument("html"); e.add_argument("out"); e.add_argument("selector"); e.add_argument("--pad", type=int, default=16); e.add_argument("--box")
    f = sub.add_parser("fetch"); f.add_argument("course", type=int); f.add_argument("slug"); f.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "crop": crop(a)
    elif a.cmd == "element": asyncio.run(_element(a))
    else: fetch(a)


if __name__ == "__main__":
    main()
