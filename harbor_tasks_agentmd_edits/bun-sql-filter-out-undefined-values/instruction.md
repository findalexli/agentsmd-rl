# sql() INSERT helper converts undefined to NULL instead of omitting the column

## Problem

When using the `sql()` helper to INSERT data with `undefined` values, the helper converts `undefined` to `NULL`. This causes `NOT NULL` constraint violations on columns that have `DEFAULT` values — the database never gets a chance to use the default because the column is explicitly set to `NULL`.

For example:
```ts
await sql`INSERT INTO users ${sql({ foo: undefined, id: "123" })}`;
// Generates: INSERT INTO users (foo, id) VALUES (NULL, "123")
// Fails if foo is NOT NULL DEFAULT 'some-default'
```

Additionally, in **bulk inserts**, columns are only determined from the first item. If a later item has a value for a column the first item doesn't, that value is silently dropped — a data loss bug.

```ts
await sql`INSERT INTO t ${sql([
  { id: 1, name: "a", optional: undefined },
  { id: 2, name: "b", optional: "important-value" },  // <-- "important-value" is LOST
])}`;
```

## Expected Behavior

1. `undefined` values should be **filtered out** of the INSERT column list entirely, allowing the database to apply `DEFAULT` values for those columns.
2. In bulk inserts, columns should be determined by checking **all items**, not just the first. If any item has a defined value for a column, that column must be included.
3. If all column values are `undefined`, the helper should throw a clear error.

The logic for building the column list from defined values should be shared across all SQL adapters (SQLite, MySQL, PostgreSQL) to avoid duplication.

## Files to Look At

- `src/js/internal/sql/shared.ts` — shared SQL utilities used by all adapters
- `src/js/internal/sql/sqlite.ts` — SQLite adapter, INSERT handling in the template literal processor
- `src/js/internal/sql/mysql.ts` — MySQL adapter, same INSERT handling
- `src/js/internal/sql/postgres.ts` — PostgreSQL adapter, same INSERT handling

After fixing the code, update `test/CLAUDE.md` to add guidance about testing patterns for nested/complex object equality — the project's testing guidelines should recommend using `.toEqual` rather than many individual `.toBe` assertions when comparing arrays of objects or nested structures.
