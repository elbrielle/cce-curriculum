# CCE Canvas student-resource access repair

## What this fixes

Canvas Commons copies can preserve a lock on the file record even after the
containing folder has been opened. The earlier CCE image repair found only
`<img>` files. Linked PDFs, including Exit Tickets, were intentionally outside
that scan and can therefore still show a padlock in Student View.

This tool audits every Canvas file referenced by course Pages and module
content. It covers images, ordinary download links, embedded/previewed files,
direct File module items, and files referenced by module Assignments,
Discussions, and Classic Quizzes.

For each referenced file it checks all Canvas availability controls:

- file and ancestor-folder `locked` state;
- file and ancestor-folder `hidden` state;
- file and ancestor-folder availability dates.

The repair preserves each file's existing `visibility_level`. Canvas documents
`inherit` as the normal default; changing that setting is not required to clear
a lock and could broaden or narrow access beyond this task.

## Safety boundary

The tool changes only existing file and folder availability fields. It does not
create, upload, move, rename, replace, or delete files. It never publishes or
unpublishes modules, module items, Pages, Assignments, Discussions, or Quizzes.
An apply run snapshots every publication state and fails if any state differs
afterward.

`--discover` and `--check` are read-only. A write requires the explicit
`--apply` flag and explicit course IDs. Discovered courses are never
automatically selected for repair.

## Run from this folder

First list CCE courses visible to the token:

```bash
uv run --with httpx python cce_student_resource_access_fix.py --discover
```

Audit one or more exact course IDs:

```bash
uv run --with httpx python cce_student_resource_access_fix.py \
  --check \
  --course-id 97981 \
  --course-id 98060
```

Apply only after reading the audit:

```bash
uv run --with httpx python cce_student_resource_access_fix.py \
  --apply \
  --course-id 97981 \
  --course-id 98060
```

The script asks for the Canvas token with hidden input. It may also receive one
line through standard input. The token is never saved or printed.

For a longer list, put one numeric course ID on each line and use
`--courses-file ids.txt`. Comments beginning with `#` are allowed.

## Verification after apply

The JSON result must show:

- `passed: true`;
- `restricted_after.files: 0` and `restricted_after.folders: 0`;
- empty unresolved and cross-course lists; and
- `publication_states_unchanged: true`.

Then have a teacher open one Student Guide through its module item in Student
View and test both an image and a linked Exit Ticket PDF. The API proves the
saved settings; Student View proves the enrolled-student experience.
