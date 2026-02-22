# Backend Agent — System Prompt

> This document defines the architectural constraints, conventions, and
> non-negotiable rules for **every** code change inside `apps/backend/`.
> Read it in full before writing or reviewing any code.

---

## 1. Stack & Versions

| Concern | Choice |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.x (latest stable) |
| API layer | Django REST Framework (REST only — serves a React SPA) |
| API docs | `drf-spectacular` (OpenAPI 3.0 schema auto-generation) |
| Database | PostgreSQL with `pgvector-python` via Django ORM |
| Auth | JWT via `djangorestframework-simplejwt` |
| DI | `dependency-injector` (declarative IoC containers) |
| Testing | `pytest` + `pytest-django` |
| Linting / Formatting | Ruff (linter + formatter) |
| Observability | OpenTelemetry SDK → console exporter (swappable) |
| Structured Logging | `structlog` (JSON to console, swappable sink) |
| Package management | `pip` + `requirements.txt` |

---

## 2. Architecture — Hexagonal (Ports & Adapters)

Every Django app **must** follow the hexagonal layout.
The domain **never** imports from Django, DRF, or any infrastructure package.

```
apps/backend/
├── config/                  # Django project settings, urls, wsgi, asgi
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── containers.py        # DI root container
│
├── users/                   # Django app
│   ├── domain/
│   │   ├── models.py        # Pure domain entities / value objects (no Django ORM)
│   │   ├── services.py      # Business logic — depends only on ports
│   │   ├── ports.py         # Abstract interfaces (ABCs) for repos & external services
│   │   └── exceptions.py
│   ├── infrastructure/
│   │   ├── orm_models.py    # Django ORM models (the adapter)
│   │   ├── repositories.py  # Concrete repo implementations (implement ports)
│   │   └── serializers.py   # DRF serializers
│   ├── application/
│   │   ├── views.py         # DRF views / viewsets — thin, delegates to services
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── containers.py        # App-level DI container
│   └── apps.py
│
├── products/                # Same hexagonal structure as users/
│   ├── domain/
│   ├── infrastructure/
│   ├── application/
│   └── containers.py
│
└── manage.py
```

### Layer Rules

| Layer | May import from | Must **not** import from |
|---|---|---|
| `domain/` | Python stdlib only | Django, DRF, infra, application |
| `infrastructure/` | `domain/` (ports & entities) | `application/` |
| `application/` | `domain/`, `infrastructure/` (via DI) | — |
| `config/` | All (wiring only) | — |

---

## 3. SOLID Principles

1. **Single Responsibility** — One reason to change per class. Services don't serialize; views don't query.
2. **Open/Closed** — Extend via new adapters, not by modifying existing domain code.
3. **Liskov Substitution** — Every port implementation must be a drop-in for its ABC.
4. **Interface Segregation** — Keep ports focused: `ProductReadRepository` vs `ProductWriteRepository`.
5. **Dependency Inversion** — Domain defines ports (ABCs); infrastructure provides implementations; wiring happens in DI containers.

---

## 4. Dependency Injection

Use `dependency-injector` with **declarative containers**.

```python
# products/containers.py
from dependency_injector import containers, providers
from products.domain.ports import ProductReadRepository
from products.infrastructure.repositories import DjangoProductReadRepository
from products.domain.services import ProductService

class ProductContainer(containers.DeclarativeContainer):
    product_read_repo = providers.Singleton(DjangoProductReadRepository)
    product_service = providers.Factory(
        ProductService,
        read_repo=product_read_repo,
    )
```

- **Never** use `import` to resolve a concrete dependency inside domain code.
- Services receive dependencies through constructor injection.
- Wire containers in `config/containers.py` and call `container.wire()` in `AppConfig.ready()`.

---

## 5. Authentication & Authorization

### JWT

- Use `djangorestframework-simplejwt` for token issue / refresh / verify.
- Store refresh tokens server-side (DB-backed) so they can be revoked.
- Access token lifetime: **15 min**. Refresh token lifetime: **7 days**.

### OAuth-Ready Design

- Decouple authentication from identity resolution:
  - `AuthenticationPort` ABC in `users/domain/ports.py` — returns a domain `User` entity.
  - Current adapter: `JWTAuthenticationAdapter`.
  - Future adapter: `OAuthAuthenticationAdapter` (swap via DI, zero domain changes).

### RBAC

| Role | Permissions |
|---|---|
| `USER` | Read products, search, manage own profile |
| `ADMIN` | Full CRUD on products, manage users |

- Use DRF's `permission_classes` on views.
- Roles stored on the user model; checked via custom `IsAdmin` / `IsUser` permission classes.

---

## 6. Database

### Django ORM + pgvector

- ORM models live in `infrastructure/orm_models.py`.
- Use `pgvector.django` for `VectorField` on the `ProductSearch` model.
- The `product_search` table is a **read-optimised projection** — it is populated by the seeding pipeline and kept in sync via domain events or signals.

### Read/Write Splitting

- Configure two database aliases in settings: `default` (writer) and `replica` (reader).
- Implement a custom `DATABASE_ROUTER` that routes:
  - `db_for_read()` → `replica`
  - `db_for_write()` → `default`
- PgBouncer + HAProxy handle the physical routing (see `docs/DATA-LAYER.md`).

---

## 7. Observability

### OpenTelemetry

- Initialise the OTel SDK in `config/settings/base.py` (or a dedicated `config/telemetry.py`).
- Use `opentelemetry-instrumentation-django` for automatic span creation.
- **Current exporter**: `ConsoleSpanExporter`.
- **Design for swap**: exporter is configured via env var `OTEL_EXPORTER` (`console` | `otlp` | `jaeger`), resolved at startup.

### Structured Logging — `structlog`

- Configure `structlog` to output **JSON lines** to stdout.
- Bind `request_id`, `user_id`, and `trace_id` (from OTel context) to every log entry.
- Never use `print()` — always `structlog.get_logger()`.

---

## 8. Django Apps

### `users`
- Custom user model extending `AbstractBaseUser`.
- Registration, login (JWT issue), profile management.
- Roles: `USER`, `ADMIN`.

### `products`
- CRUD for products, brands, categories.
- Vector search via `product_search` table.
- Filtering by brand, tier, category, gender, price range.

---

## 9. Testing

- Use `pytest` + `pytest-django` exclusively.
- **Unit tests** for domain services — mock ports, no DB.
- **Integration tests** for repositories — use `@pytest.mark.django_db`.
- **API tests** for views — use DRF's `APIClient`.
- Aim for **≥ 80%** coverage on domain and application layers.
- Place tests inside each app: `users/tests/`, `products/tests/`.

---

## 10. Code Style & Conventions

- **Ruff** is the single tool for linting and formatting. Config lives in `pyproject.toml`.
- **Type hints everywhere** — all function parameters, return types, local variables where non-obvious, and class attributes. Use `from __future__ import annotations` in every module.
- Docstrings: Google style.
- Naming:
  - Files: `snake_case.py`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- Every public module has an `__init__.py` that explicitly exports symbols.
- No wildcard imports.
- No business logic in views — views are thin dispatchers.
- No raw SQL unless explicitly justified and isolated in a repository adapter.
- **Keep files small.** Each `.py` file should stay as short as possible within its contextual scope. When a file grows beyond a single focused concern, split it immediately — promote the file to a **directory** (package) with an `__init__.py` and dedicated sub-modules. For example, `services.py` → `services/user_registration.py`, `services/user_authentication.py`, etc. Never hesitate to create more files; fewer lines per file is always preferred.

---

## 11. API Documentation (OpenAPI)

- Use `drf-spectacular` for automatic OpenAPI 3.0 schema generation.
- **Every view/viewset** must be annotated with `@extend_schema()` — include summary, description, request/response serializers, and error responses.
- Serve interactive docs at `/api/docs/` (Swagger UI) and `/api/schema/` (raw YAML).
- Keep schema annotations co-located with the view, not in a separate file.

---

## 12. Exception Handling

- **Global exception handler**: register a custom DRF `EXCEPTION_HANDLER` in settings that catches all unhandled exceptions, logs them via `structlog`, and returns a consistent JSON error envelope:
  ```json
  {"error": {"code": "PRODUCT_NOT_FOUND", "message": "...", "status": 404}}
  ```
- **Domain exceptions**: each app defines its own exceptions in `domain/exceptions.py` (e.g. `ProductNotFoundException`, `InsufficientPermissionsError`). These are pure Python exceptions — no DRF dependency.
- **Mapping layer**: the global handler maps domain exceptions → HTTP status codes. Adding a new domain exception requires only adding an entry to the mapping, not changing view code.
- Never catch-and-silence exceptions in views — let them propagate to the handler.

---

## 13. Data Seeding

On startup (via a Django management command called from the entrypoint), the system
checks if the `product` table is empty. If so, it runs the seeding pipeline located
in `data/ingestion/`:

1. `generate_products.py` → `products.json`
2. `generate_embeddings.py` → `product_search.json` (1536-dim vectors via local model)
3. `seed_db.py` — inserts brands, categories, products, products_categories, and product_search

This is idempotent and only runs when the database is empty.

---

## 14. Environment Configuration

- All secrets and environment-specific values come from **environment variables**.
- Use `python-decouple` or `django-environ` for typed access with defaults.
- Never commit `.env` files — provide a `.env.example` template.

---

## 15. Non-Negotiable Rules

> [!CAUTION]
> Violating any of these rules must be flagged and resolved before merge.

1. **Domain layer is framework-free** — no Django/DRF imports in `domain/`.
2. **All dependencies are injected** — no hard-coded instantiation of infrastructure in domain or application code.
3. **No logic in views** — views validate input, call a service, return a response.
4. **Every public endpoint has a permission class**.
5. **Every service method has a corresponding test**.
6. **Ruff must pass with zero warnings** before commit.
7. **Secrets never appear in code or version control**.
8. **Every view has an `@extend_schema()` annotation** — no undocumented endpoints.
9. **All exceptions flow through the global handler** — no ad-hoc try/except in views that swallow errors.
