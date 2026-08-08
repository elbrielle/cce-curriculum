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

## Later audit queue

- User observation on 2026-08-08: several images in the first six weeks appeared to load slowly during signed-in Canvas review. Treat this as the first performance sample, even where individual files appear modest in size.
- Sample image-heavy pages from the first six weeks in signed-in Canvas on desktop and a 390-pixel viewport. Include at least one cold-load check on a constrained connection when practical; browser cache can hide the delay students experience on first visit.
- Record the largest delivery files and the pages students report as slow.
- Prioritize repeated images, files above roughly 500 KB, and full-page screenshots displayed below half their native width.
- Compare an optimized copy with the existing Canvas file before replacing anything.
- Record the combined image weight per page, not only each file size. Several individually reasonable images can still make one student page slow.
- Keep a text or downloadable-document route for any instructional image whose smallest labels cannot remain readable after optimization.
