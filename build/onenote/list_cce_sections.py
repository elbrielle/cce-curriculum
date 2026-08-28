import sys
import os
import atexit
import msal
import requests

AUTHORITY = "https://login.microsoftonline.com/common"
CLIENT_ID = "24c79ddc-5d02-4334-9603-24f1e8eb8dfb"
SCOPES = ["Notes.Read.All"]
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

def find_cce_notebook(token):
    headers = {'Authorization': f'Bearer {token}'}
    print("Fetching Notebooks...", file=sys.stderr)
    url = "https://graph.microsoft.com/v1.0/me/onenote/notebooks"
    # Find specific notebook by name
    res = requests.get(url, headers=headers, params={"$filter": "displayName eq 'CCE 2026-27 · Lucero'", "$select": "id,displayName"}, timeout=10)
    res.raise_for_status()
    notebooks = res.json().get('value', [])
    if not notebooks:
        print("Notebook not found!")
        return
    nb_id = notebooks[0]['id']

    print(f"Found Notebook: {notebooks[0]['displayName']}")
    # Fetch section groups
    grp_res = requests.get(f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{nb_id}/sectionGroups", headers=headers, timeout=10)
    groups = grp_res.json().get('value', [])
    for grp in groups:
        print(f"\nSection Group: {grp['displayName']}")
        sec_res = requests.get(f"https://graph.microsoft.com/v1.0/me/onenote/sectionGroups/{grp['id']}/sections", headers=headers, timeout=10)
        sections = sec_res.json().get('value', [])
        for sec in sections:
            print(f"  - Section: {sec['displayName']} | ID: {sec['id']}")

if __name__ == "__main__":
    token = get_access_token()
    find_cce_notebook(token)
