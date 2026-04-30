#!/bin/bash
# Gold solution for superset-mcp-chart-type-schema task
set -e

cd /workspace/superset

# Check if fix already applied (idempotency)
if grep -q "get_chart_type_schema" superset/mcp_service/chart/tool/__init__.py 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/superset/mcp_service/app.py b/superset/mcp_service/app.py
index fc9df494ab96..9a014915a7d2 100644
--- a/superset/mcp_service/app.py
+++ b/superset/mcp_service/app.py
@@ -430,6 +430,7 @@ def create_mcp_app(
     get_chart_data,
     get_chart_info,
     get_chart_preview,
+    get_chart_type_schema,
     list_charts,
     update_chart,
     update_chart_preview,
diff --git a/superset/mcp_service/chart/tool/__init__.py b/superset/mcp_service/chart/tool/__init__.py
index a3c8388a75c4..0ad428528699 100644
--- a/superset/mcp_service/chart/tool/__init__.py
+++ b/superset/mcp_service/chart/tool/__init__.py
@@ -19,6 +19,7 @@
 from .get_chart_data import get_chart_data
 from .get_chart_info import get_chart_info
 from .get_chart_preview import get_chart_preview
+from .get_chart_type_schema import get_chart_type_schema
 from .list_charts import list_charts
 from .update_chart import update_chart
 from .update_chart_preview import update_chart_preview
@@ -31,4 +32,5 @@
     "update_chart_preview",
     "get_chart_preview",
     "get_chart_data",
+    "get_chart_type_schema",
 ]
diff --git a/superset/mcp_service/chart/tool/get_chart_type_schema.py b/superset/mcp_service/chart/tool/get_chart_type_schema.py
new file mode 100644
index 000000000000..dc21f3c62035
--- /dev/null
+++ b/superset/mcp_service/chart/tool/get_chart_type_schema.py
@@ -0,0 +1,174 @@
+# Licensed to the Apache Software Foundation (ASF) under one
+# or more contributor license agreements.  See the NOTICE file
+# distributed with this work for additional information
+# regarding copyright ownership.  The ASF licenses this file
+# to you under the Apache License, Version 2.0 (the
+# "License"); you may not use this file except in compliance
+# with the License.  You may obtain a copy of the License at
+#
+#   http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing,
+# software distributed under the License is distributed on an
+# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+# KIND, either express or implied.  See the License for the
+# specific language governing permissions and limitations
+# under the License.
+
+"""
+MCP tool: get_chart_type_schema
+"""
+
+from __future__ import annotations
+
+import logging
+from typing import Any, Dict
+
+from pydantic import TypeAdapter
+from superset_core.mcp.decorators import tool, ToolAnnotations
+
+from superset.mcp_service.chart.schemas import (
+    BigNumberChartConfig,
+    HandlebarsChartConfig,
+    MixedTimeseriesChartConfig,
+    PieChartConfig,
+    PivotTableChartConfig,
+    TableChartConfig,
+    XYChartConfig,
+)
+
+logger = logging.getLogger(__name__)
+
+# Module-level TypeAdapters — one per chart type, compiled once.
+_CHART_TYPE_ADAPTERS: Dict[str, TypeAdapter[Any]] = {
+    "xy": TypeAdapter(XYChartConfig),
+    "table": TypeAdapter(TableChartConfig),
+    "pie": TypeAdapter(PieChartConfig),
+    "pivot_table": TypeAdapter(PivotTableChartConfig),
+    "mixed_timeseries": TypeAdapter(MixedTimeseriesChartConfig),
+    "handlebars": TypeAdapter(HandlebarsChartConfig),
+    "big_number": TypeAdapter(BigNumberChartConfig),
+}
+
+VALID_CHART_TYPES = sorted(_CHART_TYPE_ADAPTERS.keys())
+
+# Per-type examples — lightweight inline examples for each chart type.
+_CHART_EXAMPLES: Dict[str, list[Dict[str, Any]]] = {
+    "xy": [
+        {
+            "chart_type": "xy",
+            "kind": "line",
+            "x": {"name": "order_date"},
+            "y": [{"name": "revenue", "aggregate": "SUM"}],
+            "time_grain": "P1D",
+        },
+        {
+            "chart_type": "xy",
+            "kind": "bar",
+            "x": {"name": "category"},
+            "y": [{"name": "sales", "aggregate": "SUM"}],
+        },
+    ],
+    "table": [
+        {
+            "chart_type": "table",
+            "columns": [
+                {"name": "customer_name"},
+                {"name": "revenue", "aggregate": "SUM"},
+            ],
+        },
+    ],
+    "pie": [
+        {
+            "chart_type": "pie",
+            "dimension": {"name": "region"},
+            "metric": {"name": "revenue", "aggregate": "SUM"},
+        },
+    ],
+    "pivot_table": [
+        {
+            "chart_type": "pivot_table",
+            "rows": [{"name": "region"}],
+            "metrics": [{"name": "revenue", "aggregate": "SUM"}],
+            "columns": [{"name": "quarter"}],
+        },
+    ],
+    "mixed_timeseries": [
+        {
+            "chart_type": "mixed_timeseries",
+            "x": {"name": "order_date"},
+            "y": [{"name": "revenue", "aggregate": "SUM"}],
+            "y_secondary": [{"name": "orders", "aggregate": "COUNT"}],
+            "time_grain": "P1M",
+        },
+    ],
+    "handlebars": [
+        {
+            "chart_type": "handlebars",
+            "query_mode": "raw",
+            "columns": [{"name": "customer_name"}, {"name": "email"}],
+            "handlebars_template": "{{#each data}}<p>{{customer_name}}</p>{{/each}}",
+        },
+    ],
+    "big_number": [
+        {
+            "chart_type": "big_number",
+            "metric": {"name": "revenue", "aggregate": "SUM"},
+        },
+    ],
+}
+
+
+def _get_chart_type_schema_impl(
+    chart_type: str,
+    include_examples: bool = True,
+) -> Dict[str, Any]:
+    """Pure logic for chart type schema lookup — no auth, no decorators."""
+    adapter = _CHART_TYPE_ADAPTERS.get(chart_type)
+    if adapter is None:
+        return {
+            "error": f"Unknown chart_type: {chart_type!r}",
+            "valid_chart_types": VALID_CHART_TYPES,
+            "hint": (
+                "Use one of the valid chart_type values listed above. "
+                "Call this tool again with a valid chart_type to see "
+                "its schema and examples."
+            ),
+        }
+
+    schema = adapter.json_schema()
+    result: Dict[str, Any] = {
+        "chart_type": chart_type,
+        "schema": schema,
+    }
+
+    if include_examples:
+        result["examples"] = _CHART_EXAMPLES.get(chart_type, [])
+
+    return result
+
+
+@tool(
+    tags=["discovery"],
+    annotations=ToolAnnotations(
+        title="Get chart type schema",
+        readOnlyHint=True,
+        destructiveHint=False,
+    ),
+)
+def get_chart_type_schema(
+    chart_type: str,
+    include_examples: bool = True,
+) -> Dict[str, Any]:
+    """Get the full JSON Schema and examples for a specific chart type.
+
+    Use this tool to discover the exact fields, types, and constraints
+    for a chart configuration before calling generate_chart or update_chart.
+
+    Valid chart_type values: xy, table, pie, pivot_table,
+    mixed_timeseries, handlebars, big_number.
+
+    Returns the JSON Schema for the requested chart type, optionally
+    with working examples.
+    """
+    return _get_chart_type_schema_impl(chart_type, include_examples)
diff --git a/tests/unit_tests/mcp_service/chart/tool/test_get_chart_type_schema.py b/tests/unit_tests/mcp_service/chart/tool/test_get_chart_type_schema.py
new file mode 100644
index 000000000000..f7f2d166a5ae
--- /dev/null
+++ b/tests/unit_tests/mcp_service/chart/tool/test_get_chart_type_schema.py
@@ -0,0 +1,86 @@
+# Licensed to the Apache Software Foundation (ASF) under one
+# or more contributor license agreements.  See the NOTICE file
+# distributed with this work for additional information
+# regarding copyright ownership.  The ASF licenses this file
+# to you under the Apache License, Version 2.0 (the
+# "License"); you may not use this file except in compliance
+# with the License.  You may obtain a copy of the License at
+#
+#   http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing,
+# software distributed under the License is distributed on an
+# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+# KIND, either express or implied.  See the License for the
+# specific language governing permissions and limitations
+# under the License.
+
+"""Tests for get_chart_type_schema tool logic."""
+
+import pytest
+
+from superset.mcp_service.chart.tool.get_chart_type_schema import (
+    _CHART_EXAMPLES,
+    _get_chart_type_schema_impl as _call_schema,
+    VALID_CHART_TYPES,
+)
+
+
+class TestGetChartTypeSchema:
+    @pytest.mark.parametrize("chart_type", VALID_CHART_TYPES)
+    def test_valid_chart_type_returns_schema(self, chart_type: str) -> None:
+        result = _call_schema(chart_type)
+        assert "schema" in result
+        assert result["chart_type"] == chart_type
+        assert isinstance(result["schema"], dict)
+        assert "properties" in result["schema"]
+        assert "examples" in result
+
+    def test_xy_schema_has_expected_fields(self) -> None:
+        result = _call_schema("xy")
+        props = result["schema"]["properties"]
+        assert "x" in props
+        assert "y" in props
+        assert "kind" in props
+
+    def test_table_schema_has_columns(self) -> None:
+        result = _call_schema("table")
+        props = result["schema"]["properties"]
+        assert "columns" in props
+
+    def test_pie_schema_has_dimension_metric(self) -> None:
+        result = _call_schema("pie")
+        props = result["schema"]["properties"]
+        assert "dimension" in props
+        assert "metric" in props
+
+    def test_big_number_schema_has_metric(self) -> None:
+        result = _call_schema("big_number")
+        props = result["schema"]["properties"]
+        assert "metric" in props
+
+    def test_include_examples_false_omits_examples(self) -> None:
+        result = _call_schema("xy", include_examples=False)
+        assert "schema" in result
+        assert "examples" not in result
+
+    def test_invalid_chart_type_returns_error(self) -> None:
+        result = _call_schema("nonexistent")
+        assert "error" in result
+        assert "valid_chart_types" in result
+        assert result["valid_chart_types"] == VALID_CHART_TYPES
+
+    def test_examples_match_chart_type(self) -> None:
+        result = _call_schema("pie")
+        for example in result["examples"]:
+            assert example["chart_type"] == "pie"
+
+    def test_valid_chart_types_constant(self) -> None:
+        assert len(VALID_CHART_TYPES) == 7
+        assert "xy" in VALID_CHART_TYPES
+        assert "table" in VALID_CHART_TYPES
+
+    def test_all_chart_types_have_examples(self) -> None:
+        for chart_type in VALID_CHART_TYPES:
+            assert chart_type in _CHART_EXAMPLES
+            assert len(_CHART_EXAMPLES[chart_type]) >= 1
PATCH

echo "Gold patch applied successfully"
