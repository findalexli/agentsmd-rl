# MCP Database Tools Issues

## Context

The Superset MCP (Model Context Protocol) database tools have several gaps compared to the chart and dashboard tools. The following issues need to be resolved across multiple files in the `superset/mcp_service/` directory.

## Issues

### 1. DatabaseFilter cannot filter by owner

`DatabaseFilter` in `superset/mcp_service/database/schemas.py` does not accept `created_by_fk` or `changed_by_fk` as valid filter columns. `ChartFilter` and `DashboardFilter` in the same codebase already support both fields. The `DatabaseFilter` description also does not document how to use `created_by_fk` for owner-based filtering — the description should contain the phrase `created_by_fk with the user`.

### 2. ListDatabasesRequest fails on JSON string parameters

When MCP CLI clients pass `filters` or `select_columns` as JSON strings rather than native Python objects, `ListDatabasesRequest` in `superset/mcp_service/database/schemas.py` raises a parsing error. `ListChartsRequest` and `ListDashboardsRequest` already handle this correctly via pydantic field validators. `ListDatabasesRequest` needs the same treatment so that both `filters` and `select_columns` accept JSON string inputs as well as native Python lists.

### 3. Duplicate default database columns across modules

The list of default database columns is independently defined in both `superset/mcp_service/database/tool/schema_discovery.py` and `superset/mcp_service/database/tool/list_databases.py`. When one copy is updated, the other drifts. There should be a single source of truth — `list_databases.py` should reuse the canonical list from `schema_discovery.py` instead of maintaining its own duplicate copy.

### 4. Timestamps are timezone-naive

`DatabaseError.create()` in `superset/mcp_service/database/schemas.py` produces naive timestamps (no timezone info). Similarly, `_humanize_timestamp()` does not handle timezone-aware datetime inputs — when a timezone-aware datetime is passed, the subtraction `datetime.now() - dt` fails with a TypeError. After fixing, `DatabaseError.create()` should produce UTC-aware timestamps, and `_humanize_timestamp()` should handle both naive and timezone-aware datetime inputs correctly.

### 5. Test helper missing type annotations

The `create_mock_database()` function in `tests/unit_tests/mcp_service/database/tool/test_database_tools.py` has parameters without Python type annotations. The corrected function should have `database_id: int = 1`, `database_name: str = "examples"`, and return type `-> MagicMock`.

### 6. MCP app instructions omit database ownership filtering

Users of the MCP server aren't told they can filter databases by owner. The instructions in `superset/mcp_service/app.py` should: mention `charts/dashboards/databases` in the find-your-own section, include an example showing `list_databases(filters=[{"col": "created_by_fk"` (with braces doubled for Python f-strings), and have a `My databases:` section.

### 7. ModelGetSchemaCore docstring omits database

The `ModelGetSchemaCore` docstring in `superset/mcp_service/mcp_core.py` lists valid model types as `(chart, dataset, dashboard)` but does not include `database`. The corrected docstring should read `(chart, dataset, dashboard, database)`.

## Reference Patterns

For issues 1 and 2, look at the existing chart/dashboard implementations:
- `ChartFilter` and `DashboardFilter` in `superset/mcp_service/chart/schemas.py` and `superset/mcp_service/dashboard/schemas.py` for user ownership column support
- `ListChartsRequest` and `ListDashboardsRequest` for JSON string parameter handling via field validators
- `superset/mcp_service/utils/schema_utils` for JSON parsing utility functions

## Affected Files

- `superset/mcp_service/database/schemas.py` (issues 1, 2, 4)
- `superset/mcp_service/database/tool/list_databases.py` (issue 3)
- `superset/mcp_service/app.py` (issue 6)
- `superset/mcp_service/mcp_core.py` (issue 7)
- `tests/unit_tests/mcp_service/database/tool/test_database_tools.py` (issue 5)
