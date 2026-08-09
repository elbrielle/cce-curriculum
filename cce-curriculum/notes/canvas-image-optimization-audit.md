# Canvas Image Optimization Audit

**Audit date:** 2026-08-08

**Scope:** `cce-curriculum/resources/canvas-licensed` raster delivery assets

**Delivery rule:** licensed originals remain outside Git; Canvas importers may prefer optimized delivery copies when both exist.

## Baseline

Before the pilot conversion, the Canvas-only asset tree contained:

- 284 PNG/JPEG files;
- 100.3 MB total;
- 68 files larger than 500 KB;
- 39.0 MB concentrated in those files; and
- 9 exact-duplicate groups containing 19 redundant copies.

The largest files were not unusually large in pixel dimensions. Most workbook pages were about 1,275 × 1,650 and most presentation slides were 1,600 × 900. The slow-load problem is therefore primarily format/compression and repeated upload, not simply extreme resolution.

## Pilot Result

The approved pilot targets were:

1. `1SW Wk1 Day 1` manufacturing chapter opener; and
2. the seven `1SW Wk5 Day 2` Safe or Spoofed email images.

JPEG delivery copies were exported at quality 82 while retaining the original dimensions. Visual inspection confirmed that body text, sender/domain clues, workbook labels, and image details remained readable at original size.

| Pilot set | Original PNG total | Optimized JPEG total | Savings |
|---|---:|---:|---:|
| 8 images | 7.99 MB | 1.65 MB | 6.34 MB / 79.4% |

`build_wk1.py` and `build_wk5.py` now prefer a same-stem JPEG when it exists and skip the larger PNG during Canvas upload. The original PNGs remain available for regeneration and close inspection but are no longer the active delivery files for those pages.

## Duplicate Findings

The clearest repeated uploads are:

- the same IT App Exploration image in seven 1SW lesson folders;
- Irving IT Programs page 2 in five folders;
- Irving IT Programs page 1 in four folders; and
- repeated Xello/legal, outbreak, pest-patrol, and EMT deck images in two folders each.

The importers currently organize files by lesson/day for teacher clarity. A later deduplication pass should use a locked shared folder such as `CCR Materials/Shared Visuals` and reference one Canvas file ID from multiple pages. Do not delete existing Canvas files until every referencing page has been migrated and checked.

## Optimization Standard

- Workbook page or dense screenshot: target 1,200–1,400 pixels on the long edge. Use JPEG quality 82–86 when there is no transparency; visually inspect small text.
- Slide or photo: retain enough resolution for zoom, usually 1,400–1,600 pixels wide; JPEG quality 80–84 is the default.
- Diagram with flat colors or transparency: retain PNG, then optimize losslessly if an approved optimizer is available.
- Do not convert an image merely to hit a file-size number. Readability, color contrast, source fidelity, and zoom are the acceptance criteria.
- Native Canvas text must carry required directions. An image may orient, model, or supply licensed evidence, but it should not be the only accessible route when the learning task can be expressed as text.
- Give each image meaningful alt text. For observation tasks, describe visible details without disclosing the answer.

## Priority Queue

1. Convert remaining 1SW presentation slides and chapter openers larger than 750 KB after side-by-side text checks.
2. Move exact shared IT/Xello images to one locked shared Canvas folder and update importers to reuse their file IDs.
3. Optimize 2SW/3SW chapter openers and image-heavy deck slides larger than 750 KB.
4. Leave the already optimized 5SW/6SW JPEG production sets alone unless browser timing shows a specific problem; most are already roughly 90–300 KB.
5. After the unpublished course import, test representative pages on a student Chromebook/network and record first-load behavior before changing more files.

## Verification Gate

An optimized file replaces the active Canvas delivery file only when:

1. pixel dimensions are documented;
2. the optimized size is lower;
3. small text and task evidence are readable at 100% and browser-fit width;
4. alt text remains correct;
5. the importer references the optimized filename; and
6. the student page renders without a broken or unauthorized file link.
