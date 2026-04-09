#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'waitTerminalFocusIdle' packages/app/e2e/actions.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/app/e2e/AGENTS.md b/packages/app/e2e/AGENTS.md
index 4b62634f0bfd..f263e49a023c 100644
--- a/packages/app/e2e/AGENTS.md
+++ b/packages/app/e2e/AGENTS.md
@@ -174,6 +174,8 @@ await page.keyboard.press(`${modKey}+Comma`) // Open settings
 - In terminal tests, type through the browser. Do not write to the PTY through the SDK.
 - Use `waitTerminalReady(page, { term? })` and `runTerminal(page, { cmd, token, term?, timeout? })` from `actions.ts`.
 - These helpers use the fixture-enabled test-only terminal driver and wait for output after the terminal writer settles.
+- After opening the terminal, use `waitTerminalFocusIdle(...)` before the next keyboard action when prompt focus or keyboard routing matters.
+- This avoids racing terminal mount, focus handoff, and prompt readiness when the next step types or sends shortcuts.
 - Avoid `waitForTimeout` and custom DOM or `data-*` readiness checks.

 ### Wait on state
@@ -182,6 +184,9 @@ await page.keyboard.press(`${modKey}+Comma`) // Open settings
 - Avoid race-prone flows that assume work is finished after an action
 - Wait or poll on observable state with `expect(...)`, `expect.poll(...)`, or existing helpers
 - Prefer locator assertions like `toBeVisible()`, `toHaveCount(0)`, and `toHaveAttribute(...)` for normal UI state, and reserve `expect.poll(...)` for probe, mock, or backend state
+- Prefer semantic app state over transient DOM visibility when behavior depends on active selection, focus ownership, or async retry loops
+- Do not treat a visible element as proof that the app will route the next action to it
+- When fixing a flake, validate with `--repeat-each` and multiple workers when practical

 ### Add hooks

@@ -189,11 +194,16 @@ await page.keyboard.press(`${modKey}+Comma`) // Open settings
 - Keep these hooks minimal and purpose-built, following the style of `packages/app/src/testing/terminal.ts`
 - Test-only hooks must be inert unless explicitly enabled; do not add normal-runtime listeners, reactive subscriptions, or per-update allocations for e2e ceremony
 - When mocking routes or APIs, expose explicit mock state and wait on that before asserting post-action UI
+- Add minimal test-only probes for semantic state like the active list item or selected command when DOM intermediates are unstable
+- Prefer probing committed app state over asserting on transient highlight, visibility, or animation states

 ### Prefer helpers

 - Prefer fluent helpers and drivers when they make intent obvious and reduce locator-heavy noise
 - Use direct locators when the interaction is simple and a helper would not add clarity
+- Prefer helpers that both perform an action and verify the app consumed it
+- Avoid composing helpers redundantly when one already includes the other or already waits for the resulting state
+- If a helper already covers the required wait or verification, use it directly instead of layering extra clicks, keypresses, or assertions

 ## Writing New Tests

diff --git a/packages/app/e2e/actions.ts b/packages/app/e2e/actions.ts
index 8e21579e2134..aa047fb287ab 100644
--- a/packages/app/e2e/actions.ts
+++ b/packages/app/e2e/actions.ts
@@ -16,6 +16,7 @@ import {
   listItemSelector,
   listItemKeySelector,
   listItemKeyStartsWithSelector,
+  promptSelector,
   terminalSelector,
   workspaceItemSelector,
   workspaceMenuTriggerSelector,
@@ -61,6 +62,15 @@ async function terminalReady(page: Page, term?: Locator) {
   }, id)
 }

+async function terminalFocusIdle(page: Page, term?: Locator) {
+  const next = term ?? page.locator(terminalSelector).first()
+  const id = await terminalID(next)
+  return page.evaluate((id) => {
+    const state = (window as E2EWindow).__opencode_e2e?.terminal?.terminals?.[id]
+    return (state?.focusing ?? 0) === 0
+  }, id)
+}
+
 async function terminalHas(page: Page, input: { term?: Locator; token: string }) {
   const next = input.term ?? page.locator(terminalSelector).first()
   const id = await terminalID(next)
@@ -73,6 +83,29 @@ async function terminalHas(page: Page, input: { term?: Locator; token: string })
   )
 }

+async function promptSlashActive(page: Page, id: string) {
+  return page.evaluate((id) => {
+    const state = (window as E2EWindow).__opencode_e2e?.prompt?.current
+    if (state?.popover !== "slash") return false
+    if (!state.slash.ids.includes(id)) return false
+    return state.slash.active === id
+  }, id)
+}
+
+async function promptSlashSelects(page: Page) {
+  return page.evaluate(() => {
+    return (window as E2EWindow).__opencode_e2e?.prompt?.current?.selects ?? 0
+  })
+}
+
+async function promptSlashSelected(page: Page, input: { id: string; count: number }) {
+  return page.evaluate((input) => {
+    const state = (window as E2EWindow).__opencode_e2e?.prompt?.current
+    if (!state) return false
+    return state.selected === input.id && state.selects >= input.count
+  }, input)
+}
+
 export async function waitTerminalReady(page: Page, input?: { term?: Locator; timeout?: number }) {
   const term = input?.term ?? page.locator(terminalSelector).first()
   const timeout = input?.timeout ?? 10_000
@@ -81,6 +114,43 @@ export async function waitTerminalReady(page: Page, input?: { term?: Locator; ti
   await expect.poll(() => terminalReady(page, term), { timeout }).toBe(true)
 }

+export async function waitTerminalFocusIdle(page: Page, input?: { term?: Locator; timeout?: number }) {
+  const term = input?.term ?? page.locator(terminalSelector).first()
+  const timeout = input?.timeout ?? 10_000
+  await waitTerminalReady(page, { term, timeout })
+  await expect.poll(() => terminalFocusIdle(page, term), { timeout }).toBe(true)
+}
+
+export async function showPromptSlash(
+  page: Page,
+  input: { id: string; text: string; prompt?: Locator; timeout?: number },
+) {
+  const prompt = input.prompt ?? page.locator(promptSelector)
+  const timeout = input.timeout ?? 10_000
+  await expect
+    .poll(
+      async () => {
+        await prompt.click().catch(() => false)
+        await prompt.fill(input.text).catch(() => false)
+        return promptSlashActive(page, input.id).catch(() => false)
+      },
+      { timeout },
+    )
+    .toBe(true)
+}
+
+export async function runPromptSlash(
+  page: Page,
+  input: { id: string; text: string; prompt?: Locator; timeout?: number },
+) {
+  const prompt = input.prompt ?? page.locator(promptSelector)
+  const timeout = input.timeout ?? 10_000
+  const count = await promptSlashSelects(page)
+  await showPromptSlash(page, input)
+  await prompt.press("Enter")
+  await expect.poll(() => promptSlashSelected(page, { id: input.id, count: count + 1 }), { timeout }).toBe(true)
+}
+
 export async function runTerminal(page: Page, input: { cmd: string; token: string; term?: Locator; timeout?: number }) {
   const term = input.term ?? page.locator(terminalSelector).first()
   const timeout = input.timeout ?? 10_000
diff --git a/packages/app/e2e/fixtures.ts b/packages/app/e2e/fixtures.ts
index efefd479efcb..7bc994e50763 100644
--- a/packages/app/e2e/fixtures.ts
+++ b/packages/app/e2e/fixtures.ts
@@ -98,6 +98,9 @@ async function seedStorage(page: Page, input: { directory: string; extra?: strin
       model: {
         enabled: true,
       },
+      prompt: {
+        enabled: true,
+      },
       terminal: {
         enabled: true,
         terminals: {},
diff --git a/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts b/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
index 100d1878ab40..466b3ba1bb88 100644
--- a/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
+++ b/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { waitTerminalReady } from "../actions"
+import { runPromptSlash, waitTerminalFocusIdle } from "../actions"
 import { promptSelector, terminalSelector } from "../selectors"

 test("/terminal toggles the terminal panel", async ({ page, gotoSession }) => {
@@ -7,29 +7,12 @@ test("/terminal toggles the terminal panel", async ({ page, gotoSession }) => {

   const prompt = page.locator(promptSelector)
   const terminal = page.locator(terminalSelector)
-  const slash = page.locator('[data-slash-id="terminal.toggle"]').first()

   await expect(terminal).not.toBeVisible()

-  await prompt.fill("/terminal")
-  await expect(slash).toBeVisible()
-  await page.keyboard.press("Enter")
-  await waitTerminalReady(page, { term: terminal })
+  await runPromptSlash(page, { prompt, text: "/terminal", id: "terminal.toggle" })
+  await waitTerminalFocusIdle(page, { term: terminal })

-  // Terminal panel retries focus (immediate, RAF, 120ms, 240ms) after opening,
-  // which can steal focus from the prompt and prevent fill() from triggering
-  // the slash popover. Re-attempt click+fill until all retries are exhausted
-  // and the popover appears.
-  await expect
-    .poll(
-      async () => {
-        await prompt.click().catch(() => false)
-        await prompt.fill("/terminal").catch(() => false)
-        return slash.isVisible().catch(() => false)
-      },
-      { timeout: 10_000 },
-    )
-    .toBe(true)
-  await page.keyboard.press("Enter")
+  await runPromptSlash(page, { prompt, text: "/terminal", id: "terminal.toggle" })
   await expect(terminal).not.toBeVisible()
 })
diff --git a/packages/app/e2e/settings/settings-keybinds.spec.ts b/packages/app/e2e/settings/settings-keybinds.spec.ts
index 9fc2a50ad372..5789dc0eb025 100644
--- a/packages/app/e2e/settings/settings-keybinds.spec.ts
+++ b/packages/app/e2e/settings/settings-keybinds.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { openSettings, closeDialog, waitTerminalReady, withSession } from "../actions"
+import { openSettings, closeDialog, waitTerminalFocusIdle, withSession } from "../actions"
 import { keybindButtonSelector, terminalSelector } from "../selectors"
 import { modKey } from "../utils"

@@ -302,7 +302,7 @@ test("changing terminal toggle keybind works", async ({ page, gotoSession }) =>
   await expect(terminal).not.toBeVisible()

   await page.keyboard.press(`${modKey}+Y`)
-  await waitTerminalReady(page, { term: terminal })
+  await waitTerminalFocusIdle(page, { term: terminal })

   await page.keyboard.press(`${modKey}+Y`)
   await expect(terminal).not.toBeVisible()
diff --git a/packages/app/e2e/terminal/terminal-init.spec.ts b/packages/app/e2e/terminal/terminal-init.spec.ts
index d9bbfa2bed9d..689d0436a56a 100644
--- a/packages/app/e2e/terminal/terminal-init.spec.ts
+++ b/packages/app/e2e/terminal/terminal-init.spec.ts
@@ -1,5 +1,5 @@
 import { test, expect } from "../fixtures"
-import { waitTerminalReady } from "../actions"
+import { waitTerminalFocusIdle, waitTerminalReady } from "../actions"
 import { promptSelector, terminalSelector } from "../selectors"
 import { terminalToggleKey } from "../utils"

@@ -14,7 +14,7 @@ test("smoke terminal mounts and can create a second tab", async ({ page, gotoSes
     await page.keyboard.press(terminalToggleKey)
   }

-  await waitTerminalReady(page, { term: terminals.first() })
+  await waitTerminalFocusIdle(page, { term: terminals.first() })
   await expect(terminals).toHaveCount(1)

   // Ghostty captures a lot of keybinds when focused; move focus back
diff --git a/packages/app/src/components/prompt-input.tsx b/packages/app/src/components/prompt-input.tsx
index b2553e4c024f..4fbc82a7068f 100644
--- a/packages/app/src/components/prompt-input.tsx
+++ b/packages/app/src/components/prompt-input.tsx
@@ -36,6 +36,7 @@ import { useLanguage } from "@/context/language"
 import { usePlatform } from "@/context/platform"
 import { useSessionLayout } from "@/pages/session/session-layout"
 import { createSessionTabs } from "@/pages/session/helpers"
+import { promptEnabled, promptProbe } from "@/testing/prompt"
 import { createTextFragment, getCursorPosition, setCursorPosition, setRangeEdge } from "./prompt-input/editor-dom"
 import { createPromptAttachments } from "./prompt-input/attachments"
 import { ACCEPTED_FILE_TYPES } from "./prompt-input/files"
@@ -604,6 +605,7 @@ export const PromptInput: Component<PromptInputProps> = (props) => {

   const handleSlashSelect = (cmd: SlashCommand | undefined) => {
     if (!cmd) return
+    promptProbe.select(cmd.id)
     closePopover()

     if (cmd.type === "custom") {
@@ -692,6 +694,20 @@ export const PromptInput: Component<PromptInputProps> = (props) => {
     })
   })

+  if (promptEnabled()) {
+    createEffect(() => {
+      promptProbe.set({
+        popover: store.popover,
+        slash: {
+          active: slashActive() ?? null,
+          ids: slashFlat().map((cmd) => cmd.id),
+        },
+      })
+    })
+
+    onCleanup(() => promptProbe.clear())
+  }
+
   const selectPopoverActive = () => {
     if (store.popover === "at") {
       const items = atFlat()
diff --git a/packages/app/src/pages/session/terminal-panel.tsx b/packages/app/src/pages/session/terminal-panel.tsx
index e78ebecfc41f..d62d91c1979e 100644
--- a/packages/app/src/pages/session/terminal-panel.tsx
+++ b/packages/app/src/pages/session/terminal-panel.tsx
@@ -18,8 +18,10 @@ import { terminalTabLabel } from "@/pages/session/terminal-label"
 import { createSizing, focusTerminalById } from "@/pages/session/helpers"
 import { getTerminalHandoff, setTerminalHandoff } from "@/pages/session/handoff"
 import { useSessionLayout } from "@/pages/session/session-layout"
+import { terminalProbe } from "@/testing/terminal"

 export function TerminalPanel() {
+  const delays = [120, 240]
   const layout = useLayout()
   const terminal = useTerminal()
   const language = useLanguage()
@@ -79,16 +81,20 @@ export function TerminalPanel() {
   )

   const focus = (id: string) => {
+    const probe = terminalProbe(id)
+    probe.focus(delays.length + 1)
     focusTerminalById(id)

     const frame = requestAnimationFrame(() => {
+      probe.step()
       if (!opened()) return
       if (terminal.active() !== id) return
       focusTerminalById(id)
     })

-    const timers = [120, 240].map((ms) =>
+    const timers = delays.map((ms) =>
       window.setTimeout(() => {
+        probe.step()
         if (!opened()) return
         if (terminal.active() !== id) return
         focusTerminalById(id)
@@ -96,6 +102,7 @@ export function TerminalPanel() {
     )

     return () => {
+      probe.focus(0)
       cancelAnimationFrame(frame)
       for (const timer of timers) clearTimeout(timer)
     }
diff --git a/packages/app/src/testing/prompt.ts b/packages/app/src/testing/prompt.ts
new file mode 100644
index 000000000000..e11462f30137
--- /dev/null
+++ b/packages/app/src/testing/prompt.ts
@@ -0,0 +1,56 @@
+import type { E2EWindow } from "./terminal"
+
+export type PromptProbeState = {
+  popover: "at" | "slash" | null
+  slash: {
+    active: string | null
+    ids: string[]
+  }
+  selected: string | null
+  selects: number
+}
+
+export const promptEnabled = () => {
+  if (typeof window === "undefined") return false
+  return (window as E2EWindow).__opencode_e2e?.prompt?.enabled === true
+}
+
+const root = () => {
+  if (!promptEnabled()) return
+  return (window as E2EWindow).__opencode_e2e?.prompt
+}
+
+export const promptProbe = {
+  set(input: Omit<PromptProbeState, "selected" | "selects">) {
+    const state = root()
+    if (!state) return
+    state.current = {
+      popover: input.popover,
+      slash: {
+        active: input.slash.active,
+        ids: [...input.slash.ids],
+      },
+      selected: state.current?.selected ?? null,
+      selects: state.current?.selects ?? 0,
+    }
+  },
+  select(id: string) {
+    const state = root()
+    if (!state) return
+    const prev = state.current
+    state.current = {
+      popover: prev?.popover ?? null,
+      slash: {
+        active: prev?.slash.active ?? null,
+        ids: [...(prev?.slash.ids ?? [])],
+      },
+      selected: id,
+      selects: (prev?.selects ?? 0) + 1,
+    }
+  },
+  clear() {
+    const state = root()
+    if (!state) return
+    state.current = undefined
+  },
+}
diff --git a/packages/app/src/testing/terminal.ts b/packages/app/src/testing/terminal.ts
index af1c33309262..2bca39b31cdf 100644
--- a/packages/app/src/testing/terminal.ts
+++ b/packages/app/src/testing/terminal.ts
@@ -7,6 +7,7 @@ export type TerminalProbeState = {
   connects: number
   rendered: string
   settled: number
+  focusing: number
 }

 type TerminalProbeControl = {
@@ -19,6 +20,10 @@ export type E2EWindow = Window & {
       enabled?: boolean
       current?: ModelProbeState
     }
+    prompt?: {
+      enabled?: boolean
+      current?: import("./prompt").PromptProbeState
+    }
     terminal?: {
       enabled?: boolean
       terminals?: Record<string, TerminalProbeState>
@@ -32,6 +37,7 @@ const seed = (): TerminalProbeState => ({
   connects: 0,
   rendered: "",
   settled: 0,
+  focusing: 0,
 })

 const root = () => {
@@ -88,6 +94,15 @@ export const terminalProbe = (id: string) => {
       const prev = state[id] ?? seed()
       state[id] = { ...prev, settled: prev.settled + 1 }
     },
+    focus(count: number) {
+      set({ focusing: Math.max(0, count) })
+    },
+    step() {
+      const state = terms()
+      if (!state) return
+      const prev = state[id] ?? seed()
+      state[id] = { ...prev, focusing: Math.max(0, prev.focusing - 1) }
+    },
     control(next: Partial<TerminalProbeControl>) {
       const state = controls()
       if (!state) return

PATCH

echo "Patch applied successfully."
