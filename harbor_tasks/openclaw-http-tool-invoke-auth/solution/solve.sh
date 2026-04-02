#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency check: if the scope authorization is already in tools-invoke-http.ts, skip
if grep -q 'authorizeOperatorScopesForMethod' src/gateway/tools-invoke-http.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/gateway/tools-invoke-http.ts b/src/gateway/tools-invoke-http.ts
index f9f97c5c9ee0..43d08b28e1c9 100644
--- a/src/gateway/tools-invoke-http.ts
+++ b/src/gateway/tools-invoke-http.ts
@@ -13,6 +13,7 @@ import {
   buildDefaultToolPolicyPipelineSteps,
 } from "../agents/tool-policy-pipeline.js";
 import {
+  applyOwnerOnlyToolPolicy,
   collectExplicitAllowlist,
   mergeAlsoAllowPolicy,
   resolveToolProfilePolicy,
@@ -28,7 +29,10 @@ import { DEFAULT_GATEWAY_HTTP_TOOL_DENY } from "../security/dangerous-tools.js";
 import { normalizeMessageChannel } from "../utils/message-channel.js";
 import type { AuthRateLimiter } from "./auth-rate-limit.js";
 import type { ResolvedGatewayAuth } from "./auth.js";
-import { authorizeGatewayBearerRequestOrReply } from "./http-auth-helpers.js";
+import {
+  authorizeGatewayBearerRequestOrReply,
+  resolveGatewayRequestedOperatorScopes,
+} from "./http-auth-helpers.js";
 import {
   readJsonBodyOrError,
   sendInvalidRequest,
@@ -36,6 +40,7 @@ import {
   sendMethodNotAllowed,
 } from "./http-common.js";
 import { getHeader } from "./http-utils.js";
+import { authorizeOperatorScopesForMethod } from "./method-scopes.js";

 const DEFAULT_BODY_BYTES = 2 * 1024 * 1024;
 const MEMORY_TOOL_NAMES = new Set(["memory_search", "memory_get"]);
@@ -168,6 +173,19 @@ export async function handleToolsInvokeHttpRequest(
     return true;
   }

+  const requestedScopes = resolveGatewayRequestedOperatorScopes(req);
+  const scopeAuth = authorizeOperatorScopesForMethod("agent", requestedScopes);
+  if (!scopeAuth.allowed) {
+    sendJson(res, 403, {
+      ok: false,
+      error: {
+        type: "forbidden",
+        message: `missing scope: ${scopeAuth.missingScope}`,
+      },
+    });
+    return true;
+  }
+
   const bodyUnknown = await readJsonBodyOrError(req, res, opts.maxBodyBytes ?? DEFAULT_BODY_BYTES);
   if (bodyUnknown === undefined) {
     return true;
@@ -305,7 +323,10 @@ export async function handleToolsInvokeHttpRequest(
     Array.isArray(gatewayToolsCfg?.deny) ? gatewayToolsCfg.deny : [],
   );
   const gatewayDenySet = new Set(gatewayDenyNames);
-  const gatewayFiltered = subagentFiltered.filter((t) => !gatewayDenySet.has(t.name));
+  // HTTP bearer auth does not bind a device-owner identity, so owner-only tools
+  // stay unavailable on this surface even when callers assert admin scopes.
+  const ownerFiltered = applyOwnerOnlyToolPolicy(subagentFiltered, false);
+  const gatewayFiltered = ownerFiltered.filter((t) => !gatewayDenySet.has(t.name));

   const tool = gatewayFiltered.find((t) => t.name === toolName);
   if (!tool) {
diff --git a/src/security/dangerous-tools.ts b/src/security/dangerous-tools.ts
index 6d1274723a52..12c4417242c2 100644
--- a/src/security/dangerous-tools.ts
+++ b/src/security/dangerous-tools.ts
@@ -7,6 +7,20 @@
  * or interactive flows that don't make sense over a non-interactive HTTP surface.
  */
 export const DEFAULT_GATEWAY_HTTP_TOOL_DENY = [
+  // Direct command execution — immediate RCE surface
+  "exec",
+  // Arbitrary child process creation — immediate RCE surface
+  "spawn",
+  // Shell command execution — immediate RCE surface
+  "shell",
+  // Arbitrary file mutation on the host
+  "fs_write",
+  // Arbitrary file deletion on the host
+  "fs_delete",
+  // Arbitrary file move/rename on the host
+  "fs_move",
+  // Patch application can rewrite arbitrary files
+  "apply_patch",
   // Session orchestration — spawning agents remotely is RCE
   "sessions_spawn",
   // Cross-session injection — message injection across sessions
@@ -15,6 +29,8 @@ export const DEFAULT_GATEWAY_HTTP_TOOL_DENY = [
   "cron",
   // Gateway control plane — prevents gateway reconfiguration via HTTP
   "gateway",
+  // Node command relay can reach system.run on paired hosts
+  "nodes",
   // Interactive setup — requires terminal QR scan, hangs on HTTP
   "whatsapp_login",
 ] as const;

PATCH

echo "Patch applied successfully."
