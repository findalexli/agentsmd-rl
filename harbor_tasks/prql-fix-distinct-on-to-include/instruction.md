# DISTINCT ON generates invalid SQL

## Problem

When compiling PRQL queries that use `group ... (take 1)` targeting PostgreSQL, the generated SQL for `DISTINCT ON` is malformed. The `SELECT` list in the `DISTINCT ON` CTE produces a `NULL` expression instead of projecting columns from the source table.

For example, this PRQL:

```prql
prql target:sql.postgres

from tab1
group col1 (take 1)
derive {x = col1 + 1}
```

Produces output containing `SELECT DISTINCT ON (col1) NULL` — the `NULL` is wrong because it should include all columns from `tab1`.

The same issue occurs when `DISTINCT ON` is combined with `aggregate`:

```prql
prql target:sql.postgres

from t1
group {id, name} (take 1)
aggregate {c = count this}
```

This also produces `NULL` in the `DISTINCT ON` projection instead of projecting all columns from `t1`.

## Expected Behavior

For both query patterns above, the compiled SQL must produce valid `DISTINCT ON` CTEs where the `SELECT` list includes all source table columns (i.e., a full column projection). The `NULL` literal must not appear as the select-list expression in the `DISTINCT ON` clause.

Fix the PRQL compiler so that `DISTINCT ON` SQL generation produces valid, semantically correct PostgreSQL output for these query patterns.
