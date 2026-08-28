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
    if "user_code" not in flow:
        raise ValueError("Failed to create device flow")

    print(flow["message"], file=sys.stderr)
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result['access_token']
    else:
        raise Exception(f"Failed to acquire token")

def list_notebooks_and_sections(token):
    headers = {'Authorization': f'Bearer {token}'}

    print("Fetching Notebooks...", file=sys.stderr)
    notebooks_url = "https://graph.microsoft.com/v1.0/me/onenote/notebooks"
    response = requests.get(notebooks_url, headers=headers)
    response.raise_for_status()

    notebooks = response.json().get('value', [])
    for nb in notebooks:
        print(f"\nNotebook: {nb['displayName']}")

        # Fetch root sections for this notebook
        sections_url = f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{nb['id']}/sections"
        sec_response = requests.get(sections_url, headers=headers)
        if sec_response.status_code == 200:
            sections = sec_response.json().get('value', [])
            for sec in sections:
                print(f"  - Section: {sec['displayName']} | ID: {sec['id']}")

        # Fetch section groups (like _Teacher Only)
        groups_url = f"https://graph.microsoft.com/v1.0/me/onenote/notebooks/{nb['id']}/sectionGroups"
        grp_response = requests.get(groups_url, headers=headers)
        if grp_response.status_code == 200:
            groups = grp_response.json().get('value', [])
            for grp in groups:
                print(f"  > Section Group: {grp['displayName']}")
                # Fetch sections within this group
                gsec_url = f"https://graph.microsoft.com/v1.0/me/onenote/sectionGroups/{grp['id']}/sections"
                gsec_response = requests.get(gsec_url, headers=headers)
                if gsec_response.status_code == 200:
                    gsections = gsec_response.json().get('value', [])
                    for gsec in gsections:
                        print(f"      - Section: {gsec['displayName']} | ID: {gsec['id']}")

if __name__ == "__main__":
    try:
        token = get_access_token()
        list_notebooks_and_sections(token)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
