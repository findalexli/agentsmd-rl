# Bun SQL: Filter Out Undefined Values in INSERT Helper

## Problem

When using the `sql()` helper function for INSERT statements, `undefined` values are being converted to `NULL` instead of being filtered out. This causes two problems:

1. **NOT NULL columns with DEFAULT values fail**: When a column is defined as `NOT NULL` with a `DEFAULT` value, passing `undefined` causes a constraint violation because it's converted to `NULL` instead of letting the database use the default.

   ```typescript
   // Before (broken):
   sql`INSERT INTO table ${sql({ foo: undefined, id: "123" })}`
   // Generates: INSERT INTO table (foo, id) VALUES (NULL, "123")
   // Causes: NOT NULL constraint violation even though foo has a DEFAULT!
   ```

2. **Data loss in bulk inserts**: When inserting multiple items where some have different columns defined (e.g., first item has `optional: undefined`, second has `optional: "value"`), the values in later items are silently dropped because columns were determined only from the first item.

   ```typescript
   // Before (broken):
   sql`INSERT INTO table ${sql([
     { id: 1, optional: undefined },
     { id: 2, optional: "value" }  // This value is LOST!
   ])}`
   // Only inserts: (id) VALUES (1), (2) - optional column entirely omitted!
   ```

## Expected Behavior

1. `undefined` values should be **filtered out entirely** from INSERT statements, allowing the database to use DEFAULT values.
2. For bulk inserts, all items should be scanned to determine which columns have at least one defined value, ensuring no data loss.

   ```typescript
   // After (fixed):
   sql`INSERT INTO table ${sql({ foo: undefined, id: "123" })}`
   // Generates: INSERT INTO table (id) VALUES ("123")
   // foo is omitted - database uses its DEFAULT value

   sql`INSERT INTO table ${sql([
     { id: 1, optional: undefined },
     { id: 2, optional: "value" }
   ])}`
   // Generates: INSERT INTO table (id, optional) VALUES (1, NULL), (2, "value")
   // Both values preserved! First item's undefined becomes NULL, second keeps its value.
   ```

## Files to Look At

- `src/js/internal/sql/shared.ts` - Contains the `buildDefinedColumnsAndQuery` helper function that needs to be added
- `src/js/internal/sql/mysql.ts` - MySQL adapter INSERT logic (needs to use the new helper)
- `src/js/internal/sql/postgres.ts` - Postgres adapter INSERT logic (needs to use the new helper)
- `src/js/internal/sql/sqlite.ts` - SQLite adapter INSERT logic (needs to use the new helper)
- `test/js/sql/sqlite-sql.test.ts` - Existing SQLite SQL tests (add regression tests here)
- `test/CLAUDE.md` - Testing conventions (add nested object equality guidance)

## Implementation Notes

1. Add a new helper function `buildDefinedColumnsAndQuery` in `shared.ts` that:
   - Takes columns array, items (single or array), and escape identifier function
   - Scans all items to find which columns have at least one defined (non-undefined) value
   - Returns the filtered columns and SQL fragment

2. Update all three adapters (MySQL, Postgres, SQLite) to use this helper instead of their current logic.

3. If all columns are undefined for a single item insert, throw a `SyntaxError` with message: "Insert needs to have at least one column with a defined value"

4. When an item has `undefined` for a column that other items defined, use `null` (not omit entirely).

## Regression Tests to Add

Add tests to `test/js/sql/sqlite-sql.test.ts` that verify:
1. Single insert with `undefined` on NOT NULL column with DEFAULT uses default value
2. Bulk insert where first item has `undefined` but later items have values - data must be preserved
3. Bulk insert with middle items having values - all values must be preserved
4. All-undefined columns should throw appropriate error

See issue #25829 for the original bug report.
