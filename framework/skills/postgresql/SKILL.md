---
name: postgresql
description: PostgreSQL database expertise. Activates when working with .sql files, database migrations, or discussing SQL queries, indexes, and database design.
---

# PostgreSQL Development Skill

Domain knowledge for PostgreSQL database development and administration.

## The Iron Law

```
EXPLAIN ANALYZE BEFORE DEPLOY + INDEXES ON FOREIGN KEYS + TIMESTAMPTZ NOT TIMESTAMP
Every query is analyzed. Every FK has an index. Time zones are explicit.
```

## Core Principle

> "The database outlives your code. Design schemas for decades, not sprints."

## When to Use

**Always:**
- Writing SQL queries or migrations
- Designing database schemas
- Optimizing query performance
- Creating stored procedures/functions

**Exceptions (ask human partner):**
- Embedded/SQLite scenarios
- NoSQL-first architectures

## Stack

| Component | Technology |
|-----------|------------|
| Version | PostgreSQL 15+ |
| Client | psql, pgcli |
| Migration | Flyway, Liquibase, EF Core |
| Monitoring | pg_stat_statements, EXPLAIN |
| Formatting | pg_format, SQLFluff |

## Essential Commands

```bash
# Connect
psql -h localhost -U username -d database
psql "postgresql://user:pass@host:5432/dbname"

# Execute
psql -f script.sql -d database
psql -c "SELECT * FROM users" -d database

# Dump/restore
pg_dump -Fc database > backup.dump
pg_restore -d database backup.dump
```

## Patterns

### Table Design

<Good>
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_format CHECK (email ~* '^[^@]+@[^@]+$')
);

-- Auto-update timestamp trigger
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
- UUID for distributed-friendly IDs
- TIMESTAMPTZ preserves timezone
- Named constraints for clear errors
- Automatic audit timestamps
</Good>

<Bad>
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    created TIMESTAMP
);
```
- SERIAL instead of UUID (not distributed-friendly)
- VARCHAR without benefit over TEXT
- TIMESTAMP loses timezone info
- No NOT NULL constraints
- No named constraints
</Bad>

### Indexes

<Good>
```sql
-- B-tree for equality/range
CREATE INDEX idx_users_email ON users(email);

-- Partial index (smaller, faster)
CREATE INDEX idx_active_users ON users(email)
WHERE deleted_at IS NULL;

-- Composite (order matters for queries!)
CREATE INDEX idx_orders_user_date
ON orders(user_id, created_at DESC);

-- GIN for JSONB containment
CREATE INDEX idx_events_data ON events USING gin(data);

-- BRIN for naturally ordered data (logs, time-series)
CREATE INDEX idx_logs_created ON logs USING brin(created_at);

-- CONCURRENTLY for production (no lock)
CREATE INDEX CONCURRENTLY idx_users_phone ON users(phone);
```
- Right index type for query pattern
- Partial indexes for filtered queries
- CONCURRENTLY for zero-downtime
</Good>

### Queries

<Good>
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
    SUM(order_total) OVER (
        PARTITION BY user_id
        ORDER BY created_at
    ) as running_total
FROM orders;

-- UPSERT (INSERT ... ON CONFLICT)
INSERT INTO users (email, name)
VALUES ('user@example.com', 'John')
ON CONFLICT (email) DO UPDATE
SET name = EXCLUDED.name, updated_at = now();
```
- CTEs over nested subqueries
- COALESCE for null handling
- Window functions for analytics
</Good>

### Migrations

<Good>
```sql
-- Idempotent (safe to re-run)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT now()
);

-- Safe column add
ALTER TABLE users
ADD COLUMN IF NOT EXISTS phone TEXT;

-- Safe index (no lock, idempotent)
CREATE INDEX CONCURRENTLY IF NOT EXISTS
idx_users_phone ON users(phone);

-- Safe column rename: add new, migrate, drop old
ALTER TABLE users ADD COLUMN full_name TEXT;
UPDATE users SET full_name = name;
ALTER TABLE users DROP COLUMN name;
```
- IF NOT EXISTS for idempotency
- CONCURRENTLY for zero downtime
- Additive changes only
</Good>

### Performance Analysis

```sql
-- Always analyze before deploying
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM users WHERE email = 'test@example.com';

-- Update statistics
ANALYZE users;

-- Check index usage
SELECT
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find slow queries (requires pg_stat_statements)
SELECT
    LEFT(query, 60) as query,
    calls,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    ROUND(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Testing Patterns

### pgTAP

<Good>
```sql
BEGIN;
SELECT plan(4);

SELECT has_table('users');
SELECT has_column('users', 'email');
SELECT col_is_unique('users', 'email');
SELECT col_not_null('users', 'email');

SELECT * FROM finish();
ROLLBACK;
```
- Tests in transaction
- Rollback preserves state
- Clear structural assertions
</Good>

### Transaction Testing

```sql
BEGIN;

INSERT INTO users (email) VALUES ('test@example.com');
SELECT * FROM users WHERE email = 'test@example.com';

-- Verify constraint
DO $$
BEGIN
    INSERT INTO users (email) VALUES ('test@example.com');
    RAISE EXCEPTION 'Should have failed unique constraint';
EXCEPTION
    WHEN unique_violation THEN NULL; -- Expected
END $$;

ROLLBACK;
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "We'll add indexes later" | You'll forget. Add them with the FK now. |
| "TIMESTAMP is fine" | Until DST breaks your app. Use TIMESTAMPTZ. |
| "EXPLAIN is slow" | Running bad queries in prod is slower. Analyze first. |
| "VARCHAR(255) is standard" | TEXT performs identically. Use TEXT. |

## Red Flags - STOP

- `TIMESTAMP` instead of `TIMESTAMPTZ`
- Foreign key without index on referencing column
- `SELECT *` in application code
- No `EXPLAIN ANALYZE` on new queries
- `VARCHAR(n)` without specific length requirement
- Missing `NOT NULL` on required columns
- `CREATE INDEX` without `CONCURRENTLY` in production
- No named constraints

If you see these, stop and fix before continuing.

## Verification Checklist

- [ ] `EXPLAIN ANALYZE` shows index usage (no seq scans on large tables)
- [ ] All FKs have indexes on referencing columns
- [ ] All timestamps use `TIMESTAMPTZ`
- [ ] Migrations are idempotent (IF NOT EXISTS)
- [ ] Production indexes use `CONCURRENTLY`
- [ ] Constraints are explicitly named
- [ ] pgTAP tests pass

## Review Tools

```bash
# Syntax check
psql -f script.sql --set ON_ERROR_STOP=on -1

# Format
pg_format script.sql

# Lint (Python-based)
sqlfluff lint script.sql --dialect postgres
sqlfluff fix script.sql --dialect postgres
```

## When Stuck

| Problem | Solution |
|---------|----------|
| Seq scan on indexed column | Check column type matches, run ANALYZE, verify WHERE clause |
| Lock timeout on ALTER | Use `LOCK_TIMEOUT`, add `CONCURRENTLY` |
| Slow JOIN | Ensure FK columns indexed, check EXPLAIN for nested loops |
| Migration rollback needed | Write DOWN migration, test in staging first |

## Related Skills

- `dotnet` - EF Core migrations and data access
- `tdd` - Test-first with pgTAP
- `reviewer` - Uses EXPLAIN for validation
