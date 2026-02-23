import os
from math import ceil
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

DATABASE_URL     = os.environ["DATABASE_URL"]
VALID_COLORS     = {"W", "U", "B", "R", "G", "C", "M"}
VALID_RARITIES   = {"Common", "Uncommon", "Rare", "Mythic"}
VALID_CONDITIONS = {"NM", "LP", "MP", "HP", "DMG"}
VALID_SORT_COLS  = {"name", "mana_value", "rarity", "quantity", "created_at"}
VALID_PAGE_SIZES = {5, 10, 20, 50}


# --- Database helpers ---

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name        VARCHAR(80)  NOT NULL,
                    set_code    VARCHAR(10)  NOT NULL,
                    type_line   VARCHAR(80)  NOT NULL,
                    mana_value  SMALLINT     NOT NULL CHECK (mana_value BETWEEN 0 AND 20),
                    colors      VARCHAR(1)   NOT NULL CHECK (colors IN ('W','U','B','R','G','C','M')),
                    rarity      VARCHAR(10)  NOT NULL CHECK (rarity IN ('Common','Uncommon','Rare','Mythic')),
                    quantity    SMALLINT     NOT NULL CHECK (quantity BETWEEN 1 AND 99),
                    condition   VARCHAR(3)   NOT NULL CHECK (condition IN ('NM','LP','MP','HP','DMG')),
                    notes       VARCHAR(200) NOT NULL DEFAULT '',
                    image_url   VARCHAR(500) NOT NULL DEFAULT '',
                    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
                )
            """)
        conn.commit()


init_db()


def row_to_card(row):
    return {
        "id":        str(row["id"]),
        "name":      row["name"],
        "set":       row["set_code"],
        "typeLine":  row["type_line"],
        "manaValue": row["mana_value"],
        "colors":    row["colors"],
        "rarity":    row["rarity"],
        "quantity":  row["quantity"],
        "condition": row["condition"],
        "notes":     row["notes"],
        "imageUrl":  row["image_url"],
    }


# --- Validation ---

def validate_card(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    name      = str(data.get("name", "")).strip()
    card_set  = str(data.get("set", "")).strip()
    type_line = str(data.get("typeLine", "")).strip()
    colors    = str(data.get("colors", "")).strip()
    rarity    = str(data.get("rarity", "")).strip()
    condition = str(data.get("condition", "")).strip()
    notes     = str(data.get("notes", "")).strip()
    image_url = str(data.get("imageUrl", "")).strip()

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

    if image_url and not (image_url.startswith("http://") or image_url.startswith("https://")):
        return None, "Image URL must start with http:// or https://."
    if len(image_url) > 500:
        return None, "Image URL must be 500 characters or fewer."

    cleaned = {
        "name":      name,
        "set":       card_set,
        "typeLine":  type_line,
        "manaValue": mana_value,
        "colors":    colors,
        "rarity":    rarity,
        "quantity":  quantity,
        "condition": condition,
        "notes":     notes,
        "imageUrl":  image_url,
    }
    return cleaned, None


# --- API Routes ---

@app.route("/api/cards", methods=["GET"])
def list_cards():
    search   = request.args.get("search", "").strip()
    color    = request.args.get("color", "").strip()

    sort_by  = request.args.get("sortBy", "created_at")
    sort_dir = request.args.get("sortDir", "DESC").upper()
    if sort_by not in VALID_SORT_COLS:
        sort_by = "created_at"
    if sort_dir not in {"ASC", "DESC"}:
        sort_dir = "DESC"

    try:
        page_size = int(request.args.get("pageSize", 10))
    except (ValueError, TypeError):
        page_size = 10
    if page_size not in VALID_PAGE_SIZES:
        page_size = 10

    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    if page < 1:
        page = 1

    conditions = []
    params = []
    if search:
        conditions.append(
            "(name ILIKE %s OR set_code ILIKE %s OR type_line ILIKE %s "
            "OR rarity ILIKE %s OR colors ILIKE %s)"
        )
        like = f"%{search}%"
        params.extend([like, like, like, like, like])
    if color:
        conditions.append("colors = %s")
        params.append(color)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS cnt FROM cards {where}", params)
            total_count = cur.fetchone()["cnt"]

            total_pages = max(1, ceil(total_count / page_size))
            page = min(page, total_pages)
            offset = (page - 1) * page_size

            # sort_by and sort_dir are validated against allowlists above — safe to interpolate
            cur.execute(
                f"SELECT * FROM cards {where} "
                f"ORDER BY {sort_by} {sort_dir} "
                f"LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            rows = cur.fetchall()

    return jsonify({
        "cards":      [row_to_card(r) for r in rows],
        "page":       page,
        "totalPages": total_pages,
        "totalCount": total_count,
        "pageSize":   page_size,
    })


@app.route("/api/cards/<card_id>", methods=["GET"])
def get_card(card_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM cards WHERE id = %s", (card_id,))
            row = cur.fetchone()
    if not row:
        return jsonify({"error": "Card not found"}), 404
    return jsonify({"card": row_to_card(row)})


@app.route("/api/cards", methods=["POST"])
def create_card():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    cleaned, error = validate_card(data)
    if error:
        return jsonify({"error": error}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cards
                    (name, set_code, type_line, mana_value, colors, rarity,
                     quantity, condition, notes, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                cleaned["name"], cleaned["set"], cleaned["typeLine"],
                cleaned["manaValue"], cleaned["colors"], cleaned["rarity"],
                cleaned["quantity"], cleaned["condition"],
                cleaned["notes"], cleaned["imageUrl"],
            ))
            row = cur.fetchone()
        conn.commit()

    return jsonify({"card": row_to_card(row)}), 201


@app.route("/api/cards/<card_id>", methods=["PUT"])
def update_card(card_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    cleaned, error = validate_card(data)
    if error:
        return jsonify({"error": error}), 400

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE cards SET
                    name = %s, set_code = %s, type_line = %s, mana_value = %s,
                    colors = %s, rarity = %s, quantity = %s, condition = %s,
                    notes = %s, image_url = %s
                WHERE id = %s
                RETURNING *
            """, (
                cleaned["name"], cleaned["set"], cleaned["typeLine"],
                cleaned["manaValue"], cleaned["colors"], cleaned["rarity"],
                cleaned["quantity"], cleaned["condition"],
                cleaned["notes"], cleaned["imageUrl"],
                card_id,
            ))
            row = cur.fetchone()
        conn.commit()

    if not row:
        return jsonify({"error": "Card not found"}), 404
    return jsonify({"card": row_to_card(row)})


@app.route("/api/cards/<card_id>", methods=["DELETE"])
def delete_card(card_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM cards WHERE id = %s RETURNING id", (card_id,))
            row = cur.fetchone()
        conn.commit()
    if not row:
        return jsonify({"error": "Card not found"}), 404
    return jsonify({"deleted": True})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*)                                            AS total_records,
                    COALESCE(ROUND(AVG(mana_value)::numeric, 2), 0)   AS avg_mv,
                    SUM(CASE WHEN colors = 'W' THEN 1 ELSE 0 END)     AS cnt_w,
                    SUM(CASE WHEN colors = 'U' THEN 1 ELSE 0 END)     AS cnt_u,
                    SUM(CASE WHEN colors = 'B' THEN 1 ELSE 0 END)     AS cnt_b,
                    SUM(CASE WHEN colors = 'R' THEN 1 ELSE 0 END)     AS cnt_r,
                    SUM(CASE WHEN colors = 'G' THEN 1 ELSE 0 END)     AS cnt_g,
                    SUM(CASE WHEN colors = 'C' THEN 1 ELSE 0 END)     AS cnt_c,
                    SUM(CASE WHEN colors = 'M' THEN 1 ELSE 0 END)     AS cnt_m,
                    SUM(CASE WHEN rarity = 'Common'   THEN 1 ELSE 0 END) AS cnt_common,
                    SUM(CASE WHEN rarity = 'Uncommon' THEN 1 ELSE 0 END) AS cnt_uncommon,
                    SUM(CASE WHEN rarity = 'Rare'     THEN 1 ELSE 0 END) AS cnt_rare,
                    SUM(CASE WHEN rarity = 'Mythic'   THEN 1 ELSE 0 END) AS cnt_mythic
                FROM cards
            """)
            r = cur.fetchone()

    total = r["total_records"]
    avg_mv = float(r["avg_mv"] or 0)

    color_counts = {
        "W": r["cnt_w"], "U": r["cnt_u"], "B": r["cnt_b"],
        "R": r["cnt_r"], "G": r["cnt_g"], "C": r["cnt_c"], "M": r["cnt_m"],
    }

    most_common_color = "\u2014"
    most_common_count = 0
    if total > 0:
        best = max(color_counts.items(), key=lambda x: x[1])
        most_common_color, most_common_count = best

    return jsonify({
        "totalRecords":         total,
        "averageManaValue":     avg_mv,
        "colorCounts":          color_counts,
        "mostCommonColor":      most_common_color,
        "mostCommonColorCount": most_common_count,
        "rarityCounts": {
            "Common":   r["cnt_common"],
            "Uncommon": r["cnt_uncommon"],
            "Rare":     r["cnt_rare"],
            "Mythic":   r["cnt_mythic"],
        },
    })


# --- Serve frontend ---

@app.route("/")
def serve_index():
    return app.send_static_file("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
