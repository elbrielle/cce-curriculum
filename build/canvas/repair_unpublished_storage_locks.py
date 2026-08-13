"""Lock the exact unpublished storage packages for three legacy CCR modules.

This repair is intentionally narrower than rebuilding the modules. It performs a
complete read-only preflight first, then changes only folder/file ``locked``
state, and finally proves the folder membership is unchanged and every scoped
record is locked.

Run with a Canvas token on hidden stdin. The token is never stored or printed.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass

import httpx

BASE = "https://learn.irvingisd.net"
COURSE_ID = 98060


@dataclass(frozen=True)
class Target:
    module_id: int
    module_name: str
    folders: dict[str, frozenset[str]]


TARGETS = (
    Target(
        542880,
        "1SW Wk0: Classroom Routines and Career Self-Discovery",
        {
            "course files/CCR Materials/1SW/Wk0": frozenset(
                {
                    "1sw-wk0-day1-lab-routines-and-your-choice-flex-day.pdf",
                    "1sw-wk0-day2-h-and-l-setup-and-discover-your-core-core-day-a.pdf",
                    "1sw-wk0-day3-work-values-and-building-blocks-core-day-b.pdf",
                    "1sw-wk0-day4-my-career-journey-reflection-core-day-c.pdf",
                    "1sw-wk0-day5-catch-up-and-your-choice-flex-day.pdf",
                    "building-blocks-word-bank-bilingual.pdf",
                    "building-blocks-word-bank.pdf",
                    "career-hunt-scaffold.pdf",
                    "career-research-worksheet-bilingual.pdf",
                    "career-research-worksheet-example.pdf",
                    "career-research-worksheet.pdf",
                    "lab-safety-contract-spanish.pdf",
                    "lab-safety-contract.pdf",
                    "my-career-journey-bilingual.pdf",
                    "my-career-journey-stems.pdf",
                    "my-career-journey.pdf",
                    "wk0-career-journey-rubric.pdf",
                }
            ),
            "course files/CCR Materials/1SW/Wk0/Day 1 Visuals": frozenset(
                {"behind-the-scenes.png", "classroom-career-hunt.png"}
            ),
            "course files/CCR Materials/1SW/Wk0/Day 2 Visuals": frozenset(
                {
                    "irving-isd-ccmr-programs-of-study.png",
                    "open-hats-and-ladders-discover-your-core.png",
                    "six-core-personality-types.png",
                }
            ),
            "course files/CCR Materials/1SW/Wk0/Day 3 Visuals": frozenset(
                {
                    "my-building-blocks-introduction.png",
                    "my-building-blocks-inventory.png",
                    "my-building-blocks-skills.png",
                    "open-hats-and-ladders-discover-your-work-values.png",
                }
            ),
            "course files/CCR Materials/1SW/Wk0/Day 4 Visuals": frozenset(
                {"building-a-career-community.png"}
            ),
            "course files/CCR Materials/1SW/Wk0/Day 5 Visuals": frozenset(
                {"perks-and-quirks-career-tables.png", "perks-and-quirks-introduction.png"}
            ),
        },
    ),
    Target(
        542972,
        "1SW Wk3: Computer Science and Networking Careers",
        {
            "course files/CCR Materials/1SW/Wk3": frozenset(
                {
                    "1sw-wk3-day1-networking-systems-pathway-transferable-skills.pdf",
                    "1sw-wk3-day2-website-revamp-audit-a-real-site.pdf",
                    "wk3-app-design-rubric.pdf",
                    "wk3-day4-career-comparison.pdf",
                    "wk3-day5-learning-style-connection.pdf",
                    "wk3-emerging-careers-link-sheet.pdf",
                    "wk3-emerging-tech-research-template.pdf",
                    "wk3-networking-career-cards.pdf",
                    "wk3-transferable-skills-list.pdf",
                    "wk3-ux-audit-scaffold.pdf",
                    "wk3-wireframe-template-bilingual.pdf",
                    "wk3-wireframe-template.pdf",
                }
            ),
            "course files/CCR Materials/1SW/Wk3/Day 1 Visuals": frozenset(
                {"it-app-exploration.png"}
            ),
            "course files/CCR Materials/1SW/Wk3/Day 2 Visuals": frozenset(
                {
                    "paws-and-claws-cart.png",
                    "paws-and-claws-home.png",
                    "website-revamp-034.png",
                    "website-revamp-035.png",
                    "website-revamp-climber-slide.png",
                }
            ),
            "course files/CCR Materials/1SW/Wk3/Day 3 Visuals": frozenset(
                {
                    "wireframe-workbook-036.png",
                    "wireframe-workbook-037.png",
                    "wireframe-workbook-038.png",
                    "wireframe-workbook-039.png",
                }
            ),
            "course files/CCR Materials/1SW/Wk3/Day 4 Visuals": frozenset(),
            "course files/CCR Materials/1SW/Wk3/Day 5 Visuals": frozenset(),
        },
    ),
    Target(
        542988,
        "2SW Wk2: First Responders - Evidence, Response, and Handoff",
        {
            "course files/CCR Materials/2SW/Wk2": frozenset(
                {
                    "2sw-wk2-clinton-lake-evidence-tracker.pdf",
                    "2sw-wk2-first-responder-route-guide.pdf",
                    "2sw-wk2-integrity-career-reflection.pdf",
                    "2sw-wk2-patient-care-report.pdf",
                    "2sw-wk2-pcr-rubric.pdf",
                    "2sw-wk2-trail-simulation-record.pdf",
                }
            ),
            "course files/CCR Materials/2SW/Wk2/Day 1 Visuals": frozenset(
                {"irving-first-responder-programs.png", "law-public-safety-opener.png"}
            ),
            "course files/CCR Materials/2SW/Wk2/Day 2 Visuals": frozenset(
                {f"file-{number}-upright.png" for number in range(1, 7)}
            ),
            "course files/CCR Materials/2SW/Wk2/Day 3 Visuals": frozenset(
                {"injured-trail-intro.png", "slide-2.png", "slide-3.png"}
            ),
            "course files/CCR Materials/2SW/Wk2/Day 4 Visuals": frozenset(
                {
                    "injured-trail-complications.png",
                    "injured-trail-report.png",
                    "slide-2.png",
                    "slide-3.png",
                }
            ),
            "course files/CCR Materials/2SW/Wk2/Day 5 Visuals": frozenset(
                {"law-public-safety-app.png"}
            ),
        },
    ),
)


async def api(client, method, path, *, data=None, params=None):
    response = await client.request(
        method, f"{BASE}/api/v1{path}", data=data, params=params
    )
    response.raise_for_status()
    return response.json() if response.content else None


async def paged(client, path, params=None):
    results = []
    url = f"{BASE}/api/v1{path}"
    query = {"per_page": 100, **(params or {})}
    while url:
        response = await client.get(url, params=query)
        response.raise_for_status()
        results.extend(response.json())
        url = response.links.get("next", {}).get("url")
        query = None
    return results


def local_preflight() -> None:
    module_ids = [target.module_id for target in TARGETS]
    module_names = [target.module_name for target in TARGETS]
    folder_paths = [path for target in TARGETS for path in target.folders]
    if len(module_ids) != len(set(module_ids)) or len(module_names) != len(set(module_names)):
        raise RuntimeError("Duplicate module target in storage repair specification")
    if len(folder_paths) != len(set(folder_paths)):
        raise RuntimeError("Duplicate folder target in storage repair specification")
    if any(not path.startswith("course files/CCR Materials/") for path in folder_paths):
        raise RuntimeError("Storage repair target escapes CCR Materials")


async def folder_by_path(client, path):
    relative = path.removeprefix("course files/")
    encoded = httpx.URL("/" + relative).raw_path.decode("ascii").lstrip("/")
    response = await client.get(
        f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}"
    )
    response.raise_for_status()
    records = response.json()
    if not records:
        raise RuntimeError(f"Canvas folder not found: {path}")
    folder = records[-1]
    full_name = folder.get("full_name") or ""
    if full_name and full_name != path:
        raise RuntimeError(f"Folder path mismatch: expected {path!r}, found {full_name!r}")
    return folder


async def preflight(client):
    modules = await paged(client, f"/courses/{COURSE_ID}/modules")
    by_id = {int(module["id"]): module for module in modules}
    prepared = []
    for target in TARGETS:
        module = by_id.get(target.module_id)
        if not module or module.get("name") != target.module_name:
            found = None if not module else module.get("name")
            raise RuntimeError(
                f"Module identity mismatch for {target.module_id}: {found!r}"
            )
        if module.get("published") is not False:
            raise RuntimeError(f"Module is published: {target.module_id}")
        items = await paged(
            client, f"/courses/{COURSE_ID}/modules/{target.module_id}/items"
        )
        published_items = [item.get("id") for item in items if item.get("published")]
        if published_items:
            raise RuntimeError(
                f"Module {target.module_id} has published items: {published_items}"
            )
        folders = []
        for path, expected_names in target.folders.items():
            folder = await folder_by_path(client, path)
            files = await paged(client, f"/folders/{folder['id']}/files")
            names = {file.get("display_name") or file.get("filename") for file in files}
            missing = expected_names - names
            if missing:
                raise RuntimeError(f"Folder {path} is missing {sorted(missing)}")
            folders.append(
                {
                    "path": path,
                    "folder": folder,
                    "files": files,
                    "expected_names": expected_names,
                    "before_ids": {int(file["id"]) for file in files},
                }
            )
        prepared.append({"target": target, "module": module, "folders": folders})
    return prepared


async def repair(client, prepared):
    changed_folders = 0
    changed_files = 0
    results = []
    for record in prepared:
        target = record["target"]
        folder_results = []
        for entry in record["folders"]:
            folder = entry["folder"]
            if folder.get("locked") is not True:
                await api(client, "PUT", f"/folders/{folder['id']}", data={"locked": "true"})
                changed_folders += 1
            for file in entry["files"]:
                if file.get("locked") is not True:
                    await api(client, "PUT", f"/files/{file['id']}", data={"locked": "true"})
                    changed_files += 1
            current_folder = await api(client, "GET", f"/folders/{folder['id']}")
            current_files = await paged(client, f"/folders/{folder['id']}/files")
            after_ids = {int(file["id"]) for file in current_files}
            names = {
                file.get("display_name") or file.get("filename")
                for file in current_files
            }
            missing = entry["expected_names"] - names
            unlocked = [
                int(file["id"])
                for file in current_files
                if file.get("locked") is not True
            ]
            if (
                current_folder.get("locked") is not True
                or after_ids != entry["before_ids"]
                or missing
                or unlocked
            ):
                raise RuntimeError(
                    f"Final storage invariant failed for {entry['path']}: "
                    f"membership_changed={after_ids != entry['before_ids']} "
                    f"missing={sorted(missing)} unlocked={unlocked}"
                )
            folder_results.append(
                {
                    "path": entry["path"],
                    "id": int(current_folder["id"]),
                    "locked": True,
                    "files": len(current_files),
                }
            )
        module = await api(client, "GET", f"/courses/{COURSE_ID}/modules/{target.module_id}")
        if module.get("published") is not False or module.get("name") != target.module_name:
            raise RuntimeError(f"Module changed during repair: {target.module_id}")
        results.append(
            {
                "module_id": target.module_id,
                "module_name": target.module_name,
                "published": False,
                "folders": folder_results,
            }
        )
    return {
        "dry_run": False,
        "changed_folders": changed_folders,
        "changed_files": changed_files,
        "modules": results,
    }


def summarize_preflight(prepared):
    modules = []
    for record in prepared:
        modules.append(
            {
                "module_id": record["target"].module_id,
                "module_name": record["target"].module_name,
                "published": False,
                "folders": [
                    {
                        "path": entry["path"],
                        "id": int(entry["folder"]["id"]),
                        "locked": entry["folder"].get("locked") is True,
                        "files": len(entry["files"]),
                        "unlocked_files": sum(
                            file.get("locked") is not True for file in entry["files"]
                        ),
                    }
                    for entry in record["folders"]
                ],
            }
        )
    return {
        "dry_run": True,
        "folders_would_lock": sum(
            entry["folder"].get("locked") is not True
            for record in prepared
            for entry in record["folders"]
        ),
        "files_would_lock": sum(
            file.get("locked") is not True
            for record in prepared
            for entry in record["folders"]
            for file in entry["files"]
        ),
        "modules": modules,
    }


async def main(token: str, *, dry_run: bool) -> None:
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        prepared = await preflight(client)
        result = summarize_preflight(prepared) if dry_run else await repair(client, prepared)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    local_preflight()
    unknown = [arg for arg in sys.argv[1:] if arg != "--dry-run"]
    if unknown:
        raise SystemExit(f"Unknown arguments: {' '.join(unknown)}")
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")
    asyncio.run(main(token, dry_run="--dry-run" in sys.argv[1:]))
