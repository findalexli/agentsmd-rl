# MCP Service Bug Fixes

The MCP (Model Context Protocol) service in Apache Superset has several bugs that need to be fixed.

## Bug 1: Chart Info Missing form_data

When calling `get_chart_info` through the MCP service, the response's `form_data` field is always `null`, even when the chart has valid configuration data stored in its `params` field.

**Expected**: The `form_data` field should contain the parsed chart configuration from `chart.params`.

**Implementation requirements**:
- The chart info serialization must parse `chart.params` using a JSON decoder
- The parsed result must be assigned to a variable named `chart_form_data`
- The expression `utils_json.loads(chart_params)` must be used to parse the JSON string
- The `ChartInfo` response must include `form_data=chart_form_data`
- Must handle the case where `chart.params` is already a dict (use `isinstance(chart_params, dict)`)

## Bug 2: Dataset URL is Relative

The `get_dataset_info` endpoint returns a relative URL like `/tablemodelview/edit/123` instead of an absolute URL with the full hostname.

**Expected**: Dataset URLs should be absolute (e.g., `http://superset.example.com/tablemodelview/edit/123`), matching how chart and dashboard URLs work.

**Implementation requirements**:
- Use `get_superset_base_url()` to construct the absolute URL
- Include `/tablemodelview/edit/` path segment in the URL

## Bug 3: ASCII Preview Crashes on Empty Charts

When a chart has no `groupby`, `x_axis`, or `all_columns` configured, the ASCII preview feature crashes with a "Columns missing" error from QueryContextFactory instead of returning a graceful error message.

**Expected**: Return an `UnsupportedChart` error when the chart configuration has no columns or metrics.

**Implementation requirements**:
- Check for empty columns and metrics using: `not columns and not metrics`
- Return an `UnsupportedChart` error with message "Cannot generate ASCII preview"

## Bug 4: Chart Rename Requires Full Config

The `update_chart` MCP tool requires the `config` field even when the user only wants to rename a chart. This makes simple operations unnecessarily complex.

**Expected**: Allow renaming a chart with just `identifier` and `chart_name`, without requiring `config`.

**Implementation requirements**:
- Define a helper function `_build_update_payload()` that supports name-only updates
- When no config is provided, return `{"slice_name": request.chart_name}`
- Return a `ValidationError` with message "Either 'config' or 'chart_name' must be provided" when neither is supplied
- Define a helper function `_find_chart()` that:
  - Handles numeric identifiers with `identifier.isdigit()` and `int(identifier)`
  - Handles UUID strings with `id_column="uuid"`
- `UpdateChartRequest.config` field must be `Optional` with type `ChartConfig | None = Field(None, ...)`
- Errors must use structured format with `error_type`, `message`, and `details` fields

## Requirements

- Fix all 4 bugs
- Ensure code passes `ruff check`
- Add appropriate type hints for any new code
- Follow existing code patterns in the MCP service module