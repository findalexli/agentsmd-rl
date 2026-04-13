#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

if grep -q "getActivePluginRegistry" src/plugins/tools.ts 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/src/plugins/tools.ts b/src/plugins/tools.ts
index 66f16f73b883..7f6e76c7e37b 100644
--- a/src/plugins/tools.ts
+++ b/src/plugins/tools.ts
@@ -3,8 +3,9 @@ import type { AnyAgentTool } from "../agents/tools/common.js";
 import { applyPluginAutoEnable } from "../config/plugin-auto-enable.js";
 import { createSubsystemLogger } from "../logging/subsystem.js";
 import { applyTestPluginDefaults, normalizePluginsConfig } from "./config-state.js";
-import { resolveRuntimePluginRegistry } from "./loader.js";
+import { resolveRuntimePluginRegistry, type PluginLoadOptions } from "./loader.js";
 import { createPluginLoaderLogger } from "./logger.js";
+import { getActivePluginRegistry } from "./runtime.js";
 import type { OpenClawPluginToolContext } from "./types.js";
 
 const log = createSubsystemLogger("plugins");
@@ -50,6 +51,16 @@ function isOptionalToolAllowed(params: {
   return params.allowlist.has("group:plugins");
 }
 
+function resolvePluginToolRegistry(params: {
+  loadOptions: PluginLoadOptions;
+  allowGatewaySubagentBinding?: boolean;
+}) {
+  if (params.allowGatewaySubagentBinding) {
+    return getActivePluginRegistry() ?? resolveRuntimePluginRegistry(params.loadOptions);
+  }
+  return resolveRuntimePluginRegistry(params.loadOptions);
+}
+
 export function resolvePluginTools(params: {
   context: OpenClawPluginToolContext;
   existingToolNames?: Set<string>;
@@ -68,18 +79,20 @@ export function resolvePluginTools(params: {
     return [];
   }
 
+  const runtimeOptions = params.allowGatewaySubagentBinding
+    ? { allowGatewaySubagentBinding: true as const }
+    : undefined;
   const loadOptions = {
     config: effectiveConfig,
     workspaceDir: params.context.workspaceDir,
-    runtimeOptions: params.allowGatewaySubagentBinding
-      ? {
-          allowGatewaySubagentBinding: true,
-        }
-      : undefined,
+    runtimeOptions,
     env,
     logger: createPluginLoaderLogger(log),
   };
-  const registry = resolveRuntimePluginRegistry(loadOptions);
+  const registry = resolvePluginToolRegistry({
+    loadOptions,
+    allowGatewaySubagentBinding: params.allowGatewaySubagentBinding,
+  });
   if (!registry) {
     return [];
   }

PATCH
