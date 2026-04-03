#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if [ -f "e2e/studio/utils/clipboard.ts" ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix - <<'PATCH'
diff --git a/.cursor/rules/testing/e2e-studio/RULE.md b/.cursor/rules/testing/e2e-studio/RULE.md
index 354cd86ac2025..4d98bbfc35ad7 100644
--- a/.cursor/rules/testing/e2e-studio/RULE.md
+++ b/.cursor/rules/testing/e2e-studio/RULE.md
@@ -117,10 +117,6 @@ await waitForApiResponse(page, 'pg-meta', ref, 'tables')
 // ✅ Acceptable - waiting for client-side debounce
 await page.getByRole('textbox').fill('search term')
 await page.waitForTimeout(300) // Allow debounce to complete
-
-// ✅ Acceptable - waiting for clipboard API
-await page.evaluate(() => navigator.clipboard.readText())
-await page.waitForTimeout(500)
 ```

 ## Test Structure
@@ -274,6 +270,22 @@ import {
 } from '../utils/wait-for-response.js'
 ```

+### Use the existing assertions utilities
+
+#### Clipboard assertions
+
+```ts
+// ❌ Avoid - brittle hard coded timeout
+await page.evaluate(() => navigator.clipboard.readText())
+await page.waitForTimeout(500)
+
+// ✅ Good - this utility function uses Playwright auto-retries mechanisms
+await expectClipboardValue({
+  page,
+  value: 'expectedValue'
+})
+```
+
 ## API Mocking

 ### Mock APIs for isolated testing
diff --git a/e2e/studio/features/database.spec.ts b/e2e/studio/features/database.spec.ts
index 6b0806c35ae81..ace3323d0d032 100644
--- a/e2e/studio/features/database.spec.ts
+++ b/e2e/studio/features/database.spec.ts
@@ -1,6 +1,7 @@
 import { expect } from '@playwright/test'

 import { env } from '../env.config.js'
+import { expectClipboardValue } from '../utils/clipboard.js'
 import { createTable, dropTable, query } from '../utils/db/index.js'
 import { test, withSetupCleanup } from '../utils/test.js'
 import { toUrl } from '../utils/to-url.js'
@@ -39,13 +40,15 @@ test.describe('Database', () => {
       // copies schema definition to clipboard
       await page.getByRole('button', { name: 'Copy as SQL' }).click()
       await expect(page.getByTestId('copy-sql-ready')).toBeVisible()
-      const clipboardText = await page.evaluate(() => navigator.clipboard.readText())
-      expect(clipboardText).toContain(`CREATE TABLE public.${databaseTableName} (
+      await expectClipboardValue({
+        page,
+        value: `CREATE TABLE public.${databaseTableName} (
   id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
   created_at timestamp with time zone DEFAULT now(),
   ${databaseColumnName} text,
   CONSTRAINT ${databaseTableName}_pkey PRIMARY KEY (id)
-);`)
+);`,
+      })

       // downloads schema diagram when export is triggered
       const downloadPromise = page.waitForEvent('download')
@@ -91,6 +94,7 @@ test.describe('Database', () => {
       await page.getByText(`${databaseTableName} actions`).click()
       await expect(page.getByRole('menuitem', { name: 'Edit table' })).toBeVisible()
       await page.getByRole('menuitem', { name: 'Edit table' }).click({ force: true })
+      await expect(page.getByRole('menuitem', { name: 'Edit table' })).not.toBeVisible()
       const dialog = page.getByRole('dialog')
       await expect(dialog).toBeVisible()
       await expect(dialog.getByText('timestamptz')).toBeVisible()
@@ -103,6 +107,7 @@ test.describe('Database', () => {
       await page.getByText(`${databaseTableName} actions`).click()
       await expect(page.getByRole('menuitem', { name: 'Edit table' })).toBeVisible()
       await page.getByRole('menuitem', { name: 'Edit table' }).click()
+      await expect(page.getByRole('menuitem', { name: 'Edit table' })).not.toBeVisible()
       await expect(page.getByRole('dialog')).toBeVisible()
       // FIXME: For some reason, the dialog is not stable and rerenders, sometimes preventing the description to be filled
       await page.waitForTimeout(500)
@@ -113,9 +118,8 @@ test.describe('Database', () => {
       await page.getByText(`${databaseTableName} actions`).click()
       await expect(page.getByRole('menuitem', { name: 'Copy name' })).toBeVisible()
       await page.getByRole('menuitem', { name: 'Copy name' }).click()
-      await page.waitForTimeout(500)
-      const copiedTableResult = await page.evaluateHandle(() => navigator.clipboard.readText())
-      expect(await copiedTableResult.jsonValue()).toBe(databaseTableName)
+      await expect(page.getByRole('menuitem', { name: 'Copy name' })).not.toBeVisible()
+      await expectClipboardValue({ page, value: databaseTableName, exact: true })

       await page.getByText(`${databaseTableName} actions`).click()
       await expect(page.getByRole('menuitem', { name: 'View in Table Editor' })).toBeVisible()
@@ -175,9 +179,7 @@ test.describe('Database', () => {
         .click({ force: true })
       await expect(page.getByRole('menuitem', { name: 'Copy name' })).toBeVisible()
       await page.getByRole('menuitem', { name: 'Copy name' }).click()
-      await page.waitForTimeout(500)
-      const copiedTableResult = await page.evaluateHandle(() => navigator.clipboard.readText())
-      expect(await copiedTableResult.jsonValue()).toBe(databaseColumnName)
+      await expectClipboardValue({ page, value: databaseColumnName, exact: true })
     })
   })

diff --git a/e2e/studio/features/sql-editor.spec.ts b/e2e/studio/features/sql-editor.spec.ts
index ac6c8f98a8709..8f405531a9dc1 100644
--- a/e2e/studio/features/sql-editor.spec.ts
+++ b/e2e/studio/features/sql-editor.spec.ts
@@ -1,6 +1,8 @@
-import { expect, Page } from '@playwright/test'
 import fs from 'fs'
+import { expect, Page } from '@playwright/test'
+
 import { env } from '../env.config.js'
+import { expectClipboardValue } from '../utils/clipboard.js'
 import { isCLI } from '../utils/is-cli.js'
 import { resetLocalStorage } from '../utils/reset-local-storage.js'
 import { test } from '../utils/test.js'
@@ -189,12 +191,8 @@ test.describe('SQL Editor', () => {
     await page.getByTestId('sql-run-button').click()

     // verify warning modal blocks execution
-    await expect(
-      page.getByRole('heading', { name: 'Potential issue detected with' })
-    ).toBeVisible()
-    await expect(
-      page.getByText('Query will prevent connections to your database')
-    ).toBeVisible()
+    await expect(page.getByRole('heading', { name: 'Potential issue detected with' })).toBeVisible()
+    await expect(page.getByText('Query will prevent connections to your database')).toBeVisible()
     expect(queryDispatched).toBe(false)

     // cancel should dismiss without executing
@@ -233,12 +231,8 @@ test.describe('SQL Editor', () => {
     await page.getByTestId('sql-run-button').click()

     // verify warning modal blocks execution
-    await expect(
-      page.getByRole('heading', { name: 'Potential issue detected with' })
-    ).toBeVisible()
-    await expect(
-      page.getByText('Query will prevent connections to your database')
-    ).toBeVisible()
+    await expect(page.getByRole('heading', { name: 'Potential issue detected with' })).toBeVisible()
+    await expect(page.getByText('Query will prevent connections to your database')).toBeVisible()
     expect(queryDispatched).toBe(false)

     // cancel should dismiss without executing
@@ -277,9 +271,7 @@ test.describe('SQL Editor', () => {
     await page.getByTestId('sql-run-button').click()

     // verify warning modal blocks execution
-    await expect(
-      page.getByRole('heading', { name: 'Potential issue detected with' })
-    ).toBeVisible()
+    await expect(page.getByRole('heading', { name: 'Potential issue detected with' })).toBeVisible()
     await expect(page.getByText('Query uses update without a where clause')).toBeVisible()
     expect(queryDispatched).toBe(false)

@@ -332,27 +324,35 @@ test.describe('SQL Editor', () => {
     // export as markdown
     await page.getByRole('button', { name: 'Export' }).click()
     await page.getByRole('menuitem', { name: 'Copy as markdown' }).click()
-    await page.waitForTimeout(500)
-    const copiedMarkdownResult = await page.evaluate(() => navigator.clipboard.readText())
-    expect(copiedMarkdownResult).toBe(`| ?column?    |
+    // Make sure the dropdown has closed otherwise it would make the other assertions unstable
+    await expect(page.getByRole('menuitem', { name: 'Copy as markdown' })).not.toBeVisible()
+    await expectClipboardValue({
+      page,
+      value: `| ?column?    |
 | ----------- |
-| hello world |`)
+| hello world |`,
+      exact: true,
+    })

     // export as JSON
     await page.getByRole('button', { name: 'Export' }).click()
     await page.getByRole('menuitem', { name: 'Copy as JSON' }).click()
-    await page.waitForTimeout(500)
-    const copiedJsonResult = await page.evaluate(() => navigator.clipboard.readText())
-    expect(copiedJsonResult).toBe(`[
+    await expect(page.getByRole('menuitem', { name: 'Copy as JSON' })).not.toBeVisible()
+    await expectClipboardValue({
+      page,
+      value: `[
   {
     "?column?": "hello world"
   }
-]`)
+]`,
+      exact: true,
+    })

     // export as CSV
     const downloadPromise = page.waitForEvent('download')
     await page.getByRole('button', { name: 'Export' }).click()
     await page.getByRole('menuitem', { name: 'Download CSV' }).click()
+    await expect(page.getByRole('menuitem', { name: 'Download CSV' })).not.toBeVisible()
     const download = await downloadPromise
     expect(download.suggestedFilename()).toContain('.csv')
     const downloadPath = await download.path()
diff --git a/e2e/studio/features/storage.spec.ts b/e2e/studio/features/storage.spec.ts
index 2f9496634364e..9182c92ec0dfb 100644
--- a/e2e/studio/features/storage.spec.ts
+++ b/e2e/studio/features/storage.spec.ts
@@ -2,6 +2,7 @@ import path from 'path'
 import { expect } from '@playwright/test'

 import { env } from '../env.config.js'
+import { expectClipboardValue } from '../utils/clipboard.js'
 import {
   createBucket,
   createFolder,
@@ -248,61 +249,55 @@ test.describe('Storage', () => {
     const folderFile = page.getByTitle(folderFileName)
     await folderFile.click({ button: 'right' })
     await page.getByRole('menuitem', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(
-        `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`
-      )
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`,
+    })
     await expect(page.getByRole('menuitem', { name: 'Get URL' })).not.toBeVisible()

     // Right-click on the root file to open context menu while the folder is still open
     const rootFile = page.getByTitle(rootFileName)
     await rootFile.click({ button: 'right' })
     await page.getByRole('menuitem', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(`storage/v1/object/public/${bucketName}/${rootFileName}`)
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${rootFileName}`,
+    })
     await expect(page.getByRole('menuitem', { name: 'Get URL' })).not.toBeVisible()

     // Click the actions button on the folder file to open dropdown menu
     await page.getByRole('button', { name: `${folderFileName} actions` }).click()
     await page.getByRole('menuitem', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(
-        `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`
-      )
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`,
+    })
     await expect(page.getByRole('menuitem', { name: 'Get URL' })).not.toBeVisible()

     // Click the actions button on the root file to open dropdown menu while the folder is still open
     await page.getByRole('button', { name: `${rootFileName} actions` }).click()
     await page.getByRole('menuitem', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(`storage/v1/object/public/${bucketName}/${rootFileName}`)
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${rootFileName}`,
+    })
     await expect(page.getByRole('menuitem', { name: 'Get URL' })).not.toBeVisible()

     // Click the folder file to open its preview pane
     await folderFile.click()
     await page.getByRole('button', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(
-        `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`
-      )
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${folderName}/${folderFileName}`,
+    })

     // Click the root file to open its preview pane while folder is still open
     await rootFile.click()
     await page.getByRole('button', { name: 'Get URL' }).click()
-    await expect(async () => {
-      const copiedUrl = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedUrl).toContain(`storage/v1/object/public/${bucketName}/${rootFileName}`)
-    }).toPass({ timeout: 2000 })
+    await expectClipboardValue({
+      page,
+      value: `storage/v1/object/public/${bucketName}/${rootFileName}`,
+    })
   })

   test('resets folder name when renaming with empty string', async ({ page, ref }) => {
diff --git a/e2e/studio/features/table-editor.spec.ts b/e2e/studio/features/table-editor.spec.ts
index f1d5065965fe5..d3802a29ad78a 100644
--- a/e2e/studio/features/table-editor.spec.ts
+++ b/e2e/studio/features/table-editor.spec.ts
@@ -3,6 +3,7 @@ import path from 'path'
 import { expect, Page } from '@playwright/test'

 import { env } from '../env.config.js'
+import { expectClipboardValue } from '../utils/clipboard.js'
 import { dropTable, query } from '../utils/db/index.js'
 import { createTable, createTableWithRLS } from '../utils/db/queries.js'
 import { resetLocalStorage } from '../utils/reset-local-storage.js'
@@ -80,9 +81,14 @@ testRunner('table editor', () => {
       .nth(2)
       .click()
     await page.getByRole('menuitem', { name: 'Copy name' }).click()
-    await page.waitForTimeout(500)
-    const copiedTableResult = await page.evaluate(() => navigator.clipboard.readText())
-    expect(copiedTableResult).toBe('pw_table_actions')
+    // Make sure the dropdown has closed otherwise it would make the other assertions unstable
+    await expect(page.getByRole('menuitem', { name: 'Copy name' })).not.toBeVisible()
+
+    await expectClipboardValue({
+      page,
+      value: 'pw_table_actions',
+      exact: true,
+    })

     // copies table schema to clipboard when copy schema option is clicked
     await page
@@ -91,15 +97,17 @@ testRunner('table editor', () => {
       .nth(2)
       .click()
     await page.getByRole('menuitem', { name: 'Copy table schema' }).click()
-    await expect(async () => {
-      const copiedSchemaResult = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedSchemaResult).toBe(`create table public.pw_table_actions (
+    await expect(page.getByRole('menuitem', { name: 'Copy table schema' })).not.toBeVisible()
+    await expectClipboardValue({
+      page,
+      value: `create table public.pw_table_actions (
   id bigint generated by default as identity not null,
   created_at timestamp with time zone null default now(),
   pw_column text null,
   constraint pw_table_actions_pkey primary key (id)
-) TABLESPACE pg_default;`)
-    }).toPass({ timeout: 2000 })
+) TABLESPACE pg_default;`,
+      exact: true,
+    })

     // duplicates table
     await page
@@ -108,6 +116,7 @@ testRunner('table editor', () => {
       .nth(2)
       .click()
     await page.getByRole('menuitem', { name: 'Duplicate table' }).click()
+    await expect(page.getByRole('menuitem', { name: 'Duplicate table' })).not.toBeVisible()
     const duplicatePromise = waitForApiResponse(page, 'pg-meta', ref, 'query?key=', {
       method: 'POST',
     })
@@ -542,9 +551,11 @@ testRunner('table editor', () => {
     await page.getByRole('columnheader', { name: colName }).getByRole('button').nth(1).click()
     await page.getByRole('menuitem', { name: 'Copy name' }).click()

-    await page.waitForTimeout(500)
-    const copiedTableResult = await page.evaluate(() => navigator.clipboard.readText())
-    expect(copiedTableResult).toBe(colName)
+    await expectClipboardValue({
+      page,
+      value: colName,
+      exact: true,
+    })
   })

   test('importing, pagination and large data actions works as expected', async ({ page, ref }) => {
@@ -769,11 +780,13 @@ testRunner('table editor', () => {

     // Click "Copy cell" from context menu
     await page.getByRole('menuitem', { name: 'Copy cell' }).click()
-    await page.waitForTimeout(500)

     // Verify first row value was copied
-    const firstCopiedValue = await page.evaluate(() => navigator.clipboard.readText())
-    expect(firstCopiedValue).toBe('first_row_value')
+    await expectClipboardValue({
+      page,
+      value: 'first_row_value',
+      exact: true,
+    })

     // Right-click on the second row's cell to open context menu
     const secondRowCell = page.getByRole('gridcell', { name: 'second_row_value' })
@@ -782,11 +795,13 @@ testRunner('table editor', () => {

     // Click "Copy cell" from context menu
     await page.getByRole('menuitem', { name: 'Copy cell' }).click()
-    await page.waitForTimeout(500)

     // Verify second row value was copied
-    const secondCopiedValue = await page.evaluate(() => navigator.clipboard.readText())
-    expect(secondCopiedValue).toBe('second_row_value')
+    await expectClipboardValue({
+      page,
+      value: 'second_row_value',
+      exact: true,
+    })
   })

   test('boolean fields can be edited correctly', async ({ page, ref }) => {
@@ -1248,14 +1263,15 @@ testRunner('table editor', () => {
       .nth(2)
       .click()
     await page.getByRole('menuitem', { name: 'Copy table schema' }).click()
-    await expect(async () => {
-      const copiedSchemaResult = await page.evaluate(() => navigator.clipboard.readText())
-      expect(copiedSchemaResult).toBe(`create table public.${tableName} (
+    await expectClipboardValue({
+      page,
+      value: `create table public.${tableName} (
   id bigint generated by default as identity not null,
   created_at timestamp with time zone not null default now(),
   pw_column bigint null default '10'::bigint,
   constraint ${tableName}_pkey primary key (id)
-) TABLESPACE pg_default;`)
-    }).toPass({ timeout: 2000 })
+) TABLESPACE pg_default;`,
+      exact: true,
+    })
   })
 })
diff --git a/e2e/studio/utils/clipboard.ts b/e2e/studio/utils/clipboard.ts
new file mode 100644
index 0000000000000..f9feff47daa65
--- /dev/null
+++ b/e2e/studio/utils/clipboard.ts
@@ -0,0 +1,21 @@
+import { expect, type Page } from '@playwright/test'
+
+export const expectClipboardValue = ({
+  page,
+  value,
+  exact = false,
+  timeout = 2000,
+}: {
+  page: Page
+  value: string
+  exact?: boolean
+  timeout?: number
+}) =>
+  expect(async () => {
+    await using handle = await page.evaluateHandle(() => navigator.clipboard.readText())
+    if (exact) {
+      expect(await handle.jsonValue()).toEqual(value)
+    } else {
+      expect(await handle.jsonValue()).toContain(value)
+    }
+  }).toPass({ timeout })
diff --git a/e2e/studio/utils/storage-helpers.ts b/e2e/studio/utils/storage-helpers.ts
index c715d83cab337..e4065654f0b81 100644
--- a/e2e/studio/utils/storage-helpers.ts
+++ b/e2e/studio/utils/storage-helpers.ts
@@ -1,7 +1,8 @@
 import { expect, Page } from '@playwright/test'
-import { waitForApiResponse } from './wait-for-response.js'
-import { toUrl } from './to-url.js'
+
 import { dismissToastsIfAny } from './dismiss-toast.js'
+import { toUrl } from './to-url.js'
+import { waitForApiResponse } from './wait-for-response.js'

 /**
  * Navigates to a the storage home view
@@ -175,14 +176,14 @@ export const uploadFile = async (page: Page, filePath: string, fileName: string)
   const fileInput = page.locator('input[type="file"]')
   await fileInput.setInputFiles(filePath)

-  // Wait for upload to complete - file should appear in the explorer
-  await page.waitForTimeout(15_000) // Allow time for upload to process
-
+  await expect(page.getByRole('status')).not.toBeVisible()
   // Verify file appears in the explorer by title
   await expect(
     page.getByTitle(fileName),
     `File ${fileName} should be visible in explorer after upload`
   ).toBeVisible()
+  // Verify its action button is visible too as it means the upload is indeed complete
+  await expect(page.getByRole('button', { name: `${fileName} actions` })).toBeVisible()
 }

 /**

PATCH

echo "Patch applied successfully."
