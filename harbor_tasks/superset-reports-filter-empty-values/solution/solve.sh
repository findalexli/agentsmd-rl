#!/bin/bash
set -e

# Idempotency check - if already patched, exit early
if grep -q "requires_values =" /workspace/superset/superset/reports/models.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

cd /workspace/superset

# Apply the gold patch from PR #38954
cat <<'PATCH' | git apply -
diff --git a/superset/reports/models.py b/superset/reports/models.py
index db70595063bf..5bea67c6d681 100644
--- a/superset/reports/models.py
+++ b/superset/reports/models.py
@@ -245,8 +245,22 @@ def _generate_native_filter(
             A tuple of (filter_config, warning_message). If the filter type is
             unrecognized, returns an empty dict and a warning message.
         """
+        # Filter types that require at least one value
+        requires_values = (
+            "filter_time",
+            "filter_timegrain",
+            "filter_timecolumn",
+            "filter_range",
+        )
+        if filter_type in requires_values and not values:
+            warning_msg = (
+                f"Skipping {filter_type} with empty filterValues "
+                f"(filter_id: {native_filter_id})"
+            )
+            logger.warning(warning_msg)
+            return {}, warning_msg
+
         if filter_type == "filter_time":
-            # For select filters, we need to use the "IN" operator
             return (
                 {
                     native_filter_id or "": {
PATCH

echo "Patch applied successfully"
