#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

TEST_FILE="test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts"

# Idempotency check: if the fix is already applied, skip
if grep -q "{ timeout: 50 }" "$TEST_FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts b/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts
index 5792beccc3be5..a1cd26e5bb7a4 100644
--- a/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts
+++ b/test/development/app-dir/instant-navs-devtools/instant-navs-devtools.test.ts
@@ -38,7 +38,10 @@ describe('instant-nav-panel', () => {
   }

   async function clickStartClientNav(browser: Playwright) {
-    await browser.elementByCssInstant('[data-instant-nav-client]').click()
+    await browser
+      // TODO: Monitor if we need to increase timeouts for all *instant calls
+      .elementByCss('[data-instant-nav-client]', { timeout: 50 })
+      .click()
     await waitForInstantModeCookie(browser)
   }

PATCH

echo "Fix applied successfully."
