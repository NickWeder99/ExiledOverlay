# api/poe_api.py
import requests

def fetch_gear(account_name, character_name, poesessid=None):
    url = "https://api.pathofexile.com/character-window/get-items"
    params = {"accountName": account_name, "character": character_name}
    headers = {
        "User-Agent": "PoE Overlay Tool by Nick",
        "Accept": "application/json"
    }
    cookies = {"POESESSID": poesessid} if poesessid else {}

    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

    data = response.json()
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
