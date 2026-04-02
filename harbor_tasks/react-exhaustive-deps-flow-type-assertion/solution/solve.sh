#!/bin/bash
set -euo pipefail

# Gold patch for react-exhaustive-deps-flow-type-assertion
# PR: facebook/react#35691

REPO_ROOT="/workspace/react"
cd "$REPO_ROOT"

# Check if patch already applied (idempotency check)
# The fix adds a check for GenericTypeAnnotation
if grep -q "dependencyNode.parent?.type === 'GenericTypeAnnotation'" packages/eslint-plugin-react-hooks/src/rules/ExhaustiveDeps.ts 2>/dev/null; then
    echo "Patch already applied (GenericTypeAnnotation check found)"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/packages/eslint-plugin-react-hooks/__tests__/ESLintRuleExhaustiveDeps-test.js b/packages/eslint-plugin-react-hooks/__tests__/ESLintRuleExhaustiveDeps-test.js
index b479ce48521c..29e956d314a2 100644
--- a/packages/eslint-plugin-react-hooks/__tests__/ESLintRuleExhaustiveDeps-test.js
+++ b/packages/eslint-plugin-react-hooks/__tests__/ESLintRuleExhaustiveDeps-test.js
@@ -7913,6 +7913,25 @@ const testsFlow = {
         }
       `,
     },
+    // Flow type aliases in type assertions should not be flagged as missing dependencies
+    {
+      code: normalizeIndent`
+        function MyComponent() {
+          type ColumnKey = 'id' | 'name';
+          type Item = {id: string, name: string};
+
+          const columns = useMemo(
+            () => [
+              {
+                type: 'text',
+                key: 'id',
+              } as TextColumn<ColumnKey, Item>,
+            ],
+            [],
+          );
+        }
+      `,
+    },
   ],
   invalid: [
     {
diff --git a/packages/eslint-plugin-react-hooks/src/rules/ExhaustiveDeps.ts b/packages/eslint-plugin-react-hooks/src/rules/ExhaustiveDeps.ts
index 05321ffb46f6..6b790680608d 100644
--- a/packages/eslint-plugin-react-hooks/src/rules/ExhaustiveDeps.ts
+++ b/packages/eslint-plugin-react-hooks/src/rules/ExhaustiveDeps.ts
@@ -21,7 +21,7 @@ import type {
   VariableDeclarator,
 } from 'estree';

-import { getAdditionalEffectHooksFromSettings } from '../shared/Utils';
+import {getAdditionalEffectHooksFromSettings} from '../shared/Utils';

 type DeclaredDependency = {
   key: string;
@@ -80,7 +80,6 @@ const rule = {
     const rawOptions = context.options && context.options[0];
     const settings = context.settings || {};

-
     // Parse the `additionalHooks` regex.
     // Use rule-level additionalHooks if provided, otherwise fall back to settings
     const additionalHooks =
@@ -565,8 +564,12 @@ const rule = {
             continue;
           }
           // Ignore Flow type parameters
-          // @ts-expect-error We don't have flow types
-          if (def.type === 'TypeParameter') {
+          if (
+            // @ts-expect-error We don't have flow types
+            def.type === 'TypeParameter' ||
+            // @ts-expect-error Flow-specific AST node type
+            dependencyNode.parent?.type === 'GenericTypeAnnotation'
+          ) {
             continue;
           }
 PATCH

echo "Patch applied successfully"
