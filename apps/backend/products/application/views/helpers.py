"""Shared helpers for product views."""
from __future__ import annotations

import math

from products.domain.models import Product


def product_to_dict(p: Product) -> dict:
    """Map a domain Product to the serializer's expected shape."""
    return {
        "publicId": p.public_id,
        "title": p.title,
        "brandName": p.brand.name,
        "categoryNames": [c.name for c in p.categories],
        "price": p.price,
        "tier": p.tier.value,
        "gender": p.gender.value,
        "color": p.color,
        "productUrl": p.product_url,
        "imageUrl": p.image_url,
    }


def paged_response(products: list[Product], total: int, page: int, size: int) -> dict:
    """Build the paged response envelope."""
    total_pages: int = max(1, math.ceil(total / size))
    return {
        "content": [product_to_dict(p) for p in products],
        "page": page,
        "size": size,
        "totalElements": total,
        "totalPages": total_pages,
        "last": page >= total_pages - 1,
    }
