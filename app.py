import json
import os
import uuid
from math import ceil
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cards.json")
PAGE_SIZE = 10

VALID_COLORS = {"W", "U", "B", "R", "G", "C", "M"}
VALID_RARITIES = {"Common", "Uncommon", "Rare", "Mythic"}
VALID_CONDITIONS = {"NM", "LP", "MP", "HP", "DMG"}


# --- JSON file helpers ---

def read_cards():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_cards(cards):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)


# --- Validation ---

def validate_card(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    name = str(data.get("name", "")).strip()
    card_set = str(data.get("set", "")).strip()
    type_line = str(data.get("typeLine", "")).strip()
    colors = str(data.get("colors", "")).strip()
    rarity = str(data.get("rarity", "")).strip()
    condition = str(data.get("condition", "")).strip()
    notes = str(data.get("notes", "")).strip()

    if not name:
        return None, "Card Name is required."
    if len(name) > 80:
        return None, "Card Name must be 80 characters or fewer."

    if not card_set:
        return None, "Set Code is required."
    if len(card_set) > 10:
        return None, "Set Code must be 10 characters or fewer."

    if not type_line:
        return None, "Type Line is required."
    if len(type_line) > 80:
        return None, "Type Line must be 80 characters or fewer."

    try:
        mana_value = int(data.get("manaValue", ""))
    except (ValueError, TypeError):
        return None, "Mana Value must be an integer."
    if mana_value < 0 or mana_value > 20:
        return None, "Mana Value must be between 0 and 20."

    if colors not in VALID_COLORS:
        return None, "Colors must be one of: W, U, B, R, G, C, M."

    if rarity not in VALID_RARITIES:
        return None, "Rarity must be one of: Common, Uncommon, Rare, Mythic."

    try:
        quantity = int(data.get("quantity", ""))
    except (ValueError, TypeError):
        return None, "Quantity must be an integer."
    if quantity < 1 or quantity > 99:
        return None, "Quantity must be between 1 and 99."

    if condition not in VALID_CONDITIONS:
        return None, "Condition must be one of: NM, LP, MP, HP, DMG."

    if len(notes) > 200:
        return None, "Notes must be 200 characters or fewer."

    cleaned = {
        "name": name,
        "set": card_set,
        "typeLine": type_line,
        "manaValue": mana_value,
        "colors": colors,
        "rarity": rarity,
        "quantity": quantity,
        "condition": condition,
        "notes": notes,
    }
    return cleaned, None


# --- API Routes ---

@app.route("/api/cards", methods=["GET"])
def list_cards():
    cards = read_cards()

    search = request.args.get("search", "").strip().lower()
    color = request.args.get("color", "").strip()

    if search:
        cards = [
            c for c in cards
            if search in c.get("name", "").lower()
            or search in c.get("set", "").lower()
            or search in c.get("typeLine", "").lower()
            or search in c.get("rarity", "").lower()
            or search in c.get("colors", "").lower()
        ]

    if color:
        cards = [c for c in cards if c.get("colors") == color]

    total_count = len(cards)
    total_pages = max(1, ceil(total_count / PAGE_SIZE))

    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_cards = cards[start:end]

    return jsonify({
        "cards": page_cards,
        "page": page,
        "totalPages": total_pages,
        "totalCount": total_count,
    })


@app.route("/api/cards/<card_id>", methods=["GET"])
def get_card(card_id):
    cards = read_cards()
    card = next((c for c in cards if c.get("id") == card_id), None)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    return jsonify({"card": card})


@app.route("/api/cards", methods=["POST"])
def create_card():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    cleaned, error = validate_card(data)
    if error:
        return jsonify({"error": error}), 400

    cleaned["id"] = str(uuid.uuid4())

    cards = read_cards()
    cards.insert(0, cleaned)
    write_cards(cards)

    return jsonify({"card": cleaned}), 201


@app.route("/api/cards/<card_id>", methods=["PUT"])
def update_card(card_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    cleaned, error = validate_card(data)
    if error:
        return jsonify({"error": error}), 400

    cards = read_cards()
    idx = next((i for i, c in enumerate(cards) if c.get("id") == card_id), None)
    if idx is None:
        return jsonify({"error": "Card not found"}), 404

    cleaned["id"] = card_id
    cards[idx] = cleaned
    write_cards(cards)

    return jsonify({"card": cleaned})


@app.route("/api/cards/<card_id>", methods=["DELETE"])
def delete_card(card_id):
    cards = read_cards()
    idx = next((i for i, c in enumerate(cards) if c.get("id") == card_id), None)
    if idx is None:
        return jsonify({"error": "Card not found"}), 404

    cards.pop(idx)
    write_cards(cards)

    return jsonify({"deleted": True})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    cards = read_cards()
    total = len(cards)

    avg_mv = 0
    if total > 0:
        avg_mv = round(sum(c.get("manaValue", 0) for c in cards) / total, 2)

    color_counts = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0, "M": 0}
    for c in cards:
        col = c.get("colors", "")
        if col in color_counts:
            color_counts[col] += 1

    most_common_color = "\u2014"
    most_common_count = 0
    if total > 0:
        for k, v in color_counts.items():
            if v > most_common_count:
                most_common_count = v
                most_common_color = k

    rarity_counts = {"Common": 0, "Uncommon": 0, "Rare": 0, "Mythic": 0}
    for c in cards:
        r = c.get("rarity", "")
        if r in rarity_counts:
            rarity_counts[r] += 1

    return jsonify({
        "totalRecords": total,
        "averageManaValue": avg_mv,
        "colorCounts": color_counts,
        "mostCommonColor": most_common_color,
        "mostCommonColorCount": most_common_count,
        "rarityCounts": rarity_counts,
    })


# --- Serve frontend (for local development) ---

@app.route("/")
def serve_index():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
