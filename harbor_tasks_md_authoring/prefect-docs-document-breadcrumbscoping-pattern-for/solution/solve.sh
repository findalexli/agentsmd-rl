#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "**Strict mode on detail pages**: When asserting the name of a resource on its de" "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -80,6 +80,18 @@ await expect(page).toHaveURL(/\/dashboard/);
 expect(await page.getByText("Success").isVisible()).toBe(true);
 ```
 
+**Strict mode on detail pages**: When asserting the name of a resource on its detail page (e.g., a task run or flow run), the name can appear in multiple places — the breadcrumb, the page heading, and as log entry metadata once logs finish loading. Scope the assertion to the specific landmark:
+
+```typescript
+// ✅ Good - scoped to breadcrumb; avoids matching log metadata that loads later
+await expect(
+  page.getByLabel("breadcrumb").getByText(taskRunName, { exact: true }),
+).toBeVisible({ timeout: 10000 });
+
+// ❌ Bad - strict mode violation once logs load and the name appears a second time
+await expect(page.getByText(taskRunName)).toBeVisible();
+```
+
 **Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict mode because the name matches both the table row and the dialog description simultaneously. Always wait for the dialog to close before asserting the item's absence, and scope the final assertion to the list/table to avoid matching unrelated page elements (e.g., breadcrumbs, headers):
 
 ```typescript
PATCH

echo "Gold patch applied."
