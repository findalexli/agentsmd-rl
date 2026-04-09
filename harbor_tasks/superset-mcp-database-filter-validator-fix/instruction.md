# Fix MCP Database Service Issues

The Superset MCP (Model Context Protocol) service has several issues in the database tools that need to be fixed:

## 1. DatabaseFilter Missing User Fields

The `DatabaseFilter` class in `superset/mcp_service/database/schemas.py` is missing the `created_by_fk` and `changed_by_fk` filter columns. These are needed to allow "find my databases" queries using the user's ID from `get_instance_info`.

**Expected**: The `col` field in `DatabaseFilter` should accept `created_by_fk` and `changed_by_fk` as valid filter columns, matching the pattern used in chart and dashboard filters.

## 2. Missing Field Validators for JSON Parsing

The `ListDatabasesRequest` class lacks field validators for `filters` and `select_columns`. MCP clients may send these as JSON strings (due to double-serialization issues), but the current implementation doesn't handle this.

**Expected**: Add `@field_validator` decorators for both `filters` and `select_columns` fields that can parse JSON strings or accept native Python lists. Look at how `DashboardFilter` or `ChartFilter` handles this for reference - they use utilities from `superset.mcp_service.utils.schema_utils`.

## 3. Duplicate DEFAULT_DATABASE_COLUMNS

The `DEFAULT_DATABASE_COLUMNS` list is defined in both `superset/mcp_service/database/tool/list_databases.py` AND `superset/mcp_service/common/schema_discovery.py`. This creates maintenance issues.

**Expected**: The `list_databases.py` file should import `DATABASE_DEFAULT_COLUMNS` from `schema_discovery` instead of defining its own local copy.

## 4. Timezone-Aware Timestamp Issues

Two timestamp-related bugs need fixing:

a) `DatabaseError.create()` in `schemas.py` uses `datetime.now()` without timezone info, creating naive timestamps.

b) `_humanize_timestamp()` function doesn't properly handle timezone-aware datetimes, which can cause errors when comparing naive and aware datetimes.

**Expected**: Use `datetime.now(timezone.utc)` for UTC-aware timestamps, and ensure `_humanize_timestamp` handles both aware and naive datetimes correctly.

## 5. Documentation Updates

The default instructions in `superset/mcp_service/app.py` need updates:

- The "To find your own charts/dashboards:" section should mention databases too
- Add an example showing `list_databases(filters=[{"col": "created_by_fk", ...}])`
- Add a "My databases:" section in the examples

## 6. Docstring Fix

In `superset/mcp_service/mcp_core.py`, the `ModelGetSchemaCore.__init__` docstring mentions model types but is missing "database" from the list.

**Expected**: The docstring should say `(chart, dataset, dashboard, database)` instead of just `(chart, dataset, dashboard)`.

## Files to Modify

- `superset/mcp_service/database/schemas.py` - Add field validators, fix timestamps, add filter columns
- `superset/mcp_service/database/tool/list_databases.py` - Remove duplicate DEFAULT_DATABASE_COLUMNS, import from schema_discovery
- `superset/mcp_service/app.py` - Update documentation/instructions
- `superset/mcp_service/mcp_core.py` - Update docstring

## Testing

You can verify your changes by:
1. Checking that `DatabaseFilter` accepts `created_by_fk` and `changed_by_fk` as valid filter columns
2. Verifying that `ListDatabasesRequest` can parse JSON string inputs for `filters` and `select_columns`
3. Confirming that `list_databases.py` imports `DATABASE_DEFAULT_COLUMNS` from schema_discovery
4. Testing that `DatabaseError.create()` produces timezone-aware timestamps
5. Ensuring the documentation in `app.py` includes database examples

## Reference

Look at how the chart and dashboard tools implement similar features - they already have these patterns in place:
- `superset/mcp_service/chart/schemas.py` for filter validators
- `superset/mcp_service/dashboard/schemas.py` for field validation patterns
- `superset/mcp_service/common/schema_discovery.py` for the canonical DEFAULT_DATABASE_COLUMNS
