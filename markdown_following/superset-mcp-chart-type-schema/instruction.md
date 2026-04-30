# Add MCP Tool for Chart Type Schema Discovery

## Problem

The Superset MCP (Model Context Protocol) service currently lacks a way for AI assistants to discover the exact JSON Schema for specific chart types on demand.

When an agent wants to create or update a chart, it needs to know the exact fields, types, and constraints for that chart type's configuration. Currently, agents must either:
1. Read the entire `chart://configs` resource (a static blob with all chart types)
2. Guess the schema from tool descriptions

This is inefficient — agents often only need the schema for a single chart type.

## Task

Implement a new `get_chart_type_schema` MCP tool in `superset/mcp_service/chart/tool/get_chart_type_schema.py`.

You will also need to:
- Export the tool from `superset/mcp_service/chart/tool/__init__.py` (import it and add it to `__all__`)
- Import the tool in `superset/mcp_service/app.py` for automatic MCP registration

## Module Layout

The module must define the following symbols:

### 1. `_CHART_TYPE_ADAPTERS` dict

Define a module-level dict variable named `_CHART_TYPE_ADAPTERS` with type `Dict[str, TypeAdapter]` that maps chart type strings to `TypeAdapter` instances. Import `TypeAdapter` from `pydantic` using the import statement `from pydantic import TypeAdapter`.

| Chart type key | Config class (from `superset.mcp_service.chart.schemas`) |
|---|---|
| `"xy"` | `XYChartConfig` |
| `"table"` | `TableChartConfig` |
| `"pie"` | `PieChartConfig` |
| `"pivot_table"` | `PivotTableChartConfig` |
| `"mixed_timeseries"` | `MixedTimeseriesChartConfig` |
| `"handlebars"` | `HandlebarsChartConfig` |
| `"big_number"` | `BigNumberChartConfig` |

Each dict value must be `TypeAdapter(<ConfigClass>)`. For example:
- The `"xy"` entry must use `TypeAdapter(XYChartConfig)`
- The `"pie"` entry must use `TypeAdapter(PieChartConfig)`
- And similarly for the other five chart types

### 2. `VALID_CHART_TYPES` constant

Define a constant named `VALID_CHART_TYPES` as a sorted list of the keys from `_CHART_TYPE_ADAPTERS`.

### 3. `_CHART_EXAMPLES` dict

Define a module-level dict variable named `_CHART_EXAMPLES` that maps each chart type string to a list of example configuration dicts. Every example dict must include a `"chart_type"` field whose value matches the chart type string. Specifically, the examples must contain entries matching these patterns:
- `"chart_type": "xy"` in the xy examples
- `"chart_type": "table"` in the table examples
- `"chart_type": "pie"` in the pie examples
- `"chart_type": "pivot_table"` in the pivot_table examples
- `"chart_type": "mixed_timeseries"` in the mixed_timeseries examples
- `"chart_type": "handlebars"` in the handlebars examples
- `"chart_type": "big_number"` in the big_number examples

### 4. `_get_chart_type_schema_impl` function

Define a function named `_get_chart_type_schema_impl` with this signature:

```python
def _get_chart_type_schema_impl(
    chart_type: str,
    include_examples: bool = True,
) -> Dict[str, Any]:
```

Core logic (no auth, no decorators):

- Look up `chart_type` in `_CHART_TYPE_ADAPTERS`. If the adapter is `None` (i.e., the code must contain the check `adapter is None`), return an error response (see below).
- Otherwise call `adapter.json_schema()` to produce the JSON Schema.
- Build a result dict containing `"chart_type"` and `"schema"` keys.
- Conditionally add an `"examples"` key (from `_CHART_EXAMPLES`) using `if include_examples`.

### 5. `get_chart_type_schema` public function

Define a public function named `get_chart_type_schema` that is the MCP-facing function, decorated with `@tool`, and delegates to `_get_chart_type_schema_impl`. It must have a meaningful docstring (more than 20 characters).

## Response Schemas

### Valid chart type response

The successful response dict must contain these keys:
- `"chart_type"` — the requested chart type string
- `"schema"` — the JSON Schema object produced by calling `json_schema()` on the adapter
- `"examples"` — list of example dicts (only included when `include_examples` is `True`)

### Invalid chart type error response

When the chart type is not found (adapter is `None`), return a dict with these keys:
- `"error"` — a descriptive error message
- `"valid_chart_types"` — the sorted list of valid chart type strings (i.e., `VALID_CHART_TYPES`)
- `"hint"` — a suggestion for the caller

## Tool Metadata

Import both `tool` and `ToolAnnotations` from `superset_core.mcp.decorators`. Apply `ToolAnnotations` to the decorated function with `readOnlyHint=True` and `destructiveHint=False`.

## Code Style

- Include the Apache License header (must reference "Licensed to the Apache Software Foundation" and "Apache License, Version 2.0").
- Follow the MCP service conventions described in `superset/mcp_service/CLAUDE.md`.
- The resulting code must pass `ruff check` and `ruff format --check`.
