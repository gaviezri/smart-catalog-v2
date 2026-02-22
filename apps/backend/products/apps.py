"""Django app configuration for the products bounded context."""
from __future__ import annotations

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Products app config — wires the DI container on startup."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "products"

    def ready(self) -> None:
        """Initialise the DI container when Django starts."""
        from products.containers import ProductContainer

        container = ProductContainer()
        container.wire(modules=[
            "products.application.views.products_view",
            "products.application.views.product_filter_view",
            "products.application.views.product_delete_view",
            "products.application.views.category_list_view",
            "products.application.views.tier_list_view",
        ])
