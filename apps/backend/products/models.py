"""Re-export ORM models so Django's model discovery finds them.

Django discovers models by importing ``<app>.models``. Since our ORM models
live in ``infrastructure/orm_models.py`` (hexagonal layout), this bridge
module makes them visible to the framework.
"""
from products.infrastructure.orm_models import (  # noqa: F401
    BrandORM,
    CategoryORM,
    ProductORM,
    ProductSearchORM,
)

__all__: list[str] = ["BrandORM", "CategoryORM", "ProductORM", "ProductSearchORM"]
