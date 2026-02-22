"""Concrete repository implementations for the users bounded context."""
from __future__ import annotations

import threading

from users.domain.models import Role, User
from users.domain.ports import TokenBlacklistPort, UserRepository
from users.infrastructure.orm_models import UserORM


class DjangoUserRepository(UserRepository):
    """User repository backed by Django ORM."""

    def find_by_username(self, username: str) -> User | None:
        """Look up a user and map to a domain entity."""
        try:
            orm_user: UserORM = UserORM.objects.get(username=username)
        except UserORM.DoesNotExist:
            return None
        return User(
            id=orm_user.pk,
            username=orm_user.username,
            role=Role(orm_user.role),
        )

    def check_password(self, username: str, raw_password: str) -> bool:
        """Verify a raw password against the stored hash."""
        try:
            orm_user: UserORM = UserORM.objects.get(username=username)
        except UserORM.DoesNotExist:
            return False
        return orm_user.check_password(raw_password)

    def user_exists(self, username: str) -> bool:
        """Check whether a username is already taken."""
        return UserORM.objects.filter(username=username).exists()


class InMemoryTokenBlacklist(TokenBlacklistPort):
    """In-memory token blacklist.

    Suitable for MVP / single-worker deployments only.
    See APPLICATION-LAYER.md § Known Limitations for details.
    """

    def __init__(self) -> None:
        self._blacklisted: set[str] = set()
        self._lock: threading.Lock = threading.Lock()

    def blacklist(self, token: str) -> None:
        """Add a token to the revocation set."""
        with self._lock:
            self._blacklisted.add(token)

    def is_blacklisted(self, token: str) -> bool:
        """Check if the token has been revoked."""
        with self._lock:
            return token in self._blacklisted
