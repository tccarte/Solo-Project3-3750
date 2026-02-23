#!/usr/bin/env python3
"""
Seed the PostgreSQL database with 30 MTG cards including Scryfall image URLs.

Usage:
  Local:   DATABASE_URL=postgresql://... python seed.py
  Railway: railway run python seed.py

Idempotent — skips if the database already has data.
"""
import os
import psycopg2

DATABASE_URL = os.environ["DATABASE_URL"]

# Columns: name, set_code, type_line, mana_value, colors, rarity, quantity, condition, notes, image_url
CARDS = [
    (
        "Lightning Bolt", "M11", "Instant",
        1, "R", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/e/3/e3285d0e-4633-4b52-a784-d6aced05a842.jpg",
    ),
    (
        "Counterspell", "2XM", "Instant",
        2, "U", "Uncommon", 1, "LP", "",
        "https://cards.scryfall.io/normal/front/8/c/8c49dc7e-fa4a-4b84-a0de-7ca18d1f5848.jpg",
    ),
    (
        "Llanowar Elves", "M19", "Creature — Elf Druid",
        1, "G", "Common", 4, "NM", "",
        "https://cards.scryfall.io/normal/front/f/6/f6af56a1-8e95-4377-9bd0-2d4903e8fdc5.jpg",
    ),
    (
        "Swords to Plowshares", "2XM", "Instant",
        1, "W", "Uncommon", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/3/e/3e4f3b06-4a0c-4b51-8b67-b89c3a93d6f1.jpg",
    ),
    (
        "Thoughtseize", "2XM", "Sorcery",
        1, "B", "Rare", 1, "MP", "",
        "https://cards.scryfall.io/normal/front/b/0/b0faa7f2-b547-42c4-a810-839da50dadfe.jpg",
    ),
    (
        "Sol Ring", "CMM", "Artifact",
        1, "C", "Uncommon", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/f/0/f0e29ac2-0428-4d72-a26c-ac609e8e0e54.jpg",
    ),
    (
        "Arcane Signet", "ELD", "Artifact",
        2, "C", "Common", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/0/a/0a6a0d74-6f55-4a22-af6b-65b8ff9e1efb.jpg",
    ),
    (
        "Path to Exile", "2XM", "Instant",
        1, "W", "Uncommon", 2, "LP", "",
        "https://cards.scryfall.io/normal/front/0/2/02ea6e46-f775-4068-935f-70b2d29eb6d1.jpg",
    ),
    (
        "Cultivate", "M21", "Sorcery",
        3, "G", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/e/e/ee4ae30a-7b67-469f-8bd5-fc18e72476d9.jpg",
    ),
    (
        "Kodama's Reach", "CMM", "Sorcery",
        3, "G", "Common", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/d/e/de58f1c8-cc11-4afc-9fea-1b42c0765aa3.jpg",
    ),
    (
        "Shivan Dragon", "M10", "Creature — Dragon",
        6, "R", "Rare", 1, "LP", "",
        "https://cards.scryfall.io/normal/front/1/4/1498cfe2-facc-4db7-b93e-e8b85ea25b1f.jpg",
    ),
    (
        "Serra Angel", "M10", "Creature — Angel",
        5, "W", "Uncommon", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/9/b/9bb35bda-4ff0-46b6-a5f5-b7e79a95e498.jpg",
    ),
    (
        "Doom Blade", "M12", "Instant",
        2, "B", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/a/a/aa0f2e76-47a7-4cee-b76d-399bda64d93e.jpg",
    ),
    (
        "Opt", "XLN", "Instant",
        1, "U", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/0/e/0e2a37f8-c640-40c7-a2f3-4a3d5e42a7eb.jpg",
    ),
    (
        "Giant Growth", "M19", "Instant",
        1, "G", "Common", 3, "NM", "",
        "https://cards.scryfall.io/normal/front/5/8/5876e7fc-e88d-4a1c-ba67-29a4e08c7c54.jpg",
    ),
    (
        "Wrath of God", "2ED", "Sorcery",
        4, "W", "Rare", 1, "HP", "Old copy",
        "https://cards.scryfall.io/normal/front/1/e/1e8c2b08-0dcd-4f1c-8a30-3bfa39e87ff9.jpg",
    ),
    (
        "Brainstorm", "EMA", "Instant",
        1, "U", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/f/a/fa50b490-c4c1-40ba-8aea-74dbf9d65aca.jpg",
    ),
    (
        "Dark Ritual", "A25", "Instant",
        1, "B", "Common", 1, "LP", "",
        "https://cards.scryfall.io/normal/front/d/1/d14e0ed2-e69d-4f86-a16c-d1d20b17aa0a.jpg",
    ),
    (
        "Faithless Looting", "UMA", "Sorcery",
        1, "R", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/e/7/e79f2a0d-01e8-4db4-b0a2-c5b84a93e7e7.jpg",
    ),
    (
        "Birds of Paradise", "M12", "Creature — Bird",
        1, "G", "Rare", 1, "MP", "",
        "https://cards.scryfall.io/normal/front/7/2/72edd889-5a8c-48a0-bde4-71085413f6d3.jpg",
    ),
    (
        "Supreme Verdict", "RTR", "Sorcery",
        4, "M", "Rare", 1, "NM", "UW",
        "https://cards.scryfall.io/normal/front/6/0/6006dfc5-cf8a-4e94-92f8-dc0b01b4f56b.jpg",
    ),
    (
        "Terminate", "ARB", "Instant",
        2, "M", "Uncommon", 1, "LP", "BR",
        "https://cards.scryfall.io/normal/front/9/d/9d8d0017-9e33-4c79-b4c2-ff0a2c7fac54.jpg",
    ),
    (
        "Coiling Oracle", "GK1", "Creature — Snake Elf Druid",
        2, "M", "Uncommon", 1, "NM", "UG",
        "https://cards.scryfall.io/normal/front/5/e/5e03d8a5-1519-4d40-b3d3-30d3cc4cded1.jpg",
    ),
    (
        "Boros Charm", "GTC", "Instant",
        2, "M", "Uncommon", 1, "NM", "RW",
        "https://cards.scryfall.io/normal/front/9/2/92f9d6f3-7d18-478d-b8e7-25ec4e001cf0.jpg",
    ),
    (
        "Sphinx's Revelation", "RTR", "Instant",
        3, "M", "Mythic", 1, "LP", "XUW",
        "https://cards.scryfall.io/normal/front/5/b/5ba8f5a0-9ede-4e17-b53d-b1882f6c8e80.jpg",
    ),
    (
        "Wastes", "OGW", "Basic Land",
        0, "C", "Common", 5, "NM", "",
        "https://cards.scryfall.io/normal/front/5/9/59a2536b-ee4a-4a9c-9ab2-de3613c9c2d5.jpg",
    ),
    (
        "Evolving Wilds", "M20", "Land",
        0, "C", "Common", 2, "NM", "",
        "https://cards.scryfall.io/normal/front/d/d/dd5adc8a-3d69-4e00-8789-62e2e0b6f9d5.jpg",
    ),
    (
        "Command Tower", "CMM", "Land",
        0, "C", "Common", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/0/d/0d8c77b6-bd5e-4fe8-8b15-1f15d08b6d7e.jpg",
    ),
    (
        "Mystic Remora", "ICE", "Enchantment",
        1, "U", "Rare", 1, "MP", "",
        "https://cards.scryfall.io/normal/front/2/1/21ab8c2a-0e58-4cc6-956e-48d74e0c5a3f.jpg",
    ),
    (
        "Smothering Tithe", "RNA", "Enchantment",
        4, "W", "Rare", 1, "NM", "",
        "https://cards.scryfall.io/normal/front/a/2/a2c45e67-2fbd-4b13-9c1d-5f5e22a8e0c3.jpg",
    ),
]


def seed():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cards")
            count = cur.fetchone()[0]
            if count > 0:
                print(f"Database already has {count} cards — skipping seed.")
                return

            cur.executemany("""
                INSERT INTO cards
                    (name, set_code, type_line, mana_value, colors, rarity,
                     quantity, condition, notes, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, CARDS)
        conn.commit()
        print(f"Seeded {len(CARDS)} cards successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
