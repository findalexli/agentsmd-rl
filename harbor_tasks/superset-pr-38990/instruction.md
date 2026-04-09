# Fix MCP Service Table Chart Raw Mode and Dashboard Title XSS

There are several bugs in the Superset MCP (Model Context Protocol) service that need fixing:

## Bug 1: Table Chart ASCII Preview Fails in Raw Mode

When calling `get_chart_preview` with `format: "ascii"` on a table chart configured in raw mode (showing individual rows without aggregation), the preview fails with an "Empty query?" error.

**Location**: `superset/mcp_service/chart/tool/get_chart_preview.py`

The `ASCIIPreviewStrategy` class doesn't properly handle table charts in raw mode. It needs to check for `query_mode: "raw"` and use `all_columns` or `columns` fields instead of assuming `groupby` and `x_axis` are always present.

## Bug 2: Table Chart Compile Check Fails in Raw Mode

The `_build_query_columns()` function in `preview_utils.py` doesn't handle table charts in raw mode, causing compile checks to fail for table chart generation.

**Location**: `superset/mcp_service/chart/preview_utils.py`

The function currently only looks at `x_axis`, `groupby`, and `columns` but doesn't check for `all_columns` which is used in raw mode.

## Bug 3: Table Chart Form Data Missing Required Fields

When `map_table_config()` builds form_data for table charts in raw mode, it only includes `"all_columns"` but the `QueryContextFactory` validation requires both `"all_columns"` AND `"columns"` to avoid "Empty query?" errors.

**Location**: `superset/mcp_service/chart/chart_utils.py`

The fix should add `"columns": raw_columns` alongside the existing `"all_columns"` setting.

## Bug 4: Dashboard Title XSS Vulnerability

The `GenerateDashboardRequest` schema in `superset/mcp_service/dashboard/schemas.py` does not sanitize the `dashboard_title` field, allowing XSS attacks via HTML tags in the title.

**Location**: `superset/mcp_service/dashboard/schemas.py`

The fix requires:
1. Import `_strip_html_tags` and `_remove_dangerous_unicode` from `superset.mcp_service.utils.sanitization`
2. Add a `@field_validator("dashboard_title")` method that strips HTML tags and removes dangerous unicode characters

The existing chart schemas already use this pattern - follow the same approach for dashboard titles.

## Files to Modify

1. `superset/mcp_service/chart/chart_utils.py` - Add "columns" alongside "all_columns" in raw mode
2. `superset/mcp_service/chart/preview_utils.py` - Handle raw mode in `_build_query_columns()`
3. `superset/mcp_service/chart/tool/get_chart_preview.py` - Handle raw mode in ASCIIPreviewStrategy
4. `superset/mcp_service/dashboard/schemas.py` - Add field_validator to sanitize dashboard_title

## Testing

After fixing:
- Table charts in raw mode should return data instead of "Empty query?" errors
- Dashboard titles with `<script>alert(1)</script>Test` should have the script tags stripped
- Dashboard titles with dangerous unicode should have those characters removed
