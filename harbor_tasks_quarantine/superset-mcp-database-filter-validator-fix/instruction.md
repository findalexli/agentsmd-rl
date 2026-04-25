# Fix MCP Database Service Issues

The Superset MCP (Model Context Protocol) service has several issues in the database tools that need to be fixed to bring them to parity with the chart and dashboard tools.

## 1. DatabaseFilter Missing User Fields

The `DatabaseFilter` model does not accept `created_by_fk` and `changed_by_fk` as valid filter columns, preventing "find my databases" queries.

**Expected behavior**:
- `DatabaseFilter(col="created_by_fk", opr="eq", value=123)` should work without validation errors
- `DatabaseFilter(col="changed_by_fk", opr="eq", value=456)` should work without validation errors
- The `DatabaseFilter` description text should mention using `created_by_fk with the user` ID from `get_instance_info's current_user`

## 2. Missing Field Validators for JSON Parsing

The database request model does not handle JSON string inputs for `filters` and `select_columns`. MCP clients may send these as JSON strings due to double-serialization issues.

**Expected behavior**:
- `ListDatabasesRequest(filters='[{"col": "created_by_fk", "opr": "eq", "value": 123}]')` should parse into a list of filter model objects with `.col`, `.opr`, and `.value` accessible
- `ListDatabasesRequest(select_columns='["id", "database_name", "backend"]')` should parse into `["id", "database_name", "backend"]`
- The database schemas module must re-export `field_validator` (from pydantic), `parse_json_or_list`, and `parse_json_or_model_list` so they are importable from the `superset.mcp_service.database.schemas` namespace

## 3. Duplicate Default Columns Constant

The default database columns list is duplicated — it exists in the database list tool and also in the shared `superset.mcp_service.common.schema_discovery` module as `DATABASE_DEFAULT_COLUMNS`. The local copy in the list tool should be eliminated by importing `DATABASE_DEFAULT_COLUMNS` from `superset.mcp_service.common.schema_discovery` and using it (e.g., `default_columns=DATABASE_DEFAULT_COLUMNS`).

## 4. Timezone-Aware Timestamp Issues

Two timestamp bugs exist in the database schemas:

- `DatabaseError.create()` produces naive timestamps (missing timezone info)
- The `_humanize_timestamp` function fails when given timezone-aware datetime objects

**Expected behavior**:
- `DatabaseError.create(error="Test error", error_type="test")` should produce a timestamp where `.tzinfo is not None`
- `_humanize_timestamp()` should work correctly with both timezone-aware and naive datetimes (e.g., `datetime.now(timezone.utc) - timedelta(hours=2)` should return a string containing "hour" or "ago"; naive datetimes should also produce valid results)

## 5. Documentation Updates

The default MCP instructions need to be updated to include database examples:

- The existing "charts/dashboards" references should be updated to include databases as well (the literal text `charts/dashboards/databases` should appear)
- Include an example showing `list_databases(filters=[{"col": "created_by_fk", ...}])`
- Add a section with the heading `My databases:`

## 6. Docstring Fix

The `ModelGetSchemaCore.__init__` docstring lists supported model types as `(chart, dataset, dashboard)` but omits `database`. It should say `(chart, dataset, dashboard, database)`.

## Verification

You can verify your changes by running the MCP database unit tests:
```bash
SUPERSET_TESTENV=true SUPERSET_SECRET_KEY=test python -m pytest tests/unit_tests/mcp_service/ -v --tb=short -x
```
