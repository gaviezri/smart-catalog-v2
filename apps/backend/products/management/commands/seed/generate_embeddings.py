"""
Generate mock random embeddings for every product in products.json.
Output: product_search.json
"""

import json
import random

MODEL_NAME = "mock-random-1536"


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
    """Build a descriptive sentence for a product (kept for interface compatibility)."""
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
    """Generate search records with mock random embeddings (1536-dim)."""
    brand_lookup, category_lookup = _build_lookup(products)

    print(f"Generating mock random embeddings (dim=1536) for {len(products)} products …")
    
    records = []
    # Seed for reproducibility in seeding
    random.seed(42)
    
    for product in products:
        # Generate random 1536-dim vector
        emb = [random.uniform(-1, 1) for _ in range(1536)]
        
        records.append({
            "product_id": product["id"],
            "embedding": emb,
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

    print(f"✅  Generated {len(records)} mock search records → product_search.json")


if __name__ == "__main__":
    main()
