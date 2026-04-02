#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if header.tsx is already deleted (key indicator of fix applied)
if [ ! -f "packages/opencode/src/cli/cmd/tui/routes/session/header.tsx" ]; then
    echo "Fix already applied (header.tsx deleted)."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/app.tsx b/packages/opencode/src/cli/cmd/tui/app.tsx
index 2557d965ad8..5a2e1b15588 100644
--- a/packages/opencode/src/cli/cmd/tui/app.tsx
+++ b/packages/opencode/src/cli/cmd/tui/app.tsx
@@ -584,7 +584,6 @@ function App(props: { onSnapshot?: () => Promise<string[]> }) {
       value: "variant.cycle",
       keybind: "variant_cycle",
       category: "Agent",
-      hidden: true,
       onSelect: () => {
         local.model.variant.cycle()
       },
diff --git a/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx b/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
index 257248c3c12..f6ac9660d30 100644
--- a/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
+++ b/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx
@@ -5,7 +5,7 @@ import path from "path"
 import { Filesystem } from "@/util/filesystem"
 import { useLocal } from "@tui/context/local"
 import { useTheme } from "@tui/context/theme"
-import { EmptyBorder } from "@tui/component/border"
+import { EmptyBorder, SplitBorder } from "@tui/component/border"
 import { useSDK } from "@tui/context/sdk"
 import { useRoute } from "@tui/context/route"
 import { useSync } from "@tui/context/sync"
@@ -22,7 +22,7 @@ import { useKeyboard, useRenderer } from "@opentui/solid"
 import { Editor } from "@tui/util/editor"
 import { useExit } from "../../context/exit"
 import { Clipboard } from "../../util/clipboard"
-import type { FilePart } from "@opencode-ai/sdk/v2"
+import type { AssistantMessage, FilePart } from "@opencode-ai/sdk/v2"
 import { TuiEvent } from "../../event"
 import { iife } from "@/util/iife"
 import { Locale } from "@/util/locale"
@@ -59,6 +59,10 @@ export type PromptRef = {

 const PLACEHOLDERS = ["Fix a TODO in the codebase", "What is the tech stack of this project?", "Fix broken tests"]
 const SHELL_PLACEHOLDERS = ["ls -la", "git status", "pwd"]
+const money = new Intl.NumberFormat("en-US", {
+  style: "currency",
+  currency: "USD",
+})

 export function Prompt(props: PromptProps) {
   let input: TextareaRenderable
@@ -122,6 +126,25 @@ export function Prompt(props: PromptProps) {
     return messages.findLast((m) => m.role === "user")
   })

+  const usage = createMemo(() => {
+    if (!props.sessionID) return
+    const msg = sync.data.message[props.sessionID] ?? []
+    const last = msg.findLast((item): item is AssistantMessage => item.role === "assistant" && item.tokens.output > 0)
+    if (!last) return
+
+    const tokens =
+      last.tokens.input + last.tokens.output + last.tokens.reasoning + last.tokens.cache.read + last.tokens.cache.write
+    if (tokens <= 0) return
+
+    const model = sync.data.provider.find((item) => item.id === last.providerID)?.models[last.modelID]
+    const pct = model?.limit.context ? `${Math.round((tokens / model.limit.context) * 100)}%` : undefined
+    const cost = msg.reduce((sum, item) => sum + (item.role === "assistant" ? item.cost : 0), 0)
+    return {
+      context: pct ? `${Locale.number(tokens)} (${pct})` : Locale.number(tokens),
+      cost: cost > 0 ? money.format(cost) : undefined,
+    }
+  })
+
   const [store, setStore] = createStore<{
     prompt: PromptInfo
     mode: "normal" | "shell"
@@ -833,8 +856,7 @@ export function Prompt(props: PromptProps) {
           border={["left"]}
           borderColor={highlight()}
           customBorderChars={{
-            ...EmptyBorder,
-            vertical: "┃",
+            ...SplitBorder.customBorderChars,
             bottomLeft: "╹",
           }}
         >
@@ -1158,14 +1180,25 @@ export function Prompt(props: PromptProps) {
             <box gap={2} flexDirection="row">
               <Switch>
                 <Match when={store.mode === "normal"}>
-                  <Show when={local.model.variant.list().length > 0}>
-                    <text fg={theme.text}>
-                      {keybind.print("variant_cycle")} <span style={{ fg: theme.textMuted }}>variants</span>
-                    </text>
-                  </Show>
-                  <text fg={theme.text}>
-                    {keybind.print("agent_cycle")} <span style={{ fg: theme.textMuted }}>agents</span>
-                  </text>
+                  <Switch>
+                    <Match when={usage()}>
+                      {(item) => (
+                        <text fg={theme.textMuted} wrapMode="none">
+                          {[item().context, item().cost].filter(Boolean).join(" · ")}
+                        </text>
+                      )}
+                    </Match>
+                    <Match when={true}>
+                      <Show when={local.model.variant.list().length > 0}>
+                        <text fg={theme.text}>
+                          {keybind.print("variant_cycle")} <span style={{ fg: theme.textMuted }}>variants</span>
+                        </text>
+                      </Show>
+                      <text fg={theme.text}>
+                        {keybind.print("agent_cycle")} <span style={{ fg: theme.textMuted }}>agents</span>
+                      </text>
+                    </Match>
+                  </Switch>
                   <text fg={theme.text}>
                     {keybind.print("command_list")} <span style={{ fg: theme.textMuted }}>commands</span>
                   </text>
diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/header.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/header.tsx
deleted file mode 100644
index f64dbe533a7..00000000000
--- a/packages/opencode/src/cli/cmd/tui/routes/session/header.tsx
+++ /dev/null
@@ -1,172 +0,0 @@
-import { type Accessor, createMemo, createSignal, Match, Show, Switch } from "solid-js"
-import { useRouteData } from "@tui/context/route"
-import { useSync } from "@tui/context/sync"
-import { pipe, sumBy } from "remeda"
-import { useTheme } from "@tui/context/theme"
-import { SplitBorder } from "@tui/component/border"
-import type { AssistantMessage, Session } from "@opencode-ai/sdk/v2"
-import { useCommandDialog } from "@tui/component/dialog-command"
-import { useKeybind } from "../../context/keybind"
-import { Flag } from "@/flag/flag"
-import { useTerminalDimensions } from "@opentui/solid"
-
-const Title = (props: { session: Accessor<Session> }) => {
-  const { theme } = useTheme()
-  return (
-    <text fg={theme.text}>
-      <span style={{ bold: true }}>#</span> <span style={{ bold: true }}>{props.session().title}</span>
-    </text>
-  )
-}
-
-const ContextInfo = (props: { context: Accessor<string | undefined>; cost: Accessor<string> }) => {
-  const { theme } = useTheme()
-  return (
-    <Show when={props.context()}>
-      <text fg={theme.textMuted} wrapMode="none" flexShrink={0}>
-        {props.context()} ({props.cost()})
-      </text>
-    </Show>
-  )
-}
-
-const WorkspaceInfo = (props: { workspace: Accessor<string | undefined> }) => {
-  const { theme } = useTheme()
-  return (
-    <Show when={props.workspace()}>
-      <text fg={theme.textMuted} wrapMode="none" flexShrink={0}>
-        {props.workspace()}
-      </text>
-    </Show>
-  )
-}
-
-export function Header() {
-  const route = useRouteData("session")
-  const sync = useSync()
-  const session = createMemo(() => sync.session.get(route.sessionID)!)
-  const messages = createMemo(() => sync.data.message[route.sessionID] ?? [])
-
-  const cost = createMemo(() => {
-    const total = pipe(
-      messages(),
-      sumBy((x) => (x.role === "assistant" ? x.cost : 0)),
-    )
-    return new Intl.NumberFormat("en-US", {
-      style: "currency",
-      currency: "USD",
-    }).format(total)
-  })
-
-  const context = createMemo(() => {
-    const last = messages().findLast((x) => x.role === "assistant" && x.tokens.output > 0) as AssistantMessage
-    if (!last) return
-    const total =
-      last.tokens.input + last.tokens.output + last.tokens.reasoning + last.tokens.cache.read + last.tokens.cache.write
-    const model = sync.data.provider.find((x) => x.id === last.providerID)?.models[last.modelID]
-    let result = total.toLocaleString()
-    if (model?.limit.context) {
-      result += "  " + Math.round((total / model.limit.context) * 100) + "%"
-    }
-    return result
-  })
-
-  const workspace = createMemo(() => {
-    const id = session()?.workspaceID
-    if (!id) return "Workspace local"
-    const info = sync.workspace.get(id)
-    if (!info) return `Workspace ${id}`
-    return `Workspace ${id} (${info.type})`
-  })
-
-  const { theme } = useTheme()
-  const keybind = useKeybind()
-  const command = useCommandDialog()
-  const [hover, setHover] = createSignal<"parent" | "prev" | "next" | null>(null)
-  const dimensions = useTerminalDimensions()
-  const narrow = createMemo(() => dimensions().width < 80)
-
-  return (
-    <box flexShrink={0}>
-      <box
-        paddingTop={1}
-        paddingBottom={1}
-        paddingLeft={2}
-        paddingRight={1}
-        {...SplitBorder}
-        border={["left"]}
-        borderColor={theme.border}
-        flexShrink={0}
-        backgroundColor={theme.backgroundPanel}
-      >
-        <Switch>
-          <Match when={session()?.parentID}>
-            <box flexDirection="column" gap={1}>
-              <box flexDirection={narrow() ? "column" : "row"} justifyContent="space-between" gap={narrow() ? 1 : 0}>
-                {Flag.OPENCODE_EXPERIMENTAL_WORKSPACES ? (
-                  <box flexDirection="column">
-                    <text fg={theme.text}>
-                      <b>Subagent session</b>
-                    </text>
-                    <WorkspaceInfo workspace={workspace} />
-                  </box>
-                ) : (
-                  <text fg={theme.text}>
-                    <b>Subagent session</b>
-                  </text>
-                )}
-
-                <ContextInfo context={context} cost={cost} />
-              </box>
-              <box flexDirection="row" gap={2}>
-                <box
-                  onMouseOver={() => setHover("parent")}
-                  onMouseOut={() => setHover(null)}
-                  onMouseUp={() => command.trigger("session.parent")}
-                  backgroundColor={hover() === "parent" ? theme.backgroundElement : theme.backgroundPanel}
-                >
-                  <text fg={theme.text}>
-                    Parent <span style={{ fg: theme.textMuted }}>{keybind.print("session_parent")}</span>
-                  </text>
-                </box>
-                <box
-                  onMouseOver={() => setHover("prev")}
-                  onMouseOut={() => setHover(null)}
-                  onMouseUp={() => command.trigger("session.child.previous")}
-                  backgroundColor={hover() === "prev" ? theme.backgroundElement : theme.backgroundPanel}
-                >
-                  <text fg={theme.text}>
-                    Prev <span style={{ fg: theme.textMuted }}>{keybind.print("session_child_cycle_reverse")}</span>
-                  </text>
-                </box>
-                <box
-                  onMouseOver={() => setHover("next")}
-                  onMouseOut={() => setHover(null)}
-                  onMouseUp={() => command.trigger("session.child.next")}
-                  backgroundColor={hover() === "next" ? theme.backgroundElement : theme.backgroundPanel}
-                >
-                  <text fg={theme.text}>
-                    Next <span style={{ fg: theme.textMuted }}>{keybind.print("session_child_cycle")}</span>
-                  </text>
-                </box>
-              </box>
-            </box>
-          </Match>
-          <Match when={true}>
-            <box flexDirection={narrow() ? "column" : "row"} justifyContent="space-between" gap={1}>
-              {Flag.OPENCODE_EXPERIMENTAL_WORKSPACES ? (
-                <box flexDirection="column">
-                  <Title session={session} />
-                  <WorkspaceInfo workspace={workspace} />
-                </box>
-              ) : (
-                <Title session={session} />
-              )}
-              <ContextInfo context={context} cost={cost} />
-            </box>
-          </Match>
-        </Switch>
-      </box>
-    </box>
-  )
-}
diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
index 080065fd787..1baa2e9973f 100644
--- a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
+++ b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
@@ -51,7 +51,6 @@ import { useSDK } from "@tui/context/sdk"
 import { useCommandDialog } from "@tui/component/dialog-command"
 import type { DialogContext } from "@tui/ui/dialog"
 import { useKeybind } from "@tui/context/keybind"
-import { Header } from "./header"
 import { parsePatch } from "diff"
 import { useDialog } from "../../ui/dialog"
 import { TodoItem } from "../../component/todo-item"
@@ -154,7 +153,6 @@ export function Session() {
   const [showDetails, setShowDetails] = kv.signal("tool_details_visibility", true)
   const [showAssistantMetadata, setShowAssistantMetadata] = kv.signal("assistant_metadata_visibility", true)
   const [showScrollbar, setShowScrollbar] = kv.signal("scrollbar_visible", true)
-  const [showHeader, setShowHeader] = kv.signal("header_visible", true)
   const [diffWrapMode] = kv.signal<"word" | "none">("diff_wrap_mode", "word")
   const [animationsEnabled, setAnimationsEnabled] = kv.signal("animations_enabled", true)
   const [showGenericToolOutput, setShowGenericToolOutput] = kv.signal("generic_tool_output_visibility", false)
@@ -635,15 +633,6 @@ export function Session() {
         dialog.clear()
       },
     },
-    {
-      title: showHeader() ? "Hide header" : "Show header",
-      value: "session.toggle.header",
-      category: "Session",
-      onSelect: (dialog) => {
-        setShowHeader((prev) => !prev)
-        dialog.clear()
-      },
-    },
     {
       title: showGenericToolOutput() ? "Hide generic tool output" : "Show generic tool output",
       value: "session.toggle.generic_tool_output",
@@ -1045,11 +1034,8 @@ export function Session() {
       }}
     >
       <box flexDirection="row">
-        <box flexGrow={1} paddingBottom={1} paddingTop={1} paddingLeft={2} paddingRight={2} gap={1}>
+        <box flexGrow={1} paddingBottom={1} paddingLeft={2} paddingRight={2} gap={1}>
           <Show when={session()}>
-            <Show when={showHeader() && (!sidebarVisible() || !wide())}>
-              <Header />
-            </Show>
             <scrollbox
               ref={(r) => (scroll = r)}
               viewportOptions={{
@@ -1068,6 +1054,7 @@ export function Session() {
               flexGrow={1}
               scrollAcceleration={scrollAcceleration()}
             >
+              <box height={1} />
               <For each={messages()}>
                 {(message, index) => (
                   <Switch>

PATCH

echo "Patch applied successfully."
