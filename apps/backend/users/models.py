"""Re-export ORM models so Django's model discovery finds them.

Django discovers models by importing ``<app>.models``. Since our ORM models
live in ``infrastructure/orm_models.py`` (hexagonal layout), this bridge
module makes them visible to the framework.
"""
from users.infrastructure.orm_models import UserORM  # noqa: F401

__all__: list[str] = ["UserORM"]
