"""Base Django settings shared across all environments."""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

import environ
import structlog

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=False)

# ── Security ─────────────────────────────────────────────────────────────────
SECRET_KEY: str = env("DJANGO_SECRET_KEY", default="change-me-in-production")
ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])

# ── Application definition ───────────────────────────────────────────────────
INSTALLED_APPS: list[str] = [
    # Django
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # Local
    "users",
    "products",
]

MIDDLEWARE: list[str] = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF: str = "config.urls"
WSGI_APPLICATION: str = "config.wsgi.application"
ASGI_APPLICATION: str = "config.asgi.application"

# ── Auth ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL: str = "users.UserORM"

# ── Database ─────────────────────────────────────────────────────────────────
DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="smart_catalog"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    },
    "replica": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="smart_catalog"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_REPLICA_HOST", default="localhost"),
        "PORT": env("DB_REPLICA_PORT", default="5433"),
    },
}

DATABASE_ROUTERS: list[str] = ["config.db_router.ReadWriteRouter"]

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# ── DRF ──────────────────────────────────────────────────────────────────────
REST_FRAMEWORK: dict = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "config.exceptions.global_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ── SimpleJWT ────────────────────────────────────────────────────────────────
SIMPLE_JWT: dict = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": "users.infrastructure.serializers.CustomTokenObtainPairSerializer",
}

# ── drf-spectacular ──────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS: dict = {
    "TITLE": "Smart Catalog API",
    "DESCRIPTION": "Product catalog with vector search",
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS: list[str] = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ],
)
CORS_ALLOW_CREDENTIALS: bool = True

# ── Structured Logging (structlog) ───────────────────────────────────────────
LOGGING: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# ── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE: str = "en-us"
TIME_ZONE: str = "UTC"
USE_TZ: bool = True
