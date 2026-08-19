"""Reconcile only the Week 0 Day 1-Day 3 Canvas pages and support files.

This is intentionally narrower than ``build_wk0.py``. It preserves the live
module and page publication states, does not touch module items or assessments,
and reads the Canvas token only from stdin.
"""

import asyncio
import json
import sys

import httpx

from build_wk0 import (
    ASSET_ROOT,
    BASE,
    COURSE_ID,
    DECK_ROOT,
    GOOGLE_DECK_COPY_URLS,
    GOOGLE_GOAL_COPY_URL,
    MODULE_ID,
    MODULE_NAME,
    TEMPLATES,
    api,
    lock_folder_files,
    paged,
    render_template,
    resolve_folder_files,
    upload,
)


DAYS = {
    1: {
        "teacher_url": "teacher-day-1-facilitator-guide",
        "teacher_title": "TEACHER: Day 1 Facilitator Guide",
        "student_url": "student-1sw-wk0-day-1-cce-notebook-and-first-week-goal",
        "student_title": "STUDENT: 1SW Wk0 Day 1 - CCE Notebook and First-Week Goal",
        "deck_name": "cce-week1-day1-source-grounded.pptx",
        "visual_names": (),
    },
    2: {
        "teacher_url": "teacher-day-2-facilitator-guide",
        "teacher_title": "TEACHER: Day 2 Facilitator Guide",
        "student_url": "student-1sw-wk0-day-2-who-are-you-at-work",
        "student_title": "STUDENT: 1SW Wk0 Day 2 - Who Are You at Work?",
        "deck_name": "cce-week1-day2-source-grounded.pptx",
        "visual_names": (
            "irving-isd-ccmr-programs-of-study.png",
            "six-core-personality-types.png",
            "open-hats-and-ladders-discover-your-core.png",
        ),
    },
    3: {
        "teacher_url": "teacher-day-3-facilitator-guide",
        "teacher_title": "TEACHER: Day 3 Facilitator Guide",
        "student_url": "student-1sw-wk0-day-3-work-values-and-building-blocks",
        "student_title": "STUDENT: 1SW Wk0 Day 3 - Work Values and Building Blocks",
        "deck_name": "cce-week1-day3-source-grounded.pptx",
        "visual_names": (
            "my-building-blocks-introduction.png",
            "my-building-blocks-inventory.png",
            "my-building-blocks-skills.png",
            "open-hats-and-ladders-discover-your-work-values.png",
        ),
    },
}


def preflight() -> None:
    required = []
    for day, spec in DAYS.items():
        required.extend(
            TEMPLATES / f"wk0-day{day}-{role}.html"
            for role in ("teacher", "student")
        )
        required.append(DECK_ROOT / spec["deck_name"])
        required.extend(
            ASSET_ROOT / f"day{day}" / name for name in spec["visual_names"]
        )
    required.extend(
        (
            DECK_ROOT / "cce-week1-day1-source-grounded.pptx",
            ASSET_ROOT.parents[4] / "docs/resources/worksheets/cce-first-week-goal-setting.pdf",
            ASSET_ROOT.parents[4] / "docs/resources/worksheets/cce-first-week-goal-setting.docx",
        )
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"Day 1-3 local preflight failed; missing={missing}")


async def exact_folder(client, folder_path):
    encoded = httpx.URL("/" + folder_path).raw_path.decode("ascii").lstrip("/")
    response = await client.get(
        f"{BASE}/api/v1/courses/{COURSE_ID}/folders/by_path/{encoded}"
    )
    response.raise_for_status()
    matches = response.json()
    if not matches:
        raise RuntimeError(f"Canvas folder is missing: {folder_path}")
    folder = matches[-1]
    if folder.get("full_name") != f"course files/{folder_path}":
        raise RuntimeError(
            f"Unexpected Canvas folder path: {folder.get('full_name')!r}"
        )
    # Folder chains that hold embedded images are intentionally unlocked by
    # normalize_embedded_image_access.py so students can load <img> files; only
    # non-image support files keep their own file-level locks. Do not require a
    # locked folder here.
    return folder


async def exact_page(client, url, title):
    page = await api(client, "GET", f"/courses/{COURSE_ID}/pages/{url}")
    if page.get("url") != url or page.get("title") != title:
        raise RuntimeError(
            f"Canvas page identity mismatch for {url}: "
            f"url={page.get('url')!r} title={page.get('title')!r}"
        )
    return page


async def assert_replacement(client, before_id, after_id, label):
    """Canvas ``on_duplicate=overwrite`` replaces the attachment: the old ID keeps
    resolving (redirecting) to the new record. Accept identical IDs or a resolved
    replacement; reject anything else (which would mean a duplicate file)."""
    if before_id == after_id:
        return
    resolved = await api(client, "GET", f"/files/{before_id}")
    if resolved.get("id") != after_id:
        raise RuntimeError(
            f"{label} overwrite created a duplicate instead of a replacement: "
            f"before={before_id} after={after_id} resolved={resolved.get('id')}"
        )


def page_payload(page, body):
    return {
        "wiki_page[title]": page["title"],
        "wiki_page[body]": body,
        "wiki_page[published]": "true" if page.get("published") else "false",
        "wiki_page[editing_roles]": page.get("editing_roles") or "teachers",
    }


async def main() -> None:
    preflight()
    token = sys.stdin.readline().strip()
    if not token:
        raise SystemExit("Canvas token required on stdin")

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"}, timeout=120
    ) as client:
        modules = await paged(client, f"/courses/{COURSE_ID}/modules")
        matches = [module for module in modules if module.get("name") == MODULE_NAME]
        if len(matches) != 1 or matches[0].get("id") != MODULE_ID:
            raise RuntimeError(
                f"Expected one Wk0 module id={MODULE_ID}; "
                f"found={[(m.get('id'), m.get('name')) for m in matches]}"
            )
        module_before = matches[0]

        pages_before = {}
        for day, spec in DAYS.items():
            pages_before[day] = {
                "teacher": await exact_page(
                    client, spec["teacher_url"], spec["teacher_title"]
                ),
                "student": await exact_page(
                    client, spec["student_url"], spec["student_title"]
                ),
            }

        support_folder = await exact_folder(client, "CCR Materials/1SW/Wk0")
        _, support_files_before = await lock_folder_files(
            client,
            support_folder,
            [DAYS[day]["deck_name"] for day in DAYS]
            + ["cce-first-week-goal-setting.pdf", "cce-first-week-goal-setting.docx"],
        )
        support_before = resolve_folder_files(
            support_files_before,
            {
                "D1_DECK": DAYS[1]["deck_name"],
                "D2_DECK": DAYS[2]["deck_name"],
                "D3_DECK": DAYS[3]["deck_name"],
                "D1_GOAL": "cce-first-week-goal-setting.pdf",
                "D1_GOAL_DOCX": "cce-first-week-goal-setting.docx",
                "D3_WORD_BANK": "building-blocks-word-bank.pdf",
                "D3_WORD_BANK_BI": "building-blocks-word-bank-bilingual.pdf",
            },
        )
        for day, key in ((1, "D1_DECK"), (2, "D2_DECK"), (3, "D3_DECK")):
            uploaded = await upload(
                client,
                DECK_ROOT / DAYS[day]["deck_name"],
                "course files/CCR Materials/1SW/Wk0",
            )
            await assert_replacement(client, support_before[key].get("id"), uploaded.get("id"), f"Day {day} deck")

        _, support_files_after = await lock_folder_files(
            client,
            support_folder,
            [DAYS[day]["deck_name"] for day in DAYS]
            + ["cce-first-week-goal-setting.pdf", "cce-first-week-goal-setting.docx"],
        )
        support = resolve_folder_files(
            support_files_after,
            {
                "D1_DECK": DAYS[1]["deck_name"],
                "D2_DECK": DAYS[2]["deck_name"],
                "D3_DECK": DAYS[3]["deck_name"],
                "D1_GOAL": "cce-first-week-goal-setting.pdf",
                "D1_GOAL_DOCX": "cce-first-week-goal-setting.docx",
                "D3_WORD_BANK": "building-blocks-word-bank.pdf",
                "D3_WORD_BANK_BI": "building-blocks-word-bank-bilingual.pdf",
            },
        )

        visuals = {}
        for day, spec in DAYS.items():
            if not spec["visual_names"]:
                visuals[day] = {}
                continue
            folder = await exact_folder(
                client, f"CCR Materials/1SW/Wk0/Day {day} Visuals"
            )
            _, files_before = await lock_folder_files(
                client, folder, spec["visual_names"]
            )
            before = resolve_folder_files(
                files_before, {name: name for name in spec["visual_names"]}
            )
            route_name = (
                "open-hats-and-ladders-discover-your-core.png"
                if day == 2
                else "open-hats-and-ladders-discover-your-work-values.png"
            )
            uploaded = await upload(
                client,
                ASSET_ROOT / f"day{day}" / route_name,
                f"course files/CCR Materials/1SW/Wk0/Day {day} Visuals",
            )
            await assert_replacement(client, before[route_name].get("id"), uploaded.get("id"), f"Day {day} route image")
            _, files_after = await lock_folder_files(
                client, folder, spec["visual_names"]
            )
            visuals[day] = resolve_folder_files(
                files_after, {name: name for name in spec["visual_names"]}
            )

        values = {
            1: {
                "DECK_FILE_ID": support["D1_DECK"]["id"],
                "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[1],
                "GOAL_FILE_ID": support["D1_GOAL"]["id"],
                "GOAL_DOCX_FILE_ID": support["D1_GOAL_DOCX"]["id"],
                "GOOGLE_GOAL_COPY_URL": GOOGLE_GOAL_COPY_URL,
            },
            2: {
                "DECK_FILE_ID": support["D2_DECK"]["id"],
                "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[2],
                "WORKBOOK_IMAGE_ID": visuals[2][
                    "irving-isd-ccmr-programs-of-study.png"
                ]["id"],
                "TYPES_IMAGE_ID": visuals[2]["six-core-personality-types.png"][
                    "id"
                ],
                "APP_IMAGE_ID": visuals[2][
                    "open-hats-and-ladders-discover-your-core.png"
                ]["id"],
            },
            3: {
                "DECK_FILE_ID": support["D3_DECK"]["id"],
                "GOOGLE_DECK_COPY_URL": GOOGLE_DECK_COPY_URLS[3],
                "WORK_VALUES_IMAGE_ID": visuals[3][
                    "open-hats-and-ladders-discover-your-work-values.png"
                ]["id"],
                "BUILDING_BLOCKS_IMAGE_ID": visuals[3][
                    "my-building-blocks-inventory.png"
                ]["id"],
                "WORD_BANK_FILE_ID": support["D3_WORD_BANK"]["id"],
                "WORD_BANK_BILINGUAL_FILE_ID": support["D3_WORD_BANK_BI"]["id"],
            },
        }

        for day, spec in DAYS.items():
            template_values = {
                "COURSE_ID": COURSE_ID,
                "STUDENT_PAGE_URL": spec["student_url"],
                **values[day],
            }
            for role in ("student", "teacher"):
                page = pages_before[day][role]
                body = render_template(
                    f"wk0-day{day}-{role}.html", template_values
                )
                await api(
                    client,
                    "PUT",
                    f"/courses/{COURSE_ID}/pages/{page['url']}",
                    data=page_payload(page, body),
                )

        module_after = await api(
            client, "GET", f"/courses/{COURSE_ID}/modules/{MODULE_ID}"
        )
        if module_after.get("published") != module_before.get("published"):
            raise RuntimeError("Wk0 module publication state changed")

        pages_after = {}
        stale_fragments = (
            "13hsWv5_pShfI0bzmxAgaLLREGLGvM_Nwscpnph5WLKo",
            "1UX3uGRnXlVI8TW1wbJAlS28pXy4hyfQnbvillK7xRdk",
            "ClassLink",
            "close or refresh",
            "save and reopen",
            "save-and-reopen",
        )
        for day, spec in DAYS.items():
            pages_after[day] = {}
            for role in ("teacher", "student"):
                before = pages_before[day][role]
                after = await exact_page(
                    client,
                    before["url"],
                    before["title"],
                )
                if after.get("published") != before.get("published"):
                    raise RuntimeError(
                        f"Day {day} {role} page publication state changed"
                    )
                body = after.get("body") or ""
                # Only the teacher guide links the Google deck copy; student pages do not.
                if role == "teacher" and GOOGLE_DECK_COPY_URLS[day] not in body:
                    raise RuntimeError(
                        f"Day {day} {role} page is missing the current Google deck"
                    )
                if any(fragment in body for fragment in stale_fragments):
                    raise RuntimeError(
                        f"Day {day} {role} page contains stale route or workflow text"
                    )
                pages_after[day][role] = after

        print(
            json.dumps(
                {
                    "module": {
                        "id": MODULE_ID,
                        "published_before": module_before.get("published"),
                        "published_after": module_after.get("published"),
                    },
                    "pages": {
                        str(day): {
                            role: {
                                "url": page["url"],
                                "published": page.get("published"),
                            }
                            for role, page in roles.items()
                        }
                        for day, roles in pages_after.items()
                    },
                    "decks": {
                        "1": support["D1_DECK"]["id"],
                        "2": support["D2_DECK"]["id"],
                        "3": support["D3_DECK"]["id"],
                    },
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
