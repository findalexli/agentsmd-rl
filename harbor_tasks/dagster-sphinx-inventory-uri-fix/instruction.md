# Fix Sphinx Inventory URI Transformation

The `transform_inventory_uri` function in `docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py` is not correctly transforming documentation paths.

## Problem

When processing Sphinx inventory URIs, paths like `sections/api/apidocs/dagster/internals/` should be transformed to `api/dagster/internals` in the final documentation. Currently, the function is incorrectly transforming these paths, resulting in broken documentation links.

The function should:
1. Transform paths starting with `sections/api/apidocs/` to start with `api/`
2. Remove trailing slashes from the transformed path
3. Leave other paths unchanged

## Files to Modify

- `docs/sphinx/_ext/dagster-sphinx/dagster_sphinx/__init__.py` - The `transform_inventory_uri` function

## Verification

After fixing, the function should correctly transform:
- `sections/api/apidocs/dagster/internals/` → `api/dagster/internals`
- `sections/api/apidocs/dagster/pipes` → `api/dagster/pipes`
- `sections/api/apidocs/` → `api`
- `other/path/` → `other/path/` (unchanged)

## Code Quality

After making changes, run `make ruff` at the repository root to ensure the code passes formatting and linting checks.
