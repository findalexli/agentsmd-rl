#!/usr/bin/env bash
set -euo pipefail

cd /workspace/expo

# Idempotent: skip if already applied
if grep -q 'transformImportMeta?: boolean' packages/babel-preset-expo/src/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/babel-preset-expo/README.md b/packages/babel-preset-expo/README.md
index 4ca77209aa1e37..c423155f372bef 100644
--- a/packages/babel-preset-expo/README.md
+++ b/packages/babel-preset-expo/README.md
@@ -152,11 +152,11 @@ If `undefined` (default), this will be set automatically via `caller.supportsSta

 Changes the engine preset in `@react-native/babel-preset` based on the JavaScript engine that is being targeted. In Expo SDK 50 and greater, this is automatically set based on the [`jsEngine`](https://docs.expo.dev/versions/latest/config/app/#jsengine) option in your `app.json`.

-### `unstable_transformImportMeta`
+### `transformImportMeta`

-Enable that transform that converts `import.meta` to `globalThis.__ExpoImportMetaRegistry`, defaults to `false` in client bundles and `true` for server bundles.
+Enable transform that converts `import.meta` to `globalThis.__ExpoImportMetaRegistry`. Defaults to `true`.

-> **Note:** Use this option at your own risk. If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.
+> **Note:** If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.

 ### `enableBabelRuntime`

diff --git a/packages/babel-preset-expo/build/import-meta-transform-plugin.js b/packages/babel-preset-expo/build/import-meta-transform-plugin.js
index 394aa6660205db..326a43cc99aa07 100644
--- a/packages/babel-preset-expo/build/import-meta-transform-plugin.js
+++ b/packages/babel-preset-expo/build/import-meta-transform-plugin.js
@@ -15,7 +15,7 @@ function expoImportMetaTransformPluginFactory(pluginEnabled) {
                     if (node.meta.name === 'import' && node.property.name === 'meta') {
                         if (!pluginEnabled) {
                             if (platform !== 'web') {
-                                throw path.buildCodeFrameError('`import.meta` is not supported in Hermes. Enable the polyfill `unstable_transformImportMeta` in babel-preset-expo to use this syntax.');
+                                throw path.buildCodeFrameError('`import.meta` is not supported in Hermes. Enable the polyfill `transformImportMeta` in babel-preset-expo to use this syntax.');
                             }
                             return;
                         }
diff --git a/packages/babel-preset-expo/build/index.d.ts b/packages/babel-preset-expo/build/index.d.ts
index e78491d10a95b5..6e011a57064a4d 100644
--- a/packages/babel-preset-expo/build/index.d.ts
+++ b/packages/babel-preset-expo/build/index.d.ts
@@ -33,11 +33,11 @@ type BabelPresetExpoPlatformOptions = {
     /**
      * Enable that transform that converts `import.meta` to `globalThis.__ExpoImportMetaRegistry`.
      *
-     * > **Note:** Use this option at your own risk. If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.
+     * > **Note:** If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.
      *
-     * @default `false` on client and `true` on server.
+     * @default `true`
      */
-    unstable_transformImportMeta?: boolean;
+    transformImportMeta?: boolean;
 };
 export type BabelPresetExpoOptions = BabelPresetExpoPlatformOptions & {
     /** Web-specific settings. */
diff --git a/packages/babel-preset-expo/build/index.js b/packages/babel-preset-expo/build/index.js
index 1d1f89d556bef0..26cc2c278f50ea 100644
--- a/packages/babel-preset-expo/build/index.js
+++ b/packages/babel-preset-expo/build/index.js
@@ -223,7 +223,7 @@ function babelPresetExpo(api, options = {}) {
     if (platformOptions.disableImportExportTransform) {
         extraPlugins.push([require('./detect-dynamic-exports').detectDynamicExports]);
     }
-    const polyfillImportMeta = platformOptions.unstable_transformImportMeta ?? isServerEnv;
+    const polyfillImportMeta = platformOptions.transformImportMeta !== false;
     extraPlugins.push((0, import_meta_transform_plugin_1.expoImportMetaTransformPluginFactory)(polyfillImportMeta === true));
     return {
         presets: [
diff --git a/packages/babel-preset-expo/src/import-meta-transform-plugin.ts b/packages/babel-preset-expo/src/import-meta-transform-plugin.ts
index d45b5ed52cd296..30e2b9540bd3aa 100644
--- a/packages/babel-preset-expo/src/import-meta-transform-plugin.ts
+++ b/packages/babel-preset-expo/src/import-meta-transform-plugin.ts
@@ -18,7 +18,7 @@ export function expoImportMetaTransformPluginFactory(pluginEnabled: boolean) {
             if (!pluginEnabled) {
               if (platform !== 'web') {
                 throw path.buildCodeFrameError(
-                  '`import.meta` is not supported in Hermes. Enable the polyfill `unstable_transformImportMeta` in babel-preset-expo to use this syntax.'
+                  '`import.meta` is not supported in Hermes. Enable the polyfill `transformImportMeta` in babel-preset-expo to use this syntax.'
                 );
               }
               return;
diff --git a/packages/babel-preset-expo/src/index.ts b/packages/babel-preset-expo/src/index.ts
index a2d2cc59c1fcc2..ed73aed08e2051 100644
--- a/packages/babel-preset-expo/src/index.ts
+++ b/packages/babel-preset-expo/src/index.ts
@@ -71,11 +71,11 @@ type BabelPresetExpoPlatformOptions = {
   /**
    * Enable that transform that converts `import.meta` to `globalThis.__ExpoImportMetaRegistry`.
    *
-   * > **Note:** Use this option at your own risk. If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.
+   * > **Note:** If the JavaScript engine supports `import.meta` natively, this transformation may interfere with the native implementation.
    *
-   * @default `false` on client and `true` on server.
+   * @default `true`
    */
-  unstable_transformImportMeta?: boolean;
+  transformImportMeta?: boolean;
 };

 export type BabelPresetExpoOptions = BabelPresetExpoPlatformOptions & {
@@ -338,7 +338,7 @@ function babelPresetExpo(api: ConfigAPI, options: BabelPresetExpoOptions = {}):
     extraPlugins.push([require('./detect-dynamic-exports').detectDynamicExports]);
   }

-  const polyfillImportMeta = platformOptions.unstable_transformImportMeta ?? isServerEnv;
+  const polyfillImportMeta = platformOptions.transformImportMeta !== false;

   extraPlugins.push(expoImportMetaTransformPluginFactory(polyfillImportMeta === true));


PATCH

echo "Patch applied successfully."
