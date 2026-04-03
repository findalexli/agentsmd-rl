#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

git apply - <<'PATCH'
diff --git a/extensions/discord/src/monitor/provider.lifecycle.ts b/extensions/discord/src/monitor/provider.lifecycle.ts
index 5f455b61b901..5b61ed2b4836 100644
--- a/extensions/discord/src/monitor/provider.lifecycle.ts
+++ b/extensions/discord/src/monitor/provider.lifecycle.ts
@@ -82,13 +82,10 @@ export async function runDiscordGatewayLifecycle(params: {
       if (decision !== "stop") {
         return "continue";
       }
-      // Don't throw for expected shutdown events — intentional disconnect
-      // (reconnect-exhausted with maxAttempts=0) and disallowed-intents are
-      // both handled without crashing the provider.
-      if (
-        event.type === "disallowed-intents" ||
-        (lifecycleStopping && event.type === "reconnect-exhausted")
-      ) {
+      // Don't throw for expected shutdown events. `reconnect-exhausted` can be
+      // queued before teardown flips `lifecycleStopping`, so treat it as a
+      // graceful stop here and let the health monitor own reconnect behavior.
+      if (event.type === "disallowed-intents" || event.type === "reconnect-exhausted") {
         return "stop";
       }
       throw event.err;
PATCH
