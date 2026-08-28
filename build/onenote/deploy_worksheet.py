import argparse
import sys
import os
import atexit
import re
import time
import msal
import requests

AUTHORITY = "https://login.microsoftonline.com/common"
CLIENT_ID = "24c79ddc-5d02-4334-9603-24f1e8eb8dfb"
SCOPES = ["Notes.ReadWrite.All"]
CACHE_FILE = os.environ.get(
    "CCE_ONENOTE_CACHE",
    os.path.join(os.path.expanduser("~"), ".cache", "cce-onenote", "msal_cache.bin"),
)


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), mode=0o700, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as handle:
        handle.write(cache.serialize())
    os.chmod(CACHE_FILE, 0o600)

def get_access_token():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    atexit.register(lambda: _save_cache(cache) if cache.has_state_changed else None)

    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            return result['access_token']

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise ValueError("Failed to create device flow")

    print(flow["message"], file=sys.stderr)
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception(f"Failed to acquire token: {result.get('error')} - {result.get('error_description')}")

def find_pages_by_title(token, section_id, title):
    """List a section and compare titles locally.

    Graph's title filter can lag behind page creation. A filtered upsert can
    therefore create a duplicate several minutes after the first page exists.
    """
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages"
    params = {"$select": "id,title,createdDateTime,lastModifiedDateTime", "$top": "100"}
    matches = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        matches.extend(page for page in payload.get("value", []) if page.get("title") == title)
        url = payload.get("@odata.nextLink")
        params = None
    return matches


def deploy_to_onenote(token, section_id, title, html_content):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/html'
    }

    # Accept complete OneNote-ready HTML files without nesting a second document.
    if "<html" in html_content.lower() and "<head" in html_content.lower():
        html_payload = html_content
    else:
        html_payload = f"""
        <!DOCTYPE html>
        <html>
          <head><title>{title}</title></head>
          <body>{html_content}</body>
        </html>
        """

    # Update the existing teacher master in place when the exact title already exists.
    if section_id:
        matches = find_pages_by_title(token, section_id, title)
        if len(matches) > 1:
            raise RuntimeError(f"Refusing to update duplicate OneNote pages titled {title!r}")
        if matches:
            page_id = matches[0]["id"]
            current_response = requests.get(
                f"https://graph.microsoft.com/v1.0/me/onenote/pages/{page_id}/content",
                headers={'Authorization': f'Bearer {token}'},
                params={"includeIDs": "true"},
                timeout=30,
            )
            current_response.raise_for_status()
            current_tables = re.findall(r"<table\b[^>]*>.*?</table>", current_response.text, re.I | re.S)
            source_tables = re.findall(r"<table\b[^>]*>.*?</table>", html_content, re.I | re.S)
            if len(current_tables) != len(source_tables):
                raise RuntimeError(
                    f"Refusing partial OneNote update for {title!r}: "
                    f"live tables={len(current_tables)} source tables={len(source_tables)}"
                )
            commands = []
            for current_table, source_table in zip(current_tables, source_tables):
                match = re.search(r'\bid="([^"]+)"', current_table)
                if not match:
                    raise RuntimeError(f"OneNote did not return a generated table ID for {title!r}")
                commands.append({"target": match.group(1), "action": "replace", "content": source_table})
            patch_response = requests.patch(
                f"https://graph.microsoft.com/v1.0/me/onenote/pages/{page_id}/content",
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
                json=commands,
                timeout=30,
            )
            patch_response.raise_for_status()
            print(f"Successfully updated OneNote Page: {title}")
            return

    # Give a just-created page one final chance to appear before creating a new
    # master. This keeps reruns idempotent even when Graph indexing is delayed.
    if section_id:
        for _ in range(2):
            time.sleep(1.5)
            matches = find_pages_by_title(token, section_id, title)
            if len(matches) > 1:
                raise RuntimeError(f"Refusing to create duplicate OneNote pages titled {title!r}")
            if matches:
                raise RuntimeError(
                    f"OneNote page {title!r} appeared during the create guard; rerun to update it in place"
                )

    # If section_id is provided, deploy to that section. Otherwise, deploy to the default notebook.
    endpoint = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages" if section_id else "https://graph.microsoft.com/v1.0/me/onenote/pages"

    response = requests.post(endpoint, headers=headers, data=html_payload.encode('utf-8'))
    response.raise_for_status()

    page_info = response.json()
    print(f"Successfully created OneNote Page: {page_info.get('links', {}).get('oneNoteClientUrl', {}).get('href')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy HTML worksheets natively to Microsoft OneNote using the Graph API.")
    parser.add_argument("--title", required=True, help="Title of the OneNote page")
    parser.add_argument("--html-file", required=True, help="Path to the HTML file containing the worksheet content")
    parser.add_argument("--section-id", required=False, help="Optional OneNote Section ID to deploy the page to")

    args = parser.parse_args()

    with open(args.html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        print("Acquiring Microsoft Graph access token...", file=sys.stderr)
        token = get_access_token()
        print(f"Deploying '{args.title}' to OneNote...", file=sys.stderr)
        deploy_to_onenote(token, args.section_id, args.title, content)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
