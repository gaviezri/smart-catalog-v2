"""Management command: seed the database with products, users and embeddings.

Runs on startup if the database is empty. Idempotent.
"""
from __future__ import annotations

import uuid
from typing import Any

import structlog
from django.core.management.base import BaseCommand
from django.db import transaction

from products.infrastructure.orm_models import (
    BrandORM,
    CategoryORM,
    ProductCategoryORM,
    ProductORM,
    ProductSearchORM,
)
from users.infrastructure.orm_models import UserORM

# Import generation logic from sibling seed/ package
from .seed.generate_embeddings import generate_search_records
from .seed.generate_products import generate_all_products

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    """Seed the database with products and default users if empty."""

    help = "Seed the database with products and default users."

    def handle(self, *args: object, **options: object) -> None:
        """Run the seed pipeline."""
        self._seed_users()
        self._seed_data()

    def _seed_users(self) -> None:
        """Create default admin and user accounts."""
        if UserORM.objects.using("default").filter(username="admin").exists():
            logger.info("seed.users.skip", reason="already seeded")
            return

        UserORM.objects.db_manager("default").create_user(username="admin", password="admin123", role="ADMIN")
        UserORM.objects.db_manager("default").create_user(username="user", password="user123", role="USER")
        logger.info("seed.users.done", users=["admin (ADMIN)", "user (USER)"])

    def _seed_data(self) -> None:
        """Generate and seed products, categories, brands and embeddings."""
        if ProductORM.objects.exists():
            logger.info("seed.products.skip", reason="already seeded")
            return

        logger.info("seed.generation.start")
        
        # 1. Generate core product data
        products_data = generate_all_products(count=100)
        logger.info("seed.products.generated", count=len(products_data))

        # 2. Generate embeddings and search records
        search_records = generate_search_records(products_data)
        logger.info("seed.embeddings.generated", count=len(search_records))

        logger.info("seed.db.insertion.start")
        
        with transaction.atomic(using="default"):
            # Maps to track DB objects for junction table and search table
            json_id_to_db_product: dict[int, ProductORM] = {}
            brand_name_to_obj: dict[str, BrandORM] = {}
            cat_name_to_obj: dict[str, CategoryORM] = {}

            # A. Process Brands
            unique_brands = sorted({p["brand"] for p in products_data})
            for name in unique_brands:
                brand, _ = BrandORM.objects.using("default").get_or_create(name=name)
                brand_name_to_obj[name] = brand

            # B. Process Categories
            unique_cats = set()
            for p in products_data:
                unique_cats.update(p["categories"])
            for name in sorted(unique_cats):
                cat, _ = CategoryORM.objects.using("default").get_or_create(
                    name=name,
                    defaults={"public_id": uuid.uuid4()},
                )
                cat_name_to_obj[name] = cat

            # C. Process Products and M2M
            for data in products_data:
                brand = brand_name_to_obj[data["brand"]]
                product = ProductORM.objects.using("default").create(
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
                json_id_to_db_product[data["id"]] = product
                
                # Junction table
                for cat_name in data["categories"]:
                    cat = cat_name_to_obj[cat_name]
                    ProductCategoryORM.objects.using("default").create(
                        product=product,
                        category=cat
                    )

            # D. Process Search Table (Embeddings)
            # Re-constructing the same mapping as generate_embeddings.py to map fake IDs to real ones
            all_cats_sorted = sorted(cat_name_to_obj.keys())
            category_lookup = {name: i + 1 for i, name in enumerate(all_cats_sorted)}
            inv_lookup = {v: k for k, v in category_lookup.items()}

            for rec in search_records:
                product = json_id_to_db_product[rec["product_id"]]
                brand = brand_name_to_obj[rec["brand_name"]]
                db_cat_ids = [cat_name_to_obj[inv_lookup[cid]].id for cid in rec["category_ids"]]

                ProductSearchORM.objects.using("default").create(
                    product_id=product.id,
                    embedding=rec["embedding"],
                    brand_id=brand.id,
                    brand_name=rec["brand_name"],
                    tier=rec["tier"],
                    price=rec["price"],
                    category_ids=db_cat_ids,
                    gender=rec["gender"],
                    color=rec["color"],
                )

        logger.info("seed.db.insertion.done", count=len(products_data))
