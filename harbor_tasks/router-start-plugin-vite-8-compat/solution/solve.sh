#!/bin/bash
set -e

# Apply the gold patch to fix Vite 7/8 compatibility

cd /workspace/router

# Check if already applied (idempotency)
if grep -q "isRolldown = 'rolldownVersion' in vite" packages/start-plugin-core/src/utils.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch using git apply
cat <<'PATCH' | git apply -
diff --git a/packages/start-plugin-core/src/plugin.ts b/packages/start-plugin-core/src/plugin.ts
index 40ce36c17f1..9a7ddbaa3a0 100644
--- a/packages/start-plugin-core/src/plugin.ts
+++ b/packages/start-plugin-core/src/plugin.ts
@@ -5,6 +5,7 @@ import { join } from 'pathe'
 import { escapePath } from 'tinyglobby'
 import { startManifestPlugin } from './start-manifest-plugin/plugin'
 import { ENTRY_POINTS, VITE_ENVIRONMENT_NAMES } from './constants'
+import { bundlerOptionsKey, getBundlerOptions } from './utils'
 import { tanStackStartRouter } from './start-router-plugin/plugin'
 import { loadEnvPlugin } from './load-env-plugin/plugin'
 import { devServerPlugin } from './dev-server-plugin/plugin'
@@ -244,7 +245,7 @@ export function TanStackStartVitePluginCore(
             [VITE_ENVIRONMENT_NAMES.client]: {
               consumer: 'client',
               build: {
-                rollupOptions: {
+                [bundlerOptionsKey]: {
                   input: {
                     main: ENTRY_POINTS.client,
                   },
@@ -264,10 +265,12 @@ export function TanStackStartVitePluginCore(
               consumer: 'server',
               build: {
                 ssr: true,
-                rollupOptions: {
+                [bundlerOptionsKey]: {
                   input:
-                    viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
-                      ?.build?.rollupOptions?.input ?? serverAlias,
+                    getBundlerOptions(
+                      viteConfig.environments?.[VITE_ENVIRONMENT_NAMES.server]
+                        ?.build,
+                    )?.input ?? serverAlias,
                 },
                 outDir: getServerOutputDirectory(viteConfig),
                 commonjsOptions: {
diff --git a/packages/start-plugin-core/src/preview-server-plugin/plugin.ts b/packages/start-plugin-core/src/preview-server-plugin/plugin.ts
index 3257a8323b7..0943d11c888 100644
--- a/packages/start-plugin-core/src/preview-server-plugin/plugin.ts
+++ b/packages/start-plugin-core/src/preview-server-plugin/plugin.ts
@@ -4,6 +4,7 @@ import { NodeRequest, sendNodeResponse } from 'srvx/node'
 import { joinURL } from 'ufo'
 import { VITE_ENVIRONMENT_NAMES } from '../constants'
 import { getServerOutputDirectory } from '../output-directory'
+import { getBundlerOptions } from '../utils'
 import type { Plugin } from 'vite'

 export function previewServerPlugin(): Plugin {
@@ -27,7 +28,7 @@ export function previewServerPlugin(): Plugin {
                 const serverEnv =
                   server.config.environments[VITE_ENVIRONMENT_NAMES.server]
                 const serverInput =
-                  serverEnv?.build.rollupOptions.input ?? 'server'
+                  getBundlerOptions(serverEnv?.build)?.input ?? 'server'

                 if (typeof serverInput !== 'string') {
                   throw new Error('Invalid server input. Expected a string.')
diff --git a/packages/start-plugin-core/src/utils.ts b/packages/start-plugin-core/src/utils.ts
index 252712ef662..9b9801df1c9 100644
--- a/packages/start-plugin-core/src/utils.ts
+++ b/packages/start-plugin-core/src/utils.ts
@@ -1,3 +1,21 @@
+import * as vite from 'vite'
+
+/**
+ * Vite 8+ uses Rolldown instead of Rollup, renaming `build.rollupOptions`
+ * to `build.rolldownOptions`. Detect which bundler is in use.
+ */
+export const isRolldown = 'rolldownVersion' in vite
+
+/** Returns `'rolldownOptions'` when using Rolldown, `'rollupOptions'` otherwise. */
+export const bundlerOptionsKey = isRolldown
+  ? 'rolldownOptions'
+  : 'rollupOptions'
+
+/** Read `build.rollupOptions` or `build.rolldownOptions` from a build config. */
+export function getBundlerOptions(build: any): any {
+  return build?.rolldownOptions ?? build?.rollupOptions
+}
+
 export function resolveViteId(id: string) {
   return `\0${id}`
 }
PATCH

echo "Patch applied successfully"

# Rebuild the package after applying the fix
CI=1 NX_DAEMON=false pnpm nx run @tanstack/start-plugin-core:build --outputStyle=stream --skipRemoteCache

echo "Build completed"
