"""View: list all categories."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.containers import ProductContainer
from products.domain.services import ProductService
from products.infrastructure.serializers import CategorySerializer


class CategoryListView(APIView):
    """List all categories."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List categories",
        responses={200: CategorySerializer(many=True)},
    )
    @inject
    def get(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle GET /api/products/categories."""
        categories = service.get_all_categories()
        return Response([{"id": c.id, "name": c.name} for c in categories])
