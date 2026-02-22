"""Concrete DAO implementations for the products bounded context.

Each DAO provides a unified interface to the domain, hiding the
read/write split and ORM details.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from django.db.models import QuerySet

from pgvector.django import CosineDistance

from products.domain.models import Brand, Category, Gender, PriceTier, Product
from products.domain.ports import BrandDAO, CategoryDAO, ProductDAO
from products.infrastructure.orm_models import (
    BrandORM,
    CategoryORM,
    ProductORM,
    ProductSearchORM,
)


def _orm_to_domain(orm: ProductORM) -> Product:
    """Map an ORM instance to a domain Product."""
    return Product(
        id=orm.pk,
        public_id=orm.public_id,
        title=orm.title,
        brand=Brand(id=orm.brand_id, name=orm.brand.name),
        categories=[Category(id=c.pk, name=c.name) for c in orm.categories.all()],
        price=orm.price,
        tier=PriceTier(orm.tier),
        gender=Gender(orm.gender),
        color=orm.color,
        product_url=orm.product_url,
        image_url=orm.image_url,
    )


class DjangoProductDAO(ProductDAO):
    """Product data access backed by Django ORM.

    Internally uses ``select_related`` / ``prefetch_related`` for reads
    and standard ORM create/delete for writes. The read/write DB routing
    is handled transparently by Django's ``DATABASE_ROUTERS``.
    """

    # ── Reads ────────────────────────────────────────────────────────────

    def _base_qs(self) -> QuerySet[ProductORM]:
        """Queryset with eager-loaded brand and categories."""
        return ProductORM.objects.select_related("brand").prefetch_related("categories")

    def get_all(self, page: int, page_size: int) -> tuple[list[Product], int]:
        """Paginated list of all products."""
        qs: QuerySet[ProductORM] = self._base_qs().order_by("-created_at")
        total: int = qs.count()
        offset: int = page * page_size
        products: list[Product] = [_orm_to_domain(p) for p in qs[offset : offset + page_size]]
        return products, total

    def get_filtered(
        self,
        tier: PriceTier | None,
        category_ids: list[int] | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Product], int]:
        """Filtered + paginated products."""
        qs: QuerySet[ProductORM] = self._base_qs()

        if tier is not None:
            qs = qs.filter(tier=tier.value)
        if category_ids:
            qs = qs.filter(categories__id__in=category_ids).distinct()

        qs = qs.order_by("-created_at")
        total: int = qs.count()
        offset: int = page * page_size
        products: list[Product] = [_orm_to_domain(p) for p in qs[offset : offset + page_size]]
        return products, total

    def find_by_public_id(self, public_id: UUID) -> Product | None:
        """Look up by public UUID."""
        try:
            orm: ProductORM = self._base_qs().get(public_id=public_id)
        except ProductORM.DoesNotExist:
            return None
        return _orm_to_domain(orm)

    # ── Writes ───────────────────────────────────────────────────────────

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
        """Persist a new product."""
        orm: ProductORM = ProductORM.objects.create(
            title=title,
            brand_id=brand_id,
            price=price,
            tier=tier.value,
            gender=gender,
            color=color,
            product_url=product_url,
            image_url=image_url,
        )
        if category_ids:
            orm.categories.set(category_ids)

        # Refetch with relations for the domain mapping
        orm = self._base_qs().get(pk=orm.pk)
        return _orm_to_domain(orm)

    def find_similar(
        self,
        vector: list[float],
        max_price: Decimal | None = None,
        category_ids: list[int] | None = None,
        tier: PriceTier | None = None,
        gender: str | None = None,
        limit: int = 5,
    ) -> list[Product]:
        """Hybrid similarity search using pgvector + metadata filters."""
        qs = ProductSearchORM.objects.all()

        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        if category_ids:
            # ArrayField lookup in PostgreSQL
            qs = qs.filter(category_ids__overlap=category_ids)
        if tier is not None:
            qs = qs.filter(tier=tier.value)
        if gender is not None:
            qs = qs.filter(gender=gender)

        # Vector search using Cosine distance (<=>)
        qs = (
            qs.annotate(distance=CosineDistance("embedding", vector))
            .order_by("distance")
            .select_related("product__brand")
            .prefetch_related("product__categories")[:limit]
        )

        return [_orm_to_domain(p.product) for p in qs]

    def delete_by_public_id(self, public_id: UUID) -> None:
        """Delete by public UUID."""
        ProductORM.objects.filter(public_id=public_id).delete()


class DjangoBrandDAO(BrandDAO):
    """Brand data access backed by Django ORM."""

    def find_by_name_icase(self, name: str) -> Brand | None:
        """Case-insensitive brand lookup."""
        try:
            orm: BrandORM = BrandORM.objects.get(name__iexact=name)
        except BrandORM.DoesNotExist:
            return None
        return Brand(id=orm.pk, name=orm.name)

    def create(self, name: str) -> Brand:
        """Create a new brand."""
        orm: BrandORM = BrandORM.objects.create(name=name)
        return Brand(id=orm.pk, name=orm.name)

    def get_all(self) -> list[Brand]:
        """Return all brands."""
        return [Brand(id=b.pk, name=b.name) for b in BrandORM.objects.all()]


class DjangoCategoryDAO(CategoryDAO):
    """Category data access backed by Django ORM."""

    def find_by_name_icase(self, name: str) -> Category | None:
        """Case-insensitive category lookup."""
        try:
            orm: CategoryORM = CategoryORM.objects.get(name__iexact=name)
        except CategoryORM.DoesNotExist:
            return None
        return Category(id=orm.pk, name=orm.name)

    def create(self, name: str) -> Category:
        """Create a new category (auto-generates public_id)."""
        orm: CategoryORM = CategoryORM.objects.create(name=name, public_id=uuid.uuid4())
        return Category(id=orm.pk, name=orm.name)

    def get_all(self) -> list[Category]:
        """Return all categories."""
        return [Category(id=c.pk, name=c.name) for c in CategoryORM.objects.all()]
