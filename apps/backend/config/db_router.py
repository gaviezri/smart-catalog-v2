"""Database router for read/write splitting.

Routes read queries to the ``replica`` database and writes to ``default``.
PgBouncer + HAProxy handle the physical routing underneath.
"""
from __future__ import annotations

from typing import Any


class ReadWriteRouter:
    """Route DB operations between writer (default) and reader (replica)."""

    def db_for_read(self, model: type, **hints: Any) -> str:  # noqa: ARG002
        """Send all reads to the replica."""
        return "replica"

    def db_for_write(self, model: type, **hints: Any) -> str:  # noqa: ARG002
        """Send all writes to the default (primary)."""
        return "default"

    def allow_relation(
        self, obj1: Any, obj2: Any, **hints: Any  # noqa: ARG002
    ) -> bool:
        """Allow relations between objects in both databases."""
        return True

    def allow_migrate(
        self,
        db: str,
        app_label: str,  # noqa: ARG002
        model_name: str | None = None,  # noqa: ARG002
        **hints: Any,  # noqa: ARG002
    ) -> bool:
        """Only run migrations on the default (primary) database."""
        return db == "default"
