"""Django app configuration for the users bounded context."""
from __future__ import annotations

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Users app config — wires the DI container on startup."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "users"

    def ready(self) -> None:
        """Initialise the DI container when Django starts."""
        from users.containers import UserContainer

        container = UserContainer()
        container.wire(modules=[
            "users.application.views.login_view",
            "users.application.views.logout_view",
        ])
