#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for APP-1093: prioritize STARTING status over WebSocket DISCONNECTED
# This ensures "Starting" is displayed when server reports STARTING during resume
cat <<'PATCH' | git apply -
diff --git a/frontend/src/utils/status.ts b/frontend/src/utils/status.ts
index e64820b291b9..29e336dcf21a 100644
--- a/frontend/src/utils/status.ts
+++ b/frontend/src/utils/status.ts
@@ -119,6 +119,14 @@ export function getStatusCode(
     return I18nKey.CHAT_INTERFACE$STOPPED;
   }

+  // PRIORITY 2.5: Handle conversation starting state
+  // This must come before WebSocket status check to show "Starting" when
+  // the server reports STARTING, even if WebSocket is temporarily disconnected
+  // during the resume process
+  if (conversationStatus === "STARTING") {
+    return I18nKey.COMMON$STARTING;
+  }
+
   // Prioritize agent state when it indicates readiness, even if runtime status is stale
   const agentIsReady =
     agentState &&
PATCH

# Idempotency check: verify the STARTING check exists
grep -q 'conversationStatus === "STARTING"' frontend/src/utils/status.ts || exit 1

echo "Fix applied successfully"
