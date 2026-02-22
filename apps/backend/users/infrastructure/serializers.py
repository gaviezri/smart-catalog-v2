"""DRF serializers for the users bounded context."""
from __future__ import annotations

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.infrastructure.orm_models import UserORM


class LoginRequestSerializer(serializers.Serializer):
    """Validates login payloads."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Shape of a successful login response."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    username = serializers.CharField()
    role = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):  # type: ignore[type-arg]
    """Embed ``role`` claim in the JWT access token."""

    @classmethod
    def get_token(cls, user: UserORM) -> any:  # type: ignore[override]
        """Add custom claims to the token."""
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token
