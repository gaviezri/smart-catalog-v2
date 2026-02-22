"""Domain services for the users bounded context."""
from __future__ import annotations

from users.domain.exceptions import InvalidCredentialsError
from users.domain.models import User
from users.domain.ports import TokenBlacklistPort, UserRepository


class AuthService:
    """Handles authentication logic — depends only on ports."""

    def __init__(
        self,
        user_repo: UserRepository,
        token_blacklist: TokenBlacklistPort,
    ) -> None:
        self._user_repo: UserRepository = user_repo
        self._token_blacklist: TokenBlacklistPort = token_blacklist

    def authenticate(self, username: str, password: str) -> User:
        """Validate credentials and return the domain user.

        Raises:
            InvalidCredentialsError: If username/password don't match.
        """
        if not self._user_repo.check_password(username, password):
            raise InvalidCredentialsError

        user: User | None = self._user_repo.find_by_username(username)
        if user is None:
            raise InvalidCredentialsError

        return user

    def logout(self, token: str) -> None:
        """Blacklist the given JWT."""
        self._token_blacklist.blacklist(token)

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token has been revoked."""
        return self._token_blacklist.is_blacklisted(token)
