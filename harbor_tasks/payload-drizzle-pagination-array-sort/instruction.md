# Fix Array Sub-field Sort Pagination

## The Bug

When sorting by a field inside an array (e.g., `sort: 'arrayWithIDs.text'`), the SQL query applies `LIMIT` before deduplication. Since each document has multiple array items, the JOIN explodes rows — a document with 3 items contributes 3 rows. With `LIMIT 5`, you get 5 rows but possibly fewer than 5 distinct documents. This causes:

- Page 1 to return fewer than the expected number of distinct documents
- Page 2 to contain duplicates from page 1
- `totalPages` and `totalDocs` to be incorrect

## Expected Behavior

When sorting by an array sub-field with `limit: 5`:
- Each page returns the correct number of distinct documents (up to the limit)
- No document appears in more than one page
- Documents are sorted correctly across pages

## Technical Details

The fix requires changes across four files in `packages/drizzle/src/`:

### findMany.ts
The query must use GROUP BY with `min`/`max` aggregation instead of SELECT DISTINCT when sorting on array sub-fields. The `groupBy` method must be called, and `min`/`max` must be imported from `drizzle-orm`.

### buildQuery.ts
The `BuildQueryJoinAliases` type needs a boolean field to distinguish one-to-many joins from regular joins.

### addJoinTable.ts
The join helper must accept and propagate this boolean flag.

### getTableColumnFromPath.ts
When joining array parent tables, this flag must be set to `true`.

## Files to Modify

1. `packages/drizzle/src/find/findMany.ts`
2. `packages/drizzle/src/queries/buildQuery.ts`
3. `packages/drizzle/src/queries/addJoinTable.ts`
4. `packages/drizzle/src/queries/getTableColumnFromPath.ts`

## Verification

After applying the fix, the following should pass:
- `pnpm run lint` in `packages/drizzle/`
- `pnpm run build:swc` in `packages/drizzle/`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
