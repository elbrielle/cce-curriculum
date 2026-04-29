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

The CSS and logo come from the design team. Three rounds have shipped:

- **Round 1** (`PDF Template for CCE Exit Tickets.zip`) — four canonical formats: MCQ, Comparison Matrix, Venn, Short Constructed Response.
- **Round 2** (`PDF Template for CCE Exit Tickets (1).zip`) — six canonical formats: Concept Map, Decision Tree, Ranked Justification, Mini-Case, Trade-off, 3-2-1 Reflective.
- **Round 3** — six variants of Round 1/2 formats: Multi-Question MCQ (F01b), Seven-Bubble Concept Map (F04b), Routed Decision Tree (F05b), Procedural Decision Tree (F05c), Prose-Follow-up Ranked (F06b), Feedback Sandwich (F07b). Delivered as `exit-tickets-round3.css` (append-only, loaded after Round 1 + 2). The design agent's session ran out before three of the six HTML mockups (F05c, F06b, F07b) were drawn; those Jinja branches were authored from the CSS class hierarchy alone and verified visually.

To incorporate a future design refresh, drop the new CSS and any new assets into `build/exit_ticket_template/` and re-run `build_pdfs.py`. Do not hand-edit the CSS — keep it as the design source of truth so future refreshes overwrite cleanly.

## Status — what is structured vs fallback

**173 of 173 tickets (100%) render with a per-format structured component.** 167 fire one of the canonical Round 1/2 layouts; 6 fire one of the Round 3 variants. Zero tickets fall back to markdown rendering.

| Format | Status | Notes |
|---|---|---|
| Diagnostic MCQ (F01) | **Structured** (4 of 5) | Parses A/B/C/D options, scenario, stem, callout. The single fallback at `6sw/wk4/day2` is a multi-question quiz with three separate stems, not a single Diagnostic MCQ. |
| Comparison Matrix (F02) | **Structured** (29 of 29) | Detects a markdown table inside the payload, parses headers and row labels, renders the navy/gold matrix layout. |
| Venn Diagram (F03) | **Structured** (6 of 6) | The structured render now fires from any of four detection patterns: title "X vs Y" / "X or Y", body "Unique to <NAME>" twice, two bold ALL-CAPS labels close together (iceberg metaphors), or paired "My <X> career: ___" fill-ins. |
| Concept Map (F04) | **Structured** (31 of 32) | Two pattern variants are supported: canonical `**N. Label**` numbered sections, and the "Place **X** in the center" variant where the center is a named concept and items are plain `1. label: ____` numbered bullets. The single fallback at `6sw/wk5/day1` uses 7 step bubbles around the center, which doesn't fit the 3-4-node grid. |
| Decision Tree (F05) | **Structured** (12 of 14) | Detects `Step N:` linear prompts with optional `I need to talk to / Because` two-column branch. Two variants fall back: 6sw/wk5/day3 and 6sw/wk4/day4 use `**Step N:**` with YES/NO bullet branches and apply-the-tree follow-up sections — a different shape from the design template. |
| Ranked Justification (F06) | **Structured** (22 of 23) | Two modes are supported: canonical (pre-filled items + writeable rank) and inverse (pre-filled rank + writeable item label). The single fallback at `6sw/wk6/day3` is canonical mode but its follow-up rows use prose ("For the Rank 1 criterion...") instead of the bullet `Rank N:` form the parser keys on. |
| Mini-Case (F07) | **Structured** (27 of 28) | Detects `Scenario:` block + numbered questions with optional "Step 1 / Step 2" sub-bullet pairs. The single fallback at `2sw/wk5/day2` is a "feedback sandwich" with three labeled writing slots, not numbered questions. |
| Trade-off (F08) | **Structured** (7 of 7) | Detects bold `(A)` / `(B)` options + Pros A/B + My choice + Quality list + justification. Handles both label-inside-bold and label-outside-bold markdown shapes. |
| Short Constructed Response (F09) | **Structured** (24 of 24) | Numbered prompts at the top, single 9-line ruled writing area below. |
| 3-2-1 Reflective (F10) | **Structured** (5 of 5) | Detects bold sections opening with the numerals 3 / 2 / 1, with N gold-tinted writing slots per column. Handles both `**3 things ...**` and `**3** things ...` markdown shapes. |

### The 6 Round 3 variants

These tickets render with their own per-variant structured component. The variant detector runs before the canonical extractor for the same parent format, so a ticket that fits both shapes prefers the variant.

| Ticket | Variant code | Variant name | Parent |
|---|---|---|---|
| `6sw/wk4-sales-presentations/day2.md` | F01b | Multi-Question Diagnostic MCQ | F01 |
| `6sw/wk5-job-skills-mock-interview/day1.md` | F04b | Seven-Bubble Ordered Concept Map | F04 |
| `6sw/wk4-sales-presentations/day4.md` | F05b | Routed Decision Tree | F05 |
| `6sw/wk5-job-skills-mock-interview/day3.md` | F05c | Procedural Decision Tree | F05 |
| `6sw/wk6-capstone/day3.md` | F06b | Prose-Follow-up Ranked | F06 |
| `2sw/wk5-powerskills-communication/day2.md` | F07b | Feedback Sandwich | F07 |

The page-id footer carries the variant suffix (e.g., `2SW-Wk5-Day2 · F07b`). The format-number strip in the body header keeps the parent's number (`07 / 10`) since the format-name strip and glyph already differentiate the variant.

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

1. **Round 3 visual polish.** The design agent's session ran out before three Round 3 mockups (F05c Procedural Tree, F06b Prose-Follow-up Ranked, F07b Feedback Sandwich) were drawn. The Jinja branches for those three were authored from the CSS class hierarchy and rendered correctly, but the design team has not visually approved them. A polish pass should review the rendered PDFs against the CSS contract and tweak any layout choices that diverge from intent.
2. **Round 3 README + screenshots.** The Round 3 design bundle never shipped a `README.md` or `screenshots/*.png` because of the same usage cap. The CSS itself is well-commented and `build/exit_ticket_template/round3-mockups.html` carries the 3 mockups that did ship. A README pass would document the variant-suffix scheme and the Round 3 data-model fields.
3. **Two-up half-page sheet PDF** so a teacher prints one Letter page with two half-page tickets side-by-side. Requires a separate "two-up combiner" pass that pairs MCQ / Mini-Case / Short / 3-2-1 tickets after generation.
4. **Incremental rebuild** keyed on day-file mtime + SHA, if generation time becomes a concern. ~5 min for the full 173-ticket run today.
5. **Static visual regression** snapshot folder so a future agent can diff a representative ticket per format against a checked-in baseline PNG before committing pipeline changes.
6. **F09 = Compare-Contrast frame** if the design team wants to add an eleventh format. The Round 2 README mentioned this as a future possibility. F09 in production is Short Constructed Response; a Compare-Contrast addition should take a new number (F11+).
