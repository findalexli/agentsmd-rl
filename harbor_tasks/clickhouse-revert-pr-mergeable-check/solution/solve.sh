#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for revert PR mergeable check fix
patch -p1 <<'PATCH'
diff --git a/ci/praktika/native_jobs.py b/ci/praktika/native_jobs.py
index aead5642fba3..36363c6d0a3e 100644
--- a/ci/praktika/native_jobs.py
+++ b/ci/praktika/native_jobs.py
@@ -839,6 +839,18 @@ def _finish_workflow(workflow, job_name):
         if dropped_results:
             ready_for_merge_description += f", Dropped: {len(dropped_results)}"

+    # Revert PRs should be easy to merge - only Fast test is required
+    if "Reverts ClickHouse/" in env.PR_BODY:
+        fast_test_failed = any(
+            "Fast test" in name for name in failed_results
+        )
+        if not fast_test_failed and ready_for_merge_status != Result.Status.SUCCESS:
+            print(
+                f"NOTE: Revert PR detected - setting merge status to success despite failures"
+            )
+            ready_for_merge_status = Result.Status.SUCCESS
+            ready_for_merge_description = "Revert PR"
+
     if workflow.enable_merge_ready_status:
         if not GH.post_commit_status(
             name=Settings.READY_FOR_MERGE_CUSTOM_STATUS_NAME
PATCH

# Idempotency check: verify the distinctive line exists
grep -q "Revert PR detected - setting merge status to success despite failures" ci/praktika/native_jobs.py

echo "Patch applied successfully"
