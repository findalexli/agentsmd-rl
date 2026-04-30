#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for distinctive line from the patch)
if grep -q 'waitSlug(page, skip?)' packages/app/e2e/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch — includes BOTH code and config changes
git apply - <<'PATCH'
diff --git a/packages/app/e2e/AGENTS.md b/packages/app/e2e/AGENTS.md
index f978389783da..8bfbd111b250 100644
--- a/packages/app/e2e/AGENTS.md
+++ b/packages/app/e2e/AGENTS.md
@@ -72,6 +72,9 @@ test("test description", async ({ page, sdk, gotoSession }) => {
 - `openSidebar(page)` / `closeSidebar(page)` - Toggle sidebar
 - `withSession(sdk, title, callback)` - Create temp session
 - `withProject(...)` - Create temp project/workspace
+- `sessionIDFromUrl(url)` - Read session ID from URL
+- `slugFromUrl(url)` - Read workspace slug from URL
+- `waitSlug(page, skip?)` - Wait for resolved workspace slug
 - `trackSession(sessionID, directory?)` - Register session for fixture cleanup
 - `trackDirectory(directory)` - Register directory for fixture cleanup
 - `clickListItem(container, filter)` - Click list item by key/text
@@ -169,9 +172,10 @@ await page.keyboard.press(`${modKey}+Comma`) // Open settings
 1. Choose appropriate folder or create new one
 2. Import from `../fixtures`
 3. Use helper functions from `../actions` and `../selectors`
-4. Clean up any created resources
-5. Use specific selectors (avoid CSS classes)
-6. Test one feature per test file
+4. When validating routing, use shared helpers from `../actions`. Workspace URL slugs can be canonicalized on Windows, so assert against canonical or resolved workspace slugs.
+5. Clean up any created resources
+6. Use specific selectors (avoid CSS classes)
+7. Test one feature per test file

 ## Local Development

diff --git a/packages/app/e2e/actions.ts b/packages/app/e2e/actions.ts
index 2354b88e83c2..86147dc65d50 100644
--- a/packages/app/e2e/actions.ts
+++ b/packages/app/e2e/actions.ts
@@ -199,6 +199,33 @@ export async function cleanupTestProject(directory: string) {
   await fs.rm(directory, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 }).catch(() => undefined)
 }

+export function slugFromUrl(url: string) {
+  return /\/([^/]+)\/session(?:[/?#]|$)/.exec(url)?.[1] ?? ""
+}
+
+export async function waitSlug(page: Page, skip: string[] = []) {
+  let prev = ""
+  let next = ""
+  await expect
+    .poll(
+      () => {
+        const slug = slugFromUrl(page.url())
+        if (!slug) return ""
+        if (skip.includes(slug)) return ""
+        if (slug !== prev) {
+          prev = slug
+          next = ""
+          return ""
+        }
+        next = slug
+        return slug
+      },
+      { timeout: 45_000 },
+    )
+    .not.toBe("")
+  return next
+}
+
 export function sessionIDFromUrl(url: string) {
   const match = /\/session\/([^/?#]+)/.exec(url)
   return match?.[1]
diff --git a/packages/app/e2e/projects/projects-switch.spec.ts b/packages/app/e2e/projects/projects-switch.spec.ts
index a942f29e0378..6ad64f592789 100644
--- a/packages/app/e2e/projects/projects-switch.spec.ts
+++ b/packages/app/e2e/projects/projects-switch.spec.ts
@@ -1,13 +1,9 @@
 import { base64Decode } from "@opencode-ai/util/encode"
 import type { Page } from "@playwright/test"
 import { test, expect } from "../fixtures"
-import { defocus, createTestProject, cleanupTestProject, openSidebar, sessionIDFromUrl } from "../actions"
+import { defocus, createTestProject, cleanupTestProject, openSidebar, sessionIDFromUrl, waitSlug } from "../actions"
 import { projectSwitchSelector, promptSelector, workspaceItemSelector, workspaceNewSessionSelector } from "../selectors"
-import { dirSlug } from "../utils"
-
-function slugFromUrl(url: string) {
-  return /\/([^/]+)\/session(?:\/|$)/.exec(url)?.[1] ?? ""
-}
+import { dirSlug, resolveDirectory } from "../utils"

 async function workspaces(page: Page, directory: string, enabled: boolean) {
   await page.evaluate(
@@ -76,7 +72,6 @@ test("switching back to a project opens the latest workspace session", async ({

   const other = await createTestProject()
   const otherSlug = dirSlug(other)
-  let workspaceDir: string | undefined
   try {
     await withProject(
       async ({ directory, slug, trackSession, trackDirectory }) => {
@@ -89,33 +84,27 @@ test("switching back to a project opens the latest workspace session", async ({

         await page.getByRole("button", { name: "New workspace" }).first().click()

-        await expect
-          .poll(
-            () => {
-              const next = slugFromUrl(page.url())
-              if (!next) return ""
-              if (next === slug) return ""
-              return next
-            },
-            { timeout: 45_000 },
-          )
-          .not.toBe("")
-
-        const workspaceSlug = slugFromUrl(page.url())
-        workspaceDir = base64Decode(workspaceSlug)
-        if (!workspaceDir) throw new Error(`Failed to decode workspace slug: ${workspaceSlug}`)
-        trackDirectory(workspaceDir)
+        const raw = await waitSlug(page, [slug])
+        const dir = base64Decode(raw)
+        if (!dir) throw new Error(`Failed to decode workspace slug: ${raw}`)
+        const space = await resolveDirectory(dir)
+        const next = dirSlug(space)
+        trackDirectory(space)
         await openSidebar(page)

-        const workspace = page.locator(workspaceItemSelector(workspaceSlug)).first()
-        await expect(workspace).toBeVisible()
-        await workspace.hover()
+        const item = page.locator(`${workspaceItemSelector(next)}, ${workspaceItemSelector(raw)}`).first()
+        await expect(item).toBeVisible()
+        await item.hover()

-        const newSession = page.locator(workspaceNewSessionSelector(workspaceSlug)).first()
-        await expect(newSession).toBeVisible()
-        await newSession.click({ force: true })
+        const btn = page.locator(`${workspaceNewSessionSelector(next)}, ${workspaceNewSessionSelector(raw)}`).first()
+        await expect(btn).toBeVisible()
+        await btn.click({ force: true })

-        await expect(page).toHaveURL(new RegExp(`/${workspaceSlug}/session(?:[/?#]|$)`))
+        // A new workspace can be discovered via a transient slug before the route and sidebar
+        // settle to the canonical workspace path on Windows, so interact with either and assert
+        // against the resolved workspace slug.
+        await waitSlug(page)
+        await expect(page).toHaveURL(new RegExp(`/${next}/session(?:[/?#]|$)`))

         // Create a session by sending a prompt
         const prompt = page.locator(promptSelector)
@@ -128,9 +117,9 @@ test("switching back to a project opens the latest workspace session", async ({

         const created = sessionIDFromUrl(page.url())
         if (!created) throw new Error(`Failed to get session ID from url: ${page.url()}`)
-        trackSession(created, workspaceDir)
+        trackSession(created, space)

-        await expect(page).toHaveURL(new RegExp(`/${workspaceSlug}/session/${created}(?:[/?#]|$)`))
+        await expect(page).toHaveURL(new RegExp(`/${next}/session/${created}(?:[/?#]|$)`))

         await openSidebar(page)

diff --git a/packages/app/e2e/projects/workspace-new-session.spec.ts b/packages/app/e2e/projects/workspace-new-session.spec.ts
index 621ba0f3ad55..18fa46d3299c 100644
--- a/packages/app/e2e/projects/workspace-new-session.spec.ts
+++ b/packages/app/e2e/projects/workspace-new-session.spec.ts
@@ -1,34 +1,10 @@
 import { base64Decode } from "@opencode-ai/util/encode"
 import type { Page } from "@playwright/test"
 import { test, expect } from "../fixtures"
-import { openSidebar, sessionIDFromUrl, setWorkspacesEnabled } from "../actions"
+import { openSidebar, sessionIDFromUrl, setWorkspacesEnabled, slugFromUrl, waitSlug } from "../actions"
 import { promptSelector, workspaceItemSelector, workspaceNewSessionSelector } from "../selectors"
 import { createSdk } from "../utils"

-function slugFromUrl(url: string) {
-  return /\/([^/]+)\/session(?:\/|$)/.exec(url)?.[1] ?? ""
-}
-
-async function waitSlug(page: Page, skip: string[] = []) {
-  let prev = ""
-  await expect
-    .poll(
-      () => {
-        const slug = slugFromUrl(page.url())
-        if (!slug) return ""
-        if (skip.includes(slug)) return ""
-        if (slug !== prev) {
-          prev = slug
-          return ""
-        }
-        return slug
-      },
-      { timeout: 45_000 },
-    )
-    .not.toBe("")
-  return slugFromUrl(page.url())
-}
-
 async function waitWorkspaceReady(page: Page, slug: string) {
   await openSidebar(page)
   await expect

diff --git a/packages/app/e2e/projects/workspaces.spec.ts b/packages/app/e2e/projects/workspaces.spec.ts
index 805b45e98978..aeeccb9bba9a 100644
--- a/packages/app/e2e/projects/workspaces.spec.ts
+++ b/packages/app/e2e/projects/workspaces.spec.ts
@@ -14,34 +14,12 @@ import {
   openSidebar,
   openWorkspaceMenu,
   setWorkspacesEnabled,
+  slugFromUrl,
+  waitSlug,
 } from "../actions"
 import { dropdownMenuContentSelector, inlineInputSelector, workspaceItemSelector } from "../selectors"
 import { createSdk, dirSlug } from "../utils"

-function slugFromUrl(url: string) {
-  return /\/([^/]+)\/session(?:\/|$)/.exec(url)?.[1] ?? ""
-}
-
-async function waitSlug(page: Page, skip: string[] = []) {
-  let prev = ""
-  await expect
-    .poll(
-      () => {
-        const slug = slugFromUrl(page.url())
-        if (!slug) return ""
-        if (skip.includes(slug)) return ""
-        if (slug !== prev) {
-          prev = slug
-          return ""
-        }
-        return slug
-      },
-      { timeout: 45_000 },
-    )
-    .not.toBe("")
-  return slugFromUrl(page.url())
-}
-
 async function setupWorkspaceTest(page: Page, project: { slug: string }) {
   const rootSlug = project.slug
   await openSidebar(page)
@@ -353,17 +331,7 @@ test("can reorder workspaces by drag and drop", async ({ page, withProject }) =>
       for (const _ of [0, 1]) {
         const prev = slugFromUrl(page.url())
         await page.getByRole("button", { name: "New workspace" }).first().click()
-        await expect
-          .poll(
-            () => {
-              const slug = slugFromUrl(page.url())
-              return slug.length > 0 && slug !== rootSlug && slug !== prev
-            },
-            { timeout: 45_000 },
-          )
-          .toBe(true)
-
-        const slug = slugFromUrl(page.url())
+        const slug = await waitSlug(page, [rootSlug, prev])
         const dir = base64Decode(slug)
         workspaces.push({ slug, directory: dir })

PATCH

echo "Patch applied successfully."
