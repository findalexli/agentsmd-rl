# DISTINCT ON generates invalid SQL with NULL instead of wildcard

## Problem

When compiling PRQL queries that use `group ... (take 1)` targeting PostgreSQL, the generated SQL contains `DISTINCT ON (...) NULL` instead of `DISTINCT ON (...) *`. This produces incorrect SQL — PostgreSQL's `DISTINCT ON` clause requires a valid projection, and `NULL` as a column expression is semantically wrong here.

For example, this PRQL:

```
prql target:sql.postgres

from tab1
group col1 (take 1)
derive {x = col1 + 1}
```

Generates a CTE with `DISTINCT ON (col1) NULL` when it should produce `DISTINCT ON (col1) *`.

The same issue occurs when `DISTINCT ON` is combined with `aggregate` — the projection in the CTE gets a `NULL` placeholder instead of a wildcard.

## Expected Behavior

The SQL generator should emit `*` (wildcard) instead of `NULL` in the `SELECT` list when the projection for a `DISTINCT ON` subquery is empty or contains only a `NULL` placeholder.

## Files to Look At

- `prqlc/prqlc/src/sql/gen_query.rs` — the SQL code generation pipeline where `DISTINCT ON` and projections are assembled

After fixing the code generation, update the project's `CLAUDE.md` to document the preferred testing approach for this kind of bug fix — the project currently lacks guidance on when contributors should write inline unit tests vs full integration tests.
