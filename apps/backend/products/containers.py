"""DI container for the products bounded context."""
from __future__ import annotations

from dependency_injector import containers, providers

from products.domain.services import ProductService
from products.infrastructure.daos import (
    DjangoBrandDAO,
    DjangoCategoryDAO,
    DjangoProductDAO,
)


class ProductContainer(containers.DeclarativeContainer):
    """Wire domain services to infrastructure DAO implementations."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "products.application.views.products_view",
            "products.application.views.product_filter_view",
            "products.application.views.product_delete_view",
            "products.application.views.category_list_view",
            "products.application.views.tier_list_view",
        ],
    )

    product_dao = providers.Singleton(DjangoProductDAO)
    brand_dao = providers.Singleton(DjangoBrandDAO)
    category_dao = providers.Singleton(DjangoCategoryDAO)

    product_service = providers.Factory(
        ProductService,
        product_dao=product_dao,
        brand_dao=brand_dao,
        category_dao=category_dao,
    )
