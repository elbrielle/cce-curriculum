#!/usr/bin/env python3
"""Build the public-safe CCE curriculum mirror from canonical Markdown."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "public-site"
DOCS_ROOT = ROOT / "docs"
DEFAULT_OUTPUT = SITE_ROOT / "dist"

CHAPTERS = {
    "1sw": {
        "number": "01",
        "title": "IT & Manufacturing",
        "description": "Start with career self-discovery, then investigate the systems, people, and skills behind computing and modern production.",
        "color": "var(--chapter-1)",
    },
    "2sw": {
        "number": "02",
        "title": "Law, Public Service & Health Science",
        "description": "Use evidence, communication, and care-centered decisions across legal, emergency, and health pathways.",
        "color": "var(--chapter-2)",
    },
    "3sw": {
        "number": "03",
        "title": "Agriculture, Hospitality, Human Services & Business",
        "description": "Connect practical work, service, creativity, and entrepreneurship to real career evidence.",
        "color": "var(--chapter-3)",
    },
    "4sw": {
        "number": "04",
        "title": "Career Planning, Transportation & Engineering",
        "description": "Turn exploration into a course plan while testing how routes, systems, and design choices work.",
        "color": "var(--chapter-4)",
    },
    "5sw": {
        "number": "05",
        "title": "Architecture & Construction",
        "description": "Read constraints, compare skilled-trade routes, and connect work decisions to money and place.",
        "color": "var(--chapter-5)",
    },
    "6sw": {
        "number": "06",
        "title": "Education, Arts, Business & Capstone",
        "description": "Practice how people teach, design, market, sell, apply, interview, and communicate a career plan.",
        "color": "var(--chapter-6)",
    },
}

DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
MARKDOWN_EXTENSIONS = ["tables", "admonition", "attr_list", "fenced_code", "sane_lists"]


@dataclass(frozen=True)
class Page:
    source: Path
    output: Path
    title: str
    kind: str
    eyebrow: str
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def first_heading(source: Path) -> str:
    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError(f"Missing H1: {source.relative_to(ROOT)}")


def compact_summary(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:177].rsplit(" ", 1)[0] + "…") if len(text) > 180 else text


def section_paragraph(lines: list[str], heading: str) -> str:
    try:
        start = next(index for index, line in enumerate(lines) if line.strip().lower() == heading.lower()) + 1
    except StopIteration:
        return ""
    paragraph: list[str] = []
    for raw in lines[start:]:
        line = raw.strip()
        if line.startswith("#"):
            break
        if not line:
            if paragraph:
                break
            continue
        if line.startswith(("- ", "* ", "|", "!!!", ">", "<!--")):
            if paragraph:
                break
            continue
        paragraph.append(line)
    return compact_summary(" ".join(paragraph))


def first_summary(source: Path) -> str:
    lines = source.read_text(encoding="utf-8").splitlines()
    if source.name == "overview.md":
        for heading in ("## Weekly objective", "## Lesson Objective"):
            objective = section_paragraph(lines, heading)
            if objective:
                return objective
    if re.fullmatch(r"day[1-5]\.md", source.name):
        for line in lines:
            match = re.match(r"- \*\*Objective:\*\*\s*(.+)", line.strip())
            if match:
                return compact_summary(match.group(1))
    paragraphs: list[str] = []
    collecting = False
    for raw in lines:
        line = raw.strip()
        if line.startswith("#") or line.startswith("<!--") or line.startswith("|") or line.startswith("!!!"):
            if collecting:
                break
            continue
        if not line:
            if collecting:
                break
            continue
        if line.startswith(("- ", "* ", ">", "```")):
            if collecting:
                break
            continue
        collecting = True
        paragraphs.append(re.sub(r"[*_`]", "", line))
    return compact_summary(" ".join(paragraphs))


def output_for_markdown(source: Path) -> Path:
    rel = source.relative_to(DOCS_ROOT)
    parts = rel.parts
    if rel == Path("index.md"):
        return Path("index.html")
    if rel == Path("scope-and-sequence.md"):
        return Path("resources/scope-and-sequence/index.html")
    if parts[0] == "resources":
        return Path("resources", *parts[1:-1], source.stem, "index.html")
    if len(parts) == 2 and parts[1] == "cfa.md":
        return Path("curriculum", parts[0], "cfa", "index.html")
    if len(parts) == 3 and parts[1].startswith("wk"):
        week_root = Path("curriculum", parts[0], parts[1])
        if source.name == "overview.md":
            return week_root / "index.html"
        match = re.fullmatch(r"day([1-5])\.md", source.name)
        if match:
            return week_root / f"day-{match.group(1)}" / "index.html"
    raise ValueError(f"No public route for {source.relative_to(ROOT)}")


def classify(source: Path) -> tuple[str, str]:
    rel = source.relative_to(DOCS_ROOT)
    if rel == Path("scope-and-sequence.md"):
        return "resource", "36-week planning reference"
    if rel.parts[0] == "resources":
        return "resource", "Teacher resource"
    if source.name == "overview.md":
        week = re.match(r"wk(\d+)", rel.parts[1]).group(1)
        return "week", f"{CHAPTERS[rel.parts[0]]['title']} · Week {week}"
    match = re.fullmatch(r"day([1-5])\.md", source.name)
    if match:
        week = re.match(r"wk(\d+)", rel.parts[1]).group(1)
        day = int(match.group(1))
        return "lesson", f"Six Weeks {int(rel.parts[0][0])} · Week {week} · {DAY_LABELS[day - 1]}"
    if source.name == "cfa.md":
        return "assessment", "Common formative assessment"
    return "page", "CCE curriculum"


def discover_pages() -> dict[Path, Page]:
    pages: dict[Path, Page] = {}
    for source in sorted(DOCS_ROOT.rglob("*.md")):
        if source == DOCS_ROOT / "index.md":
            continue
        output = output_for_markdown(source)
        kind, eyebrow = classify(source)
        pages[source.resolve()] = Page(source, output, first_heading(source), kind, eyebrow, first_summary(source))
    return pages


def rel_url(current: Path, target: Path) -> str:
    return PurePosixPath(os.path.relpath(target.as_posix(), current.parent.as_posix())).as_posix()


def strip_fragment_query(href: str) -> tuple[str, str, str]:
    parsed = urlsplit(href)
    return unquote(parsed.path), parsed.query, parsed.fragment


def markdown_html(page: Page, pages: dict[Path, Page], output_root: Path, copied: dict[Path, Path], policy: dict) -> str:
    body = markdown.markdown(page.source.read_text(encoding="utf-8"), extensions=MARKDOWN_EXTENSIONS)
    soup = BeautifulSoup(body, "html.parser")
    source_h1 = soup.find("h1")
    if source_h1:
        source_h1.decompose()
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if href.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        if href.startswith("#"):
            continue
        path_part, query, fragment = strip_fragment_query(href)
        resolved = (page.source.parent / path_part).resolve()
        if resolved in pages:
            new_href = rel_url(page.output, pages[resolved].output)
        elif resolved.is_file():
            try:
                resource_rel = resolved.relative_to(DOCS_ROOT / "resources")
            except ValueError as exc:
                raise ValueError(f"Public page links outside docs/resources: {page.source.relative_to(ROOT)} -> {href}") from exc
            lowered = resolved.as_posix().lower()
            if any(fragment_value in lowered for fragment_value in policy["protected_path_fragments"]):
                raise ValueError(f"Protected asset linked from public page: {resolved.relative_to(ROOT)}")
            if resolved.suffix.lower() in policy["protected_file_extensions"]:
                raise ValueError(f"Protected file type linked from public page: {resolved.relative_to(ROOT)}")
            target = Path("assets", "resources", resource_rel)
            copied[resolved] = target
            new_href = rel_url(page.output, target)
        else:
            raise FileNotFoundError(f"Broken local link: {page.source.relative_to(ROOT)} -> {href}")
        if query:
            new_href += f"?{query}"
        if fragment:
            new_href += f"#{fragment}"
        anchor["href"] = new_href
    for image in soup.find_all("img", src=True):
        src = image["src"].strip()
        if src.startswith(("http://", "https://", "data:")):
            continue
        resolved = (page.source.parent / strip_fragment_query(src)[0]).resolve()
        try:
            resource_rel = resolved.relative_to(DOCS_ROOT / "resources")
        except ValueError as exc:
            raise ValueError(f"Public image outside docs/resources: {page.source.relative_to(ROOT)} -> {src}") from exc
        if not resolved.is_file():
            raise FileNotFoundError(f"Broken image: {page.source.relative_to(ROOT)} -> {src}")
        target = Path("assets", "resources", resource_rel)
        copied[resolved] = target
        image["src"] = rel_url(page.output, target)
        image["loading"] = "lazy"
        image["decoding"] = "async"
    return str(soup)


def day_pages_for_week(page: Page, pages: dict[Path, Page]) -> list[Page]:
    week_dir = page.source.parent
    return [pages[(week_dir / f"day{day}.md").resolve()] for day in range(1, 6)]


def breadcrumb(page: Page, pages: dict[Path, Page]) -> list[tuple[str, Path]]:
    crumbs: list[tuple[str, Path]] = [("Home", Path("index.html")), ("Curriculum", Path("curriculum/index.html"))]
    rel = page.source.relative_to(DOCS_ROOT)
    if page.kind in {"week", "lesson"}:
        overview = pages[(page.source.parent / "overview.md").resolve()]
        if page.kind == "lesson":
            crumbs.append((overview.title, overview.output))
    if page.kind == "resource":
        crumbs = [("Home", Path("index.html")), ("Resources", Path("resources/index.html"))]
    return crumbs


def navigation(current: Path) -> str:
    links = [
        ("Home", Path("index.html")),
        ("Curriculum", Path("curriculum/index.html")),
        ("Resources", Path("resources/index.html")),
        ("About", Path("about/index.html")),
    ]
    return "".join(f'<a href="{rel_url(current, target)}">{label}</a>' for label, target in links)


def page_shell(current: Path, title: str, description: str, body: str, page_class: str = "") -> str:
    css = rel_url(current, Path("assets/site.css"))
    js = rel_url(current, Path("assets/site.js"))
    search_index = rel_url(current, Path("data/search-index.json"))
    home = rel_url(current, Path("index.html"))
    escaped_title = html.escape(title)
    escaped_description = html.escape(description or "CCE curriculum planning mirror")
    return f"""<!doctype html>
<html lang="en" data-search-index="{search_index}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escaped_description}">
  <meta name="theme-color" content="#fbf8ff">
  <title>{escaped_title} · CCE Curriculum</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{css}">
</head>
<body class="{page_class}">
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="wordmark" href="{home}" aria-label="CCE Curriculum home">
        <span class="wordmark-mark">CCE</span>
        <span class="wordmark-copy"><strong>Career & College Explorations</strong><span>Irving ISD · Grade 7</span></span>
      </a>
      <button class="header-button menu-toggle" type="button" data-menu-toggle aria-expanded="false">Menu</button>
      <nav class="site-nav" data-site-nav aria-label="Main navigation">
        {navigation(current)}
        <button class="header-button" type="button" data-search-toggle aria-expanded="false">Search</button>
      </nav>
    </div>
  </header>
  <section class="search-panel" data-search-panel hidden>
    <div class="search-inner">
      <label for="site-search" class="eyebrow">Search the 36-week curriculum</label>
      <input id="site-search" data-search-input type="search" autocomplete="off" placeholder="Try cybersecurity, salary, d(4)(C), or interview">
      <div class="search-results" data-search-results aria-live="polite"><p class="search-hint">Search by career, skill, week, TEKS, or lesson title.</p></div>
    </div>
  </section>
  <main id="main-content">{body}</main>
  <footer class="site-footer">
    <div class="shell footer-grid">
      <div><h2>Public curriculum reference</h2><p>This site contains the course sequence and public resources. Canvas holds the active lessons, assignments, and licensed source material.</p></div>
      <div><h2>Source repository</h2><p>The pages are generated from the tracked curriculum files. <a href="https://github.com/elbrielle/cce-curriculum">View the source on GitHub</a>.</p></div>
    </div>
  </footer>
  <script src="{js}" defer></script>
</body>
</html>"""


def render_content_page(page: Page, content: str, pages: dict[Path, Page]) -> str:
    crumb_html = "<span aria-hidden='true'>/</span>".join(
        f'<a href="{rel_url(page.output, target)}">{html.escape(label)}</a>' for label, target in breadcrumb(page, pages)
    )
    rail = ""
    if page.kind in {"week", "lesson"}:
        overview = pages[(page.source.parent / "overview.md").resolve()]
        days = day_pages_for_week(overview, pages)
        items = [f'<a href="{rel_url(page.output, overview.output)}"><b>W</b><span>Week overview</span></a>']
        for number, day_page in enumerate(days, 1):
            items.append(f'<a href="{rel_url(page.output, day_page.output)}"><b>{number}</b><span>{html.escape(day_page.title)}</span></a>')
        rail = f'<aside class="day-rail" aria-label="Week navigation"><strong>This week</strong>{"".join(items)}</aside>'
    boundary = ""
    if page.kind in {"week", "lesson", "assessment"}:
        boundary = '<aside class="public-boundary"><strong>Planning mirror:</strong> authenticated student links, licensed workbook pages, platform interactions, and submissions live in Canvas. This page preserves the public-safe instructional plan.</aside>'
    body = f"""
      <header class="page-hero shell">
        <nav class="breadcrumb" aria-label="Breadcrumb">{crumb_html}</nav>
        <p class="eyebrow">{html.escape(page.eyebrow)}</p>
        <h1>{html.escape(page.title)}</h1>
        {f'<p class="page-summary">{html.escape(page.summary)}</p>' if page.summary else ''}
      </header>
      <div class="shell week-layout">
        <article class="prose">{content}{boundary}</article>
        {rail}
      </div>"""
    return page_shell(page.output, page.title, page.summary, body, f"page-{page.kind}")


def week_number(page: Page) -> int:
    return int(re.match(r"wk(\d+)", page.source.parent.name).group(1))


def weeks_by_chapter(pages: dict[Path, Page]) -> dict[str, list[Page]]:
    result = {key: [] for key in CHAPTERS}
    for page in pages.values():
        if page.kind == "week":
            result[page.source.relative_to(DOCS_ROOT).parts[0]].append(page)
    for rows in result.values():
        rows.sort(key=week_number)
    return result


def home_page(pages: dict[Path, Page]) -> str:
    current = Path("index.html")
    grouped = weeks_by_chapter(pages)
    launch = next(page for page in pages.values() if page.kind == "week" and page.source.parent.name == "wk0-classroom-routines")
    launch_days = day_pages_for_week(launch, pages)
    chapter_bands = "".join(
        f'''<a class="chapter-band" style="--chapter-bg:{info['color']}" href="{rel_url(current, Path('curriculum/index.html'))}#chapter-{key}">
          <span class="chapter-number">{info['number']}</span><span><h3>{info['title']}</h3><p>{info['description']}</p></span><span class="chapter-count">{len(grouped[key])} weeks</span>
        </a>''' for key, info in CHAPTERS.items()
    )
    launch_cards = "".join(
        f'''<a class="launch-day" href="{rel_url(current, day.output)}"><span>{DAY_LABELS[index - 1]} · Day {index}</span><h3>{html.escape(day.title.replace(f'Day {index}: ', ''))}</h3><p>{html.escape(day.summary)}</p></a>'''
        for index, day in enumerate(launch_days, 1)
    )
    body = f"""
    <section class="hero"><div class="shell hero-grid">
      <div><p class="eyebrow">Irving ISD · Grade 7 · TEKS §127.2</p><h1>Career and College Explorations</h1><p class="hero-copy">A public reference for the 36-week Grade 7 curriculum, including weekly overviews, daily lesson plans, pacing, TEKS alignment, and public resources.</p><div class="actions"><a class="button primary" href="{rel_url(current, Path('curriculum/index.html'))}">Browse all 36 weeks</a><a class="button secondary" href="{rel_url(current, launch.output)}">Open the launch week</a><a class="button tertiary" href="{rel_url(current, Path('resources/scope-and-sequence/index.html'))}">Read the scope & sequence</a></div></div>
      <div class="hero-compass" aria-label="36 weeks across six grading periods"><span class="route-line" aria-hidden="true"></span><strong>36</strong><p>weeks organized across six grading periods.</p></div>
    </div></section>
    <section class="section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Course sequence</p><h2>Six grading periods</h2></div><p>The course is organized by grading period and week. Each week links to an overview and five daily lesson plans.</p></div><div class="chapter-list">{chapter_bands}</div></div></section>
    <section class="section launch-section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Launch week</p><h2>CCE routines and career self-discovery</h2></div><p>The opening week establishes the notebook route, completes the assigned H&L and <em>Find Your Future</em> work, and checks Xello access.</p></div><div class="launch-rail">{launch_cards}</div></div></section>
    <section class="section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Course tools</p><h2>Materials and platforms</h2></div><p>Each material or platform has a defined role in the course.</p></div><div class="source-roles"><article class="source-role"><h3>H&L + Find Your Future</h3><p>Core career content, including personality, work values, career evidence, pathways, and career planning.</p></article><article class="source-role"><h3>Canvas</h3><p>Daily Teacher and Student Guides, assignments, authenticated links, and licensed source files.</p></article><article class="source-role"><h3>Xello + technology</h3><p>Required Xello work and named technology extensions in the scope and sequence.</p></article></div></div></section>
    """
    return page_shell(current, "Career and College Explorations", "A 36-week Grade 7 Career and College Explorations curriculum for Irving ISD.", body, "page-home")


def curriculum_page(pages: dict[Path, Page]) -> str:
    current = Path("curriculum/index.html")
    grouped = weeks_by_chapter(pages)
    sections = []
    for key, info in CHAPTERS.items():
        rows = []
        for page in grouped[key]:
            number = week_number(page)
            search = html.escape(f"{page.title} {page.summary} {info['title']}".lower(), quote=True)
            rows.append(f'''<a class="week-row" data-week-row data-search="{search}" href="{rel_url(current, page.output)}"><span>Week {number}</span><h3>{html.escape(page.title)}</h3><small>{html.escape(page.summary)}</small></a>''')
        sections.append(f'''<section class="curriculum-chapter" id="chapter-{key}" data-six-weeks-section><div><p class="eyebrow">Six Weeks {int(key[0])}</p><h2>{info['title']}</h2></div><div class="week-list">{"".join(rows)}</div></section>''')
    body = f'''<header class="page-hero shell"><p class="eyebrow">36 weeks · 180 lessons</p><h1>The CCE year</h1><p class="page-summary">Follow the sequence by six-weeks chapter, or search for a career, skill, TEKS code, or instructional move.</p></header><div class="shell"><label class="curriculum-filter"><span class="eyebrow">Filter the curriculum</span><input data-curriculum-filter type="search" placeholder="Try health science, teamwork, or d(4)(A)"></label>{"".join(sections)}</div>'''
    return page_shell(current, "The CCE year", "Browse all 36 weeks of the CCE curriculum.", body, "page-curriculum")


def resources_page(pages: dict[Path, Page]) -> str:
    current = Path("resources/index.html")
    resources = sorted((page for page in pages.values() if page.kind == "resource"), key=lambda page: page.title)
    cards = "".join(f'<a class="resource-link" href="{rel_url(current, page.output)}"><h2>{html.escape(page.title)}</h2><p>{html.escape(page.summary)}</p></a>' for page in resources)
    body = f'''<header class="page-hero shell"><p class="eyebrow">Public planning tools</p><h1>Course resources</h1><p class="page-summary">Pacing, TEKS, assessment, facilitation, and implementation references generated from the same curriculum source.</p></header><div class="shell resource-index">{cards}</div>'''
    return page_shell(current, "Course resources", "Public CCE planning and implementation resources.", body, "page-resources")


def about_page() -> str:
    current = Path("about/index.html")
    body = '''<header class="page-hero shell"><p class="eyebrow">Site information</p><h1>About this curriculum site</h1><p class="page-summary">A public reference for administrators, teachers, and portfolio review.</p></header><div class="shell"><article class="prose"><h2>Course delivery</h2><p>Canvas holds the active Teacher and Student Guides, assignments, authenticated platform links, and licensed files. Teachers control when course materials are published.</p><h2>Public curriculum reference</h2><p>This site contains the tracked 36-week curriculum, public planning documents, and public-safe resources. Its pages are generated from the curriculum source files in GitHub.</p><h2>Licensed and private materials</h2><p>Hats & Ladders, <em>Find Your Future</em>, Xello, Climber Notes, private AVID source files, and student information are not included on this public site.</p><h2>Source use and adaptations</h2><p>Teacher-created materials are preserved when they fit the course. Changes are documented when Grade 7, CCE, access, or timing requires an adaptation.</p></article></div>'''
    return page_shell(current, "About this curriculum site", "A public reference for the CCE curriculum and its source boundaries.", body, "page-about")


def write_text(output_root: Path, rel: Path, value: str) -> None:
    target = output_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value, encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output_root: Path) -> None:
    policy = json.loads((SITE_ROOT / "publication-policy.json").read_text(encoding="utf-8"))
    pages = discover_pages()
    copied: dict[Path, Path] = {}
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)
    shutil.copytree(SITE_ROOT / "assets", output_root / "assets")

    search_entries = []
    rendered_manifest = []
    for page in pages.values():
        content = markdown_html(page, pages, output_root, copied, policy)
        rendered = render_content_page(page, content, pages)
        write_text(output_root, page.output, rendered)
        plain = BeautifulSoup(content, "html.parser").get_text(" ", strip=True)
        search_entries.append({
            "title": page.title,
            "eyebrow": page.eyebrow,
            "summary": page.summary,
            "url": rel_url(Path("index.html"), page.output),
            "search": f"{page.title} {page.eyebrow} {page.summary} {plain}".lower(),
        })
        rendered_manifest.append({"source": page.source.relative_to(ROOT).as_posix(), "output": page.output.as_posix(), "kind": page.kind})

    write_text(output_root, Path("index.html"), home_page(pages))
    write_text(output_root, Path("curriculum/index.html"), curriculum_page(pages))
    write_text(output_root, Path("resources/index.html"), resources_page(pages))
    write_text(output_root, Path("about/index.html"), about_page())

    for source, target in sorted(copied.items(), key=lambda item: item[1].as_posix()):
        destination = output_root / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    write_text(output_root, Path("data/search-index.json"), json.dumps(search_entries, ensure_ascii=False, separators=(",", ":")))
    identities = json.loads((SITE_ROOT / "data/module-identities.json").read_text(encoding="utf-8"))
    write_text(output_root, Path("data/module-identities.json"), json.dumps(identities, indent=2))
    manifest = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": os.environ.get("GITHUB_SHA") or "local",
        "pages": rendered_manifest,
        "page_count": len(rendered_manifest) + 4,
        "week_count": len([page for page in pages.values() if page.kind == "week"]),
        "lesson_count": len([page for page in pages.values() if page.kind == "lesson"]),
        "copied_resources": [
            {"source": source.relative_to(ROOT).as_posix(), "output": target.as_posix(), "sha256": sha256(source), "bytes": source.stat().st_size}
            for source, target in sorted(copied.items(), key=lambda item: item[1].as_posix())
        ],
        "publication_policy": policy,
    }
    write_text(output_root, Path("data/site-manifest.json"), json.dumps(manifest, indent=2))
    write_text(output_root, Path(".nojekyll"), "")
    print(f"Built {manifest['page_count']} pages, {manifest['week_count']} weeks, {manifest['lesson_count']} lessons, {len(copied)} linked resources -> {output_root}")


if __name__ == "__main__":
    build(parse_args().output.resolve())
