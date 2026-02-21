"""Management command: seed the database with products and default users.

Runs on startup if the database is empty. Idempotent.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

import structlog
from django.core.management.base import BaseCommand

from products.infrastructure.orm_models import BrandORM, CategoryORM, ProductORM
from users.infrastructure.orm_models import UserORM

logger = structlog.get_logger(__name__)

# Docker sets INGESTION_DIR=/data/ingestion; local dev resolves relative to project root
# This is a bit of a hack to make it work in both cases
INGESTION_DIR: Path = Path(
    os.environ.get("INGESTION_DIR", Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "data" / "ingestion")
)


class Command(BaseCommand):
    """Seed the database with products and default users if empty."""

    help = "Seed the database with products and default users."

    def handle(self, *args: object, **options: object) -> None:
        """Run the seed pipeline."""
        self._seed_users()
        self._seed_products()

    def _seed_users(self) -> None:
        """Create default admin and user accounts."""
        if UserORM.objects.filter(username="admin").exists():
            logger.info("seed.users.skip", reason="already seeded")
            return

        UserORM.objects.create_user(username="admin", password="admin123", role="ADMIN")
        UserORM.objects.create_user(username="user", password="user123", role="USER")
        logger.info("seed.users.done", users=["admin (ADMIN)", "user (USER)"])

    def _seed_products(self) -> None:
        """Load products.json and insert into DB."""
        if ProductORM.objects.exists():
            logger.info("seed.products.skip", reason="already seeded")
            return

        products_path: Path = INGESTION_DIR / "products.json"
        if not products_path.exists():
            logger.warning("seed.products.skip", reason="products.json not found", path=str(products_path))
            return

        with open(products_path) as f:
            products_data: list[dict] = json.load(f)

        logger.info("seed.products.start", count=len(products_data))

        for data in products_data:
            brand_name: str = data["brand"]
            brand, _ = BrandORM.objects.get_or_create(name=brand_name)

            category_orms: list[CategoryORM] = []
            for cat_name in data["categories"]:
                cat, _ = CategoryORM.objects.get_or_create(
                    name=cat_name,
                    defaults={"public_id": uuid.uuid4()},
                )
                category_orms.append(cat)

            product: ProductORM = ProductORM.objects.create(
                public_id=data.get("publicId", uuid.uuid4()),
                title=data["title"],
                brand=brand,
                price=data["price"],
                tier=data["tier"],
                gender=data.get("gender", "U"),
                color=data.get("color", ""),
                product_url=data.get("productUrl", ""),
                image_url=data.get("imageUrl", ""),
            )
            product.categories.set(category_orms)

        logger.info("seed.products.done", count=len(products_data))
