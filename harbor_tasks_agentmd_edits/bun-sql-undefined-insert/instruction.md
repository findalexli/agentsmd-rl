# Fix SQL helper undefined value handling and update testing documentation

The `sql()` helper in Bun's SQL implementation has a bug with how it handles `undefined` values in INSERT statements. Currently, `undefined` values are converted to `NULL`, which prevents columns with `DEFAULT` values from using their defaults.

## The Bug

When you use the SQL helper like this:
```typescript
await sql`INSERT INTO users ${sql({ id: "123", name: undefined })}`;
```

The current behavior generates: `(id, name) VALUES (?, ?)` with binding `["123", null]`

This causes issues when the `name` column has a `DEFAULT` constraint - the explicit `NULL` overrides the default.

## What Should Happen

The helper should **omit** columns that have `undefined` values from the INSERT statement entirely:
- `sql({ foo: undefined, id: "123" })` in INSERT should generate `(id) VALUES (?)`, letting the database use the DEFAULT value for `foo`
- In bulk inserts, check ALL items for defined values (not just the first item) to avoid silently dropping data from later items

## Files to Modify

The SQL implementation is in `src/js/internal/sql/`:
- `shared.ts` - Contains shared SQL helper functions
- `sqlite.ts` - SQLite adapter implementation
- `mysql.ts` - MySQL adapter implementation
- `postgres.ts` - PostgreSQL adapter implementation

## Additional Task: Update Testing Documentation

After fixing the code, you must also update the project's testing documentation to reflect best practices demonstrated by your fix.

The file `test/CLAUDE.md` contains testing guidelines for contributors. When writing tests for this fix, consider:
- How should complex/nested objects be compared in tests?
- What's the preferred way to assert on arrays of objects?

Update `test/CLAUDE.md` with appropriate guidance for future contributors.

## Testing Your Fix

1. The fix should handle single item inserts with undefined values
2. The fix should handle bulk inserts where some items have undefined values for certain columns
3. The fix should preserve values from ALL items in a bulk insert, not just the first one
4. An error should be thrown if all columns are undefined

## Notes

- Look at how the SQL helper currently constructs INSERT queries
- Consider creating a shared helper function that determines which columns have at least one defined value across all items
- The bulk insert case is important - ensure values from middle items aren't lost
- For the documentation update, think about what testing patterns would help catch similar issues
