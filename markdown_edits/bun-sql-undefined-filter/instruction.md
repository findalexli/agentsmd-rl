# Fix sql() INSERT helper undefined handling and update test documentation

## Problem

The `sql()` helper function in Bun's SQL library has two related bugs when handling `undefined` values in INSERT statements:

1. **Default value overriding**: When inserting with `sql({ foo: undefined, id: "123" })`, the helper was converting `undefined` to `NULL`, causing NOT NULL constraint violations even when the column has a DEFAULT value. The column should be omitted from the INSERT entirely, allowing the database to use its DEFAULT.

2. **Bulk insert data loss**: In bulk inserts like `sql([{ a: 1 }, { a: 2, b: 3 }])`, columns were determined only from the first item. This meant values in later items (like `b: 3`) were silently dropped if not present in the first item.

## What you need to do

### 1. Fix the SQL helper implementation

Modify the SQL adapter files in `src/js/internal/sql/` to:

- Add a `buildDefinedColumnsAndQuery` function in `shared.ts` that:
  - Takes columns, items, and an escapeIdentifier function
  - Returns only the columns that have at least one defined value across all items
  - Handles both single items and arrays uniformly
  - Builds the SQL fragment for column names

- Update `sqlite.ts`, `postgres.ts`, and `mysql.ts` to:
  - Import and use `buildDefinedColumnsAndQuery`
  - Only include columns with defined values in INSERT statements
  - Use `null` for items that have `undefined` for a column that other items defined
  - Throw a `SyntaxError` with message "Insert needs to have at least one column with a defined value" if all columns are undefined

### 2. Update test documentation

Update `test/CLAUDE.md` to add a new section on nested/complex object equality testing:

- Add a section titled "Nested/complex object equality" that documents:
  - Prefer using `.toEqual` rather than many `.toBe` assertions for nested or complex objects
  - Show a BAD example using multiple `.toBe` assertions on individual properties
  - Show a GOOD example using a single `.toEqual` with the expected object/array structure
  - Include the comment "CRITICAL: middle item's value must be preserved" in the example

- Fix the existing `Promise.withResolvers()` example to include a type annotation: `Promise.withResolvers<void>()`

## Files to modify

- `src/js/internal/sql/shared.ts` - add `buildDefinedColumnsAndQuery` function
- `src/js/internal/sql/sqlite.ts` - use the new function
- `src/js/internal/sql/postgres.ts` - use the new function
- `src/js/internal/sql/mysql.ts` - use the new function
- `test/CLAUDE.md` - add documentation for nested object equality testing

## Key implementation details

The `buildDefinedColumnsAndQuery` function should:
1. Iterate through all items to find which columns have at least one defined value
2. For arrays, check every item - not just the first one
3. Return `{ definedColumns, columnsSql }` where columnsSql is like `"(col1, col2) VALUES"`
4. Use the provided `escapeIdentifier` function for column names

The adapters should then:
1. Use `definedColumns` instead of the original `columns` array for iteration
2. Push `null` (not `undefined`) when an item doesn't have a value for a defined column
3. Handle the single item case where `item[column]` will always be defined

## Verification

After making changes, verify that:
- All three SQL adapters import and use the new function
- The function correctly handles both single items and arrays
- Error handling exists for the all-undefined case
- The CLAUDE.md documentation is updated with the new section and examples
