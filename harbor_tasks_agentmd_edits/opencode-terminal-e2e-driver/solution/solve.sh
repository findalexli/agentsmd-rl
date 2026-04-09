#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'waitTerminalReady' packages/app/e2e/actions.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
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
+  connects: number
+  rendered: string
+  settled: number
+  focusing: number
+}
+
+type TerminalProbeControl = {
+  disconnect?: VoidFunction
+}
+
+export type E2EWindow = Window & {
+  __opencode_e2e?: {
+    model?: {
+      enabled?: boolean
+      current?: ModelProbeState
+    }
+    prompt?: {
+      enabled?: boolean
+      current?: import("./prompt").PromptProbeState
+      sent?: import("./prompt").PromptSendState
+    }
+    terminal?: {
+      enabled?: boolean
+      terminals?: Record<string, TerminalProbeState>
+      controls?: Record<string, TerminalProbeControl>
+    }
+  }
+}
+
+const seed = (): TerminalProbeState => ({
+  connected: false,
+  connects: 0,
+  rendered: "",
+  settled: 0,
+  focusing: 0,
+})
+
+const root = () => {
+  if (typeof window === "undefined") return
+  const state = (window as E2EWindow).__opencode_e2e?.terminal
+  if (!state?.enabled) return
+  return state
+}
+
+const terms = () => {
+  const state = root()
+  if (!state) return
+  state.terminals ??= {}
+  return state.terminals
+}
+
+const controls = () => {
+  const state = root()
+  if (!state) return
+  state.controls ??= {}
+  return state.controls
+}
+
+export const terminalProbe = (id: string) => {
+  const set = (next: Partial<TerminalProbeState>) => {
+    const state = terms()
+    if (!state) return
+    state[id] = { ...(state[id] ?? seed()), ...next }
+  }
+
+  return {
+    init() {
+      set(seed())
+    },
+    connect() {
+      const state = terms()
+      if (!state) return
+      const prev = state[id] ?? seed()
+      state[id] = {
+        ...prev,
+        connected: true,
+        connects: prev.connects + 1,
+      }
+    },
+    render(data: string) {
+      const state = terms()
+      if (!state) return
+      const prev = state[id] ?? seed()
+      state[id] = { ...prev, rendered: prev.rendered + data }
+    },
+    settle() {
+      const state = terms()
+      if (!state) return
+      const prev = state[id] ?? seed()
+      state[id] = { ...prev, settled: prev.settled + 1 }
+    },
+    focus(count: number) {
+      set({ focusing: Math.max(0, count) })
+    },
+    step() {
+      const state = terms()
+      if (!state) return
+      const prev = state[id] ?? seed()
+      state[id] = { ...prev, focusing: Math.max(0, prev.focusing - 1) }
+    },
+    control(next: Partial<TerminalProbeControl>) {
+      const state = controls()
+      if (!state) return
+      state[id] = { ...(state[id] ?? {}), ...next }
+    },
+    drop() {
+      const state = terms()
+      if (state) delete state[id]
+      const control = controls()
+      if (control) delete control[id]
+    },
+  }
+}
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

@@ -460,6 +467,7 @@ export const Terminal = (props: TerminalProps) => {
       ws = socket

       const handleOpen = () => {
+        probe.connect()
         local.onConnect?.()
         scheduleSize(t.cols, t.rows)
       }
@@ -560,6 +568,7 @@ export const Terminal = (props: TerminalProps) => {
     <div
       ref={container}
       data-component="terminal"
+      {...{ [terminalAttr]: id }}
       data-prevent-autofocus
       tabIndex={-1}
       style={{ "background-color": terminalColors().background }}
diff --git a/packages/app/e2e/AGENTS.md b/packages/app/e2e/AGENTS.md
index 8bfbd111b250..cb8080fb2526 100644
--- a/packages/app/e2e/AGENTS.md
+++ b/packages/app/e2e/AGENTS.md
@@ -70,6 +70,8 @@ test("test description", async ({ page, gotoSession }) => {
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

PATCH

echo "Patch applied successfully."
