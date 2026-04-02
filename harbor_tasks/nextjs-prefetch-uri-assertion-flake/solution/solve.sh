#!/usr/bin/env bash
set -euo pipefail

FILE="test/e2e/app-dir/app-prefetch/prefetching.test.ts"

# Idempotency: check if the fix is already applied
# Must check for hasElementByCss (NOT hasElementByCssSelector) near accordion-to-dashboard
if grep -q 'retry(async' "$FILE" && grep -q "hasElementByCss('#accordion-to-dashboard')" "$FILE"; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/test/e2e/app-dir/app-prefetch/prefetching.test.ts b/test/e2e/app-dir/app-prefetch/prefetching.test.ts
index 91fdbad1bd9d7..6cceb0f6a23c8 100644
--- a/test/e2e/app-dir/app-prefetch/prefetching.test.ts
+++ b/test/e2e/app-dir/app-prefetch/prefetching.test.ts
@@ -366,9 +366,11 @@ describe('app dir - prefetching', () => {
     await browser.elementById('prefetch-via-link').click()

     // Assert that we're on the homepage (check for accordion since links are hidden)
-    expect(
-      await browser.hasElementByCssSelector('#accordion-to-dashboard')
-    ).toBe(true)
+    await retry(async () => {
+      expect(await browser.hasElementByCss('#accordion-to-dashboard')).toBe(
+        true
+      )
+    })

     await browser.waitForIdleNetwork()

PATCH

echo "Fix applied successfully."
