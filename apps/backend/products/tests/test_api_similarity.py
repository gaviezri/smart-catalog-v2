"""API integration tests for product similarity endpoint."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch, MagicMock
from uuid import uuid4

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from products.domain.models import Brand, Category, PriceTier, Product, Gender


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def mock_products() -> list[Product]:
    """Create domain Product entities to return from the mocked service."""
    brand = Brand(id=1, name="Nike")
    cat_sport = Category(id=10, name="Sportswear")

    p1 = Product(
        id=100,
        public_id=uuid4(),
        title="Running Shoes",
        brand=brand,
        categories=[cat_sport],
        price=Decimal("120.00"),
        tier=PriceTier.BUDGET,
        gender=Gender.MALE,
    )

    p2 = Product(
        id=101,
        public_id=uuid4(),
        title="Premium Jacket",
        brand=brand,
        categories=[cat_sport],
        price=Decimal("450.00"),
        tier=PriceTier.PREMIUM,
        gender=Gender.MALE,
    )

    p3 = Product(
        id=102,
        public_id=uuid4(),
        title="Women's Top",
        brand=brand,
        categories=[],
        price=Decimal("30.00"),
        tier=PriceTier.BUDGET,
        gender=Gender.FEMALE,
    )

    return [p1, p2, p3]


class TestProductSimilarityEndpoint:
    """POST /api/products/similarity."""

    def test_requires_vector(self, api_client: APIClient) -> None:
        response = api_client.post("/api/products/similarity", {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "1536-dimensional vector is required" in response.json()["error"]

    def test_invalid_vector_size(self, api_client: APIClient) -> None:
        response = api_client.post("/api/products/similarity", {"vector": [1.0, 2.0]}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("products.domain.services.ProductService.find_similar_products")
    def test_basic_similarity_search(
        self, mock_find: MagicMock, api_client: APIClient, mock_products: list[Product]
    ) -> None:
        # Arrange
        mock_find.return_value = mock_products
        vector = [0.9] + [0.0] * 1535

        # Act
        response = api_client.post(
            "/api/products/similarity",
            {"vector": vector, "gender": "M", "maxPrice": 500.0},
            format="json"
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["content"]) == 3
        # Should match what the mock returned
        assert data["content"][0]["title"] == "Running Shoes"
        assert data["content"][1]["title"] == "Premium Jacket"

        # Verify the service was called securely with the extracted filters
        mock_find.assert_called_once_with(
            vector=vector,
            max_price=Decimal("500.0"),
            category_ids=None,
            tier=None,
            gender="M",
            limit=5,
        )

    def test_requires_at_least_two_filters(self, api_client: APIClient) -> None:
        vector = [0.9] + [0.0] * 1535
        # Only 1 filter
        response = api_client.post(
            "/api/products/similarity", 
            {"vector": vector, "gender": "M"}, 
            format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "At least 2 metadata filters" in response.json()["error"]
        
        # 0 filters
        response2 = api_client.post(
            "/api/products/similarity", 
            {"vector": vector}, 
            format="json"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    @patch("products.domain.services.ProductService.find_similar_products")
    def test_parses_filters_correctly(
        self, mock_find: MagicMock, api_client: APIClient, mock_products: list[Product]
    ) -> None:
        mock_find.return_value = [mock_products[0]]
        vector = [0.0, 0.9] + [0.0] * 1534
        
        # Act
        response = api_client.post(
            "/api/products/similarity", 
            {
                "vector": vector, 
                "maxPrice": 200.0,
                "categories": [10],
                "tier": 0, # BUDGET
                "gender": "M",
                "limit": 2
            }, 
            format="json"
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["content"]) == 1

        # Most importantly, verify the view passed the correctly parsed types to the domain service
        mock_find.assert_called_once_with(
            vector=vector,
            max_price=Decimal("200.0"),
            category_ids=[10],
            tier=PriceTier.BUDGET,
            gender="M",
            limit=2,
        )

    def test_invalid_max_price(self, api_client: APIClient) -> None:
        vector = [0.1] * 1536
        response = api_client.post(
            "/api/products/similarity", 
            {"vector": vector, "maxPrice": "invalid", "gender": "M"}, 
            format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid maxPrice format" in response.json()["error"]
