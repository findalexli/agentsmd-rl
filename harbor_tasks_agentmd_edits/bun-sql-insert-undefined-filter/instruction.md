# sql() INSERT helper treats undefined values as NULL instead of filtering them

## Problem

When using the `sql()` tagged template helper for INSERT statements in Bun's built-in SQL module, passing `undefined` as a column value causes it to be treated as `NULL`. This breaks INSERTs into columns with `DEFAULT` values — a column like `foo TEXT NOT NULL DEFAULT 'bar'` gets `NULL` instead of its default when you pass `{ foo: undefined }`, triggering a NOT NULL constraint violation.

Additionally, in bulk inserts, the column set is determined only from the first item. If a later item has a defined value for a column that the first item has as `undefined`, that value is silently dropped (data loss).

## Expected Behavior

- `undefined` values should be **filtered out** of INSERT statements entirely, allowing database `DEFAULT` values to be used.
- Bulk inserts should check **all** items when determining which columns to include, preventing data loss.

## Files to Look At

- `src/js/internal/sql/shared.ts` — shared SQL helper utilities, where column filtering logic should live
- `src/js/internal/sql/sqlite.ts` — SQLite adapter INSERT handling
- `src/js/internal/sql/mysql.ts` — MySQL adapter INSERT handling
- `src/js/internal/sql/postgres.ts` — PostgreSQL adapter INSERT handling
- `test/CLAUDE.md` — testing guidelines that should be updated to reflect best practices for complex object assertions
