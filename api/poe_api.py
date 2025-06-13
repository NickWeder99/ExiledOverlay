# api/poe_api.py
import json
from urllib import request, parse

def fetch_gear(account_name, character_name, poesessid=None):
    url = "https://api.pathofexile.com/character-window/get-items"
    params = {"accountName": account_name, "character": character_name}
    headers = {
        "User-Agent": "PoE Overlay Tool by Nick",
        "Accept": "application/json",
    }
    query = parse.urlencode(params)
    req = request.Request(f"{url}?{query}", headers=headers)
    if poesessid:
        req.add_header("Cookie", f"POESESSID={poesessid}")

    with request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed to fetch data: {resp.status}")
        data = json.load(resp)
    gear = {}
    for item in data.get("items", []):
        slot = item.get("inventoryId")
        gear[slot] = {
            "name": item.get("name", ""),
            "type": item.get("typeLine", "Unknown"),
            "icon": item.get("icon"),
            "rarity": item.get("frameType", 0),
            "implicitMods": item.get("implicitMods", []),
            "explicitMods": item.get("explicitMods", [])
        }
    return gear


def _api_request(url, token=None):
    """Internal helper to perform an authenticated GET request."""
    headers = {
        "User-Agent": "ExiledOverlay",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, headers=headers)
    with request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Failed request: {resp.status}")
        return json.load(resp)


def fetch_currency(token, league, currencies):
    """Return currency counts for the logged in account."""
    base = "https://api.pathofexile.com"
    tabs_url = f"{base}/profile/stash-tabs?league={parse.quote(league)}"
    data = _api_request(tabs_url, token)
    tab_ids = [t["id"] for t in data.get("tabs", [])]

    counts = {c: 0 for c in currencies}
    for tab_id in tab_ids:
        items_url = f"{base}/stash/{tab_id}?league={parse.quote(league)}"
        tab_data = _api_request(items_url, token)
        for item in tab_data.get("items", []):
            name = item.get("typeLine")
            if name in counts:
                counts[name] += int(item.get("stackSize", 1))
    return counts


def fetch_item_count(token, league, item_name):
    """Return the total count of ``item_name`` across all stashes."""
    base = "https://api.pathofexile.com"
    tabs_url = f"{base}/profile/stash-tabs?league={parse.quote(league)}"
    data = _api_request(tabs_url, token)
    tab_ids = [t["id"] for t in data.get("tabs", [])]

    total = 0
    for tab_id in tab_ids:
        items_url = f"{base}/stash/{tab_id}?league={parse.quote(league)}"
        tab_data = _api_request(items_url, token)
        for item in tab_data.get("items", []):
            if item.get("typeLine") == item_name or item.get("name") == item_name:
                total += int(item.get("stackSize", 1))
    return total
<<<<<<< 7mtxb8-codex/füge-währungslogik-hinzu
=======

>>>>>>> main
