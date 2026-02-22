"""Products domain — public exports.

Exports are string-listed to avoid circular imports during Django app loading.
Import concrete classes directly from their submodules when needed.
"""
__all__: list[str] = [
    "Brand",
    "BrandDAO",
    "Category",
    "CategoryDAO",
    "Gender",
    "InvalidFilterError",
    "PriceTier",
    "Product",
    "ProductDAO",
    "ProductNotFoundError",
    "ProductService",
    "calculate_tier",
]
