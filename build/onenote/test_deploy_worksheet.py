from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).with_name("deploy_worksheet.py")


def load_script():
    spec = importlib.util.spec_from_file_location("deploy_worksheet_for_test", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


deploy = load_script()


class DeployWorksheetSafetyTests(unittest.TestCase):
    def test_requires_explicit_section_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "section ID is required"):
            deploy.deploy_to_onenote("token", None, "Day 1", "<p>Work</p>")

    def test_existing_title_fails_closed_without_partial_patch(self) -> None:
        with (
            patch.object(deploy, "find_pages_by_title", return_value=[{"id": "page-1"}]),
            patch.object(deploy.requests, "patch") as patch_request,
            patch.object(deploy.requests, "post") as post_request,
        ):
            with self.assertRaisesRegex(RuntimeError, "Refusing to partially update"):
                deploy.deploy_to_onenote(
                    "token", "section-1", "Day 1", "<html><head></head><body>Work</body></html>"
                )
        patch_request.assert_not_called()
        post_request.assert_not_called()

    def test_create_targets_only_the_reviewed_section(self) -> None:
        response = Mock()
        response.json.return_value = {"links": {}}
        with (
            patch.object(deploy, "find_pages_by_title", return_value=[]),
            patch.object(deploy.requests, "post", return_value=response) as post_request,
        ):
            deploy.deploy_to_onenote("token", "section-1", "Day 1", "<p>Work</p>")
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            post_request.call_args.args[0],
            "https://graph.microsoft.com/v1.0/me/onenote/sections/section-1/pages",
        )
        self.assertEqual(post_request.call_args.kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
