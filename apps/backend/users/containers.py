"""DI container for the users bounded context."""
from __future__ import annotations

from dependency_injector import containers, providers

from users.domain.services import AuthService
from users.infrastructure.repositories import DjangoUserRepository, InMemoryTokenBlacklist
from users.infrastructure.token_service import TokenService


class UserContainer(containers.DeclarativeContainer):
    """Wire domain services to infrastructure implementations."""

    wiring_config = containers.WiringConfiguration(
        modules=["users.application.views"],
    )

    user_repo = providers.Singleton(DjangoUserRepository)
    token_blacklist = providers.Singleton(InMemoryTokenBlacklist)
    token_service = providers.Singleton(TokenService)

    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repo,
        token_blacklist=token_blacklist,
    )

