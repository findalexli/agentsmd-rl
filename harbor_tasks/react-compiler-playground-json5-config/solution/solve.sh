#!/bin/bash
set -euo pipefail

cd /workspace/react/compiler/apps/playground

# Check if already patched
if grep -q "parseConfigOverrides" lib/compilation.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt b/compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt
index a012d051ec04..2191397ae126 100644
--- a/compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt
+++ b/compiler/apps/playground/__tests__/e2e/__snapshots__/page.spec.ts/default-config.txt
@@ -1,5 +1,3 @@
-import type { PluginOptions } from
-'babel-plugin-react-compiler/dist';
-({
+{
   //compilationMode: "all"
-} satisfies PluginOptions);
\ No newline at end of file
+}
diff --git a/compiler/apps/playground/__tests__/e2e/page.spec.ts b/compiler/apps/playground/__tests__/e2e/page.spec.ts
index 20596e5d93bf..1f7bf1def137 100644
--- a/compiler/apps/playground/__tests__/e2e/page.spec.ts
+++ b/compiler/apps/playground/__tests__/e2e/page.spec.ts
@@ -237,7 +237,7 @@ test('show internals button toggles correctly', async ({page}) => {
 test('error is displayed when config has syntax error', async ({page}) => {
   const store: Store = {
     source: TEST_SOURCE,
-    config: `compilationMode: `,
+    config: `{ compilationMode: }`,
     showInternals: false,
   };
   const hash = encodeStore(store);
@@ -254,17 +254,17 @@ test('error is displayed when config has syntax error', async ({page}) => {
   const output = text.join('');

   // Remove hidden chars
-  expect(output.replace(/\s+/g, ' ')).toContain('Invalid override format');
+  expect(output.replace(/\s+/g, ' ')).toContain(
+    'Unexpected failure when transforming configs',
+  );
 });

 test('error is displayed when config has validation error', async ({page}) => {
   const store: Store = {
     source: TEST_SOURCE,
-    config: `import type { PluginOptions } from 'babel-plugin-react-compiler/dist';
-
-({
+    config: `{
   compilationMode: "123"
-} satisfies PluginOptions);`,
+}`,
     showInternals: false,
   };
   const hash = encodeStore(store);
diff --git a/compiler/apps/playground/lib/compilation.ts b/compiler/apps/playground/lib/compilation.ts
index f668c05dde2a..b2bee8bd66d4 100644
--- a/compiler/apps/playground/lib/compilation.ts
+++ b/compiler/apps/playground/lib/compilation.ts
@@ -25,6 +25,7 @@ import BabelPluginReactCompiler, {
   type LoggerEvent,
 } from 'babel-plugin-react-compiler';
 import {transformFromAstSync} from '@babel/core';
+import JSON5 from 'json5';
 import type {
   CompilerOutput,
   CompilerTransformOutput,
@@ -126,6 +127,14 @@ const COMMON_HOOKS: Array<[string, Hook]> = [
   ],
 ];

+export function parseConfigOverrides(configOverrides: string): any {
+  const trimmed = configOverrides.trim();
+  if (!trimmed) {
+    return {};
+  }
+  return JSON5.parse(trimmed);
+}
+
 function parseOptions(
   source: string,
   mode: 'compiler' | 'linter',
@@ -156,16 +165,7 @@ function parseOptions(
   });

   // Parse config overrides from config editor
-  let configOverrideOptions: any = {};
-  const configMatch = configOverrides.match(/^\s*import.*?\n\n\((.*)\)/s);
-  if (configOverrides.trim()) {
-    if (configMatch && configMatch[1]) {
-      const configString = configMatch[1].replace(/satisfies.*$/, '').trim();
-      configOverrideOptions = new Function(`return (${configString})`)();
-    } else {
-      throw new Error('Invalid override format');
-    }
-  }
+  const configOverrideOptions = parseConfigOverrides(configOverrides);

   const opts: PluginOptions = parsePluginOptions({
     ...parsedPragmaOptions,
diff --git a/compiler/apps/playground/lib/defaultStore.ts b/compiler/apps/playground/lib/defaultStore.ts
index 2baada0b8179..9711249ff4f5 100644
--- a/compiler/apps/playground/lib/defaultStore.ts
+++ b/compiler/apps/playground/lib/defaultStore.ts
@@ -14,11 +14,9 @@ export default function MyApp() {
 `;

 export const defaultConfig = `\
-import type { PluginOptions } from 'babel-plugin-react-compiler/dist';
-
-({
+{
   //compilationMode: "all"
-} satisfies PluginOptions);`;
+}`;

 export const defaultStore: Store = {
   source: index,
diff --git a/compiler/apps/playground/package.json b/compiler/apps/playground/package.json
index 217153e6a219..65f27158d8f2 100644
--- a/compiler/apps/playground/package.json
+++ b/compiler/apps/playground/package.json
@@ -32,6 +32,7 @@
     "hermes-eslint": "^0.25.0",
     "hermes-parser": "^0.25.0",
     "invariant": "^2.2.4",
+    "json5": "^2.2.3",
     "lru-cache": "^11.2.2",
     "lz-string": "^1.5.0",
     "monaco-editor": "^0.52.0",
PATCH

echo "Patch applied successfully"
