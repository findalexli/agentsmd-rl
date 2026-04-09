#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if [ -f "packages/app/src/testing/terminal.ts" ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/packages/app/e2e/AGENTS.md b/packages/app/e2e/AGENTS.md
index 8bfbd111b250..cb8080fb2526 100644
--- a/packages/app/e2e/AGENTS.md
+++ b/packages/app/e2e/AGENTS.md
@@ -70,6 +70,8 @@ test("test description", async ({ page, sdk, gotoSession }) => {
 - `openSettings(page)` - Open settings dialog
 - `closeDialog(page, dialog)` - Close any dialog
 - `openSidebar(page)` / `closeSidebar(page)` - Toggle sidebar
+- `waitTerminalReady(page, { term? })` - Wait for a mounted terminal to connect and finish rendering output
+- `runTerminal(page, { cmd, token, term?, timeout? })` - Type into the terminal via the browser and wait for rendered output
 - `withSession(sdk, title, callback)` - Create temp session
 - `withProject(...)` - Create temp project/workspace
 - `sessionIDFromUrl(url)` - Read session ID from URL
@@ -167,6 +169,13 @@ await page.keyboard.press(`${modKey}+B`) // Toggle sidebar
 await page.keyboard.press(`${modKey}+Comma`) // Open settings
 ```

+### Terminal Tests
+
+- In terminal tests, type through the browser. Do not write to the PTY through the SDK.
+- Use `waitTerminalReady(page, { term? })` and `runTerminal(page, { cmd, token, term?, timeout? })` from `actions.ts`.
+- These helpers use the fixture-enabled test-only terminal driver and wait for output after the terminal writer settles.
+- Avoid `waitForTimeout` and custom DOM or `data-*` readiness checks.
+
 ## Writing New Tests

 1. Choose appropriate folder or create new one
diff --git a/packages/app/e2e/actions.ts b/packages/app/e2e/actions.ts
index 86147dc65d50..f721e0a7c945 100644
--- a/packages/app/e2e/actions.ts
+++ b/packages/app/e2e/actions.ts
@@ -3,6 +3,7 @@ import fs from "node:fs/promises"
 import os from "node:os"
 import path from "node:path"
 import { execSync } from "node:child_process"
+import { terminalAttr, type E2EWindow } from "../src/testing/terminal"
 import { createSdk, modKey, resolveDirectory, serverUrl } from "./utils"
 import {
   dropdownMenuTriggerSelector,
@@ -15,6 +16,7 @@ import {
   listItemSelector,
   listItemKeySelector,
   listItemKeyStartsWithSelector,
+  terminalSelector,
   workspaceItemSelector,
   workspaceMenuTriggerSelector,
 } from "./selectors"
@@ -28,6 +30,57 @@ export async function defocus(page: Page) {
     .catch(() => undefined)
 }

+async function terminalID(term: Locator) {
+  const id = await term.getAttribute(terminalAttr)
+  if (id) return id
+  throw new Error(`Active terminal missing ${terminalAttr}`)
+}
+
+async function terminalReady(page: Page, term?: Locator) {
+  const next = term ?? page.locator(terminalSelector).first()
+  const id = await terminalID(next)
+  return page.evaluate((id) => {
+    const state = (window as E2EWindow).__opencode_e2e?.terminal?.terminals?.[id]
+    return !!state?.connected && (state.settled ?? 0) > 0
+  }, id)
+}
+
+async function terminalHas(page: Page, input: { term?: Locator; token: string }) {
+  const next = input.term ?? page.locator(terminalSelector).first()
+  const id = await terminalID(next)
+  return page.evaluate(
+    (input) => {
+      const state = (window as E2EWindow).__opencode_e2e?.terminal?.terminals?.[input.id]
+      return state?.rendered.includes(input.token) ?? false
+    },
+    { id, token: input.token },
+  )
+}
+
+export async function waitTerminalReady(page: Page, input?: { term?: Locator; timeout?: number }) {
+  const term = input?.term ?? page.locator(terminalSelector).first()
+  const timeout = input?.timeout ?? 10_000
+  await expect(term).toBeVisible()
+  await expect(term.locator("textarea")).toHaveCount(1)
+  await expect
+    .poll(() => terminalReady(page, term), { timeout })
+    .toBe(true)
+}
+
+export async function runTerminal(page: Page, input: { cmd: string; token: string; term?: Locator; timeout?: number }) {
+  const term = input.term ?? page.locator(terminalSelector).first()
+  const timeout = input.timeout ?? 10_000
+  await waitTerminalReady(page, { term, timeout })
+  const textarea = term.locator("textarea")
+  await term.click()
+  await expect(textarea).toBeFocused()
+  await page.keyboard.type(input.cmd)
+  await page.keyboard.press("Enter")
+  await expect
+    .poll(() => terminalHas(page, { term, token: input.token }), { timeout })
+    .toBe(true)
+}
+
 export async function openPalette(page: Page) {
   await defocus(page)
   await page.keyboard.press(`${modKey}+P`)
diff --git a/packages/app/e2e/fixtures.ts b/packages/app/e2e/fixtures.ts
index 6a35c6901eae..cf59eeb4761a 100644
--- a/packages/app/e2e/fixtures.ts
+++ b/packages/app/e2e/fixtures.ts
@@ -1,4 +1,5 @@
 import { test as base, expect, type Page } from "@playwright/test"
+import type { E2EWindow } from "../src/testing/terminal"
 import { cleanupSession, cleanupTestProject, createTestProject, seedProjects, sessionIDFromUrl } from "./actions"
 import { promptSelector } from "./selectors"
 import { createSdk, dirSlug, getWorktree, sessionPath } from "./utils"
@@ -91,6 +92,14 @@ export const test = base.extend<TestFixtures, WorkerFixtures>({
 async function seedStorage(page: Page, input: { directory: string; extra?: string[] }) {
   await seedProjects(page, input)
   await page.addInitScript(() => {
+    const win = window as E2EWindow
+    win.__opencode_e2e = {
+      ...win.__opencode_e2e,
+      terminal: {
+        enabled: true,
+        terminals: {},
+      },
+    }
     localStorage.setItem(
       "opencode.global.dat:model",
       JSON.stringify({
diff --git a/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts b/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
index fa884b752d7b..100d1878ab40 100644
--- a/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
+++ b/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
@@ -1,4 +1,5 @@
 import { test, expect } from "../fixtures"
+import { waitTerminalReady } from "../actions"
 import { promptSelector, terminalSelector } from "../selectors"

 test("/terminal toggles the terminal panel", async ({ page, gotoSession }) => {
@@ -13,7 +14,7 @@ test("/terminal toggles the terminal panel", async ({ page, gotoSession }) => {
   await prompt.fill("/terminal")
   await expect(slash).toBeVisible()
   await page.keyboard.press("Enter")
-  await expect(terminal).toBeVisible()
+  await waitTerminalReady(page, { term: terminal })

   // Terminal panel retries focus (immediate, RAF, 120ms, 240ms) after opening,
   // which can steal focus from the prompt and prevent fill() from triggering
diff --git a/packages/app/e2e/settings/settings-keybinds.spec.ts b/packages/app/e2e/settings/settings-keybinds.spec.ts
index e0d590b31af9..9fc2a50ad372 100644
--- a/packages/app/e2e/settings/settings-keybinds.spec.ts
+++ b/packages/app/e2e/settings/settings-keybinds.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { openSettings, closeDialog, withSession } from "../actions"
+import { openSettings, closeDialog, waitTerminalReady, withSession } from "../actions"
 import { keybindButtonSelector, terminalSelector } from "../selectors"
 import { modKey } from "../utils"

@@ -302,7 +302,7 @@ test("changing terminal toggle keybind works", async ({ page, gotoSession }) =>
   await expect(terminal).not.toBeVisible()

   await page.keyboard.press(`${modKey}+Y`)
-  await expect(terminal).toBeVisible()
+  await waitTerminalReady(page, { term: terminal })

   await page.keyboard.press(`${modKey}+Y`)
   await expect(terminal).not.toBeVisible()
diff --git a/packages/app/e2e/terminal/terminal-init.spec.ts b/packages/app/e2e/terminal/terminal-init.spec.ts
index 18991bf76364..d9bbfa2bed9d 100644
--- a/packages/app/e2e/terminal/terminal-init.spec.ts
+++ b/packages/app/e2e/terminal/terminal-init.spec.ts
@@ -1,4 +1,5 @@
 import { test, expect } from "../fixtures"
+import { waitTerminalReady } from "../actions"
 import { promptSelector, terminalSelector } from "../selectors"
 import { terminalToggleKey } from "../utils"

@@ -13,8 +14,7 @@ test("smoke terminal mounts and can create a second tab", async ({ page, gotoS
     await page.keyboard.press(terminalToggleKey)
   }

-  await expect(terminals.first()).toBeVisible()
-  await expect(terminals.first().locator("textarea")).toHaveCount(1)
+  await waitTerminalReady(page, { term: terminals.first() })
   await expect(terminals).toHaveCount(1)

   // Ghostty captures a lot of keybinds when focused; move focus back
@@ -24,5 +24,5 @@ test("smoke terminal mounts and can create a second tab", async ({ page, gotoS

   await expect(tabs).toHaveCount(2)
   await expect(terminals).toHaveCount(1)
-  await expect(terminals.first().locator("textarea")).toHaveCount(1)
+  await waitTerminalReady(page, { term: terminals.first() })
 })
diff --git a/packages/app/e2e/terminal/terminal-tabs.spec.ts b/packages/app/e2e/terminal/terminal-tabs.spec.ts
index afa6254cd0ab..ca1f7eee8b72 100644
--- a/packages/app/e2e/terminal/terminal-tabs.spec.ts
+++ b/packages/app/e2e/terminal/terminal-tabs.spec.ts
@@ -1,4 +1,5 @@
 import type { Page } from "@playwright/test"
+import { runTerminal, waitTerminalReady } from "../actions"
 import { test, expect } from "../fixtures"
 import { terminalSelector } from "../selectors"
 import { terminalToggleKey, workspacePersistKey } from "../utils"
@@ -17,16 +18,7 @@ async function open(page: Page) {
   const terminal = page.locator(terminalSelector)
   const visible = await terminal.isVisible().catch(() => false)
   if (!visible) await page.keyboard.press(terminalToggleKey)
-  await expect(terminal).toBeVisible()
-  await expect(terminal.locator("textarea")).toHaveCount(1)
-}
-
-async function run(page: Page, cmd: string) {
-  const terminal = page.locator(terminalSelector)
-  await expect(terminal).toBeVisible()
-  await terminal.click()
-  await page.keyboard.type(cmd)
-  await page.keyboard.press("Enter")
+  await waitTerminalReady(page, { term: terminal })
 }

 async function store(page: Page, key: string) {
@@ -56,15 +48,16 @@ test("inactive terminal tab buffers persist across tab switches", async ({ page
     await gotoSession()
     await open(page)

-    await run(page, `echo ${one}`)
+    await runTerminal(page, { cmd: `echo ${one}`, token: one })

     await page.getByRole("button", { name: /new terminal/i }).click()
     await expect(tabs).toHaveCount(2)

-    await run(page, `echo ${two}`)
+    await runTerminal(page, { cmd: `echo ${two}`, token: two })

     await first.click()
     await expect(first).toHaveAttribute("aria-selected", "true")
+
     await expect
       .poll(
         async () => {
@@ -76,7 +69,7 @@ test("inactive terminal tab buffers persist across tab switches", async ({ page
             second: second.includes(two),
           }
         },
-        { timeout: 30_000 },
+        { timeout: 5_000 },
       )
       .toEqual({ first: false, second: true })

@@ -93,7 +86,7 @@ test("inactive terminal tab buffers persist across tab switches", async ({ page
             second: second.includes(two),
           }
         },
-        { timeout: 30_000 },
+        { timeout: 5_000 },
       )
       .toEqual({ first: true, second: false })
   })
diff --git a/packages/app/e2e/terminal/terminal.spec.ts b/packages/app/e2e/terminal/terminal.spec.ts
index ef88aa34e52d..768f7b182133 100644
--- a/packages/app/e2e/terminal/terminal.spec.ts
+++ b/packages/app/e2e/terminal/terminal.spec.ts
@@ -1,4 +1,5 @@
 import { test, expect } from "../fixtures"
+import { waitTerminalReady } from "../actions"
 import { terminalSelector } from "../selectors"
 import { terminalToggleKey } from "../utils"

@@ -13,5 +14,5 @@ test("terminal panel can be toggled", async ({ page, gotoSession }) => {
   }

   await page.keyboard.press(terminalToggleKey)
-  await expect(terminal).toBeVisible()
+  await waitTerminalReady(page, { term: terminal })
 })
diff --git a/packages/app/src/components/terminal.tsx b/packages/app/src/components/terminal.tsx
index 120af0a17269..ed4fd4c4fc57 100644
--- a/packages/app/src/components/terminal.tsx
+++ b/packages/app/src/components/terminal.tsx
@@ -10,6 +10,7 @@ import { useSDK } from "@/context/sdk"
 import { useServer } from "@/context/server"
 import { monoFontFamily, useSettings } from "@/context/settings"
 import type { LocalPTY } from "@/context/terminal"
+import { terminalAttr, terminalProbe } from "@/testing/terminal"
 import { disposeIfDisposable, getHoveredLinkText, setOptionIfSupported } from "@/utils/runtime-adapters"
 import { terminalWriter } from "@/utils/terminal-writer"

@@ -160,6 +161,7 @@ export const Terminal = (props: TerminalProps) => {
   let container!: HTMLDivElement
   const [local, others] = splitProps(props, ["pty", "class", "classList", "autoFocus", "onConnect", "onConnectError"])
   const id = local.pty.id
+  const probe = terminalProbe(id)
   const restore = typeof local.pty.buffer === "string" ? local.pty.buffer : ""
   const restoreSize =
     restore &&
@@ -326,6 +328,9 @@ export const Terminal = (props: TerminalProps) => {
   }

   onMount(() => {
+    probe.init()
+    cleanups.push(() => probe.drop())
+
     const run = async () => {
       const loaded = await loadGhostty()
       if (disposed) return
@@ -353,7 +358,13 @@ export const Terminal = (props: TerminalProps) => {
       }
       ghostty = g
       term = t
-      output = terminalWriter((data, done) => t.write(data, done))
+      output = terminalWriter((data, done) =>
+        t.write(data, () => {
+          probe.render(data)
+          probe.settle()
+          done?.()
+        }),
+      )

       t.attachCustomKeyEventHandler((event) => {
         const key = event.key.toLowerCase()
@@ -441,10 +452,6 @@ export const Terminal = (props: TerminalProps) => {
         startResize()
       }

-      // t.onScroll((ydisp) => {
-      // console.log("Scroll position:", ydisp)
-      // })
-
       const once = { value: false }
       let closing = false

@@ -460,6 +467,7 @@ export const Terminal = (props: TerminalProps) {
       ws = socket

       const handleOpen = () => {
+        probe.connect()
         local.onConnect?.()
         scheduleSize(t.cols, t.rows)
       }
@@ -560,6 +568,7 @@ export const Terminal = (props: TerminalProps) {
     <div
       ref={container}
       data-component="terminal"
+      {...{ [terminalAttr]: id }}
       data-prevent-autofocus
       tabIndex={-1}
       style={{ "background-color": terminalColors().background }}
diff --git a/packages/app/src/testing/terminal.ts b/packages/app/src/testing/terminal.ts
new file mode 100644
index 000000000000..aa197440455a
--- /dev/null
+++ b/packages/app/src/testing/terminal.ts
@@ -0,0 +1,64 @@
+export const terminalAttr = "data-pty-id"
+
+export type TerminalProbeState = {
+  connected: boolean
+  rendered: string
+  settled: number
+}
+
+export type E2EWindow = Window & {
+  __opencode_e2e?: {
+    terminal?: {
+      enabled?: boolean
+      terminals?: Record<string, TerminalProbeState>
+    }
+  }
+}
+
+const seed = (): TerminalProbeState => ({
+  connected: false,
+  rendered: "",
+  settled: 0,
+})
+
+const root = () => {
+  if (typeof window === "undefined") return
+  const state = (window as E2EWindow).__opencode_e2e?.terminal
+  if (!state?.enabled) return
+  state.terminals ??= {}
+  return state.terminals
+}
+
+export const terminalProbe = (id: string) => {
+  const set = (next: Partial<TerminalProbeState>) => {
+    const terms = root()
+    if (!terms) return
+    terms[id] = { ...(terms[id] ?? seed()), ...next }
+  }
+
+  return {
+    init() {
+      set(seed())
+    },
+    connect() {
+      set({ connected: true })
+    },
+    render(data: string) {
+      const terms = root()
+      if (!terms) return
+      const prev = terms[id] ?? seed()
+      terms[id] = { ...prev, rendered: prev.rendered + data }
+    },
+    settle() {
+      const terms = root()
+      if (!terms) return
+      const prev = terms[id] ?? seed()
+      terms[id] = { ...prev, settled: prev.settled + 1 }
+    },
+    drop() {
+      const terms = root()
+      if (!terms) return
+      delete terms[id]
+    },
+  }
+}

PATCH

echo "Patch applied successfully."
