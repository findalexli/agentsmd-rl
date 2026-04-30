# DISTINCT ON generates invalid SQL

## Problem

When compiling PRQL queries that use `group ... (take 1)`, the generated SQL for `DISTINCT ON` is malformed. The `SELECT` list in the `DISTINCT ON` CTE fails to project columns from the source table, producing either the `NULL` literal or an empty projection instead of the `*` wildcard.

For example, this PRQL targeting DuckDB:

```prql
prql target:sql.duckdb

from tab1
group col1 (take 1)
derive foo = 1
select foo
```

Produces output containing `SELECT DISTINCT ON (col1) NULL` — the `NULL` is wrong because the `DISTINCT ON` CTE should project all columns from `tab1` using `*`.

The same issue occurs when `DISTINCT ON` is combined with `aggregate`. This PRQL targeting PostgreSQL:

```prql
prql target:sql.postgres

from t1
group {id, name} (take 1)
aggregate {c = count this}
```

Produces an empty projection after `DISTINCT ON (id, name)` — there is no `*` wildcard and no column list between `DISTINCT ON (id, name)` and `FROM`. The projection is simply missing.

## Expected Behavior

For all query patterns above, the compiled SQL must produce valid `DISTINCT ON` CTEs where the `SELECT` list uses the `*` wildcard to include all source table columns. The `NULL` literal and empty projection must not appear as the select-list in the `DISTINCT ON` clause.

Fix the PRQL compiler so that `DISTINCT ON` SQL generation produces valid, semantically correct output for these query patterns.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
