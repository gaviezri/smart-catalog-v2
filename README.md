# Smart Catalog V2

This is an implementation of the smart catalog that includes smart matchmaking engine.
The vision of this system is a read-heavy, zero-latency platform that would need to maintain data integrity and availability no matter the demand.

see the `docs` for architectural decisions and topology.

## Launch Guide

### Quick Start (Simple Mode)

Single Postgres instance + Django backend — good for development and testing.

```bash
docker compose up --build
```

This will:
1. Start a Postgres instance with pgvector + pgvectorscale extensions
2. Run Django migrations and seed the database with sample data
3. Start the backend on **http://localhost:8000**
4. API docs available at **http://localhost:8000/api/docs/**

### Default Credentials
| User | Password | Role |
|------|----------|------|
| admin | admin123 | ADMIN |
| user | user123 | USER |

### HA Mode (Production Topology)

The full HA topology with Patroni (streaming replication), PgBouncer (connection pooling), and HAProxy (read/write split routing) is prepared as a Compose profile. To activate:

```bash
docker compose --profile ha up --build
```

> **Note:** The HA services in `docker-compose.yml` are currently stubbed out. Uncomment and configure them using the configs under `deploy/` (haproxy, pgbouncer, postgres) before using this mode.

### Running Tests

```bash
cd apps/backend
pip install -r requirements.txt
python -m pytest -v
```

### Useful Commands

```bash
# Seed database manually
docker compose exec backend python manage.py seed_db

# Open Django shell
docker compose exec backend python manage.py shell

# View API schema
curl http://localhost:8000/api/schema/ | python -m json.tool
```
