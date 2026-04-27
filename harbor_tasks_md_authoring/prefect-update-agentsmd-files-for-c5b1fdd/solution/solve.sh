#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "Comparing a count captured before an action to a count captured after the action" "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -157,6 +157,28 @@ await expect(page.getByRole("heading", { name: /get started/i })).toBeVisible();
 
 Each test file should use its own `TEST_PREFIX` or unique identifiers to avoid conflicts with other test files running in parallel.
 
+**Avoid count comparisons across time snapshots:**
+
+Comparing a count captured before an action to a count captured after the action is flaky in parallel CI: other shards continuously emit background events (work-pool polls, heartbeats, etc.), so the "after" count can exceed the "before" count even when the action (e.g., a filter) is working correctly. Assert content directly instead — verify that each displayed item matches the expected criteria:
+
+```typescript
+// ❌ Bad - flaky: background events can push the post-action count above the pre-action count
+const unfilteredCount = await page.locator("ol.list-none li").count();
+await applyFilter("prefect.flow-run.*");
+const filteredCount = await page.locator("ol.list-none li").count();
+expect(filteredCount).toBeLessThanOrEqual(unfilteredCount);
+
+// ✅ Good - assert content rather than count
+const prefix = "prefect.flow-run"; // strip trailing ".*" from the filter label
+await applyFilter("prefect.flow-run.*");
+const items = page.locator("ol.list-none li");
+await expect(items.first()).toBeVisible();
+const allText = await items.allTextContents();
+for (const text of allText) {
+  expect(text).toContain(prefix);
+}
+```
+
 ### Handling Page Loading States
 
 When tests navigate to a page and immediately interact with it, the page might not be fully loaded, especially under parallel execution when the API server is handling multiple requests. Always wait for the page to be ready before interacting:
PATCH

echo "Gold patch applied."
