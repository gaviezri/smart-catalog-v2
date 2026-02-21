"""
Generate real embeddings for every product in products.json using a local model.

Model : Alibaba-NLP/gte-Qwen2-1.5B-instruct  (1536-dim, runs locally)
Output: product_search.json

Each record mirrors the `product_search` table:
  - product_id, embedding, brand_id, brand_name,
    tier, price, category_ids, gender, color

Requirements:
  pip install sentence-transformers torch
"""

import json

from sentence_transformers import SentenceTransformer

MODEL_NAME = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"
BATCH_SIZE = 16


def _build_lookup(products: list[dict]) -> tuple[dict[str, int], dict[str, int]]:
    """Create deterministic id mappings for brands and categories."""
    brands: dict[str, int] = {}
    categories: dict[str, int] = {}

    for p in products:
        brand = p["brand"]
        if brand not in brands:
            brands[brand] = len(brands) + 1

        for cat in p["categories"]:
            if cat not in categories:
                categories[cat] = len(categories) + 1

    return brands, categories


def _product_to_text(product: dict) -> str:
    """Build a descriptive sentence for a product to embed."""
    cats = ", ".join(product["categories"])
    return (
        f"{product['title']}. "
        f"Brand: {product['brand']}. "
        f"Categories: {cats}. "
        f"Tier: {product['tier']}. "
        f"Price: ${product['price']:.2f}. "
        f"Gender: {product['gender']}. "
        f"Color: {product['color']}."
    )


def generate_search_records(products: list[dict]) -> list[dict]:
    """Generate search records with embeddings for a list of products."""
    brand_lookup, category_lookup = _build_lookup(products)

    # ── Load model ───────────────────────────────────────────────────────
    print(f"Loading model: {MODEL_NAME} …")
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    print(f"Model loaded — embedding dim: {model.get_sentence_embedding_dimension()}")

    # ── Encode ───────────────────────────────────────────────────────────
    texts = [_product_to_text(p) for p in products]
    print(f"Encoding {len(texts)} products (batch_size={BATCH_SIZE}) …")
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)

    # ── Build records ────────────────────────────────────────────────────
    records = []
    for product, emb in zip(products, embeddings):
        records.append({
            "product_id": product["id"],
            "embedding": emb.tolist(),
            "brand_id": brand_lookup[product["brand"]],
            "brand_name": product["brand"],
            "tier": product["tier"],
            "price": product["price"],
            "category_ids": [category_lookup[c] for c in product["categories"]],
            "gender": product["gender"],
            "color": product["color"],
        })
    return records


def main():
    # ── Load products ────────────────────────────────────────────────────
    with open("products.json") as f:
        products = json.load(f)

    records = generate_search_records(products)

    # ── Write output ─────────────────────────────────────────────────────
    with open("product_search.json", "w") as f:
        json.dump(records, f, indent=2)

    print(f"✅  Generated {len(records)} search records → product_search.json")
    print(f"   Brands:     {len(brand_lookup)}")
    print(f"   Categories: {len(category_lookup)}")
    print(f"   Embedding dim: {model.get_sentence_embedding_dimension()}")


if __name__ == "__main__":
    main()
