"""API integration tests for auth endpoints."""
from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient

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


@pytest.mark.django_db()
class TestLoginEndpoint:
    """POST /api/auth/login."""

    def test_login_success(self, api_client: APIClient, admin_user: UserORM) -> None:
        response = api_client.post(
            "/api/auth/login",
            {"username": "admin", "password": "admin123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert data["username"] == "admin"
        assert data["role"] == "ADMIN"

    def test_login_wrong_password(self, api_client: APIClient, admin_user: UserORM) -> None:
        response = api_client.post(
            "/api/auth/login",
            {"username": "admin", "password": "wrong"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_user(self, api_client: APIClient) -> None:
        response = api_client.post(
            "/api/auth/login",
            {"username": "nobody", "password": "pass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
class TestLogoutEndpoint:
    """POST /api/auth/logout."""

    def test_logout_success(self, api_client: APIClient, admin_user: UserORM) -> None:
        # Login first to get a real token
        login_resp = api_client.post(
            "/api/auth/login",
            {"username": "admin", "password": "admin123"},
            format="json",
        )
        token: str = login_resp.json()["access"]

        response = api_client.post(
            "/api/auth/logout",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Logged out successfully."

    def test_logout_without_token(self, api_client: APIClient) -> None:
        response = api_client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_200_OK
