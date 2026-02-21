# ── Stage 1: Build dependencies ──────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

COPY apps/backend/requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.13-slim

RUN groupadd -r catalog && useradd -r -g catalog catalog

WORKDIR /app

# Installed Python packages from builder
COPY --from=builder /install /usr/local

# Backend source
COPY apps/backend/ /app/

# Data ingestion scripts (used by `manage.py seed_db`)
# The management command resolves: Path(__file__).parents[5] / "data" / "ingestion"
# __file__ = /app/products/management/commands/seed_db.py  → parents[5] = /
COPY data/ingestion/ /data/ingestion/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    INGESTION_DIR=/data/ingestion

EXPOSE 8000

USER catalog

ENTRYPOINT ["sh", "-c", "\
    echo 'Running migrations...' && \
    python manage.py migrate --noinput && \
    echo 'Seeding database...' && \
    python manage.py seed_db && \
    echo 'Starting gunicorn...' && \
    exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    "]
