"""Port interfaces (ABCs) for the users bounded context."""
from __future__ import annotations

import abc

from users.domain.models import User


class UserRepository(abc.ABC):
    """Abstraction for user persistence."""

    @abc.abstractmethod
    def find_by_username(self, username: str) -> User | None:
        """Return a domain ``User`` or ``None``."""

    @abc.abstractmethod
    def check_password(self, username: str, raw_password: str) -> bool:
        """Verify a raw password against the stored hash."""

    @abc.abstractmethod
    def user_exists(self, username: str) -> bool:
        """Check whether a username is already taken."""


class TokenBlacklistPort(abc.ABC):
    """Abstraction for JWT token revocation."""

    @abc.abstractmethod
    def blacklist(self, token: str) -> None:
        """Mark a token as revoked."""

    @abc.abstractmethod
    def is_blacklisted(self, token: str) -> bool:
        """Return ``True`` if the token has been revoked."""
