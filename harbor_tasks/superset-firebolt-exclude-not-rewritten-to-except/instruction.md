# Firebolt SQL: `EXCLUDE` is being rewritten to `EXCEPT`

## Symptom

When SQL containing the `SELECT * EXCLUDE (column)` projection is run through
Apache Superset's Firebolt SQLGlot dialect, the round-tripped SQL has the
`EXCLUDE` keyword replaced with `EXCEPT`. Firebolt only supports the `EXCLUDE`
syntax, so queries that the user wrote with `EXCLUDE` fail when Superset
sends them to the database.

Concretely, parsing this query with the firebolt dialect and re-rendering it
should yield SQL that contains the keyword `EXCLUDE`, not `EXCEPT`:

```sql
SELECT g.* EXCLUDE (source_file_timestamp) FROM public.games g
```

The same applies to `EXCLUDE` with multiple columns:

```sql
SELECT * EXCLUDE (col1, col2, col3) FROM my_table
```

## Expected behavior (contract)

For the firebolt dialect:

1. Round-tripping `SELECT * EXCLUDE (col) FROM t` (parse, then re-render with
   the firebolt dialect) must produce SQL that contains the substring
   `EXCLUDE` and does **not** contain `EXCEPT`.
2. The same must hold for `EXCLUDE` with two or more columns; the column
   names must be preserved in the output.
3. Pre-existing Firebolt behavior must continue to work — most importantly,
   `WHERE x NOT IN (...)` must still be parenthesized as `NOT (... IN ...)`
   (this is enforced by the existing `not_sql` override and must not regress).
4. The Firebolt SQLGlot dialect (`Firebolt` class in
   `superset/sql/dialects/firebolt.py`) must remain a valid sqlglot
   `Dialect` subclass and continue to be discoverable via
   `sqlglot.parse_one(..., dialect="firebolt")`.

## Background

`sqlglot`'s base `Generator` class controls how the parsed `* EXCLUDE (...)`
construct is rendered via a class-level configuration that defaults to the
standard SQL spelling. Several dialects (e.g. DuckDB, Snowflake) override
that configuration because they use the `EXCLUDE` spelling instead. The
Firebolt dialect needs the same treatment.

The fix should be a small change to the Firebolt `Generator` inner class so
that the round-trip behavior described above holds. Do not modify the
`Parser` inner class — Firebolt parses `EXCLUDE` correctly today; the
problem is purely on the generation/serialization side.

## Code Style Requirements

The fix must remain consistent with the rest of the file:

- Keep the existing Apache Software Foundation license header at the top of
  any file you modify.
- New Python code (functions, methods) must have type hints per the repo's
  Python conventions.
- Do not introduce time-specific words (`now`, `currently`, `today`) in any
  new code comments — comments should be timeless.
- Keep the diff minimal: do not refactor unrelated dialect classes (`DB2`,
  `Dremio`, `Pinot`) or unrelated parts of the Firebolt file.

## Out of scope

- Changing how Firebolt parses the input SQL (the parser is already correct).
- Touching dialects other than Firebolt.
- Adding new database connectors or Superset-level configuration.
