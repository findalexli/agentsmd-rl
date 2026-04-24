# MCP List Tools Missing Certification Information

The MCP (Model Context Protocol) service provides tools for AI assistants to browse Superset assets. When users call `list_charts`, `list_dashboards`, or `list_datasets`, they receive a response with basic asset information.

## Problem

The current list tool responses are missing key information that AI assistants need to identify **certified, trusted assets**:

1. **Certification status is unavailable** - The `certified_by` and `certification_details` fields exist on the database models but are not included in the list tool default columns. This forces N+1 roundtrips when an LLM needs to check which assets are certified.

2. **Description is missing from defaults** - Asset descriptions are not returned by default, making it harder for AI assistants to understand what each asset contains.

3. **Schema discovery inconsistency** - The `schema_discovery.py` default columns don't match the list tool defaults, causing `get_schema().default_select` to return inconsistent information.

## Files to Investigate

- `superset/mcp_service/chart/tool/list_charts.py` - Chart list tool (contains `DEFAULT_CHART_COLUMNS`)
- `superset/mcp_service/dashboard/tool/list_dashboards.py` - Dashboard list tool (contains default columns list)
- `superset/mcp_service/dataset/tool/list_datasets.py` - Dataset list tool (contains `DEFAULT_DATASET_COLUMNS`)
- `superset/mcp_service/common/schema_discovery.py` - Default column definitions
- `superset/mcp_service/chart/schemas.py` - `ChartInfo` Pydantic schema and `serialize_chart_object` function
- `superset/mcp_service/dataset/schemas.py` - `DatasetInfo` Pydantic schema and `serialize_dataset_object` function

## Expected Behavior

After the fix:

### Schema Discovery (`schema_discovery.py`)

The following module-level lists must include `"certified_by"`, `"certification_details"`, and `"description"` as entries:
- `CHART_DEFAULT_COLUMNS`
- `DATASET_DEFAULT_COLUMNS`
- `DASHBOARD_DEFAULT_COLUMNS`

The following module-level dicts must include `"certified_by"` and `"certification_details"` as keys:
- `CHART_EXTRA_COLUMNS`
- `DATASET_EXTRA_COLUMNS`

### List Tool Default Columns

The default columns constants in each list tool must include `"certified_by"` and `"certification_details"`:
- `DEFAULT_CHART_COLUMNS` in `list_charts.py`
- `DEFAULT_DATASET_COLUMNS` in `list_datasets.py`
- The default columns list in `list_dashboards.py`

### Pydantic Schemas

- The `ChartInfo` Pydantic model in `chart/schemas.py` must have `certified_by` and `certification_details` fields
- The `DatasetInfo` Pydantic model in `dataset/schemas.py` must have `certified_by` and `certification_details` fields

### Serializers

The serializer functions must extract certification fields from model objects using `getattr()`:

- `serialize_chart_object` in `chart/schemas.py` must include `certified_by=getattr(chart, "certified_by", ...)` and `certification_details=getattr(chart, "certification_details", ...)` keyword arguments
- `serialize_dataset_object` in `dataset/schemas.py` must include `certified_by=getattr(dataset, "certified_by", ...)` and `certification_details=getattr(dataset, "certification_details", ...)` keyword arguments

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
