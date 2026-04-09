#!/bin/bash
set -e

cd /workspace/dagster

# Apply the fix: drop local state before run
cat <<'PATCH' | git apply -
diff --git a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
index faf5b20f47899..3e68b49709eb8 100644
--- a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
+++ b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
@@ -282,6 +282,18 @@ def _run(
                 ]
             )

+        # Dlt keeps some local state that interferes with next runs.
+        # This is annoying when an asset fails and running a different one on the same pipeline
+        # would just pick up the failing job and fail again.
+        # When restore_from_destination is enabled (default), we can safely drop all local state
+        # because it will be restored from the destination.
+        # When restore_from_destination is disabled, we only drop pending packages to avoid
+        # wiping incremental loading cursors that can't be recovered from the destination.
+        if dlt_pipeline.config.restore_from_destination:
+            dlt_pipeline.drop()
+        else:
+            dlt_pipeline.drop_pending_packages()
+
         load_info = dlt_pipeline.run(dlt_source, **kwargs)

         load_info.raise_on_failed_jobs()
PATCH

# Verify the patch was applied
grep -q "dlt_pipeline.drop()" python_modules/libraries/dagster-dlt/dagster_dlt/resource.py && echo "Patch applied successfully"
