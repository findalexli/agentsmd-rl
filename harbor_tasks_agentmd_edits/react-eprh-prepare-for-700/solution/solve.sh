#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q "version: '7.0.0'" packages/eslint-plugin-react-hooks/src/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/ReactVersions.js b/ReactVersions.js
index c657857cbbc8..ba7b222bf068 100644
--- a/ReactVersions.js
+++ b/ReactVersions.js
@@ -33,7 +33,7 @@ const canaryChannelLabel = 'canary';
 const rcNumber = 0;

 const stablePackages = {
-  'eslint-plugin-react-hooks': '6.2.0',
+  'eslint-plugin-react-hooks': '7.0.0',
   'jest-react': '0.18.0',
   react: ReactVersion,
   'react-art': ReactVersion,
diff --git a/fixtures/eslint-v6/.eslintrc.json b/fixtures/eslint-v6/.eslintrc.json
index f76a20fea576..672da7a085a6 100644
--- a/fixtures/eslint-v6/.eslintrc.json
+++ b/fixtures/eslint-v6/.eslintrc.json
@@ -1,6 +1,6 @@
 {
   "root": true,
-  "extends": ["plugin:react-hooks/recommended-latest-legacy"],
+  "extends": ["plugin:react-hooks/recommended"],
   "parserOptions": {
     "ecmaVersion": 2020,
     "sourceType": "module",
diff --git a/fixtures/eslint-v7/.eslintrc.json b/fixtures/eslint-v7/.eslintrc.json
index f76a20fea576..672da7a085a6 100644
--- a/fixtures/eslint-v7/.eslintrc.json
+++ b/fixtures/eslint-v7/.eslintrc.json
@@ -1,6 +1,6 @@
 {
   "root": true,
-  "extends": ["plugin:react-hooks/recommended-latest-legacy"],
+  "extends": ["plugin:react-hooks/recommended"],
   "parserOptions": {
     "ecmaVersion": 2020,
     "sourceType": "module",
diff --git a/fixtures/eslint-v8/.eslintrc.json b/fixtures/eslint-v8/.eslintrc.json
index f76a20fea576..672da7a085a6 100644
--- a/fixtures/eslint-v8/.eslintrc.json
+++ b/fixtures/eslint-v8/.eslintrc.json
@@ -1,6 +1,6 @@
 {
   "root": true,
-  "extends": ["plugin:react-hooks/recommended-latest-legacy"],
+  "extends": ["plugin:react-hooks/recommended"],
   "parserOptions": {
     "ecmaVersion": 2020,
     "sourceType": "module",
diff --git a/packages/eslint-plugin-react-hooks/CHANGELOG.md b/packages/eslint-plugin-react-hooks/CHANGELOG.md
index cd376cd4dca0..0aba9e00561f 100644
--- a/packages/eslint-plugin-react-hooks/CHANGELOG.md
+++ b/packages/eslint-plugin-react-hooks/CHANGELOG.md
@@ -1,3 +1,9 @@
+## 7.0.0
+
+This release slims down presets to just 2 configurations (`recommended` and `recommended-latest`), and all compiler rules are enabled by default.
+
+- **Breaking:** Removed `recommended-latest-legacy` and `flat/recommended` configs. The plugin now provides `recommended` (legacy and flat configs with all recommended rules),  and `recommended-latest` (legacy and flat configs with all recommended rules plus new bleeding edge experimental compiler rules). ([@poteto](https://github.com/poteto) in [#34757](https://github.com/facebook/react/pull/34757))
+
 ## 6.1.1

 **Note:** 6.1.0 accidentally allowed use of `recommended` without flat config, causing errors when used with ESLint v9's `defineConfig()` helper. This has been fixed in 6.1.1.
diff --git a/packages/eslint-plugin-react-hooks/README.md b/packages/eslint-plugin-react-hooks/README.md
index afd89ab2263a..a1b4bcabb59f 100644
--- a/packages/eslint-plugin-react-hooks/README.md
+++ b/packages/eslint-plugin-react-hooks/README.md
@@ -4,8 +4,6 @@ The official ESLint plugin for [React](https://react.dev) which enforces the [Ru

 ## Installation

-**Note: If you're using Create React App, please use `react-scripts` >= 3 instead of adding it directly.**
-
 Assuming you already have ESLint installed, run:

 ```sh
@@ -18,9 +16,7 @@ yarn add eslint-plugin-react-hooks --dev

 ### Flat Config (eslint.config.js|ts)

-#### >= 6.0.0
-
-For users of 6.0 and beyond, add the `recommended` config.
+Add the `recommended` config for all recommended rules:

 ```js
 // eslint.config.js
@@ -28,61 +24,32 @@ import reactHooks from 'eslint-plugin-react-hooks';
 import { defineConfig } from 'eslint/config';

 export default defineConfig([
-  {
-    files: ["src/**/*.{js,jsx,ts,tsx}"],
-    plugins: {
-      'react-hooks': reactHooks,
-    },
-    extends: ['react-hooks/recommended'],
-  },
+  reactHooks.configs.flat.recommended,
 ]);
 ```

-#### 5.2.0
-
-For users of 5.2.0 (the first version with flat config support), add the `recommended-latest` config.
+If you want to try bleeding edge experimental compiler rules, use `recommended-latest`.

 ```js
+// eslint.config.js
 import reactHooks from 'eslint-plugin-react-hooks';
 import { defineConfig } from 'eslint/config';

 export default defineConfig([
-  {
-    files: ["src/**/*.{js,jsx,ts,tsx}"],
-    plugins: {
-      'react-hooks': reactHooks,
-    },
-    extends: ['react-hooks/recommended-latest'],
-  },
+  reactHooks.configs.flat['recommended-latest'],
 ]);
 ```

 ### Legacy Config (.eslintrc)

-#### >= 5.2.0
-
-If you are still using ESLint below 9.0.0, you can use `recommended-legacy` for accessing a legacy version of the recommended config.
+If you are still using ESLint below 9.0.0, the `recommended` preset can also be used to enable all recommended rules.

 ```js
 {
-  "extends": [
-    // ...
-    "plugin:react-hooks/recommended-legacy"
-  ]
+  "extends": ["plugin:react-hooks/recommended"],
+  // ...
 }
-```
-
-#### < 5.2.0
-
-If you're using a version earlier than 5.2.0, the legacy config was simply `recommended`.

-```js
-{
-  "extends": [
-    // ...
-    "plugin:react-hooks/recommended"
-  ]
-}
 ```

 ### Custom Configuration
@@ -92,7 +59,7 @@ If you want more fine-grained configuration, you can instead choose to enable sp
 #### Flat Config (eslint.config.js|ts)

 ```js
-import * as reactHooks from 'eslint-plugin-react-hooks';
+import reactHooks from 'eslint-plugin-react-hooks';

 export default [
   {
@@ -100,8 +67,26 @@ export default [
     plugins: { 'react-hooks': reactHooks },
     // ...
     rules: {
+      // Core hooks rules
       'react-hooks/rules-of-hooks': 'error',
       'react-hooks/exhaustive-deps': 'warn',
+
+      // React Compiler rules
+      'react-hooks/config': 'error',
+      'react-hooks/error-boundaries': 'error',
+      'react-hooks/component-hook-factories': 'error',
+      'react-hooks/gating': 'error',
+      'react-hooks/globals': 'error',
+      'react-hooks/immutability': 'error',
+      'react-hooks/preserve-manual-memoization': 'error',
+      'react-hooks/purity': 'error',
+      'react-hooks/refs': 'error',
+      'react-hooks/set-state-in-effect': 'error',
+      'react-hooks/set-state-in-render': 'error',
+      'react-hooks/static-components': 'error',
+      'react-hooks/unsupported-syntax': 'warn',
+      'react-hooks/use-memo': 'error',
+      'react-hooks/incompatible-library': 'warn',
     }
   },
 ];
@@ -116,8 +101,26 @@ export default [
   ],
   "rules": {
     // ...
+    // Core hooks rules
     "react-hooks/rules-of-hooks": "error",
-    "react-hooks/exhaustive-deps": "warn"
+    "react-hooks/exhaustive-deps": "warn",
+
+    // React Compiler rules
+    "react-hooks/config": "error",
+    "react-hooks/error-boundaries": "error",
+    "react-hooks/component-hook-factories": "error",
+    "react-hooks/gating": "error",
+    "react-hooks/globals": "error",
+    "react-hooks/immutability": "error",
+    "react-hooks/preserve-manual-memoization": "error",
+    "react-hooks/purity": "error",
+    "react-hooks/refs": "error",
+    "react-hooks/set-state-in-effect": "error",
+    "react-hooks/set-state-in-render": "error",
+    "react-hooks/static-components": "error",
+    "react-hooks/unsupported-syntax": "warn",
+    "react-hooks/use-memo": "error",
+    "react-hooks/incompatible-library": "warn"
   }
 }
 ```
diff --git a/packages/eslint-plugin-react-hooks/package.json b/packages/eslint-plugin-react-hooks/package.json
index ea39fb490324..a22448f11c78 100644
--- a/packages/eslint-plugin-react-hooks/package.json
+++ b/packages/eslint-plugin-react-hooks/package.json
@@ -1,7 +1,7 @@
 {
   "name": "eslint-plugin-react-hooks",
   "description": "ESLint rules for React Hooks",
-  "version": "5.2.0",
+  "version": "7.0.0",
   "repository": {
     "type": "git",
     "url": "https://github.com/facebook/react.git",
diff --git a/packages/eslint-plugin-react-hooks/src/index.ts b/packages/eslint-plugin-react-hooks/src/index.ts
index 838b1081a7ef..2de0141a8e55 100644
--- a/packages/eslint-plugin-react-hooks/src/index.ts
+++ b/packages/eslint-plugin-react-hooks/src/index.ts
@@ -44,55 +44,32 @@ const allRuleConfigs: Linter.RulesRecord = {
 const plugins = ['react-hooks'];

 type ReactHooksFlatConfig = {
-  plugins: Record<string, any>;
+  plugins: {react: any};
   rules: Linter.RulesRecord;
 };

 const configs = {
-  'recommended-legacy': {
-    plugins,
-    rules: basicRuleConfigs,
-  },
-  'recommended-latest-legacy': {
+  recommended: {
     plugins,
     rules: allRuleConfigs,
   },
-  'flat/recommended': {
-    plugins,
-    rules: basicRuleConfigs,
-  },
   'recommended-latest': {
     plugins,
     rules: allRuleConfigs,
   },
-  recommended: {
-    plugins,
-    rules: basicRuleConfigs,
-  },
   flat: {} as Record<string, ReactHooksFlatConfig>,
 };

 const plugin = {
   meta: {
     name: 'eslint-plugin-react-hooks',
+    version: '7.0.0',
   },
   rules,
   configs,
 };

 Object.assign(configs.flat, {
-  'recommended-legacy': {
-    plugins: {'react-hooks': plugin},
-    rules: configs['recommended-legacy'].rules,
-  },
-  'recommended-latest-legacy': {
-    plugins: {'react-hooks': plugin},
-    rules: configs['recommended-latest-legacy'].rules,
-  },
-  'flat/recommended': {
-    plugins: {'react-hooks': plugin},
-    rules: configs['flat/recommended'].rules,
-  },
   'recommended-latest': {
     plugins: {'react-hooks': plugin},
     rules: configs['recommended-latest'].rules,

PATCH

echo "Patch applied successfully."
