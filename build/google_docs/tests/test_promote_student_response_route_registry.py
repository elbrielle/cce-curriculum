from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "promote_student_response_route_registry.py"
)
SPEC = importlib.util.spec_from_file_location(
    "promote_student_response_route_registry", SCRIPT
)
assert SPEC and SPEC.loader
promote_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = promote_module
SPEC.loader.exec_module(promote_module)
sync = promote_module.sync


def fixture_payloads(draft_path: Path) -> tuple[dict, dict]:
    routes = []
    targets = []
    serial = 0
    curriculum_weeks = [(1, week) for week in range(0, 6)] + [
        (six_weeks, week)
        for six_weeks in range(2, 7)
        for week in range(1, 7)
    ]
    for six_weeks, week in curriculum_weeks:
            for day in range(1, 6):
                serial += 1
                route_id = f"{six_weeks}SW-Wk{week}-Day{day}"
                document_id = f"Doc_{serial:03d}"
                route = {
                    "route_id": route_id,
                    "day_key": route_id,
                    "title": f"Worksheet {serial}",
                    "source": {"day_source": {"sha256": "a" * 64}},
                    "google_doc": {
                        "id": document_id,
                        "copy_url": (
                            f"https://docs.google.com/document/d/{document_id}/copy"
                        ),
                        "pdf_export_url": (
                            "https://docs.google.com/document/d/"
                            f"{document_id}/export?format=pdf"
                        ),
                        "folder_path": (
                            f"VILS27/Units_CCR/SW{six_weeks}/Google Masters"
                        ),
                    },
                    "onenote": {"status": "pending", "url": None},
                    "canvas": {
                        "status": "pending_fresh_source_course_audit",
                        "source_course": {
                            "course_id": None,
                            "teacher": None,
                            "student": None,
                        },
                    },
                }
                routes.append(route)
                normalised_route = {
                    "route_id": route_id,
                    "day_key": route_id,
                    "title": route["title"],
                    "google_doc": {
                        "document_id": document_id,
                        "copy_url": route["google_doc"]["copy_url"],
                        "pdf_export_url": route["google_doc"]["pdf_export_url"],
                    },
                }
                for role in ("teacher", "student"):
                    if role == "student":
                        before = (
                            '<div class="response"><strong>Response Home:</strong> '
                            "old route</div><p>Keep me</p>"
                        )
                    else:
                        before = (
                            '<p>Keep me</p><aside id="cce-student-google-doc">'
                            '<h2>Student Google Doc</h2>'
                            '<a href="https://docs.google.com/document/d/Old/copy">'
                            "old</a></aside>"
                        )
                    after, transformation = sync.replace_response_home(
                        before, sync.link_block(normalised_route, role)
                    )
                    page_id = serial * 2 + (role == "student")
                    page_url = f"{role}-{route_id.lower()}"
                    targets.append(
                        {
                            "route_id": route_id,
                            "day_key": route_id,
                            "role": role,
                            "page_id": page_id,
                            "page_url": page_url,
                            "title": f"{role.upper()}: {route_id} fixture",
                            "endpoint": (
                                f"/api/v1/courses/98060/pages/{page_url}"
                            ),
                            "registry_expected_before_body_sha256": None,
                            "observed_before_body_sha256": sync.sha256_text(before),
                            "expected_published_readback": None,
                            "observed_published": False,
                            "before_body": before,
                            "after_body": after,
                            "after_body_sha256": sync.sha256_text(after),
                            "transformation": transformation,
                            "would_change": before != after,
                            "issues": [],
                        }
                    )
    draft = {
        "schema_version": 1,
        "artifact": "fixture draft",
        "review_status": "draft",
        "mutation_authority": "none",
        "canonical_drive_root": {
            "id": "fixture",
            "path": "VILS27/Units_CCR",
        },
        "summary": {"route_count": 180, "canvas_identity_count": 0},
        "routes": routes,
    }
    draft_bytes = (json.dumps(draft, ensure_ascii=False, indent=2) + "\n").encode()
    draft_path.write_bytes(draft_bytes)
    draft_sha256 = promote_module.sha256_file(draft_path)
    plan = {
        "schema_version": 2,
        "artifact": "fixture immutable plan",
        "created_at": "2026-08-25T00:00:00+00:00",
        "mode": "prepare_read_only",
        "authorization": "not_applied",
        "status": "blocked_or_draft",
        "course_id": 98060,
        "registry": {
            "path": str(draft_path.resolve()),
            "sha256": draft_sha256,
            "review_status": "draft",
            "route_count": 180,
        },
        "safety_contract": {
            "allowed_put_fields": ["wiki_page[body]"],
            "publication_fields_sent": [],
        },
        "summary": {
            "route_count": 180,
            "target_count": 360,
            "would_change_count": 360,
            "issue_count": 0,
        },
        "issues": [],
        "targets": targets,
    }
    return draft, plan


class PromotionTests(unittest.TestCase):
    def prepare_files(self, temporary: str) -> tuple[Path, Path, Path, str, dict]:
        root = Path(temporary)
        draft_path = root / "student_response_route_registry.draft.json"
        final_path = root / "student_response_route_registry.json"
        _, plan = fixture_payloads(draft_path)
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        os.chmod(plan_path, 0o400)
        plan_sha256 = promote_module.sha256_file(plan_path)
        return draft_path, plan_path, final_path, plan_sha256, plan

    def run_promotion(
        self,
        draft_path: Path,
        plan_path: Path,
        final_path: Path,
        plan_sha256: str,
        *,
        replace: bool = False,
    ) -> dict:
        with (
            mock.patch.object(promote_module, "DRAFT_REGISTRY", draft_path),
            mock.patch.object(promote_module, "FINAL_REGISTRY", final_path),
        ):
            return promote_module.promote(
                draft_path=draft_path,
                plan_path=plan_path,
                expected_plan_sha256=plan_sha256,
                replace=replace,
            )

    def test_promotes_only_reviewed_registry_with_360_identities(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            draft, plan, final, plan_sha256, _ = self.prepare_files(temporary)
            result = self.run_promotion(draft, plan, final, plan_sha256)
            payload = json.loads(final.read_text(encoding="utf-8"))
            self.assertEqual(result["network_calls"], 0)
            self.assertEqual(result["canvas_writes"], 0)
            self.assertEqual(payload["review_status"], "reviewed")
            self.assertEqual(payload["summary"]["canvas_identity_count"], 360)
            self.assertEqual(len(payload["routes"]), 180)
            self.assertEqual(
                payload["routes"][0]["canvas"]["source_course"]["course_id"],
                98060,
            )
            self.assertEqual(final.stat().st_mode & 0o777, 0o444)

    def test_refuses_overwrite_without_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            draft, plan, final, plan_sha256, _ = self.prepare_files(temporary)
            self.run_promotion(draft, plan, final, plan_sha256)
            with self.assertRaisesRegex(promote_module.PromotionError, "Refusing to overwrite"):
                self.run_promotion(draft, plan, final, plan_sha256)
            replaced = self.run_promotion(
                draft, plan, final, plan_sha256, replace=True
            )
            self.assertEqual(replaced["status"], "promoted_reviewed_registry")

    def test_rejects_writable_or_wrong_hash_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            draft, plan, final, plan_sha256, _ = self.prepare_files(temporary)
            os.chmod(plan, 0o600)
            with self.assertRaisesRegex(promote_module.PromotionError, "immutable"):
                self.run_promotion(draft, plan, final, plan_sha256)
            os.chmod(plan, 0o400)
            with self.assertRaisesRegex(promote_module.PromotionError, "mismatch"):
                self.run_promotion(draft, plan, final, "0" * 64)

    def test_rejects_duplicate_identity_and_nonboolean_publication(self) -> None:
        for mutation, message in (
            ("duplicate_page_id", "Duplicate Canvas page_id"),
            ("bad_publication", "publication readback must be boolean"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                draft, plan_path, final, _, plan = self.prepare_files(temporary)
                if mutation == "duplicate_page_id":
                    plan["targets"][1]["page_id"] = plan["targets"][0]["page_id"]
                else:
                    plan["targets"][0]["observed_published"] = "false"
                os.chmod(plan_path, 0o600)
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                os.chmod(plan_path, 0o400)
                plan_sha256 = promote_module.sha256_file(plan_path)
                with self.assertRaisesRegex(promote_module.PromotionError, message):
                    self.run_promotion(draft, plan_path, final, plan_sha256)


if __name__ == "__main__":
    unittest.main()
