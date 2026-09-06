
## PostgreSQL Setup

The project uses PostgreSQL as a persistent database running in Docker.

### 1. Environment variables

Database credentials are stored in `.env` and are not committed to Git.

```env
POSTGRES_DB=war_analysis
POSTGRES_USER=war
POSTGRES_PASSWORD=your_password
```

`.env` is included in `.gitignore`.

### 2. PostgreSQL in Docker

PostgreSQL runs as a separate Docker Compose service.

Database files are persisted on the host:

```text
data/
└── db/
    └── postgres/
```

The directory is mounted to PostgreSQL's data directory:

```yaml
volumes:
  - ./data/db/postgres:/var/lib/postgresql/data
```

This keeps database data independent from the PostgreSQL container lifecycle.

### 3. Python dependencies

The project uses:

```text
SQLAlchemy
Alembic
psycopg[binary]
```

* **SQLAlchemy** — database access and ORM
* **psycopg** — PostgreSQL driver
* **Alembic** — database schema migrations

### 4. Database configuration

The application receives the database connection string through the `DATABASE_URL` environment variable:

```text
postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
```

Inside Docker Compose, `postgres` is the PostgreSQL service hostname.

### 5. Alembic initialization

Alembic is initialized with:

```bash
docker compose run --rm app alembic init alembic
```

This creates:

```text
alembic/
├── versions/
├── env.py
└── script.py.mako

alembic.ini
```

Alembic configuration and migration files are committed to Git.

### 6. SQLAlchemy models

Database configuration and models are stored under:

```text
src/models/db/
```

The SQLAlchemy `Base` metadata is connected to Alembic through `alembic/env.py`.

### 7. Initial migration

A migration is generated from the SQLAlchemy models:

```bash
docker compose run --rm app alembic revision --autogenerate -m "create records table"
```

The migration is then applied to PostgreSQL:

```bash
docker compose run --rm app alembic upgrade head
```

This creates the initial database schema and the `alembic_version` table used to track applied migrations.
