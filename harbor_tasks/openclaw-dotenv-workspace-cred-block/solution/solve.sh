#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if ANTHROPIC_API_KEY is already in the blocked set
if grep -q '"ANTHROPIC_API_KEY"' src/infra/dotenv.ts; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/infra/dotenv.ts b/src/infra/dotenv.ts
index 419d3396b646..65781e17fae0 100644
--- a/src/infra/dotenv.ts
+++ b/src/infra/dotenv.ts
@@ -10,20 +10,32 @@ import {

 const BLOCKED_WORKSPACE_DOTENV_KEYS = new Set([
   "ALL_PROXY",
+  "ANTHROPIC_API_KEY",
+  "ANTHROPIC_OAUTH_TOKEN",
   "HTTP_PROXY",
   "HTTPS_PROXY",
   "NODE_TLS_REJECT_UNAUTHORIZED",
   "NO_PROXY",
   "OPENCLAW_AGENT_DIR",
   "OPENCLAW_CONFIG_PATH",
+  "OPENCLAW_GATEWAY_PASSWORD",
+  "OPENCLAW_GATEWAY_SECRET",
+  "OPENCLAW_GATEWAY_TOKEN",
   "OPENCLAW_HOME",
+  "OPENCLAW_LIVE_ANTHROPIC_KEY",
+  "OPENCLAW_LIVE_ANTHROPIC_KEYS",
+  "OPENCLAW_LIVE_GEMINI_KEY",
+  "OPENCLAW_LIVE_OPENAI_KEY",
   "OPENCLAW_OAUTH_DIR",
   "OPENCLAW_PROFILE",
   "OPENCLAW_STATE_DIR",
+  "OPENAI_API_KEY",
+  "OPENAI_API_KEYS",
   "PI_CODING_AGENT_DIR",
 ]);

 const BLOCKED_WORKSPACE_DOTENV_SUFFIXES = ["_BASE_URL"];
+const BLOCKED_WORKSPACE_DOTENV_PREFIXES = ["ANTHROPIC_API_KEY_", "OPENAI_API_KEY_"];

 function shouldBlockRuntimeDotEnvKey(key: string): boolean {
   return isDangerousHostEnvVarName(key) || isDangerousHostEnvOverrideVarName(key);
@@ -34,6 +46,7 @@ function shouldBlockWorkspaceDotEnvKey(key: string): boolean {
   return (
     shouldBlockRuntimeDotEnvKey(upper) ||
     BLOCKED_WORKSPACE_DOTENV_KEYS.has(upper) ||
+    BLOCKED_WORKSPACE_DOTENV_PREFIXES.some((prefix) => upper.startsWith(prefix)) ||
     BLOCKED_WORKSPACE_DOTENV_SUFFIXES.some((suffix) => upper.endsWith(suffix))
   );
 }

PATCH

echo "Fix applied: blocked credential and gateway auth vars from workspace dotenv."
