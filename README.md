# War Analysis

Python project for collecting, storing, processing, and analyzing publicly available data related to the Russia–Ukraine war.

The project combines data from multiple open sources into a local PostgreSQL database and provides tools for parsing, importing, querying, and analyzing the collected information.

The project is designed as an extensible platform: new data sources and analytical components can be added without changing the overall architecture.

---

## Features

* Collection of data from public open sources
* Persistent storage in PostgreSQL/PostGIS
* SQLAlchemy ORM models
* Database schema migrations with Alembic
* Repository layer for database access
* Source-specific services and parsers
* Historical geographic data processing
* SQL-based analysis
* Python-based analytical scripts
* Database backup utilities
* Docker-based development environment

---

# Architecture

The project is organized around several main layers.

```text
Open data sources
        │
        ▼
┌───────────────────────┐
│ Source-specific       │
│ clients / parsers     │
│ / crawlers            │
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│ Services              │
│ normalization and     │
│ persistence logic     │
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│ PostgreSQL / PostGIS  │
└───────────────────────┘
        │
        ▼
┌───────────────────────┐
│ Analytics             │
│ SQL / Python          │
│ statistics / charts   │
└───────────────────────┘
```

The architecture separates:

* source communication;
* data parsing;
* source-specific business logic;
* database models and access;
* analysis.

---

# Project Structure

```text
war-analysis/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docs/
│   ├── analysis/
│   │   └── sql/
│   └── db/
│
├── scripts/
│   ├── analytics/
│   ├── db/
│   │   └── backup/
│   ├── deepstatemap/
│   └── ualosses/
│
├── src/
│   ├── models/
│   │   └── db/
│   │       ├── database.py
│   │       ├── deepstatemap/
│   │       └── ualosses/
│   │
│   └── services/
│       ├── analytics/
│       └── osint_sources/
│           ├── deepstatemap/
│           └── ualosses/
│
├── tests/
│
├── data/
│   └── db/
│       └── postgres/
│
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md
```

---

# Data Sources

The project currently contains integrations and processing logic for the following public sources.

## DeepStateMap

`DeepStateMap` integration provides tools for working with publicly available geographic and historical data.

Main components:

```text
src/services/osint_sources/deepstatemap/
```

The source integration contains:

* HTTP client;
* configuration;
* parser;
* validator;
* data models;
* service layer;
* custom exceptions.

Database models and repository logic are located in:

```text
src/models/db/deepstatemap/
```

Utility and import scripts are located in:

```text
scripts/deepstatemap/
```

These include tools for:

* inspecting GeoJSON structure;
* testing source integration;
* importing historical geographic data.

---

## UALosses

The project contains a dedicated integration for processing publicly available records from the UALosses source.

Source integration:

```text
src/services/osint_sources/ualosses/
```

The integration includes:

* HTTP client;
* crawler;
* parser;
* source data models;
* service layer.

The crawler supports large datasets and uses adaptive prefix traversal to retrieve records from source search results.

Database models are separated into:

```text
src/models/db/ualosses/
```

Repository implementations are located in:

```text
src/models/db/ualosses/repositories/
```

Utility scripts are located in:

```text
scripts/ualosses/
```

Available scripts include:

* crawling and saving data;
* crawling source URLs;
* reparsing failed URLs;
* demonstration and diagnostic scripts.

---

# Database

The project uses:

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic
* psycopg

PostgreSQL runs as a Docker Compose service.

Database files are persisted on the host:

```text
data/
└── db/
    └── postgres/
```

This directory is mounted into the PostgreSQL container.

The database configuration is described in:

```text
docs/db/README.md
```

Additional database documentation:

```text
docs/db/
├── README.md
├── backup.md
└── postgis_and_collation.md
```

---

# Database Models

Database configuration is located in:

```text
src/models/db/database.py
```

The main database package exports shared database components.

```python
from src.models.db import Base, SessionLocal
```

Source-specific database models are organized separately.

```text
src/models/db/
├── deepstatemap/
└── ualosses/
```

This allows each source to have its own database models and repository layer while sharing the same database infrastructure.

---

# Repository Layer

Database access is separated from service logic through repositories.

For example:

```text
src/models/db/ualosses/repositories/
```

Repositories encapsulate database operations such as:

* retrieving records;
* searching by source identifiers;
* creating / updating records;
* managing relationships.

Services should use repositories instead of placing database queries directly into source processing logic.

---

# Services

Application logic is organized under:

```text
src/services/
```

Current service areas include:

```text
src/services/
├── analytics/
└── osint_sources/
    ├── deepstatemap/
    └── ualosses/
```

---

## OSINT Sources

Source-specific integrations are grouped under:

```text
src/services/osint_sources/
```

Each source may contain its own:

* client;
* parser;
* crawler;
* data models;
* validation logic;
* service layer.

This structure allows additional sources to be added independently.
The exact structure may vary depending on the source.

---

# Analytics

The project contains a dedicated area for analytical functionality:

```text
src/services/analytics/
```

The purpose of this component is to analyze data collected from multiple sources.

Future analytical functionality may include:

* statistical aggregation;
* time-series analysis;
* geographic analysis;
* comparison of multiple sources;
* correlation analysis;
* data quality analysis;
* chart generation;
* derived datasets.

The analytics layer is intended to operate on normalized data stored in the database rather than directly on raw source responses.

---

# SQL Analysis

SQL queries used for analysis are stored in:

```text
docs/analysis/sql/
```

Current areas include:

```text
docs/analysis/sql/
├── territory/
└── ualosses/
```

Examples of analysis include:

* daily dynamics;
* weekly dynamics;
* monthly dynamics;
* geographic aggregation;
* source-specific queries.

Keeping analytical SQL queries in version control makes them reproducible and easier to review.

---

# Scripts

Executable and utility scripts are organized under:

```text
scripts/
```

The main categories are:

```text
scripts/
├── analytics/
├── db/
├── deepstatemap/
└── ualosses/
```

Scripts are intended for:

* data collection;
* bulk imports;
* reparsing;
* diagnostics;
* source exploration;
* database maintenance;
* analysis.

---

# Database Migrations

Database schema changes are managed with Alembic.

Migration files are stored in:

```text
alembic/versions/
```

## Check database schema

To verify that SQLAlchemy models and the database schema are synchronized:

```bash
docker compose run --rm app alembic check
```

## Create a migration

After modifying database models:

```bash
docker compose run --rm app \
    alembic revision --autogenerate -m "description"
```

## Apply migrations

```bash
docker compose run --rm app alembic upgrade head
```

---

# Installation

## Requirements

The project requires:

* Docker
* Docker Compose
* Make

Python dependencies are installed inside the application container.

---

## Clone the repository

```bash
git clone https://github.com/serguzz/war-analysis.git

cd war-analysis
```

---

## Environment Configuration

Create a local `.env` file based on:

```text
.env.example
```

Example:

```env
POSTGRES_DB=war_analysis
POSTGRES_USER=war
POSTGRES_PASSWORD=your_password
```

The `.env` file is not committed to Git.

---

## Build the Docker image

```bash
docker compose build
```

---

# Running the Project

The application environment is managed with Docker Compose.

## Start the environment

```bash
docker compose up
```

Or run in the background:

```bash
docker compose up -d
```

## Stop the environment

```bash
docker compose down
```

---

# Makefile Commands

The project includes a `Makefile` with common commands.

## Build

```bash
make build
```

## Run the application container

```bash
make run
```

## Open a shell

```bash
make shell
```

## Start services

```bash
make up
```

## Stop services

```bash
make down
```

## Run tests

```bash
make test
```

## Run crawler tests

```bash
make test-crawler
```

## Run database backup

```bash
make db-backup
```

---

# Running Python Scripts

Scripts can be executed directly inside the application container.

Example:

```bash
docker compose run --rm app \
    python scripts/ualosses/ualosses_demo.py
```

Another example:

```bash
docker compose run --rm app \
    python scripts/deepstatemap/demo_deepstatemap.py
```

The exact command depends on the script being executed.

---

# Testing

Tests are located in:

```text
tests/
```

Run all tests:

```bash
docker compose run --rm app \
    python -m pytest -v
```

Or:

```bash
make test
```

Run a specific test file:

```bash
docker compose run --rm app \
    python -m pytest -v \
    tests/services/ualosses/test_crawler.py
```

Run an individual test:

```bash
docker compose run --rm app \
    python -m pytest -v \
    tests/services/ualosses/test_crawler.py::test_next_prefix
```

Additional testing notes are available in:

```text
tests/README.md
```

---

# Database Backup

See backup documentation in:

```text
docs/db/backup.md
```

---

# Development Workflow

A typical development workflow is:

```text
Modify source code
        ↓
Run tests
        ↓
Check imports and application startup
        ↓
Check database models
        ↓
Generate migration if required
        ↓
Apply migration
        ↓
Run source-specific scripts
        ↓
Commit changes
```

For database model changes:

```text
Modify SQLAlchemy models
        ↓
alembic check
        ↓
alembic revision --autogenerate
        ↓
Review migration
        ↓
alembic upgrade head
```

Always review automatically generated migrations before applying them.

---

# Documentation

Additional project documentation is stored in:

```text
docs/
```

Current documentation areas include:

```text
docs/
├── analysis/
│   └── sql/
└── db/
```

---

# Data Storage

The local `data/` directory contains runtime data and database storage.

Typical structure:

```text
data/
└── db/
    └── postgres/
```

Runtime data is excluded from Git where appropriate.

The repository contains application code, configuration, migrations, documentation, and scripts required to reproduce the development environment.

---

# Technology Stack

## Application

* Python

## Database

* PostgreSQL
* PostGIS
* SQLAlchemy
* Alembic
* psycopg

## Data Processing

* Pandas
* PyArrow
* ODF / odfpy

## Visualization

* Matplotlib

## Testing

* pytest

## Infrastructure

* Docker
* Docker Compose
* Make

---

# Project Status

The project is under active development.

Current development focuses on:

* expanding integrations with public data sources;
* improving data normalization;
* developing database models and repository layers;
* processing historical and geographic data;
* improving crawler reliability;
* expanding automated tests;
* developing a unified analytics layer.

The architecture is designed to support additional open data sources and new analytical functionality over time.
