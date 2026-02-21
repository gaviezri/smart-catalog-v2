"""Django ORM model for the users bounded context."""
from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager["UserORM"]):
    """Custom manager for ``UserORM``."""

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "USER",
    ) -> UserORM:
        """Create and return a regular user."""
        user: UserORM = self.model(username=username, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        password: str,
        role: str = "ADMIN",
    ) -> UserORM:
        """Create and return an admin user."""
        return self.create_user(username=username, password=password, role=role)


class UserORM(AbstractBaseUser):  # type: ignore[type-arg]
    """Django ORM user model — maps to ``app_users`` table."""

    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=10, default="USER")

    objects = UserManager()

    USERNAME_FIELD: str = "username"

    class Meta:
        db_table = "app_users"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
