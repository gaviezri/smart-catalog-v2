"""Pure domain models for the users bounded context."""
from __future__ import annotations

import enum
from dataclasses import dataclass


class Role(enum.Enum):
    """User roles for RBAC."""

    ADMIN = "ADMIN"
    USER = "USER"


@dataclass(frozen=True)
class User:
    """Domain entity representing an authenticated user."""

    id: int
    username: str
    role: Role
