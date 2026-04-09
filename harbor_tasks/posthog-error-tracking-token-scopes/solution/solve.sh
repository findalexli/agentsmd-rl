#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'scope_object_read_actions' products/error_tracking/backend/api/issues.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/products/error_tracking/backend/api/issues.py b/products/error_tracking/backend/api/issues.py
index f7add95634fc..3d5f6485182c 100644
--- a/products/error_tracking/backend/api/issues.py
+++ b/products/error_tracking/backend/api/issues.py
@@ -120,6 +120,20 @@ def update(self, instance, validated_data):
 @extend_schema(tags=[ProductKey.ERROR_TRACKING])
 class ErrorTrackingIssueViewSet(TeamAndOrgViewSetMixin, ForbidDestroyModel, viewsets.ModelViewSet):
     scope_object = "error_tracking"
+    # These override the base defaults, so keep the standard DRF actions too.
+    scope_object_read_actions = ["list", "retrieve", "values"]
+    scope_object_write_actions = [
+        "create",
+        "update",
+        "partial_update",
+        "patch",
+        "destroy",
+        "merge",
+        "split",
+        "assign",
+        "cohort",
+        "bulk",
+    ]
     queryset = ErrorTrackingIssue.objects.with_first_seen().all()
     serializer_class = ErrorTrackingIssueFullSerializer

PATCH

echo "Patch applied successfully."
