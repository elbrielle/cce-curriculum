"""Run structural and readability checks across Canvas HTML templates."""

import argparse
import re
from pathlib import Path

from bs4 import BeautifulSoup
import textstat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("patterns", nargs="+", help="Template glob(s), such as wk2-*.html")
    args = parser.parse_args()
    root = Path(__file__).parent / "templates"
    paths = sorted({path for pattern in args.patterns for path in root.glob(pattern)})
    if not paths:
        raise SystemExit("No templates matched")
    for path in paths:
        html = path.read_text()
        soup = BeautifulSoup(html, "html.parser")
        headings = [int(h.name[1]) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        assert not [(a, b) for a, b in zip(headings, headings[1:]) if b > a + 1], f"heading jump: {path}"
        assert all(i.get("alt", "").strip() for i in soup.find_all("img")), f"missing alt: {path}"
        assert all(d.find("summary") for d in soup.find_all("details")), f"unlabeled details: {path}"
        assert not soup.find("table"), f"layout table: {path}"
        assert "enhanceable_content" not in html, f"legacy Canvas tabs: {path}"
        unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", html)))
        visible_tokens = re.findall(r"\{\{[^}]+\}\}", soup.get_text(" "))
        reading = None if visible_tokens else round(textstat.flesch_kincaid_grade(soup.get_text(" ")), 1)
        print(path.name, {"fk": reading, "images": len(soup.find_all("img")), "details": len(soup.find_all("details")), "tokens": len(unresolved)})


if __name__ == "__main__":
    main()
