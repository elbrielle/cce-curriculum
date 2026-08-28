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

def get_access_token():
    os.makedirs(os.path.dirname(CACHE_FILE), mode=0o700, exist_ok=True)
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    atexit.register(lambda: open(CACHE_FILE, "w").write(cache.serialize()) if cache.has_state_changed else None)

    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            return result['access_token']

    flow = app.initiate_device_flow(scopes=SCOPES)
    print(flow["message"], file=sys.stderr)
    result = app.acquire_token_by_device_flow(flow)
    return result['access_token']

def create_sections(token):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("Finding CCE Notebook...", file=sys.stderr)
    url = "https://graph.microsoft.com/v1.0/me/onenote/notebooks"
    res = requests.get(url, headers=headers, params={"$filter": "displayName eq 'CCE 2026-27 · Lucero'", "$select": "id"}, timeout=10)
    res.raise_for_status()
    notebooks = res.json().get('value', [])
    if not notebooks:
        print("Notebook not found!")
        return
    nb_id = notebooks[0]['id']

    grp_res = requests.get(f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{nb_id}/sectionGroups", headers=headers, timeout=10)
    groups = grp_res.json().get('value', [])
    teacher_only_id = None
    for grp in groups:
        if grp['displayName'] == '_Teacher Only':
            teacher_only_id = grp['id']
            break

    if not teacher_only_id:
        print("'_Teacher Only' section group not found!")
        return

    # Check existing sections to avoid duplicates
    sec_res = requests.get(f"https://graph.microsoft.com/v1.0/me/onenote/sectionGroups/{teacher_only_id}/sections", headers=headers, timeout=10)
    existing_sections = [s['displayName'] for s in sec_res.json().get('value', [])]

    sections_to_create = ["Focus Notes", "Evidence and Reflection", "CCE Work"]

    for sec_name in sections_to_create:
        if sec_name in existing_sections:
            print(f"Section '{sec_name}' already exists.")
            continue

        print(f"Creating section: {sec_name}")
        post_res = requests.post(
            f"https://graph.microsoft.com/v1.0/me/onenote/sectionGroups/{teacher_only_id}/sections",
            headers=headers,
            json={"displayName": sec_name},
            timeout=10
        )
        if post_res.status_code == 201:
            print(f"  -> Successfully created!")
        else:
            print(f"  -> Failed: {post_res.text}")

if __name__ == "__main__":
    token = get_access_token()
    create_sections(token)
