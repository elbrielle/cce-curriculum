#!/usr/bin/env python3
"""Build the complete unit-artifact contract for the CCE Google Drive mirror.

This inventory joins the 36 current Canvas builders with the generated public
unit-download lists and records their complete public-safe union from
``docs/resources``.

PDFs remain PDFs.  They are not converted into loose Google Docs merely to
create a second format.  Editable PowerPoint, Word, and Excel sources continue
to be governed by ``google-workspace-parity-manifest.json``.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANVAS_ROOT = ROOT / "build/canvas"
RESOURCE_ROOT = ROOT / "docs/resources"
DRIVE_STATE = ROOT / "cce-curriculum/notes/google-workspace-drive-state.json"
PARITY_MANIFEST = ROOT / "cce-curriculum/notes/google-workspace-parity-manifest.json"
SITE_MANIFEST = ROOT / "public-site/dist/data/site-manifest.json"
DISTRIBUTION_INVENTORY = ROOT / "cce-curriculum/notes/google-workspace-distribution-inventory.json"
OUTPUT = ROOT / "cce-curriculum/notes/google-workspace-complete-artifact-inventory.json"

BUILDER_RE = re.compile(r"build_(?:(?P<sw>[2-6])sw_)?wk(?P<wk>[0-6])\.py")
FILE_LITERAL_RE = re.compile(r'''["']([^"']+\.(?:pdf|docx|pptx|xlsx))["']''', re.I)

# A domain-readable distribution folder must not expose answer keys to students.
EXCLUDED_BASENAMES = {
    "2sw-wk4-evidence-check-teacher-key.pdf": "teacher_answer_key_canvas_only",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"complete artifact inventory: FAIL: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def address_for_builder(path: Path) -> str | None:
    match = BUILDER_RE.fullmatch(path.name)
    if not match:
        return None
    sw = int(match.group("sw") or 1)
    wk = int(match.group("wk"))
    return f"{sw}SW Wk{wk}"


def main() -> None:
    require(DRIVE_STATE.is_file(), f"missing {DRIVE_STATE.relative_to(ROOT)}")
    require(PARITY_MANIFEST.is_file(), f"missing {PARITY_MANIFEST.relative_to(ROOT)}")
    require(SITE_MANIFEST.is_file(), "build public-site/dist before creating the inventory")
    require(DISTRIBUTION_INVENTORY.is_file(), "build the public distribution inventory before creating the complete inventory")

    resource_by_name: dict[str, Path] = {}
    for path in RESOURCE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        require(path.name not in resource_by_name, f"duplicate resource basename {path.name}")
        resource_by_name[path.name] = path

    drive_state = json.loads(DRIVE_STATE.read_text(encoding="utf-8"))
    parity = json.loads(PARITY_MANIFEST.read_text(encoding="utf-8"))
    site = json.loads(SITE_MANIFEST.read_text(encoding="utf-8"))
    distribution = json.loads(DISTRIBUTION_INVENTORY.read_text(encoding="utf-8"))

    drive_units = {unit["curriculum_address"]: unit for unit in drive_state["units"]}
    public_sources = {row["source"] for row in site["copied_resources"]}
    public_sources_by_unit = {
        row["curriculum_address"]: {release["source"] for release in row["public_resources"]}
        for row in distribution["units"]
    }
    builders = {
        address: path
        for path in sorted(CANVAS_ROOT.glob("build_*.py"))
        if (address := address_for_builder(path)) is not None
    }
    require(len(builders) == 36, f"expected 36 unit builders, found {len(builders)}")
    require(set(builders) == set(drive_units), "Canvas builder and Drive unit addresses differ")

    excluded: list[dict[str, str]] = []
    units: list[dict[str, object]] = []
    all_required_refs = 0
    all_required_sources: set[str] = set()
    missing_drive_refs = 0

    for address in sorted(builders, key=lambda value: (int(value[0]), int(value.split("Wk")[1]))):
        builder = builders[address]
        literals = FILE_LITERAL_RE.findall(builder.read_text(encoding="utf-8"))
        builder_basenames = {Path(value).name for value in literals if Path(value).name in resource_by_name}
        require(builder_basenames, f"{address} builder resolves no docs/resources artifacts")

        required: list[dict[str, object]] = []
        state = drive_units[address]
        drive_by_source = {
            row["source"]: row
            for row in [*state.get("public_releases", []), *state.get("complete_releases", [])]
        }

        public_sources_for_unit = public_sources_by_unit[address]
        builder_sources_for_unit = {
            resource_by_name[basename].relative_to(ROOT).as_posix()
            for basename in builder_basenames
        }
        source_set = builder_sources_for_unit | public_sources_for_unit

        for source in sorted(source_set):
            source_path = ROOT / source
            require(source_path.is_file(), f"{address}: missing distribution source {source}")
            basename = source_path.name
            if basename in EXCLUDED_BASENAMES:
                excluded.append(
                    {
                        "curriculum_address": address,
                        "source": source,
                        "reason": EXCLUDED_BASENAMES[basename],
                    }
                )
                continue

            require(source_path.suffix.lower() == ".pdf" or source_path.suffix.lower() in {".docx", ".pptx", ".xlsx"}, f"unsupported artifact {source}")
            drive_record = drive_by_source.get(source)
            required.append(
                {
                    "source": source,
                    "sha256": sha256(source_path),
                    "bytes": source_path.stat().st_size,
                    "artifact_type": "fixed_layout_pdf" if source_path.suffix.lower() == ".pdf" else "editable_office_source",
                    "google_native_required": source_path.suffix.lower() != ".pdf",
                    "public_site_included": source in public_sources,
                    "source_origins": sorted(
                        origin
                        for origin, present in (
                            ("canvas_builder", source in builder_sources_for_unit),
                            ("public_site", source in public_sources_for_unit),
                        )
                        if present
                    ),
                    "drive_file": (
                        {
                            "id": drive_record["drive_file_id"],
                            "name": drive_record["drive_name"],
                        }
                        if drive_record
                        else None
                    ),
                }
            )
            all_required_sources.add(source)

        all_required_refs += len(required)
        missing = sum(row["drive_file"] is None for row in required)
        missing_drive_refs += missing
        units.append(
            {
                "curriculum_address": address,
                "builder": builder.relative_to(ROOT).as_posix(),
                "unit_folder": state["unit_folder"],
                "google_masters_folder_id": state["google_masters_folder_id"],
                "download_releases_folder_id": state["download_releases_folder_id"],
                "required_release_count": len(required),
                "missing_drive_release_count": missing,
                "required_releases": required,
            }
        )

    editable_sources = {artifact["source"]["path"] for artifact in parity["artifacts"]}
    native_support_sources = {
        item["source"]
        for unit in drive_state["units"]
        for item in unit.get("native_support_files", [])
    }

    payload = {
        "version": 1,
        "generated_from": {
            "canvas_builders": "build/canvas/build_*.py",
            "drive_state": DRIVE_STATE.relative_to(ROOT).as_posix(),
            "editable_parity_manifest": PARITY_MANIFEST.relative_to(ROOT).as_posix(),
            "public_site_manifest": SITE_MANIFEST.relative_to(ROOT).as_posix(),
        },
        "contract": {
            "fixed_layout_pdf": "Upload the exact verified PDF to Download Releases; do not create a loose Google Doc.",
            "editable_office_source": "Keep the Office release in Download Releases and a verified native Google equivalent in Google Masters.",
            "licensed_or_authenticated_source": "Canvas only; never copy to Git or the public Drive mirror.",
            "teacher_answer_key": "Canvas only while the Drive mirror is readable across the IISD domain.",
        },
        "summary": {
            "unit_count": len(units),
            "required_unit_release_references": all_required_refs,
            "unique_required_sources": len(all_required_sources),
            "missing_drive_release_references": missing_drive_refs,
            "editable_parity_sources": len(editable_sources),
            "native_support_sources": len(native_support_sources),
            "excluded_artifacts": len(excluded),
        },
        "units": units,
        "editable_sources": sorted(editable_sources | native_support_sources),
        "excluded_artifacts": excluded,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "complete artifact inventory: PASS "
        f"units={len(units)} refs={all_required_refs} unique={len(all_required_sources)} "
        f"missing_drive_refs={missing_drive_refs} excluded={len(excluded)}"
    )


if __name__ == "__main__":
    main()
