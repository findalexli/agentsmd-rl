#!/bin/bash
set -e

cd /workspace/mantine

# Apply the gold patch from PR #8781
cat <<'PATCH' | git apply -
diff --git a/.github/workflows/npm_test.yml b/.github/workflows/npm_test.yml
index 1e13b3d9b3..d050711c2f 100644
--- a/.github/workflows/npm_test.yml
+++ b/.github/workflows/npm_test.yml
@@ -15,8 +15,8 @@ jobs:
   test_pull_request:
     runs-on: ubuntu-latest
     steps:
-      - uses: actions/checkout@v5
-      - uses: actions/setup-node@v5
+      - uses: actions/checkout@v6
+      - uses: actions/setup-node@v6
         with:
           node-version-file: '.nvmrc'
           cache: 'yarn'

diff --git a/apps/help.mantine.dev/@types/css.d.ts b/apps/help.mantine.dev/@types/css.d.ts
index ab57c34529..591b6b3bf8 100644
--- a/apps/help.mantine.dev/@types/css.d.ts
+++ b/apps/help.mantine.dev/@types/css.d.ts
@@ -1,4 +1,4 @@
-declare module '*.module.css' {
+declare module '*.css' {
   const classes: Record<string, string>;
   export default classes;
 }

diff --git a/packages/@mantine/core/src/components/Select/Select.tsx b/packages/@mantine/core/src/components/Select/Select.tsx
index 4d7d890204..c63bb71995 100644
--- a/packages/@mantine/core/src/components/Select/Select.tsx
+++ b/packages/@mantine/core/src/components/Select/Select.tsx
@@ -319,8 +319,7 @@ export const Select = genericFactory<SelectFactory>((_props) => {
           const nextValue = optionLockup ? optionLockup.value : null;

           nextValue !== _value && setValue(nextValue as any, optionLockup);
-          !controlled &&
-            handleSearchChange(nextValue != null ? optionLockup?.label || '' : '');
+          !controlled && handleSearchChange(nextValue != null ? optionLockup?.label || '' : '');
           combobox.closeDropdown();
         }}
         {...comboboxProps}

diff --git a/packages/@mantine/form/src/use-form.ts b/packages/@mantine/form/src/use-form.ts
index 1f7b3080a5..74b4eaafb4 100644
--- a/packages/@mantine/form/src/use-form.ts
+++ b/packages/@mantine/form/src/use-form.ts
@@ -8,6 +8,7 @@ import { useFormValidating } from './hooks/use-form-validating/use-form-validat
 import { useFormValues } from './hooks/use-form-values/use-form-values';
 import { useFormWatch } from './hooks/use-form-watch/use-form-watch';
 import { getDataPath, getPath } from './paths';
+import type { FormPathValue, LooseKeys } from './paths.types';
 import {
   FormErrors,
   FormRulesRecord,
@@ -101,8 +102,14 @@ export function useForm<
       if (value !== previousValue) {
         $watch.subscribers.current[path]?.forEach((cb) =>
           cb({
-            previousValue: getPath(path, previousValues),
-            value: getPath(path, $values.refValues.current),
+            previousValue: getPath(path, previousValues) as FormPathValue<
+              Values,
+              LooseKeys<Values>
+            >,
+            value: getPath(path, $values.refValues.current) as FormPathValue<
+              Values,
+              LooseKeys<Values>
+            >,
             touched: $status.isTouched(path),
             dirty: $status.isDirty(path),
           })

diff --git a/packages/@mantinex/colors-generator/tsconfig.json b/packages/@mantinex/colors-generator/tsconfig.json
index 1070fe315b..ba0efb9773 100644
--- a/packages/@mantinex/colors-generator/tsconfig.json
+++ b/packages/@mantinex/colors-generator/tsconfig.json
@@ -9,7 +9,7 @@
     "target": "ES2015",
     "lib": ["DOM", "ESNext"],
     "module": "ESNext",
-    "moduleResolution": "Node",
+    "moduleResolution": "bundler",
     "jsx": "react-jsx",
     "emitDeclarationOnly": true,
     "resolveJsonModule": true,
PATCH

echo "Patch applied successfully"

# Idempotency check: verify distinctive line from patch is present
grep -q "import type { FormPathValue, LooseKeys } from './paths.types';" packages/@mantine/form/src/use-form.ts
echo "Idempotency check passed"
