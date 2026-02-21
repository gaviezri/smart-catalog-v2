"""Port interfaces (ABCs) for the products bounded context.

Each DAO presents a unified data-access interface to the domain layer.
The read/write split (replicas, separate adapters) is an infrastructure
detail hidden behind these abstractions.
"""
from __future__ import annotations

import abc
from decimal import Decimal
from uuid import UUID

from products.domain.models import Brand, Category, PriceTier, Product


class ProductDAO(abc.ABC):
    """Unified data-access interface for products."""

    # ── Reads ────────────────────────────────────────────────────────────

    @abc.abstractmethod
    def get_all(self, page: int, page_size: int) -> tuple[list[Product], int]:
        """Return a page of products and the total count."""

    @abc.abstractmethod
    def get_filtered(
        self,
        tier: PriceTier | None,
        category_ids: list[int] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        """Return filtered products and total count."""

    @abc.abstractmethod
    def find_by_public_id(self, public_id: UUID) -> Product | None:
        """Look up a single product by its public UUID."""

    # ── Writes ───────────────────────────────────────────────────────────

    @abc.abstractmethod
    def save(
        self,
        title: str,
        brand_id: int,
        category_ids: list[int],
        price: Decimal,
        tier: PriceTier,
        gender: str,
        color: str,
        product_url: str,
        image_url: str,
    ) -> Product:
        """Persist a new product and return the domain entity."""

    @abc.abstractmethod
    def delete_by_public_id(self, public_id: UUID) -> None:
        """Delete a product by its public UUID."""


class BrandDAO(abc.ABC):
    """Unified data-access interface for brands."""

    @abc.abstractmethod
    def find_by_name_icase(self, name: str) -> Brand | None:
        """Case-insensitive lookup."""

    @abc.abstractmethod
    def create(self, name: str) -> Brand:
        """Create a new brand."""

    @abc.abstractmethod
    def get_all(self) -> list[Brand]:
        """Return all brands."""


class CategoryDAO(abc.ABC):
    """Unified data-access interface for categories."""

    @abc.abstractmethod
    def find_by_name_icase(self, name: str) -> Category | None:
        """Case-insensitive lookup."""

    @abc.abstractmethod
    def create(self, name: str) -> Category:
        """Create a new category."""

    @abc.abstractmethod
    def get_all(self) -> list[Category]:
        """Return all categories."""
