"""Pure domain models for the products bounded context."""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


class PriceTier(enum.Enum):
    """Product pricing tiers."""

    BUDGET = "BUDGET"
    MID = "MID"
    PREMIUM = "PREMIUM"


class Gender(enum.Enum):
    """Product target gender."""

    MALE = "M"
    FEMALE = "F"
    UNISEX = "U"


@dataclass(frozen=True)
class Brand:
    """Domain value object for a product brand."""

    id: int
    name: str


@dataclass(frozen=True)
class Category:
    """Domain value object for a product category."""

    id: int
    name: str


@dataclass(frozen=True)
class Product:
    """Domain entity for a catalog product."""

    id: int
    public_id: UUID
    title: str
    brand: Brand
    categories: list[Category] = field(default_factory=list)
    price: Decimal = Decimal("0.00")
    tier: PriceTier = PriceTier.BUDGET
    gender: Gender = Gender.UNISEX
    color: str = ""
    product_url: str = ""
    image_url: str = ""
