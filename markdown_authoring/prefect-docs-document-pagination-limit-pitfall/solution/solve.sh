#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "When testing pagination, set a small enough `limit` in the URL so the next-page " "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -280,6 +280,26 @@ await page.goto(`/events?resource=${resourceFilter}`);
 
 Pass the resource IDs (or prefixes) of the resources your test cares about. This keeps the result set small regardless of how much background activity other shards produce.
 
+### Pagination Tests — Use a Small Limit
+
+When testing pagination, set a small enough `limit` in the URL so the next-page button stays enabled even after filters are applied. A large limit (e.g., `limit=5`) against a filtered data set that returns fewer rows than the limit leaves the next-page button disabled, and a conditional `isEnabled()` check silently skips the assertion rather than catching the regression:
+
+```typescript
+// ❌ Fragile - filtering may reduce results to ≤ limit, so next-page is never available
+await page.goto(`/runs?limit=5&flow-run-search=${filter}`);
+if (await nextPageButton.isEnabled({ timeout: 3000 }).catch(() => false)) {
+  await nextPageButton.click(); // silently skipped when pagination isn't triggered
+}
+
+// ✅ Reliable - small limit guarantees next page is always needed
+await page.goto(`/runs?limit=2&flow-run-search=${filter}`);
+await expect(nextPageButton).toBeEnabled({ timeout: 10000 });
+await nextPageButton.click();
+await expect(page).toHaveURL(/page=2/);
+```
+
+Always assert `toBeEnabled()` rather than conditionally checking — the conditional silently turns a pagination test into a no-op when setup conditions change.
+
 ### Explicit Waits
 
 Avoid `waitForTimeout()` unless absolutely necessary. When required, always add a comment explaining why:
PATCH

echo "Gold patch applied."
