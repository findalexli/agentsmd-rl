#!/bin/bash
set -e

# Apply the gold patch for apache/superset#38990
# This fixes table chart raw mode handling and dashboard title XSS

cd /workspace/superset

# Check if already applied
distinctive_line='Include both "all_columns" (Superset table viz) and "columns"'
if grep -q "$distinctive_line" superset/mcp_service/chart/chart_utils.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
cat <<'PATCH' | git apply --check && git apply -
diff --git a/superset/mcp_service/chart/chart_utils.py b/superset/mcp_service/chart/chart_utils.py
index b4fdfd3b13ec..b5e2d6b0a090 100644
--- a/superset/mcp_service/chart/chart_utils.py
+++ b/superset/mcp_service/chart/chart_utils.py
@@ -412,9 +412,12 @@ def map_table_config(config: TableChartConfig) -> Dict[str, Any]:
     # Handle raw columns (no aggregation)
     if raw_columns and not aggregated_metrics:
         # Pure raw columns - show individual rows
+        # Include both "all_columns" (Superset table viz) and "columns"
+        # (QueryContextFactory validation) to avoid "Empty query?" errors
         form_data.update(
             {
                 "all_columns": raw_columns,
+                "columns": raw_columns,
                 "query_mode": "raw",
                 "include_time": False,
                 "order_desc": True,
diff --git a/superset/mcp_service/chart/preview_utils.py b/superset/mcp_service/chart/preview_utils.py
index d46865c9d137..d585e3cda991 100644
--- a/superset/mcp_service/chart/preview_utils.py
+++ b/superset/mcp_service/chart/preview_utils.py
@@ -39,6 +39,12 @@

 def _build_query_columns(form_data: Dict[str, Any]) -> list[str]:
     """Build query columns list from form_data, including both x_axis and groupby."""
+    # Table charts in raw mode use all_columns or columns
+    all_columns = form_data.get("all_columns", [])
+    raw_columns_field = form_data.get("columns", [])
+    if form_data.get("query_mode") == "raw" and (all_columns or raw_columns_field):
+        return list(all_columns or raw_columns_field)
+
     x_axis_config = form_data.get("x_axis")
     groupby_columns: list[str] = form_data.get("groupby") or []
     raw_columns: list[str] = form_data.get("columns") or []
diff --git a/superset/mcp_service/chart/tool/get_chart_preview.py b/superset/mcp_service/chart/tool/get_chart_preview.py
index 548898e03b47..3f36d5378c20 100644
--- a/superset/mcp_service/chart/tool/get_chart_preview.py
+++ b/superset/mcp_service/chart/tool/get_chart_preview.py
@@ -133,12 +133,18 @@ def generate(self) -> ASCIIPreview | ChartError:
             groupby_columns = form_data.get("groupby", [])
             metrics = form_data.get("metrics", [])

-            columns = groupby_columns.copy()
-            if x_axis_config and isinstance(x_axis_config, str):
-                columns.append(x_axis_config)
-            elif x_axis_config and isinstance(x_axis_config, dict):
-                if "column_name" in x_axis_config:
-                    columns.append(x_axis_config["column_name"])
+            # Table charts in raw mode use all_columns or columns
+            all_columns = form_data.get("all_columns", [])
+            raw_columns = form_data.get("columns", [])
+            if form_data.get("query_mode") == "raw" and (all_columns or raw_columns):
+                columns = list(all_columns or raw_columns)
+            else:
+                columns = groupby_columns.copy()
+                if x_axis_config and isinstance(x_axis_config, str):
+                    columns.append(x_axis_config)
+                elif x_axis_config and isinstance(x_axis_config, dict):
+                    if "column_name" in x_axis_config:
+                        columns.append(x_axis_config["column_name"])

             factory = QueryContextFactory()
             query_context = factory.create(
diff --git a/superset/mcp_service/dashboard/schemas.py b/superset/mcp_service/dashboard/schemas.py
index be2860e07cbe..6f7f716849d1 100644
--- a/superset/mcp_service/dashboard/schemas.py
+++ b/superset/mcp_service/dashboard/schemas.py
@@ -93,6 +93,10 @@ from superset.mcp_service.utils.metadata import (
     TagInfo,
     UserInfo,
 )
+from superset.mcp_service.utils.sanitization import (
+    _remove_dangerous_unicode,
+    _strip_html_tags,
+)


 class DashboardError(BaseModel):
@@ -448,6 +452,16 @@ class GenerateDashboardRequest(BaseModel):
         default=True, description="Whether to publish the dashboard"
     )

+    @field_validator("dashboard_title")
+    @classmethod
+    def sanitize_dashboard_title(cls, v: str | None) -> str | None:
+        """Strip HTML tags from dashboard title to prevent XSS."""
+        if v is None:
+            return None
+        v = _strip_html_tags(v.strip())
+        v = _remove_dangerous_unicode(v)
+        return v

 class GenerateDashboardResponse(BaseModel):
     """Response schema for dashboard generation."""
PATCH

echo "Patch applied successfully"
