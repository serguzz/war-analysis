# Database Backup

## Create backup

Backups are created with PostgreSQL `pg_dump` in Custom Format (`-Fc`).

Run:

```bash
docker compose up -d
make db-backup
```

The backup is saved to:

```text
data/db/backups/
```

Example:

```text
data/db/backups/war_analysis_2026-09-11_21-09-07.dump
```

The backup script:

```text
scripts/db/backup/backup_all.py
```

uses `pg_dump` inside the `postgres` Docker container.

The backup does not require stopping the crawler or PostgreSQL.

---

## Check backup contents

Use the PostgreSQL 17 tools inside the Docker container:

```bash
docker compose exec -T postgres \
  pg_restore -l < data/db/backups/war_analysis_2026-09-11_21-09-07.dump
```

This checks the dump without restoring it.

The dump should contain:

* all tables;
* table data;
* indexes;
* primary/unique constraints;
* foreign keys;
* PostgreSQL types/enums.

The first backup was successfully checked this way.

Important: use `pg_restore` from the PostgreSQL 17 container. An older `pg_restore` installed on the host may report:

```text
unsupported version (1.16) in file header
```

---

## Full restore test

Create a separate test database:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE war_analysis_restore_test;"'
```

Restore the dump:

```bash
docker compose exec -T postgres \
  sh -c 'pg_restore -U "$POSTGRES_USER" -d war_analysis_restore_test' \
  < data/db/backups/war_analysis_2026-09-11_21-09-07.dump
```

### Verify restored data

Check that all tables exist:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d war_analysis_restore_test -c "\dt"'
```

Check row counts:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d war_analysis_restore_test' <<'SQL'
SELECT 'soldiers' AS table_name, COUNT(*) FROM soldiers
UNION ALL
SELECT 'military_units', COUNT(*) FROM military_units
UNION ALL
SELECT 'locations', COUNT(*) FROM locations
UNION ALL
SELECT 'places', COUNT(*) FROM places
UNION ALL
SELECT 'sources', COUNT(*) FROM sources
UNION ALL
SELECT 'soldier_sources', COUNT(*) FROM soldier_sources;
SQL
```

Check foreign keys:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d war_analysis_restore_test' <<'SQL'
SELECT conname, conrelid::regclass AS table_name,
       confrelid::regclass AS referenced_table
FROM pg_constraint
WHERE contype = 'f'
ORDER BY conrelid::regclass::text, conname;
SQL
```

Check indexes:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d war_analysis_restore_test' <<'SQL'
SELECT tablename, indexname
FROM pg_indexes
ORDER BY tablename, indexname;
SQL
```

The restored database can also be opened in pgAdmin for visual inspection.

The full restore test is the final verification that the backup can actually be used for recovery.



## Cleanup restore test

After the restore test, remove the test database:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS war_analysis_restore_test;"'
```

If PostgreSQL reports that the database is being accessed by other users, terminate those connections first:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '\''war_analysis_restore_test'\'' AND pid <> pg_backend_pid();"'
```

Then remove the database:

```bash
docker compose exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS war_analysis_restore_test;"'
```

The commands above affect only `war_analysis_restore_test` and do not modify the production `war_analysis` database or backup files.
