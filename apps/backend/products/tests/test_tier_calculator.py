"""Unit tests for the tier calculator — pure domain logic, no DB."""
from __future__ import annotations

from decimal import Decimal

import pytest

from products.domain.models import PriceTier
from products.domain.tier_calculator import calculate_tier


class TestCalculateTier:
    """Verify tier boundaries: ≤200 → BUDGET, ≤750 → MID, >750 → PREMIUM."""

    @pytest.mark.parametrize(
        ("price", "expected"),
        [
            (Decimal("0"), PriceTier.BUDGET),
            (Decimal("1"), PriceTier.BUDGET),
            (Decimal("199.99"), PriceTier.BUDGET),
            (Decimal("200"), PriceTier.BUDGET),
        ],
    )
    def test_budget_tier(self, price: Decimal, expected: PriceTier) -> None:
        assert calculate_tier(price) == expected

    @pytest.mark.parametrize(
        ("price", "expected"),
        [
            (Decimal("200.01"), PriceTier.MID),
            (Decimal("201"), PriceTier.MID),
            (Decimal("500"), PriceTier.MID),
            (Decimal("750"), PriceTier.MID),
        ],
    )
    def test_mid_tier(self, price: Decimal, expected: PriceTier) -> None:
        assert calculate_tier(price) == expected

    @pytest.mark.parametrize(
        ("price", "expected"),
        [
            (Decimal("750.01"), PriceTier.PREMIUM),
            (Decimal("751"), PriceTier.PREMIUM),
            (Decimal("10000"), PriceTier.PREMIUM),
        ],
    )
    def test_premium_tier(self, price: Decimal, expected: PriceTier) -> None:
        assert calculate_tier(price) == expected
