"""Global DRF exception handler.

Maps domain exceptions to consistent JSON error envelopes.
"""
from __future__ import annotations

from typing import Any

import structlog
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = structlog.get_logger(__name__)

# ── Domain exception → (HTTP status, error code) mapping ─────────────────────
# Import domain exceptions lazily inside the handler to avoid circular imports.

_DOMAIN_EXCEPTION_MAP: dict[str, tuple[int, str]] = {
    "InvalidCredentialsError": (status.HTTP_401_UNAUTHORIZED, "INVALID_CREDENTIALS"),
    "UserNotFoundError": (status.HTTP_404_NOT_FOUND, "USER_NOT_FOUND"),
    "ProductNotFoundError": (status.HTTP_404_NOT_FOUND, "PRODUCT_NOT_FOUND"),
    "InvalidFilterError": (status.HTTP_400_BAD_REQUEST, "INVALID_FILTER"),
}


def global_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Handle both DRF and domain exceptions with a uniform envelope."""
    # Let DRF handle its own exceptions first (validation, auth, etc.)
    response: Response | None = exception_handler(exc, context)

    if response is not None:
        return _wrap_drf_response(response)

    # Map domain exceptions
    exc_name: str = type(exc).__name__
    mapping: tuple[int, str] | None = _DOMAIN_EXCEPTION_MAP.get(exc_name)

    if mapping is not None:
        http_status, error_code = mapping
        logger.warning("domain_exception", code=error_code, detail=str(exc))
        return Response(
            {"error": {"code": error_code, "message": str(exc), "status": http_status}},
            status=http_status,
        )

    # Unhandled — log and return 500
    logger.exception("unhandled_exception", exc_info=exc)
    return Response(
        {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _wrap_drf_response(response: Response) -> Response:
    """Normalise DRF's default error format into our envelope."""
    detail: Any = response.data
    if isinstance(detail, dict) and "detail" in detail:
        detail = detail["detail"]
    response.data = {
        "error": {
            "code": _status_to_code(response.status_code),
            "message": str(detail),
            "status": response.status_code,
        }
    }
    return response


def _status_to_code(http_status: int) -> str:
    """Convert HTTP status to a generic error code string."""
    mapping: dict[int, str] = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        429: "THROTTLED",
    }
    return mapping.get(http_status, "ERROR")
