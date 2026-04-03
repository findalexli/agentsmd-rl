#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'if (params.submit || params.slowly)' packages/playwright-core/src/tools/backend/keyboard.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/backend/keyboard.ts b/packages/playwright-core/src/tools/backend/keyboard.ts
index 91b21999d749b..7fc8b5b0188f5 100644
--- a/packages/playwright-core/src/tools/backend/keyboard.ts
+++ b/packages/playwright-core/src/tools/backend/keyboard.ts
@@ -94,7 +94,7 @@ const type = defineTabTool({
     const { locator, resolved } = await tab.refLocator(params);
     const secret = tab.context.lookupSecret(params.text);

-    await tab.waitForCompletion(async () => {
+    const action = async () => {
       if (params.slowly) {
         response.setIncludeSnapshot();
         response.addCode(`await page.${resolved}.pressSequentially(${secret.code});`);
@@ -109,7 +109,12 @@ const type = defineTabTool({
         response.addCode(`await page.${resolved}.press('Enter');`);
         await locator.press('Enter', tab.actionTimeoutOptions);
       }
-    });
+    };
+
+    if (params.submit || params.slowly)
+      await tab.waitForCompletion(action);
+    else
+      await action();
   },
 });

diff --git a/packages/playwright-core/src/tools/backend/mouse.ts b/packages/playwright-core/src/tools/backend/mouse.ts
index f0cdc67c5baa3..bfdb29679cfa6 100644
--- a/packages/playwright-core/src/tools/backend/mouse.ts
+++ b/packages/playwright-core/src/tools/backend/mouse.ts
@@ -35,9 +35,7 @@ const mouseMove = defineTabTool({
     response.addCode(`// Move mouse to (${params.x}, ${params.y})`);
     response.addCode(`await page.mouse.move(${params.x}, ${params.y});`);

-    await tab.waitForCompletion(async () => {
-      await tab.page.mouse.move(params.x, params.y);
-    });
+    await tab.page.mouse.move(params.x, params.y);
   },
 });

diff --git a/packages/playwright-core/src/tools/backend/snapshot.ts b/packages/playwright-core/src/tools/backend/snapshot.ts
index e4982abae5ff5..2fced17c98133 100644
--- a/packages/playwright-core/src/tools/backend/snapshot.ts
+++ b/packages/playwright-core/src/tools/backend/snapshot.ts
@@ -135,9 +135,7 @@ const hover = defineTabTool({
     const { locator, resolved } = await tab.refLocator(params);
     response.addCode(`await page.${resolved}.hover();`);

-    await tab.waitForCompletion(async () => {
-      await locator.hover(tab.actionTimeoutOptions);
-    });
+    await locator.hover(tab.actionTimeoutOptions);
   },
 });

@@ -161,9 +159,7 @@ const selectOption = defineTabTool({
     const { locator, resolved } = await tab.refLocator(params);
     response.addCode(`await page.${resolved}.selectOption(${formatObject(params.values)});`);

-    await tab.waitForCompletion(async () => {
-      await locator.selectOption(params.values, tab.actionTimeoutOptions);
-    });
+    await locator.selectOption(params.values, tab.actionTimeoutOptions);
   },
 });

diff --git a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
index 33bc1bc3612f7..77a0c0eae0f8e 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
@@ -35,7 +35,8 @@ playwright-cli goto https://playwright.dev
 playwright-cli type "search query"
 playwright-cli click e3
 playwright-cli dblclick e7
-playwright-cli fill e5 "user@example.com"
+# --submit presses Enter after filling the element
+playwright-cli fill e5 "user@example.com"  --submit
 playwright-cli drag e2 e8
 playwright-cli hover e4
 playwright-cli select e9 "option-value"

PATCH

echo "Patch applied successfully."
