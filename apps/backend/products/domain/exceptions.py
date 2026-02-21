"""Domain exceptions for the products bounded context."""
from __future__ import annotations

from uuid import UUID


class ProductNotFoundError(Exception):
    """Raised when a product cannot be found."""

    def __init__(self, public_id: UUID) -> None:
        super().__init__(f"Product not found: {public_id}")


class InvalidFilterError(Exception):
    """Raised when filter parameters are invalid or missing."""

    def __init__(self, message: str = "At least one filter parameter is required.") -> None:
        super().__init__(message)
