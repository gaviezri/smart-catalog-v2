"""View: list all pricing tiers."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.containers import ProductContainer
from products.domain.services import ProductService
from products.infrastructure.serializers import TierSerializer


class TierListView(APIView):
    """List all pricing tiers."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List tiers",
        responses={200: TierSerializer(many=True)},
    )
    @inject
    def get(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle GET /api/products/tiers."""
        return Response(service.get_all_tiers())
