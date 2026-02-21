"""DRF views for the users bounded context."""
from __future__ import annotations

from dependency_injector.wiring import Provide, inject
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.containers import UserContainer
from users.domain.services import AuthService
from users.infrastructure.serializers import LoginRequestSerializer, LoginResponseSerializer
from users.infrastructure.token_service import TokenService


class LoginView(APIView):
    """Authenticate a user and return JWT tokens."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login",
        description="Validate credentials and return access + refresh JWT tokens.",
        request=LoginRequestSerializer,
        responses={200: LoginResponseSerializer, 401: None},
    )
    @inject
    def post(
        self,
        request: Request,
        auth_service: AuthService = Provide[UserContainer.auth_service],
        token_service: TokenService = Provide[UserContainer.token_service],
    ) -> Response:
        """Handle POST /api/auth/login."""
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = auth_service.authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        tokens: dict[str, str] = token_service.issue_tokens(user)

        return Response(
            {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "username": user.username,
                "role": user.role.value,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Blacklist a JWT token."""

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Logout",
        description="Blacklist the provided JWT so it can no longer be used.",
        responses={200: None},
    )
    @inject
    def post(
        self,
        request: Request,
        auth_service: AuthService = Provide[UserContainer.auth_service],
    ) -> Response:
        """Handle POST /api/auth/logout."""
        auth_header: str | None = request.META.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.startswith("Bearer "):
            token: str = auth_header[7:]
            auth_service.logout(token)

        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)

