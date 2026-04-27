#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "Tests that skip based on a pre-navigation API check (e.g., \"skip if no artifacts" "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -121,6 +121,24 @@ const items = await listItems(apiClient);
 expect(items.find((i) => i.name === itemName)?.value).toBe(expectedValue);
 ```
 
+**Re-verify global state after navigation:**
+
+Tests that skip based on a pre-navigation API check (e.g., "skip if no artifacts exist") must re-verify after the page loads. Another shard may have changed global state between the check and navigation, hiding a real rendering bug behind a skip:
+
+```typescript
+// ✅ Good - re-verify after page load so rendering bugs still surface
+const preCheck = await listItems(apiClient);
+test.skip(preCheck.length > 0, "Items exist, skipping empty-state test");
+
+await page.goto("/items");
+await waitForPageReady(page);
+
+const recheck = await listItems(apiClient);
+test.skip(recheck.length > 0, "Items appeared from another shard");
+
+await expect(page.getByRole("heading", { name: /get started/i })).toBeVisible();
+```
+
 **Isolate test data by test file:**
 
 Each test file should use its own `TEST_PREFIX` or unique identifiers to avoid conflicts with other test files running in parallel.
PATCH

echo "Gold patch applied."
