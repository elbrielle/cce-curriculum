#!/usr/bin/env python3
"""Render a day plan's **EXIT TICKET** block (docs/<sw>/<week>/dayN.md) as Docs-friendly HTML,
so the exit-ticket Google Doc is built from the same text as the plan and the PDF.

  python3 build/google_docs/render_exit_ticket_gdoc_html.py 2SW-Wk1-Day1 [...] --out DIR
Prints one line per day: <day_key>\t<title>\t<html path>.
"""
from __future__ import annotations
import argparse, html, json, re, sys
from pathlib import Path
import markdown as md
sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_worksheet_gdoc_html import pre_markdown, post_html, TABLE_STYLE, CELL_STYLE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "build/google_docs/student_response_route_registry.json"
TEKS = re.compile(r"\s*\*\(d\(\d\)\([A-Z]\)(?:,\s*d\(\d\)\([A-Z]\))*\)\*")
HEAD = re.compile(r"\*\*EXIT TICKET\*\*\s*\(([^)]*)\)[^:]*:\s*")


def exit_block(day_md: str):
    i = day_md.find("**EXIT TICKET**")
    if i < 0:
        return None, None
    j = day_md.find("\n## ", i)
    block = day_md[i:j if j > 0 else None].strip()
    m = HEAD.match(block)
    fmt = m.group(1) if m else "Exit Ticket"
    body = block[m.end():] if m else block
    body = TEKS.sub("", body)
    body = re.sub(r"\n-{3,}\s*$", "", body.strip()).strip()
    return fmt, body


def add_boxes(body: str) -> str:
    lines = body.split("\n"); out = []
    for k, ln in enumerate(lines):
        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", ln)
        if m:
            ln = f"{m.group(1)}**{m.group(2)}.** {m.group(3)}"
        out.append(ln)
        if m:
            nxt = next((x for x in lines[k + 1:] if x.strip()), "")
            if not (re.match(r"^\s*_{6,}\s*$", nxt) or nxt.strip().startswith(("|", "[[")) or re.match(r"^\s*\d+\.\s", nxt)) and "___" not in ln:
                out += ["", "[[lines: 3]]"]
            elif re.match(r"^\s*\d+\.\s", nxt) and "___" not in ln:
                out += ["", "[[lines: 2]]"]
    body = "\n".join(out).rstrip()
    if not body.endswith("]]") and not body.endswith("|") and not re.search(r"_{6,}\s*$", body):
        body += "\n\n[[lines: 4]]"
    return body


def render(day_key: str, route: dict) -> tuple[str, str]:
    day_md = (ROOT / route["source"]["day_source"]["path"]).read_text(encoding="utf-8")
    fmt, body = exit_block(day_md)
    if body is None:
        raise SystemExit(f"{day_key}: no **EXIT TICKET** block in the day plan")
    sw, wk, day = re.match(r"(\d)SW-Wk(\d+)-Day(\d)", day_key).groups()
    title = f"CCE | {sw}SW Wk{wk} Day {day} | Exit Ticket ({fmt})"
    body_html = post_html(md.markdown(pre_markdown(add_boxes(body)), extensions=["tables"]))
    header = (
        f"<p style='font-size:16pt;font-weight:bold'>{html.escape(title)}</p>"
        "<p style='color:#5f6368'>Career and College Explorations · Exit Ticket</p>"
        f"<table style='{TABLE_STYLE}'><tr><td style='{CELL_STYLE}'><b>Name:</b>&nbsp;</td>"
        f"<td style='{CELL_STYLE}'><b>Class / Period:</b>&nbsp;</td><td style='{CELL_STYLE}'><b>Date:</b>&nbsp;</td></tr></table>"
        "<p style='font-size:10pt;color:#5f6368'>Type in the shaded boxes. Use evidence from today's work. / Escribe en los cuadros sombreados.</p>"
    )
    return title, f"<html><body style='font-family:Arial;font-size:11pt'>{header}{body_html}</body></html>"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("days", nargs="+"); ap.add_argument("--out", default=str(ROOT / ".tmp/exit-html"))
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    routes = {r["day_key"]: r for r in json.load(open(REG))["routes"]}
    for dk in a.days:
        title, h = render(dk, routes[dk])
        p = out / f"{dk}.html"; p.write_text(h, encoding="utf-8")
        print(f"{dk}\t{title}\t{p}")


if __name__ == "__main__":
    main()
