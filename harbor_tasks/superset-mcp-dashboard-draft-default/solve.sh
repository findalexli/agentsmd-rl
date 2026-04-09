#!/bin/bash
set -e

cd /workspace/superset

# Apply the fix: change published default from True to False
cat <<'PATCH' | git apply -
diff --git a/superset/mcp_service/dashboard/schemas.py b/superset/mcp_service/dashboard/schemas.py
index be2860e07cbe..cc01255eea4b 100644
--- a/superset/mcp_service/dashboard/schemas.py
+++ b/superset/mcp_service/dashboard/schemas.py
@@ -445,7 +445,7 @@ class GenerateDashboardRequest(BaseModel):
     )
     description: str | None = Field(None, description="Description for the dashboard")
     published: bool = Field(
-        default=True, description="Whether to publish the dashboard"
+        default=False, description="Whether to publish the dashboard"
     )


diff --git a/tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py b/tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py
index 71e4b83b5ec3..3464d8eb611f 100644
--- a/tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py
+++ b/tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py
@@ -444,7 +444,34 @@ async def test_generate_dashboard_minimal_request(
                 == "Minimal Dashboard"
             )

-            # Verify dashboard was created with default published=True
+            # Verify dashboard was created with default published=False
+            created = mock_dashboard_cls.return_value
+            assert created.published is False
+
+    @patch("superset.models.dashboard.Dashboard")
+    @patch("superset.daos.dashboard.DashboardDAO.find_by_id")
+    @patch("superset.db.session")
+    @pytest.mark.asyncio
+    async def test_generate_dashboard_explicit_published(
+        self, mock_db_session, mock_find_by_id, mock_dashboard_cls, mcp_server
+    ):
+        """Test dashboard generation with published explicitly set to True."""
+        charts = [_mock_chart(id=3)]
+        mock_dashboard = _mock_dashboard(id=41, title="Published Dashboard")
+        _setup_generate_dashboard_mocks(
+            mock_db_session, mock_find_by_id, mock_dashboard_cls, charts, mock_dashboard
+        )
+
+        request = {
+            "chart_ids": [3],
+            "dashboard_title": "Published Dashboard",
+            "published": True,
+        }
+
+        async with Client(mcp_server) as client:
+            result = await client.call_tool("generate_dashboard", {"request": request})
+
+            assert result.structured_content["error"] is None
             created = mock_dashboard_cls.return_value
             assert created.published is True
PATCH

echo "Fix applied successfully"
