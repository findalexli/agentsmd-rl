#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'export async function cleanupSession' packages/app/e2e/actions.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
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
index 8787b70f5315..2354b88e83c2 100644
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
diff --git a/packages/app/e2e/projects/projects-switch.spec.ts b/packages/app/e2e/projects/projects-switch.spec.ts
index 2725100f45b3..a942f29e0378 100644
--- a/packages/app/e2e/projects/projects-switch.spec.ts
+++ b/packages/app/e2e/projects/projects-switch.spec.ts
@@ -3,7 +3,7 @@ import type { Page } from "@playwright/test"
 import { test, expect } from "../fixtures"
 import { defocus, createTestProject, cleanupTestProject, openSidebar, sessionIDFromUrl } from "../actions"
 import { projectSwitchSelector, promptSelector, workspaceItemSelector, workspaceNewSessionSelector } from "../selectors"
-import { createSdk, dirSlug, sessionPath } from "../utils"
+import { dirSlug } from "../utils"

 function slugFromUrl(url: string) {
   return /\/([^/]+)\/session(?:\/|$)/.exec(url)?.[1] ?? ""
@@ -76,14 +76,10 @@ test("switching back to a project opens the latest workspace session", async ({

   const other = await createTestProject()
   const otherSlug = dirSlug(other)
-  let rootDir: string | undefined
   let workspaceDir: string | undefined
-  let sessionID: string | undefined
-
   try {
     await withProject(
-      async ({ directory, slug }) => {
-        rootDir = directory
+      async ({ directory, slug, trackSession, trackDirectory }) => {
         await defocus(page)
         await workspaces(page, directory, true)
         await page.reload()
@@ -108,6 +104,7 @@ test("switching back to a project opens the latest workspace session", async ({
         const workspaceSlug = slugFromUrl(page.url())
         workspaceDir = base64Decode(workspaceSlug)
         if (!workspaceDir) throw new Error(`Failed to decode workspace slug: ${workspaceSlug}`)
+        trackDirectory(workspaceDir)
         await openSidebar(page)

         const workspace = page.locator(workspaceItemSelector(workspaceSlug)).first()
@@ -131,7 +128,7 @@ test("switching back to a project opens the latest workspace session", async ({

         const created = sessionIDFromUrl(page.url())
         if (!created) throw new Error(`Failed to get session ID from url: ${page.url()}`)
-        sessionID = created
+        trackSession(created, workspaceDir)

         await expect(page).toHaveURL(new RegExp(`/${workspaceSlug}/session/${created}(?:[/?#]|$)`))

@@ -152,20 +149,6 @@ test("switching back to a project opens the latest workspace session", async ({
       { extra: [other] },
     )
   } finally {
-    if (sessionID) {
-      const id = sessionID
-      const dirs = [rootDir, workspaceDir].filter((x): x is string => !!x)
-      await Promise.all(
-        dirs.map((directory) =>
-          createSdk(directory)
-            .session.delete({ sessionID: id })
-            .catch(() => undefined),
-        ),
-      )
-    }
-    if (workspaceDir) {
-      await cleanupTestProject(workspaceDir)
-    }
     await cleanupTestProject(other)
   }
 })
diff --git a/packages/app/e2e/projects/workspace-new-session.spec.ts b/packages/app/e2e/projects/workspace-new-session.spec.ts
index cb1294259ac6..f21ba0e4ad55 100644
--- a/packages/app/e2e/projects/workspace-new-session.spec.ts
+++ b/packages/app/e2e/projects/workspace-new-session.spec.ts
@@ -1,7 +1,7 @@
 import { base64Decode } from "@opencode-ai/util/encode"
 import type { Page } from "@playwright/test"
 import { test, expect } from "../fixtures"
-import { cleanupTestProject, openSidebar, sessionIDFromUrl, setWorkspacesEnabled } from "../actions"
+import { openSidebar, sessionIDFromUrl, setWorkspacesEnabled } from "../actions"
 import { promptSelector, workspaceItemSelector, workspaceNewSessionSelector } from "../selectors"
 import { createSdk } from "../utils"

@@ -105,48 +105,29 @@ async function sessionDirectory(directory: string, sessionID: string) {
 test("new sessions from sidebar workspace actions stay in selected workspace", async ({ page, withProject }) => {
   await page.setViewportSize({ width: 1400, height: 800 })

-  await withProject(async ({ directory, slug: root }) => {
-    const workspaces = [] as { slug: string; directory: string }[]
-    const sessions = [] as string[]
-
-    try {
-      await openSidebar(page)
-      await setWorkspacesEnabled(page, root, true)
-
-      const first = await createWorkspace(page, root, [])
-      workspaces.push(first)
-      await waitWorkspaceReady(page, first.slug)
-
-      const second = await createWorkspace(page, root, [first.slug])
-      workspaces.push(second)
-      await waitWorkspaceReady(page, second.slug)
-
-      const firstSession = await createSessionFromWorkspace(page, first.slug, `workspace one ${Date.now()}`)
-      sessions.push(firstSession.sessionID)
-
-      const secondSession = await createSessionFromWorkspace(page, second.slug, `workspace two ${Date.now()}`)
-      sessions.push(secondSession.sessionID)
-
-      const thirdSession = await createSessionFromWorkspace(page, first.slug, `workspace one again ${Date.now()}`)
-      sessions.push(thirdSession.sessionID)
-
-      await expect.poll(() => sessionDirectory(first.directory, firstSession.sessionID)).toBe(first.directory)
-      await expect.poll(() => sessionDirectory(second.directory, secondSession.sessionID)).toBe(second.directory)
-      await expect.poll(() => sessionDirectory(first.directory, thirdSession.sessionID)).toBe(first.directory)
-    } finally {
-      const dirs = [directory, ...workspaces.map((workspace) => workspace.directory)]
-      await Promise.all(
-        sessions.map((sessionID) =>
-          Promise.all(
-            dirs.map((dir) =>
-              createSdk(dir)
-                .session.delete({ sessionID })
-                .catch(() => undefined),
-            ),
-          ),
-        ),
-      )
-      await Promise.all(workspaces.map((workspace) => cleanupTestProject(workspace.directory)))
-    }
+  await withProject(async ({ directory, slug: root, trackSession, trackDirectory }) => {
+    await openSidebar(page)
+    await setWorkspacesEnabled(page, root, true)
+
+    const first = await createWorkspace(page, root, [])
+    trackDirectory(first.directory)
+    await waitWorkspaceReady(page, first.slug)
+
+    const second = await createWorkspace(page, root, [first.slug])
+    trackDirectory(second.directory)
+    await waitWorkspaceReady(page, second.slug)
+
+    const firstSession = await createSessionFromWorkspace(page, first.slug, `workspace one ${Date.now()}`)
+    trackSession(firstSession.sessionID, first.directory)
+
+    const secondSession = await createSessionFromWorkspace(page, second.slug, `workspace two ${Date.now()}`)
+    trackSession(secondSession.sessionID, second.directory)
+
+    const thirdSession = await createSessionFromWorkspace(page, first.slug, `workspace one again ${Date.now()}`)
+    trackSession(thirdSession.sessionID, first.directory)
+
+    await expect.poll(() => sessionDirectory(first.directory, firstSession.sessionID)).toBe(first.directory)
+    await expect.poll(() => sessionDirectory(second.directory, secondSession.sessionID)).toBe(second.directory)
+    await expect.poll(() => sessionDirectory(first.directory, thirdSession.sessionID)).toBe(first.directory)
   })
 })
diff --git a/packages/app/e2e/prompt/prompt-async.spec.ts b/packages/app/e2e/prompt/prompt-async.spec.ts
index 10e3fc312c46..51bfc3e4ae33 100644
--- a/packages/app/e2e/prompt/prompt-async.spec.ts
+++ b/packages/app/e2e/prompt/prompt-async.spec.ts
@@ -1,6 +1,6 @@
 import { test, expect } from "../fixtures"
 import { promptSelector } from "../selectors"
-import { sessionIDFromUrl, withSession } from "../actions"
+import { cleanupSession, sessionIDFromUrl, withSession } from "../actions"

 const text = (value: string | null) => (value ?? "").replace(/\u200B/g, "").trim()

@@ -40,7 +40,7 @@ test("prompt succeeds when sync message endpoint is unreachable", async ({ page,
       )
       .toContain(token)
   } finally {
-    await sdk.session.delete({ sessionID }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID })
   }
 })
diff --git a/packages/app/e2e/prompt/prompt-shell.spec.ts b/packages/app/e2e/prompt/prompt-shell.spec.ts
index c9880bf20c15..c92f4a2f28c 100644
--- a/packages/app/e2e/prompt/prompt-shell.spec.ts
+++ b/packages/app/e2e/prompt/prompt-shell.spec.ts
@@ -14,7 +14,7 @@ const isBash = (part: unknown): part is ToolPart => {
 test("shell mode runs a command in the project directory", async ({ page, withProject }) => {
   test.setTimeout(120_000)

-  await withProject(async ({ directory, gotoSession }) => {
+  await withProject(async ({ directory, gotoSession, trackSession }) => {
     const sdk = createSdk(directory)
     const prompt = page.locator(promptSelector)
     const cmd = process.platform === "win32" ? "dir" : "ls"
@@ -31,6 +31,7 @@ test("shell mode runs a command in the project directory", async ({ page, withPr

     const id = sessionIDFromUrl(page.url())
     if (!id) throw new Error(`Failed to parse session id from url: ${page.url()}`)
+    trackSession(id, directory)

     await expect
       .poll(
diff --git a/packages/app/e2e/prompt/prompt.spec.ts b/packages/app/e2e/prompt/prompt.spec.ts
index ff5d5daf0d49..0466d0988c8d 100644
--- a/packages/app/e2e/prompt/prompt.spec.ts
+++ b/packages/app/e2e/prompt/prompt.spec.ts
@@ -1,6 +1,6 @@
 import { test, expect } from "../fixtures"
 import { promptSelector } from "../selectors"
-import { sessionIDFromUrl, withSession } from "../actions"
+import { cleanupSession, sessionIDFromUrl, withSession } from "../actions"

 test("can send a prompt and receive a reply", async ({ page, sdk, gotoSession }) => {
   test.setTimeout(120_000)
@@ -46,7 +46,7 @@ test("can send a prompt and receive a reply", async ({ page, sdk, gotoSession }
       .toContain(token)
   } finally {
     page.off("pageerror", onPageError)
-    await sdk.session.delete({ sessionID }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID })
   }

   if (pageErrors.length > 0) {
diff --git a/packages/app/e2e/session/session-composer-dock.spec.ts b/packages/app/e2e/session/session-composer-dock.spec.ts
index 4cf075fc9a18..5e8eed2927 100644
--- a/packages/app/e2e/session/session-composer-dock.spec.ts
+++ b/packages/app/e2e/session/session-composer-dock.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { clearSessionDockSeed, seedSessionQuestion, seedSessionTodos } from "../actions"
+import { cleanupSession, clearSessionDockSeed, seedSessionQuestion, seedSessionTodos } from "../actions"
 import {
   permissionDockSelector,
   promptSelector,
@@ -26,7 +26,7 @@ async function withDockSession<T>(
   try {
     return await fn(session)
   } finally {
-    await sdk.session.delete({ sessionID: session.id }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID: session.id })
   }
 }

@@ -311,7 +311,7 @@ test("child session question request blocks parent dock and unblocks after submi
         await expect(page.locator(promptSelector)).toBeVisible()
       })
     } finally {
-      await sdk.session.delete({ sessionID: child.id }).catch(() => undefined)
+      await cleanupSession({ sdk, sessionID: child.id })
     }
   })
 })
@@ -358,7 +358,7 @@ test("child session permission request blocks parent dock and supports allow onc
         },
       )
     } finally {
-      await sdk.session.delete({ sessionID: child.id }).catch(() => undefined)
+      await cleanupSession({ sdk, sessionID: child.id })
     }
   })
 })
diff --git a/packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts b/packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts
index 09701f4a490d..d10bca0e490d 100644
--- a/packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts
+++ b/packages/app/e2e/sidebar/sidebar-popover-actions.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { closeSidebar, hoverSessionItem } from "../actions"
+import { cleanupSession, closeSidebar, hoverSessionItem } from "../actions"
 import { projectSwitchSelector } from "../selectors"

 test("collapsed sidebar popover stays open when archiving a session", async ({ page, slug, sdk, gotoSession }) => {
@@ -33,7 +33,7 @@ test("collapsed sidebar popover stays open when archiving a session", async ({ p

     await expect(twoItem).toBeVisible()
   } finally {
-    await sdk.session.delete({ sessionID: one.id }).catch(() => undefined)
-    await sdk.session.delete({ sessionID: two.id }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID: one.id })
+    await cleanupSession({ sdk, sessionID: two.id })
   }
 })
diff --git a/packages/app/e2e/sidebar/sidebar-session-links.spec.ts b/packages/app/e2e/sidebar/sidebar-session-links.spec.ts
index 052b7cb4841..2f98e94cafe 100644
--- a/packages/app/e2e/sidebar/sidebar-session-links.spec.ts
+++ b/packages/app/e2e/sidebar/sidebar-session-links.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { openSidebar, withSession } from "../actions"
+import { cleanupSession, openSidebar, withSession } from "../actions"
 import { promptSelector } from "../selectors"

 test("sidebar session links navigate to the selected session", async ({ page, slug, sdk, gotoSession }) => {
@@ -24,7 +24,7 @@ test("sidebar session links navigate to the selected session", async ({ page, sl
     await expect(page.locator(promptSelector)).toBeVisible()
     await expect(page.locator(`[data-session-id="${two.id}"] a`).first()).toHaveClass(/\bactive\b/)
   } finally {
-    await sdk.session.delete({ sessionID: one.id }).catch(() => undefined)
-    await sdk.session.delete({ sessionID: two.id }).catch(() => undefined)
+    await cleanupSession({ sdk, sessionID: one.id })
+    await cleanupSession({ sdk, sessionID: two.id })
   }
 })

PATCH

echo "Patch applied successfully."
