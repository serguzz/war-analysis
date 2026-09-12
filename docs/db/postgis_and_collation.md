# PostGIS Image Pinning & Collation Version Fix

## Background

The project's `postgres` service was switched from the plain `postgres:17` image
to `postgis/postgis:17-3.5` in order to add PostGIS spatial support.

This image is built on Debian 11 (bullseye), which ships **glibc 2.31**. The
database, however, had originally been created under a container whose glibc
reported collation version **2.41**. Postgres tracks the glibc collation
version it was created with and refuses to silently trust a different one,
because the sort order of text can change between glibc versions — which can
silently corrupt any existing indexes on text columns (a binary search over a
now-differently-sorted index can miss rows).

This surfaced as a warning on every connection:

```
WARNING:  database "war_analysis" has a collation version mismatch
DETAIL:  The database was created using collation version 2.41, but the
operating system provides version 2.31.
```

At the time, the database had **6 tables and several hundred thousand rows**,
but no spatial (geometry/geography) tables or indexes had been created yet —
so no PostGIS-specific reindexing was needed, only a standard one.

## 1. Pinning the PostGIS image by digest

Floating tags like `postgis/postgis:17-3.5` can be rebuilt over time and may
change base OS / glibc version without warning (this is what caused the
mismatch above). To prevent this from happening again, the image was pinned
to its exact digest (a SHA-256 hash uniquely identifying that specific build).

```bash
# Pull the tag once to have it locally
docker compose pull postgres

# Get its digest
docker inspect --format='{{index .RepoDigests 0}}' postgis/postgis:17-3.5
# -> postgis/postgis@sha256:01a6a70e41e6c4467c8f55f6063555ed72db2d6662cd0d571040d42eadaeb6f6
```

`docker-compose.yml` was updated from:

```yaml
image: postgis/postgis:17-3.5
```

to:

```yaml
image: postgis/postgis@sha256:01a6a70e41e6c4467c8f55f6063555ed72db2d6662cd0d571040d42eadaeb6f6
```

This guarantees the exact same image build is always used, regardless of
future tag rebuilds. Upgrading now requires deliberately picking a new
digest rather than an implicit `docker compose pull`.

Rebuilt and confirmed with:

```bash
docker compose up -d postgres
docker compose images postgres
```

## 2. Fixing the collation version mismatch

Steps taken, in order:

**a. Backup**

```bash
docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d war_analysis \
  > war_analysis_backup.sql
```

**b. Reindex the whole database**

Rebuilds all existing indexes so they match the sort order that glibc 2.31
actually uses.

```bash
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
REINDEX DATABASE war_analysis;
SQL
```

Took only a few seconds given the current row counts. Output ended with
`REINDEX`, confirming success (the repeated collation warnings before it are
expected — one per internal reconnect Postgres makes during the operation).

**c. Refresh the recorded collation version**

```bash
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
ALTER DATABASE war_analysis REFRESH COLLATION VERSION;
SQL
```

Output: `NOTICE:  changing version from 2.41 to 2.31` / `ALTER DATABASE`.

**d. Verify**

```bash
docker compose exec -T postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' <<'SQL'
SELECT datcollversion FROM pg_database WHERE datname = current_database();
SQL
```

Result: `2.31`, with no warning — mismatch resolved.

## 3. Result

- Image pinned by digest, so this collation drift cannot silently happen
  again from a `docker compose pull`.
- Existing 6 tables' indexes rebuilt and consistent with the running glibc
  version.
- Clear to proceed with creating geometry/spatial tables and indexes, which
  will be built correctly under glibc 2.31 from the start.