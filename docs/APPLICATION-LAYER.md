# The Application Layer

I chose to introduce a monolithic Django server to serve as the application layer.
Initial implementation took place with Java Spring because Im more comfortable with this framework and I think the Jvm maturity and strong concurrency capabilites
are unmatched in the current serverside scene BUT
since we would like to utilize Python for its great native integration with the ML ecosystem, and faster development speed, I think it's a better option.

Python offers rapid prototyping and with recent upgrades to the Python interpreter its concurrency traits have improved drastically and ofcourse the JIT which is introduced
in recent Python versions could significantly closes the performance gap for high-throughput I/O tasks

A monolithic design is good enough, easier to maintain and deploy at the current phase.
It simplifies the deployment pipeline and lower operational complexity and costs.
The design remains decoupled enough to allow for transitioning  into microservices to handle scaling only on required services in the future.

Django’s 'batteries-included' philosophy provides a cohesive ecosystem that minimizes integration friction between various system components.

I went with Hexagonal over Onion because our scaling challenges are technical, not logical. 
At 100M products, the "how" (Postgres tuning, pgvector, and replica routing) is as important as the "what."
Hexagonal lets us treat our vector search as a specialized adapter. 
This isolates the high-performance infrastructure code from our business logic. If we eventually need to swap pgvector for a dedicated vector DB or change our sharding strategy,
we only swap the adapter—your core API stays untouched. It's a cleaner way to manage a system where the infrastructure is the heavy lifter.

## Dependency Injection

Python isn't Java — DI isn't built in. But without it, hexagonal architecture is just a folder structure.
We use `dependency-injector` with declarative containers because it gives us compile-time-like wiring (the container validates the dependency graph on import) without the annotation magic that makes Spring Boot configs feel like magic.
Each Django app owns its own container. The app's `AppConfig.ready()` wires it. Domain services never import concrete implementations.

## Read/Write Repository Split

With Interface Segregation in mind, `ProductReadRepository` and `ProductWriteRepository` are separate ABCs.
This isn't premature — it maps directly onto the database topology. Reads hit the replica via `DATABASE_ROUTERS`, writes hit the primary.
If we ever need to optimise reads separately (materialised views, caching layer), we swap the read adapter without touching write logic.

In simple mode (default `docker compose up`) both `DB_HOST` and `DB_REPLICA_HOST` point to the same single Postgres container — no actual replication, but the routing logic is exercised end-to-end.
When the HA profile is activated, Patroni handles streaming replication between primary and replica nodes, and HAProxy exposes separate ports for writes (5432) and reads (5433).
The transition is two env vars: `DB_REPLICA_HOST → haproxy`, `DB_REPLICA_PORT → 5433`. Zero code changes.

## Structured Logging

`structlog` over Python's `logging` because we need machine-parseable logs from day one.
Every log entry binds `request_id`, `user_id`, and OTel `trace_id`. When debugging a production issue at 2am, grep-able JSON beats wall-of-text every time.
Console renderer in dev, JSON in prod — same code, different config.

## JWT & Auth Design

`simplejwt` handles the heavy lifting (token issue/refresh/verify, rotation, claim injection).
The domain layer doesn't know JWT exists — it talks to an `AuthenticationPort` ABC.
When we add OAuth later, we write a new adapter, swap it in the DI container, and the domain doesn't change. Zero code modifications to `AuthService`.

## Data Seeding

A single `python manage.py seed_db` command handles the full pipeline: default users + products from `products.json`.
Idempotent — checks if tables already have data before insertion. This runs from the Docker entrypoint before `gunicorn` starts, so every fresh deployment gets a populated catalog out of the box.

## Similarity Search

For our vector-based product discovery, we implemented a hybrid search endpoint that combines semantic similarity with metadata filtering. We allow filtering the similarity search results by all the filters that are currently used for standard product queries (e.g., max price, categories, tier, and gender). This ensures the recommended items are not only visually or semantically similar, but also match the user's explicit preferences.

- **HTTP POST over GET**: Although the similarity search is a read-only operation, we use `POST` instead of `GET`. A 1536-dimensional embedding vector, when represented as a JSON array or a string, easily exceeds the URL length limits of most browsers and proxies (typically 2KB-8KB). `POST` allows us to safely transmit the large vector payload in the request body.
- **Base64 Encoded Vectors over JSON Arrays**: To significantly reduce the payload size and JSON parsing overhead, the 1536-dimensional float32 vector is expected as a base64 encoded string rather than a plain JSON array of numerical floats. A JSON representation of 1536 floats could take over 25KB, whereas the equivalent binary 32-bit floats encoded in base64 take roughly 8KB. The decoding takes place directly in the view layer before passing it down as a standard Python array to the services.
- **Cosine Similarity over L2/L1**: We use **Cosine Distance** (`<=>` operator in `pgvector`) for measuring similarity. While L2 (Euclidean) distance measures the absolute distance between points, Cosine Similarity focuses on the angle between vectors. In high-dimensional embedding spaces, the directional orientation of a vector is often more semantically meaningful than its magnitude, making Cosine Similarity the industry standard for text and image embeddings.

## Known Limitations

### Token Blacklist (In-Memory)
The current token blacklist implementation uses an **in-memory set** to store revoked JWTs.
This means:
- Blacklisted tokens are **lost on server restart**.
- In a multi-worker/multi-process deployment, blacklisted tokens are **not shared** across workers.

This is acceptable for the MVP phase. Before production, this should be replaced with a **Redis-backed** or **database-backed** blacklist to ensure durability and cross-worker consistency.
