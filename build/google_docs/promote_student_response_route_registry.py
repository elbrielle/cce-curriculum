#!/usr/bin/env python3
"""Promote a reviewed source-course prepare plan into the final route registry.

This helper is intentionally local-only. It makes no network or Canvas calls.
It accepts the canonical 180-route draft registry, an immutable read-only plan
created by ``sync_student_google_doc_links.py``, and the plan's exact SHA-256.
Only after every draft, plan, body, publication, and identity guard passes does
it write the canonical reviewed registry.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CANVAS_DIR = ROOT / "build" / "canvas"
if str(CANVAS_DIR) not in sys.path:
    sys.path.insert(0, str(CANVAS_DIR))

import sync_student_google_doc_links as sync  # noqa: E402


DRAFT_REGISTRY = (
    ROOT / "build" / "google_docs" / "student_response_route_registry.draft.json"
)
FINAL_REGISTRY = (
    ROOT / "build" / "google_docs" / "student_response_route_registry.json"
)
COURSE_ID = 98060
ROUTE_COUNT = 180
TARGET_COUNT = 360
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PromotionError(ValueError):
    """The draft or immutable plan failed a promotion guard."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PromotionError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError(f"Could not read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PromotionError(f"JSON root must be an object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    """Use a repository-relative path when the guarded file is in the repo."""

    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def _require_canonical_draft(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise PromotionError("Canonical draft must not be a symlink")
    resolved = expanded.resolve()
    if resolved != DRAFT_REGISTRY.resolve():
        raise PromotionError(f"Draft must be the canonical file: {DRAFT_REGISTRY}")
    if not resolved.is_file() or resolved.is_symlink():
        raise PromotionError("Canonical draft must be a regular non-symlink file")
    return resolved


def _require_immutable_plan(path: Path, expected_sha256: str) -> tuple[Path, dict]:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise PromotionError("Plan must not be a symlink")
    resolved = expanded.resolve()
    if not resolved.is_file():
        raise PromotionError("Plan must be a regular non-symlink file")
    mode = resolved.stat().st_mode & 0o777
    if mode & 0o222:
        raise PromotionError(
            f"Plan must be immutable (no write bits); found mode {mode:04o}"
        )
    if not SHA256_RE.fullmatch(expected_sha256):
        raise PromotionError("Expected plan SHA-256 must be 64 lowercase hex characters")
    actual_sha256 = sha256_file(resolved)
    if actual_sha256 != expected_sha256:
        raise PromotionError(
            f"Plan SHA-256 mismatch: expected {expected_sha256}, found {actual_sha256}"
        )
    return resolved, load_json(resolved)


def _validate_draft(draft_path: Path) -> tuple[dict, dict]:
    raw = load_json(draft_path)
    if raw.get("review_status") != "draft":
        raise PromotionError("Draft review_status must be exactly 'draft'")
    if raw.get("mutation_authority") != "none":
        raise PromotionError("Draft mutation_authority must remain 'none'")
    normalised = sync.load_registry(draft_path, for_apply=False)
    if len(normalised["routes"]) != ROUTE_COUNT:
        raise PromotionError(f"Draft must contain exactly {ROUTE_COUNT} routes")
    for route in normalised["routes"]:
        route_id = route["route_id"]
        google_doc = route.get("google_doc")
        if not isinstance(google_doc, dict):
            raise PromotionError(f"{route_id} has no complete Google Doc identity")
        folder_path = google_doc.get("folder_path")
        if (
            not isinstance(folder_path, str)
            or not folder_path.startswith(sync.CANONICAL_DRIVE_PREFIX)
            or not folder_path.endswith("/Google Masters")
        ):
            raise PromotionError(f"{route_id} is outside canonical Google Masters")
        onenote = route.get("onenote")
        if not isinstance(onenote, dict) or onenote.get("status") != "pending":
            raise PromotionError(f"{route_id} OneNote route must remain pending")
        if onenote.get("url") is not None:
            raise PromotionError(f"{route_id} OneNote URL must remain null")
        if not isinstance(route.get("source"), dict) or not route["source"]:
            raise PromotionError(f"{route_id} has no source evidence")
        if route.get("canvas") is not None:
            raise PromotionError(f"{route_id} draft already contains Canvas identities")
    return raw, normalised


def _require_plan_header(
    plan: dict,
    *,
    draft_path: Path,
    draft_sha256: str,
) -> None:
    if plan.get("mode") != "prepare_read_only":
        raise PromotionError("Plan mode must be exactly 'prepare_read_only'")
    if plan.get("authorization") != "not_applied":
        raise PromotionError("Plan authorization must be exactly 'not_applied'")
    if plan.get("status") != "blocked_or_draft":
        raise PromotionError("Draft prepare-plan status must be 'blocked_or_draft'")
    if plan.get("course_id") != COURSE_ID:
        raise PromotionError(f"Plan course_id must be {COURSE_ID}")
    if plan.get("issues") != []:
        raise PromotionError("Plan must contain zero top-level issues")
    registry = plan.get("registry")
    if not isinstance(registry, dict):
        raise PromotionError("Plan registry evidence is missing")
    if registry.get("sha256") != draft_sha256:
        raise PromotionError("Plan draft-registry SHA-256 does not match current draft")
    if Path(str(registry.get("path", ""))).expanduser().resolve() != draft_path:
        raise PromotionError("Plan points to a different draft-registry path")
    if registry.get("review_status") != "draft":
        raise PromotionError("Plan must have been prepared from a draft registry")
    if registry.get("route_count") != ROUTE_COUNT:
        raise PromotionError(f"Plan registry route_count must be {ROUTE_COUNT}")
    safety = plan.get("safety_contract")
    if not isinstance(safety, dict):
        raise PromotionError("Plan safety contract is missing")
    if safety.get("allowed_put_fields") != ["wiki_page[body]"]:
        raise PromotionError("Plan allowed PUT fields are not body-only")
    if safety.get("publication_fields_sent") != []:
        raise PromotionError("Plan unexpectedly allows publication fields")


def _validate_target(
    target: dict,
    *,
    route: dict,
    role: str,
) -> dict:
    key = f"{route['route_id']} {role}"
    if target.get("day_key") != route["day_key"]:
        raise PromotionError(f"{key}: day_key differs from draft")
    if target.get("issues") != []:
        raise PromotionError(f"{key}: target contains unresolved issues")
    page_id = target.get("page_id")
    if not isinstance(page_id, int) or isinstance(page_id, bool) or page_id <= 0:
        raise PromotionError(f"{key}: page_id must be a positive integer")
    page_url = target.get("page_url")
    try:
        page_url = sync.canonical_page_slug(page_url)
    except sync.RegistryError as exc:
        raise PromotionError(f"{key}: invalid Page URL: {exc}") from exc
    if page_url != target.get("page_url"):
        raise PromotionError(f"{key}: plan must store the canonical Page URL slug")
    expected_endpoint = f"/api/v1/courses/{COURSE_ID}/pages/{page_url}"
    if target.get("endpoint") != expected_endpoint:
        raise PromotionError(f"{key}: endpoint does not match Page URL")
    if not isinstance(target.get("title"), str) or not target["title"].strip():
        raise PromotionError(f"{key}: Canvas title is missing")

    before = target.get("before_body")
    if not isinstance(before, str):
        raise PromotionError(f"{key}: before_body must be exact text")
    before_sha256 = sync.sha256_text(before)
    if target.get("observed_before_body_sha256") != before_sha256:
        raise PromotionError(f"{key}: observed before-body SHA-256 is invalid")
    if target.get("registry_expected_before_body_sha256") is not None:
        raise PromotionError(f"{key}: draft plan unexpectedly has a registry body hash")

    published = target.get("observed_published")
    if not isinstance(published, bool):
        raise PromotionError(f"{key}: observed publication readback must be boolean")
    if target.get("expected_published_readback") is not None:
        raise PromotionError(
            f"{key}: draft plan unexpectedly has a registry publication readback"
        )

    after = target.get("after_body")
    if not isinstance(after, str):
        raise PromotionError(f"{key}: after_body must be exact text")
    if target.get("after_body_sha256") != sync.sha256_text(after):
        raise PromotionError(f"{key}: after-body SHA-256 is invalid")
    rebuilt, transformation = sync.replace_response_home(
        before, sync.link_block(route, role)
    )
    if after != rebuilt:
        raise PromotionError(f"{key}: after_body is not reproducible")
    if target.get("transformation") != transformation:
        raise PromotionError(f"{key}: transformation metadata is not reproducible")
    if target.get("would_change") is not (before != after):
        raise PromotionError(f"{key}: would_change is invalid")
    return {
        "page_id": page_id,
        "url": page_url,
        "expected_body_sha256": before_sha256,
        "published_readback": published,
    }


def validate_plan_and_build_identities(
    plan: dict,
    *,
    draft_path: Path,
    draft_sha256: str,
    normalised_draft: dict,
) -> dict[str, dict]:
    _require_plan_header(
        plan,
        draft_path=draft_path,
        draft_sha256=draft_sha256,
    )
    targets = plan.get("targets")
    if not isinstance(targets, list) or len(targets) != TARGET_COUNT:
        raise PromotionError(f"Plan must contain exactly {TARGET_COUNT} targets")
    summary = plan.get("summary")
    if not isinstance(summary, dict):
        raise PromotionError("Plan summary is missing")
    if summary.get("route_count") != ROUTE_COUNT:
        raise PromotionError(f"Plan summary route_count must be {ROUTE_COUNT}")
    if summary.get("target_count") != TARGET_COUNT:
        raise PromotionError(f"Plan summary target_count must be {TARGET_COUNT}")
    if summary.get("issue_count") != 0:
        raise PromotionError("Plan summary issue_count must be zero")

    route_by_id = {
        route["route_id"]: route for route in normalised_draft["routes"]
    }
    target_by_key: dict[tuple[str, str], dict] = {}
    page_ids: set[int] = set()
    page_urls: set[str] = set()
    for target in targets:
        if not isinstance(target, dict):
            raise PromotionError("Every plan target must be an object")
        route_id = target.get("route_id")
        role = target.get("role")
        key = (route_id, role)
        if route_id not in route_by_id or role not in {"teacher", "student"}:
            raise PromotionError(f"Unexpected plan target: {key}")
        if key in target_by_key:
            raise PromotionError(f"Duplicate plan target: {key}")
        target_by_key[key] = target

    expected_keys = {
        (route_id, role)
        for route_id in route_by_id
        for role in ("teacher", "student")
    }
    if set(target_by_key) != expected_keys:
        missing = sorted(expected_keys - set(target_by_key))
        extra = sorted(set(target_by_key) - expected_keys)
        raise PromotionError(f"Plan target coverage mismatch; missing={missing}, extra={extra}")

    identities: dict[str, dict] = {}
    would_change_count = 0
    for route_id, route in route_by_id.items():
        roles: dict[str, dict] = {}
        for role in ("teacher", "student"):
            target = target_by_key[(route_id, role)]
            identity = _validate_target(target, route=route, role=role)
            if identity["page_id"] in page_ids:
                raise PromotionError(f"Duplicate Canvas page_id: {identity['page_id']}")
            if identity["url"] in page_urls:
                raise PromotionError(f"Duplicate Canvas page URL: {identity['url']}")
            page_ids.add(identity["page_id"])
            page_urls.add(identity["url"])
            roles[role] = identity
            would_change_count += target["would_change"] is True
        identities[route_id] = roles
    if len(page_ids) != TARGET_COUNT or len(page_urls) != TARGET_COUNT:
        raise PromotionError("Plan does not contain 360 unique Canvas identities")
    if summary.get("would_change_count") != would_change_count:
        raise PromotionError("Plan summary would_change_count is inconsistent")
    return identities


def build_reviewed_registry(
    raw_draft: dict,
    identities: dict[str, dict],
    *,
    draft_path: Path,
    draft_sha256: str,
    plan_path: Path,
    plan_sha256: str,
    plan: dict,
) -> dict:
    reviewed = copy.deepcopy(raw_draft)
    reviewed["schema_version"] = 2
    reviewed["artifact"] = "CCE student response-route reviewed registry"
    reviewed["review_status"] = "reviewed"
    reviewed["mutation_authority"] = "reviewed_source_course_body_plan_only"
    reviewed["determinism"] = (
        "Routes remain in curriculum order. Promotion provenance records the review "
        "time; exact draft, plan, source, Google Doc, Canvas Page, body, and publication "
        "identities are guarded."
    )
    for route in reviewed["routes"]:
        route_id = route["route_id"]
        route["canvas"] = {
            "status": "reviewed_source_course_identity",
            "source_course": {
                "course_id": COURSE_ID,
                "teacher": identities[route_id]["teacher"],
                "student": identities[route_id]["student"],
            },
        }
    summary = reviewed.setdefault("summary", {})
    summary["route_count"] = ROUTE_COUNT
    summary["canvas_identity_count"] = TARGET_COUNT
    summary["canvas_identity_pending_count"] = 0
    summary["reviewed_source_course_count"] = 1
    reviewed["review_provenance"] = {
        "promoted_at": datetime.now(timezone.utc).isoformat(),
        "promotion_tool": str(Path(__file__).resolve().relative_to(ROOT)),
        "draft_registry": {
            "path": display_path(draft_path),
            "sha256": draft_sha256,
            "review_status": "draft",
        },
        "source_course_plan": {
            "path": str(plan_path),
            "sha256": plan_sha256,
            "created_at": plan.get("created_at"),
            "mode": "prepare_read_only",
            "authorization": "not_applied",
            "course_id": COURSE_ID,
            "target_count": TARGET_COUNT,
        },
        "verified_contract": {
            "unique_route_count": ROUTE_COUNT,
            "unique_canvas_page_count": TARGET_COUNT,
            "target_issue_count": 0,
            "body_identity": "exact UTF-8 SHA-256",
            "publication_identity": "boolean readback only; never a mutation field",
        },
    }
    return reviewed


def validate_reviewed_payload(payload: dict) -> None:
    if payload.get("review_status") != "reviewed":
        raise PromotionError("Promoted payload is not reviewed")
    routes = payload.get("routes")
    if not isinstance(routes, list) or len(routes) != ROUTE_COUNT:
        raise PromotionError("Promoted payload lost routes")
    route_ids: set[str] = set()
    page_ids: set[int] = set()
    page_urls: set[str] = set()
    for route in routes:
        route_id = route.get("route_id")
        if not isinstance(route_id, str) or route_id in route_ids:
            raise PromotionError(f"Invalid promoted route_id: {route_id!r}")
        route_ids.add(route_id)
        source_course = (route.get("canvas") or {}).get("source_course")
        if not isinstance(source_course, dict) or source_course.get("course_id") != COURSE_ID:
            raise PromotionError(f"{route_id} has no reviewed source-course identity")
        for role in ("teacher", "student"):
            identity = source_course.get(role)
            if not isinstance(identity, dict):
                raise PromotionError(f"{route_id} {role} identity is missing")
            if identity.get("page_id") in page_ids or identity.get("url") in page_urls:
                raise PromotionError(f"{route_id} {role} identity is not unique")
            page_ids.add(identity["page_id"])
            page_urls.add(identity["url"])
            if not SHA256_RE.fullmatch(str(identity.get("expected_body_sha256", ""))):
                raise PromotionError(f"{route_id} {role} body SHA-256 is invalid")
            if not isinstance(identity.get("published_readback"), bool):
                raise PromotionError(f"{route_id} {role} publication readback is invalid")
    if len(page_ids) != TARGET_COUNT or len(page_urls) != TARGET_COUNT:
        raise PromotionError("Promoted payload lacks 360 unique Canvas identities")
    if not isinstance(payload.get("review_provenance"), dict):
        raise PromotionError("Promoted payload lacks review provenance")


def write_final_registry(payload: dict, *, replace: bool) -> str:
    # Do not resolve the final component: an existing symlink must be replaced
    # or rejected as that exact path, never followed to an unintended target.
    output = Path(os.path.abspath(FINAL_REGISTRY.expanduser()))
    output.parent.mkdir(parents=True, exist_ok=True)
    if (output.exists() or output.is_symlink()) and not replace:
        raise PromotionError(
            f"Refusing to overwrite {output}; pass --replace only after reviewing the new plan"
        )
    encoded = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        if replace:
            os.replace(temporary, output)
        else:
            try:
                os.link(temporary, output)
            except FileExistsError as exc:
                raise PromotionError(
                    f"Refusing concurrent overwrite of {output}; rerun only with --replace"
                ) from exc
            temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)
    return sha256_file(output)


def promote(
    *,
    draft_path: Path,
    plan_path: Path,
    expected_plan_sha256: str,
    replace: bool,
) -> dict:
    canonical_draft = _require_canonical_draft(draft_path)
    draft_sha256 = sha256_file(canonical_draft)
    raw_draft, normalised_draft = _validate_draft(canonical_draft)
    immutable_plan, plan = _require_immutable_plan(
        plan_path, expected_plan_sha256
    )
    identities = validate_plan_and_build_identities(
        plan,
        draft_path=canonical_draft,
        draft_sha256=draft_sha256,
        normalised_draft=normalised_draft,
    )
    reviewed = build_reviewed_registry(
        raw_draft,
        identities,
        draft_path=canonical_draft,
        draft_sha256=draft_sha256,
        plan_path=immutable_plan,
        plan_sha256=expected_plan_sha256,
        plan=plan,
    )
    validate_reviewed_payload(reviewed)
    output_sha256 = write_final_registry(reviewed, replace=replace)
    return {
        "status": "promoted_reviewed_registry",
        "output": str(FINAL_REGISTRY.resolve()),
        "output_sha256": output_sha256,
        "draft_sha256": draft_sha256,
        "plan_sha256": expected_plan_sha256,
        "route_count": ROUTE_COUNT,
        "canvas_identity_count": TARGET_COUNT,
        "canvas_writes": 0,
        "network_calls": 0,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draft", type=Path, default=DRAFT_REGISTRY)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--expected-plan-sha256", required=True)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace an existing reviewed registry after explicitly reviewing this plan",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = promote(
        draft_path=args.draft,
        plan_path=args.plan,
        expected_plan_sha256=args.expected_plan_sha256,
        replace=args.replace,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
