# SQL Lab cost estimation leaks query plans without authorization

You are working in the Apache Superset repository (Python backend, Flask /
SQLAlchemy / Flask-AppBuilder).

## The bug

Superset exposes an **SQL Lab "estimate"** endpoint that returns a query's cost
estimate (and, depending on the engine, a query plan) for a given database. The
relevant business-logic class is `QueryEstimationCommand` in
`superset/commands/sql_lab/`.

The command's request-validation step today does only one thing: it loads the
target `Database` row by `database_id` and raises a
`SupersetErrorException` (status 404, error type
`SupersetErrorType.RESULTS_BACKEND_ERROR`) when the row is missing.

It **does not** verify that the calling user is authorized to use that
database. Any authenticated user can therefore submit an estimate request for
*any* database id and receive its cost / plan back, even when they have no
access to the database itself. This is inconsistent with the rest of SQL Lab,
where every other database-touching command goes through the
`SecurityManager`'s mandatory access check before returning data to the caller.

## What "fixed" looks like

`QueryEstimationCommand`'s validation must enforce **database-level access
control** on the resolved `Database` object using Superset's standard
`SecurityManager` API: `security_manager.raise_for_access(database=...)`.

Required behaviour after the fix:

1. **Authorized caller (`raise_for_access` returns normally)** —
   validation succeeds and the rest of the command proceeds as before.
2. **Unauthorized caller (`raise_for_access` raises
   `SupersetSecurityException`)** — the exception must propagate out of the
   command unchanged. It must not be swallowed, wrapped, or downgraded; in
   particular, the agent must not catch it and return a cost estimate, query
   plan, or any other database-derived metadata.
3. **Database does not exist** — the existing 404-style
   `SupersetErrorException` (with `error_type ==
   SupersetErrorType.RESULTS_BACKEND_ERROR`) must still be raised, **and the
   access check must not be invoked**. Calling the access check on a
   nonexistent record would either error out for unrelated reasons or leak
   record-existence information to unauthorized users.
4. The access check must use the resolved `Database` ORM object — the same
   object obtained from the session lookup — passed as the `database=`
   keyword argument.

The `security_manager` symbol is available in this codebase as
`from superset import security_manager` (it is the Flask-AppBuilder /
Superset singleton, also re-exported from `superset.extensions`).

## Out of scope

- The `run()` method's post-validation logic (template processing, timeout
  handling, cost formatting) is correct as-is. Do not change it.
- Other SQL-Lab commands (execute, export, streaming export) already perform
  this check — no changes are required there.
- No new public API, schema, or migration is needed.

## Code Style Requirements

This repository enforces, via `pre-commit` (ruff, black, mypy):

- **Type hints** on all new/modified Python code.
- **MyPy compliance** — `pre-commit run mypy` must pass.
- **No time-specific language** (`now`, `currently`, `today`, …) in code
  comments.
- **Apache Software Foundation license header** at the top of any *newly
  created* `.py` file.
- For unit tests, prefer plain `MagicMock()` over `AsyncMock()` for
  synchronous code paths.

## Reference

- PR: https://github.com/apache/superset/pull/38648
- Repo agent guide: `AGENTS.md`, `CLAUDE.md`,
  `.cursor/rules/dev-standard.mdc`.
