"""Root DI container — aggregates app-level containers."""
from __future__ import annotations

from dependency_injector import containers, providers


class RootContainer(containers.DeclarativeContainer):
    """Top-level container that wires all app containers together."""

    wiring_config = containers.WiringConfiguration(
        packages=["users.application", "products.application"],
    )

    # App containers are imported and wired in each app's AppConfig.ready().
    # This container exists as the single aggregation point.
    config = providers.Configuration()
