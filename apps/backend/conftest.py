"""conftest.py — shared pytest fixtures and configuration."""
from __future__ import annotations

import django
from django.conf import settings


def pytest_configure() -> None:
    """Ensure Django settings are loaded before any test."""
    settings.DJANGO_SETTINGS_MODULE = "config.settings.dev"  # type: ignore[attr-defined]
    django.setup()
