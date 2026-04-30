#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'settings-auto-accept-permissions' packages/app/src/components/settings-general.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/app/e2e/prompt/prompt-shell.spec.ts b/packages/app/e2e/prompt/prompt-shell.spec.ts
index 28fa02dcd328..81af4cb1bc5c 100644
--- a/packages/app/e2e/prompt/prompt-shell.spec.ts
+++ b/packages/app/e2e/prompt/prompt-shell.spec.ts
@@ -1,6 +1,6 @@
 import type { ToolPart } from "@opencode-ai/sdk/v2/client"
 import { test, expect } from "../fixtures"
-import { withSession } from "../actions"
+import { closeDialog, openSettings, withSession } from "../actions"
 import { promptModelSelector, promptSelector, promptVariantSelector } from "../selectors"

 const isBash = (part: unknown): part is ToolPart => {
@@ -19,12 +19,15 @@ test("shell mode runs a command in the project directory", async ({ page, projec
   await withSession(project.sdk, `e2e shell ${Date.now()}`, async (session) => {
     project.trackSession(session.id)
     await project.gotoSession(session.id)
-    const button = page.locator('[data-action="prompt-permissions"]').first()
-    await expect(button).toBeVisible()
-    if ((await button.getAttribute("aria-pressed")) !== "true") {
-      await button.click()
-      await expect(button).toHaveAttribute("aria-pressed", "true")
+    const dialog = await openSettings(page)
+    const toggle = dialog.locator('[data-action="settings-auto-accept-permissions"]').first()
+    const input = toggle.locator('[data-slot="switch-input"]').first()
+    await expect(toggle).toBeVisible()
+    if ((await input.getAttribute("aria-checked")) !== "true") {
+      await toggle.locator('[data-slot="switch-control"]').click()
+      await expect(input).toHaveAttribute("aria-checked", "true")
     }
+    await closeDialog(page, dialog)
     await project.shell(cmd)

     await expect
diff --git a/packages/app/e2e/session/session-composer-dock.spec.ts b/packages/app/e2e/session/session-composer-dock.spec.ts
index 8eeac5b1a18a..ecacea83dcb8 100644
--- a/packages/app/e2e/session/session-composer-dock.spec.ts
+++ b/packages/app/e2e/session/session-composer-dock.spec.ts
@@ -5,7 +5,7 @@ import {
   type ComposerProbeState,
   type ComposerWindow,
 } from "../../src/testing/session-composer"
-import { cleanupSession, clearSessionDockSeed, seedSessionQuestion } from "../actions"
+import { cleanupSession, clearSessionDockSeed, closeDialog, openSettings, seedSessionQuestion } from "../actions"
 import {
   permissionDockSelector,
   promptSelector,
@@ -65,12 +65,14 @@ async function clearPermissionDock(page: any, label: RegExp) {
 }

 async function setAutoAccept(page: any, enabled: boolean) {
-  const button = page.locator('[data-action="prompt-permissions"]').first()
-  await expect(button).toBeVisible()
-  const pressed = (await button.getAttribute("aria-pressed")) === "true"
-  if (pressed === enabled) return
-  await button.click()
-  await expect(button).toHaveAttribute("aria-pressed", enabled ? "true" : "false")
+  const dialog = await openSettings(page)
+  const toggle = dialog.locator('[data-action="settings-auto-accept-permissions"]').first()
+  const input = toggle.locator('[data-slot="switch-input"]').first()
+  await expect(toggle).toBeVisible()
+  const checked = (await input.getAttribute("aria-checked")) === "true"
+  if (checked !== enabled) await toggle.locator('[data-slot="switch-control"]').click()
+  await expect(input).toHaveAttribute("aria-checked", enabled ? "true" : "false")
+  await closeDialog(page, dialog)
 }

 async function expectQuestionBlocked(page: any) {
@@ -277,6 +279,7 @@ test("default dock shows prompt input", async ({ page, project }) => {

       await expect(page.locator(sessionComposerDockSelector)).toBeVisible()
       await expect(page.locator(promptSelector)).toBeVisible()
+      await expect(page.locator('[data-action="prompt-permissions"]')).toHaveCount(0)
       await expect(page.locator(questionDockSelector)).toHaveCount(0)
       await expect(page.locator(permissionDockSelector)).toHaveCount(0)

@@ -290,10 +293,6 @@ test("default dock shows prompt input", async ({ page, project }) => {
 test("auto-accept toggle works before first submit", async ({ page, project }) => {
   await project.open()

-  const button = page.locator('[data-action="prompt-permissions"]').first()
-  await expect(button).toBeVisible()
-  await expect(button).toHaveAttribute("aria-pressed", "false")
-
   await setAutoAccept(page, true)
   await setAutoAccept(page, false)
 })
diff --git a/packages/app/src/components/prompt-input.tsx b/packages/app/src/components/prompt-input.tsx
index e9049ae7e23e..eedbc91cfdbe 100644
--- a/packages/app/src/components/prompt-input.tsx
+++ b/packages/app/src/components/prompt-input.tsx
@@ -1079,17 +1079,6 @@ export const PromptInput: Component<PromptInputProps> = (props) => {
     if (!id) return permission.isAutoAcceptingDirectory(sdk.directory)
     return permission.isAutoAccepting(id, sdk.directory)
   })
-  const acceptLabel = createMemo(() =>
-    language.t(accepting() ? "command.permissions.autoaccept.disable" : "command.permissions.autoaccept.enable"),
-  )
-  const toggleAccept = () => {
-    if (!params.id) {
-      permission.toggleAutoAcceptDirectory(sdk.directory)
-      return
-    }
-
-    permission.toggleAutoAccept(params.id, sdk.directory)
-  }

   const { abort, handleSubmit } = createPromptSubmit({
     info,
@@ -1333,11 +1322,7 @@ export const PromptInput: Component<PromptInputProps> = (props) => {
           onMouseDown={(e) => {
             const target = e.target
             if (!(target instanceof HTMLElement)) return
-            if (
-              target.closest(
-                '[data-action="prompt-attach"], [data-action="prompt-submit"], [data-action="prompt-permissions"]',
-              )
-            ) {
+            if (target.closest('[data-action="prompt-attach"], [data-action="prompt-submit"]')) {
               return
             }
             editorRef?.focus()
@@ -1597,28 +1582,6 @@ export const PromptInput: Component<PromptInputProps> = (props) => {
                     </TooltipKeybind>
                   </div>
                 </Show>
-                <TooltipKeybind
-                  placement="top"
-                  gutter={8}
-                  title={acceptLabel()}
-                  keybind={command.keybind("permissions.autoaccept")}
-                >
-                  <Button
-                    data-action="prompt-permissions"
-                    variant="ghost"
-                    onClick={toggleAccept}
-                    classList={{
-                      "h-7 w-7 p-0 shrink-0 flex items-center justify-center": true,
-                      "text-text-base": !accepting(),
-                      "hover:bg-surface-success-base": accepting(),
-                    }}
-                    style={control()}
-                    aria-label={acceptLabel()}
-                    aria-pressed={accepting()}
-                  >
-                    <Icon name="shield" size="small" classList={{ "text-icon-success-base": accepting() }} />
-                  </Button>
-                </TooltipKeybind>
               </div>
             </div>
           </div>
diff --git a/packages/app/src/components/settings-general.tsx b/packages/app/src/components/settings-general.tsx
index 8a4d498866aa..b4ac061df494 100644
--- a/packages/app/src/components/settings-general.tsx
+++ b/packages/app/src/components/settings-general.tsx
@@ -8,7 +8,9 @@ import { TextField } from "@opencode-ai/ui/text-field"
 import { Tooltip } from "@opencode-ai/ui/tooltip"
 import { useTheme, type ColorScheme } from "@opencode-ai/ui/theme/context"
 import { showToast } from "@opencode-ai/ui/toast"
+import { useParams } from "@solidjs/router"
 import { useLanguage } from "@/context/language"
+import { usePermission } from "@/context/permission"
 import { usePlatform } from "@/context/platform"
 import {
   monoDefault,
@@ -19,6 +21,7 @@ import {
   sansInput,
   useSettings,
 } from "@/context/settings"
+import { decode64 } from "@/utils/base64"
 import { playSoundById, SOUND_OPTIONS } from "@/utils/sound"
 import { Link } from "./link"
 import { SettingsList } from "./settings-list"
@@ -64,7 +67,9 @@ const playDemoSound = (id: string | undefined) => {
 export const SettingsGeneral: Component = () => {
   const theme = useTheme()
   const language = useLanguage()
+  const permission = usePermission()
   const platform = usePlatform()
+  const params = useParams()
   const settings = useSettings()

   onMount(() => {
@@ -76,6 +81,31 @@ export const SettingsGeneral: Component = () => {
   })

   const linux = createMemo(() => platform.platform === "desktop" && platform.os === "linux")
+  const dir = createMemo(() => decode64(params.dir))
+  const accepting = createMemo(() => {
+    const value = dir()
+    if (!value) return false
+    if (!params.id) return permission.isAutoAcceptingDirectory(value)
+    return permission.isAutoAccepting(params.id, value)
+  })
+
+  const toggleAccept = (checked: boolean) => {
+    const value = dir()
+    if (!value) return
+
+    if (!params.id) {
+      if (permission.isAutoAcceptingDirectory(value) === checked) return
+      permission.toggleAutoAcceptDirectory(value)
+      return
+    }
+
+    if (checked) {
+      permission.enableAutoAccept(params.id, value)
+      return
+    }
+
+    permission.disableAutoAccept(params.id, value)
+  }

   const check = () => {
     if (!platform.checkUpdate) return
@@ -201,6 +231,15 @@ export const SettingsGeneral: Component = () => {
           />
         </SettingsRow>

+        <SettingsRow
+          title={language.t("command.permissions.autoaccept.enable")}
+          description={language.t("toast.permissions.autoaccept.on.description")}
+        >
+          <div data-action="settings-auto-accept-permissions">
+            <Switch checked={accepting()} disabled={!dir()} onChange={toggleAccept} />
+          </div>
+        </SettingsRow>
+
         <SettingsRow
           title={language.t("settings.general.row.reasoningSummaries.title")}
           description={language.t("settings.general.row.reasoningSummaries.description")}

PATCH

echo "Patch applied successfully."
