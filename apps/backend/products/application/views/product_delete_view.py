"""View: delete a product by public ID."""
from __future__ import annotations

from uuid import UUID

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from products.containers import ProductContainer
from products.domain.services import ProductService
from users.application.permissions import IsAdmin


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
