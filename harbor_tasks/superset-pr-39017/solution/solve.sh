#!/bin/bash
# Gold solution: Apply the fix for adding certification fields to MCP list tools
set -e

cd /workspace/superset

# Idempotency check: skip if already applied
if grep -q '"certified_by"' superset/mcp_service/chart/tool/list_charts.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

echo "Applying certification fields fix..."

# Use Python for all modifications to avoid sed line matching issues
python3 << 'PYEOF'
import re

# 1. Update chart/schemas.py
with open("superset/mcp_service/chart/schemas.py", "r") as f:
    content = f.read()

# Add to ChartLike Protocol (after query_context line)
content = content.replace(
    "    query_context: Any | None\n    changed_by: Any | None",
    "    query_context: Any | None\n    certified_by: str | None\n    certification_details: str | None\n    changed_by: Any | None"
)

# Add to ChartInfo class (after created_on_humanized field)
old_chartinfo = '''    created_on_humanized: str | None = Field(
        None, description="Humanized creation time"
    )
    uuid: str | None = Field(None, description="Chart UUID")'''
new_chartinfo = '''    created_on_humanized: str | None = Field(
        None, description="Humanized creation time"
    )
    certified_by: str | None = Field(
        None, description="Name of the person or team who certified this chart"
    )
    certification_details: str | None = Field(
        None, description="Certification details or reason"
    )
    uuid: str | None = Field(None, description="Chart UUID")'''
content = content.replace(old_chartinfo, new_chartinfo)

# Add to serialize_chart_object (after description line)
content = content.replace(
    '        description=getattr(chart, "description", None),\n        cache_timeout',
    '        description=getattr(chart, "description", None),\n        certified_by=getattr(chart, "certified_by", None),\n        certification_details=getattr(chart, "certification_details", None),\n        cache_timeout'
)

with open("superset/mcp_service/chart/schemas.py", "w") as f:
    f.write(content)
print("Updated chart/schemas.py")

# 2. Update chart/tool/list_charts.py
with open("superset/mcp_service/chart/tool/list_charts.py", "r") as f:
    content = f.read()

# Find the DEFAULT_CHART_COLUMNS list and add new fields
old_default = '''    "id",
    "slice_name",
    "viz_type",
    "url",
    "changed_on",
    "changed_on_humanized",
]'''
new_default = '''    "id",
    "slice_name",
    "viz_type",
    "description",
    "certified_by",
    "certification_details",
    "url",
    "changed_on",
    "changed_on_humanized",
]'''
content = content.replace(old_default, new_default)

with open("superset/mcp_service/chart/tool/list_charts.py", "w") as f:
    f.write(content)
print("Updated chart/tool/list_charts.py")

# 3. Update schema_discovery.py
with open("superset/mcp_service/common/schema_discovery.py", "r") as f:
    content = f.read()

# Replace CHART_DEFAULT_COLUMNS
old_chart = 'CHART_DEFAULT_COLUMNS = ["id", "slice_name", "viz_type", "url", "changed_on_humanized"]'
new_chart = '''CHART_DEFAULT_COLUMNS = [
    "id",
    "slice_name",
    "viz_type",
    "description",
    "certified_by",
    "certification_details",
    "url",
    "changed_on",
    "changed_on_humanized",
]'''
content = content.replace(old_chart, new_chart)

# Replace DATASET_DEFAULT_COLUMNS
old_dataset = 'DATASET_DEFAULT_COLUMNS = ["id", "table_name", "schema", "changed_on_humanized"]'
new_dataset = '''DATASET_DEFAULT_COLUMNS = [
    "id",
    "table_name",
    "schema",
    "description",
    "certified_by",
    "certification_details",
    "changed_on",
    "changed_on_humanized",
]'''
content = content.replace(old_dataset, new_dataset)

# Update DASHBOARD_DEFAULT_COLUMNS
old_dash = '''"id",
    "dashboard_title",
    "slug",
    "url",
    "changed_on_humanized",
]
DASHBOARD_SORTABLE_COLUMNS'''
new_dash = '''"id",
    "dashboard_title",
    "slug",
    "description",
    "certified_by",
    "certification_details",
    "url",
    "changed_on",
    "changed_on_humanized",
]
DASHBOARD_SORTABLE_COLUMNS'''
content = content.replace(old_dash, new_dash)

# Add certified_by and certification_details to CHART_EXTRA_COLUMNS
old_chart_extra = '''    "tags": ColumnMetadata(
        name="tags", description="Chart tags", type="list", is_default=False
    ),'''
new_chart_extra = '''    "certified_by": ColumnMetadata(
        name="certified_by",
        description="Name of the person who certified this chart",
        type="str",
        is_default=True,
    ),
    "certification_details": ColumnMetadata(
        name="certification_details",
        description="Certification details or reason",
        type="str",
        is_default=True,
    ),
    "tags": ColumnMetadata(
        name="tags", description="Chart tags", type="list", is_default=False
    ),'''
content = content.replace(old_chart_extra, new_chart_extra)

# Add certified_by and certification_details to DATASET_EXTRA_COLUMNS
old_dataset_extra = '''    "metrics": ColumnMetadata(
        name="metrics",
        description="Dataset metrics definitions",'''
new_dataset_extra = '''    "certified_by": ColumnMetadata(
        name="certified_by",
        description="Name of the person who certified this dataset",
        type="str",
        is_default=True,
    ),
    "certification_details": ColumnMetadata(
        name="certification_details",
        description="Certification details or reason",
        type="str",
        is_default=True,
    ),
    "metrics": ColumnMetadata(
        name="metrics",
        description="Dataset metrics definitions",'''
content = content.replace(old_dataset_extra, new_dataset_extra)

with open("superset/mcp_service/common/schema_discovery.py", "w") as f:
    f.write(content)
print("Updated common/schema_discovery.py")

# 4. Update dashboard/tool/list_dashboards.py
with open("superset/mcp_service/dashboard/tool/list_dashboards.py", "r") as f:
    content = f.read()

old_dash_default = '''    "id",
    "dashboard_title",
    "slug",
    "url",
    "changed_on",
    "changed_on_humanized",
]'''
new_dash_default = '''    "id",
    "dashboard_title",
    "slug",
    "description",
    "certified_by",
    "certification_details",
    "url",
    "changed_on",
    "changed_on_humanized",
]'''
content = content.replace(old_dash_default, new_dash_default)

with open("superset/mcp_service/dashboard/tool/list_dashboards.py", "w") as f:
    f.write(content)
print("Updated dashboard/tool/list_dashboards.py")

# 5. Update dataset/schemas.py
with open("superset/mcp_service/dataset/schemas.py", "r") as f:
    content = f.read()

# Add to DatasetInfo class
old_dataset_info = '''    description: str | None = Field(None, description="Dataset description")
    changed_by: str | None = Field'''
new_dataset_info = '''    description: str | None = Field(None, description="Dataset description")
    certified_by: str | None = Field(
        None, description="Name of the person or team who certified this dataset"
    )
    certification_details: str | None = Field(
        None, description="Certification details or reason"
    )
    changed_by: str | None = Field'''
content = content.replace(old_dataset_info, new_dataset_info)

# Add to serialize_dataset_object
content = content.replace(
    '        description=getattr(dataset, "description", None),\n        changed_by',
    '        description=getattr(dataset, "description", None),\n        certified_by=getattr(dataset, "certified_by", None),\n        certification_details=getattr(dataset, "certification_details", None),\n        changed_by'
)

with open("superset/mcp_service/dataset/schemas.py", "w") as f:
    f.write(content)
print("Updated dataset/schemas.py")

# 6. Update dataset/tool/list_datasets.py
with open("superset/mcp_service/dataset/tool/list_datasets.py", "r") as f:
    content = f.read()

old_dataset_cols = '''DEFAULT_DATASET_COLUMNS = [
    "id",
    "table_name",
    "schema",
    "changed_on",
    "changed_on_humanized",
]'''
new_dataset_cols = '''DEFAULT_DATASET_COLUMNS = [
    "id",
    "table_name",
    "schema",
    "description",
    "certified_by",
    "certification_details",
    "changed_on",
    "changed_on_humanized",
]'''
content = content.replace(old_dataset_cols, new_dataset_cols)

with open("superset/mcp_service/dataset/tool/list_datasets.py", "w") as f:
    f.write(content)
print("Updated dataset/tool/list_datasets.py")

# 7. Update mcp_core.py
with open("superset/mcp_service/mcp_core.py", "r") as f:
    content = f.read()

# Update the columns_to_load assignment to make a mutable list
content = content.replace(
    "            columns_to_load = select_columns\n",
    "            columns_to_load = list(select_columns)\n"
)
content = content.replace(
    "            columns_to_load = self.default_columns\n",
    "            columns_to_load = list(self.default_columns)\n"
)

# Add computed column dependencies logic
old_code = '''            columns_requested = self.default_columns
        # Query the DAO'''
new_code = '''            columns_requested = self.default_columns

        # Ensure computed columns have their dependencies loaded.
        # Humanized timestamps are derived from their raw counterparts —
        # if the raw column isn't loaded, the serializer produces null.
        computed_deps: dict[str, str] = {
            "changed_on_humanized": "changed_on",
            "created_on_humanized": "created_on",
        }
        for computed, dependency in computed_deps.items():
            if computed in columns_to_load and dependency not in columns_to_load:
                columns_to_load.append(dependency)

        # Query the DAO'''
content = content.replace(old_code, new_code)

with open("superset/mcp_service/mcp_core.py", "w") as f:
    f.write(content)
print("Updated mcp_core.py")

print("All files updated successfully!")
PYEOF

echo "Patch applied successfully."
