#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check: if the footer plugin already exists, patch is already applied
if [ -f "packages/opencode/src/cli/cmd/tui/feature-plugins/home/footer.tsx" ]; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/feature-plugins/home/footer.tsx b/packages/opencode/src/cli/cmd/tui/feature-plugins/home/footer.tsx
new file mode 100644
index 00000000000..8047c26458c
--- /dev/null
+++ b/packages/opencode/src/cli/cmd/tui/feature-plugins/home/footer.tsx
@@ -0,0 +1,93 @@
+import type { TuiPlugin, TuiPluginApi, TuiPluginModule } from "@opencode-ai/plugin/tui"
+import { createMemo, Match, Show, Switch } from "solid-js"
+import { Global } from "@/global"
+
+const id = "internal:home-footer"
+
+function Directory(props: { api: TuiPluginApi }) {
+  const theme = () => props.api.theme.current
+  const dir = createMemo(() => {
+    const dir = props.api.state.path.directory || process.cwd()
+    const out = dir.replace(Global.Path.home, "~")
+    const branch = props.api.state.vcs?.branch
+    if (branch) return out + ":" + branch
+    return out
+  })
+
+  return <text fg={theme().textMuted}>{dir()}</text>
+}
+
+function Mcp(props: { api: TuiPluginApi }) {
+  const theme = () => props.api.theme.current
+  const list = createMemo(() => props.api.state.mcp())
+  const has = createMemo(() => list().length > 0)
+  const err = createMemo(() => list().some((item) => item.status === "failed"))
+  const count = createMemo(() => list().filter((item) => item.status === "connected").length)
+
+  return (
+    <Show when={has()}>
+      <box gap={1} flexDirection="row" flexShrink={0}>
+        <text fg={theme().text}>
+          <Switch>
+            <Match when={err()}>
+              <span style={{ fg: theme().error }}>⊙ </span>
+            </Match>
+            <Match when={true}>
+              <span style={{ fg: count() > 0 ? theme().success : theme().textMuted }}>⊙ </span>
+            </Match>
+          </Switch>
+          {count()} MCP
+        </text>
+        <text fg={theme().textMuted}>/status</text>
+      </box>
+    </Show>
+  )
+}
+
+function Version(props: { api: TuiPluginApi }) {
+  const theme = () => props.api.theme.current
+
+  return (
+    <box flexShrink={0}>
+      <text fg={theme().textMuted}>{props.api.app.version}</text>
+    </box>
+  )
+}
+
+function View(props: { api: TuiPluginApi }) {
+  return (
+    <box
+      width="100%"
+      paddingTop={1}
+      paddingBottom={1}
+      paddingLeft={2}
+      paddingRight={2}
+      flexDirection="row"
+      flexShrink={0}
+      gap={2}
+    >
+      <Directory api={props.api} />
+      <Mcp api={props.api} />
+      <box flexGrow={1} />
+      <Version api={props.api} />
+    </box>
+  )
+}
+
+const tui: TuiPlugin = async (api) => {
+  api.slots.register({
+    order: 100,
+    slots: {
+      home_footer() {
+        return <View api={api} />
+      },
+    },
+  })
+}
+
+const plugin: TuiPluginModule & { id: string } = {
+  id,
+  tui,
+}
+
+export default plugin
diff --git a/packages/opencode/src/cli/cmd/tui/plugin/internal.ts b/packages/opencode/src/cli/cmd/tui/plugin/internal.ts
index 9e28bbd2e3b..856ee0ebb15 100644
--- a/packages/opencode/src/cli/cmd/tui/plugin/internal.ts
+++ b/packages/opencode/src/cli/cmd/tui/plugin/internal.ts
@@ -1,3 +1,4 @@
+import HomeFooter from "../feature-plugins/home/footer"
 import HomeTips from "../feature-plugins/home/tips"
 import SidebarContext from "../feature-plugins/sidebar/context"
 import SidebarMcp from "../feature-plugins/sidebar/mcp"
@@ -14,6 +15,7 @@ export type InternalTuiPlugin = TuiPluginModule & {
 }

 export const INTERNAL_TUI_PLUGINS: InternalTuiPlugin[] = [
+  HomeFooter,
   HomeTips,
   SidebarContext,
   SidebarMcp,
diff --git a/packages/opencode/src/cli/cmd/tui/routes/home.tsx b/packages/opencode/src/cli/cmd/tui/routes/home.tsx
index b63bf2d2dfc..8826df314b5 100644
--- a/packages/opencode/src/cli/cmd/tui/routes/home.tsx
+++ b/packages/opencode/src/cli/cmd/tui/routes/home.tsx
@@ -1,15 +1,11 @@
 import { Prompt, type PromptRef } from "@tui/component/prompt"
-import { createEffect, createMemo, Match, on, onMount, Show, Switch } from "solid-js"
-import { useTheme } from "@tui/context/theme"
+import { createEffect, on, onMount } from "solid-js"
 import { Logo } from "../component/logo"
-import { Locale } from "@/util/locale"
 import { useSync } from "../context/sync"
 import { Toast } from "../ui/toast"
 import { useArgs } from "../context/args"
-import { useDirectory } from "../context/directory"
 import { useRouteData } from "@tui/context/route"
 import { usePromptRef } from "../context/prompt"
-import { Installation } from "@/installation"
 import { useLocal } from "../context/local"
 import { TuiPluginRuntime } from "../plugin"

@@ -22,37 +18,8 @@ const placeholder = {

 export function Home() {
   const sync = useSync()
-  const { theme } = useTheme()
   const route = useRouteData("home")
   const promptRef = usePromptRef()
-  const mcp = createMemo(() => Object.keys(sync.data.mcp).length > 0)
-  const mcpError = createMemo(() => {
-    return Object.values(sync.data.mcp).some((x) => x.status === "failed")
-  })
-
-  const connectedMcpCount = createMemo(() => {
-    return Object.values(sync.data.mcp).filter((x) => x.status === "connected").length
-  })
-
-  const Hint = (
-    <box flexShrink={0} flexDirection="row" gap={1}>
-      <Show when={connectedMcpCount() > 0}>
-        <text fg={theme.text}>
-          <Switch>
-            <Match when={mcpError()}>
-              <span style={{ fg: theme.error }}>•</span> mcp errors{" "}
-              <span style={{ fg: theme.textMuted }}>ctrl+x s</span>
-            </Match>
-            <Match when={true}>
-              <span style={{ fg: theme.success }}>•</span>{" "}
-              {Locale.pluralize(connectedMcpCount(), "{} mcp server", "{} mcp servers")}
-            </Match>
-          </Switch>
-        </text>
-      </Show>
-    </box>
-  )
-
   let prompt: PromptRef | undefined
   const args = useArgs()
   const local = useLocal()
@@ -81,7 +48,6 @@ export function Home() {
       },
     ),
   )
-  const directory = useDirectory()

   return (
     <>
@@ -101,7 +67,6 @@ export function Home() {
                 prompt = r
                 promptRef.set(r)
               }}
-              hint={Hint}
               workspaceID={route.workspaceID}
               placeholders={placeholder}
             />
@@ -111,28 +76,8 @@ export function Home() {
         <box flexGrow={1} minHeight={0} />
         <Toast />
       </box>
-      <box paddingTop={1} paddingBottom={1} paddingLeft={2} paddingRight={2} flexDirection="row" flexShrink={0} gap={2}>
-        <text fg={theme.textMuted}>{directory()}</text>
-        <box gap={1} flexDirection="row" flexShrink={0}>
-          <Show when={mcp()}>
-            <text fg={theme.text}>
-              <Switch>
-                <Match when={mcpError()}>
-                  <span style={{ fg: theme.error }}>⊙ </span>
-                </Match>
-                <Match when={true}>
-                  <span style={{ fg: connectedMcpCount() > 0 ? theme.success : theme.textMuted }}>⊙ </span>
-                </Match>
-              </Switch>
-              {connectedMcpCount()} MCP
-            </text>
-            <text fg={theme.textMuted}>/status</text>
-          </Show>
-        </box>
-        <box flexGrow={1} />
-        <box flexShrink={0}>
-          <text fg={theme.textMuted}>{Installation.VERSION}</text>
-        </box>
+      <box width="100%" flexShrink={0}>
+        <TuiPluginRuntime.Slot name="home_footer" mode="single_winner" />
       </box>
     </>
   )
diff --git a/packages/plugin/src/tui.ts b/packages/plugin/src/tui.ts
index bbf3494909b..b082f6abe47 100644
--- a/packages/plugin/src/tui.ts
+++ b/packages/plugin/src/tui.ts
@@ -296,6 +296,7 @@ export type TuiSlotMap = {
     workspace_id?: string
   }
   home_bottom: {}
+  home_footer: {}
   sidebar_title: {
     session_id: string
     title: string

PATCH

echo "Patch applied successfully."
