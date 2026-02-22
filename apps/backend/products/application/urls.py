"""URL routing for the products bounded context."""
from __future__ import annotations

from django.urls import path

from products.application.views import (
    CategoryListView,
    ProductDeleteView,
    ProductFilterView,
    ProductsView,
    ProductSimilarityView,
    TierListView,
)

urlpatterns = [
    path("", ProductsView.as_view(), name="product-list"),
    path("filter", ProductFilterView.as_view(), name="product-filter"),
    path("similarity", ProductSimilarityView.as_view(), name="product-similarity"),
    path("categories", CategoryListView.as_view(), name="category-list"),
    path("tiers", TierListView.as_view(), name="tier-list"),
    path("<str:public_id>", ProductDeleteView.as_view(), name="product-delete"),
]
