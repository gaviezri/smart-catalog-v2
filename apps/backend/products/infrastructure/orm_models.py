"""Django ORM models for the products bounded context."""
from __future__ import annotations

import uuid

from django.db import models
from pgvector.django import VectorField


class BrandORM(models.Model):
    """Maps to the ``brands`` table."""

    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "brands"

    def __str__(self) -> str:
        return self.name


class CategoryORM(models.Model):
    """Maps to the ``categories`` table."""

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"

    def __str__(self) -> str:
        return self.name


class ProductORM(models.Model):
    """Maps to the ``product`` table."""

    TIER_CHOICES = [
        ("BUDGET", "Budget"),
        ("MID", "Mid"),
        ("PREMIUM", "Premium"),
    ]
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("U", "Unisex"),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.TextField(blank=True, default="")
    brand = models.ForeignKey(
        BrandORM,
        on_delete=models.CASCADE,
        related_name="products",
    )
    categories = models.ManyToManyField(
        CategoryORM,
        related_name="products",
        db_table="product_categories",
        blank=True,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    color = models.TextField(blank=True, default="")
    product_url = models.TextField(blank=True, default="")
    image_url = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product"
        indexes = [
            models.Index(fields=["brand"], name="idx_product_brand_id_fk"),
            models.Index(fields=["-created_at"], name="idx_product_created_at"),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.brand.name})"


class ProductSearchORM(models.Model):
    """Maps to the ``product_search`` read-optimised projection table."""

    product = models.OneToOneField(
        ProductORM,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="search_projection",
    )
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    brand_id = models.BigIntegerField(null=True, blank=True)
    brand_name = models.TextField(blank=True, default="")
    tier = models.CharField(max_length=20, blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    category_ids = models.JSONField(default=list, blank=True)
    gender = models.CharField(max_length=1, blank=True, default="")
    color = models.TextField(blank=True, default="")

    class Meta:
        db_table = "product_search"
        managed = False  # table is created by init-db.sql, not Django migrations

    def __str__(self) -> str:
        return f"Search({self.product_id})"
