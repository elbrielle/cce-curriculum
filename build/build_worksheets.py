#!/usr/bin/env python3
"""
build_worksheets.py — Render printable CCE worksheets from source markdown.

Companion to build_pdfs.py (exit tickets). Same Irving ISD print language,
different input: a worksheet is authored as a standalone source file rather
than extracted from a day page.

Pipeline:
  1. Read every build/worksheet_sources/*.md
  2. Parse the front matter block and the body markers
  3. Render HTML via build/worksheet_template/template.html.j2 + worksheets.css
  4. Print to PDF with Playwright headless Chromium (Letter, portrait or
     landscape, repeating page footer in the bottom margin)
  5. Output: docs/resources/worksheets/<slug>.pdf

Source contract (see cce-curriculum/notes/exit-ticket-pdf-pipeline.md
"Worksheet pipeline"):

    ---
    title: Career Research Worksheet
    slug: career-research-worksheet
    kind: worksheet            # worksheet | rubric | contract | reference | scaffold
    weeks: 1sw/wk0-classroom-routines, 1sw/wk1-robotics-manufacturing
    audience: student          # student | teacher
    variant_of:                # parent slug, empty for masters
    language: en               # en | bilingual
    pages: 1                   # max Letter pages
    orientation: portrait      # portrait | landscape
    ---
    Body in GitHub markdown. H1 is NOT repeated (the title renders in the
    header band). Markers:
      [[lines: 4]]     four ruled writing lines
      [[box: 2.5]]     empty drawing/writing box 2.5 inches tall
      [[pagebreak]]    hard page break (only when pages > 1)
      - [ ] item       checkbox line
    Tables: empty cells print as handwriting space (generous row height).
    Student sheets get Name/Date/Period slots automatically.

Usage:
  /usr/bin/python3 build/build_worksheets.py                     # all real sources
  /usr/bin/python3 build/build_worksheets.py build/worksheet_sources/foo.md
  /usr/bin/python3 build/build_worksheets.py --fixtures          # test fixtures only
  /usr/bin/python3 build/build_worksheets.py --dry-run           # parse + validate
  /usr/bin/python3 build/build_worksheets.py --html-only         # write HTML previews
  /usr/bin/python3 build/build_worksheets.py --strict            # exit 2 on any warning
"""

import argparse
import asyncio
import html as html_mod
import re
import subprocess
import sys
from pathlib import Path

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright

# Reuse the exit-ticket pipeline's slug + blank-run helpers so the two
# families stay consistent. build_pdfs.py is import-safe (main() is guarded).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_pdfs import slugify, INLINE_UNDERSCORES, UNDERSCORE_LINE  # noqa: E402


# ---------- Paths ----------

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "build" / "worksheet_sources"
TEMPLATE_DIR = ROOT / "build" / "worksheet_template"
OUT_DIR = ROOT / "docs" / "resources" / "worksheets"
FIXTURE_OUT_DIR = ROOT / "build" / "_fixture_out"
RENDER_TMP = TEMPLATE_DIR / "_render.html"
FIXTURE_TOKEN = "_fixtures"


# ---------- Front matter ----------

FM_FIELDS = (
    "title", "slug", "kind", "weeks", "audience",
    "variant_of", "language", "pages", "orientation",
)

KINDS = ("worksheet", "rubric", "contract", "reference", "scaffold")
AUDIENCES = ("student", "teacher")
LANGUAGES = ("en", "bilingual")
ORIENTATIONS = ("portrait", "landscape")

KIND_LABELS = {
    "worksheet": "Student Worksheet",
    "rubric": "Rubric",
    "contract": "Class Contract",
    "reference": "Reference Sheet",
    "scaffold": "Scaffold",
}

SLUG_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

MAX_PAGES = 12
MAX_LINES = 60
MIN_BOX_IN = 0.25
MAX_BOX_IN = 9.0


class Sheet(object):
    """One parsed worksheet source."""

    def __init__(self, path):
        self.path = path
        self.title = ""
        self.slug = ""
        self.kind = "worksheet"
        self.weeks = ""
        self.audience = "student"
        self.variant_of = ""
        self.language = "en"
        self.pages = 1
        self.orientation = "portrait"
        self.body = ""
        self.body_html = ""
        self.warnings = []
        self.rendered_pages = None

    @property
    def is_fixture(self):
        return FIXTURE_TOKEN in self.path.parts

    def warn(self, msg):
        self.warnings.append(msg)


def parse_front_matter(text, sheet):
    """Split `---` front matter from body. Flat `key: value` lines only.

    Hand-rolled rather than YAML on purpose: titles routinely contain colons
    ("Week 1: Careers") and a YAML parser would choke on them unquoted.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        sheet.warn("no front matter block (file must open with ---)")
        return {}, text

    fm = {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            sheet.warn("front matter line is not `key: value`: %r" % raw.strip())
            continue
        key, value = raw.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        # strip an inline `# comment` tail only when it follows whitespace
        value = re.sub(r"\s+#\s.*$", "", value).strip()
        # strip matching quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key not in FM_FIELDS:
            sheet.warn("unknown front matter key %r (ignored)" % key)
            continue
        fm[key] = value

    if end is None:
        sheet.warn("front matter block never closed with ---; treating whole file as body")
        return {}, text

    return fm, "\n".join(lines[end + 1:])


def parse_source(path):
    sheet = Sheet(path)
    text = path.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text, sheet)

    sheet.title = fm.get("title", "").strip()
    if not sheet.title:
        sheet.title = path.stem.replace("-", " ").title()
        sheet.warn("missing `title`; derived %r from the filename" % sheet.title)

    slug = fm.get("slug", "").strip()
    if not slug:
        slug = slugify(path.stem)
        sheet.warn("missing `slug`; derived %r from the filename" % slug)
    elif not SLUG_OK.match(slug):
        fixed = slugify(slug)
        sheet.warn("slug %r is not kebab-case; using %r" % (slug, fixed))
        slug = fixed
    if not sheet.is_fixture and slug != path.stem:
        sheet.warn("slug %r does not match filename %r (output uses the slug)"
                   % (slug, path.stem))
    sheet.slug = slug

    sheet.kind = _enum(fm.get("kind", "worksheet"), KINDS, "kind", "worksheet", sheet)
    sheet.audience = _enum(fm.get("audience", "student"), AUDIENCES, "audience", "student", sheet)
    sheet.language = _enum(fm.get("language", "en"), LANGUAGES, "language", "en", sheet)
    sheet.orientation = _enum(fm.get("orientation", "portrait"), ORIENTATIONS,
                              "orientation", "portrait", sheet)
    sheet.weeks = fm.get("weeks", "").strip()
    sheet.variant_of = fm.get("variant_of", "").strip()

    pages_raw = fm.get("pages", "1").strip() or "1"
    try:
        pages = int(pages_raw)
    except ValueError:
        sheet.warn("pages %r is not an integer; using 1" % pages_raw)
        pages = 1
    if pages < 1:
        sheet.warn("pages %d is below 1; using 1" % pages)
        pages = 1
    if pages > MAX_PAGES:
        sheet.warn("pages %d exceeds the %d-page ceiling; using %d"
                   % (pages, MAX_PAGES, MAX_PAGES))
        pages = MAX_PAGES
    sheet.pages = pages

    sheet.body = body.strip("\n")
    sheet.body_html = render_body_html(sheet)
    return sheet


def _enum(value, allowed, field, default, sheet):
    v = (value or "").strip().lower()
    if not v:
        return default
    if v not in allowed:
        sheet.warn("%s %r is not one of %s; using %r" % (field, v, "/".join(allowed), default))
        return default
    return v


# ---------- Body markers ----------

LINES_MARKER = re.compile(r"\[\[\s*lines\s*:\s*(\d+)\s*\]\]", re.I)
BOX_MARKER = re.compile(r"\[\[\s*box\s*:\s*([0-9]*\.?[0-9]+)\s*(?:in|\")?\s*\]\]", re.I)
PAGEBREAK_MARKER = re.compile(r"\[\[\s*pagebreak\s*\]\]", re.I)
ANY_MARKER = re.compile(
    r"(\[\[\s*lines\s*:\s*\d+\s*\]\]"
    r"|\[\[\s*box\s*:\s*[0-9]*\.?[0-9]+\s*(?:in|\")?\s*\]\]"
    r"|\[\[\s*pagebreak\s*\]\])",
    re.I,
)
UNKNOWN_MARKER = re.compile(r"\[\[[^\]]*\]\]")
TASK_LINE = re.compile(r"^(\s*)[-*+]\s+\[([ xX])\]\s*(.*)$")
TABLE_ROW = re.compile(r"^\s*\|")
FENCE = re.compile(r"^\s*(```|~~~)")


def _lines_block(n, sheet):
    n = int(n)
    if n < 1:
        sheet.warn("[[lines: %d]] below 1; using 1" % n)
        n = 1
    if n > MAX_LINES:
        sheet.warn("[[lines: %d]] above the %d-line ceiling; using %d" % (n, MAX_LINES, MAX_LINES))
        n = MAX_LINES
    rules = "".join('<div class="ws-line"></div>' for _ in range(n))
    return '<div class="ws-lines" data-n="%d">%s</div>' % (n, rules)


def _box_block(height, sheet):
    h = float(height)
    if h < MIN_BOX_IN:
        sheet.warn("[[box: %s]] below %sin; using %sin" % (height, MIN_BOX_IN, MIN_BOX_IN))
        h = MIN_BOX_IN
    if h > MAX_BOX_IN:
        sheet.warn("[[box: %s]] above %sin; using %sin" % (height, MAX_BOX_IN, MAX_BOX_IN))
        h = MAX_BOX_IN
    tall = " ws-box--tall" if h > 8.0 else ""
    return '<div class="ws-box%s" style="height: %.2fin"></div>' % (tall, h)


def _marker_to_html(token, sheet):
    m = LINES_MARKER.fullmatch(token.strip())
    if m:
        return _lines_block(m.group(1), sheet)
    m = BOX_MARKER.fullmatch(token.strip())
    if m:
        return _box_block(m.group(1), sheet)
    if PAGEBREAK_MARKER.fullmatch(token.strip()):
        if sheet.pages < 2:
            sheet.warn("[[pagebreak]] used on a 1-page sheet; raise `pages:` or drop it")
        return '<div class="ws-pagebreak"></div>'
    return ""


def render_body_html(sheet):
    """Markdown body -> HTML, with the worksheet markers expanded first.

    Markers are lifted to their own block so python-markdown treats them as
    raw HTML blocks. A marker sharing a line with prose is split out around
    the prose, which keeps the common `1. Prompt? [[lines: 2]]` form working.
    """
    out = []
    in_fence = False

    for raw in sheet.body.split("\n"):
        if FENCE.match(raw):
            in_fence = not in_fence
            out.append(raw)
            continue
        if in_fence:
            out.append(raw)
            continue

        # Markers inside a markdown table row would destroy the row; strip
        # them (an empty cell already prints as handwriting space).
        if TABLE_ROW.match(raw):
            if ANY_MARKER.search(raw):
                sheet.warn("markers are not supported inside table cells "
                           "(row: %r); marker dropped, cell prints as blank space"
                           % raw.strip()[:60])
                raw = ANY_MARKER.sub(" ", raw)
            out.append(_inline_blanks(raw))
            continue

        # `- [ ] item` -> checkbox line
        task = TASK_LINE.match(raw)
        if task:
            indent, state, text = task.group(1), task.group(2), task.group(3)
            cls = "ws-cb ws-cb--on" if state.lower() == "x" else "ws-cb"
            raw = '%s- <span class="%s"></span>%s' % (indent, cls, text)

        # A line of only underscores -> one ruled writing line
        if UNDERSCORE_LINE.match(raw):
            out.extend(["", _lines_block(1, sheet), ""])
            continue

        if ANY_MARKER.search(raw):
            for seg in ANY_MARKER.split(raw):
                if not seg:
                    continue
                if ANY_MARKER.fullmatch(seg.strip()):
                    out.extend(["", _marker_to_html(seg, sheet), ""])
                elif seg.strip():
                    out.append(_inline_blanks(seg.rstrip()))
            continue

        if UNKNOWN_MARKER.search(raw):
            for bad in UNKNOWN_MARKER.findall(raw):
                sheet.warn("unrecognized marker %r left as literal text" % bad)

        out.append(_inline_blanks(raw))

    # A trailing pagebreak just makes an empty last page.
    while out and out[-1].strip() in ("", '<div class="ws-pagebreak"></div>'):
        if out[-1].strip():
            sheet.warn("trailing [[pagebreak]] dropped (it would print a blank page)")
        out.pop()

    html = md.markdown(
        "\n".join(out),
        extensions=["extra", "tables", "sane_lists", "nl2br"],
    )
    return _tag_task_lists(html)


def _inline_blanks(line):
    """`______` runs become an inline writing blank (same rule as exit tickets)."""
    return INLINE_UNDERSCORES.sub('<span class="ws-blank"></span>', line)


UL_BLOCK = re.compile(r"<ul>(.*?)</ul>", re.S)


def _tag_task_lists(html):
    """Give any <ul> that holds checkboxes the .ws-tasks class (drops bullets).

    The stylesheet also carries a `:has()` rule, so this is belt and braces
    for nested-list shapes the regex can mis-scope.
    """
    def repl(m):
        if "ws-cb" in m.group(1):
            return '<ul class="ws-tasks">%s</ul>' % m.group(1)
        return m.group(0)
    return UL_BLOCK.sub(repl, html)


# ---------- Rendering ----------

def build_jinja_env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=False,
        lstrip_blocks=False,
    )


def sheet_to_context(sheet):
    return {
        "title": sheet.title,
        "slug": sheet.slug,
        "kind": sheet.kind,
        "kind_label": KIND_LABELS.get(sheet.kind, sheet.kind.title()),
        "weeks": sheet.weeks,
        "audience": sheet.audience,
        "language": sheet.language,
        "orientation": sheet.orientation,
        "pages": sheet.pages,
        "body_html": sheet.body_html,
    }


def render_html_for(sheet, env):
    return env.get_template("template.html.j2").render(**sheet_to_context(sheet))


FOOTER_STYLE = (
    "font-family:'Source Sans 3',Arial,sans-serif;font-size:7.5pt;color:#8a95a1;"
    "width:100%;margin:0 0.55in;padding-top:4pt;border-top:0.5pt solid #c8d0d7;"
    "display:flex;justify-content:space-between;align-items:baseline;"
    "-webkit-print-color-adjust:exact;"
)


def footer_template(sheet):
    return (
        '<div style="%s">'
        '<span style="letter-spacing:0.02em;">%s</span>'
        '<span style="letter-spacing:0.06em;text-transform:uppercase;">'
        'Irving ISD CCE &middot; Page <span class="pageNumber"></span>'
        ' of <span class="totalPages"></span></span>'
        "</div>"
    ) % (FOOTER_STYLE, html_mod.escape(sheet.title))


HEADER_TEMPLATE = '<div style="display:none"></div>'

MARGINS = {"top": "0.5in", "right": "0.55in", "bottom": "0.62in", "left": "0.55in"}


async def render_pdfs(sheets, out_dir, html_only=False, quiet=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    env = build_jinja_env()
    results = []

    if html_only:
        for s in sheets:
            path = TEMPLATE_DIR / ("_preview-%s.html" % s.slug)
            path.write_text(render_html_for(s, env), encoding="utf-8")
            results.append((s, path))
        return results

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        for s in sheets:
            RENDER_TMP.write_text(render_html_for(s, env), encoding="utf-8")
            await page.goto("file://%s" % RENDER_TMP)
            await page.wait_for_load_state("networkidle")
            try:
                await page.evaluate("document.fonts.ready")
            except Exception:
                pass
            out = out_dir / ("%s.pdf" % s.slug)
            await page.pdf(
                path=str(out),
                format="Letter",
                landscape=(s.orientation == "landscape"),
                print_background=True,
                display_header_footer=True,
                header_template=HEADER_TEMPLATE,
                footer_template=footer_template(s),
                margin=MARGINS,
            )
            s.rendered_pages = pdf_page_count(out)
            if s.rendered_pages and s.rendered_pages > s.pages:
                s.warn("rendered %d pages but front matter declares pages: %d"
                       % (s.rendered_pages, s.pages))
            if not quiet:
                pages = s.rendered_pages if s.rendered_pages else "?"
                print("  %-46s %s  %s p" % (out.name, s.orientation[:4], pages))
            results.append((s, out))
        await context.close()
        await browser.close()

    if RENDER_TMP.exists():
        RENDER_TMP.unlink()

    return results


PDFINFO_PAGES = re.compile(r"^Pages:\s+(\d+)", re.M)
PDF_PAGE_OBJ = re.compile(rb"/Type\s*/Page[^s]")


def pdf_page_count(path):
    """Page count via pdfinfo, falling back to a byte scan."""
    try:
        proc = subprocess.run(
            ["pdfinfo", str(path)],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        m = PDFINFO_PAGES.search(proc.stdout.decode("utf-8", "replace"))
        if m:
            return int(m.group(1))
    except (OSError, ValueError):
        pass
    try:
        n = len(PDF_PAGE_OBJ.findall(path.read_bytes()))
        return n or None
    except OSError:
        return None


# ---------- Driver ----------

def _rel(path):
    """Repo-relative display path, tolerant of paths outside the repo."""
    try:
        return str(Path(path).relative_to(ROOT))
    except ValueError:
        return str(path)


def collect_sources(globs, include_fixtures):
    if globs:
        paths = []
        for g in globs:
            gp = Path(g)
            if gp.is_absolute():
                paths.extend(Path("/").glob(g.lstrip("/")) if any(c in g for c in "*?[") else [gp])
            else:
                paths.extend(ROOT.glob(g) if any(c in g for c in "*?[") else [ROOT / g])
        paths = [p for p in paths if p.suffix == ".md" and p.is_file()]
    elif include_fixtures:
        # --fixtures is a test run: the fixture suite only, never mixed with
        # real sheets, so fixture output can't leak into docs/.
        paths = list(SRC_DIR.glob("%s/*.md" % FIXTURE_TOKEN))
    else:
        paths = list(SRC_DIR.glob("*.md"))

    keep = []
    for p in sorted(set(paths)):
        if FIXTURE_TOKEN in p.parts and not include_fixtures:
            continue
        if p.name.startswith("_") and FIXTURE_TOKEN not in p.parts:
            continue
        keep.append(p)
    return keep


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", help="Optional source-file paths or globs")
    parser.add_argument("--fixtures", action="store_true",
                        help="Render the fixture suite only "
                             "(build/worksheet_sources/_fixtures/*.md -> build/_fixture_out/)")
    parser.add_argument("--out-dir", default=None, help="Override the output directory")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate only")
    parser.add_argument("--html-only", action="store_true",
                        help="Write _preview-<slug>.html into build/worksheet_template/")
    parser.add_argument("--clean", action="store_true", help="Delete existing output first")
    parser.add_argument("--strict", action="store_true", help="Exit 2 if any sheet warns")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-sheet logging")
    args = parser.parse_args(argv)

    files = collect_sources(args.paths, args.fixtures)
    if not files:
        where = _rel(SRC_DIR)
        print("No worksheet sources matched (looked in %s)." % where, file=sys.stderr)
        return 1

    sheets = []
    seen = {}
    for p in files:
        s = parse_source(p)
        if s.slug in seen:
            print("ERROR duplicate slug %r: %s and %s (second one skipped)"
                  % (s.slug, _rel(seen[s.slug]), _rel(p)),
                  file=sys.stderr)
            continue
        seen[s.slug] = p
        sheets.append(s)

    if args.out_dir:
        out_dir = Path(args.out_dir)
        if not out_dir.is_absolute():
            out_dir = ROOT / out_dir
    elif args.fixtures and not args.paths:
        out_dir = FIXTURE_OUT_DIR
    elif any(s.is_fixture for s in sheets):
        out_dir = FIXTURE_OUT_DIR
    else:
        out_dir = OUT_DIR

    if not args.quiet:
        print("Parsed %d worksheet source(s) -> %s" % (len(sheets), _rel(out_dir)))

    if args.clean and out_dir.exists():
        for f in list(out_dir.glob("*.pdf")) + list(out_dir.glob("*.html")):
            f.unlink()

    if not args.dry_run:
        asyncio.run(render_pdfs(sheets, out_dir, html_only=args.html_only, quiet=args.quiet))

    warned = [s for s in sheets if s.warnings]
    if warned:
        print("\nWarnings:")
        for s in warned:
            print("  %s" % _rel(s.path))
            for w in s.warnings:
                print("    - %s" % w)

    if not args.quiet:
        print("\n%d sheet(s), %d with warnings." % (len(sheets), len(warned)))

    if args.strict and warned:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
