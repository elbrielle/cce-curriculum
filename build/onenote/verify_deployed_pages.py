"""Read back selected OneNote pages and verify the native worksheet contract."""

import argparse
import re
import requests

from deploy_worksheet import find_pages_by_title, get_access_token


def verify_page(token, section_id, title):
    headers = {"Authorization": f"Bearer {token}"}
    matches = find_pages_by_title(token, section_id, title)
    if len(matches) != 1:
        raise RuntimeError(f"Expected one OneNote page titled {title!r}; found {len(matches)}")

    page = matches[0]
    content_response = requests.get(
        f"https://graph.microsoft.com/v1.0/me/onenote/pages/{page['id']}/content",
        headers=headers,
        timeout=30,
    )
    content_response.raise_for_status()
    content = content_response.text
    table_tags = re.findall(r"<table\b[^>]*>.*?</table>", content, flags=re.IGNORECASE | re.DOTALL)
    table_widths_ok = []
    for table in table_tags:
        first_row = re.search(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.IGNORECASE | re.DOTALL)
        if not first_row:
            table_widths_ok.append(False)
            continue
        widths = [int(value) for value in re.findall(r"width:\s*(\d+)(?:px)?", first_row.group(1), re.I)]
        table_widths_ok.append(bool(widths) and 849 <= sum(widths) <= 851)
    checks = {
        "absolute_850_tables": bool(table_tags) and all(table_widths_ok),
        "bilingual_word_bank": "Banco de palabras" in content,
        "english_sentence_stems": "because" in content,
        "spanish_sentence_stems": "porque" in content,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError(
            f"OneNote page {title!r} failed read-back checks: {failures}; "
            f"table_widths_ok={table_widths_ok}"
        )
    return {"title": page["title"], "id": page["id"], "checks": checks}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--section-id", required=True)
    parser.add_argument("--title", action="append", required=True)
    args = parser.parse_args()

    token = get_access_token()
    for title in args.title:
        result = verify_page(token, args.section_id, title)
        print(f"PASS: {result['title']} ({result['id']})")


if __name__ == "__main__":
    main()
