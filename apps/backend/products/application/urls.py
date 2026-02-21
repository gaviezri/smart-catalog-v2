"""URL routing for the products bounded context."""
from __future__ import annotations

from django.urls import path

from products.application.views import (
    CategoryListView,
    ProductCreateView,
    ProductDeleteView,
    ProductFilterView,
    ProductListView,
    TierListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/filter", ProductFilterView.as_view(), name="product-filter"),
    path("products/create", ProductCreateView.as_view(), name="product-create"),
    path("products/<str:public_id>", ProductDeleteView.as_view(), name="product-delete"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("tiers/", TierListView.as_view(), name="tier-list"),
]
