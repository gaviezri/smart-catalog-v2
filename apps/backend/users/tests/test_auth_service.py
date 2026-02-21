"""Unit tests for AuthService — mocked ports, no DB."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from users.domain.exceptions import InvalidCredentialsError
from users.domain.models import Role, User
from users.domain.ports import TokenBlacklistPort, UserRepository
from users.domain.services import AuthService


@pytest.fixture()
def mock_user_repo() -> MagicMock:
    return MagicMock(spec=UserRepository)


@pytest.fixture()
def mock_blacklist() -> MagicMock:
    return MagicMock(spec=TokenBlacklistPort)


@pytest.fixture()
def auth_service(mock_user_repo: MagicMock, mock_blacklist: MagicMock) -> AuthService:
    return AuthService(user_repo=mock_user_repo, token_blacklist=mock_blacklist)


class TestAuthenticate:
    """Tests for AuthService.authenticate."""

    def test_returns_user_on_valid_credentials(
        self,
        auth_service: AuthService,
        mock_user_repo: MagicMock,
    ) -> None:
        user = User(id=1, username="admin", role=Role.ADMIN)
        mock_user_repo.check_password.return_value = True
        mock_user_repo.find_by_username.return_value = user

        result = auth_service.authenticate("admin", "admin123")

        assert result == user
        mock_user_repo.check_password.assert_called_once_with("admin", "admin123")

    def test_raises_on_wrong_password(
        self,
        auth_service: AuthService,
        mock_user_repo: MagicMock,
    ) -> None:
        mock_user_repo.check_password.return_value = False

        with pytest.raises(InvalidCredentialsError):
            auth_service.authenticate("admin", "wrong")

    def test_raises_when_user_not_found_after_password_check(
        self,
        auth_service: AuthService,
        mock_user_repo: MagicMock,
    ) -> None:
        mock_user_repo.check_password.return_value = True
        mock_user_repo.find_by_username.return_value = None

        with pytest.raises(InvalidCredentialsError):
            auth_service.authenticate("ghost", "pass")


class TestLogout:
    """Tests for AuthService.logout."""

    def test_blacklists_token(
        self,
        auth_service: AuthService,
        mock_blacklist: MagicMock,
    ) -> None:
        auth_service.logout("some-jwt-token")
        mock_blacklist.blacklist.assert_called_once_with("some-jwt-token")


class TestIsTokenBlacklisted:
    """Tests for AuthService.is_token_blacklisted."""

    def test_returns_true_for_blacklisted(
        self,
        auth_service: AuthService,
        mock_blacklist: MagicMock,
    ) -> None:
        mock_blacklist.is_blacklisted.return_value = True
        assert auth_service.is_token_blacklisted("revoked-token") is True

    def test_returns_false_for_valid(
        self,
        auth_service: AuthService,
        mock_blacklist: MagicMock,
    ) -> None:
        mock_blacklist.is_blacklisted.return_value = False
        assert auth_service.is_token_blacklisted("good-token") is False
