#!/usr/bin/env python3
"""Run one Canvas builder, then reopen every course-referenced file.

Legacy week builders still contain internal storage-lock assertions. This
wrapper preserves their idempotent content behavior, then applies the current
owner policy as the final deployment invariant: modules remain under teacher
publication control, while referenced images, PDFs, decks, and other files and
their ancestor folders remain available to enrolled students.

The Canvas token is accepted only on stdin and passed to the builder and
resource-access finalizer on stdin. It is never put in an argument, written to
disk, or printed. Student response-route changes are intentionally not chained
to a builder: that separate workflow requires a reviewed 180-route registry,
an immutable prepare plan, and an explicitly supplied plan SHA-256.
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = Path(__file__).resolve().parent
RESOURCE_FIX = (
    CANVAS_DIR
    / "dist"
    / "cce-student-resource-access-fix"
    / "cce_student_resource_access_fix.py"
)
WORKSHEET_LINK_SYNC = CANVAS_DIR / "sync_student_google_doc_links.py"


def literal_course_id(builder: Path) -> int | None:
    tree = ast.parse(builder.read_text(encoding="utf-8"), filename=str(builder))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(
            isinstance(target, ast.Name) and target.id == "COURSE_ID"
            for target in targets
        ):
            continue
        value = node.value
        if isinstance(value, ast.Constant) and isinstance(value.value, int):
            return value.value
    return None


def redact(value: str, token: str) -> str:
    return value.replace(token, "[REDACTED]") if token else value


def resolve_builder(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if candidate.parent != CANVAS_DIR or not candidate.name.startswith("build_"):
        raise SystemExit("Builder must be a build/canvas/build_*.py file.")
    if not candidate.is_file():
        raise SystemExit(f"Builder not found: {candidate}")
    return candidate


def validated_resource_access_result(payload: object, course_id: int) -> dict:
    """Require the finalizer's complete, publication-neutral success contract."""
    if not isinstance(payload, list) or len(payload) != 1:
        raise ValueError("expected one course result")
    result = payload[0]
    if not isinstance(result, dict):
        raise ValueError("course result must be an object")
    restricted_after = result.get("restricted_after")
    if (
        result.get("course_id") != course_id
        or result.get("passed") is not True
        or result.get("publication_states_unchanged") is not True
        or restricted_after != {"files": 0, "folders": 0}
    ):
        raise ValueError(
            "finalizer did not prove zero restrictions and unchanged publication states"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a Canvas builder and enforce unlocked referenced resources."
    )
    parser.add_argument("builder", help="build/canvas/build_*.py")
    parser.add_argument(
        "--course-id",
        type=int,
        help="required only when the builder has no literal COURSE_ID",
    )
    args = parser.parse_args()
    builder = resolve_builder(args.builder)
    if not RESOURCE_FIX.is_file():
        raise SystemExit(f"Resource-access fixer not found: {RESOURCE_FIX}")
    py_compile.compile(str(builder), doraise=True)
    py_compile.compile(str(RESOURCE_FIX), doraise=True)
    if WORKSHEET_LINK_SYNC.is_file():
        py_compile.compile(str(WORKSHEET_LINK_SYNC), doraise=True)
    course_id = args.course_id or literal_course_id(builder)
    if not course_id:
        raise SystemExit("Could not resolve COURSE_ID; pass --course-id explicitly.")

    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    builder_run = subprocess.run(
        [sys.executable, str(builder)],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if builder_run.returncode:
        print(
            redact(builder_run.stderr or builder_run.stdout, token),
            file=sys.stderr,
        )
        print(
            "Builder failed; the resource-access finalizer was not run.",
            file=sys.stderr,
        )
        return builder_run.returncode

    resource_run = subprocess.run(
        [
            sys.executable,
            str(RESOURCE_FIX),
            "--apply",
            "--course-id",
            str(course_id),
        ],
        cwd=ROOT,
        input=token + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    if resource_run.returncode:
        print(
            redact(resource_run.stderr or resource_run.stdout, token),
            file=sys.stderr,
        )
        print(
            "Builder completed, but referenced-resource access verification failed. "
            "Nothing was published; rerun the finalizer after diagnosing the error.",
            file=sys.stderr,
        )
        return resource_run.returncode

    try:
        builder_payload = json.loads(builder_run.stdout)
    except json.JSONDecodeError:
        builder_payload = {"raw_output": redact(builder_run.stdout[-4000:], token)}
    try:
        resource_payload = validated_resource_access_result(
            json.loads(resource_run.stdout), course_id
        )
    except (json.JSONDecodeError, ValueError):
        print(
            redact(resource_run.stdout[-4000:], token),
            file=sys.stderr,
        )
        print(
            "Referenced-resource finalizer did not prove safe completion.",
            file=sys.stderr,
        )
        return 3
    link_payload = {
        "status": "separate_reviewed_plan_required",
        "canvas_writes": 0,
        "tool": str(WORKSHEET_LINK_SYNC.relative_to(ROOT)),
    }
    print(
        json.dumps(
            {
                "builder": builder.name,
                "course_id": course_id,
                "builder_result": builder_payload,
                "student_google_docs": link_payload,
                "resource_access": resource_payload,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
