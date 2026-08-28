from __future__ import annotations

import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "sync_student_google_doc_links.py"
SPEC = importlib.util.spec_from_file_location("sync_student_google_doc_links", SCRIPT)
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = sync
SPEC.loader.exec_module(sync)


def sample_route() -> dict:
    document_id = "Doc_ABC-123"
    return {
        "route_id": "1SW-Wk1-Day1",
        "day_key": "1SW-Wk1-Day1",
        "title": "Manufacturing & Evidence",
        "google_doc": {
            "document_id": document_id,
            "copy_url": f"https://docs.google.com/document/d/{document_id}/copy",
            "pdf_export_url": (
                f"https://docs.google.com/document/d/{document_id}/export?format=pdf"
            ),
        },
    }


def reviewed_registry() -> dict:
    routes = []
    serial = 0
    for six_weeks in range(1, 7):
        weeks = range(0, 6) if six_weeks == 1 else range(1, 7)
        for week in weeks:
            for day in range(1, 6):
                serial += 1
                day_key = f"{six_weeks}SW-Wk{week}-Day{day}"
                document_id = f"Doc_{serial:03d}"
                body = f"<div>before {serial}</div>"
                routes.append(
                    {
                        "route_id": day_key,
                        "day_key": day_key,
                        "title": f"Worksheet {serial}",
                        "google_doc": {
                            "document_id": document_id,
                            "copy_url": (
                                "https://docs.google.com/document/d/"
                                f"{document_id}/copy"
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
                        "source": {"body_fixture_sha256": sync.sha256_text(body)},
                        "canvas": {
                            "source_course": {
                                "course_id": 98060,
                                "teacher": {
                                    "page_id": serial * 2,
                                    "url": f"teacher-{day_key.lower()}",
                                    "expected_body_sha256": sync.sha256_text(body),
                                    "published_readback": False,
                                },
                                "student": {
                                    "page_id": serial * 2 + 1,
                                    "url": f"student-{day_key.lower()}",
                                    "expected_body_sha256": sync.sha256_text(body),
                                    "published_readback": False,
                                },
                            }
                        },
                    }
                )
    return {
        "schema_version": 1,
        "review_status": "reviewed",
        "mutation_authority": "reviewed_source_course_body_plan_only",
        "routes": routes,
    }


class PanelTests(unittest.TestCase):
    def test_student_panel_is_google_copy_response_home_only(self) -> None:
        panel = sync.link_block(sample_route(), "student")
        self.assertIn("Response Home", panel)
        self.assertIn("/copy", panel)
        self.assertEqual(panel.count("<a "), 1)
        self.assertNotIn("OneNote", panel)
        self.assertNotIn("export?format=pdf", panel)

    def test_teacher_panel_has_copy_placeholder_and_same_doc_pdf(self) -> None:
        panel = sync.link_block(sample_route(), "teacher")
        self.assertEqual(panel.count("<a "), 2)
        self.assertIn("OneNote template — link coming soon</strong></span>", panel)
        self.assertNotIn("OneNote template — link coming soon</a>", panel)
        self.assertIn("Doc_ABC-123/copy", panel)
        self.assertIn("Doc_ABC-123/export?format=pdf", panel)

    def test_panels_use_canvas_sanitizer_stable_semantic_emphasis(self) -> None:
        for role in ("teacher", "student"):
            with self.subTest(role=role):
                panel = sync.link_block(sample_route(), role)
                self.assertIn("<strong>", panel)
                self.assertNotIn("font-weight:", panel)
                self.assertNotIn("text-transform:", panel)
                self.assertNotIn("letter-spacing:", panel)

    def test_body_only_payload_has_no_publication_field(self) -> None:
        self.assertEqual(
            sync.body_only_payload("<p>after</p>"),
            {"wiki_page[body]": "<p>after</p>"},
        )


class ReplacementTests(unittest.TestCase):
    def test_replaces_response_home_and_removes_old_appended_route(self) -> None:
        block = sync.link_block(sample_route(), "student")
        old_route = (
            f'<aside id="{sync.BLOCK_ID}"><h2>Typeable Google Doc</h2>'
            '<a href="https://docs.google.com/document/d/Old/copy">old</a></aside>'
        )
        before = (
            '<div id="keep"><p>Intro</p><div class="old-response">'
            '<strong>Response Home:</strong> OneNote and paper.</div>'
            f'<p>After</p></div>\n{old_route}'
        )
        after, metadata = sync.replace_response_home(before, block)
        self.assertEqual(metadata["method"], "replace_response_home")
        self.assertEqual(metadata["removed_route_block_count"], 1)
        self.assertEqual(metadata["replaced_response_home_count"], 1)
        self.assertEqual(
            after,
            f'<div id="keep"><p>Intro</p>{block}<p>After</p></div>\n',
        )

    def test_replaces_existing_route_in_place_when_no_other_response_home(self) -> None:
        block = sync.link_block(sample_route(), "teacher")
        before = (
            '<section><p>Teacher content</p></section>\n'
            f'<aside id="{sync.BLOCK_ID}"><h2>Student Google Doc</h2>'
            '<a href="https://docs.google.com/document/d/Old/copy">old</a></aside>\n'
            '<p>Tail</p>'
        )
        after, metadata = sync.replace_response_home(before, block)
        self.assertEqual(metadata["method"], "replace_existing_route_block")
        self.assertEqual(
            after,
            f'<section><p>Teacher content</p></section>\n{block}\n<p>Tail</p>',
        )

    def test_chooses_inner_response_container_not_layout_wrapper(self) -> None:
        block = "<aside>NEW</aside>"
        before = (
            '<div class="layout"><p><strong>Response Home:</strong> old</p>'
            '<section>Other content</section></div>'
        )
        after, metadata = sync.replace_response_home(before, block)
        self.assertEqual(metadata["method"], "replace_response_home")
        self.assertEqual(
            after,
            '<div class="layout"><aside>NEW</aside>'
            '<section>Other content</section></div>',
        )

    def test_disjoint_response_homes_are_a_hard_stop(self) -> None:
        before = (
            '<div><strong>Response Home:</strong> first</div>'
            '<div><strong>Response Home:</strong> second</div>'
        )
        with self.assertRaises(sync.RouteReplacementError):
            sync.replace_response_home(before, "<aside>NEW</aside>")

    def test_midyear_profile_uses_detailed_linked_route_and_relabels_summary(self) -> None:
        block = sync.link_block(sample_route(), "student")
        old_route = (
            f'<aside id="{sync.BLOCK_ID}"><h2>Typeable Google Doc</h2>'
            '<a href="https://docs.google.com/document/d/Old/copy">old</a></aside>'
        )
        compact = (
            '<div class="summary"><strong style="color:#234b18">Response Home:'
            "</strong><p>complete a Mid-Year Profile Audit with an earlier result, "
            "three current facts, and a supported conclusion.</p></div>"
        )
        detailed = (
            '<p><strong>Response home:</strong> use the front-and-back Mid-Year Profile '
            "Audit your teacher gives you. Write your name on it. Your teacher will "
            "collect it today and return it for the Day 5 Blueprint. "
            '<a href="https://learn.irvingisd.net/courses/98060/files/14565910/preview">'
            "Open the same audit</a> only if you need a replacement or absence copy. "
            "H&amp;L, Xello, and earlier portfolio work are optional evidence sources; "
            "a private screenshot is not required.</p>"
        )
        before = f'<div id="keep">{compact}<h3>Get Ready</h3>{detailed}</div>{old_route}'
        after, metadata = sync.replace_response_home(before, block)
        self.assertEqual(
            metadata["method"],
            "replace_detailed_response_home_and_relabel_summary",
        )
        self.assertEqual(metadata["relabeled_response_summary_count"], 1)
        self.assertIn("<strong style=\"color:#234b18\">Today’s work:</strong>", after)
        self.assertIn(f"<h3>Get Ready</h3>{block}", after)
        self.assertNotIn("Open the same audit", after)
        self.assertNotIn("https://docs.google.com/document/d/Old/copy", after)
        self.assertEqual(after.count(f'id="{sync.BLOCK_ID}"'), 1)

        destination_before = before.replace("/courses/98060/files/", "/courses/97247/files/")
        destination_after, destination_metadata = sync.replace_response_home(
            destination_before, block
        )
        self.assertEqual(
            destination_metadata["method"],
            "replace_detailed_response_home_and_relabel_summary",
        )
        self.assertIn("Today’s work:", destination_after)

    def test_midyear_override_near_match_still_fails_closed(self) -> None:
        compact = (
            '<div><strong>Response Home:</strong><p>complete a Mid-Year Profile Audit '
            "with an earlier result, three current facts, and a supported "
            "conclusion.</p></div>"
        )
        detailed = (
            '<p><strong>Response home:</strong> use the front-and-back Mid-Year Profile '
            "Audit your teacher gives you. Write your name on it. Your teacher will "
            "collect it today and return it for the Day 5 Blueprint. "
            '<a href="https://learn.irvingisd.net/courses/98060/files/14565910/preview">'
            "Open a different audit</a> only if you need a replacement or absence "
            "copy. H&amp;L, Xello, and earlier portfolio work are optional evidence "
            "sources; a private screenshot is not required.</p>"
        )
        with self.assertRaises(sync.RouteReplacementError):
            sync.replace_response_home(compact + detailed, "<aside>NEW</aside>")


class DiscoveryTests(unittest.TestCase):
    def test_all_27_exception_titles_require_one_exact_match(self) -> None:
        self.assertEqual(len(sync.DISCOVERY_TITLE_OVERRIDES), 27)
        for serial, ((day_key, role), title) in enumerate(
            sync.DISCOVERY_TITLE_OVERRIDES.items(), start=1
        ):
            with self.subTest(day_key=day_key, role=role):
                exact = {"page_id": serial, "title": title, "url": f"page-{serial}"}
                near_match = {
                    "page_id": serial + 1000,
                    "title": title + " (old)",
                    "url": f"old-page-{serial}",
                }
                self.assertIs(
                    sync._discover_page([near_match, exact], day_key, role), exact
                )

    def test_exception_does_not_fall_back_to_generic_title(self) -> None:
        generic = {
            "page_id": 1,
            "title": "TEACHER: 1SW Wk0 Day 1 Facilitator Guide",
            "url": "generic",
        }
        with self.assertRaisesRegex(RuntimeError, "exact-title"):
            sync._discover_page([generic], "1SW-Wk0-Day1", "teacher")

    def test_duplicate_exact_exception_title_is_a_hard_stop(self) -> None:
        title = sync.DISCOVERY_TITLE_OVERRIDES[("6SW-Wk6-Day5", "student")]
        pages = [
            {"page_id": 1, "title": title, "url": "first"},
            {"page_id": 2, "title": title, "url": "second"},
        ]
        with self.assertRaisesRegex(RuntimeError, "found"):
            sync._discover_page(pages, "6SW-Wk6-Day5", "student")


class RegistryAndArtifactTests(unittest.TestCase):
    def test_workspace_historical_registry_cannot_authorize_apply(self) -> None:
        with self.assertRaisesRegex(sync.RegistryError, "review_status"):
            sync.load_registry(sync.FINAL_REGISTRY, for_apply=True)

    def test_reviewed_registry_requires_180_complete_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / sync.FINAL_REGISTRY.name
            path.write_text(json.dumps(reviewed_registry()), encoding="utf-8")
            with mock.patch.object(sync, "FINAL_REGISTRY", path):
                loaded = sync.load_registry(path, for_apply=True)
            self.assertEqual(loaded["review_status"], "reviewed")
            self.assertEqual(len(loaded["routes"]), 180)
            self.assertEqual(
                loaded["routes"][0]["google_doc"]["document_id"], "Doc_001"
            )

    def test_reviewed_registry_rejects_wrong_180_day_address_set(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / sync.FINAL_REGISTRY.name
            payload = reviewed_registry()
            payload["routes"][0]["day_key"] = "1SW-Wk6-Day1"
            payload["routes"][0]["route_id"] = "1SW-Wk6-Day1"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.object(sync, "FINAL_REGISTRY", path):
                with self.assertRaisesRegex(sync.RegistryError, "exact 180-day"):
                    sync.load_registry(path, for_apply=True)

    def test_draft_filename_is_rejected_before_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / sync.DRAFT_REGISTRY.name
            payload = reviewed_registry()
            payload["review_status"] = "draft"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(sync.RegistryError, "Apply requires --registry"):
                sync.load_registry(path, for_apply=True)

    def test_pdf_must_be_exported_from_same_google_doc(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / sync.FINAL_REGISTRY.name
            payload = reviewed_registry()
            payload["routes"][0]["google_doc"]["pdf_export_url"] = (
                "https://docs.google.com/document/d/Different/export?format=pdf"
            )
            path.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.object(sync, "FINAL_REGISTRY", path):
                with self.assertRaisesRegex(sync.RegistryError, "same-Doc PDF export"):
                    sync.load_registry(path, for_apply=True)

    def test_private_artifact_is_exclusive_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "plan.json"
            sync.write_private_immutable(path, {"status": "test"})
            mode = stat.S_IMODE(path.stat().st_mode)
            self.assertEqual(mode, 0o400)
            with self.assertRaises(FileExistsError):
                sync.write_private_immutable(path, {"status": "replacement"})


if __name__ == "__main__":
    unittest.main()
