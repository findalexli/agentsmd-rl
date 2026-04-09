# Task: Add get_chart_type_schema MCP Tool

## Problem

The Superset MCP (Model Context Protocol) service needs a new tool that allows AI agents to discover the exact JSON Schema and configuration options for each chart type. Currently, agents must guess the schema from tool descriptions or read large static resources.

## Requirements

Implement a new MCP tool called `get_chart_type_schema` that:

1. **Returns JSON Schema for a specific chart type**
   - Supported chart types: `xy`, `table`, `pie`, `pivot_table`, `mixed_timeseries`, `handlebars`, `big_number`
   - Each chart type has a corresponding Pydantic model in `superset.mcp_service.chart.schemas`
   - Use `pydantic.TypeAdapter` to generate JSON schemas at runtime

2. **Accepts parameters:**
   - `chart_type` (str): The chart type to get schema for
   - `include_examples` (bool, default True): Whether to include example configurations

3. **Returns structure:**
   - For valid chart types: `{"chart_type": str, "schema": dict, "examples": list}` (examples omitted if `include_examples=False`)
   - For invalid chart types: `{"error": str, "valid_chart_types": list, "hint": str}`

4. **Follows MCP service conventions:**
   - Use the `@tool` decorator from `superset_core.mcp.decorators`
   - Include `tags=["discovery"]` and appropriate `ToolAnnotations`
   - Add Apache license header (see existing files for format)
   - Create the file at `superset/mcp_service/chart/tool/get_chart_type_schema.py`

5. **Integration:**
   - Import and re-export the tool in `superset/mcp_service/chart/tool/__init__.py`
   - Add the import to `superset/mcp_service/app.py` (around line 430-435 where other chart tools are imported)

## Key Files to Modify

- `superset/mcp_service/chart/tool/get_chart_type_schema.py` (new file)
- `superset/mcp_service/chart/tool/__init__.py` (add import and export)
- `superset/mcp_service/app.py` (add import for auto-registration)

## Reference

Look at existing chart tools in `superset/mcp_service/chart/tool/` for patterns:
- `get_chart_info.py` shows the @tool decorator pattern
- `list_charts.py` shows return type patterns

The schema models are defined in `superset.mcp_service.chart.schemas`:
- `XYChartConfig`, `TableChartConfig`, `PieChartConfig`, etc.

Read `superset/mcp_service/CLAUDE.md` for detailed conventions on:
- Tool registration patterns
- Apache license header requirements
- Type hint conventions (use `T | None` instead of `Optional[T]`)
