#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'waitForCompletion' packages/playwright/src/mcp/browser/tools/keyboard.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/playwright/src/mcp/browser/tools/keyboard.ts b/packages/playwright/src/mcp/browser/tools/keyboard.ts
index d6b9bc712ce22..c0901e60c0892 100644
--- a/packages/playwright/src/mcp/browser/tools/keyboard.ts
+++ b/packages/playwright/src/mcp/browser/tools/keyboard.ts
@@ -34,7 +34,14 @@ const press = defineTabTool({
   handle: async (tab, params, response) => {
     response.addCode(`// Press ${params.key}`);
     response.addCode(`await page.keyboard.press('${params.key}');`);
-    await tab.page.keyboard.press(params.key);
+    if (params.key === 'Enter') {
+      response.setIncludeSnapshot();
+      await tab.waitForCompletion(async () => {
+        await tab.page.keyboard.press('Enter');
+      });
+    } else {
+      await tab.page.keyboard.press(params.key);
+    }
   },
 });

diff --git a/packages/playwright/src/mcp/terminal/SKILL.md b/packages/playwright/src/mcp/terminal/SKILL.md
index a4f8489a64a5e..42540bc2ebd6e 100644
--- a/packages/playwright/src/mcp/terminal/SKILL.md
+++ b/packages/playwright/src/mcp/terminal/SKILL.md
@@ -18,9 +18,8 @@ playwright-cli press Enter
 ## Core workflow

 1. Navigate: `playwright-cli open https://example.com`
-2. Snapshot: `playwright-cli snapshot` (returns elements with refs like `ref=e1`, `ref=e2`)
-3. Interact using refs from the snapshot
-4. Re-snapshot after navigation or significant DOM changes
+2. Interact using refs from the snapshot
+3. Re-snapshot after significant changes

PATCH

echo "Patch applied successfully."
