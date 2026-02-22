"""View: list / create products."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.application.views.helpers import paged_response, product_to_dict
from products.containers import ProductContainer
from products.domain.models import Product
from products.domain.services import ProductService
from products.infrastructure.serializers import (
    PagedResponseSerializer,
    ProductCreateSerializer,
    ProductSerializer,
)
from users.application.permissions import IsAdmin


class ProductsView(APIView):
    """List all products (paginated) or create a new one."""

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        elif self.request.method == "POST":
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]

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
        """Handle GET /api/products."""
        page: int = int(request.query_params.get("page", 0))
        size: int = int(request.query_params.get("size", 20))
        products, total = service.get_all_products(page, size)
        return Response(paged_response(products, total, page, size))

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
        """Handle POST /api/products."""
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
        return Response(product_to_dict(product), status=status.HTTP_201_CREATED)
