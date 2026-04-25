#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/openclaw"
cd "$REPO"

# Idempotency: check if fix is already applied
if grep -q 'requiredOperatorMethod' src/gateway/embeddings-http.ts 2>/dev/null; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/gateway/embeddings-http.ts b/src/gateway/embeddings-http.ts
index a67501b87cf6..c82821d3d8e5 100644
--- a/src/gateway/embeddings-http.ts
+++ b/src/gateway/embeddings-http.ts
@@ -209,6 +209,7 @@ export async function handleOpenAiEmbeddingsHttpRequest(
 ): Promise<boolean> {
   const handled = await handleGatewayPostJsonEndpoint(req, res, {
     pathname: "/v1/embeddings",
+    requiredOperatorMethod: "chat.send",
     auth: opts.auth,
     trustedProxies: opts.trustedProxies,
     allowRealIpFallback: opts.allowRealIpFallback,

PATCH

echo "Applied: added requiredOperatorMethod to embeddings HTTP handler."
