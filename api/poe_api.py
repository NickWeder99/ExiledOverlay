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
