#!/usr/bin/env python3
"""Verify the one-button Google-copy contract in Canvas authoring sources.

This verifier is local and read-only. It proves that every reviewed CCE day has
one response action, that only the reviewed PDF anchors were retargeted, and
that the generic response-route panel and its process prose are absent.
"""

from __future__ import annotations

import ast
import html
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "build/google_docs/student_response_link_selector_inventory.json"
REGISTRY = ROOT / "build/google_docs/student_response_route_registry.json"
COPY_URL_RE = re.compile(
    r"https://docs\.google\.com/document/d/[A-Za-z0-9_-]+/copy"
)
FORBIDDEN_STUDENT_SOURCE = (
    'id="cce-student-google-doc"',
    "Type in your copy and submit or share it the way your teacher directs",
    "Choose one response home before class",
    "Type today’s work in Google Docs",
    "Complete this work in one place only",
)


class SourceContractError(RuntimeError):
    """The persisted authoring source no longer matches the reviewed contract."""


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceContractError(f"Expected a JSON object: {path}")
    return value


def visible_text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def anchor_records(source: str) -> list[dict[str, str]]:
    records = []
    for match in re.finditer(r"<a\b[^>]*>.*?</a>", source, re.I | re.S):
        href = re.search(
            r'\bhref\s*=\s*(["\'])(.*?)\1', match.group(0), re.I | re.S
        )
        if href:
            records.append(
                {
                    "href": html.unescape(href.group(2)),
                    "text": visible_text(match.group(0)),
                    "open_tag": match.group(0).split(">", 1)[0] + ">",
                }
            )
    return records


def literal_mapping(tree: ast.AST, name: str) -> dict[int, str]:
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if not isinstance(node.value, ast.Dict):
            raise SourceContractError(f"{name} must be a literal dictionary")
        value: dict[int, str] = {}
        for key, item in zip(node.value.keys, node.value.values):
            if not (
                isinstance(key, ast.Constant)
                and isinstance(key.value, int)
                and isinstance(item, ast.Constant)
                and isinstance(item.value, str)
            ):
                raise SourceContractError(f"{name} must contain literal day-to-URL entries")
            value[key.value] = item.value
        matches.append(value)
    if len(matches) != 1:
        raise SourceContractError(f"Expected one {name} mapping; found {len(matches)}")
    return matches[0]


def literal_calls(tree: ast.AST, name: str) -> Counter[tuple[int, str]]:
    result: Counter[tuple[int, str]] = Counter()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == name
            and len(node.args) >= 2
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, int)
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        ):
            continue
        result[(node.args[0].value, node.args[1].value)] += 1
    return result


def verify() -> dict[str, int]:
    inventory = load_json(INVENTORY)
    registry_payload = load_json(REGISTRY)
    if inventory.get("review_status") != "reviewed":
        raise SourceContractError("Selector inventory is not reviewed")
    if registry_payload.get("review_status") != "reviewed":
        raise SourceContractError("Route registry is not reviewed")

    days = inventory.get("days", [])
    routes = registry_payload.get("routes", [])
    route_by_key = {row["day_key"]: row for row in routes}
    if len(days) != 180 or len(routes) != 180 or len(route_by_key) != 180:
        raise SourceContractError("Expected 180 reviewed day routes")
    if {row["day_key"] for row in days} != set(route_by_key):
        raise SourceContractError("Inventory and registry day keys differ")

    template_expected: dict[str, Counter[tuple[str, str]]] = {}
    template_no_anchor: dict[str, tuple[str, str]] = {}
    builder_links: dict[str, Counter[tuple[int, str]]] = {}
    builder_buttons: dict[str, Counter[tuple[int, str]]] = {}
    source_paths: set[Path] = set()

    for day in days:
        day_key = day["day_key"]
        route = route_by_key[day_key]
        source_paths.add(ROOT / route["source"]["student_template"]["path"])
        copy_url = route["google_doc"]["copy_url"]
        if copy_url != day["google_doc_copy_url"] or not COPY_URL_RE.fullmatch(copy_url):
            raise SourceContractError(f"{day_key}: registry/inventory copy URL mismatch")
        day_number = int(day_key.rsplit("Day", 1)[1])
        selectors = day["selectors"]
        if selectors:
            for selector in selectors:
                label = selector.get("replacement_anchor_text") or selector["anchor_text"]
                evidence = selector["source_evidence"]
                path = evidence["authored_path"]
                source_paths.add(ROOT / path)
                if evidence["href_authored_in"] == "student_template":
                    template_expected.setdefault(path, Counter())[(copy_url, label)] += 1
                elif evidence["href_authored_in"] == "canvas_builder":
                    builder_links.setdefault(path, Counter())[(day_number, label)] += 1
                else:
                    raise SourceContractError(f"{day_key}: unknown authoring layer")
        else:
            student_template = route["source"]["student_template"]["path"]
            lesson_title = route["title"].rsplit(" | ", 1)[-1]
            label = f"Make your copy: {lesson_title}"
            if "-day" in Path(student_template).name:
                template_no_anchor[student_template] = (copy_url, label)
                source_paths.add(ROOT / student_template)
            else:
                builder = route["source"]["canvas_builder"]["path"]
                builder_buttons.setdefault(builder, Counter())[(day_number, label)] += 1
                source_paths.add(ROOT / builder)

    template_selector_count = 0
    template_button_count = 0
    for path, expected in template_expected.items():
        source = (ROOT / path).read_text(encoding="utf-8")
        records = anchor_records(source)
        actual = Counter(
            (record["href"], record["text"])
            for record in records
            if COPY_URL_RE.fullmatch(record["href"])
        )
        for key, count in expected.items():
            if actual[key] != count:
                raise SourceContractError(
                    f"{path}: expected {count} reviewed anchors {key}; found {actual[key]}"
                )
            selected = [
                record for record in records
                if (record["href"], record["text"]) == key
            ]
            if any(
                attribute in record["open_tag"]
                for record in selected
                for attribute in ("data-api-endpoint", "data-api-returntype")
            ):
                raise SourceContractError(f"{path}: stale Canvas file metadata remains")
        template_selector_count += sum(expected.values())

    for path, (copy_url, label) in template_no_anchor.items():
        source = (ROOT / path).read_text(encoding="utf-8")
        matches = [
            record for record in anchor_records(source)
            if record["href"] == copy_url and record["text"] == label
        ]
        if len(matches) != 1 or "background:#1f617a" not in matches[0]["open_tag"]:
            raise SourceContractError(f"{path}: missing compact teal point-of-use button")
        template_button_count += 1

    builder_paths = sorted(set(builder_links) | set(builder_buttons))
    builder_selector_count = 0
    builder_button_count = 0
    for path in builder_paths:
        source_path = ROOT / path
        source_paths.add(source_path)
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        expected_routes = sorted(
            (row for row in routes if row["source"]["canvas_builder"]["path"] == path),
            key=lambda row: row["day"],
        )
        expected_mapping = {
            row["day"]: row["google_doc"]["copy_url"] for row in expected_routes
        }
        if literal_mapping(tree, "STUDENT_GOOGLE_COPY_URLS") != expected_mapping:
            raise SourceContractError(f"{path}: day-to-copy URL mapping drift")
        actual_links = literal_calls(tree, "student_copy_link")
        actual_buttons = literal_calls(tree, "student_copy_button")
        if actual_links != builder_links.get(path, Counter()):
            raise SourceContractError(f"{path}: reviewed response-link call set drift")
        if actual_buttons != builder_buttons.get(path, Counter()):
            raise SourceContractError(f"{path}: point-of-use button call set drift")
        builder_selector_count += sum(actual_links.values())
        builder_button_count += sum(actual_buttons.values())

    for path in source_paths:
        source = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STUDENT_SOURCE:
            if forbidden in source:
                raise SourceContractError(
                    f"{path.relative_to(ROOT)}: forbidden generic route UI/prose remains"
                )

    summary = {
        "route_count": len(days),
        "selector_count": template_selector_count + builder_selector_count,
        "template_selector_count": template_selector_count,
        "builder_selector_count": builder_selector_count,
        "point_of_use_button_count": template_button_count + builder_button_count,
        "template_button_count": template_button_count,
        "builder_button_count": builder_button_count,
    }
    expected_summary = {
        "route_count": 180,
        "selector_count": 185,
        "template_selector_count": 48,
        "builder_selector_count": 137,
        "point_of_use_button_count": 14,
        "template_button_count": 10,
        "builder_button_count": 4,
    }
    if summary != expected_summary:
        raise SourceContractError(f"Source coverage drift: {summary}")
    return summary


if __name__ == "__main__":
    result = verify()
    print(
        "STUDENT RESPONSE SOURCE VERIFY: PASS "
        f"routes={result['route_count']} selectors={result['selector_count']} "
        f"point_of_use_buttons={result['point_of_use_button_count']}"
    )
