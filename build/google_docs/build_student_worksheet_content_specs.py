#!/usr/bin/env python3
"""Compose deterministic semantic content specs for all 180 CCE student Docs.

This is a local-only authoring step.  It reads the guarded source-spec draft,
the seven reviewed manual route/content specs, current worksheet Markdown, and
current Canvas builder/student-template text.  It never imports a builder and
never calls Canvas, Google Drive, or any network service.

The output is renderer-neutral JSON.  Markdown response markers become native
table cells, response boxes, checklists, and page breaks instead of underline
art or stale OneNote placeholders.

Usage:

    python3 build/google_docs/build_student_worksheet_content_specs.py
    python3 build/google_docs/build_student_worksheet_content_specs.py --strict
    python3 build/google_docs/build_student_worksheet_content_specs.py --check --strict
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
GOOGLE_DOCS_ROOT = ROOT / "build" / "google_docs"
SOURCE_SPEC = GOOGLE_DOCS_ROOT / "student_worksheet_source_specs.draft.json"
ROUTE_MANUAL_SPEC = GOOGLE_DOCS_ROOT / "student_response_route_manual_specs.json"
CONTENT_MANUAL_SPEC = (
    GOOGLE_DOCS_ROOT / "student_response_route_manual_content_specs.json"
)
DEFAULT_OUTPUT = GOOGLE_DOCS_ROOT / "student_worksheet_content_specs.draft.json"

DAY_KEY_RE = re.compile(r"^(?P<sw>[1-6])SW-Wk(?P<week>\d+)-Day(?P<day>[1-5])$")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CHECK_RE = re.compile(r"^\s*[-*]\s+\[\s*\]\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*[-*+]\s+(.+?)\s*$")
ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+(.+?)\s*$")
LINES_RE = re.compile(r"^\[\[lines:\s*(\d+(?:\.\d+)?)\s*\]\]$", re.I)
BOX_RE = re.compile(r"^\[\[box:\s*(\d+(?:\.\d+)?)\s*\]\]$", re.I)
INLINE_RESPONSE_RE = re.compile(r"_{3,}")
TABLE_SEPARATOR_RE = re.compile(
    r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$"
)
HTML_TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_FORMAT_RE = re.compile(r"(?<!\\)[*_`]+")

STALE_PATTERNS = {
    "legacy_drive_path": re.compile(r"(?<!VILS27/)27 CCR Planning", re.I),
    "stale_projected_exit_placeholder": re.compile(
        r"refer to the physical or projected exit ticket", re.I
    ),
    "stale_specific_prompts_placeholder": re.compile(
        r"specific prompts? (?:will be|are) (?:provided|shown)", re.I
    ),
    "todo_placeholder": re.compile(r"\b(?:TODO|TBD|LOREM IPSUM)\b", re.I),
    "link_coming_soon": re.compile(r"link coming soon", re.I),
}

TARGET_BUILDER_FIELDS = {
    "TITLE",
    "PURPOSE",
    "EXIT",
    "DONE",
    "SUPPORT",
    "LANGUAGE",
    "STUDENT_DOL",
    "SHOW",
    "SHOW_LEARNING",
}


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        clean = re.sub(r"\s+", " ", value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            output.append(clean)
    return output


def strip_markdown(value: str) -> str:
    value = HTML_TAG_RE.sub(" ", value)
    value = MARKDOWN_FORMAT_RE.sub("", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    lines = match.group(0).splitlines()[1:-1]
    for line in lines:
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    return metadata, text[match.end() :]


def split_pipe_row(line: str) -> list[str]:
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in value:
        if char == "\\" and not escaped:
            escaped = True
            current.append(char)
            continue
        if char == "|" and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        escaped = False
    cells.append("".join(current).strip())
    return cells


def response_cell(text: str, *, header: bool = False) -> dict[str, Any]:
    clean = text.strip()
    response = not header and (not clean or bool(INLINE_RESPONSE_RE.search(clean)))
    record: dict[str, Any] = {"text": clean}
    if response:
        record["response"] = True
        record["lines"] = 2
    return record


def inline_response_block(text: str) -> dict[str, Any]:
    segments: list[dict[str, Any]] = []
    cursor = 0
    for match in INLINE_RESPONSE_RE.finditer(text):
        if match.start() > cursor:
            segments.append({"text": text[cursor : match.start()]})
        length = match.end() - match.start()
        segments.append(
            {
                "response": True,
                "width": "long" if length >= 30 else "medium" if length >= 15 else "short",
            }
        )
        cursor = match.end()
    if cursor < len(text):
        segments.append({"text": text[cursor:]})
    return {"type": "inline_response", "segments": segments}


def paragraph_block(text: str, style: str | None = None) -> dict[str, Any]:
    text = re.sub(r"\s+", " ", text).strip()
    if INLINE_RESPONSE_RE.search(text):
        block = inline_response_block(text)
    else:
        block = {"type": "paragraph", "text": text}
    if style:
        block["style"] = style
    return block


@dataclass
class HtmlNode:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)
    parent: "HtmlNode | None" = None


class HtmlTreeParser(HTMLParser):
    VOID = {"br", "hr", "img", "input", "meta", "link", "col"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = HtmlNode("root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = HtmlNode(tag.lower(), {key: value or "" for key, value in attrs})
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        if node.tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag.lower() and tag.lower() not in self.VOID:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def node_text(node: HtmlNode | str) -> str:
    if isinstance(node, str):
        return node
    pieces: list[str] = []
    for child in node.children:
        pieces.append(node_text(child))
        if isinstance(child, HtmlNode) and child.tag in {"br", "p", "li", "tr", "div"}:
            pieces.append(" ")
    return re.sub(r"\s+", " ", "".join(pieces)).strip()


def find_nodes(node: HtmlNode, tags: set[str]) -> list[HtmlNode]:
    found: list[HtmlNode] = []
    for child in node.children:
        if not isinstance(child, HtmlNode):
            continue
        if child.tag in tags:
            found.append(child)
        found.extend(find_nodes(child, tags))
    return found


def html_table_block(node: HtmlNode) -> dict[str, Any]:
    rows: list[list[dict[str, Any]]] = []
    header_rows = 0
    for row in find_nodes(node, {"tr"}):
        cells = [
            child
            for child in row.children
            if isinstance(child, HtmlNode) and child.tag in {"th", "td"}
        ]
        if not cells:
            continue
        is_header = all(cell.tag == "th" for cell in cells)
        if is_header and not rows:
            header_rows += 1
        rows.append([response_cell(node_text(cell), header=is_header) for cell in cells])
    return {"type": "table", "native": True, "header_rows": header_rows, "rows": rows}


def html_node_to_blocks(node: HtmlNode) -> list[dict[str, Any]]:
    if node.tag in {"p", "blockquote"}:
        text = node_text(node)
        return [paragraph_block(text, "callout" if node.tag == "blockquote" else None)] if text else []
    if node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        text = node_text(node)
        return [{"type": "heading", "level": int(node.tag[1]), "text": text}] if text else []
    if node.tag in {"ul", "ol"}:
        items = [node_text(item) for item in find_nodes(node, {"li"})]
        items = [item for item in items if item]
        return [{"type": "list", "ordered": node.tag == "ol", "items": items}] if items else []
    if node.tag == "table":
        block = html_table_block(node)
        return [block] if block["rows"] else []
    if node.tag == "hr":
        return [{"type": "divider"}]
    output: list[dict[str, Any]] = []
    for child in node.children:
        if isinstance(child, HtmlNode):
            output.extend(html_node_to_blocks(child))
    return output


def html_fragment_to_blocks(fragment: str) -> list[dict[str, Any]]:
    parser = HtmlTreeParser()
    parser.feed(fragment)
    return html_node_to_blocks(parser.root)


def markdown_to_blocks(markdown: str) -> list[dict[str, Any]]:
    """Parse the worksheet Markdown subset without executing extensions."""

    _, body = parse_front_matter(markdown)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    lines = body.splitlines()
    blocks: list[dict[str, Any]] = []
    index = 0

    def special(at: int) -> bool:
        if at >= len(lines):
            return True
        raw = lines[at].strip()
        if not raw:
            return True
        if (
            HEADING_RE.match(raw)
            or LINES_RE.match(raw)
            or BOX_RE.match(raw)
            or raw.lower() == "[[pagebreak]]"
            or raw in {"---", "***", "___"}
            or CHECK_RE.match(raw)
            or BULLET_RE.match(raw)
            or ORDERED_RE.match(raw)
            or raw.lower().startswith("<table")
        ):
            return True
        return at + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[at + 1]) is not None

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue

        heading = HEADING_RE.match(stripped)
        if heading:
            blocks.append(
                {"type": "heading", "level": len(heading.group(1)), "text": heading.group(2).strip()}
            )
            index += 1
            continue

        if stripped.lower() == "[[pagebreak]]":
            blocks.append({"type": "page_break"})
            index += 1
            continue

        lines_marker = LINES_RE.match(stripped)
        if lines_marker:
            blocks.append(
                {
                    "type": "response_box",
                    "prompt": None,
                    "lines": max(1, int(float(lines_marker.group(1)))),
                    "full_width": True,
                }
            )
            index += 1
            continue

        box_marker = BOX_RE.match(stripped)
        if box_marker:
            height = float(box_marker.group(1))
            blocks.append(
                {
                    "type": "response_box",
                    "prompt": None,
                    "height_inches": height,
                    "mode": "drawing_or_text" if height >= 2 else "text",
                    "full_width": True,
                }
            )
            index += 1
            continue

        if stripped in {"---", "***", "___"}:
            blocks.append({"type": "divider"})
            index += 1
            continue

        if stripped.lower().startswith("<table"):
            html_lines = [raw]
            index += 1
            while index < len(lines):
                html_lines.append(lines[index])
                if "</table>" in lines[index].lower():
                    index += 1
                    break
                index += 1
            blocks.extend(html_fragment_to_blocks("\n".join(html_lines)))
            continue

        if index + 1 < len(lines) and TABLE_SEPARATOR_RE.match(lines[index + 1]):
            raw_rows = [raw]
            index += 2
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                raw_rows.append(lines[index])
                index += 1
            rows: list[list[dict[str, Any]]] = []
            for row_index, row in enumerate(raw_rows):
                rows.append(
                    [response_cell(cell, header=row_index == 0) for cell in split_pipe_row(row)]
                )
            blocks.append({"type": "table", "native": True, "header_rows": 1, "rows": rows})
            continue

        if CHECK_RE.match(stripped):
            items: list[str] = []
            while index < len(lines):
                match = CHECK_RE.match(lines[index].strip())
                if not match:
                    break
                items.append(match.group(1).strip())
                index += 1
            blocks.append({"type": "checklist", "items": items})
            continue

        bullet = BULLET_RE.match(stripped)
        if bullet:
            items: list[str] = []
            while index < len(lines):
                match = BULLET_RE.match(lines[index].strip())
                if not match or CHECK_RE.match(lines[index].strip()):
                    break
                items.append(match.group(1).strip())
                index += 1
            blocks.append({"type": "list", "ordered": False, "items": items})
            continue

        ordered = ORDERED_RE.match(stripped)
        if ordered:
            items = []
            while index < len(lines):
                match = ORDERED_RE.match(lines[index].strip())
                if not match:
                    break
                items.append(match.group(1).strip())
                index += 1
            blocks.append({"type": "list", "ordered": True, "items": items})
            continue

        style = "callout" if stripped.startswith(">") else None
        paragraph_lines = [stripped.lstrip("> ")]
        index += 1
        while index < len(lines) and not special(index):
            paragraph_lines.append(lines[index].strip().lstrip("> "))
            index += 1
        blocks.append(paragraph_block(" ".join(paragraph_lines), style))

    return blocks


def block_has_response(block: dict[str, Any]) -> bool:
    if block.get("type") in {"response_box", "conditional_response_box", "screen_canvas", "inline_response"}:
        return True
    if block.get("type") == "table":
        return any(
            cell.get("response")
            for row in block.get("rows", [])
            for cell in row
            if isinstance(cell, dict)
        )
    if block.get("type") == "checklist":
        return bool(block.get("items"))
    return False


def block_has_writable_response(block: dict[str, Any]) -> bool:
    if block.get("type") in {
        "response_box",
        "conditional_response_box",
        "screen_canvas",
        "inline_response",
    }:
        return True
    if block.get("type") == "table":
        return any(
            cell.get("response")
            for row in block.get("rows", [])
            for cell in row
            if isinstance(cell, dict)
        )
    return False


def count_tables(blocks: list[dict[str, Any]]) -> int:
    return sum(block.get("type") == "table" for block in blocks)


def count_source_tables(markdown: str) -> int:
    _, body = parse_front_matter(markdown)
    lines = body.splitlines()
    markdown_tables = sum(
        1
        for index in range(len(lines) - 1)
        if "|" in lines[index] and TABLE_SEPARATOR_RE.match(lines[index + 1])
    )
    html_tables = len(re.findall(r"<table\b", body, flags=re.I))
    return markdown_tables + html_tables


def text_values(block: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("text", "prompt", "title", "condition"):
        value = block.get(key)
        if isinstance(value, str):
            values.append(value)
    for key in ("items", "fields"):
        value = block.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if isinstance(item, str))
    if block.get("type") == "table":
        values.extend(
            str(cell.get("text", ""))
            for row in block.get("rows", [])
            for cell in row
            if isinstance(cell, dict)
        )
    if block.get("type") == "inline_response":
        values.extend(
            str(segment.get("text", ""))
            for segment in block.get("segments", [])
            if isinstance(segment, dict)
        )
    return values


def extract_language_support(
    blocks: list[dict[str, Any]], *, include_strategies: bool = False
) -> dict[str, list[str]]:
    word_bank: list[str] = []
    sentence_stems: list[str] = []
    strategies: list[str] = []
    for block in blocks:
        for raw in text_values(block):
            text = strip_markdown(raw)
            lowered = text.lower()
            is_word_bank = (
                "word bank" in lowered
                or "choice bank" in lowered
                or "banco de palabras" in lowered
                or "spanish terms" in lowered
                or "vocabulario" in lowered
                or "términos" in lowered
                or bool(re.search(r"\b[^=·]{2,30}\s*=\s*[^=·]{2,30}(?:\s*·|$)", text))
            )
            is_stem = (
                "use this frame" in lowered
                or "use these frames" in lowered
                or "complete frame" in lowered
                or "sentence stem" in lowered
                or "sentence frame" in lowered
                or "sentence starter" in lowered
                or ("_____" in raw and (" / " in raw or "because" in lowered or "porque" in lowered))
                or (include_strategies and bool(re.search(r"\[[^\]]+\]", raw)))
            )
            if is_word_bank:
                word_bank.append(text)
            if is_stem:
                sentence_stems.append(text)
            if include_strategies and text and not is_word_bank and not is_stem:
                strategies.append(text)
    return {
        "word_bank": stable_unique(word_bank),
        "sentence_stems": stable_unique(sentence_stems),
        "strategies": stable_unique(strategies),
    }


def merge_language_support(*supports: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "word_bank": stable_unique(
            str(item) for support in supports for item in support.get("word_bank", [])
        ),
        "sentence_stems": stable_unique(
            str(item) for support in supports for item in support.get("sentence_stems", [])
        ),
        "strategies": stable_unique(
            str(item) for support in supports for item in support.get("strategies", [])
        ),
    }


def compact_rubric(title: str, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table = next((block for block in blocks if block.get("type") == "table"), None)
    if not table or len(table.get("rows", [])) < 2:
        return []
    rows = table["rows"]
    header = [strip_markdown(cell.get("text", "")) for cell in rows[0]]
    best_index = next(
        (
            index
            for index, value in enumerate(header)
            if index > 0 and ("master" in value.lower() or re.search(r"\b4\b", value))
        ),
        1 if len(header) > 1 else 0,
    )
    items: list[str] = []
    for row in rows[1:]:
        if not row:
            continue
        criterion = strip_markdown(row[0].get("text", ""))
        descriptor = (
            strip_markdown(row[best_index].get("text", ""))
            if best_index < len(row)
            else ""
        )
        if criterion:
            items.append(f"{criterion}: {descriptor}" if descriptor else criterion)
    if not items:
        return []
    return [
        {"type": "heading", "level": 2, "text": f"Self-check: {title}"},
        {"type": "checklist", "items": items, "source_kind": "student_rubric_compact"},
    ]


def static_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        pieces: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                pieces.append(value.value)
            else:
                return None
        return "".join(pieces)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = static_string(node.left)
        right = static_string(node.right)
        return left + right if left is not None and right is not None else None
    return None


def dict_string_fields(node: ast.Dict) -> dict[str, str]:
    fields: dict[str, str] = {}
    for key_node, value_node in zip(node.keys, node.values):
        if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
            continue
        if key_node.value not in TARGET_BUILDER_FIELDS:
            continue
        value = static_string(value_node)
        if value is not None:
            fields[key_node.value] = value
    return fields


def builder_student_values(path: Path) -> dict[int, dict[str, str]]:
    """Read static per-day student strings from a builder AST without importing it."""

    if not path.is_file():
        return {}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    best: dict[int, tuple[int, dict[str, str]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        day_entries: dict[int, dict[str, str]] = {}
        for key_node, value_node in zip(node.keys, node.values):
            if (
                isinstance(key_node, ast.Constant)
                and isinstance(key_node.value, int)
                and 1 <= key_node.value <= 5
                and isinstance(value_node, ast.Dict)
            ):
                fields = dict_string_fields(value_node)
                if fields:
                    day_entries[key_node.value] = fields
        if len(day_entries) < 4:
            continue
        for day, fields in day_entries.items():
            score = sum(key in fields for key in ("DONE", "EXIT", "PURPOSE", "TITLE"))
            if day not in best or score > best[day][0]:
                best[day] = (score, fields)
    return {day: fields for day, (_, fields) in sorted(best.items())}


def direct_template_sections(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.is_file():
        return {"exit": [], "done": [], "response": [], "support": []}
    parser = HtmlTreeParser()
    parser.feed(path.read_text(encoding="utf-8"))
    headings = find_nodes(parser.root, {"h2", "h3", "h4", "h5"})
    exit_blocks: list[dict[str, Any]] = []
    done_blocks: list[dict[str, Any]] = []
    response_blocks: list[dict[str, Any]] = []
    for heading in headings:
        text = node_text(heading).lower().strip(":")
        target: list[dict[str, Any]] | None = None
        if "you are done" in text:
            target = done_blocks
        elif "private reflection" in text or "written reflection" in text:
            target = response_blocks
        elif (
            "exit ticket" in text
            or text in {"exit", "close", "submit and close"}
            or text.startswith("complete the exit")
        ):
            target = exit_blocks
        if target is None or heading.parent is None:
            continue
        siblings = heading.parent.children
        try:
            start = siblings.index(heading) + 1
        except ValueError:
            continue
        level = int(heading.tag[1])
        for sibling in siblings[start:]:
            if (
                target is response_blocks
                and response_blocks
                and isinstance(sibling, HtmlNode)
                and sibling.tag in {"details", "div", "section"}
            ):
                break
            if isinstance(sibling, HtmlNode) and sibling.tag in {"h2", "h3", "h4", "h5"}:
                if int(sibling.tag[1]) <= level:
                    break
            if isinstance(sibling, HtmlNode):
                target.extend(html_node_to_blocks(sibling))

    # Several early templates label the completion box with <strong> rather
    # than a heading.  Capture the list in that same panel exactly.
    for strong in find_nodes(parser.root, {"strong"}):
        if "you are done" not in node_text(strong).lower() or strong.parent is None:
            continue
        for candidate in find_nodes(strong.parent, {"ul", "ol"}):
            for block in html_node_to_blocks(candidate):
                if block.get("type") == "list":
                    block["type"] = "checklist"
                    block.pop("ordered", None)
                done_blocks.append(block)

    support_markers = (
        "word bank",
        "choice bank",
        "use this frame",
        "use these frames",
        "sentence stem",
        "sentence frame",
        "sentence starter",
        "spanish terms",
        "spanish support",
        "vocabulario",
        "términos",
    )
    support_blocks: list[dict[str, Any]] = []
    for summary in find_nodes(parser.root, {"summary"}):
        if not any(marker in node_text(summary).lower() for marker in support_markers):
            continue
        if summary.parent is None:
            continue
        for child in find_nodes(summary.parent, {"p", "li", "blockquote"}):
            text = node_text(child)
            if text:
                support_blocks.append(paragraph_block(text))
    for node in find_nodes(parser.root, {"p", "li"}):
        text = node_text(node)
        lowered = text.lower()
        if any(marker in lowered for marker in support_markers):
            support_blocks.append(paragraph_block(text))
    return {
        "exit": dedupe_blocks(exit_blocks),
        "done": dedupe_blocks(done_blocks),
        "response": dedupe_blocks(response_blocks),
        "support": dedupe_blocks(support_blocks),
    }


def dedupe_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    for block in blocks:
        key = json.dumps(block, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            output.append(block)
    return output


def blocks_plain_text(blocks: list[dict[str, Any]]) -> str:
    return " ".join(strip_markdown(value) for block in blocks for value in text_values(block))


def ensure_exit_response_box(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not blocks or any(block_has_response(block) for block in blocks):
        return blocks
    prompt = blocks_plain_text(blocks)
    if not prompt or not re.search(r"[?.:]", prompt):
        return blocks
    return [*blocks, {"type": "response_box", "prompt": None, "lines": 3, "full_width": True}]


def template_response_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn exact template reflection questions into native response boxes."""

    output: list[dict[str, Any]] = []
    for block in blocks:
        if block.get("type") in {"list", "checklist"}:
            items = block.get("items", [])
            if items and all(re.search(r"[?.:]\s*$", str(item)) for item in items):
                output.extend(
                    {
                        "type": "response_box",
                        "prompt": str(item),
                        "lines": 3,
                        "full_width": True,
                    }
                    for item in items
                )
                continue
        output.append(block)
    return output


def current_close(
    day: dict[str, Any],
    builder_fields: dict[str, str],
    template_sections: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    exit_blocks: list[dict[str, Any]] = []
    done_blocks: list[dict[str, Any]] = []
    authority: list[str] = []

    if builder_fields.get("EXIT"):
        exit_blocks = html_fragment_to_blocks(builder_fields["EXIT"])
        authority.append("canvas_builder_student_EXIT")
    elif template_sections["exit"]:
        exit_blocks = template_sections["exit"]
        authority.append("student_template_exit_section")

    if builder_fields.get("DONE"):
        done_blocks = html_fragment_to_blocks(builder_fields["DONE"])
        for block in done_blocks:
            if block.get("type") == "list":
                block["type"] = "checklist"
                block.pop("ordered", None)
        authority.append("canvas_builder_student_DONE")
    elif template_sections["done"]:
        done_blocks = template_sections["done"]
        for block in done_blocks:
            if block.get("type") == "list":
                block["type"] = "checklist"
                block.pop("ordered", None)
        authority.append("student_template_done_section")

    if not exit_blocks and day["exit_ticket"].get("marker_present"):
        exit_blocks = markdown_to_blocks(day["exit_ticket"]["section_markdown"])
        authority.append("docs_exact_exit_section_fallback")

    exit_blocks = ensure_exit_response_box(dedupe_blocks(exit_blocks))
    done_blocks = dedupe_blocks(done_blocks)
    return {
        "authority": authority,
        "exit_blocks": exit_blocks,
        "done_blocks": done_blocks,
    }


def source_path(record: dict[str, Any]) -> Path:
    return ROOT / str(record["source_path"])


def source_is_response_artifact(record: dict[str, Any], blocks: list[dict[str, Any]]) -> bool:
    return (
        record.get("audience") == "student"
        and not record.get("variant_of")
        and record.get("kind") in {"worksheet", "scaffold", "reference"}
        and any(block_has_response(block) for block in blocks)
    )


def first_direction(blocks: list[dict[str, Any]]) -> str | None:
    for block in blocks:
        if block.get("type") in {"paragraph", "inline_response"}:
            text = " ".join(text_values(block))
            clean = strip_markdown(text)
            if clean:
                return clean
    return None


def canonical_title(day: dict[str, Any]) -> str:
    h1 = str(day.get("h1") or "").strip()
    h1 = re.sub(r"^Day\s+\d+\s*:\s*", "", h1, flags=re.I)
    return f"CCE | {day['six_weeks']}SW Wk{day['week']} Day {day['day']} | {h1}"


def guard_manual_specs(
    source_by_key: dict[str, dict[str, Any]],
    route_payload: dict[str, Any],
    content_payload: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    expected_route_hash = content_payload.get("route_manual_spec_sha256")
    actual_route_hash = sha256_path(ROUTE_MANUAL_SPEC)
    if expected_route_hash != actual_route_hash:
        failures.append(
            "manual content specs guard a different student_response_route_manual_specs.json"
        )
    route_specs = {row["day_key"]: row for row in route_payload.get("specs", [])}
    content_specs = {row["day_key"]: row for row in content_payload.get("specs", [])}
    if set(route_specs) != set(content_specs):
        failures.append("manual route/content day-key sets differ")
    for day_key, route in route_specs.items():
        day = source_by_key.get(day_key)
        if not day:
            failures.append(f"{day_key}: absent from source-spec draft")
            continue
        guards = route.get("source_guards", {})
        comparisons = {
            "day_source_sha256": day["day_source"].get("sha256"),
            "canvas_builder_sha256": day["canvas_builder"].get("sha256"),
            "student_template_sha256": (day.get("student_template") or {}).get("sha256"),
        }
        for field_name, actual in comparisons.items():
            if guards.get(field_name) != actual:
                failures.append(f"{day_key}: stale manual {field_name}")
        if route.get("layout_spec_status") != "reviewed":
            failures.append(f"{day_key}: layout spec is not reviewed")
    return failures


def compose_manual_day(
    day: dict[str, Any], route: dict[str, Any], content: dict[str, Any]
) -> dict[str, Any]:
    ambiguities: list[str] = []
    authored_blocks = content["blocks"]
    blocks = authored_blocks
    base_source_record: dict[str, Any] | None = None
    composition = content.get("source_composition")
    if composition:
        base_source_record = composition.get("base_source")
        if not base_source_record or not base_source_record.get("path"):
            ambiguities.append("manual_source_composition_missing_base_source")
        else:
            base_path = ROOT / str(base_source_record["path"])
            if not base_path.is_file():
                ambiguities.append(
                    f"manual_source_composition_missing:{base_source_record['path']}"
                )
            elif sha256_path(base_path) != base_source_record.get("sha256"):
                ambiguities.append(
                    f"manual_source_composition_stale:{base_source_record['path']}"
                )
            else:
                prefix_indices = composition.get("prefix_block_indices", [])
                suffix_indices = composition.get("suffix_block_indices", [])
                indices = [*prefix_indices, *suffix_indices]
                if any(
                    not isinstance(index, int) or index < 0 or index >= len(authored_blocks)
                    for index in indices
                ):
                    ambiguities.append("manual_source_composition_block_index_out_of_range")
                else:
                    blocks = [
                        *(authored_blocks[index] for index in prefix_indices),
                        *markdown_to_blocks(base_path.read_text(encoding="utf-8")),
                        *(authored_blocks[index] for index in suffix_indices),
                    ]
    if not route["content_spec"].get("required_elements"):
        ambiguities.append("manual_route_spec_has_no_required_elements")
    return {
        "day_key": day["day_key"],
        "six_weeks": day["six_weeks"],
        "week": day["week"],
        "day": day["day"],
        "title": route["title"],
        "subtitle": route.get("subtitle"),
        "purpose": content["purpose"],
        "demonstration_of_learning": day["demonstration_of_learning"],
        "directions": [content["purpose"]],
        "language_support": content["language_support"],
        "blocks": blocks,
        "close": content["close"],
        "document_target": {
            "document_id": route.get("document_id"),
            "folder_id": route.get("folder_id"),
            "folder_path": route.get("folder_path"),
        },
        "sources": {
            "day_source": day["day_source"],
            "canvas_builder": day["canvas_builder"],
            "student_template": day["student_template"],
            "supplemental": route.get("supplemental_sources", []),
            "base_response_source": base_source_record,
            "manual_route_spec": repo_path(ROUTE_MANUAL_SPEC),
            "manual_content_spec": repo_path(CONTENT_MANUAL_SPEC),
        },
        "source_disposition": {
            "included_response_artifacts": (
                [str(base_source_record["path"])] if base_source_record else []
            ),
            "included_reference_response_artifacts": [],
            "excluded_reference_cards": [],
            "excluded_nonresponse_artifacts": [],
            "compact_student_rubrics": [],
            "excluded_teacher_artifacts": [],
            "support_only_variants": [row["path"] for row in route.get("supplemental_sources", [])],
        },
        "manual_spec": True,
        "content_scope": "reviewed_manual",
        "ambiguities": ambiguities,
    }


def compose_automatic_day(
    day: dict[str, Any],
    builder_cache: dict[Path, dict[int, dict[str, str]]],
) -> dict[str, Any]:
    ambiguities: list[str] = []
    included: list[str] = []
    included_reference_responses: list[str] = []
    excluded_refs: list[str] = []
    excluded_nonresponse: list[str] = []
    compact_rubrics: list[str] = []
    excluded_teacher: list[str] = []
    support_variants: list[str] = []
    blocks: list[dict[str, Any]] = []
    directions: list[str] = []
    language_parts: list[dict[str, list[str]]] = []

    for record in day.get("builder_linked_worksheet_sources", []):
        path = source_path(record)
        relative = str(record.get("source_path"))
        if not path.is_file():
            ambiguities.append(f"missing_source:{relative}")
            continue
        if sha256_path(path) != record.get("source_sha256"):
            ambiguities.append(f"stale_source_guard:{relative}")
            continue
        source_text = path.read_text(encoding="utf-8")
        metadata, _ = parse_front_matter(source_text)
        source_blocks = markdown_to_blocks(source_text)
        language_parts.append(extract_language_support(source_blocks))

        if record.get("audience") != "student":
            excluded_teacher.append(relative)
            continue
        if record.get("kind") == "reference" and not any(
            block_has_writable_response(block) for block in source_blocks
        ):
            excluded_refs.append(relative)
            continue
        if record.get("variant_of"):
            support_variants.append(relative)
            continue
        if record.get("kind") == "rubric":
            compact = compact_rubric(str(record.get("title") or metadata.get("title") or path.stem), source_blocks)
            if not compact:
                ambiguities.append(f"student_rubric_could_not_compact:{relative}")
                continue
            if blocks and blocks[-1].get("type") != "page_break":
                blocks.append({"type": "page_break"})
            blocks.extend(compact)
            compact_rubrics.append(relative)
            continue
        if not source_is_response_artifact(record, source_blocks):
            if record.get("kind") == "reference":
                excluded_refs.append(relative)
            else:
                excluded_nonresponse.append(relative)
            continue

        if blocks and blocks[-1].get("type") != "page_break":
            blocks.append({"type": "page_break"})
        blocks.extend(source_blocks)
        included.append(relative)
        if record.get("kind") == "reference":
            included_reference_responses.append(relative)
        direction = first_direction(source_blocks)
        if direction:
            directions.append(direction)
        source_tables = count_source_tables(source_text)
        rendered_tables = count_tables(source_blocks)
        if source_tables != rendered_tables:
            ambiguities.append(
                f"source_table_count_mismatch:{relative}:{source_tables}!={rendered_tables}"
            )

    builder_path = ROOT / str(day["canvas_builder"]["path"])
    if builder_path not in builder_cache:
        builder_cache[builder_path] = builder_student_values(builder_path)
    builder_fields = builder_cache[builder_path].get(int(day["day"]), {})
    template_path = ROOT / str(day["student_template"]["path"])
    template_sections = direct_template_sections(template_path)
    close = current_close(day, builder_fields, template_sections)

    support_fragments: list[dict[str, Any]] = []
    for field_name in ("LANGUAGE", "SUPPORT"):
        if builder_fields.get(field_name):
            support_fragments.extend(html_fragment_to_blocks(builder_fields[field_name]))
    support_fragments.extend(template_sections["support"])
    language_parts.append(
        extract_language_support(support_fragments, include_strategies=True)
    )
    day_ell = day.get("support", {}).get("ell_keyword_lines", [])
    language_parts.append(
        {
            "word_bank": [strip_markdown(value) for value in day_ell if "word" in value.lower() or "pre-teach" in value.lower()],
            "sentence_stems": [strip_markdown(value) for value in day_ell if "stem" in value.lower() or "frame" in value.lower()],
            "strategies": [strip_markdown(value) for value in day_ell],
        }
    )

    close_blocks = [*close["exit_blocks"], *close["done_blocks"]]
    if not included and not any(
        block_has_writable_response(block) for block in close["exit_blocks"]
    ):
        response_blocks = template_response_blocks(template_sections["response"])
        if response_blocks:
            blocks.extend(response_blocks)
    if close_blocks:
        existing_text = blocks_plain_text(blocks).lower()
        new_close: list[dict[str, Any]] = []
        for block in close_blocks:
            block_text = blocks_plain_text([block]).lower()
            if block_text and block_text in existing_text:
                continue
            new_close.append(block)
        if new_close:
            if blocks and blocks[-1].get("type") != "page_break":
                blocks.append({"type": "page_break"})
            blocks.append({"type": "heading", "level": 2, "text": "Close"})
            blocks.extend(new_close)

    if not blocks:
        ambiguities.append("no_renderable_student_response_content")
    if not any(block_has_writable_response(block) for block in blocks):
        ambiguities.append("no_native_response_surface")

    language = merge_language_support(*language_parts)
    if not language["word_bank"] and not language["sentence_stems"] and not language["strategies"]:
        ambiguities.append("no_point_of_use_eb_support_found")

    purpose = strip_markdown(builder_fields.get("PURPOSE", "")) or day["demonstration_of_learning"]
    if not directions:
        directions = [purpose]
    live = day.get("live_google_doc") or {}
    return {
        "day_key": day["day_key"],
        "six_weeks": day["six_weeks"],
        "week": day["week"],
        "day": day["day"],
        "title": canonical_title(day),
        "subtitle": None,
        "purpose": purpose,
        "demonstration_of_learning": day["demonstration_of_learning"],
        "directions": stable_unique(directions),
        "language_support": language,
        "blocks": dedupe_adjacent_blocks(blocks),
        "close": close,
        "document_target": {
            "document_id": live.get("document_id"),
            "folder_id": live.get("folder_id"),
            "folder_path": live.get("folder_path"),
        },
        "sources": {
            "day_source": day["day_source"],
            "canvas_builder": day["canvas_builder"],
            "student_template": day["student_template"],
            "worksheet_sources": [
                {
                    "path": row["source_path"],
                    "sha256": row["source_sha256"],
                    "kind": row["kind"],
                    "audience": row["audience"],
                    "variant_of": row["variant_of"],
                }
                for row in day.get("builder_linked_worksheet_sources", [])
            ],
        },
        "source_disposition": {
            "included_response_artifacts": included,
            "included_reference_response_artifacts": included_reference_responses,
            "excluded_reference_cards": stable_unique(excluded_refs),
            "excluded_nonresponse_artifacts": stable_unique(excluded_nonresponse),
            "compact_student_rubrics": compact_rubrics,
            "excluded_teacher_artifacts": excluded_teacher,
            "support_only_variants": support_variants,
        },
        "manual_spec": False,
        "content_scope": "combined_response_artifact" if included else "close_only",
        "ambiguities": stable_unique(ambiguities),
    }


def dedupe_adjacent_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    last: str | None = None
    for block in blocks:
        key = json.dumps(block, ensure_ascii=False, sort_keys=True)
        if key == last:
            continue
        output.append(block)
        last = key
    return output


def stale_hits(record: dict[str, Any]) -> list[str]:
    text = json.dumps(record, ensure_ascii=False)
    return [name for name, pattern in STALE_PATTERNS.items() if pattern.search(text)]


def validate_day(record: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field_name in ("day_key", "title", "purpose", "demonstration_of_learning"):
        if not record.get(field_name):
            failures.append(f"missing_{field_name}")
    if not record.get("directions"):
        failures.append("missing_directions")
    if not record.get("blocks"):
        failures.append("missing_blocks")
    if not any(block_has_writable_response(block) for block in record.get("blocks", [])):
        failures.append("missing_native_response_surface")
    if record.get("ambiguities"):
        failures.extend(f"ambiguity:{value}" for value in record["ambiguities"])
    failures.extend(f"stale:{value}" for value in stale_hits(record))
    target = record.get("document_target", {})
    if target.get("folder_path") and not str(target["folder_path"]).startswith("VILS27/Units_CCR/"):
        failures.append("noncanonical_drive_folder")
    return failures


def build_payload() -> dict[str, Any]:
    source_payload = load_json(SOURCE_SPEC)
    route_payload = load_json(ROUTE_MANUAL_SPEC)
    content_payload = load_json(CONTENT_MANUAL_SPEC)
    source_days = source_payload.get("days", [])
    source_by_key = {row["day_key"]: row for row in source_days}
    route_by_key = {row["day_key"]: row for row in route_payload.get("specs", [])}
    content_by_key = {row["day_key"]: row for row in content_payload.get("specs", [])}
    manual_guard_failures = guard_manual_specs(
        source_by_key, route_payload, content_payload
    )

    builder_cache: dict[Path, dict[int, dict[str, str]]] = {}
    days: list[dict[str, Any]] = []
    for day in source_days:
        day_key = day["day_key"]
        if day_key in route_by_key:
            content = content_by_key.get(day_key)
            if content is None:
                record = compose_manual_day(
                    day,
                    route_by_key[day_key],
                    {"purpose": "", "language_support": {}, "blocks": [], "close": {}},
                )
                record["ambiguities"].append("missing_manual_content_spec")
            else:
                record = compose_manual_day(day, route_by_key[day_key], content)
        else:
            record = compose_automatic_day(day, builder_cache)
        record["qa_failures"] = validate_day(record)
        days.append(record)

    failures = [
        {"day_key": row["day_key"], "failures": row["qa_failures"]}
        for row in days
        if row["qa_failures"]
    ]
    included_count = sum(
        len(row["source_disposition"]["included_response_artifacts"]) for row in days
    )
    excluded_reference_count = sum(
        len(row["source_disposition"]["excluded_reference_cards"]) for row in days
    )
    excluded_nonresponse_count = sum(
        len(row["source_disposition"]["excluded_nonresponse_artifacts"])
        for row in days
    )
    compact_rubric_count = sum(
        len(row["source_disposition"]["compact_student_rubrics"]) for row in days
    )
    close_only_day_keys = [
        str(row["day_key"]) for row in days if row["content_scope"] == "close_only"
    ]
    return {
        "schema_version": 1,
        "artifact": "CCE semantic student Google Doc content specification draft",
        "determinism": (
            "No timestamp is emitted. Records follow source-spec order; blocks follow exact "
            "source order. Builders are parsed as AST and are never imported or executed."
        ),
        "authority_order": source_payload.get("authority_order", []),
        "inputs": {
            "source_spec": {"path": repo_path(SOURCE_SPEC), "sha256": sha256_path(SOURCE_SPEC)},
            "manual_route_specs": {
                "path": repo_path(ROUTE_MANUAL_SPEC),
                "sha256": sha256_path(ROUTE_MANUAL_SPEC),
            },
            "manual_content_specs": {
                "path": repo_path(CONTENT_MANUAL_SPEC),
                "sha256": sha256_path(CONTENT_MANUAL_SPEC),
            },
        },
        "summary": {
            "day_count": len(days),
            "manual_day_count": sum(bool(row["manual_spec"]) for row in days),
            "automatic_day_count": sum(not row["manual_spec"] for row in days),
            "included_response_artifact_count": included_count,
            "excluded_reference_card_count": excluded_reference_count,
            "excluded_nonresponse_artifact_count": excluded_nonresponse_count,
            "compact_student_rubric_count": compact_rubric_count,
            "close_only_day_count": len(close_only_day_keys),
            "close_only_day_keys": close_only_day_keys,
            "qa_failure_day_count": len(failures),
            "manual_guard_failure_count": len(manual_guard_failures),
        },
        "manual_guard_failures": manual_guard_failures,
        "qa_failures": failures,
        "days": days,
    }


def validate_strict(payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected = {
        "day_count": 180,
        "manual_day_count": 7,
        "automatic_day_count": 173,
        "close_only_day_count": 3,
        "qa_failure_day_count": 0,
        "manual_guard_failure_count": 0,
    }
    for field_name, wanted in expected.items():
        actual = payload["summary"].get(field_name)
        if actual != wanted:
            failures.append(f"{field_name}: expected {wanted}, found {actual}")
    keys = [row["day_key"] for row in payload.get("days", [])]
    if len(keys) != len(set(keys)):
        failures.append("day keys are not unique")
    if keys != sorted(
        keys,
        key=lambda key: tuple(
            int(DAY_KEY_RE.match(key).group(name))  # type: ignore[union-attr]
            for name in ("sw", "week", "day")
        ),
    ):
        failures.append("day records are not in curriculum order")
    for row in payload.get("qa_failures", []):
        failures.append(f"{row['day_key']}: {', '.join(row['failures'])}")
    failures.extend(str(value) for value in payload.get("manual_guard_failures", []))
    return failures


def render_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def resolve_output(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    protected = {SOURCE_SPEC.resolve(), ROUTE_MANUAL_SPEC.resolve(), CONTENT_MANUAL_SPEC.resolve()}
    if path in protected:
        raise ValueError("Refusing to overwrite an input specification")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--check", action="store_true", help="Fail if output is missing or stale")
    parser.add_argument("--strict", action="store_true", help="Require all 180 records and zero ambiguity/QA failures")
    parser.add_argument("--stdout", action="store_true", help="Print JSON instead of writing it")
    args = parser.parse_args()
    try:
        output = resolve_output(args.output)
    except ValueError as error:
        parser.error(str(error))

    payload = build_payload()
    rendered = render_payload(payload)
    strict_failures = validate_strict(payload) if args.strict else []
    if strict_failures:
        for failure in strict_failures:
            print(f"STRICT: {failure}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(rendered)
        return 0
    if args.check:
        if not output.is_file():
            print(f"Content spec is missing: {output}", file=sys.stderr)
            return 1
        if output.read_text(encoding="utf-8") != rendered:
            print(f"Content spec is stale: {output}", file=sys.stderr)
            return 1
        print(f"Content spec is current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {payload['summary']['day_count']} semantic day specs to {output} "
        f"({payload['summary']['qa_failure_day_count']} QA failure days)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
