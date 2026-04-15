# SQL INSERT helper converts undefined values to NULL instead of omitting them

## Problem

The `sql()` template tag helper in Bun's SQL module treats `undefined` values as `NULL` in INSERT statements. This causes two issues:

1. **NOT NULL constraint violations**: When a column has a `DEFAULT` value and the user passes `undefined` for it (meaning "use the default"), the helper inserts `NULL` instead of omitting the column. This causes `NOT NULL` constraint failures even when the column has a valid `DEFAULT`.

   Example: `sql({ foo: undefined, id: "123" })` in an INSERT generates `(foo, id) VALUES (NULL, "123")` instead of `(id) VALUES ("123")`.

2. **Silent data loss in bulk inserts**: When inserting multiple items, the column list is determined only from the first item. If the first item has `undefined` for a column but a later item has a real value for it, that value is silently dropped.

   Example: Inserting `[{ a: 1, b: undefined }, { a: 2, b: "important" }]` — the value `"important"` is lost because column `b` was excluded based on the first item.

## Expected Behavior

- `undefined` values in single-object INSERTs should cause the column to be omitted entirely, letting the database use its DEFAULT value.
- In bulk inserts, ALL items should be checked when determining which columns to include. A column should be included if ANY item has a defined value for it.
- Items that have `undefined` for a column that other items defined should use `null` for that column's value in the VALUES clause.
- If ALL values for ALL columns are `undefined`, throw a `SyntaxError` with message `"Insert needs to have at least one column with a defined value"`.

## Implementation Requirements

Create a shared function in `src/js/internal/sql/shared.ts` named `buildDefinedColumnsAndQuery` with the following signature:

```typescript
function buildDefinedColumnsAndQuery<T>(
  columns: (keyof T)[],
  items: T | T[],
  escapeIdentifier: (name: string) => string,
): { definedColumns: (keyof T)[]; columnsSql: string }
```

The function must:
1. Return `definedColumns`: an array of column keys that have at least one defined (non-undefined) value across all items
2. Return `columnsSql`: a SQL fragment string formatted as `("col1", "col2") VALUES` with column names escaped via `escapeIdentifier`
3. For single items: include a column only if that item has a defined value for it
4. For bulk inserts (array of items): include a column if ANY item has a defined value for it

All three adapters must import and use this function:
- `src/js/internal/sql/sqlite.ts` — must import `buildDefinedColumnsAndQuery` from `internal/sql/shared` and use `definedColumns` from its return value
- `src/js/internal/sql/mysql.ts` — must import `buildDefinedColumnsAndQuery` from `internal/sql/shared` and use `definedColumns` from its return value
- `src/js/internal/sql/postgres.ts` — must import `buildDefinedColumnsAndQuery` from `internal/sql/shared` and use `definedColumns` from its return value

## Documentation Update

After fixing the code, update `test/CLAUDE.md` to add guidance about preferring `.toEqual` for asserting on nested/complex objects instead of many individual `.toBe` calls. The guidance must include:
- Mentions of "Nested" or "complex object" when discussing equality assertions
- A `.toEqual(` usage example demonstrating the pattern
