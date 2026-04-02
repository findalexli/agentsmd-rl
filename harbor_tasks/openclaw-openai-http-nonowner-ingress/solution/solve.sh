#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if already fixed
if grep -q 'senderIsOwner: false as const' src/gateway/openai-http.ts; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/gateway/openai-http.ts b/src/gateway/openai-http.ts
index 61e6c9587651..138799f06984 100644
--- a/src/gateway/openai-http.ts
+++ b/src/gateway/openai-http.ts
@@ -117,8 +117,8 @@ function buildAgentCommandInput(params: {
     deliver: false as const,
     messageChannel: params.messageChannel,
     bestEffortDeliver: false as const,
-    // HTTP API callers are authenticated operator clients for this gateway context.
-    senderIsOwner: true as const,
+    // OpenAI-compatible HTTP ingress is external input and must not inherit owner-only tools.
+    senderIsOwner: false as const,
     allowModelOverride: true as const,
   };
 }

PATCH

echo "Fix applied: senderIsOwner set to false for OpenAI HTTP ingress."
