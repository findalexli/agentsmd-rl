#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry

# Idempotency guard
if grep -qF "from sentry.analytics.events.feature_used import FeatureUsedEvent  # does not ex" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -272,6 +272,7 @@ class MyPermission(SentryPermission):
 ```python
 import logging
 from sentry import analytics
+from sentry.analytics.events.feature_used import FeatureUsedEvent  # does not exist, only for demonstration purposes
 
 logger = logging.getLogger(__name__)
 
@@ -287,10 +288,11 @@ logger.info(
 
 # Analytics event
 analytics.record(
-    "feature.used",
-    user_id=user.id,
-    organization_id=org.id,
-    feature="new-dashboard",
+    FeatureUsedEvent(
+        user_id=user.id,
+        organization_id=org.id,
+        feature="new-dashboard",
+    )
 )
 ```
 
PATCH

echo "Gold patch applied."
