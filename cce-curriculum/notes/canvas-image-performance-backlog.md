# Canvas Image Performance Backlog

Canvas image performance is a standing quality check, not a blanket compression project. Preserve the licensed source original in the local gitignored archive. Optimize only the Canvas delivery copy, and replace it only after the smaller file remains equally usable on desktop and at a 390-pixel viewport.

For each slow or unusually large image, record:

- Canvas file ID and page;
- source dimensions and byte size;
- displayed width and whether the image is reused;
- whether it contains instructional text or is primarily decorative;
- first-load and lazy-load behavior;
- smallest-text readability at desktop and 390-pixel widths; and
- optimized dimensions, byte size, and visual-QA result.

Prefer, in order:

1. a focused crop that removes unused page area;
2. a JPEG delivery copy for photographic or rendered workbook pages;
3. modest dimension reduction matched to the largest useful display size;
4. quality reduction only until the smallest instructional text begins to soften; and
5. removal when an image is decorative and adds no instructional value.

Do not batch-compress screenshots containing small directions, labels, charts, or interface controls. A fast image that students cannot read is not an optimization.

## Current observations

### 1SW local delivery baseline — first six weeks

- The local Canvas-only archive for 1SW Weeks 0-5 contains 71 raster delivery images totaling 35.1 MB. All 71 are PNG files.
- Thirty-three files exceed 500 KB and account for 26.0 MB of the total. The largest is the Week 1 Day 1 manufacturing opener at 1,564,791 bytes; 13 files are approximately 1 MB or larger.
- Fifty-four images are full workbook-page dimensions (1,275 by 1,650 pixels), 15 are slide dimensions (1,600 by 900), and two are 1,241 by 1,754. This confirms that the likely delay is not one isolated file: several pages carry full-page PNGs at dimensions materially larger than their Canvas display width.
- Exact duplicate audit found seven copies of the IT app-exploration image, five copies of the same Irving program page 2 image, and four copies of the same Irving program page 1 image. Canvas should use one locked file per identical binary where practical instead of uploading another copy for each lesson.
- First pilot candidates are the Week 1 Day 1 manufacturing opener and the seven Week 5 Day 2 email slides. The opener tests a full text-bearing workbook page; the email set tests combined page weight, where seven individually readable images load together.
- Do not replace the local licensed originals. Create focused progressive-JPEG delivery candidates, compare the smallest text and phishing-domain details at desktop and 390-pixel widths, then replace only the authenticated Canvas delivery files that pass. Record before/after Canvas file IDs and cold-load behavior.

### 3SW Week 4 pilot

- The full-page Day 1 opener was reduced from 789,795 bytes to 338,898 bytes at 935 by 1,210 pixels.
- Desktop and 390-pixel checks retained useful readability.
- Detail-heavy workbook crops were left unchanged.

### 3SW Week 5 baseline

- Nine Canvas-only workbook images are 144,771-260,856 bytes each at 1,148 by 1,485 pixels.
- Canvas file IDs are 14561579-14561587.
- All images use native lazy loading and a 700-pixel maximum display width.
- Signed-in desktop and 390-pixel browser checks found no horizontal overflow.
- Progressive scrolling loaded the Day 1, Day 4, and Day 5 images at their point of use; the 390-pixel display width was about 344 pixels and the instructional text remained readable.
- No Week 5 replacement is warranted. Reassess only if real classroom use or a slower student connection shows a first-load delay.

### 3SW Week 6 baseline

- Five Canvas-only workbook images are 116-262 KB each. They are 1,020 pixels wide and display at a maximum of 700 pixels.
- Canvas file IDs are 14561639-14561643.
- Signed-in desktop and 390-pixel checks found no horizontal overflow. Small workbook directions remained readable at desktop width; the linked support packet supplies the independent text route on a phone.
- The source HTML includes `loading="lazy"`, but Canvas did not preserve that attribute in the signed-in rendered DOM during this check. Week 6 therefore controls first-load cost primarily through targeted page selection and small JPEG delivery files rather than assuming browser lazy loading.
- No Week 6 image exceeds 300 KB. No replacement is warranted unless classroom network testing shows a real delay.

### 4SW Week 1 baseline

- Seven focused workbook JPEGs are 92-193 KB each at 1,020 by 1,320 pixels and display at a maximum of 700 pixels.
- Canvas file IDs are 14561660-14561666. Day 2 carries the largest combined image weight at about 397 KB across three instructional pages.
- Signed-in desktop and 390-pixel checks found no horizontal overflow. The mobile display width is about 342 pixels, and the linked student packet provides the independent text and writing route.
- The Day 5 image remained unloaded above the fold and completed after the student scrolled into the lesson. Do not rely on that behavior alone; the small, focused JPEG remains the primary performance control.
- No Week 1 replacement is warranted. The first-six-weeks cold-load audit remains open because cached teacher review is not equivalent to a student's first visit on a constrained connection.

### 4SW Week 2 pre-upload baseline

- Five focused workbook JPEGs are 106-193 KB each at 1,105 by 1,430 pixels. Their combined delivery weight is about 706 KB across Days 2, 4, and 5; no student page uses more than two of them.
- The local originals remain unchanged in the gitignored licensed archive. These delivery copies were visually checked at original resolution and retain readable instructional text.
- Record the Canvas file IDs, actual first-load behavior, and 390-pixel readability after the unpublished module is imported. Do not compress these files further unless the signed-in browser check reveals a real delay.

### 4SW Week 3 pre-upload baseline

- Six Canvas-only JPEGs are 31-236 KB each. The combined delivery weight is about 966 KB across Days 1, 2, and 5; Day 1 is the heaviest page at about 645 KB across three workbook pages.
- The Irving aviation paragraph was cropped from the dense mixed-program page into a focused 31 KB image so the relevant text remains readable without loading the unrelated full page.
- The adjacent workbook page was rejected from Canvas because its simulator and automotive-IBC claims are not verified current aviation facts. Removing a misleading image is preferable to optimizing and embedding it.
- All remaining pages were rendered at 120 dpi with progressive JPEG delivery copies and visually checked in a contact sheet. The downloadable CCE packets provide the independent text route.
- Record Canvas file IDs, 390-pixel readability, and signed-in first-load behavior after import. If Day 1 is slow, test whether the cluster opener can remain teacher-only before reducing text-page quality.

### 4SW Week 4 pre-upload baseline

- Two licensed workbook delivery images are 170 KB and 200 KB. Each appears on only one student page, and no Week 4 student page carries more than one licensed image.
- Both are progressive JPEG copies rendered at 120 dpi. The original licensed PDF remains unchanged in the gitignored archive.
- Day 1 uses only the page containing the Protecting Wildlife user need and requirements; the downloadable design packet supplies the independent text and response route.
- Day 5 uses the workbook program-context page. Current Irving program facts are linked separately so the image is not treated as the current source of record.
- Record Canvas file IDs, 390-pixel readability, and signed-in first-load behavior after import. Do not lower quality unless the smallest requirement or program text remains readable after comparison.

### 4SW Week 5 pre-upload baseline

- The revised week uses one licensed workbook image: the Crash Crew vehicle-view page at 195 KB and 1,020 by 1,320 pixels.
- The file is a progressive JPEG delivery copy rendered at 120 dpi. The licensed PDF remains unchanged in the local archive.
- Workbook report and repair-plan pages are not duplicated as images because the accessible CCE packet supplies the same response jobs with clearer evidence boundaries and writing space.
- The workbook district page was intentionally not embedded. Its program and event statements require current district confirmation, and a visual warning would not make it the right source of record.
- Record the Canvas file ID and 390-pixel evidence visibility after import. The combined licensed-image weight on every other Week 5 student page is zero.

### 4SW Week 6 pre-upload baseline

- Three licensed FYF Analytical Reasoning pages are 143-195 KB each at 1,020 by 1,320 pixels. Combined Day 1 image weight is about 508 KB; Days 2-5 use no licensed raster images.
- All three are progressive-JPEG delivery copies rendered at 120 dpi. The original licensed PDF remains unchanged in the local archive.
- The clue-set page preserves the four short clue groups clearly at original resolution. The downloadable CCE packet repeats every required clue and supplies the independent text and response route.
- Record Canvas file IDs, 390-pixel text readability, and signed-in first-load behavior after import. If the three-image page is slow, test keeping the tool-introduction page teacher-only before reducing clue text quality.

### 5SW Week 1 pre-upload baseline

- Seven locked delivery images are prepared: six FYF pages at 113-266 KB and one city-goals slide at about 234 KB.
- The source Climber Notes slide renders sideways from the original PPTX; the delivery copy is rotated upright and visually verified. The licensed original remains unchanged.
- Day 1 loads three targeted pages; Day 5 loads the city-goals visual plus three workbook pages. Days 2-4 use native Canvas text and downloadable packets rather than additional screenshots.
- After import, test the city-goals type and Safety Supervisor directions at 390 pixels. Keep downloadable text routes available if the smallest labels are not comfortable to read.

### 5SW Week 2 pre-upload baseline

- Five focused FYF delivery images are 102-240 KB each at 1,020 pixels wide. Day 1 is the heaviest page at about 672 KB across three images; Day 5 is about 315 KB across two images.
- All are progressive JPEG copies rendered at 120 dpi. The original licensed workbook PDF remains unchanged in the local archive.
- The contact-sheet inspection confirms that the kitchen layout, cabinet grid, Mars constraints, and rover directions remain readable at source resolution. The downloadable CCE packets provide the independent text, evidence, and writing route.
- After import, test Day 1 at a 390-pixel viewport and on a cold signed-in load. If it is slow, test whether the decorative Engineering opener can remain teacher-only before reducing the detail-heavy systems pages.

### 5SW Week 3 pre-upload baseline

- Six locked JPEG delivery images are prepared for Day 4: five source photos from the licensed Climber Notes deck at 144-340 KB and one focused FYF thermal-comparison page at about 155 KB. Combined Day 4 image weight is about 1.47 MB.
- The five deck images use the original embedded photos rather than rendered slides with empty Notes boxes. They are capped at 1,400 pixels on the long edge and were visually inspected after conversion. The original deck remains unchanged.
- The thermal page is a 1,020-by-1,320 progressive JPEG rendered at 120 dpi. The expanded CCE observation log supplies the independent text and response route, so the workbook page is not the only way to complete the lesson.
- After import, test progressive scrolling and image detail at a 390-pixel viewport. Because all six visuals appear on one student page, measure the combined cold-load behavior even though no individual file exceeds 350 KB. If the page is slow, test native Canvas disclosures that reveal one image at a time before lowering evidence quality.

### 5SW Week 4 pre-upload baseline

- Eight locked JPEG delivery images are prepared. Day 2 uses four wide Climber ticket images at 124-187 KB plus two 1,020-by-1,320 FYF pages at 163-223 KB; combined Day 2 weight is about 1.04 MB. Day 5 uses two 1,020-by-1,320 FYF pages totaling about 380 KB.
- The four ticket images retain the supplied location, complaint, extra information, and equipment photo at 1,400 pixels wide. The downloadable six-page CCE packet supplies the independent text and response route.
- FYF p.186 is useful as a source example but uses stronger diagnosis/action language than the revised lesson. It is embedded only with an adjacent correction; the CCE note form is the scoring source.
- After import, test the four ticket photos and smallest ticket text at a 390-pixel viewport and on a cold signed-in load. If Day 2 is slow, test placing each ticket in a native disclosure before reducing the evidence-image quality.
- Record Canvas file IDs and actual first-load behavior. Keep the licensed originals unchanged in the local gitignored archive.

### 5SW Week 5 pre-upload baseline

- Two existing FYF Rung 3 reminder images are reused: 105 KB and 172 KB. Both appear only on Day 1, for a combined raster weight of about 277 KB.
- The images remain in the gitignored Canvas-licensed archive and the original workbook is unchanged. They are optional reminders; every required salary label, lifestyle prompt, and writing field also appears in the accessible CCE packet and native Canvas text.
- The page explicitly warns that the workbook's broad salary fields are not current evidence. Students use the exact Xello occupation/geography/date/measure label or the fixed BLS fallback rather than inferring a value from the image.
- After import, verify Day 1 readability and cold-load behavior at a 390-pixel viewport. The current file sizes do not justify further compression unless signed-in Canvas testing shows a real delay or unreadable small text.

### 5SW Week 6 pre-upload baseline

- Three locked FYF *Flip This House* pages are 130 KB, 152 KB, and 240 KB, for a combined Day 3 raster weight of about 522 KB. Days 1, 2, 4, and 5 use no licensed raster images.
- The pages are progressive JPEG delivery copies at 120 dpi and remain readable at source resolution. The original licensed workbook is unchanged.
- Every buyer preference, upgrade cost, estimated value increase, formula, boundary, and response job also appears in native Canvas text or the expanded accessible CCE packet. The images are not the only completion route.
- After import, test Day 3 at 390 pixels and on a cold signed-in load. If the page is slow, keep p. 240 optional/teacher-only before reducing the quality of the decision table on p. 239.

### 6SW Week 1 pre-upload baseline

- Eight locked FYF pages are prepared at 152-278 KB each with a 1,300-pixel long edge. Day 1 uses three pages (about 758 KB), Day 4 uses two (about 424 KB), and Day 5 uses three (about 522 KB).
- The 1,600-pixel first pass was reduced after original-resolution inspection confirmed that a 1,300-pixel, quality-65 delivery copy kept the smallest instructional text readable. The licensed source PDF remains unchanged.
- Every requirement, evidence boundary, and response job appears in native Canvas text or the accessible CCE packet; the images are not the sole completion route.
- After import, test Days 1 and 5 at a 390-pixel viewport and on a cold signed-in load. If Day 1 is slow, keep the decorative cluster opener teacher-only before reducing the detail-bearing Community Classroom pages.

### 6SW Week 2 pre-upload baseline

- Eight locked FYF pages are 137-307 KB each at a 1,300-pixel long edge. Day 1 carries about 810 KB across three images, Day 3 about 437 KB across two, and Day 5 about 588 KB across three.
- The images preserve the podcast checklist, incomplete audio script, design-principle table, and sketch prompt. Native Canvas text and the CCE packets remain the independent route.
- After import, cold-load Days 1 and 5 at a 390-pixel viewport. If Day 1 is slow, test keeping the decorative Arts/AV opener teacher-only before reducing the checklist pages.

### 6SW Week 3 pre-upload baseline

- Eleven locked FYF delivery images are 111-300 KB each at a 1,300-pixel long edge. Day 1 is the heaviest page at about 1.15 MB across four images; Day 2 is about 408 KB, Day 3 about 624 KB, and Day 4 about 474 KB.
- The pages preserve the CTA table, Expert Edge planning prompts, Family Fun Pass tables, and focus-group quotes. The accessible CCE packets and native Canvas directions repeat all required evidence and response jobs.
- After import, cold-load Day 1 at a 390-pixel viewport and test progressive scrolling through all four images. If it is slow, make the printed ad-analysis page optional/teacher-only before lowering quality on the CTA reference or mock-up pages.

### 6SW Week 4 pre-upload baseline

- Nine locked FYF delivery images are 87-162 KB each at a 1,300-pixel long edge. Day 3 is the heaviest page at about 456 KB across four images; Day 1 is about 254 KB, Day 2 about 90 KB, and Day 5 about 241 KB.
- The reference PDF has six front-matter pages before the printed numbering. Delivery extraction used physical PDF index = printed page + 6, and visual checks confirmed printed pp. 241, 244, and 299 before recording the set.
- Native Canvas text and accessible CCE packets contain every required prompt and labor figure. After import, verify Day 3 at 390 pixels; current page weights do not justify further compression unless the signed-in cold-load check shows a real delay.

## Later audit queue

- User observation on 2026-08-08: several images in the first six weeks appeared to load slowly during signed-in Canvas review. Treat this as the first performance sample, even where individual files appear modest in size.
- Sample image-heavy pages from the first six weeks in signed-in Canvas on desktop and a 390-pixel viewport. Include at least one cold-load check on a constrained connection when practical; browser cache can hide the delay students experience on first visit.
- Record the largest delivery files and the pages students report as slow.
- Prioritize repeated images, files above roughly 500 KB, and full-page screenshots displayed below half their native width.
- Compare an optimized copy with the existing Canvas file before replacing anything.
- Record the combined image weight per page, not only each file size. Several individually reasonable images can still make one student page slow.
- Keep a text or downloadable-document route for any instructional image whose smallest labels cannot remain readable after optimization.
