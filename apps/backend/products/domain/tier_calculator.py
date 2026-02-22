"""Tier calculation — pure domain logic."""
from __future__ import annotations

from decimal import Decimal

from products.domain.models import PriceTier

_BUDGET_MAX: Decimal = Decimal("200")
_MID_MAX: Decimal = Decimal("750")


def calculate_tier(price: Decimal) -> PriceTier:
    """Determine the pricing tier for a given price.

    Thresholds:
        ≤ 200  → BUDGET
        ≤ 750  → MID
        > 750  → PREMIUM
    """
    if price <= _BUDGET_MAX:
        return PriceTier.BUDGET
    if price <= _MID_MAX:
        return PriceTier.MID
    return PriceTier.PREMIUM
