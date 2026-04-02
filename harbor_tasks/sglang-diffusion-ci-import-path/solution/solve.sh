#!/usr/bin/env bash
set -euo pipefail

FILE1="scripts/ci/utils/diffusion/publish_comparison_results.py"

# Idempotency check: if __package__ guard already present, patch was applied
if grep -q 'if __package__:' "$FILE1" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/ci/utils/diffusion/publish_comparison_results.py b/scripts/ci/utils/diffusion/publish_comparison_results.py
index e7cfbb8c1c50..03a40612c102 100644
--- a/scripts/ci/utils/diffusion/publish_comparison_results.py
+++ b/scripts/ci/utils/diffusion/publish_comparison_results.py
@@ -20,19 +20,33 @@
 from datetime import datetime, timezone
 from pathlib import Path

-# Reuse GitHub API helpers from publish_traces
-sys.path.insert(0, str(Path(__file__).parent))
-from ..publish_traces import (
-    create_blobs,
-    create_commit,
-    create_tree,
-    get_branch_sha,
-    get_tree_sha,
-    is_permission_error,
-    is_rate_limit_error,
-    update_branch_ref,
-    verify_token_permissions,
-)
+# Reuse GitHub API helpers from publish_traces.
+# Support both direct script execution and package-style imports.
+if __package__:
+    from ..publish_traces import (
+        create_blobs,
+        create_commit,
+        create_tree,
+        get_branch_sha,
+        get_tree_sha,
+        is_permission_error,
+        is_rate_limit_error,
+        update_branch_ref,
+        verify_token_permissions,
+    )
+else:
+    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
+    from publish_traces import (
+        create_blobs,
+        create_commit,
+        create_tree,
+        get_branch_sha,
+        get_tree_sha,
+        is_permission_error,
+        is_rate_limit_error,
+        update_branch_ref,
+        verify_token_permissions,
+    )

 # Repository configuration
 REPO_OWNER = "sglang-bot"
diff --git a/scripts/ci/utils/diffusion/publish_diffusion_gt.py b/scripts/ci/utils/diffusion/publish_diffusion_gt.py
index eda5de09f177..00b5de0c2fd4 100644
--- a/scripts/ci/utils/diffusion/publish_diffusion_gt.py
+++ b/scripts/ci/utils/diffusion/publish_diffusion_gt.py
@@ -6,21 +6,35 @@
 import argparse
 import os
 import sys
-
-# Allow importing from the same directory (scripts/ci/utils/)
-sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
-
-from ..publish_traces import (
-    create_blobs,
-    create_commit,
-    create_tree,
-    get_branch_sha,
-    get_tree_sha,
-    is_permission_error,
-    is_rate_limit_error,
-    update_branch_ref,
-    verify_token_permissions,
-)
+from pathlib import Path
+
+# Reuse GitHub API helpers from publish_traces.
+# Support both direct script execution and package-style imports.
+if __package__:
+    from ..publish_traces import (
+        create_blobs,
+        create_commit,
+        create_tree,
+        get_branch_sha,
+        get_tree_sha,
+        is_permission_error,
+        is_rate_limit_error,
+        update_branch_ref,
+        verify_token_permissions,
+    )
+else:
+    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
+    from publish_traces import (
+        create_blobs,
+        create_commit,
+        create_tree,
+        get_branch_sha,
+        get_tree_sha,
+        is_permission_error,
+        is_rate_limit_error,
+        update_branch_ref,
+        verify_token_permissions,
+    )

 REPO_OWNER = "sglang-bot"
 REPO_NAME = "sglang-ci-data"

PATCH

echo "Patch applied successfully."
