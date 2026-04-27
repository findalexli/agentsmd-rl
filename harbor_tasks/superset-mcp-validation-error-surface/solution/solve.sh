#!/usr/bin/env bash
# Gold solution: applies the patch from apache/superset#39522 to the repo
# checked out under /workspace/superset.
set -euo pipefail

cd /workspace/superset

# Idempotency guard — distinctive line from the inlined patch.
if grep -q '"validation_error":' superset/mcp_service/utils/error_builder.py 2>/dev/null; then
    echo "[solve] patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset/mcp_service/chart/validation/pipeline.py b/superset/mcp_service/chart/validation/pipeline.py
index 6923de0bd0b6..b2ca1fa791bb 100644
--- a/superset/mcp_service/chart/validation/pipeline.py
+++ b/superset/mcp_service/chart/validation/pipeline.py
@@ -21,6 +21,7 @@
 """

 import logging
+import re
 from typing import Any, Dict, List, Tuple

 from superset.mcp_service.chart.schemas import (
@@ -77,13 +78,27 @@ def _sanitize_validation_error(error: Exception) -> str:
     """SECURITY FIX: Sanitize validation errors to prevent disclosure."""
     error_str = str(error)

+    # Pydantic tagged-union errors prefix the message with a long
+    # ``1 validation error for tagged-union[...]`` header before the
+    # per-field body (e.g. ``Value error, ...``, ``Field required``,
+    # ``Input should be ...``). The body always lives on a line indented
+    # by exactly two spaces — pull it out so the 200-char truncation
+    # below doesn't swallow the actionable part. The pydantic footer
+    # ``\n    For further information ...`` uses four-space indent and
+    # is dropped here.
+    if "tagged-union[" in error_str:
+        body_match = re.search(r"\n  (?! )", error_str)
+        if body_match:
+            idx = body_match.end()
+            footer_idx = error_str.find("\n    For further information", idx)
+            end = footer_idx if footer_idx != -1 else len(error_str)
+            error_str = error_str[idx:end].strip()
+
     # SECURITY FIX: Limit length FIRST to prevent ReDoS attacks
     if len(error_str) > 200:
         error_str = error_str[:200] + "...[truncated]"

     # Remove potentially sensitive schema information
-    import re
-
     sensitive_patterns = [
         (r'\btable\s+[\'"`]?(\w+)[\'"`]?', "table [REDACTED]"),
         (r'\bcolumn\s+[\'"`]?(\w+)[\'"`]?', "column [REDACTED]"),
diff --git a/superset/mcp_service/utils/error_builder.py b/superset/mcp_service/utils/error_builder.py
index 61df3eb9108d..f019092dcc6d 100644
--- a/superset/mcp_service/utils/error_builder.py
+++ b/superset/mcp_service/utils/error_builder.py
@@ -186,6 +186,18 @@ class ChartErrorBuilder:
                 "Check Superset logs for detailed error information",
             ],
         },
+        "validation_error": {
+            "message": "Chart configuration is invalid: {reason}",
+            "details": "{reason}",
+            "suggestions": [
+                "Review the field names and types in your config against the "
+                "chart_type's schema",
+                "Call get_chart_type_schema or read the chart://configs resource "
+                "for valid fields and examples",
+                "Replace any unknown field names with the ones listed in the "
+                "error details above",
+            ],
+        },
     }

     @classmethod
PATCH

echo "[solve] patch applied."
