#!/usr/bin/env python3
"""Build the reviewed CCE Student Guide response-link selector inventory.

This is a read-only audit generator. It combines the immutable source-course
Canvas plan, the reviewed 180-route Google Doc registry, the composed worksheet
content specification, and live read-only Canvas file metadata. It never writes
Canvas.

The inventory selects only existing links to genuine student response-work PDFs.
It deliberately excludes assignments, quizzes, rubrics, word banks, support
variants, and reference-only PDFs. A selected link keeps its text, styling,
location, and every non-href byte; the matching Google Doc ``/copy`` URL is the
only approved replacement value.

Canvas file ``?verifier=`` query strings are capability-bearing values and are
never written to the repository. The output stores the exact canonical URL
without its query plus a SHA-256 digest of the complete observed href.

Usage:

    python3 build/google_docs/build_student_response_link_selector_inventory.py \
      < ~/.canvas_token

    python3 build/google_docs/build_student_response_link_selector_inventory.py \
      --check < ~/.canvas_token
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "build/google_docs/student_response_route_registry.json"
CONTENT_SPECS = ROOT / "build/google_docs/student_worksheet_content_specs.draft.json"
MANUAL_CONTENT_SPECS = (
    ROOT / "build/google_docs/student_response_route_manual_content_specs.json"
)
DEFAULT_OUTPUT = (
    ROOT / "build/google_docs/student_response_link_selector_inventory.json"
)
DEFAULT_PLAN = (
    Path.home()
    / ".config/canvas-fleet-parity/cce/source-response-routes/plans"
    / "course-98060-response-routes-20260826T010619.949837Z.json"
)
EXPECTED_PLAN_SHA256 = (
    "9cc7b6f27ad03fcf947ff5e1987c8ef9fc941e2142ab7dc65d320b6c1f07e00c"
)
EXPECTED_REGISTRY_SHA256 = (
    "e33d06f8fe9a22f2be7d1c2a3346b9929ce1d0d4c0b1e433f4f37dd8b12f16d7"
)
BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060
FILE_HREF_RE = re.compile(r"/courses/(\d+)/files/(\d+)(?:/preview)?")
INJECTED_PANEL_RE = re.compile(
    r"<aside\b(?=[^>]*\bid\s*=\s*([\"'])cce-student-google-doc\1)[^>]*>"
    r".*?</aside>",
    re.IGNORECASE | re.DOTALL,
)


# These four source-spec gaps have reviewed, existing response-work PDF links.
# Support variants and rubrics on the same pages remain excluded.
MANUAL_RESPONSE_PDFS = {
    "1SW-Wk0-Day1": {
        "cce-first-week-goal-setting.pdf": (
            "build/google_docs/student_response_route_manual_content_specs.json"
        )
    },
    "1SW-Wk0-Day4": {
        "my-career-journey.pdf": (
            "build/google_docs/student_response_route_manual_content_specs.json"
        )
    },
    "1SW-Wk3-Day3": {
        "wk3-wireframe-template.pdf": (
            "build/google_docs/student_response_route_manual_content_specs.json"
        )
    },
    "1SW-Wk5-Day5": {
        "wk5-reflection-update-template.pdf": (
            "build/google_docs/student_response_route_manual_content_specs.json"
        )
    },
}


# These two response links remain the same control in the same location, but
# their PDF-specific label would be false after the target becomes a Google
# ``/copy`` URL. No other selected anchor text changes.
REVIEWED_ANCHOR_TEXT_REPLACEMENTS = {
    (
        "1SW-Wk1-Day1",
        "1sw-wk1-day1-manufacturing-cluster-tour-more-than-assembly-lines.pdf",
    ): "Open the Day 1 exit ticket",
    (
        "1SW-Wk1-Day4",
        "1sw-wk1-robots-for-crayons-action-plan.pdf",
    ): "Open the Robots for Crayons action plan",
}


# No selector below is permission to add UI. These are reviewed, exact insertion
# landmarks only if the owner later authorizes a bare one-button addition for a
# universal Google-default route.
NO_SELECTOR_INSERTION_REVIEW = {
    "1SW-Wk0-Day2": {
        "heading": "6. Move the result to your private response",
        "reason": "No response-work PDF link exists; this is the exact point where the private response begins.",
    },
    "1SW-Wk0-Day3": {
        "heading": "4. Make one connection",
        "reason": "Only English and bilingual word-bank PDFs are linked; both are excluded.",
    },
    "1SW-Wk0-Day5": {
        "heading": "2. Complete your career table",
        "reason": "The current primary response is FYF p. 5 and no response-work PDF is linked.",
    },
    "1SW-Wk1-Day2": {
        "heading": "3. Research One Manufacturing Career",
        "reason": "The checklist, career worksheet, and exit PDF exist in source evidence but are not linked on the Student Guide.",
    },
    "1SW-Wk1-Day3": {
        "heading": "4. Exit Ticket",
        "reason": "The exit response PDF exists in source evidence but is not linked on the Student Guide.",
    },
    "1SW-Wk1-Day5": {
        "heading": "3. Submit Your Private Reflection",
        "reason": "Only a private Canvas Assignment is linked; assignments are excluded from href retargeting.",
    },
    "1SW-Wk2-Day5": {
        "heading": "3. Finish the Minor 2 Reflection",
        "reason": "Only the rubric PDF is linked; rubrics are excluded and the response packet link is absent.",
    },
    "2SW-Wk1-Day2": {
        "heading": "1. Choose the Scenario and Ten Items",
        "reason": "The emergency-kit plan and exit PDF exist in source evidence but are not linked on the Student Guide.",
    },
    "2SW-Wk3-Day1": {
        "heading": "1. Meet the Health Science Cluster",
        "reason": "The primary comparison PDF link is absent; the linked route guide is reference-only.",
    },
    "2SW-Wk3-Day2": {
        "heading": "1. Compare RN and Nurse Practitioner",
        "reason": "The primary nursing comparison and exit PDFs exist in source evidence but are not linked on the Student Guide.",
    },
    "3SW-Wk1-Day1": {
        "heading": "3. Choose one role",
        "reason": "The only linked PDF is explicitly reference-only in the content specification.",
    },
    "3SW-Wk2-Day1": {
        "heading": "1. Meet the work",
        "reason": "The only linked PDF is explicitly reference-only; the private Canvas check is excluded.",
    },
    "3SW-Wk3-Day1": {
        "heading": "3. Choose and defend",
        "reason": "The only linked PDF is explicitly reference-only; the private Canvas response is excluded.",
    },
    "4SW-Wk4-Day2": {
        "heading": "1. Compare the work",
        "reason": "The linked occupation PDF is explicitly reference-only; quiz links are excluded.",
    },
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def portable_private_path(path: Path) -> str:
    resolved = path.expanduser().resolve()
    try:
        return "~/" + resolved.relative_to(Path.home().resolve()).as_posix()
    except ValueError:
        return str(resolved)


def canonical_href(value: str) -> str:
    parsed = urlsplit(value)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def response_pdf_name(source_path: str) -> str:
    path = ROOT / source_path
    stem = path.stem
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n") and "\n---\n" in text:
            front_matter = text.split("\n---\n", 1)[0]
            match = re.search(r"^slug:\s*(.+?)\s*$", front_matter, re.MULTILINE)
            if match:
                stem = match.group(1).strip()
    return f"{stem}.pdf"


class StudentBodyParser(HTMLParser):
    """Collect ordered anchors and their nearest preceding heading."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, Any]] = []
        self.headings: list[str] = []
        self._last_heading: str | None = None
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._anchor: dict[str, Any] | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag in {"h2", "h3", "h4"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag == "a":
            if self._anchor is not None:
                raise ValueError("Nested anchor tags are not supported")
            self._anchor = {
                "attrs": attributes,
                "text_parts": [],
                "context_heading": self._last_heading,
            }

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == self._heading_tag:
            heading = " ".join(" ".join(self._heading_parts).split())
            if heading:
                self.headings.append(heading)
                self._last_heading = heading
            self._heading_tag = None
            self._heading_parts = []
        if tag == "a" and self._anchor is not None:
            self._anchor["text"] = " ".join(
                " ".join(self._anchor["text_parts"]).split()
            )
            del self._anchor["text_parts"]
            self.anchors.append(self._anchor)
            self._anchor = None

    def handle_data(self, data: str) -> None:
        if self._heading_tag is not None:
            self._heading_parts.append(data)
        if self._anchor is not None:
            self._anchor["text_parts"].append(data)

    def close(self) -> None:
        super().close()
        if self._anchor is not None:
            raise ValueError("Unclosed anchor tag")
        if self._heading_tag is not None:
            raise ValueError(f"Unclosed heading tag: {self._heading_tag}")


def parse_student_body(body: str) -> StudentBodyParser:
    cleaned, replacements = INJECTED_PANEL_RE.subn("", body)
    if replacements > 1:
        raise ValueError(f"Found {replacements} injected Student Guide panels")
    parser = StudentBodyParser()
    parser.feed(cleaned)
    parser.close()
    return parser


def exact_heading_evidence(body: str, heading_text: str) -> dict[str, Any]:
    matches: list[tuple[str, str]] = []
    for match in re.finditer(
        r"<(h[1-6])\b[^>]*>.*?</\1>", body, flags=re.IGNORECASE | re.DOTALL
    ):
        element = match.group(0)
        text = " ".join(
            html.unescape(re.sub(r"<[^>]+>", " ", element)).split()
        )
        if text == heading_text:
            matches.append((match.group(1).lower(), element))
    if len(matches) != 1:
        raise ValueError(
            f"Expected one exact heading {heading_text!r}; found {len(matches)}"
        )
    tag, element = matches[0]
    return {
        "tag": tag,
        "text": heading_text,
        "element_sha256": sha256_text(element),
    }


def is_styled_button(anchor: dict[str, Any]) -> bool:
    attrs = anchor["attrs"]
    style = attrs.get("style", "").lower().replace(" ", "")
    classes = attrs.get("class", "").lower()
    return (
        "display:inline-block" in style
        and "padding:" in style
        and ("background:" in style or "background-color:" in style)
    ) or "button" in classes


def source_line_candidates(path: Path, anchor_text: str, filename: str) -> list[int]:
    if not path.is_file():
        return []
    escaped = html.escape(anchor_text, quote=False)
    candidates: list[int] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if anchor_text in line or escaped in line or filename in line:
            candidates.append(number)
    return sorted(set(candidates))


def load_token() -> str:
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    return token


def load_course_files(token: str) -> dict[int, dict[str, Any]]:
    files: dict[int, dict[str, Any]] = {}
    url: str | None = f"{BASE}/api/v1/courses/{COURSE_ID}/files"
    params: dict[str, int] | None = {"per_page": 100}
    with httpx.Client(
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
        follow_redirects=True,
    ) as client:
        while url:
            response = client.get(url, params=params)
            response.raise_for_status()
            params = None
            for record in response.json():
                files[int(record["id"])] = record
            url = response.links.get("next", {}).get("url")
    return files


def response_sources(content_row: dict[str, Any]) -> dict[str, str]:
    day_key = content_row["day_key"]
    if content_row["manual_spec"]:
        return dict(MANUAL_RESPONSE_PDFS.get(day_key, {}))

    disposition = content_row["source_disposition"]
    included = set(disposition["included_response_artifacts"])
    excluded = set(disposition["included_reference_response_artifacts"])
    excluded.update(disposition["compact_student_rubrics"])
    excluded.update(disposition["excluded_reference_cards"])
    excluded.update(disposition["excluded_nonresponse_artifacts"])
    excluded.update(disposition["excluded_teacher_artifacts"])
    excluded.update(disposition["support_only_variants"])
    response_paths = sorted(included - excluded)
    return {response_pdf_name(path): path for path in response_paths}


def exit_sources(route: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for record in route["source"]["linked_printable_sources"]:
        path = record.get("path")
        if isinstance(path, str) and path.startswith("docs/resources/exit-tickets/"):
            result[Path(path).name] = path
    return result


def build_payload(plan_path: Path, files: dict[int, dict[str, Any]]) -> dict[str, Any]:
    plan_hash = sha256_path(plan_path)
    if plan_hash != EXPECTED_PLAN_SHA256:
        raise ValueError(
            f"Immutable source plan hash mismatch: {plan_hash} != {EXPECTED_PLAN_SHA256}"
        )
    registry_hash = sha256_path(REGISTRY)
    if registry_hash != EXPECTED_REGISTRY_SHA256:
        raise ValueError(
            f"Reviewed route registry hash mismatch: {registry_hash} != {EXPECTED_REGISTRY_SHA256}"
        )

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    registry_payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    content_payload = json.loads(CONTENT_SPECS.read_text(encoding="utf-8"))
    routes = {row["day_key"]: row for row in registry_payload["routes"]}
    content = {row["day_key"]: row for row in content_payload["days"]}
    student_targets = {
        row["day_key"]: row
        for row in plan["targets"]
        if row.get("role") == "student"
    }
    if len(routes) != 180 or len(content) != 180 or len(student_targets) != 180:
        raise ValueError("Expected 180 routes, content specs, and Student Guide targets")

    days: list[dict[str, Any]] = []
    for day_key in sorted(routes, key=lambda value: tuple(map(int, re.findall(r"\d+", value)))):
        route = routes[day_key]
        content_row = content[day_key]
        target = student_targets[day_key]
        source_pdfs = response_sources(content_row)
        exit_pdfs = exit_sources(route)
        desired = {**source_pdfs, **exit_pdfs}

        parsed_body = parse_student_body(target["before_body"])
        all_anchors = [
            anchor for anchor in parsed_body.anchors if anchor["attrs"].get("href")
        ]
        selectors: list[dict[str, Any]] = []
        live_pdf_links: list[dict[str, Any]] = []
        selected_filenames: set[str] = set()

        template_record = route["source"]["student_template"]
        builder_record = route["source"]["canvas_builder"]
        template_path = ROOT / template_record["path"]
        builder_path = ROOT / builder_record["path"]
        per_day_template = "-day" in template_path.name
        authored_record = template_record if per_day_template else builder_record
        authored_path = ROOT / authored_record["path"]

        for anchor_index, anchor in enumerate(all_anchors):
            href = anchor["attrs"].get("href", "")
            match = FILE_HREF_RE.search(href)
            if not match or int(match.group(1)) != COURSE_ID:
                continue
            file_id = int(match.group(2))
            file_record = files.get(file_id)
            if not file_record:
                raise ValueError(f"Canvas file {file_id} is missing for {day_key}")
            filename = file_record.get("filename") or file_record.get("display_name")
            if not isinstance(filename, str):
                raise ValueError(f"Canvas file {file_id} has no filename")
            if filename.lower().endswith(".pdf"):
                live_pdf_links.append(
                    {
                        "anchor_text": anchor["text"],
                        "canonical_href": canonical_href(href),
                        "complete_href_sha256": sha256_text(href),
                        "file_id": file_id,
                        "filename": filename,
                    }
                )
            if filename not in desired:
                continue
            if filename in selected_filenames:
                raise ValueError(
                    f"{day_key} links the same selected PDF more than once: {filename}"
                )
            selected_filenames.add(filename)
            classification = (
                "daily_exit_ticket_pdf" if filename in exit_pdfs else "student_response_work_pdf"
            )
            anchor_text = anchor["text"]
            context_heading = anchor["context_heading"]
            signature = {
                "anchor_text": anchor_text,
                "canonical_old_href": canonical_href(href),
                "context_heading": context_heading,
                "expected_filename": filename,
                "style": anchor["attrs"].get("style"),
            }
            selectors.append(
                {
                    "selector_id": sha256_text(
                        f"{day_key}\n{anchor_index}\n{anchor_text}\n{filename}"
                    )[:20],
                    "anchor_index_without_injected_panel": anchor_index,
                    "anchor_text": anchor_text,
                    "replacement_anchor_text": REVIEWED_ANCHOR_TEXT_REPLACEMENTS.get(
                        (day_key, filename)
                    ),
                    "classification": classification,
                    "context_heading": context_heading,
                    "expected_canvas_file_id": file_id,
                    "expected_canvas_filename": filename,
                    "expected_old_href_canonical": canonical_href(href),
                    "expected_old_href_complete_sha256": sha256_text(href),
                    "observed_href_had_query": bool(urlsplit(href).query),
                    "is_styled_button": is_styled_button(anchor),
                    "normalized_anchor_signature_sha256": sha256_text(
                        json.dumps(signature, ensure_ascii=False, sort_keys=True)
                    ),
                    "replacement_href": route["google_doc"]["copy_url"],
                    "source_evidence": {
                        "artifact_path": desired[filename],
                        "artifact_sha256": (
                            sha256_path(ROOT / desired[filename])
                            if (ROOT / desired[filename]).is_file()
                            else None
                        ),
                        "href_authored_in": (
                            "student_template" if per_day_template else "canvas_builder"
                        ),
                        "authored_path": authored_record["path"],
                        "authored_path_sha256": authored_record["sha256"],
                        "authored_line_candidates": source_line_candidates(
                            authored_path, anchor_text, filename
                        ),
                        "canvas_builder_path": builder_record["path"],
                        "canvas_builder_sha256": builder_record["sha256"],
                        "student_template_path": template_record["path"],
                        "student_template_sha256": template_record["sha256"],
                    },
                }
            )

        selectors.sort(key=lambda row: row["anchor_index_without_injected_panel"])
        missing_desired = sorted(set(desired) - selected_filenames)
        if selectors:
            no_selector_review = None
        else:
            reviewed = NO_SELECTOR_INSERTION_REVIEW.get(day_key)
            if not reviewed:
                raise ValueError(f"Missing no-selector review for {day_key}")
            headings = set(parsed_body.headings)
            if reviewed["heading"] not in headings:
                raise ValueError(
                    f"Reviewed insertion heading missing for {day_key}: {reviewed['heading']}"
                )
            if missing_desired:
                reason_code = "response_pdf_exists_in_source_but_is_not_linked"
            elif live_pdf_links:
                reason_code = "only_excluded_pdf_links_are_present"
            else:
                reason_code = "no_response_work_pdf_link_is_present"
            no_selector_review = {
                "reason_code": reason_code,
                "reason": reviewed["reason"],
                "unlinked_response_pdf_filenames": missing_desired,
                "suggested_bare_button_insertion_if_separately_approved": {
                    "authorization": "not_authorized_by_href_only_rule",
                    "insert_immediately_after_heading": reviewed["heading"],
                    "heading_signature": exact_heading_evidence(
                        target["before_body"], reviewed["heading"]
                    ),
                    "shape": "one existing-style anchor only; no panel or explanatory prose",
                    "replacement_href": route["google_doc"]["copy_url"],
                },
            }

        days.append(
            {
                "route_id": route["route_id"],
                "day_key": day_key,
                "student_page": {
                    "page_id": target["page_id"],
                    "page_url": target["page_url"],
                    "expected_before_body_sha256": target[
                        "observed_before_body_sha256"
                    ],
                    "published_readback": target["observed_published"],
                },
                "google_doc_copy_url": route["google_doc"]["copy_url"],
                "selectors": selectors,
                "selector_count": len(selectors),
                "no_selector_review": no_selector_review,
                "excluded_live_pdf_links": [
                    row for row in live_pdf_links if row["filename"] not in selected_filenames
                ],
            }
        )

    multiplicity = Counter(row["selector_count"] for row in days)
    selector_count = sum(row["selector_count"] for row in days)
    classification_counts = Counter(
        selector["classification"]
        for row in days
        for selector in row["selectors"]
    )
    authored_counts = Counter(
        selector["source_evidence"]["href_authored_in"]
        for row in days
        for selector in row["selectors"]
    )
    authored_files = {
        selector["source_evidence"]["authored_path"]
        for row in days
        for selector in row["selectors"]
    }
    selected_file_ids = {
        selector["expected_canvas_file_id"]
        for row in days
        for selector in row["selectors"]
    }
    summary = {
        "day_count": len(days),
        "selector_count": selector_count,
        "days_with_selectors": sum(bool(row["selectors"]) for row in days),
        "days_without_selectors": sum(not row["selectors"] for row in days),
        "selector_multiplicity": {
            str(count): multiplicity[count] for count in sorted(multiplicity)
        },
        "classification_counts": dict(sorted(classification_counts.items())),
        "authoring_layer_counts": dict(sorted(authored_counts.items())),
        "authored_source_file_count": len(authored_files),
        "authored_source_files": sorted(authored_files),
        "reviewed_anchor_text_replacement_count": sum(
            selector["replacement_anchor_text"] is not None
            for row in days
            for selector in row["selectors"]
        ),
    }
    expected_summary = {
        "day_count": 180,
        "selector_count": 185,
        "days_with_selectors": 166,
        "days_without_selectors": 14,
        "selector_multiplicity": {"0": 14, "1": 151, "2": 12, "3": 2, "4": 1},
        "classification_counts": {
            "daily_exit_ticket_pdf": 8,
            "student_response_work_pdf": 177,
        },
        "reviewed_anchor_text_replacement_count": 2,
    }
    for key, expected in expected_summary.items():
        if summary[key] != expected:
            raise ValueError(f"Selector invariant drift for {key}: {summary[key]} != {expected}")

    return {
        "schema_version": 1,
        "artifact": "CCE reviewed Student Guide response-work PDF href selectors",
        "review_status": "reviewed",
        "mutation_contract": {
            "student_change": "Replace only each selected anchor href with the matching Google Doc /copy URL.",
            "preserve": "Style, position, context, and every non-href byte remain unchanged except two reviewed PDF-specific anchor-label corrections.",
            "reviewed_anchor_text_replacements": 2,
            "forbidden_targets": [
                "assignments",
                "quizzes",
                "rubrics",
                "word banks",
                "support variants",
                "reference-only PDFs",
            ],
            "no_selector_days": "Do not add UI under this href-only contract.",
            "publication": "Never send or change publication fields.",
        },
        "privacy": {
            "canvas_verifier_queries_committed": False,
            "complete_observed_href_evidence": "SHA-256 only",
        },
        "inputs": {
            "immutable_canvas_plan": {
                "path": portable_private_path(plan_path),
                "sha256": plan_hash,
            },
            "reviewed_route_registry": {
                "path": repo_path(REGISTRY),
                "sha256": registry_hash,
            },
            "content_specs": {
                "path": repo_path(CONTENT_SPECS),
                "sha256": sha256_path(CONTENT_SPECS),
            },
            "manual_content_specs": {
                "path": repo_path(MANUAL_CONTENT_SPECS),
                "sha256": sha256_path(MANUAL_CONTENT_SPECS),
            },
            "canvas_course_id": COURSE_ID,
            "selected_canvas_file_id_count": len(selected_file_ids),
        },
        "summary": summary,
        "days": days,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    plan_path = args.plan.expanduser().resolve()
    output = args.output
    if not output.is_absolute():
        output = (ROOT / output).resolve()
    token = load_token()
    payload = build_payload(plan_path, load_course_files(token))
    rendered = stable_json(payload)
    if args.stdout:
        sys.stdout.write(rendered)
        return 0
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print(f"Selector inventory is missing or stale: {output}", file=sys.stderr)
            return 1
        print(
            "Selector inventory: PASS "
            f"days={payload['summary']['day_count']} "
            f"selectors={payload['summary']['selector_count']}"
        )
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {payload['summary']['selector_count']} selectors for "
        f"{payload['summary']['day_count']} days to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
