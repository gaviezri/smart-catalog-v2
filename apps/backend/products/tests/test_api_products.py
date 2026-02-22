"""API integration tests for product endpoints."""
from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from products.infrastructure.orm_models import BrandORM, CategoryORM, ProductORM
from users.infrastructure.orm_models import UserORM


@pytest.fixture()
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture()
def admin_user(db: None) -> UserORM:
    return UserORM.objects.create_user(username="admin", password="admin123", role="ADMIN")


@pytest.fixture()
def regular_user(db: None) -> UserORM:
    return UserORM.objects.create_user(username="user", password="user123", role="USER")


def _login(client: APIClient, username: str, password: str) -> str:
    """Login and return the access token."""
    resp = client.post("/api/auth/login", {"username": username, "password": password}, format="json")
    return resp.json()["access"]


@pytest.fixture()
def sample_products(db: None) -> list[ProductORM]:
    """Create a small set of test products."""
    brand: BrandORM = BrandORM.objects.create(name="Nike")
    cat_sport: CategoryORM = CategoryORM.objects.create(name="Sportswear")
    cat_shoes: CategoryORM = CategoryORM.objects.create(name="Sneakers")

    products: list[ProductORM] = []
    for i in range(5):
        p: ProductORM = ProductORM.objects.create(
            title=f"Nike Product {i}",
            brand=brand,
            price=Decimal(f"{50 + i * 100}"),
            tier="BUDGET" if (50 + i * 100) <= 200 else "MID",
            gender="U",
            color="Black",
        )
        p.categories.add(cat_sport, cat_shoes)
        products.append(p)
    return products


@pytest.mark.django_db()
class TestProductListEndpoint:
    """GET /api/products/."""

    def test_list_returns_paginated(
        self, api_client: APIClient, sample_products: list[ProductORM]
    ) -> None:
        response = api_client.get("/api/products/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "content" in data
        assert "totalElements" in data
        assert data["totalElements"] == 5

    def test_list_respects_page_size(
        self, api_client: APIClient, sample_products: list[ProductORM]
    ) -> None:
        response = api_client.get("/api/products/?size=2&page=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["content"]) == 2
        assert data["size"] == 2


@pytest.mark.django_db()
class TestProductFilterEndpoint:
    """GET /api/products/filter."""

    def test_filter_by_tier(
        self, api_client: APIClient, sample_products: list[ProductORM]
    ) -> None:
        response = api_client.get("/api/products/filter?tier=0")  # 0 = BUDGET
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for product in data["content"]:
            assert product["tier"] == "BUDGET"

    def test_filter_requires_params(self, api_client: APIClient, sample_products: list[ProductORM]) -> None:
        response = api_client.get("/api/products/filter")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
class TestProductCreateEndpoint:
    """POST /api/products/create."""

    def test_admin_can_create(self, api_client: APIClient, admin_user: UserORM) -> None:
        token: str = _login(api_client, "admin", "admin123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(
            "/api/products/",
            {
                "title": "New Product",
                "brand_name": "Adidas",
                "category_names": ["Running"],
                "price": "120.00",
                "gender": "M",
                "color": "Blue",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Product"
        assert data["tier"] == "BUDGET"  # 120 ≤ 200
        assert data["brandName"] == "Adidas"

    def test_regular_user_cannot_create(
        self, api_client: APIClient, regular_user: UserORM
    ) -> None:
        token: str = _login(api_client, "user", "user123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = api_client.post(
            "/api/products/",
            {
                "title": "Forbidden",
                "brand_name": "X",
                "category_names": ["Y"],
                "price": "10.00",
                "gender": "U",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create(self, api_client: APIClient) -> None:
        response = api_client.post(
            "/api/products/",
            {"title": "No auth", "brand_name": "X", "category_names": ["Y"], "price": "10", "gender": "U"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
class TestProductDeleteEndpoint:
    """DELETE /api/products/{public_id}."""

    def test_admin_can_delete(
        self, api_client: APIClient, admin_user: UserORM, sample_products: list[ProductORM]
    ) -> None:
        token: str = _login(api_client, "admin", "admin123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        product: ProductORM = sample_products[0]
        response = api_client.delete(f"/api/products/{product.public_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProductORM.objects.filter(pk=product.pk).exists()

    def test_regular_user_cannot_delete(
        self, api_client: APIClient, regular_user: UserORM, sample_products: list[ProductORM]
    ) -> None:
        token: str = _login(api_client, "user", "user123")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        product: ProductORM = sample_products[0]
        response = api_client.delete(f"/api/products/{product.public_id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
class TestCategoryListEndpoint:
    """GET /api/categories/."""

    def test_returns_categories(
        self, api_client: APIClient, sample_products: list[ProductORM]
    ) -> None:
        response = api_client.get("/api/products/categories")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        names: list[str] = [c["name"] for c in data]
        assert "Sportswear" in names
        assert "Sneakers" in names


@pytest.mark.django_db()
class TestTierListEndpoint:
    """GET /api/tiers/."""

    def test_returns_all_tiers(self, api_client: APIClient) -> None:
        response = api_client.get("/api/products/tiers")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        tier_names: list[str] = [t["name"] for t in data]
        assert tier_names == ["BUDGET", "MID", "PREMIUM"]
