# Fix Migration Foreign Key Utilities

There's an inconsistency in how migration utilities handle pre-existing foreign keys.

## The Problem

The `create_fks_for_table` function in `superset/migrations/shared/utils.py` doesn't gracefully handle cases where a foreign key already exists on a table. This causes migration failures when re-running migrations or when tables have been modified outside the standard migration flow.

While `drop_fks_for_table` already handles pre-existing foreign keys gracefully, `create_fks_for_table` lacks this safety check and will fail if the foreign key constraint already exists.

## What You Need To Do

1. Look at the migration utilities in `superset/migrations/shared/utils.py`

2. Create a helper function `get_foreign_key_names(table_name)` that retrieves all foreign key constraint names for a given table. This should return a `set[str]` of constraint names.

3. Update `create_fks_for_table` to check if a foreign key already exists before attempting to create it. If the FK exists, the function should log an informative message and return early (similar to how existing "already exists" checks work in other migration utilities).

4. Refactor `drop_fks_for_table` to use your new helper function for consistency, removing any duplicated inline logic.

## Requirements

- Follow the project's existing patterns for:
  - Type hints (all functions must have proper type annotations)
  - Docstrings (follow Google-style or existing patterns in the file)
  - Logging (use the existing logger with appropriate formatting)
  - Code style and conventions

- The solution should be idempotent - running the same migration multiple times should not fail

- Ensure proper error handling for edge cases (e.g., missing tables, database dialect differences)

## Testing Your Solution

Your fix should allow `create_fks_for_table` to be called multiple times without error, and should properly skip creation when the foreign key already exists.
