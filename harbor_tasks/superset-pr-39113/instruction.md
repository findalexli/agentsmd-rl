# MCP Database Tools: Timezone and Validator Issues

## Problem

The MCP database tools have bugs that cause test failures and incorrect behavior:

### Bug 1: Timestamp Timezone Handling
The `DatabaseError.create()` method creates timestamps using `datetime.now()` without timezone information. When timestamps are compared or serialized across different timezone contexts, operations may fail or produce incorrect results.

**Symptom:** `error.timestamp.tzinfo` is `None` instead of being timezone-aware. Code that relies on timezone-aware timestamps may raise errors or produce incorrect comparisons.

### Bug 2: Timezone-Aware Humanization Failure
The `_humanize_timestamp()` function fails when given timezone-aware datetime objects.

**Symptom:** When `_humanize_timestamp()` receives a timezone-aware datetime (e.g., `datetime.now(timezone.utc)`), it raises:
```
TypeError: can't subtract offset-naive and offset-aware datetimes
```

### Bug 3: DatabaseFilter Column Gaps
The `DatabaseFilter` class is missing valid columns that downstream code expects to use.

**Symptom:** Creating a `DatabaseFilter(col="created_by_fk", ...)` or `DatabaseFilter(col="changed_by_fk", ...)` may fail validation even though these are legitimate columns.

### Bug 4: ListDatabasesRequest Validator Issues
The `ListDatabasesRequest` validator for the `filters` field does not properly handle JSON string inputs that MCP clients send.

**Symptom:** When `filters` is passed as a JSON string like `'[{"col": "database_name", "opr": "eq", "value": "test_db"}]'`, the request may not parse correctly. Similarly, `select_columns` may not accept JSON array strings like `'["id", "database_name"]'`.

### Bug 5: CI Linting Issues
The `superset/mcp_service/database/schemas.py` file may have ruff lint or format issues.

**Symptom:** Running `ruff check` or `ruff format --check` on the schemas file fails CI checks.

## Relevant File

- `superset/mcp_service/database/schemas.py` - Contains `DatabaseError.create()`, `_humanize_timestamp()`, `DatabaseFilter`, and `ListDatabasesRequest`

## Expected Behavior

1. `DatabaseError.create()` should produce timestamps that work correctly in timezone-aware comparisons and serializations.

2. `_humanize_timestamp()` should handle both timezone-aware and naive datetime inputs without raising `TypeError`.

3. `DatabaseFilter` should accept valid database columns including `created_by_fk` and `changed_by_fk`.

4. `ListDatabasesRequest` validators should accept:
   - JSON string for `filters`: `'[{"col": "database_name", "opr": "eq", "value": "test_db"}]'`
   - JSON array string for `select_columns`: `'["id", "database_name"]'`
   - Default `page` value should be `1`

5. Ruff lint and format checks should pass on `superset/mcp_service/database/schemas.py`.

## Existing Valid Columns

These columns are known to work with `DatabaseFilter`:
- `database_name`
- `expose_in_sqllab`
- `allow_file_upload`
