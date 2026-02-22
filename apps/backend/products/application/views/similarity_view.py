"""View: hybrid product similarity search."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.application.views.helpers import paged_response
from products.containers import ProductContainer
from products.domain.models import PriceTier
from products.domain.services import ProductService


class ProductSimilarityView(APIView):
    """Hybrid similarity search using vector and metadata filters."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Search similar products",
        description=(
            "Hybrid search using a 1536-dimensional vector and optional metadata filters. "
            "Returns the top 5 most similar products by default."
        ),
        request={
            "application/json": {
                "example": {
                    "vector": [0.0] * 1536,
                    "maxPrice": 100.0,
                    "categories": [1, 2],
                    "tier": 0,
                    "gender": "M",
                    "limit": 5,
                }
            }
        },
        responses={200: dict},
    )
    @inject
    def post(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle POST /api/products/similarity."""
        data = request.data

        try:
            vector = self._get_vector(data)
            max_price = self._get_max_price(data)
            category_ids = self._get_categories(data)
            tier = self._get_tier(data)
            limit = self._get_limit(data)
            gender = data.get("gender")

            filters = [max_price is not None, bool(category_ids), tier is not None, gender is not None]
            if sum(filters) < 2:
                raise ValueError("At least 2 metadata filters (maxPrice, categories, tier, gender) are required.")
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        products = service.find_similar_products(
            vector=vector,
            max_price=max_price,
            category_ids=category_ids,
            tier=tier,
            gender=gender,
            limit=limit,
        )

        return Response(paged_response(products, len(products), 0, limit))

    def _get_vector(self, data: dict) -> list[float]:
        vector = data.get("vector")
        if not vector or not isinstance(vector, list) or len(vector) != 1536:
            raise ValueError("A 1536-dimensional vector is required in the body.")
        return vector

    def _get_max_price(self, data: dict) -> Decimal | None:
        max_price_val = data.get("maxPrice")
        if max_price_val is not None:
            try:
                return Decimal(str(max_price_val))
            except (ValueError, TypeError, InvalidOperation):
                raise ValueError("Invalid maxPrice format.")
        return None

    def _get_categories(self, data: dict) -> list[int] | None:
        category_ids = data.get("categories")
        if category_ids and not isinstance(category_ids, list):
            raise ValueError("categories must be a list of integers.")
        return category_ids

    def _get_tier(self, data: dict) -> PriceTier | None:
        tier_idx = data.get("tier")
        if tier_idx is not None:
            try:
                tiers = list(PriceTier)
                idx = int(tier_idx)
                if 0 <= idx < len(tiers):
                    return tiers[idx]
            except (ValueError, TypeError):
                pass
            raise ValueError("Invalid tier ordinal index.")
        return None

    def _get_limit(self, data: dict) -> int:
        try:
            return int(data.get("limit", 5))
        except (ValueError, TypeError):
            return 5