# Fix Array Sub-field Sort Pagination

The `findMany` function in `packages/drizzle/src/find/findMany.ts` has a bug when sorting by a field inside an array (e.g., `sort: 'arrayWithIDs.text'`).

## The Problem

When a document has an array field with multiple items, a SQL JOIN explodes the rows. For example, a post with 3 array items produces 3 rows. When you apply `LIMIT 5`, you get 5 rows that may all belong to the same document. The existing deduplication approach fails to deduplicate before applying pagination, causing:

- Page 1 to return fewer than 5 distinct documents
- Page 2 to return duplicates from page 1
- `totalPages` and `totalDocs` to be wrong

## Expected Behavior

The following test in `test/database/int.spec.ts` describes the correct behavior:

```
"should return the correct number of docs per page when sorting on an array sub-field"
```

This test creates 10 documents, each with 3 array items, then paginates with `LIMIT=5` and verifies:
- Page 1 has exactly 5 distinct docs
- Page 2 has exactly 5 distinct docs
- No doc appears in both pages
- Sort order is correct across pages

## Files to Modify

Four files need changes to fix this issue:

1. `packages/drizzle/src/find/findMany.ts` — main fix; the corrected implementation should track `oneToManyJoinedTableNames` and use a `groupBy` approach with `min(column)` or `max(column)` aggregation for one-to-many joins, ensuring deduplication happens before pagination is applied
2. `packages/drizzle/src/queries/buildQuery.ts` — the join aliases type needs an `isOneToMany` field to distinguish one-to-many joins from regular joins
3. `packages/drizzle/src/queries/addJoinTable.ts` — needs to accept and propagate the `isOneToMany` parameter
4. `packages/drizzle/src/queries/getTableColumnFromPath.ts` — needs to set `isOneToMany: true` when joining array parent tables

## Verification

After applying the fix, ensure the following pass:
- `pnpm run lint` in `packages/drizzle/`
- `pnpm run build:swc` in `packages/drizzle/`
