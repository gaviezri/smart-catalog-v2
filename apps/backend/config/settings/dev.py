"""Development settings."""
from __future__ import annotations

from config.settings.base import *  # noqa: F401, F403

DEBUG: bool = True

# SQLite in-memory — no Postgres needed for local dev / tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
    "replica": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# No read/write routing needed with a single SQLite instance
DATABASE_ROUTERS: list[str] = []

# Faster password hashing for dev/tests
PASSWORD_HASHERS: list[str] = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
