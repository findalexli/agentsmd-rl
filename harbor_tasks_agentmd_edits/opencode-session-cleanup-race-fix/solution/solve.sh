#!/bin/bash
set -e

cd /workspace/opencode

# Check if already applied
if grep -q "cleanupSession" packages/app/e2e/actions.ts; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat << 'PATCH_EOF' | git apply -
diff --git a/packages/app/e2e/AGENTS.md b/packages/app/e2e/AGENTS.md
index 59662dbea560..f978389783da 100644
--- a/packages/app/e2e/AGENTS.md
+++ b/packages/app/e2e/AGENTS.md
@@ -71,6 +71,9 @@ test("test description", async ({ page, sdk, gotoSession }) => {
 - `closeDialog(page, dialog)` - Close any dialog
 - `openSidebar(page)` / `closeSidebar(page)` - Toggle sidebar
 - `withSession(sdk, title, callback)` - Create temp session
+- `withProject(...)` - Create temp project/workspace
+- `trackSession(sessionID, directory?)` - Register session for fixture cleanup
+- `trackDirectory(directory)` - Register directory for fixture cleanup
 - `clickListItem(container, filter)` - Click list item by key/text

 **Selectors** (`selectors.ts`):
@@ -109,7 +112,7 @@ import { test, expect } from "@playwright/test"

 ### Error Handling

-Tests should clean up after themselves:
+Tests should clean up after themselves. Prefer fixture-managed cleanup:

 ```typescript
 test("test with cleanup", async ({ page, sdk, gotoSession }) => {
@@ -120,6 +123,11 @@ test("test with cleanup", async ({ page, sdk, gotoSession }) => {
 })
 ```

+- Prefer `withSession(...)` for temp sessions
+- In `withProject(...)` tests that create sessions or extra workspaces, call `trackSession(sessionID, directory?)` and `trackDirectory(directory)`
+- This lets fixture teardown abort, wait for idle, and clean up safely under CI concurrency
+- Avoid calling `sdk.session.delete(...)` directly
+
 ### Timeouts

 Default: 60s per test, 10s per assertion. Override when needed:
diff --git a/packages/app/e2e/actions.ts b/packages/app/e2e/actions.ts
index 8787b70f5315..83c2 100644
--- a/packages/app/e2e/actions.ts
+++ b/packages/app/e2e/actions.ts
@@ -306,6 +306,57 @@ export async function clickListItem(
   return item
 }

+async function status(sdk: ReturnType<typeof createSdk>, sessionID: string) {
+  const data = await sdk.session
+    .status()
+    .then((x) => x.data ?? {})
+    .catch(() => undefined)
+  return data?.[sessionID]
+}
+
+async function stable(sdk: ReturnType<typeof createSdk>, sessionID: string, timeout = 10_000) {
+  let prev = ""
+  await expect
+    .poll(
+      async () => {
+        const info = await sdk.session
+          .get({ sessionID })
+          .then((x) => x.data)
+          .catch(() => undefined)
+        if (!info) return true
+        const next = `${info.title}:${info.time.updated ?? info.time.created}`
+        if (next !== prev) {
+          prev = next
+          return false
+        }
+        return true
+      },
+      { timeout },
+    )
+    .toBe(true)
+}
+
+export async function waitSessionIdle(sdk: ReturnType<typeof createSdk>, sessionID: string, timeout = 30_000) {
+  await expect.poll(() => status(sdk, sessionID).then((x) => !x || x.type === "idle"), { timeout }).toBe(true)
+}
+
+export async function cleanupSession(input: {
+  sessionID: string
+  directory?: string
+  sdk?: ReturnType<typeof createSdk>
+}) {
+  const sdk = input.sdk ?? (input.directory ? createSdk(input.directory) : undefined)
+  if (!sdk) throw new Error("cleanupSession requires sdk or directory")
+  await waitSessionIdle(sdk, input.sessionID, 5_000).catch(() => undefined)
+  const current = await status(sdk, input.sessionID).catch(() => undefined)
+  if (current && current.type !== "idle") {
+    await sdk.session.abort({ sessionID: input.sessionID }).catch(() => undefined)
+    await waitSessionIdle(sdk, input.sessionID).catch(() => undefined)
+  }
+  await stable(sdk, input.sessionID).catch(() => undefined)
+  await sdk.session.delete({ sessionID: input.sessionID }).catch(() => undefined)
+}
+
 export async function withSession<T>(
   sdk: ReturnType<typeof createSdk>,
   title: string,
@@ -317,7 +368,7 @@ export async function withSession<T>(
   try {
     return await callback(session)
   } finally {
-    await sdk.session.delete({ sessionID: session.id }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID: session.id })
   }
 }

diff --git a/packages/app/e2e/fixtures.ts b/packages/app/e2e/fixtures.ts
index ea41ed8516ec..6a35c6901eae 100644
--- a/packages/app/e2e/fixtures.ts
+++ b/packages/app/e2e/fixtures.ts
@@ -1,5 +1,5 @@
 import { test as base, expect, type Page } from "@playwright/test"
-import { cleanupTestProject, createTestProject, seedProjects } from "./actions"
+import { cleanupSession, cleanupTestProject, createTestProject, seedProjects, sessionIDFromUrl } from "./actions"
 import { promptSelector } from "./selectors"
 import { createSdk, dirSlug, getWorktree, sessionPath } from "./utils"

@@ -13,6 +13,8 @@ type TestFixtures = {
       directory: string
       slug: string
       gotoSession: (sessionID?: string) => Promise<void>
+      trackSession: (sessionID: string, directory?: string) => void
+      trackDirectory: (directory: string) => void
     }) => Promise<T>,
     options?: { extra?: string[] },
   ) => Promise<T>
@@ -51,20 +53,36 @@ export const test = base.extend<TestFixtures, WorkerFixtures>({
   },
   withProject: async ({ page }, use) => {
     await use(async (callback, options) => {
-      const directory = await createTestProject()
-      const slug = dirSlug(directory)
-      await seedStorage(page, { directory, extra: options?.extra })
+      const root = await createTestProject()
+      const slug = dirSlug(root)
+      const sessions = new Map<string, string>()
+      const dirs = new Set<string>()
+      await seedStorage(page, { directory: root, extra: options?.extra })

       const gotoSession = async (sessionID?: string) => {
-        await page.goto(sessionPath(directory, sessionID))
+        await page.goto(sessionPath(root, sessionID))
         await expect(page.locator(promptSelector)).toBeVisible()
+        const current = sessionIDFromUrl(page.url())
+        if (current) trackSession(current)
+      }
+
+      const trackSession = (sessionID: string, directory?: string) => {
+        sessions.set(sessionID, directory ?? root)
+      }
+
+      const trackDirectory = (directory: string) => {
+        if (directory !== root) dirs.add(directory)
       }

       try {
         await gotoSession()
-        return await callback({ directory, slug, gotoSession })
+        return await callback({ directory: root, slug, gotoSession, trackSession, trackDirectory })
       } finally {
-        await cleanupTestProject(directory)
+        await Promise.allSettled(
+          Array.from(sessions, ([sessionID, directory]) => cleanupSession({ sessionID, directory })),
+        )
+        await Promise.allSettled(Array.from(dirs, (directory) => cleanupTestProject(directory)))
+        await cleanupTestProject(root)
       }
     })
   },
PATCH_EOF

echo "Patch applied successfully"
