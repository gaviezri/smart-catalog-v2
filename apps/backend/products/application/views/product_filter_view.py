"""View: filter products by tier and/or category."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.application.views.helpers import paged_response
from products.containers import ProductContainer
from products.domain.models import PriceTier
from products.domain.services import ProductService
from products.infrastructure.serializers import PagedResponseSerializer


class ProductFilterView(APIView):
    """Filter products by tier and/or category."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Filter products",
        description="Filter by tier and/or category IDs (at least one required).",
        parameters=[
            OpenApiParameter("tier", int, description="Tier ordinal (0=BUDGET, 1=MID, 2=PREMIUM)", required=False),
            OpenApiParameter("category", int, description="Category ID(s)", required=False, many=True),
            OpenApiParameter("page", int, required=False),
            OpenApiParameter("size", int, required=False),
        ],
        responses={200: PagedResponseSerializer},
    )
    @inject
    def get(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle GET /api/products/filter."""
        tier_param: str | None = request.query_params.get("tier")
        tier: PriceTier | None = None
        if tier_param is not None:
            tiers = list(PriceTier)
            idx: int = int(tier_param)
            if 0 <= idx < len(tiers):
                tier = tiers[idx]

        raw_cats: list[str] = request.query_params.getlist("category")
        category_ids: list[int] | None = [int(c) for c in raw_cats] if raw_cats else None

        page: int = int(request.query_params.get("page", 0))
        size: int = int(request.query_params.get("size", 20))

        products, total = service.get_filtered(tier, category_ids, page, size)
        return Response(paged_response(products, total, page, size))
