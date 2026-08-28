#!/usr/bin/env python3
"""Build a deterministic draft source specification for CCE student Docs.

This script is deliberately local-only. It reads curriculum sources and the
existing Google Doc link registry, then writes a QA draft beside the registry.
It never calls Google Drive or Canvas and refuses to overwrite the live link
registry.

The draft exists because the historical 173-Doc registry was built from
``build/onenote`` derivatives. Current curriculum authority is split across:

* ``docs/<sw>/<week>/dayN.md`` for the daily contract, title, and planning text;
* ``build/canvas/build_*.py`` plus its student template for the delivered route;
* ``build/worksheet_sources/*.md`` for structured student response artifacts.

Usage:

    python3 build/google_docs/build_student_worksheet_source_specs.py
    python3 build/google_docs/build_student_worksheet_source_specs.py --check
    python3 build/google_docs/build_student_worksheet_source_specs.py --stdout
    python3 build/google_docs/build_student_worksheet_source_specs.py --strict
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = ROOT / "docs"
CANVAS_ROOT = ROOT / "build" / "canvas"
TEMPLATE_ROOT = CANVAS_ROOT / "templates"
WORKSHEET_SOURCE_ROOT = ROOT / "build" / "worksheet_sources"
WORKSHEET_PDF_ROOT = ROOT / "docs" / "resources" / "worksheets"
LIVE_REGISTRY = ROOT / "build" / "google_docs" / "student_worksheet_links.json"
DEFAULT_OUTPUT = (
    ROOT / "build" / "google_docs" / "student_worksheet_source_specs.draft.json"
)

DAY_PATH_RE = re.compile(
    r"^docs/(?P<sw>[1-6])sw/wk(?P<week>\d+)-[^/]+/day(?P<day>[1-5])\.md$"
)
H1_RE = re.compile(r"^#\s+(?!#)(.+?)\s*$", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(?!#)(.+?)\s*$", re.MULTILINE)
DOL_RE = re.compile(
    r"^-\s+\*\*Demonstration of Learning:\*\*\s*(.+?)\s*$", re.MULTILINE
)
EXIT_MARKER_RE = re.compile(
    r"^\*\*EXIT TICKET\*\*\s*(?:\((?P<format>[^)]+)\))?.*$", re.MULTILINE
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SUPPORT_HEADING_RE = re.compile(
    r"support|differentiat|fallback|recovery|absence|equal route|access", re.I
)
ELL_LINE_RE = re.compile(
    r"\b(?:ELL|EB|emergent bilingual|bilingual|Spanish|strongest language|"
    r"word bank|language support)\b",
    re.I,
)
RESPONSE_MARKER_RE = re.compile(
    r"\[\[\s*(?:lines|box)\s*:|_{6,}|-\s*\[\s*\]|"
    r"\bCircle\s+(?:one|ONE)\b|\|\s*\|",
    re.I,
)


def repo_path(path: Path) -> str:
    """Return a stable POSIX path relative to the repository root."""

    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def section_spans(text: str) -> list[tuple[str, int, int]]:
    matches = list(H2_RE.finditer(text))
    spans: list[tuple[str, int, int]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        spans.append((match.group(1).strip(), match.start(), end))
    return spans


def exact_exit_section(text: str) -> tuple[str | None, str | None, str | None]:
    """Return the exact H2 section containing the first EXIT TICKET marker."""

    marker = EXIT_MARKER_RE.search(text)
    if not marker:
        return None, None, None
    heading = None
    start = marker.start()
    end = len(text)
    for candidate_heading, candidate_start, candidate_end in section_spans(text):
        if candidate_start <= marker.start() < candidate_end:
            heading = candidate_heading
            start = candidate_start
            end = candidate_end
            break
    section = text[start:end].rstrip() + "\n"
    return heading, marker.group("format"), section


def support_sections(text: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for heading, start, end in section_spans(text):
        if SUPPORT_HEADING_RE.search(heading):
            markdown = text[start:end].rstrip() + "\n"
            output.append(
                {
                    "heading": heading,
                    "markdown": markdown,
                    "sha256": sha256_text(markdown),
                }
            )
    return output


def extract_ell_lines(text: str) -> list[str]:
    """Keep exact source lines that explicitly carry language support."""

    return [line.rstrip() for line in text.splitlines() if ELL_LINE_RE.search(line)]


def parse_front_matter(path: Path) -> tuple[dict[str, str], str]:
    """Parse the worksheet pipeline's flat key/value front matter."""

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "\n".join(lines)
    metadata: dict[str, str] = {}
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    body = "\n".join(lines[(end + 1) if end is not None else 0 :])
    return metadata, body


def builder_path(six_weeks: int, week: int) -> Path:
    if six_weeks == 1:
        return CANVAS_ROOT / f"build_wk{week}.py"
    return CANVAS_ROOT / f"build_{six_weeks}sw_wk{week}.py"


def student_template_path(six_weeks: int, week: int, day: int) -> Path | None:
    candidates: list[Path]
    if six_weeks == 1:
        candidates = [
            TEMPLATE_ROOT / f"wk{week}-day{day}-student.html",
            TEMPLATE_ROOT / f"wk{week}-student.html",
        ]
    else:
        candidates = [
            TEMPLATE_ROOT / f"{six_weeks}sw-wk{week}-day{day}-student.html",
            TEMPLATE_ROOT / f"{six_weeks}sw-wk{week}-student.html",
        ]
    return next((path for path in candidates if path.is_file()), None)


def _literal_pdf_map(tree: ast.AST) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Dict):
            continue
        try:
            candidate = ast.literal_eval(value)
        except (ValueError, TypeError, SyntaxError):
            continue
        if not isinstance(candidate, dict):
            continue
        for key, filename in candidate.items():
            if (
                isinstance(key, str)
                and isinstance(filename, str)
                and filename.lower().endswith(".pdf")
            ):
                mapping[key] = filename
    return mapping


def _pdf_refs(node: ast.AST, known_keys: set[str]) -> set[str]:
    found: set[str] = set()
    for subscript in ast.walk(node):
        if not isinstance(subscript, ast.Subscript):
            continue
        slice_node = subscript.slice
        if (
            isinstance(slice_node, ast.Constant)
            and isinstance(slice_node.value, str)
            and slice_node.value in known_keys
        ):
            found.add(slice_node.value)
    return found


def builder_day_pdf_sources(path: Path) -> dict[int, list[str]]:
    """Infer builder-linked PDFs without importing or executing the builder."""

    if not path.is_file():
        return {}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    pdf_map = _literal_pdf_map(tree)
    if not pdf_map:
        return {}

    # Builders use several shapes (student, students, student_values, and
    # teacher_data). Union every five-day dictionary that references a known
    # PDF key, then let worksheet front matter identify audience and role.
    per_day: dict[int, set[str]] = defaultdict(set)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        candidate: dict[int, set[str]] = {}
        for key_node, value_node in zip(node.keys, node.values):
            if (
                isinstance(key_node, ast.Constant)
                and isinstance(key_node.value, int)
                and 1 <= key_node.value <= 5
            ):
                refs = _pdf_refs(value_node, set(pdf_map))
                if refs:
                    candidate[key_node.value] = refs
        if len(candidate) >= 4:
            for day, refs in candidate.items():
                per_day[day].update(refs)

    return {
        day: sorted({pdf_map[key] for key in keys})
        for day, keys in sorted(per_day.items())
    }


def worksheet_source_record(filename: str) -> dict[str, object] | None:
    source = WORKSHEET_SOURCE_ROOT / f"{Path(filename).stem}.md"
    if not source.is_file():
        return None
    metadata, body = parse_front_matter(source)
    slug = metadata.get("slug") or source.stem
    pdf = WORKSHEET_PDF_ROOT / f"{slug}.pdf"
    audience = metadata.get("audience", "student")
    variant_of = metadata.get("variant_of", "")
    has_response_markers = bool(RESPONSE_MARKER_RE.search(body))
    record: dict[str, object] = {
        "source_path": repo_path(source),
        "source_sha256": sha256_path(source),
        "title": metadata.get("title", source.stem.replace("-", " ").title()),
        "slug": slug,
        "kind": metadata.get("kind", "worksheet"),
        "audience": audience,
        "variant_of": variant_of or None,
        "language": metadata.get("language", "en"),
        "has_response_markers": has_response_markers,
        "is_student_base_source": audience == "student" and not variant_of,
        "is_response_route_candidate": (
            audience == "student" and not variant_of and has_response_markers
        ),
        "pdf_path": repo_path(pdf) if pdf.is_file() else None,
        "pdf_sha256": sha256_path(pdf) if pdf.is_file() else None,
    }
    return record


def markdown_pdf_links(day_path: Path, text: str) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for label, raw_href in MARKDOWN_LINK_RE.findall(text):
        href = raw_href.strip().split(maxsplit=1)[0]
        parsed = urlparse(href)
        if not parsed.path.lower().endswith(".pdf"):
            continue
        key = (label.strip(), href)
        if key in seen:
            continue
        seen.add(key)
        if parsed.scheme in {"http", "https"}:
            records.append(
                {
                    "label": label.strip(),
                    "href": href,
                    "link_type": "external_url",
                    "path": None,
                    "exists": None,
                    "sha256": None,
                    "bytes": None,
                }
            )
            continue

        clean_href = href.split("#", 1)[0].split("?", 1)[0]
        resolved = (day_path.parent / clean_href).resolve()
        inside_repo = False
        try:
            relative = repo_path(resolved)
            inside_repo = True
        except ValueError:
            relative = str(resolved)
        exists = resolved.is_file()
        if inside_repo and relative.startswith("docs/resources/exit-tickets/"):
            link_type = "exit_ticket_pdf"
        elif inside_repo and relative.startswith("docs/resources/worksheets/"):
            link_type = "worksheet_pdf"
        else:
            link_type = "other_local_pdf"
        records.append(
            {
                "label": label.strip(),
                "href": href,
                "link_type": link_type,
                "path": relative,
                "exists": exists,
                "sha256": sha256_path(resolved) if exists else None,
                "bytes": resolved.stat().st_size if exists else None,
            }
        )
    return records


def day_coordinates(path: Path) -> tuple[int, int, int]:
    match = DAY_PATH_RE.match(repo_path(path))
    if not match:
        raise ValueError(f"Nonstandard day path: {path}")
    return tuple(int(match.group(name)) for name in ("sw", "week", "day"))


def discover_days() -> list[Path]:
    paths = list(DOCS_ROOT.glob("[1-6]sw/wk*-*/day[1-5].md"))
    return sorted(paths, key=day_coordinates)


def load_registry() -> tuple[dict[tuple[int, int, int], dict[str, object]], dict[str, object]]:
    payload = json.loads(LIVE_REGISTRY.read_text(encoding="utf-8"))
    by_day = {
        (int(row["six_weeks"]), int(row["week"]), int(row["day"])): row
        for row in payload.get("documents", [])
    }
    return by_day, payload


def registry_record(row: dict[str, object] | None) -> dict[str, object] | None:
    if row is None:
        return None
    return {
        "page_id": row.get("page_id"),
        "document_id": row.get("document_id"),
        "display_title": row.get("display_title"),
        "title": row.get("title"),
        "copy_url": row.get("copy_url"),
        "folder_id": row.get("folder_id"),
        "folder_path": row.get("folder_path"),
    }


def build_day_spec(
    path: Path,
    registry_by_day: dict[tuple[int, int, int], dict[str, object]],
    builder_cache: dict[Path, dict[int, list[str]]],
) -> dict[str, object]:
    six_weeks, week, day = day_coordinates(path)
    text = path.read_text(encoding="utf-8")
    h1_match = H1_RE.search(text)
    dol_match = DOL_RE.search(text)
    exit_heading, exit_format, exit_section = exact_exit_section(text)
    supports = support_sections(text)
    pdf_links = markdown_pdf_links(path, text)
    builder = builder_path(six_weeks, week)
    template = student_template_path(six_weeks, week, day)
    if builder not in builder_cache:
        builder_cache[builder] = builder_day_pdf_sources(builder)
    worksheet_records = [
        record
        for filename in builder_cache[builder].get(day, [])
        if (record := worksheet_source_record(filename)) is not None
    ]
    worksheet_records.sort(key=lambda row: str(row["source_path"]))

    registry_row = registry_by_day.get((six_weeks, week, day))
    manual_reasons: list[str] = []
    if registry_row is None:
        manual_reasons.append("missing_from_live_google_doc_registry")
        if week == 0:
            manual_reasons.append("legacy_registry_excluded_week_0")
        else:
            manual_reasons.append("legacy_registry_exit_ticket_gap")

    qa_flags: list[str] = []
    if not h1_match:
        qa_flags.append("missing_h1")
    if not dol_match:
        qa_flags.append("missing_demonstration_of_learning")
    if not builder.is_file():
        qa_flags.append("missing_canvas_builder")
    if template is None:
        qa_flags.append("missing_student_template")
    if any(link["exists"] is False for link in pdf_links):
        qa_flags.append("missing_linked_local_pdf")
    if registry_row is None:
        qa_flags.append("manual_google_doc_spec_required")

    exit_pdf = next(
        (
            link
            for link in pdf_links
            if link["link_type"] == "exit_ticket_pdf"
            and exit_section is not None
            and str(link["href"]) in exit_section
        ),
        None,
    )

    return {
        "day_key": f"{six_weeks}SW-Wk{week}-Day{day}",
        "six_weeks": six_weeks,
        "week": week,
        "day": day,
        "day_source": {
            "path": repo_path(path),
            "sha256": sha256_path(path),
            "bytes": path.stat().st_size,
        },
        "h1": h1_match.group(1).strip() if h1_match else None,
        "demonstration_of_learning": (
            dol_match.group(1).strip() if dol_match else None
        ),
        "exit_ticket": {
            "marker_present": exit_section is not None,
            "enclosing_h2": exit_heading,
            "format": exit_format,
            "section_markdown": exit_section,
            "section_sha256": sha256_text(exit_section) if exit_section else None,
            "linked_pdf": exit_pdf,
        },
        "support": {
            "sections": supports,
            "ell_keyword_lines": extract_ell_lines(text),
        },
        "linked_pdfs": pdf_links,
        "canvas_builder": {
            "path": repo_path(builder) if builder.is_file() else None,
            "sha256": sha256_path(builder) if builder.is_file() else None,
        },
        "student_template": (
            {
                "path": repo_path(template),
                "sha256": sha256_path(template),
            }
            if template
            else None
        ),
        "builder_linked_worksheet_sources": worksheet_records,
        "has_combined_daily_work_source": any(
            bool(row["is_response_route_candidate"]) for row in worksheet_records
        ),
        "live_google_doc": registry_record(registry_row),
        "manual_spec_required": bool(manual_reasons),
        "manual_spec_reasons": manual_reasons,
        "qa_flags": sorted(qa_flags),
    }


def build_payload() -> dict[str, object]:
    registry_by_day, registry_payload = load_registry()
    builder_cache: dict[Path, dict[int, list[str]]] = {}
    days = [
        build_day_spec(path, registry_by_day, builder_cache) for path in discover_days()
    ]
    manual = [str(row["day_key"]) for row in days if row["manual_spec_required"]]
    registered = [row for row in days if row["live_google_doc"] is not None]
    combined_registered = [
        row for row in registered if row["has_combined_daily_work_source"]
    ]
    close_only_registered = [
        row for row in registered if not row["has_combined_daily_work_source"]
    ]
    exit_marker_days = [
        row for row in days if row["exit_ticket"]["marker_present"]  # type: ignore[index]
    ]
    missing_local_pdfs = [
        {
            "day_key": row["day_key"],
            "path": link["path"],
            "href": link["href"],
        }
        for row in days
        for link in row["linked_pdfs"]  # type: ignore[index]
        if link["exists"] is False
    ]
    return {
        "schema_version": 1,
        "artifact": "CCE student Google Doc source specification draft",
        "determinism": (
            "No timestamp is emitted. Hashes cover exact current file bytes; "
            "records are sorted by six-weeks, week, and day."
        ),
        "authority_order": [
            "current Canvas builder and student template for delivered route and close",
            "build/worksheet_sources Markdown for structured student artifacts",
            "docs day Markdown for H1, daily contract, planning text, and legacy EXIT TICKET blocks",
            "generated worksheet and exit-ticket PDFs for printable release verification only",
            "build/onenote HTML is a derivative and is not an authoring source",
        ],
        "live_registry": {
            "path": repo_path(LIVE_REGISTRY),
            "sha256": sha256_path(LIVE_REGISTRY),
            "schema": registry_payload.get("schema"),
            "document_count": len(registry_by_day),
        },
        "summary": {
            "discovered_day_count": len(days),
            "registered_google_doc_day_count": len(registered),
            "manual_spec_day_count": len(manual),
            "manual_spec_day_keys": manual,
            "day_files_with_exit_ticket_marker": len(exit_marker_days),
            "registered_days_with_combined_daily_work_source": len(combined_registered),
            "registered_days_with_close_only_route": len(close_only_registered),
            "registered_close_only_day_keys": [
                str(row["day_key"]) for row in close_only_registered
            ],
            "missing_linked_local_pdf_count": len(missing_local_pdfs),
            "missing_linked_local_pdfs": missing_local_pdfs,
        },
        "days": days,
    }


def render_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def validate_strict(payload: dict[str, object]) -> list[str]:
    summary = payload["summary"]
    failures: list[str] = []
    expected = {
        "discovered_day_count": 180,
        "registered_google_doc_day_count": 173,
        "manual_spec_day_count": 7,
        "registered_days_with_combined_daily_work_source": 170,
        "registered_days_with_close_only_route": 3,
        "missing_linked_local_pdf_count": 0,
    }
    for field, wanted in expected.items():
        actual = summary[field]  # type: ignore[index]
        if actual != wanted:
            failures.append(f"{field}: expected {wanted}, found {actual}")
    return failures


def resolve_output(value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    if candidate == LIVE_REGISTRY.resolve():
        raise ValueError("Refusing to overwrite the live student_worksheet_links.json registry")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Draft JSON path (default: build/google_docs/student_worksheet_source_specs.draft.json)",
    )
    parser.add_argument("--check", action="store_true", help="Fail if the draft is missing or stale")
    parser.add_argument("--stdout", action="store_true", help="Print the deterministic JSON instead of writing it")
    parser.add_argument("--strict", action="store_true", help="Require the current 180/173/7 and 170/3 invariants")
    args = parser.parse_args()

    try:
        output = resolve_output(args.output)
    except ValueError as error:
        parser.error(str(error))

    payload = build_payload()
    rendered = render_payload(payload)
    failures = validate_strict(payload) if args.strict else []
    if failures:
        for failure in failures:
            print(f"STRICT: {failure}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not output.is_file():
            print(f"Draft is missing: {output}", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != rendered:
            print(f"Draft is stale: {output}", file=sys.stderr)
            return 1
        print(f"Draft is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Wrote {len(payload['days'])} day specs to {output}")  # type: ignore[arg-type]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
