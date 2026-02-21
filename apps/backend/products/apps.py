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
        container.wire(modules=["products.application.views"])
