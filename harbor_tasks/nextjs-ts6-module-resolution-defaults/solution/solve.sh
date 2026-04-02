#!/usr/bin/env bash
set -euo pipefail

cd /workspace/repo

# Idempotency check: if preferBundlerResolution already exists, patch is applied
if grep -q 'preferBundlerResolution' packages/next/src/lib/typescript/writeConfigurationDefaults.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts b/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
index a775b122bce687..8b7a907934b4dd 100644
--- a/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
+++ b/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts
@@ -1,10 +1,36 @@
 import { bold, cyan } from '../picocolors'
 import os from 'os'
 import path from 'path'
+import semver from 'next/dist/compiled/semver'

 import { FatalError } from '../fatal-error'
 import isError from '../is-error'

+function resolvePathAliasTarget(baseUrl: string, target: string): string {
+  if (
+    path.isAbsolute(target) ||
+    target.startsWith('./') ||
+    target.startsWith('../')
+  ) {
+    return target
+  }
+
+  if (baseUrl === '.' || baseUrl === './') {
+    return `./${target}`
+  }
+
+  const resolvedTarget = path.join(baseUrl, target)
+  if (
+    path.isAbsolute(resolvedTarget) ||
+    resolvedTarget.startsWith('./') ||
+    resolvedTarget.startsWith('../')
+  ) {
+    return resolvedTarget
+  }
+
+  return `./${resolvedTarget}`
+}
+
 export async function getTypeScriptConfiguration(
   typescript: typeof import('typescript'),
   tsConfigPath: string,
@@ -28,6 +54,66 @@ export async function getTypeScriptConfiguration(
     }

     let configToParse: any = config
+    if (semver.gte(typescript.version, '6.0.0')) {
+      const target = configToParse.compilerOptions?.target
+      if (
+        typeof target === 'string' &&
+        (target.toLowerCase() === 'es3' || target.toLowerCase() === 'es5')
+      ) {
+        const { target: _target, ...restCompilerOptions } =
+          configToParse.compilerOptions ?? {}
+
+        // TypeScript 6 deprecates ES3/ES5 targets. Rewrite deprecated
+        // targets in-memory to keep typechecking working without requiring
+        // `ignoreDeprecations`.
+        configToParse = {
+          ...configToParse,
+          compilerOptions: {
+            ...restCompilerOptions,
+            target: 'es2015',
+          },
+        }
+      }
+
+      const baseUrl = configToParse.compilerOptions?.baseUrl
+      const hasBaseUrl = typeof baseUrl === 'string' && baseUrl.length > 0
+
+      if (hasBaseUrl) {
+        const originalPaths = configToParse.compilerOptions?.paths
+        const rewrittenPaths: Record<string, unknown> =
+          originalPaths && typeof originalPaths === 'object'
+            ? Object.fromEntries(
+                Object.entries(originalPaths).map(([key, values]) => [
+                  key,
+                  Array.isArray(values)
+                    ? values.map((value) =>
+                        typeof value === 'string'
+                          ? resolvePathAliasTarget(baseUrl, value)
+                          : value
+                      )
+                    : values,
+                ])
+              )
+            : {
+                '*': [resolvePathAliasTarget(baseUrl, '*')],
+              }
+        if (!Object.prototype.hasOwnProperty.call(rewrittenPaths, '*')) {
+          rewrittenPaths['*'] = [resolvePathAliasTarget(baseUrl, '*')]
+        }
+        const { baseUrl: _baseUrl, ...restCompilerOptions } =
+          configToParse.compilerOptions ?? {}
+
+        // TypeScript 6 deprecates `baseUrl`; rewrite aliases to explicit
+        // relative paths so path mapping still works without this option.
+        configToParse = {
+          ...configToParse,
+          compilerOptions: {
+            ...restCompilerOptions,
+            paths: rewrittenPaths,
+          },
+        }
+      }
+    }

     const result = typescript.parseJsonConfigFileContent(
       configToParse,
diff --git a/packages/next/src/lib/typescript/writeConfigurationDefaults.ts b/packages/next/src/lib/typescript/writeConfigurationDefaults.ts
index c4dfc0e0f00df4..23772c795f7aec 100644
--- a/packages/next/src/lib/typescript/writeConfigurationDefaults.ts
+++ b/packages/next/src/lib/typescript/writeConfigurationDefaults.ts
@@ -33,9 +33,18 @@ function getDesiredCompilerOptions(

   // ModuleResolutionKind
   const moduleResolutionKindBundler = 'bundler'
-  const moduleResolutionKindNode10 = 'node10'
+  const moduleResolutionKindNode16 = 'node16'
+  const moduleResolutionKindNodeNext = 'nodenext'
   const moduleResolutionKindNode12 = 'node12'
-  const moduleResolutionKindNodeJs = 'node'
+  const moduleResolutionKindNode = 'node'
+  const configuredModule =
+    typeof userTsConfig?.compilerOptions?.module === 'string'
+      ? userTsConfig.compilerOptions.module.toLowerCase()
+      : undefined
+  const preferBundlerResolution =
+    semver.gte(typescriptVersion, '5.0.0') &&
+    configuredModule !== moduleKindCommonJS &&
+    configuredModule !== moduleKindAMD

   // Jsx
   const jsxEmitReactJSX = 'react-jsx'
@@ -89,21 +98,29 @@ function getDesiredCompilerOptions(
             reason: 'requirement for SWC / babel',
           },
           moduleResolution: {
-            // In TypeScript 5.0, `NodeJs` has renamed to `Node10`
-            parsedValue: moduleResolutionKindBundler,
+            parsedValue: preferBundlerResolution
+              ? moduleResolutionKindBundler
+              : moduleResolutionKindNode,
             // All of these values work:
-            parsedValues: [
-              moduleResolutionKindNode10,
-              moduleResolutionKindNodeJs,
-              // only newer TypeScript versions have this field, it
-              // will be filtered for new versions of TypeScript
-              moduleResolutionKindNode12,
-              moduleKindNode16,
-              moduleKindNodeNext,
-              moduleResolutionKindBundler,
-            ].filter((val) => typeof val !== 'undefined'),
-            value: 'node',
-            reason: 'to match webpack resolution',
+            parsedValues: preferBundlerResolution
+              ? [
+                  moduleResolutionKindNode16,
+                  moduleResolutionKindNodeNext,
+                  moduleResolutionKindBundler,
+                ]
+              : [
+                  moduleResolutionKindNode,
+                  // only older TypeScript versions have this field
+                  moduleResolutionKindNode12,
+                  moduleResolutionKindNode16,
+                  moduleResolutionKindNodeNext,
+                ],
+            value: preferBundlerResolution
+              ? moduleResolutionKindBundler
+              : moduleResolutionKindNode,
+            reason: preferBundlerResolution
+              ? 'to match modern bundler resolution'
+              : 'to match webpack resolution',
           },
           resolveJsonModule: {
             value: true,
@@ -161,9 +178,12 @@ export function getRequiredConfiguration(
         import('typescript').ModuleResolutionKind
       > = {
         bundler: typescript.ModuleResolutionKind.Bundler,
-        node10: typescript.ModuleResolutionKind.Node10,
+        node16: typescript.ModuleResolutionKind.Node16,
+        nodenext: typescript.ModuleResolutionKind.NodeNext,
         node12: (typescript.ModuleResolutionKind as any).Node12,
-        node: typescript.ModuleResolutionKind.NodeJs,
+        node:
+          (typescript.ModuleResolutionKind as any).Node10 ??
+          typescript.ModuleResolutionKind.NodeJs,
       }
       res[optionKey] = moduleResolutionMap[value.toLowerCase()] ?? value
     } else if (optionKey === 'jsx' && typeof value === 'string') {

PATCH

echo "Patch applied successfully."
