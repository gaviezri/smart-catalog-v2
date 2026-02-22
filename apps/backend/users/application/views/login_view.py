"""View: authenticate a user and return JWT tokens."""
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
