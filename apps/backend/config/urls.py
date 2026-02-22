"""Root URL configuration."""
from __future__ import annotations

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns: list = [
    path("api", include([
        # API
        path("/auth", include("users.application.urls")),
        path("/products", include("products.application.urls")),
        # OpenAPI
        path("/openapi/schema", SpectacularAPIView.as_view(), name="schema"),
        path("/openapi/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    ])),
]
