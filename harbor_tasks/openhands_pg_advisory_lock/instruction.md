# Add PostgreSQL Advisory Lock for Concurrent Migrations

## Problem

When multiple application pods start simultaneously, they all attempt to run database migrations concurrently. This causes:
- ROLLBACKs in logs
- Duplicate `CREATE TABLE alembic_version` attempts
- Noisy SQLAlchemy engine errors
- Confusion during deployments

The migrations in `enterprise/migrations/env.py` need to use PostgreSQL advisory locks to ensure only one pod runs migrations at a time.

## Task

Modify `enterprise/migrations/env.py` to acquire a PostgreSQL advisory lock before running migrations.

## Key Requirements

1. **Import `text` from SQLAlchemy** - You'll need `from sqlalchemy import create_engine, text` to execute raw SQL.

2. **Acquire the lock in `run_migrations_online()`** - Use `pg_advisory_lock(3617572382373537863)` - this is the md5 hash of 'openhands_enterprise_migrations'.

3. **Lock before transaction** - The lock must be acquired BEFORE `context.begin_transaction()` is called.

4. **Use connection.execute(text(...))** - Execute the lock query through the connection object.

## Implementation Notes

- The lock is automatically released when the connection context manager exits
- The lock ID 3617572382373537863 is derived from: `SELECT ('x' || md5('openhands_enterprise_migrations'))::bit(64)::bigint;`
- Other pods waiting on the lock will block until the first pod completes, then proceed (finding nothing to migrate)

## Verification

Your fix should ensure:
- The `text` function is imported from sqlalchemy
- The advisory lock call is present in `run_migrations_online()`
- The lock is acquired before `begin_transaction()`
- The file remains valid Python
