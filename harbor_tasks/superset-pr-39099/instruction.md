# Migration Utility: Foreign Key Creation Fails on Re-run

## Problem

The database migration utility in `superset/migrations/shared/utils.py` has an issue with the `create_fks_for_table()` function. When a migration is re-run (e.g., after a partial failure and restart), the function attempts to create foreign key constraints that may already exist in the database, causing the migration to fail with a constraint violation error.

The `drop_fks_for_table()` function already handles this gracefully by checking for existing constraints before attempting to drop them. However, `create_fks_for_table()` lacks equivalent protection.

## Symptoms

- Migrations fail when re-run after a partial completion
- Error messages indicate duplicate foreign key constraint names
- Database administrators have to manually clean up partial migration state
- Idempotent migration runs are not possible

## Expected Behavior

The `create_fks_for_table()` function should:
1. Check if the foreign key constraint already exists before attempting to create it
2. Skip creation gracefully (with a log message) if the constraint is already present
3. Only attempt to create constraints that don't already exist

## Implementation Requirements

To enable idempotent FK creation, you must implement a helper function called `get_foreign_key_names(table_name: str) -> set[str]` that:
- Returns a set of foreign key constraint names currently defined on the given table
- Uses the SQLAlchemy inspector API to query existing constraints

The `create_fks_for_table()` function must call this helper before creating any foreign key, and skip creation if the constraint already exists.

The `drop_fks_for_table()` function should also be refactored to use this same helper for consistency.

## Files to Examine

- `superset/migrations/shared/utils.py` - Contains the migration utility functions
