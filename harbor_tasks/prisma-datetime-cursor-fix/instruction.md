# Task

Cursor-based pagination queries using `DateTime` columns in Prisma return
incorrect results. When a query specifies a cursor on a `DateTime` field,
rows that should be excluded by the cursor boundary are still included in
the result set. The query executes without errors — the cursor simply has
no filtering effect, and pages beyond the first page include records that
belong on earlier pages.

## Affected Queries

Queries like the following are affected:

```typescript
const page2 = await prisma.model.findMany({
  cursor: { createdAt: "2025-01-03" },
  take: 10,
  skip: 1,
})
```

When `createdAt` is a `DateTime` column and the cursor value is provided
as a string (which is the natural way to pass dates from API inputs or
serialized data), the pagination boundary is silently ignored. The same
query works correctly for non-`DateTime` cursor fields.

## Expected Behavior

A `DateTime` cursor value such as `"2025-01-03"` should produce a correct
pagination boundary: all returned rows must satisfy the date comparison
relative to that cursor value.

The date value must be preserved through any conversion — a cursor of
`"2025-01-03"` must map to the same calendar date, not a shifted or
truncated date.

## Non-Affected Types

The following query variable types are **not** affected and must continue
to behave as they currently do:

- `String`
- `Int`
- `Float`
- `Boolean`
- `Json`

No change in behavior is acceptable for these types. Their values must
pass through without any conversion.

## Verification

To verify your fix, you can test with a `DateTime` cursor by constructing
a query that paginates over a model with a `DateTime` field. The second
page should not include rows from the first page. Prisma's existing test
suite and linters must continue to pass.

## Code Style Requirements

Your solution will be checked by the repository's existing linters and
formatters. All modified files must pass:

- `prettier` (JS/TS/JSON/Markdown formatter)
- `eslint` (JS/TS linter)
