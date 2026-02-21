"""DRF views for the products bounded context."""
from __future__ import annotations

import math
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.containers import ProductContainer
from products.domain.models import PriceTier, Product
from products.domain.services import ProductService
from products.infrastructure.serializers import (
    CategorySerializer,
    PagedResponseSerializer,
    ProductCreateSerializer,
    ProductSerializer,
    TierSerializer,
)
from users.application.permissions import IsAdmin


# ── Helpers ──────────────────────────────────────────────────────────────────

def _product_to_dict(p: Product) -> dict:
    """Map a domain Product to the serializer's expected shape."""
    return {
        "publicId": p.public_id,
        "title": p.title,
        "brandName": p.brand.name,
        "categoryNames": [c.name for c in p.categories],
        "price": p.price,
        "tier": p.tier.value,
        "gender": p.gender.value,
        "color": p.color,
        "productUrl": p.product_url,
        "imageUrl": p.image_url,
    }


def _paged_response(products: list[Product], total: int, page: int, size: int) -> dict:
    """Build the paged response envelope."""
    total_pages: int = max(1, math.ceil(total / size))
    return {
        "content": [_product_to_dict(p) for p in products],
        "page": page,
        "size": size,
        "totalElements": total,
        "totalPages": total_pages,
        "last": page >= total_pages - 1,
    }


# ── Views ────────────────────────────────────────────────────────────────────

class ProductListView(APIView):
    """List all products (paginated)."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List products",
        description="Paginated list of all products.",
        parameters=[
            OpenApiParameter("page", int, description="Page number (0-indexed)", required=False),
            OpenApiParameter("size", int, description="Page size", required=False),
        ],
        responses={200: PagedResponseSerializer},
    )
    @inject
    def get(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle GET /api/products/."""
        page: int = int(request.query_params.get("page", 0))
        size: int = int(request.query_params.get("size", 20))
        products, total = service.get_all_products(page, size)
        return Response(_paged_response(products, total, page, size))


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
        return Response(_paged_response(products, total, page, size))


class ProductCreateView(APIView):
    """Create a new product (ADMIN only)."""

    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Create product",
        description="Create a new product. Tier is auto-calculated from price.",
        request=ProductCreateSerializer,
        responses={201: ProductSerializer},
    )
    @inject
    def post(
        self,
        request: Request,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle POST /api/products/."""
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product: Product = service.create(
            title=data["title"],
            brand_name=data["brandName"],
            category_names=data["categoryNames"],
            price=data["price"],
            gender=data["gender"],
            color=data.get("color", ""),
            product_url=data.get("productUrl", ""),
            image_url=data.get("imageUrl", ""),
        )
        return Response(_product_to_dict(product), status=status.HTTP_201_CREATED)


class ProductDeleteView(APIView):
    """Delete a product by public ID (ADMIN only)."""

    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Delete product",
        description="Delete a product by its public UUID.",
        responses={204: None},
    )
    @inject
    def delete(
        self,
        request: Request,
        public_id: str,
        service: ProductService = Provide[ProductContainer.product_service],
    ) -> Response:
        """Handle DELETE /api/products/{public_id}."""
        service.delete(UUID(public_id))
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        """Handle GET /api/categories/."""
        categories = service.get_all_categories()
        return Response([{"id": c.id, "name": c.name} for c in categories])


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
        """Handle GET /api/tiers/."""
        return Response(service.get_all_tiers())
