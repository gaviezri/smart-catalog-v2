# Smart Catalog V2

This is an implementation of the smart catalog that includes smart matchmaking engine.
The vision of this system is a read-heavy, zero-latency platform that would need to maintain data integrity and availability no matter the demand.

see the `docs` for architectural decisions and topology.

## Launch Guide

### Quick Start (Simple Mode)

Single Postgres instance + Django backend — good for development and testing.

```bash
docker compose --profile dev up --build
```

This will:
1. Start a Postgres instance with pgvector + pgvectorscale extensions
2. Run Django migrations and seed the database with sample data
3. Start the backend on **http://localhost:8000**
4. Start the frontend on **http://localhost:3000**
5. API docs available at **http://localhost:8000/api/openapi/docs**

### HA Mode (Production Topology)

Full HA stack: etcd → Patroni cluster (streaming replication) → HAProxy (read/write split) → PgBouncer (connection pooling).
(see `docs/DATA-LAYER.md` for more information)

```bash
docker compose --profile production up --build
```

This will spin up:
- **etcd** — distributed config store for Patroni consensus
- **patroni-1 / patroni-2** — managed Postgres nodes with automatic failover
- **HAProxy** — TCP routing: writes on `:5432`, reads on `:5433`; stats dashboard at **http://localhost:1936** (admin/password)
- **PgBouncer** — transaction-mode connection pooling on `:6432`
- **Backend** — Django connecting through PgBouncer → HAProxy → Patroni
- **Frontend** — React app on **http://localhost:3000**

> **Note:** The cluster takes ~30s to stabilise after startup while Patroni elects a primary and streams the initial replication.

### Default Credentials

| User | Password | Role |
|------|----------|------|
| admin | admin123 | ADMIN |
| user | user123 | USER |

### Running Tests

```bash
cd apps/backend
pip install -r requirements.txt
python -m pytest -v
```

### Useful Commands

```bash
# Seed database manually (executed automatically at startup)
docker compose exec backend-dev python manage.py seed_db   # dev mode
docker compose exec backend-production python manage.py seed_db       # HA mode

# Open Django shell
docker compose exec backend-simple python manage.py shell

# View API schema
curl http://localhost:8000/api/openapi/schema | python -m json.tool

# Check Patroni cluster status (HA mode)
docker compose exec patroni-1 patronictl list

# HAProxy stats dashboard
open http://localhost:1936
```
