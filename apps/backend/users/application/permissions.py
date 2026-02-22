"""Custom DRF permission classes for RBAC."""
from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdmin(BasePermission):
    """Allow access only to users with the ADMIN role."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check the ``role`` attribute on the authenticated user."""
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "ADMIN"
        )


class IsUser(BasePermission):
    """Allow access only to authenticated users (any role)."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check that the user is authenticated."""
        return bool(request.user and request.user.is_authenticated)
