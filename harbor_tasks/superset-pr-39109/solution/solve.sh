#!/bin/bash
# Gold solution for apache/superset PR #39109
# Fixes: form_data null, dataset URL, ASCII preview, chart rename

set -e

cd /workspace/superset

# Idempotency check - skip if already patched
if grep -q "chart_form_data = None" superset/mcp_service/chart/schemas.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/mcp_service/chart/schemas.py b/superset/mcp_service/chart/schemas.py
index 143d60a422ff..3a840dc924c6 100644
--- a/superset/mcp_service/chart/schemas.py
+++ b/superset/mcp_service/chart/schemas.py
@@ -284,14 +284,25 @@ def serialize_chart_object(chart: ChartLike | None) -> ChartInfo | None:
     if not chart:
         return None

-    # Use the chart's native URL (explore URL) instead of screenshot URL
     from superset.mcp_service.utils.url_utils import get_superset_base_url
+    from superset.utils import json as utils_json

     chart_id = getattr(chart, "id", None)
     chart_url = None
     if chart_id:
         chart_url = f"{get_superset_base_url()}/explore/?slice_id={chart_id}"

+    # Parse form_data from the chart's params JSON string
+    chart_params = getattr(chart, "params", None)
+    chart_form_data = None
+    if chart_params and isinstance(chart_params, str):
+        try:
+            chart_form_data = utils_json.loads(chart_params)
+        except (TypeError, ValueError):
+            pass
+    elif isinstance(chart_params, dict):
+        chart_form_data = chart_params
+
     return ChartInfo(
         id=chart_id,
         slice_name=getattr(chart, "slice_name", None),
@@ -301,6 +312,7 @@ def serialize_chart_object(chart: ChartLike | None) -> ChartInfo | None:
         url=chart_url,
         description=getattr(chart, "description", None),
         cache_timeout=getattr(chart, "cache_timeout", None),
+        form_data=chart_form_data,
         changed_by=getattr(chart, "changed_by_name", None)
         or (str(chart.changed_by) if getattr(chart, "changed_by", None) else None),
         changed_by_name=getattr(chart, "changed_by_name", None),
@@ -1284,7 +1296,13 @@ class GenerateExploreLinkRequest(FormDataCacheControl):

 class UpdateChartRequest(QueryCacheControl):
     identifier: int | str = Field(..., description="Chart ID or UUID")
-    config: ChartConfig
+    config: ChartConfig | None = Field(
+        None,
+        description=(
+            "Chart configuration. Required for visualization changes. "
+            "Omit to only update the chart name."
+        ),
+    )
     chart_name: str | None = Field(
         None, description="Auto-generates if omitted", max_length=255
     )
diff --git a/superset/mcp_service/chart/tool/get_chart_preview.py b/superset/mcp_service/chart/tool/get_chart_preview.py
index 3f36d5378c20..df044dec5953 100644
--- a/superset/mcp_service/chart/tool/get_chart_preview.py
+++ b/superset/mcp_service/chart/tool/get_chart_preview.py
@@ -146,6 +146,16 @@ def generate(self) -> ASCIIPreview | ChartError:
                     if "column_name" in x_axis_config:
                         columns.append(x_axis_config["column_name"])

+            if not columns and not metrics:
+                return ChartError(
+                    error=(
+                        "Cannot generate ASCII preview: chart has no columns or "
+                        "metrics in its configuration. This chart type may not "
+                        "support ASCII preview."
+                    ),
+                    error_type="UnsupportedChart",
+                )
+
             factory = QueryContextFactory()
             query_context = factory.create(
                 datasource={
diff --git a/superset/mcp_service/chart/tool/update_chart.py b/superset/mcp_service/chart/tool/update_chart.py
index 767ef615f8b2..74878ddb2e9d 100644
--- a/superset/mcp_service/chart/tool/update_chart.py
+++ b/superset/mcp_service/chart/tool/update_chart.py
@@ -21,6 +21,7 @@

 import logging
 import time
+from typing import Any

 from fastmcp import Context
 from sqlalchemy.exc import SQLAlchemyError
@@ -46,6 +47,66 @@
 logger = logging.getLogger(__name__)


+def _find_chart(identifier: int | str) -> Any | None:
+    """Find a chart by numeric ID or UUID string."""
+    from superset.daos.chart import ChartDAO
+
+    if isinstance(identifier, int) or (
+        isinstance(identifier, str) and identifier.isdigit()
+    ):
+        chart_id = int(identifier) if isinstance(identifier, str) else identifier
+        return ChartDAO.find_by_id(chart_id)
+    return ChartDAO.find_by_id(identifier, id_column="uuid")
+
+
+def _build_update_payload(
+    request: UpdateChartRequest,
+    chart: Any,
+) -> dict[str, Any] | GenerateChartResponse:
+    """Build the update payload for a chart update.
+
+    Returns a dict payload on success, or a GenerateChartResponse error
+    when neither config nor chart_name is provided.
+    """
+    if request.config is not None:
+        dataset_id = chart.datasource_id if chart.datasource_id else None
+        new_form_data = map_config_to_form_data(request.config, dataset_id=dataset_id)
+        new_form_data.pop("_mcp_warnings", None)
+
+        chart_name = (
+            request.chart_name
+            if request.chart_name
+            else chart.slice_name or generate_chart_name(request.config)
+        )
+
+        return {
+            "slice_name": chart_name,
+            "viz_type": new_form_data["viz_type"],
+            "params": json.dumps(new_form_data),
+        }
+
+    # Name-only update: keep existing visualization, just rename
+    if not request.chart_name:
+        return GenerateChartResponse.model_validate(
+            {
+                "chart": None,
+                "error": {
+                    "error_type": "ValidationError",
+                    "message": ("Either 'config' or 'chart_name' must be provided."),
+                    "details": (
+                        "Either 'config' or 'chart_name' must be provided. "
+                        "Use config for visualization changes, chart_name "
+                        "for renaming."
+                    ),
+                },
+                "success": False,
+                "schema_version": "2.0",
+                "api_version": "v1",
+            }
+        )
+    return {"slice_name": request.chart_name}
+
+
 @tool(
     tags=["mutate"],
     class_permission_name="Chart",
@@ -105,29 +166,22 @@ async def update_chart(
     start_time = time.time()

     try:
-        # Find the existing chart
-        from superset.daos.chart import ChartDAO
-
         with event_logger.log_context(action="mcp.update_chart.chart_lookup"):
-            chart = None
-            if isinstance(request.identifier, int) or (
-                isinstance(request.identifier, str) and request.identifier.isdigit()
-            ):
-                chart_id = (
-                    int(request.identifier)
-                    if isinstance(request.identifier, str)
-                    else request.identifier
-                )
-                chart = ChartDAO.find_by_id(chart_id)
-            else:
-                # Try UUID lookup using DAO flexible method
-                chart = ChartDAO.find_by_id(request.identifier, id_column="uuid")
+            chart = _find_chart(request.identifier)

         if not chart:
             return GenerateChartResponse.model_validate(
                 {
                     "chart": None,
-                    "error": f"No chart found with identifier: {request.identifier}",
+                    "error": {
+                        "error_type": "NotFound",
+                        "message": (
+                            f"No chart found with identifier: {request.identifier}"
+                        ),
+                        "details": (
+                            f"No chart found with identifier: {request.identifier}"
+                        ),
+                    },
                     "success": False,
                     "schema_version": "2.0",
                     "api_version": "v1",
@@ -157,30 +211,15 @@ async def update_chart(
                 }
             )

-        # Map the new config to form_data format
-        # Get dataset_id from existing chart for column type checking
-        dataset_id = chart.datasource_id if chart.datasource_id else None
-        new_form_data = map_config_to_form_data(request.config, dataset_id=dataset_id)
-        new_form_data.pop("_mcp_warnings", None)
-
-        # Update chart using Superset's command
+        # Build update payload (config update or name-only rename)
         from superset.commands.chart.update import UpdateChartCommand

-        with event_logger.log_context(action="mcp.update_chart.db_write"):
-            # Generate new chart name if provided, otherwise keep existing
-            chart_name = (
-                request.chart_name
-                if request.chart_name
-                else chart.slice_name or generate_chart_name(request.config)
-            )
+        payload_or_error = _build_update_payload(request, chart)
+        if isinstance(payload_or_error, GenerateChartResponse):
+            return payload_or_error

-            update_payload = {
-                "slice_name": chart_name,
-                "viz_type": new_form_data["viz_type"],
-                "params": json.dumps(new_form_data),
-            }
-
-            command = UpdateChartCommand(chart.id, update_payload)
+        with event_logger.log_context(action="mcp.update_chart.db_write"):
+            command = UpdateChartCommand(chart.id, payload_or_error)
             updated_chart = command.run()

         # Generate semantic analysis
@@ -199,7 +238,11 @@ async def update_chart(
         chart_name = (
             updated_chart.slice_name
             if updated_chart and hasattr(updated_chart, "slice_name")
-            else generate_chart_name(request.config)
+            else (
+                generate_chart_name(request.config)
+                if request.config
+                else "Updated chart"
+            )
         )
         accessibility = AccessibilityMetadata(
             color_blind_safe=True,  # Would need actual analysis
@@ -288,7 +331,11 @@ async def update_chart(
         return GenerateChartResponse.model_validate(
             {
                 "chart": None,
-                "error": f"Chart update failed: {str(e)}",
+                "error": {
+                    "error_type": type(e).__name__,
+                    "message": f"Chart update failed: {e}",
+                    "details": str(e),
+                },
                 "performance": {
                     "query_duration_ms": execution_time,
                     "cache_status": "error",
diff --git a/superset/mcp_service/dataset/schemas.py b/superset/mcp_service/dataset/schemas.py
index 5ae92cdd6fb5..ef04e6e30402 100644
--- a/superset/mcp_service/dataset/schemas.py
+++ b/superset/mcp_service/dataset/schemas.py
@@ -324,6 +324,9 @@ def _humanize_timestamp(dt: datetime | None) -> str | None:
 def serialize_dataset_object(dataset: Any) -> DatasetInfo | None:
     if not dataset:
         return None
+
+    from superset.mcp_service.utils.url_utils import get_superset_base_url
+
     params = getattr(dataset, "params", None)
     if isinstance(params, str):
         try:
@@ -387,7 +390,12 @@ def serialize_dataset_object(dataset: Any) -> DatasetInfo | None:
         if getattr(dataset, "uuid", None)
         else None,
         schema_perm=getattr(dataset, "schema_perm", None),
-        url=getattr(dataset, "url", None),
+        url=(
+            f"{get_superset_base_url()}/tablemodelview/edit/"
+            f"{getattr(dataset, 'id', None)}"
+            if getattr(dataset, "id", None)
+            else None
+        ),
         sql=getattr(dataset, "sql", None),
         main_dttm_col=getattr(dataset, "main_dttm_col", None),
         offset=getattr(dataset, "offset", None),
diff --git a/tests/unit_tests/mcp_service/chart/tool/test_update_chart.py b/tests/unit_tests/mcp_service/chart/tool/test_update_chart.py
index 34724237a46c..0f9e3daabdbf 100644
--- a/tests/unit_tests/mcp_service/chart/tool/test_update_chart.py
+++ b/tests/unit_tests/mcp_service/chart/tool/test_update_chart.py
@@ -30,11 +30,16 @@
     AxisConfig,
     ColumnRef,
     FilterConfig,
+    GenerateChartResponse,
     LegendConfig,
     TableChartConfig,
     UpdateChartRequest,
     XYChartConfig,
 )
+from superset.mcp_service.chart.tool.update_chart import (
+    _build_update_payload,
+    _find_chart,
+)


 class TestUpdateChart:
@@ -293,29 +298,44 @@ async def test_update_chart_aggregation_functions(self):

     @pytest.mark.asyncio
     async def test_update_chart_error_responses(self):
-        """Test expected error response structures."""
+        """Test expected error response structures use ChartGenerationError."""
         # Chart not found error
-        error_response = {
-            "chart": None,
-            "error": "No chart found with identifier: 999",
-            "success": False,
-            "schema_version": "2.0",
-            "api_version": "v1",
-        }
-        assert error_response["success"] is False
-        assert error_response["chart"] is None
-        assert "chart found" in error_response["error"].lower()
+        error_response = GenerateChartResponse.model_validate(
+            {
+                "chart": None,
+                "error": {
+                    "error_type": "NotFound",
+                    "message": "No chart found with identifier: 999",
+                    "details": "No chart found with identifier: 999",
+                },
+                "success": False,
+                "schema_version": "2.0",
+                "api_version": "v1",
+            }
+        )
+        assert error_response.success is False
+        assert error_response.chart is None
+        assert error_response.error is not None
+        assert error_response.error.error_type == "NotFound"
+        assert "chart found" in error_response.error.message.lower()

         # General update error
-        update_error = {
-            "chart": None,
-            "error": "Chart update failed: Permission denied",
-            "success": False,
-            "schema_version": "2.0",
-            "api_version": "v1",
-        }
-        assert update_error["success"] is False
-        assert "failed" in update_error["error"].lower()
+        update_error = GenerateChartResponse.model_validate(
+            {
+                "chart": None,
+                "error": {
+                    "error_type": "ValueError",
+                    "message": "Chart update failed: Permission denied",
+                    "details": "Permission denied",
+                },
+                "success": False,
+                "schema_version": "2.0",
+                "api_version": "v1",
+            }
+        )
+        assert update_error.success is False
+        assert update_error.error is not None
+        assert "failed" in update_error.error.message.lower()

     @pytest.mark.asyncio
     async def test_chart_name_sanitization(self):
@@ -491,3 +511,220 @@ async def test_update_chart_dataset_not_found(
             error = result.structured_content["error"]
             assert error["error_type"] == "DatasetNotAccessible"
             assert "deleted" in error["message"]
+
+
+class TestFindChart:
+    """Tests for _find_chart helper."""
+
+    @patch("superset.daos.chart.ChartDAO.find_by_id")
+    def test_find_chart_by_numeric_id(self, mock_find):
+        """Numeric int identifier calls find_by_id with int."""
+        mock_chart = Mock()
+        mock_find.return_value = mock_chart
+
+        result = _find_chart(42)
+
+        mock_find.assert_called_once_with(42)
+        assert result is mock_chart
+
+    @patch("superset.daos.chart.ChartDAO.find_by_id")
+    def test_find_chart_by_numeric_string(self, mock_find):
+        """String-digit identifier is converted to int."""
+        mock_chart = Mock()
+        mock_find.return_value = mock_chart
+
+        result = _find_chart("123")
+
+        mock_find.assert_called_once_with(123)
+        assert result is mock_chart
+
+    @patch("superset.daos.chart.ChartDAO.find_by_id")
+    def test_find_chart_by_uuid(self, mock_find):
+        """Non-digit string identifier looks up by uuid column."""
+        mock_chart = Mock()
+        mock_find.return_value = mock_chart
+
+        uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
+        result = _find_chart(uuid)
+
+        mock_find.assert_called_once_with(uuid, id_column="uuid")
+        assert result is mock_chart
+
+    @patch("superset.daos.chart.ChartDAO.find_by_id")
+    def test_find_chart_returns_none(self, mock_find):
+        """Returns None when chart is not found."""
+        mock_find.return_value = None
+
+        result = _find_chart(999)
+
+        assert result is None
+
+
+class TestBuildUpdatePayload:
+    """Tests for _build_update_payload helper."""
+
+    def test_name_only_update(self):
+        """Name-only update returns a dict with just slice_name."""
+        request = UpdateChartRequest(
+            identifier=1,
+            chart_name="New Name",
+        )
+        chart = Mock()
+
+        result = _build_update_payload(request, chart)
+
+        assert isinstance(result, dict)
+        assert result == {"slice_name": "New Name"}
+
+    def test_error_when_no_config_and_no_name(self):
+        """Returns GenerateChartResponse error when neither config nor chart_name."""
+        request = UpdateChartRequest(identifier=1)
+        chart = Mock()
+
+        result = _build_update_payload(request, chart)
+
+        assert isinstance(result, GenerateChartResponse)
+        assert result.success is False
+        assert result.error is not None
+        assert result.error.error_type == "ValidationError"
+        assert "config" in result.error.message.lower()
+        assert "chart_name" in result.error.message.lower()
+
+    def test_config_update_uses_request_chart_name(self):
+        """When config and chart_name are both provided, uses chart_name."""
+        config = TableChartConfig(
+            chart_type="table",
+            columns=[ColumnRef(name="col1")],
+        )
+        request = UpdateChartRequest(
+            identifier=1,
+            config=config,
+            chart_name="My Custom Name",
+        )
+        chart = Mock()
+        chart.datasource_id = None  # Avoid dataset lookup
+
+        result = _build_update_payload(request, chart)
+
+        assert isinstance(result, dict)
+        assert result["slice_name"] == "My Custom Name"
+        assert "viz_type" in result
+        assert "params" in result
+
+    def test_config_update_keeps_existing_name(self):
+        """When config is provided but no chart_name, keeps existing slice_name."""
+        config = TableChartConfig(
+            chart_type="table",
+            columns=[ColumnRef(name="col1")],
+        )
+        request = UpdateChartRequest(identifier=1, config=config)
+        chart = Mock()
+        chart.datasource_id = None
+        chart.slice_name = "Existing Name"
+
+        result = _build_update_payload(request, chart)
+
+        assert isinstance(result, dict)
+        assert result["slice_name"] == "Existing Name"
+
+
+class TestUpdateChartNameOnly:
+    """Integration-style tests for name-only update via MCP tool."""
+
+    @patch(
+        "superset.mcp_service.auth.check_chart_data_access",
+        new_callable=Mock,
+    )
+    @patch(
+        "superset.commands.chart.update.UpdateChartCommand",
+        new_callable=Mock,
+    )
+    @patch("superset.daos.chart.ChartDAO.find_by_id", new_callable=Mock)
+    @patch("superset.db.session")
+    @pytest.mark.asyncio
+    async def test_name_only_update_success(
+        self,
+        mock_db_session,
+        mock_find_by_id,
+        mock_update_cmd_cls,
+        mock_check_access,
+        mcp_server,
+    ):
+        """Successful name-only update (identifier + chart_name, no config)."""
+        mock_chart = Mock()
+        mock_chart.id = 1
+        mock_chart.datasource_id = 10
+        mock_chart.slice_name = "Old Name"
+        mock_chart.viz_type = "table"
+        mock_chart.uuid = "abc-123"
+        mock_find_by_id.return_value = mock_chart
+
+        mock_check_access.return_value = DatasetValidationResult(
+            is_valid=True,
+            dataset_id=10,
+            dataset_name="my_dataset",
+            warnings=[],
+        )
+
+        updated_chart = Mock()
+        updated_chart.id = 1
+        updated_chart.slice_name = "Renamed Chart"
+        updated_chart.viz_type = "table"
+        updated_chart.uuid = "abc-123"
+        mock_update_cmd_cls.return_value.run.return_value = updated_chart
+
+        request = {
+            "identifier": 1,
+            "chart_name": "Renamed Chart",
+            "generate_preview": False,
+        }
+
+        async with Client(mcp) as client:
+            result = await client.call_tool("update_chart", {"request": request})
+
+            assert result.structured_content["success"] is True
+            assert result.structured_content["chart"]["slice_name"] == "Renamed Chart"
+
+            # Verify UpdateChartCommand was called with name-only payload
+            mock_update_cmd_cls.assert_called_once_with(
+                1, {"slice_name": "Renamed Chart"}
+            )
+
+    @patch("superset.daos.chart.ChartDAO.find_by_id", new_callable=Mock)
+    @patch("superset.db.session")
+    @pytest.mark.asyncio
+    async def test_no_config_no_name_returns_error(
+        self,
+        mock_db_session,
+        mock_find_by_id,
+        mcp_server,
+    ):
+        """Error when neither config nor chart_name is provided."""
+        mock_chart = Mock()
+        mock_chart.id = 1
+        mock_chart.datasource_id = 10
+        mock_find_by_id.return_value = mock_chart
+
+        with patch(
+            "superset.mcp_service.auth.check_chart_data_access",
+            new_callable=Mock,
+        ) as mock_check_access:
+            mock_check_access.return_value = DatasetValidationResult(
+                is_valid=True,
+                dataset_id=10,
+                dataset_name="my_dataset",
+                warnings=[],
+            )
+
+            request = {
+                "identifier": 1,
+            }
+
+            async with Client(mcp) as client:
+                result = await client.call_tool("update_chart", {"request": request})
+
+                assert result.structured_content["success"] is False
+                error = result.structured_content["error"]
+                assert error["error_type"] == "ValidationError"
+                assert "config" in error["message"].lower()
+                assert "chart_name" in error["message"].lower()
PATCH

echo "Gold patch applied successfully"
