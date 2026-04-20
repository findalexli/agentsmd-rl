# Task: Fix Docs Inventory URIs for dagster_pipes

## Problem

`dagster_pipes` is not appearing in the published API inventory. When the documentation site is built, the inventory file (objects.inv) contains incorrect URIs for the `dagster_pipes` package.

## Expected Behavior

The `transform_inventory_uri()` function in `docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py` transforms Sphinx source paths to final documentation URLs. Currently, it only transforms paths under `sections/api/apidocs/dagster/` to `api/dagster/...`. However, `dagster_pipes` lives at `sections/api/dagster/pipes` (not under `apidocs/`), so its URI is not being transformed. This causes a mismatch with the actual URL structure where `dagster_pipes` is served at `api/dagster/pipes`.

After transformation:
- `sections/api/dagster/pipes` → `api/dagster/pipes`
- `sections/integrations/libraries/dagster-airflow` → `integrations/libraries/dagster-airflow`

## Verification

The tests in `tests/test_outputs.py` verify that:
1. `transform_inventory_uri("sections/api/dagster/pipes")` returns `"api/dagster/pipes"`
2. `transform_inventory_uri("sections/integrations/libraries/dagster-airflow")` returns `"integrations/libraries/dagster-airflow"`
3. Trailing slashes are removed from transformed URIs
4. Non-sections URIs pass through unchanged

## Constraints

- The file being modified is: `docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py`
- After making changes, run `make ruff` to ensure code quality
- Use Python 3.9+ builtin types for type annotations (dict, list not typing.Dict)