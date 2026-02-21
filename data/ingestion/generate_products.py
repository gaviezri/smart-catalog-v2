"""
Generate 100 products aligned with the smart-catalog-v2 database schema.

Output: products.json
"""

import json
import random
import uuid
from datetime import datetime, timezone

# ── Brand pools ──────────────────────────────────────────────────────────────

LUXURY_BRANDS = ["Gucci", "Prada", "Fendi", "Versace", "Burberry"]
SPORTS_BRANDS = ["Nike", "Adidas", "Puma", "Reebok", "Under Armour"]
CASUAL_BRANDS = ["Levi's", "Zara", "H&M", "ATAWear", "Asos", "GAP"]

ALL_BRANDS = LUXURY_BRANDS + SPORTS_BRANDS + CASUAL_BRANDS

# ── Category pools ───────────────────────────────────────────────────────────

ITEM_CATEGORIES = [
    "T-Shirt", "Jeans", "Jacket", "Sneakers", "Hoodie",
    "Dress", "Shorts", "Skirt", "Sweater", "Coat",
]

DRESS_CATEGORIES = ["Sportswear", "Casualwear", "Formalwear"]

# ── Colors ───────────────────────────────────────────────────────────────────

COLORS = [
    "Black", "White", "Navy", "Gray", "Red",
    "Blue", "Green", "Beige", "Brown", "Pink",
    "Olive", "Burgundy", "Cream", "Charcoal",
]

# ── Gender ───────────────────────────────────────────────────────────────────

GENDERS = ["M", "F", "U"]  # Male, Female, Unisex

# ── Price ranges per tier ────────────────────────────────────────────────────

TIER_PRICE_RANGES = {
    "BUDGET":  (10, 200),
    "MID":     (210, 750),
    "PREMIUM": (751, 10_000),
}


def _pick_tier(brand: str) -> str:
    if brand in LUXURY_BRANDS:
        return "PREMIUM"
    return random.choice(["BUDGET", "MID"])


def _pick_categories(brand: str) -> list[str]:
    item = random.choice(ITEM_CATEGORIES)
    if brand in LUXURY_BRANDS:
        dress = "Formalwear"
    elif brand in SPORTS_BRANDS:
        dress = "Sportswear"
    else:
        dress = random.choice(["Sportswear", "Casualwear"])
    return [item, dress]


def _pick_price(tier: str) -> float:
    lo, hi = TIER_PRICE_RANGES[tier]
    return round(random.uniform(lo, hi), 2)


def generate_product(product_id: int) -> dict:
    brand = random.choice(ALL_BRANDS)
    tier = _pick_tier(brand)
    categories = _pick_categories(brand)
    price = _pick_price(tier)
    color = random.choice(COLORS)
    gender = random.choice(GENDERS)
    title = f"{brand} {categories[0]} {random.randint(1, 100)}"
    now = datetime.now(timezone.utc).isoformat()

    return {
        "id": product_id,
        "publicId": str(uuid.uuid4()),
        "title": title,
        "brand": brand,
        "categories": categories,
        "price": price,
        "tier": tier,
        "gender": gender,
        "color": color,
        "productUrl": f"https://example.com/products/{product_id}",
        "imageUrl": f"https://example.com/images/{product_id}.jpg",
        "createdAt": now,
    }


def main():
    random.seed(42)
    products = [generate_product(i) for i in range(1, 101)]

    with open("products.json", "w") as f:
        json.dump(products, f, indent=2)

    print(f"✅  Generated {len(products)} products → products.json")


if __name__ == "__main__":
    main()
