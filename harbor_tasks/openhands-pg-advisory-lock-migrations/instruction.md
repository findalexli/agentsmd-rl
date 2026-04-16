# Task: Fix Concurrent Database Migration Race Condition

## Symptom

When multiple pods of the application start simultaneously (common in Kubernetes deployments), each pod runs `alembic upgrade head` to apply database migrations. This causes a race condition where:

1. All pods attempt to run migrations concurrently
2. Only one pod succeeds
3. Other pods fail with noisy errors (ROLLBACKs, duplicate table creation attempts, SQLAlchemy engine errors)
4. Failed pods create confusion during deployments and may restart unnecessarily

The errors look like PostgreSQL conflicts — duplicate key violations, table already exists, or lock acquisition failures.

## Expected Behavior

When multiple pods start simultaneously:
- The first pod acquires a database lock and runs migrations
- Other pods wait for the lock
- When the first pod releases the lock (upon connection close), other pods proceed
- Subsequent pods find no migrations to run and exit cleanly

## Database Lock Requirements

PostgreSQL advisory locks can serialize migration runs across pods. The migration code in `enterprise/migrations/env.py` uses a database connection in the `run_migrations_online()` function.

A valid fix will:
- Use a PostgreSQL advisory lock with lock ID `3617572382373537863` (derived from the MD5 hash of 'openhands_enterprise_migrations')
- Execute the lock call before migrations run (before `context.run_migrations()`)
- Use SQLAlchemy's `text()` wrapper for raw SQL execution
- Include comments explaining the lock number origin and release behavior
- Appear in `run_migrations_online()`, not `run_migrations_offline()`

The exact implementation approach (where to place the lock call, how to invoke it, which import to add) should be determined by consulting the existing code patterns in the file and the SQLAlchemy documentation for raw SQL execution.

## Code Quality Requirements

- The file must pass lint checks with the repository's ruff configuration
- Python syntax must be valid

## Relevant File

- `enterprise/migrations/env.py` — Contains the migration configuration and `run_migrations_online()` function