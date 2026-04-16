#!/bin/bash
set -e

cd /workspace/superset

# Idempotency check - skip if already applied
# Check for the distinctive line added by the patch: "Use the 'limit' parameter"
if grep -q "Use the 'limit' parameter" superset/mcp_service/utils/token_utils.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --check - <<'PATCH'
diff --git a/superset/mcp_service/utils/token_utils.py b/superset/mcp_service/utils/token_utils.py
index b7f12a2c1cb1..d4891634a8e6 100644
--- a/superset/mcp_service/utils/token_utils.py
+++ b/superset/mcp_service/utils/token_utils.py
@@ -220,6 +220,11 @@ def generate_size_reduction_suggestions(
                 f"Add a 'limit' or 'page_size' parameter (suggested: 10-25 items) "
                 f"to reduce response size by ~{reduction_pct}%"
             )
+        elif tool_name == "execute_sql":
+            suggestions.append(
+                f"Use the 'limit' parameter (e.g., limit=100) to cap the number "
+                f"of rows returned — need ~{reduction_pct}% reduction"
+            )

     # Suggestion 2: Use select_columns to reduce fields
     current_columns = query_params.get("select_columns") or query_params.get("columns")
@@ -348,9 +353,13 @@ def _get_tool_specific_suggestions(

     elif tool_name == "execute_sql":
         suggestions.append(
-            "Add LIMIT clause to your SQL query to restrict the number of rows "
-            "(e.g., SELECT * FROM table LIMIT 100)"
+            "Add a LIMIT clause to your SQL query (e.g., SELECT * FROM table LIMIT 100)"
         )
+        if not query_params.get("limit"):
+            suggestions.append(
+                "Use the execute_sql 'limit' parameter to cap rows returned "
+                "(e.g., limit=100) — this overrides any SQL LIMIT clause"
+            )

     elif tool_name in ("get_chart_info", "get_dashboard_info", "get_dataset_info"):
         suggestions.append(
diff --git a/tests/unit_tests/mcp_service/utils/test_token_utils.py b/tests/unit_tests/mcp_service/utils/test_token_utils.py
index 649536019bb9..a451b086b378 100644
--- a/tests/unit_tests/mcp_service/utils/test_token_utils.py
+++ b/tests/unit_tests/mcp_service/utils/test_token_utils.py
@@ -222,7 +222,25 @@ def test_tool_specific_suggestions_execute_sql(self) -> None:
             estimated_tokens=50000,
             token_limit=25000,
         )
-        assert any("LIMIT" in s or "limit" in s.lower() for s in suggestions)
+        combined = " ".join(suggestions)
+        # Should suggest SQL LIMIT clause
+        assert "LIMIT" in combined
+        # Should suggest the tool's limit parameter
+        assert "'limit' parameter" in combined.lower() or "limit=" in combined.lower()
+
+    def test_execute_sql_with_limit_param_no_duplicate_suggestion(self) -> None:
+        """When limit param is already set, should not suggest adding it again."""
+        suggestions = generate_size_reduction_suggestions(
+            tool_name="execute_sql",
+            params={"sql": "SELECT * FROM table", "limit": 500},
+            estimated_tokens=50000,
+            token_limit=25000,
+        )
+        combined = " ".join(suggestions)
+        # Should still suggest SQL LIMIT
+        assert "LIMIT" in combined
+        # Should suggest reducing the existing limit (from general suggestion)
+        assert "500" in combined or "limit" in combined.lower()

     def test_tool_specific_suggestions_list_charts(self) -> None:
         """Should provide chart-specific suggestions for list_charts."""
PATCH

git apply - <<'PATCH'
diff --git a/superset/mcp_service/utils/token_utils.py b/superset/mcp_service/utils/token_utils.py
index b7f12a2c1cb1..d4891634a8e6 100644
--- a/superset/mcp_service/utils/token_utils.py
+++ b/superset/mcp_service/utils/token_utils.py
@@ -220,6 +220,11 @@ def generate_size_reduction_suggestions(
                 f"Add a 'limit' or 'page_size' parameter (suggested: 10-25 items) "
                 f"to reduce response size by ~{reduction_pct}%"
             )
+        elif tool_name == "execute_sql":
+            suggestions.append(
+                f"Use the 'limit' parameter (e.g., limit=100) to cap the number "
+                f"of rows returned — need ~{reduction_pct}% reduction"
+            )

     # Suggestion 2: Use select_columns to reduce fields
     current_columns = query_params.get("select_columns") or query_params.get("columns")
@@ -348,9 +353,13 @@ def _get_tool_specific_suggestions(

     elif tool_name == "execute_sql":
         suggestions.append(
-            "Add LIMIT clause to your SQL query to restrict the number of rows "
-            "(e.g., SELECT * FROM table LIMIT 100)"
+            "Add a LIMIT clause to your SQL query (e.g., SELECT * FROM table LIMIT 100)"
         )
+        if not query_params.get("limit"):
+            suggestions.append(
+                "Use the execute_sql 'limit' parameter to cap rows returned "
+                "(e.g., limit=100) — this overrides any SQL LIMIT clause"
+            )

     elif tool_name in ("get_chart_info", "get_dashboard_info", "get_dataset_info"):
         suggestions.append(
diff --git a/tests/unit_tests/mcp_service/utils/test_token_utils.py b/tests/unit_tests/mcp_service/utils/test_token_utils.py
index 649536019bb9..a451b086b378 100644
--- a/tests/unit_tests/mcp_service/utils/test_token_utils.py
+++ b/tests/unit_tests/mcp_service/utils/test_token_utils.py
@@ -222,7 +222,25 @@ def test_tool_specific_suggestions_execute_sql(self) -> None:
             estimated_tokens=50000,
             token_limit=25000,
         )
-        assert any("LIMIT" in s or "limit" in s.lower() for s in suggestions)
+        combined = " ".join(suggestions)
+        # Should suggest SQL LIMIT clause
+        assert "LIMIT" in combined
+        # Should suggest the tool's limit parameter
+        assert "'limit' parameter" in combined.lower() or "limit=" in combined.lower()
+
+    def test_execute_sql_with_limit_param_no_duplicate_suggestion(self) -> None:
+        """When limit param is already set, should not suggest adding it again."""
+        suggestions = generate_size_reduction_suggestions(
+            tool_name="execute_sql",
+            params={"sql": "SELECT * FROM table", "limit": 500},
+            estimated_tokens=50000,
+            token_limit=25000,
+        )
+        combined = " ".join(suggestions)
+        # Should still suggest SQL LIMIT
+        assert "LIMIT" in combined
+        # Should suggest reducing the existing limit (from general suggestion)
+        assert "500" in combined or "limit" in combined.lower()

     def test_tool_specific_suggestions_list_charts(self) -> None:
         """Should provide chart-specific suggestions for list_charts."""
PATCH

echo "Patch applied successfully."
