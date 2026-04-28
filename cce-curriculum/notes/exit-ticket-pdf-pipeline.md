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

The CSS and logo come from the design team. Round 1 (`PDF Template for CCE Exit Tickets.zip`) shipped four format layouts; Round 2 (`PDF Template for CCE Exit Tickets (1).zip`) added six more, delivered as `exit-tickets-round2.css` (append-only, loaded after the Round 1 stylesheet). To incorporate a future design refresh, drop the new CSS and any new assets into `build/exit_ticket_template/` and re-run `build_pdfs.py`. Do not hand-edit the CSS — keep it as the design source of truth so future refreshes overwrite cleanly.

## Status — what is structured vs fallback

All ten formats now have finished design layouts. **154 of 173 tickets (89%)** render with the per-format structured component; the other 19 hit the fallback because their markdown is in a variant shape that does not fit the corresponding design template's data model. Fallback tickets still use the same chrome and gold-tinted writing language so they read as part of the same printable family.

| Format | Status | Notes |
|---|---|---|
| Diagnostic MCQ (F01) | **Structured** (4 of 5) | Parses A/B/C/D options, scenario, stem, callout. The single fallback at `6sw/wk4/day2` is a multi-question quiz, not a single Diagnostic MCQ. |
| Comparison Matrix (F02) | **Structured** (29 of 29) | Detects a markdown table inside the payload, parses headers and row labels, renders the navy/gold matrix layout. |
| Venn Diagram (F03) | **Fallback** (0 of 6) | Structured render exists but only fires when the H1 or early payload literally contains "X vs Y" / "X or Y" with both items under 30 characters. No Venn ticket in the current corpus matches; all six render via the markdown fallback (which carries the "Unique to A / Unique to B / Both" prose shape that authors actually use). |
| Concept Map (F04) | **Structured** (29 of 32) | Detects `**N. Label**` numbered sections with a center prompt and per-node descriptor, slot, and "why" prompt. Three variant tickets fall back: 6sw/wk6/day4 ("Place X in the center" instruction with non-bold numbered items), 6sw/wk3/day5 and 6sw/wk5/day1 (similar shape variations). |
| Decision Tree (F05) | **Structured** (12 of 14) | Detects `Step N:` linear prompts with optional `I need to talk to / Because` two-column branch. Two variants fall back: 6sw/wk5/day3 and 6sw/wk4/day4 use `**Step N:**` with YES/NO bullet branches and apply-the-tree follow-up sections — a different shape from the design template. |
| Ranked Justification (F06) | **Structured** (17 of 23) | Detects bullet-list of pre-filled items + follow-up rows. Six variants fall back: tickets where students fill in BOTH the rank AND the item (4sw/wk1/day4, 4sw/wk4/day2, 4sw/wk6/day2, 5sw/wk3/day4, 6sw/wk6/day3) and 2sw/wk1/day2 which uses a cluster-rank pattern. The design template assumes pre-filled items + writeable ranks; the inverse pattern doesn't fit. |
| Mini-Case (F07) | **Structured** (27 of 28) | Detects `Scenario:` block + numbered questions with optional "Step 1 / Step 2" sub-bullet pairs. The single fallback at `2sw/wk5/day2` is a "feedback sandwich" with three labeled writing slots, not numbered questions. |
| Trade-off (F08) | **Structured** (7 of 7) | Detects bold `(A)` / `(B)` options + Pros A/B + My choice + Quality list + justification. Handles both label-inside-bold and label-outside-bold markdown shapes. |
| Short Constructed Response (F09) | **Structured** (24 of 24) | Numbered prompts at the top, single 9-line ruled writing area below. |
| 3-2-1 Reflective (F10) | **Structured** (5 of 5) | Detects bold sections opening with the numerals 3 / 2 / 1, with N gold-tinted writing slots per column. Handles both `**3 things ...**` and `**3** things ...` markdown shapes. |

The fallback glyphs that shipped pre-Round-2 have been replaced with the design team's Round 2 line-icons in `build/build_pdfs.py` `GLYPHS`. All ten glyphs are now design-authored.

### F09 numbering note

The Round 2 README mentions "F09 is reserved for a future Compare-Contrast frame and is not in this round." In production F09 has been Short Constructed Response since Round 1, so the numbering is currently consistent with what shipped. If the design team wants to introduce a Compare-Contrast frame, it can take any unused number (F11+); the field-pair `format_code` in `build/build_pdfs.py` is the source of truth for production.

## What changes when a format needs a structural update

To extend a structured format (e.g., Round 3 or a fix for a fallback variant):

1. Add or update the per-format extractor function in `build_pdfs.py` next to `extract_concept_map` / `extract_decision_tree` / etc. Return `{}` if the markdown can't support the structured render (the renderer falls back automatically when an extractor returns empty).
2. Update the corresponding `{% elif format_id == "..." %}` branch in `template.html.j2`.
3. If the design ships an updated CSS, replace `exit-tickets.css` and/or `exit-tickets-round2.css` in `build/exit_ticket_template/` and re-run `build_pdfs.py`.
4. Replace the glyph in `GLYPHS` if the design team ships a new icon.
5. Spot-check at least 5 representative tickets per format before committing.

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

1. **Variant-shape parsers for the 19 fallback tickets.** Today they render via the markdown fallback inside the same chrome — readable but not per-format-designed. A future pass could either author additional Jinja branches that handle the variant shapes (e.g., the inverse-Ranked pattern where students fill both rank and item; the YES/NO Decision-Tree variant) OR rewrite those source tickets to fit the canonical shape. Curriculum-content rewrites are out of scope for the pipeline; coordinate with the curriculum author before changing markdown.
2. **Venn coverage.** All 6 Venn tickets fall back today because the structured render requires an "X vs Y" pattern in the title or early payload. Authors who want a structured Venn must title or open the payload accordingly. An alternative would be a third extractor branch that detects the "Unique to A / Unique to B / Both" prose shape and pulls the two labels from the section headers.
3. **Two-up half-page sheet PDF** so a teacher prints one Letter page with two half-page tickets side-by-side. Requires a separate "two-up combiner" pass that pairs MCQ / Mini-Case / Short / 3-2-1 tickets after generation.
4. **Incremental rebuild** keyed on day-file mtime + SHA, if generation time becomes a concern. ~5 min for the full 173-ticket run today.
5. **Static visual regression** snapshot folder so a future agent can diff a representative ticket per format against a checked-in baseline PNG before committing pipeline changes.
6. **F09 = Compare-Contrast frame** if the design team wants to add an eleventh format. See the F09 numbering note above; do not renumber existing formats.
