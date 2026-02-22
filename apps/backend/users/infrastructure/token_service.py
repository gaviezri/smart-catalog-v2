"""Infrastructure service for JWT token issuance.

Isolates simplejwt mechanics from the application layer so views
never touch ORM models directly for token creation.
"""
from __future__ import annotations

from rest_framework_simplejwt.tokens import RefreshToken

from users.domain.models import User
from users.infrastructure.orm_models import UserORM


class TokenService:
    """Issue JWT tokens for a domain user."""

    def issue_tokens(self, user: User) -> dict[str, str]:
        """Generate access + refresh tokens with role/username claims.

        Args:
            user: Domain user entity (already authenticated).

        Returns:
            Dict with ``access`` and ``refresh`` token strings.
        """
        orm_user: UserORM = UserORM.objects.get(pk=user.id)
        refresh: RefreshToken = RefreshToken.for_user(orm_user)
        refresh["role"] = user.role.value
        refresh["username"] = user.username

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
