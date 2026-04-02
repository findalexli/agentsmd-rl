#!/usr/bin/env bash
set -euo pipefail
cd /workspace/next.js

# Idempotent: skip if already applied
grep -q 'rewritePathAliasesWithoutBaseUrl' packages/next/src/lib/typescript/getTypeScriptConfiguration.ts && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts b/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
index 8b7a907934b4d..e225c42fed932 100644
--- a/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
+++ b/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
@@ -31,6 +31,50 @@ function resolvePathAliasTarget(baseUrl: string, target: string): string {
   return `./${resolvedTarget}`
 }

+function rewritePathAliasesWithoutBaseUrl(
+  baseUrl: string,
+  originalPaths: unknown
+): Record<string, unknown> {
+  const rewrittenPaths: Record<string, unknown> =
+    originalPaths && typeof originalPaths === 'object'
+      ? Object.fromEntries(
+          Object.entries(originalPaths).map(([key, values]) => [
+            key,
+            Array.isArray(values)
+              ? values.map((value) =>
+                  typeof value === 'string'
+                    ? resolvePathAliasTarget(baseUrl, value)
+                    : value
+                )
+              : values,
+          ])
+        )
+      : {
+          '*': [resolvePathAliasTarget(baseUrl, '*')],
+        }
+
+  if (!Object.prototype.hasOwnProperty.call(rewrittenPaths, '*')) {
+    rewrittenPaths['*'] = [resolvePathAliasTarget(baseUrl, '*')]
+  }
+
+  return rewrittenPaths
+}
+
+function getNormalizedBaseUrlForPaths(
+  baseUrl: string,
+  tsConfigPath: string
+): string {
+  const tsConfigDir = path.resolve(path.dirname(tsConfigPath))
+  const absoluteBaseUrl = path.isAbsolute(baseUrl)
+    ? baseUrl
+    : baseUrl.startsWith('./') || baseUrl.startsWith('../')
+      ? path.resolve(tsConfigDir, baseUrl)
+      : path.resolve(baseUrl)
+  const relativeBaseUrl = path.relative(tsConfigDir, absoluteBaseUrl)
+
+  return relativeBaseUrl || '.'
+}
+
 export async function getTypeScriptConfiguration(
   typescript: typeof import('typescript'),
   tsConfigPath: string,
@@ -79,27 +123,10 @@ export async function getTypeScriptConfiguration(
       const hasBaseUrl = typeof baseUrl === 'string' && baseUrl.length > 0

       if (hasBaseUrl) {
-        const originalPaths = configToParse.compilerOptions?.paths
-        const rewrittenPaths: Record<string, unknown> =
-          originalPaths && typeof originalPaths === 'object'
-            ? Object.fromEntries(
-                Object.entries(originalPaths).map(([key, values]) => [
-                  key,
-                  Array.isArray(values)
-                    ? values.map((value) =>
-                        typeof value === 'string'
-                          ? resolvePathAliasTarget(baseUrl, value)
-                          : value
-                      )
-                    : values,
-                ])
-              )
-            : {
-                '*': [resolvePathAliasTarget(baseUrl, '*')],
-              }
-        if (!Object.prototype.hasOwnProperty.call(rewrittenPaths, '*')) {
-          rewrittenPaths['*'] = [resolvePathAliasTarget(baseUrl, '*')]
-        }
+        const rewrittenPaths = rewritePathAliasesWithoutBaseUrl(
+          baseUrl,
+          configToParse.compilerOptions?.paths
+        )
         const { baseUrl: _baseUrl, ...restCompilerOptions } =
           configToParse.compilerOptions ?? {}

@@ -130,6 +157,25 @@ export async function getTypeScriptConfiguration(
       path.dirname(tsConfigPath)
     )

+    if (semver.gte(typescript.version, '6.0.0')) {
+      const parsedBaseUrl = result.options.baseUrl
+      if (typeof parsedBaseUrl === 'string' && parsedBaseUrl.length > 0) {
+        const normalizedBaseUrl = getNormalizedBaseUrlForPaths(
+          parsedBaseUrl,
+          tsConfigPath
+        )
+
+        // `baseUrl` can come from extended tsconfigs. Rewrite paths from the
+        // fully-resolved baseUrl and remove it so TS6 deprecation checks do not
+        // fail type checking.
+        result.options.paths = rewritePathAliasesWithoutBaseUrl(
+          normalizedBaseUrl,
+          result.options.paths
+        ) as import('typescript').MapLike<string[]>
+        delete (result.options as { baseUrl?: unknown }).baseUrl
+      }
+    }
+
     if (result.errors) {
       result.errors = result.errors.filter(
         ({ code }) =>

PATCH
