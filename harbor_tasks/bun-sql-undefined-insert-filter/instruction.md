# SQL INSERT helper converts undefined values to NULL instead of omitting them

## Problem

The `sql()` template tag helper in Bun's SQL module treats `undefined` values as `NULL` in INSERT statements. This causes two distinct failures:

1. **NOT NULL constraint violations**: When a column has a `DEFAULT` value and the caller passes `undefined` for it (meaning "use the default"), the helper inserts `NULL` instead of omitting the column. This causes `NOT NULL` constraint failures even when the column has a valid `DEFAULT`.

   Example: `sql({ foo: undefined, id: "123" })` in an INSERT generates `(foo, id) VALUES (NULL, "123")` instead of `(id) VALUES ("123")`.

2. **Silent data loss in bulk inserts**: When inserting multiple items, the column list is determined only from the first item. If the first item has `undefined` for a column but a later item has a real value for it, that value is silently dropped.

   Example: Inserting `[{ a: 1, b: undefined }, { a: 2, b: "important" }]` — the value `"important"` is lost because column `b` was excluded based on the first item.

## Expected Behavior

- **`undefined` values in single-object INSERTs**: The column should be omitted entirely, letting the database use its DEFAULT value.
- **Bulk inserts (array of items)**: ALL items should be checked when determining which columns to include. A column should be included if ANY item has a defined value for it.
- **Per-row values in bulk inserts**: Items that have `undefined` for a column that other items defined should use `null` for that column's value in the VALUES clause.

## Implementation Requirements

The solution must add a shared column-filtering helper to `src/js/internal/sql/shared.ts`. This helper should:
- Accept the column list, the items being inserted, and an escape function
- Inspect ALL items when determining which columns have defined values (for bulk inserts)
- Return an object with two properties: an array of column names that have at least one defined value, and a SQL fragment for the column list
- Generate SQL column list as a parenthesized, comma-separated list ending with ` VALUES`

All three SQL adapters must be updated to use this shared helper:
- `src/js/internal/sql/sqlite.ts`
- `src/js/internal/sql/mysql.ts`
- `src/js/internal/sql/postgres.ts`

Each adapter must:
- Import the shared function using a `require()` call to `"internal/sql/shared"`
- Call the helper with the column list, items, and the adapter's identifier escape function
- Use the returned column list and SQL fragment in the generated INSERT statement
- Throw a `SyntaxError` when no columns have defined values (empty insert is not valid)

## Documentation Requirement

The file `test/CLAUDE.md` must include guidance recommending `.toEqual` for asserting on nested or complex object equality. The documentation must:
- Mention `.toEqual` for comparing nested or complex objects
- Include the word "Nested" (capital N) or phrase "complex object" or "object equality"
- Show a usage example containing the text `toEqual(`

## Verification Criteria

The implementation must pass all of the following checks:

1. **Behavioral correctness** (6 test cases executed against the actual implementation):
   - Single item with all defined values → all columns included
   - Single item with one undefined → that column filtered out
   - Bulk insert where first item has undefined but second has a value → column included (data loss fix)
   - Bulk insert where ALL items have undefined for a column → column excluded
   - SQL format: column list wrapped in parentheses and ends with ` VALUES`
   - Bulk insert where middle item has the only defined value → column included

2. **All three adapters updated**: SQLite, MySQL, and PostgreSQL adapters all import and use the shared filtering logic via the exact import pattern `require("internal/sql/shared")` and destructured names `definedColumns` and `columnsSql`.

3. **Documentation update**: `test/CLAUDE.md` must include guidance recommending `.toEqual` for asserting on nested or complex object equality, with an example showing `toEqual(` usage.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
