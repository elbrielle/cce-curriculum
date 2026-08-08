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

## Later audit queue

- Sample image-heavy pages from the first six weeks in signed-in Canvas.
- Record the largest delivery files and the pages students report as slow.
- Prioritize repeated images, files above roughly 500 KB, and full-page screenshots displayed below half their native width.
- Compare an optimized copy with the existing Canvas file before replacing anything.
