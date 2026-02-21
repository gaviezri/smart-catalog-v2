"""Products domain — public exports."""
from products.domain.exceptions import InvalidFilterError, ProductNotFoundError
from products.domain.models import Brand, Category, Gender, PriceTier, Product
from products.domain.ports import BrandDAO, CategoryDAO, ProductDAO
from products.domain.services import ProductService
from products.domain.tier_calculator import calculate_tier

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
