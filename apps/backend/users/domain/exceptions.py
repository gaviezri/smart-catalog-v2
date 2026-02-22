"""Domain exceptions for the users bounded context."""
from __future__ import annotations


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid username or password.")


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""

    def __init__(self, username: str) -> None:
        super().__init__(f"User not found: {username}")
