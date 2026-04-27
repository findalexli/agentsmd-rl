#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prefect

# Idempotency guard
if grep -qF "**Strict mode and confirmation dialogs**: When a confirmation dialog contains th" "ui-v2/e2e/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui-v2/e2e/AGENTS.md b/ui-v2/e2e/AGENTS.md
@@ -80,6 +80,19 @@ await expect(page).toHaveURL(/\/dashboard/);
 expect(await page.getByText("Success").isVisible()).toBe(true);
 ```
 
+**Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict mode because the name matches both the table row and the dialog description simultaneously. Always wait for the dialog to close before asserting the item's absence:
+
+```typescript
+// ✅ Good - wait for dialog to close first
+await page.getByRole("button", { name: "Delete" }).click();
+await expect(page.getByRole("alertdialog")).not.toBeVisible();
+await expect(page.getByText(itemName)).not.toBeVisible();
+
+// ❌ Bad - strict mode violation if dialog still visible
+await page.getByRole("button", { name: "Delete" }).click();
+await expect(page.getByText(itemName)).not.toBeVisible();
+```
+
 ### Test Isolation
 
 - Use unique test data with `TEST_PREFIX` and timestamps: `${TEST_PREFIX}item-${Date.now()}`
PATCH

echo "Gold patch applied."
