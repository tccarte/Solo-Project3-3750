#!/usr/bin/env python3
"""
Seed via HTTP — no psycopg2 required.
Usage: python http_seed.py https://your-app.up.railway.app
"""
import sys
import json
import ssl
import urllib.request
import urllib.error

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if len(sys.argv) < 2:
    print("Usage: python http_seed.py https://your-app.up.railway.app")
    sys.exit(1)

BASE = sys.argv[1].rstrip("/")

CARDS = [
    {"name": "Lightning Bolt",      "set": "M11",  "typeLine": "Instant",                    "manaValue": 1, "colors": "R", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/e/3/e3285d0e-4633-4b52-a784-d6aced05a842.jpg"},
    {"name": "Counterspell",         "set": "2XM",  "typeLine": "Instant",                    "manaValue": 2, "colors": "U", "rarity": "Uncommon", "quantity": 1, "condition": "LP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/8/c/8c49dc7e-fa4a-4b84-a0de-7ca18d1f5848.jpg"},
    {"name": "Llanowar Elves",       "set": "M19",  "typeLine": "Creature — Elf Druid",       "manaValue": 1, "colors": "G", "rarity": "Common",   "quantity": 4, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/f/6/f6af56a1-8e95-4377-9bd0-2d4903e8fdc5.jpg"},
    {"name": "Swords to Plowshares", "set": "2XM",  "typeLine": "Instant",                    "manaValue": 1, "colors": "W", "rarity": "Uncommon", "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/3/e/3e4f3b06-4a0c-4b51-8b67-b89c3a93d6f1.jpg"},
    {"name": "Thoughtseize",         "set": "2XM",  "typeLine": "Sorcery",                    "manaValue": 1, "colors": "B", "rarity": "Rare",     "quantity": 1, "condition": "MP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/b/0/b0faa7f2-b547-42c4-a810-839da50dadfe.jpg"},
    {"name": "Sol Ring",             "set": "CMM",  "typeLine": "Artifact",                   "manaValue": 1, "colors": "C", "rarity": "Uncommon", "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/f/0/f0e29ac2-0428-4d72-a26c-ac609e8e0e54.jpg"},
    {"name": "Arcane Signet",        "set": "ELD",  "typeLine": "Artifact",                   "manaValue": 2, "colors": "C", "rarity": "Common",   "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/0/a/0a6a0d74-6f55-4a22-af6b-65b8ff9e1efb.jpg"},
    {"name": "Path to Exile",        "set": "2XM",  "typeLine": "Instant",                    "manaValue": 1, "colors": "W", "rarity": "Uncommon", "quantity": 2, "condition": "LP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/0/2/02ea6e46-f775-4068-935f-70b2d29eb6d1.jpg"},
    {"name": "Cultivate",            "set": "M21",  "typeLine": "Sorcery",                    "manaValue": 3, "colors": "G", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/e/e/ee4ae30a-7b67-469f-8bd5-fc18e72476d9.jpg"},
    {"name": "Kodama's Reach",       "set": "CMM",  "typeLine": "Sorcery",                    "manaValue": 3, "colors": "G", "rarity": "Common",   "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/d/e/de58f1c8-cc11-4afc-9fea-1b42c0765aa3.jpg"},
    {"name": "Shivan Dragon",        "set": "M10",  "typeLine": "Creature — Dragon",          "manaValue": 6, "colors": "R", "rarity": "Rare",     "quantity": 1, "condition": "LP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/1/4/1498cfe2-facc-4db7-b93e-e8b85ea25b1f.jpg"},
    {"name": "Serra Angel",          "set": "M10",  "typeLine": "Creature — Angel",           "manaValue": 5, "colors": "W", "rarity": "Uncommon", "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/9/b/9bb35bda-4ff0-46b6-a5f5-b7e79a95e498.jpg"},
    {"name": "Doom Blade",           "set": "M12",  "typeLine": "Instant",                    "manaValue": 2, "colors": "B", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/a/a/aa0f2e76-47a7-4cee-b76d-399bda64d93e.jpg"},
    {"name": "Opt",                  "set": "XLN",  "typeLine": "Instant",                    "manaValue": 1, "colors": "U", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/0/e/0e2a37f8-c640-40c7-a2f3-4a3d5e42a7eb.jpg"},
    {"name": "Giant Growth",         "set": "M19",  "typeLine": "Instant",                    "manaValue": 1, "colors": "G", "rarity": "Common",   "quantity": 3, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/5/8/5876e7fc-e88d-4a1c-ba67-29a4e08c7c54.jpg"},
    {"name": "Wrath of God",         "set": "2ED",  "typeLine": "Sorcery",                    "manaValue": 4, "colors": "W", "rarity": "Rare",     "quantity": 1, "condition": "HP", "notes": "Old copy", "imageUrl": "https://cards.scryfall.io/normal/front/1/e/1e8c2b08-0dcd-4f1c-8a30-3bfa39e87ff9.jpg"},
    {"name": "Brainstorm",           "set": "EMA",  "typeLine": "Instant",                    "manaValue": 1, "colors": "U", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/f/a/fa50b490-c4c1-40ba-8aea-74dbf9d65aca.jpg"},
    {"name": "Dark Ritual",          "set": "A25",  "typeLine": "Instant",                    "manaValue": 1, "colors": "B", "rarity": "Common",   "quantity": 1, "condition": "LP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/d/1/d14e0ed2-e69d-4f86-a16c-d1d20b17aa0a.jpg"},
    {"name": "Faithless Looting",    "set": "UMA",  "typeLine": "Sorcery",                    "manaValue": 1, "colors": "R", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/e/7/e79f2a0d-01e8-4db4-b0a2-c5b84a93e7e7.jpg"},
    {"name": "Birds of Paradise",    "set": "M12",  "typeLine": "Creature — Bird",            "manaValue": 1, "colors": "G", "rarity": "Rare",     "quantity": 1, "condition": "MP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/7/2/72edd889-5a8c-48a0-bde4-71085413f6d3.jpg"},
    {"name": "Supreme Verdict",      "set": "RTR",  "typeLine": "Sorcery",                    "manaValue": 4, "colors": "M", "rarity": "Rare",     "quantity": 1, "condition": "NM", "notes": "UW",  "imageUrl": "https://cards.scryfall.io/normal/front/6/0/6006dfc5-cf8a-4e94-92f8-dc0b01b4f56b.jpg"},
    {"name": "Terminate",            "set": "ARB",  "typeLine": "Instant",                    "manaValue": 2, "colors": "M", "rarity": "Uncommon", "quantity": 1, "condition": "LP", "notes": "BR",  "imageUrl": "https://cards.scryfall.io/normal/front/9/d/9d8d0017-9e33-4c79-b4c2-ff0a2c7fac54.jpg"},
    {"name": "Coiling Oracle",       "set": "GK1",  "typeLine": "Creature — Snake Elf Druid", "manaValue": 2, "colors": "M", "rarity": "Uncommon", "quantity": 1, "condition": "NM", "notes": "UG",  "imageUrl": "https://cards.scryfall.io/normal/front/5/e/5e03d8a5-1519-4d40-b3d3-30d3cc4cded1.jpg"},
    {"name": "Boros Charm",          "set": "GTC",  "typeLine": "Instant",                    "manaValue": 2, "colors": "M", "rarity": "Uncommon", "quantity": 1, "condition": "NM", "notes": "RW",  "imageUrl": "https://cards.scryfall.io/normal/front/9/2/92f9d6f3-7d18-478d-b8e7-25ec4e001cf0.jpg"},
    {"name": "Sphinx's Revelation",  "set": "RTR",  "typeLine": "Instant",                    "manaValue": 3, "colors": "M", "rarity": "Mythic",   "quantity": 1, "condition": "LP", "notes": "XUW", "imageUrl": "https://cards.scryfall.io/normal/front/5/b/5ba8f5a0-9ede-4e17-b53d-b1882f6c8e80.jpg"},
    {"name": "Wastes",               "set": "OGW",  "typeLine": "Basic Land",                 "manaValue": 0, "colors": "C", "rarity": "Common",   "quantity": 5, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/5/9/59a2536b-ee4a-4a9c-9ab2-de3613c9c2d5.jpg"},
    {"name": "Evolving Wilds",       "set": "M20",  "typeLine": "Land",                       "manaValue": 0, "colors": "C", "rarity": "Common",   "quantity": 2, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/d/d/dd5adc8a-3d69-4e00-8789-62e2e0b6f9d5.jpg"},
    {"name": "Command Tower",        "set": "CMM",  "typeLine": "Land",                       "manaValue": 0, "colors": "C", "rarity": "Common",   "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/0/d/0d8c77b6-bd5e-4fe8-8b15-1f15d08b6d7e.jpg"},
    {"name": "Mystic Remora",        "set": "ICE",  "typeLine": "Enchantment",                "manaValue": 1, "colors": "U", "rarity": "Rare",     "quantity": 1, "condition": "MP", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/2/1/21ab8c2a-0e58-4cc6-956e-48d74e0c5a3f.jpg"},
    {"name": "Smothering Tithe",     "set": "RNA",  "typeLine": "Enchantment",                "manaValue": 4, "colors": "W", "rarity": "Rare",     "quantity": 1, "condition": "NM", "notes": "",    "imageUrl": "https://cards.scryfall.io/normal/front/a/2/a2c45e67-2fbd-4b13-9c1d-5f5e22a8e0c3.jpg"},
]


def api_get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())


def api_post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read())


def seed():
    stats = api_get("/api/stats")
    if stats["totalRecords"] > 0:
        print(f"Database already has {stats['totalRecords']} cards — skipping seed.")
        return

    ok = 0
    for card in CARDS:
        try:
            api_post("/api/cards", card)
            print(f"  + {card['name']}")
            ok += 1
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  ! {card['name']} FAILED: {body}")

    print(f"\nSeeded {ok}/{len(CARDS)} cards successfully.")


if __name__ == "__main__":
    seed()
