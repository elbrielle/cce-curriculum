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

## 3SW Week 1 Agriculture Opener

The 3SW Week 1 Day 1 FYF Agriculture opener was the largest remaining likely
delivery candidate in the local audit. The licensed 1,275 by 1,650 PNG remains
unchanged in the gitignored archive. A 1,020 by 1,320 JPEG delivery copy reduced
the file from 1,518,018 bytes to 482,337 bytes, a 68.2% reduction.

The original and delivery copy were compared at original detail, the 720-pixel
Canvas maximum, and a 390-pixel viewport. The chapter title, explanatory text,
decision prompt, career labels, and page number remain as readable as the source
at each displayed size. The native Student Guide and fixed career-evidence guide
remain the independent text route. `build_3sw_wk1.py` now preflights, uploads,
locks, and embeds the JPEG while retaining the PNG locally.

The local audit now reports the complete licensed archive separately from likely
Canvas delivery candidates. Same-stem PNG originals are excluded from the
delivery ranking when a JPEG delivery copy exists, which prevents source
preservation from being misreported as student download weight.

## 2SW Week 3 Health Science Opener

The 2SW Week 3 Day 1 FYF Health Science opener is an active Student Guide
image, unlike several large files that remain locked in Canvas folders but are
not embedded. The licensed 1,275 by 1,650 PNG remains unchanged in the
gitignored archive. A 1,020 by 1,320 JPEG delivery copy reduced the file from
1,314,848 bytes to 418,120 bytes, a 68.2% reduction.

The original and delivery copy were compared at original detail and at the
Canvas display sizes. The chapter title, career labels, explanatory text,
decision prompt, and page number remain as readable as the source. The native
Student Guide and nursing-route evidence materials remain the independent text
route. `build_2sw_wk3.py` now preflights, uploads, locks, and embeds the JPEG
while retaining the PNG locally.

## 2SW Week 1 Law and Public Safety Opener

The 2SW Week 1 Day 1 FYF Law and Public Safety opener is an active Student
Guide image. The licensed 1,148 by 1,485 PNG remains unchanged in the
gitignored archive. A 1,020 by 1,320 JPEG delivery copy reduced the file from
1,305,837 bytes to 464,321 bytes, a 64.4% reduction.

The original and delivery copy were compared at original detail, desktop
Canvas width, and a 430-pixel mobile viewport. The chapter title, career
labels, explanatory text, decision prompt, and page number remain as readable
as the source. The native Student Guide and Legal Career Evidence Cards remain
the independent text route. `build_2sw_wk1.py` now preflights, uploads, locks,
and embeds the JPEG while retaining the PNG locally.

This slice also brought the importer to the current release-safety standard
before any live write: local dependency preflight before stdin, a unique
unpublished mapped-Major guard before mutation, locked upload and folder
sweeps, exact typed sixteen-item reconciliation, and final fresh checks for the
module, pages, Major grading state, submission routes, rubric marker, and
storage locks.

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
