# Exit-Ticket PDF Pipeline

Built 2026-04-28 on branch `worksheet-pdf-pipeline`. This page is the operating manual for the markdown-to-PDF pipeline that produces a printable student worksheet for every daily exit ticket in `docs/`.

## What it does

For every `docs/Nsw/wkN-topic/dayN.md` file with an `**EXIT TICKET**` marker:

1. Parses the day file to extract the H1 title, the format name in parentheses, the payload body, and the trailing TEKS chip.
2. Renders an HTML page using the Irving ISD-branded template at `build/exit_ticket_template/template.html.j2` + `exit-tickets.css`.
3. Prints the page to PDF with Playwright headless Chromium.
4. Writes the PDF to `docs/resources/exit-tickets/<Nsw>-wk<N>-day<N>-<slug>.pdf`.

A separate pass (`build/inject_pdf_links.py`) updates each day file so the `**EXIT TICKET** (Format Name):` line carries a `· [Printable PDF](...)` link to its generated PDF. This is what students and teachers click from the MkDocs site.

## How to regenerate everything

```bash
cd "/Users/elishalucero/Coding Projects/27 CCR Planning"

# 1. (one-time machine setup) install dependencies
python3 -m pip install --user playwright jinja2 markdown
python3 -m playwright install chromium

# 2. regenerate all 173 PDFs (~5 min)
python3 build/build_pdfs.py

# 3. refresh the [Printable PDF] links in every day file
python3 build/inject_pdf_links.py
```

Both scripts are idempotent. Re-running on an unchanged repo writes the same bytes and produces no diff.

## How to add a new exit ticket

1. Write the ticket inside the `## Exit Ticket` section of the relevant `dayN.md` file using the standard `**EXIT TICKET** (Format Name):` marker, following `cce-curriculum/notes/exit-ticket-templates.md` for format choice.
2. End the payload with the trailing TEKS chip in the existing convention: `*(d(x)(y), d(x)(z))*`.
3. From the project root: `python3 build/build_pdfs.py docs/<path/to/dayN.md>` to render only that ticket, then `python3 build/inject_pdf_links.py docs/<path/to/dayN.md>` to add the link.
4. Run the full preservation loop in `PLANNING.md` §9 before committing.

The pipeline does not validate ticket content. ESL reading level, DOK level, and TEKS alignment remain the author's responsibility (see `cce-curriculum/notes/teks-audit-process.md` and `cce-curriculum/notes/exit-ticket-templates.md`).

## How to add a new day file

If the file has a non-standard H1 (anything other than `# Day N: <Title>`), the parser will skip it. Standard form is required. The `<Title>` becomes both the printed subtitle and the slug used in the PDF filename (lowercased, ampersand-to-"and", non-alphanumerics collapsed to hyphens).

## What's in the bundle

```
build/
├── build_pdfs.py                  # main parser + renderer
├── inject_pdf_links.py            # updates [Printable PDF] links in day files
└── exit_ticket_template/
    ├── template.html.j2           # Jinja2 template (header/body/footer chrome)
    ├── exit-tickets.css           # stylesheet from the design bundle (do not edit; replace)
    └── assets/
        └── iisd-logo.png          # Irving ISD logo, color, transparent
```

The CSS and logo come from the design team's handoff bundle (`PDF Template for CCE Exit Tickets.zip`). To incorporate a design refresh, drop the new `exit-tickets.css` and any new assets into `build/exit_ticket_template/` and re-run `build_pdfs.py`. Do not hand-edit the CSS — keep it as the design source of truth so future refreshes overwrite cleanly.

## v1 status — what is structured vs fallback

The design bundle ships finished layouts for **four of ten** formats. The pipeline renders those four with structured per-format components and renders the other six as a "preserved markdown" fallback inside the same chrome.

| Format | Status | Notes |
|---|---|---|
| Diagnostic MCQ | **Structured** | Parses A/B/C/D options, scenario, stem, callout. Pixel-matches the design when the markdown follows the standard `- A. text` / `- B. text` form. |
| Comparison Matrix | **Structured** | Detects a markdown table inside the payload, parses headers and row labels, renders the navy/gold matrix layout. Falls back to preserved-markdown if no table is present. |
| Venn Diagram | **Structured (narrow)** | Renders the two-circle SVG only when the day's H1 (or the first 300 chars of the payload) names a clear "X vs Y" or "X or Y" pair. Otherwise falls back. Most current Venn tickets in the corpus use a "Unique to A / Unique to B / Both" prose form, which renders fine via fallback; the SVG render fires on the rare title-named pair. |
| Short Constructed Response | **Structured** | Numbered prompts at the top, single 9-line ruled writing area below. |
| Concept Map | **Fallback** | Design layout TODO. |
| Decision Tree | **Fallback** | Design layout TODO. |
| Ranked Justification | **Fallback** | Design layout TODO. |
| Mini-Case | **Fallback** | Design layout TODO. |
| Trade-off | **Fallback** | Design layout TODO. |
| 3-2-1 Reflective | **Fallback** | Design layout TODO. |

In all six fallback formats the chrome is identical to the structured ones (header, format-name strip with glyph, mastery rubric footer, page-id footer). Only the body region differs: the markdown is rendered to HTML with light pre-processing (long underscore runs become `<span class="blank">` writing lines) so the student-facing prompts stay legible and printable.

The six fallback glyphs in `build/build_pdfs.py` (under `GLYPHS`) are quick line-icon placeholders. Replace them with the design team's official glyphs when those ship.

## What changes when the design team finishes a format

To upgrade a format from "fallback" to "structured":

1. Add a new branch to `template.html.j2` next to the existing `{% elif format_id == "matrix" %}` block.
2. Add a per-format extractor function in `build_pdfs.py` next to `extract_mcq` / `extract_matrix` / `extract_venn`. It should return `{}` if the markdown can't support the structured render (the renderer falls back automatically when an extractor returns empty).
3. Wire the extractor into `ticket_to_context()`.
4. Replace the placeholder glyph in `GLYPHS` with the design team's official SVG.
5. Re-run `python3 build/build_pdfs.py` and spot-check.

## Implementation decisions worth knowing

- **HTML-to-PDF renderer choice: Playwright headless Chromium.** WeasyPrint cannot reliably render the gradient-painted ruled writing lines (`linear-gradient` + `background-size: 100% calc(100% / N)`) used throughout the design CSS. Chromium handles them perfectly and survives the print-color-adjust toggling required for the gold answer-region tint.

- **Slug derivation.** The PDF filename uses `<Nsw>-wk<N>-day<N>-<slug>.pdf` where `<slug>` is the H1 title minus the `Day N: ` prefix, lowercased, ampersands replaced with "and", non-alphanumerics collapsed to hyphens. This means renaming a day file's H1 will produce a new PDF filename. The link-injection pass picks up the new filename automatically; the orphaned old PDF should be deleted manually (or via `python3 build/build_pdfs.py` with a clean `OUT_DIR`).

- **Link injection is idempotent and safe to re-run.** It only touches the single `**EXIT TICKET** (Format):` line per day file. If the line already has a `· [Printable PDF](...)` link, it is replaced with the canonical computed path. If not, it is inserted between the closing `)` and the trailing `:`. Nothing else in the day file is touched.

- **TEKS chip extraction.** The trailing `*(d(x)(y), ...)*` chip in the markdown is parsed for the chip rendering in the header, then stripped from the payload before rendering. If a single payload contains multiple chips (uncommon), the last one wins.

- **Fallback markdown rendering.** Uses `python-markdown` with `extra`, `tables`, and `sane_lists` extensions. Long underscore runs (`_____+`) are pre-processed into `<span class="blank">` spans so they render as proper writing lines instead of underscore characters.

- **Skipped files.** Seven day files do not have an `**EXIT TICKET**` marker and are skipped by the generator: the five `1sw/wk0-classroom-routines/` files (Wk0 was intentionally not included in the pilot), plus `1sw/wk3-computer-science-it/day3.md` and `1sw/wk5-cybersecurity-it/day5.md` (pre-existing gaps from the pilot pass that are content questions, not pipeline questions).

## Known limitations

- **Venn structured render is narrow.** Only fires when the H1 or early payload literally contains "X vs Y" / "X or Y" with both items under 30 characters. Most Venn tickets in the corpus take the "Unique to A / Unique to B / Both" prose form and render correctly via fallback, but a future content author who wants a structured Venn must title or open the payload accordingly.

- **Comparison Matrix structured render needs a markdown table.** If a Matrix ticket lacks a `| ... |` table block, the renderer falls back. Authors who want the styled navy-header matrix should write a real markdown table.

- **Half-page sheet sizing.** MCQ, Short Response, and 3-2-1 use the `.sheet--half` (5.5in min) sizing in CSS, but the PDF page is always Letter, so a half-page ticket prints with whitespace below. For real classroom use, two half-page tickets can be printed two-up via a manual print-step `Multiple` setting; that is outside the scope of this pipeline.

- **No incremental rebuild.** Every run regenerates every PDF. With ~173 tickets at ~2 sec each, a full run is ~5 min. If incremental builds are needed later, key on the SHA of the day file's text.

- **Google Fonts dependency.** The CSS imports Space Grotesk, Source Sans 3, and JetBrains Mono from Google Fonts. Generation requires network access. If offline or air-gapped rendering is needed, ship the fonts locally and update the `@import` line in the CSS.

## Files this pipeline writes outside `build/`

Only one location: `docs/resources/exit-tickets/*.pdf`. The link-injection pass also edits `docs/Nsw/wkN-topic/dayN.md` files in place to add or refresh the printable-PDF link on the `**EXIT TICKET**` line.

## Future work (not blocking, in priority order)

1. **Design layouts for the six fallback formats.** Concept Map, Decision Tree, Ranked Justification, Mini-Case, Trade-off, 3-2-1. The CSS bundle already carries placeholder selectors (`.cmap`, `.tree`, `.rank`, `.tradeoff`, `.tto`) — replace those with finished components and wire structured branches into the template per the upgrade procedure above.
2. **Replace the six placeholder glyphs** in `build/build_pdfs.py` `GLYPHS` once the design team ships the finished line-icon set.
3. **Two-up half-page sheet PDF** so a teacher prints one Letter page with two half-page tickets side-by-side. Requires a separate "two-up combiner" pass that pairs MCQ/Short/3-2-1 tickets after generation.
4. **Incremental rebuild** keyed on day-file mtime + SHA, if generation time becomes a concern.
5. **Static visual regression** snapshot folder so a future agent can diff a representative ticket per format against a checked-in baseline PNG before committing pipeline changes.
