# Align legacy `/datasource` views with Superset's resource-level access checks

## Context

Apache Superset's modern REST API enforces resource-level authorization on every datasource read and write — every endpoint that returns or mutates a datasource calls `security_manager.raise_for_access(...)` (for reads) or `security_manager.raise_for_ownership(...)` (for writes) before doing any work.

The **legacy** `/datasource` endpoints implemented by the `Datasource` view in `superset/views/datasource/views.py` are inconsistent with that contract. Several handlers fetch a datasource and return its data (or its external metadata) without ever consulting the security manager, and the `save` handler skips the ownership check whenever the request body happens to omit the `owners` key. The result is that an authenticated user can:

1. Read datasource metadata (the full `data` payload, or the columns returned by `external_metadata`/`external_metadata_by_name`) for a datasource they should not be able to see.
2. Update a datasource they do not own by posting a payload that simply leaves the `owners` field out — the existing `if "owners" in datasource_dict and ...` guard treats a missing `owners` key as a green light.

## What you need to fix

All changes are in `superset/views/datasource/views.py`.

### 1. Read endpoints must enforce `raise_for_access`

The following methods on the `Datasource` view currently return data without checking access. Each of them must call `security_manager.raise_for_access(datasource=<resolved_datasource>)` once the datasource has been resolved, **before** any data is returned to the caller. The exception must propagate (it is what produces the 403 response further up the stack).

- `Datasource.get(datasource_type, datasource_id)` — after `DatasourceDAO.get_datasource(...)` returns, but before `self.json_response(sanitize_datasource_data(datasource.data))`.
- `Datasource.external_metadata(datasource_type, datasource_id)` — after the datasource is resolved, before `datasource.external_metadata()` is called.
- `Datasource.external_metadata_by_name(**kwargs)` — this method has two branches:
  - **Branch A — the datasource exists in Superset's metadata.** Call `raise_for_access(datasource=datasource)` before reading `datasource.external_metadata()`.
  - **Branch B — there is no Superset datasource yet, so the columns are read directly from the live database via the SQLAlchemy inspector.** In this branch, build the `Table` (using `params["table_name"]`, `params["schema_name"]`, and `params.get("catalog_name")`) once and reuse it. Call `security_manager.raise_for_access(database=<resolved_database>, table=<that Table>)` before any metadata is fetched, and then pass the same `Table` instance into `get_physical_table_metadata`. (Branch B previously constructed a `Table` with only two positional arguments, which silently dropped any `catalog_name` from the request — fix that too.)

### 2. The `save` handler must always check ownership

In `Datasource.save`, the ownership guard currently reads:

```python
if "owners" in datasource_dict and orm_datasource.owner_class is not None:
    # Check ownership
    try:
        security_manager.raise_for_ownership(orm_datasource)
    ...
```

Drop the `"owners" in datasource_dict and` precondition. Ownership must be enforced for every update where the model supports ownership (i.e. whenever `orm_datasource.owner_class is not None`), regardless of whether the request body includes an `owners` field. The exception-handling block beneath the guard does not need to change — it already converts `SupersetSecurityException` into `DatasetForbiddenError`.

## Where the new tests go

Add unit-test coverage for the new behaviour at:

```
tests/unit_tests/views/datasource/views_test.py
```

(The directory and its `__init__.py` already exist.) The tests should exercise the handlers directly via `inspect.unwrap`, mocking `security_manager`, `DatasourceDAO`, `SqlaTable.get_datasource_by_name`, `ExternalMetadataSchema`, and (for the no-datasource branch) `db.session`. Both halves of each contract should be covered:

- An "access denied" case where `raise_for_access` raises and the handler propagates the exception, and the call args confirm the correct kwargs (`datasource=...`, or `database=...`/`table=...`).
- An "access allowed" case where `raise_for_access` returns `None` and the handler proceeds.
- For `save`: one case with `owners` omitted from the payload and one with `owners` supplied — both must end up calling `raise_for_ownership(orm_datasource)`.

Use `flask.Flask().test_request_context(...)` to drive the `save` handler so that `request.form` is populated.

## Code Style Requirements

The repository's `AGENTS.md` (and `CLAUDE.md` / `.cursor/rules/dev-standard.mdc`) require:

- **Apache License headers** on every newly created Python file (the standard ASF header — see any existing file under `tests/unit_tests/` for the canonical text).
- **Type hints** on all new Python code — function parameters and return types must be annotated.
- **`pytest`** as the test framework (do not add `unittest.TestCase` subclasses).
- **No time-specific words** ("now", "currently", "today") in code comments.

`pre-commit run --all-files` must remain clean after your changes (ruff, black, mypy).

## How your work will be evaluated

Your changes will be exercised by a pytest suite that:

1. Imports `superset.views.datasource.views` and unwraps each handler with `inspect.unwrap`, then calls it with mocks. Each handler must invoke the security manager exactly as described above (kwargs and call counts are asserted).
2. Verifies that `Datasource.save` raises `superset.commands.dataset.exceptions.DatasetForbiddenError` when the mocked `raise_for_ownership` raises, in **both** the "owners omitted" and "owners supplied" payload shapes.
3. Confirms that the new test file at `tests/unit_tests/views/datasource/views_test.py` carries an ASF license header and uses Python type annotations.
4. Confirms that `pytest --collect-only tests/unit_tests/views/datasource/` succeeds and that `superset.views.datasource.views` imports cleanly.

Do not modify other files unless strictly necessary to make the above pass.
