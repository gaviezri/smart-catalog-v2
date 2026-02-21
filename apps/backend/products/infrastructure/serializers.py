"""DRF serializers for the products bounded context."""
from __future__ import annotations

from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    """Category in API responses."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class TierSerializer(serializers.Serializer):
    """Tier in API responses."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class ProductSerializer(serializers.Serializer):
    """Product detail in API responses."""

    public_id = serializers.UUIDField(source="publicId", read_only=True)
    title = serializers.CharField()
    brand_name = serializers.CharField(source="brandName")
    category_names = serializers.ListField(
        child=serializers.CharField(),
        source="categoryNames",
    )
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    tier = serializers.CharField()
    gender = serializers.CharField()
    color = serializers.CharField()
    product_url = serializers.CharField(source="productUrl")
    image_url = serializers.CharField(source="imageUrl")


class ProductCreateSerializer(serializers.Serializer):
    """Validates product creation payloads."""

    title = serializers.CharField()
    brand_name = serializers.CharField(source="brandName")
    category_names = serializers.ListField(
        child=serializers.CharField(),
        source="categoryNames",
    )
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    gender = serializers.CharField(max_length=1)
    color = serializers.CharField(required=False, default="")
    product_url = serializers.CharField(source="productUrl", required=False, default="")
    image_url = serializers.CharField(source="imageUrl", required=False, default="")


class PagedResponseSerializer(serializers.Serializer):
    """Wrapper for paginated responses."""

    content = ProductSerializer(many=True)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    total_elements = serializers.IntegerField(source="totalElements")
    total_pages = serializers.IntegerField(source="totalPages")
    last = serializers.BooleanField()
