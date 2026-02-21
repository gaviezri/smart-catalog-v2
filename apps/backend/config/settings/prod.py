"""Production settings."""
from __future__ import annotations

from config.settings.base import *  # noqa: F401, F403

DEBUG: bool = False

# In production, DJANGO_SECRET_KEY and DB credentials MUST be set via env vars.
# ALLOWED_HOSTS should be restricted to actual domains.
