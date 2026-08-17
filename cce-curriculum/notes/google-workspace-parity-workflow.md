# Google Workspace parity workflow

## Purpose

Some CCE teachers teach from Google Slides and Google Docs; others download PowerPoint or Word files. The Google Drive mirror therefore carries both forms without replacing Canvas or creating a third curriculum source.

The three maintained surfaces are:

- **Canvas:** active teacher and student delivery, including authenticated and licensed material.
- **GitHub public site:** generated public planning mirror and public-safe downloads.
- **Google Drive:** organized teacher distribution with native Google files and Office downloads.

Canvas and the tracked curriculum source remain authoritative. A teacher may edit a Google master while teaching, but that edit is feedback until it is reconciled into the tracked source, checked, and sent back to Canvas, Drive, and the public site where licensing permits.

## Drive organization

Root folder: [`Units_CCR`](https://drive.google.com/drive/folders/1FbY0WdnXN-PkW6Vi76qcpDfp7SKq5c5H)

Each curriculum unit uses the same structure as the VILS Drive mirror:

```text
Units_CCR/
  SW# · Wk# Unit title/
    Google Masters/
      Native Google Slides, Docs, or Sheets
    Download Releases/
      .pptx, .docx, .xlsx, and public-safe PDFs
```

Generate the 36-unit inventory from the built public-site manifest and the editable-artifact parity manifest. Create folders only from that inventory; do not type or guess a second unit list. Stable folder and file IDs live in `google-workspace-drive-state.json`.

`Lucero's Weekly Slides/` is a separate teaching folder. It contains Ms. Lucero's combined Monday-Friday decks. Those decks are assembled from the approved daily masters; they do not replace the daily source files.

## Artifact rules

For every teacher-facing artifact:

1. Start from the approved tracked file or generated Canvas source.
2. Upload the exact Office binary to the unit's `Download Releases` folder.
3. Convert that same binary to a native Google file in `Google Masters`.
4. Verify page or slide count, text, images, layout, speaker notes, and the teacher name after Google conversion.
5. Record the local hash, Canvas identity, Drive identities, and public-site decision in `google-workspace-parity-manifest.json`.
6. Add an Office download and Google `/copy` option to the public site only when the source is public-safe and the Google sharing state has been intentionally verified.
7. Keep AVID source decks, H&L, Find Your Future, Xello, Climber Notes, and other licensed or authenticated material out of the public site. Those files may be available in authenticated Canvas and the shared teacher Drive.

Format pairs follow the artifact's real job:

- presentations: PowerPoint plus native Google Slides;
- editable documents: Word plus native Google Docs;
- spreadsheets: Excel plus native Google Sheets;
- fixed-layout worksheets or rubrics: the verified PDF remains the primary release. Add an editable Google version only when it preserves the instructional layout and response space.

Do not convert a PDF into a loose Google Doc merely to satisfy a file-count rule. Equivalent access matters more than matching extensions.

## Updating a file

When the tracked source changes:

1. Run the artifact-specific local QA and render checks.
2. Replace the existing Canvas file without changing its course role.
3. Replace the existing Office file bytes in Drive so its Drive ID remains stable.
4. Re-import or update the native Google master, then render and inspect it again.
5. Update the manifest hash, byte count, revision evidence, and checked date.
6. Rebuild and verify the public site when the artifact is public-safe.

Do not create a second file with `final`, `new`, or a date suffix when an existing release can be updated safely. Stable IDs keep Canvas, shared links, and `/copy` links from drifting.

## Repeatable maintenance run

Use this order after an approved tracked artifact changes:

1. Rebuild and verify `public-site/` so `public-site/dist/data/site-manifest.json` contains the current public-safe release set.
2. Run the local inventory and manifest gates:

   ```bash
   UV_CACHE_DIR=/tmp/cce-google-parity-uv \
     uv run --with beautifulsoup4 --with httpx \
     python build/google_workspace/verify_parity.py
   ```

   This one command verifies the generated public site, rebuilds the deterministic
   36-unit distribution inventory, checks every recorded Drive folder and release,
   checks the exact Canvas/public Google `/copy` link sets, and compiles the
   36-module live-Canvas expectation set before any credential is requested.

3. Use the Google Drive connector to update the recorded stable file ID. Replace bytes in place for Office or PDF releases. Update the native Google master only when an editable equivalent is justified.
4. Re-read the affected Drive folder and file metadata. Confirm the recorded parent folder, name, byte count, native file type, and Irving ISD domain-reader access.
5. Add or refresh the Canvas Google `/copy` link in the matching Teacher Facilitator Guide. Keep the page, module, and file package unpublished and locked.
6. Add a public-site `/copy` link only for an artifact whose manifest decision is `public_site.included = true`. Authenticated AVID, H&L, FYF, Xello, and Climber materials stay out of the public mirror.
7. Rebuild the public mirror and rerun the Canvas, site, parity, and Drive-distribution gates.

`google-workspace-distribution-inventory.json` is generated and may be replaced by its builder. `google-workspace-drive-state.json` is the stable-ID readback record and changes only after the live Drive operation is verified.

## Teacher edits made during class

Ms. Lucero may adjust a weekly Google deck while teaching. At the end of the week:

1. Compare the edited Google deck with the approved daily sources.
2. Identify changes that improved pacing, clarity, examples, visuals, or student directions.
3. Rebuild those changes in the tracked source rather than treating the Drive edit as the only copy.
4. Regenerate the daily and weekly releases and repeat the parity checks.

This feedback loop is how later decks should become more accurate to actual classroom use without allowing Drive, Canvas, and GitHub to diverge.

## Current synchronized state

As of 2026-08-16, `Units_CCR` contains all 36 curriculum unit folders. Each unit has one `Google Masters` folder and one `Download Releases` folder. The recorded public distribution includes 132 unique public-safe files referenced 133 times across the 36 units. Weeks 0 and 1 also contain ten verified native Google Slides masters and their matching PowerPoint releases. Week 0 includes the native first-week goal-setting Google Doc plus the matching Word and PDF releases.

The live readback verified 36 unit folders, 72 standard subfolders, all 133 public release references, ten native presentations, ten PowerPoint releases, and Irving ISD domain-reader access. The exact IDs and local hashes are recorded in the two manifests and the Drive-state file rather than repeated in this narrative.
