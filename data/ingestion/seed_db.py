"""
Seed the database with generated products and embeddings.

This script is designed to run on application startup (e.g. from a Django
management command or a Docker entrypoint).  It is idempotent: it only
seeds when the `product` table is empty.

Flow:
  1. Check if `product` table already has rows  → skip if so
  2. Run generate_products   → products.json
  3. Run generate_embeddings → product_search.json   (real 1536-dim vectors)
  4. Insert brands, categories, products, products_categories, product_search

Requirements:
  pip install psycopg2-binary sentence-transformers torch

Environment variables (with defaults for local dev):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

SCRIPT_DIR = Path(__file__).resolve().parent

# ── DB connection ────────────────────────────────────────────────────────────

def _get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "smart_catalog"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def _db_already_seeded(conn) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS(SELECT 1 FROM product LIMIT 1)")
        return cur.fetchone()[0]


# ── Generation helpers ───────────────────────────────────────────────────────

def _run_script(script_name: str):
    """Run a sibling Python script in SCRIPT_DIR."""
    path = SCRIPT_DIR / script_name
    print(f"⏳  Running {script_name} …")
    subprocess.check_call([sys.executable, str(path)], cwd=str(SCRIPT_DIR))


# ── Insertion logic ──────────────────────────────────────────────────────────

def _insert_brands(cur, products: list[dict]) -> dict[str, int]:
    """Insert unique brands and return {name: id} mapping."""
    unique_brands = sorted({p["brand"] for p in products})
    brand_map: dict[str, int] = {}
    for name in unique_brands:
        cur.execute(
            "INSERT INTO brands (name) VALUES (%s) RETURNING id",
            (name,),
        )
        brand_map[name] = cur.fetchone()[0]
    return brand_map


def _insert_categories(cur, products: list[dict]) -> dict[str, int]:
    """Insert unique categories and return {name: id} mapping."""
    unique_cats: set[str] = set()
    for p in products:
        unique_cats.update(p["categories"])

    cat_map: dict[str, int] = {}
    for name in sorted(unique_cats):
        cur.execute(
            "INSERT INTO categories (name, public_id) VALUES (%s, %s) RETURNING id",
            (name, str(uuid.uuid4())),
        )
        cat_map[name] = cur.fetchone()[0]
    return cat_map


def _insert_products(
    cur,
    products: list[dict],
    brand_map: dict[str, int],
) -> dict[int, int]:
    """Insert products and return {json_id: db_id} mapping."""
    id_map: dict[int, int] = {}
    for p in products:
        cur.execute(
            """
            INSERT INTO product (public_id, title, brand_id, price, tier,
                                 gender, color, product_url, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                p["publicId"],
                p["title"],
                brand_map[p["brand"]],
                p["price"],
                p["tier"],
                p["gender"],
                p["color"],
                p["productUrl"],
                p["imageUrl"],
            ),
        )
        id_map[p["id"]] = cur.fetchone()[0]
    return id_map


def _insert_products_categories(
    cur,
    products: list[dict],
    product_id_map: dict[int, int],
    cat_map: dict[str, int],
):
    """Populate the products_categories join table."""
    rows = []
    for p in products:
        db_product_id = product_id_map[p["id"]]
        for cat_name in p["categories"]:
            rows.append((db_product_id, cat_map[cat_name]))

    execute_values(
        cur,
        "INSERT INTO products_categories (product_id, category_id) VALUES %s",
        rows,
    )


def _insert_product_search(
    cur,
    search_records: list[dict],
    product_id_map: dict[int, int],
    brand_map_by_name: dict[str, int],
    cat_map: dict[str, int],
):
    """Populate the product_search projection table."""
    for rec in search_records:
        db_product_id = product_id_map[rec["product_id"]]
        db_brand_id = brand_map_by_name[rec["brand_name"]]
        db_cat_ids = [cat_map.get(c) for c in _original_cat_names(rec, cat_map)]

        # Fall back to the category_ids from the JSON if name lookup isn't possible
        if not db_cat_ids:
            db_cat_ids = rec["category_ids"]

        cur.execute(
            """
            INSERT INTO product_search
                (product_id, embedding, brand_id, brand_name,
                 tier, price, category_ids, gender, color)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                db_product_id,
                str(rec["embedding"]),  # pgvector accepts text '[0.1,0.2,…]'
                db_brand_id,
                rec["brand_name"],
                rec["tier"],
                rec["price"],
                db_cat_ids,
                rec["gender"],
                rec["color"],
            ),
        )


def _original_cat_names(
    search_rec: dict, cat_map: dict[str, int]
) -> list[str]:
    """Reverse-lookup category names from the search record's category_ids
    that were generated by generate_embeddings.py (1-indexed sequential)."""
    # Build reverse: gen_id → name  (gen_ids are 1-indexed sequential from _build_lookup)
    inv = {v: k for k, v in cat_map.items()}
    # search_rec["category_ids"] are the *generation-time* ids, not DB ids
    return [inv[cid] for cid in search_rec["category_ids"] if cid in inv]


# ── Main ─────────────────────────────────────────────────────────────────────

def seed():
    conn = _get_conn()
    try:
        if _db_already_seeded(conn):
            print("✅  Database already seeded — skipping.")
            return

        # Step 1 & 2: generate JSON files
        _run_script("generate_products.py")
        _run_script("generate_embeddings.py")

        # Step 3: load JSON files
        with open(SCRIPT_DIR / "products.json") as f:
            products = json.load(f)
        with open(SCRIPT_DIR / "product_search.json") as f:
            search_records = json.load(f)

        # Step 4: insert into DB inside a single transaction
        with conn.cursor() as cur:
            brand_map = _insert_brands(cur, products)
            cat_map = _insert_categories(cur, products)
            product_id_map = _insert_products(cur, products, brand_map)
            _insert_products_categories(cur, products, product_id_map, cat_map)
            _insert_product_search(
                cur, search_records, product_id_map, brand_map, cat_map,
            )

        conn.commit()
        print(f"✅  Seeded {len(products)} products + embeddings into the database.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
