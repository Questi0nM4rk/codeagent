---
name: postgresql
description: PostgreSQL database expertise. Activates when working with .sql files, database migrations, or discussing SQL queries, indexes, and database design.
---

# PostgreSQL Development Skill

Domain knowledge for PostgreSQL database development and administration.

## Stack

- **Version**: PostgreSQL 15+
- **Client**: psql, pgcli
- **Migration**: Flyway, Liquibase, or framework-specific
- **Monitoring**: pg_stat_statements, EXPLAIN ANALYZE

## Commands

### Connection

```bash
# Connect
psql -h localhost -U username -d database
psql "postgresql://user:pass@host:5432/dbname"

# Execute file
psql -f script.sql -d database
psql -c "SELECT * FROM users" -d database

# Dump and restore
pg_dump -Fc database > backup.dump
pg_restore -d database backup.dump
pg_dump --schema-only database > schema.sql
```

### psql Commands

```sql
-- List databases
\l

-- Connect to database
\c database_name

-- List tables
\dt
\dt+  -- with sizes

-- Describe table
\d table_name
\d+ table_name  -- with details

-- List indexes
\di

-- List functions
\df

-- Show query execution plan
\timing on
EXPLAIN ANALYZE SELECT ...;

-- Edit in $EDITOR
\e

-- Output to file
\o output.txt
SELECT ...;
\o
```

## Patterns

### Table Design

```sql
-- Use UUIDs for distributed-friendly IDs
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### Indexes

```sql
-- B-tree (default, for equality and range)
CREATE INDEX idx_users_email ON users(email);

-- Partial index
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- GIN for array/jsonb containment
CREATE INDEX idx_tags ON posts USING gin(tags);

-- GiST for geometric/full-text
CREATE INDEX idx_location ON places USING gist(location);

-- BRIN for naturally ordered data (timestamps)
CREATE INDEX idx_logs_created ON logs USING brin(created_at);
```

### Queries

```sql
-- CTEs for readability
WITH active_users AS (
    SELECT id, email
    FROM users
    WHERE last_login > now() - INTERVAL '30 days'
),
user_orders AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE created_at > now() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT u.email, COALESCE(o.order_count, 0) as orders
FROM active_users u
LEFT JOIN user_orders o ON u.id = o.user_id;

-- Window functions
SELECT
    email,
    order_total,
    SUM(order_total) OVER (PARTITION BY user_id ORDER BY created_at) as running_total,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as order_rank
FROM orders;

-- UPSERT
INSERT INTO users (email, name)
VALUES ('user@example.com', 'John')
ON CONFLICT (email) DO UPDATE
SET name = EXCLUDED.name, updated_at = now();
```

### JSON Operations

```sql
-- Store JSON
CREATE TABLE events (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL
);

-- Query JSON
SELECT data->>'name' as name
FROM events
WHERE data @> '{"type": "click"}';

-- Index JSON field
CREATE INDEX idx_events_type ON events ((data->>'type'));

-- JSON aggregation
SELECT jsonb_agg(jsonb_build_object(
    'id', id,
    'name', name
)) as users
FROM users;
```

### Migrations

```sql
-- Idempotent migrations
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT now()
);

-- Safe column add
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone TEXT;

-- Safe index (concurrent, no lock)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_phone ON users(phone);

-- Safe column rename (avoid in prod)
-- Instead: add new, migrate data, remove old
```

### Performance

```sql
-- Analyze query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email = 'test@example.com';

-- Table statistics
ANALYZE users;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find slow queries (requires pg_stat_statements)
SELECT
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Review Tools

```bash
# Syntax check (via psql)
psql -f script.sql --set ON_ERROR_STOP=on -1

# pgFormatter
pg_format script.sql

# SQLFluff (Python)
sqlfluff lint script.sql --dialect postgres
sqlfluff fix script.sql --dialect postgres
```

## Testing Patterns

### pgTAP

```sql
BEGIN;
SELECT plan(3);

SELECT has_table('users');
SELECT has_column('users', 'email');
SELECT col_is_unique('users', 'email');

SELECT * FROM finish();
ROLLBACK;
```

### Transaction Testing

```sql
-- Test in transaction, rollback at end
BEGIN;

INSERT INTO users (email) VALUES ('test@example.com');
SELECT * FROM users WHERE email = 'test@example.com';

-- Verify constraints
DO $$
BEGIN
    INSERT INTO users (email) VALUES ('test@example.com');
    RAISE EXCEPTION 'Should have failed unique constraint';
EXCEPTION
    WHEN unique_violation THEN
        -- Expected
END $$;

ROLLBACK;
```

## Common Conventions

- Use `TIMESTAMPTZ` not `TIMESTAMP`
- Use `TEXT` not `VARCHAR` (no performance difference)
- Use `UUID` for IDs in distributed systems
- Always add `NOT NULL` unless nullable is intentional
- Name constraints explicitly
- Use lowercase, snake_case for identifiers
- Create indexes for foreign keys
- Use `CONCURRENTLY` for production index creation
