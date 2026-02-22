"""Domain services for the products bounded context."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from products.domain.exceptions import InvalidFilterError, ProductNotFoundError
from products.domain.models import Category, PriceTier, Product
from products.domain.ports import BrandDAO, CategoryDAO, ProductDAO
from products.domain.tier_calculator import calculate_tier


def _all_tiers() -> list[dict[str, int | str]]:
    """Return all pricing tiers with ordinal IDs."""
    return [{"id": i, "name": tier.value} for i, tier in enumerate(PriceTier)]


class ProductService:
    """Business logic for product CRUD — depends only on DAO ports."""

    def __init__(
        self,
        product_dao: ProductDAO,
        brand_dao: BrandDAO,
        category_dao: CategoryDAO,
    ) -> None:
        self._product_dao: ProductDAO = product_dao
        self._brand_dao: BrandDAO = brand_dao
        self._category_dao: CategoryDAO = category_dao

    def get_all_products(self, page: int, page_size: int) -> tuple[list[Product], int]:
        """Return a paginated list of all products."""
        return self._product_dao.get_all(page, page_size)

    def get_all_categories(self) -> list[Category]:
        """Return every category."""
        return self._category_dao.get_all()

    @staticmethod
    def get_all_tiers() -> list[dict[str, int | str]]:
        """Return all pricing tiers with ordinal IDs."""
        return _all_tiers()

    def get_filtered(
        self,
        tier: PriceTier | None,
        category_ids: list[int] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        """Return filtered products.

        Raises:
            InvalidFilterError: If no filter parameters are provided.
        """
        if tier is None and (category_ids is None or len(category_ids) == 0):
            raise InvalidFilterError

        return self._product_dao.get_filtered(tier, category_ids, page, page_size)

    def create(
        self,
        title: str,
        brand_name: str,
        category_names: list[str],
        price: Decimal,
        gender: str,
        color: str,
        product_url: str,
        image_url: str,
    ) -> Product:
        """Create a product, auto-calculating tier and get-or-creating brand/categories."""
        # Get or create brand
        brand = self._brand_dao.find_by_name_icase(brand_name)
        if brand is None:
            brand = self._brand_dao.create(brand_name)

        # Get or create categories
        category_ids: list[int] = []
        for name in category_names:
            cat = self._category_dao.find_by_name_icase(name)
            if cat is None:
                cat = self._category_dao.create(name)
            category_ids.append(cat.id)

        tier: PriceTier = calculate_tier(price)

        return self._product_dao.save(
            title=title,
            brand_id=brand.id,
            category_ids=category_ids,
            price=price,
            tier=tier,
            gender=gender,
            color=color,
            product_url=product_url,
            image_url=image_url,
        )

    def delete(self, public_id: UUID) -> None:
        """Delete a product by its public UUID.

        Raises:
            ProductNotFoundError: If the product doesn't exist.
        """
        product: Product | None = self._product_dao.find_by_public_id(public_id)
        if product is None:
            raise ProductNotFoundError(public_id)
        self._product_dao.delete_by_public_id(public_id)
        
    def find_similar_products(
        self,
        vector: list[float],
        max_price: Decimal | None = None,
        category_ids: list[int] | None = None,
        tier: PriceTier | None = None,
        gender: str | None = None,
        limit: int = 5,
    ) -> list[Product]:
        """Return similar products using vector search + metadata filters."""
        return self._product_dao.find_similar_product(
            vector=vector,
            max_price=max_price,
            category_ids=category_ids,
            tier=tier,
            gender=gender,
            limit=limit,
        )
