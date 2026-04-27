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
@@ -80,13 +80,14 @@ await expect(page).toHaveURL(/\/dashboard/);
 expect(await page.getByText("Success").isVisible()).toBe(true);
 ```
 
-**Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict mode because the name matches both the table row and the dialog description simultaneously. Always wait for the dialog to close before asserting the item's absence:
+**Strict mode and confirmation dialogs**: When a confirmation dialog contains the item name (e.g., "Are you sure you want to delete `<name>`?"), asserting `getByText(name)` is gone will fail in strict mode because the name matches both the table row and the dialog description simultaneously. Always wait for the dialog to close before asserting the item's absence, and scope the final assertion to the list/table to avoid matching unrelated page elements (e.g., breadcrumbs, headers):
 
 ```typescript
-// ✅ Good - wait for dialog to close first
-await page.getByRole("button", { name: "Delete" }).click();
-await expect(page.getByRole("alertdialog")).not.toBeVisible();
-await expect(page.getByText(itemName)).not.toBeVisible();
+// ✅ Good - wait for dialog to close, then scope assertion to the table
+const deleteDialog = page.getByRole("alertdialog");
+await deleteDialog.getByRole("button", { name: "Delete" }).click();
+await expect(deleteDialog).not.toBeVisible();
+await expect(page.getByRole("table").getByText(itemName)).not.toBeVisible();
 
 // ❌ Bad - strict mode violation if dialog still visible
 await page.getByRole("button", { name: "Delete" }).click();
PATCH

echo "Gold patch applied."
