import argparse
import sys
import os
import atexit
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
    if not section_id:
        raise ValueError("A reviewed OneNote section ID is required; default-notebook writes are disabled")

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

    matches = find_pages_by_title(token, section_id, title)
    if len(matches) > 1:
        raise RuntimeError(f"Refusing to create duplicate OneNote pages titled {title!r}")
    if matches:
        raise RuntimeError(
            f"Refusing to partially update existing OneNote page {title!r}; "
            "use a new reviewed title or replace the complete page manually"
        )

    endpoint = f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages"

    response = requests.post(
        endpoint,
        headers=headers,
        data=html_payload.encode('utf-8'),
        timeout=30,
    )
    response.raise_for_status()

    page_info = response.json()
    print(f"Successfully created OneNote Page: {page_info.get('links', {}).get('oneNoteClientUrl', {}).get('href')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create reviewed HTML worksheet masters in a specific OneNote section.")
    parser.add_argument("--title", required=True, help="Title of the OneNote page")
    parser.add_argument("--html-file", required=True, help="Path to the HTML file containing the worksheet content")
    parser.add_argument("--section-id", required=True, help="Reviewed OneNote Section ID that will receive the new page")

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
