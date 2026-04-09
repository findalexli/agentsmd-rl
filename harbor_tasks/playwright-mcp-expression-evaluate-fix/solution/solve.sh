#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "const expression = params.function" packages/playwright-core/src/tools/backend/evaluate.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/backend/evaluate.ts b/packages/playwright-core/src/tools/backend/evaluate.ts
index 9e41bc9be40b6..0831ac3b65d0a 100644
--- a/packages/playwright-core/src/tools/backend/evaluate.ts
+++ b/packages/playwright-core/src/tools/backend/evaluate.ts
@@ -41,21 +41,35 @@ const evaluate = defineTabTool({

   handle: async (tab, params, response) => {
     let locator: Awaited<ReturnType<Tab['refLocator']>> | undefined;
-    if (!params.function.includes('=>'))
-      params.function = `() => (${params.function})`;
-    if (params.ref) {
+    const expression = params.function;
+    if (params.ref)
       locator = await tab.refLocator({ ref: params.ref, selector: params.selector, element: params.element || 'element' });
-      response.addCode(`await page.${locator.resolved}.evaluate(${escapeWithQuotes(params.function)});`);
-    } else {
-      response.addCode(`await page.evaluate(${escapeWithQuotes(params.function)});`);
-    }

     await tab.waitForCompletion(async () => {
-      // eslint-disable-next-line no-restricted-syntax
-      const func = new Function() as any;
-      func.toString = () => params.function;
-      const result = locator?.locator ? await locator?.locator.evaluate(func) : await tab.page.evaluate(func);
-      const text = JSON.stringify(result, null, 2) || 'undefined';
+      let evalResult: { result: unknown, isFunction: boolean };
+      if (locator?.locator) {
+        evalResult = await locator.locator.evaluate(async (element, expr) => {
+          const value = eval(`(${expr})`);
+          const isFunction = typeof value === 'function';
+          const result = await (isFunction ? value(element) : value);
+          return { result, isFunction };
+        }, expression);
+      } else {
+        evalResult = await tab.page.evaluate(async expr => {
+          const value = eval(`(${expr})`);
+          const isFunction = typeof value === 'function';
+          const result = await (isFunction ? value() : value);
+          return { result, isFunction };
+        }, expression);
+      }
+
+      const codeExpression = evalResult.isFunction ? expression : `() => (${expression})`;
+      if (locator)
+        response.addCode(`await page.${locator.resolved}.evaluate(${escapeWithQuotes(codeExpression)});`);
+      else
+        response.addCode(`await page.evaluate(${escapeWithQuotes(codeExpression)});`);
+
+      const text = JSON.stringify(evalResult.result, null, 2) ?? 'undefined';
       await response.addResult('Evaluation result', text, { prefix: 'result', ext: 'json', suggestedFilename: params.filename });
     });
   },

PATCH

echo "Patch applied successfully."
