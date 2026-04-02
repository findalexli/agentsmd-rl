#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if the fix is already applied
if [ -f "packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx" ]; then
  echo "Fix already applied (subagent-footer.tsx exists)"
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx b/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx
index a06e7e07054..ee9fa225ed0 100644
--- a/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx
+++ b/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx
@@ -138,9 +138,9 @@ export function DialogModel(props: { providerID?: string }) {
     local.model.set({ providerID, modelID }, { recent: true })
     if (local.model.variant.list().length > 0) {
       dialog.replace(() => <DialogVariant />)
-    } else {
-      dialog.clear()
+      return
     }
+    dialog.clear()
   }

   return (
diff --git a/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx b/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx
index 8d06ab64116..fd895e0cf6f 100644
--- a/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx
+++ b/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx
@@ -1,6 +1,5 @@
 import { createMemo } from "solid-js"
 import { useLocal } from "@tui/context/local"
-import { useSync } from "@tui/context/sync"
 import { DialogSelect } from "@tui/ui/dialog-select"
 import { useDialog } from "@tui/ui/dialog"

diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
index 1baa2e9973f..2f84f9d7bf6 100644
--- a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
+++ b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
@@ -61,6 +61,7 @@ import { DialogTimeline } from "./dialog-timeline"
 import { DialogForkFromTimeline } from "./dialog-fork-from-timeline"
 import { DialogSessionRename } from "../../component/dialog-session-rename"
 import { Sidebar } from "./sidebar"
+import { SubagentFooter } from "./subagent-footer.tsx"
 import { Flag } from "@/flag/flag"
 import { LANGUAGE_EXTENSIONS } from "@/lsp/language"
 import parsers from "../../../../../../parsers-config.ts"
@@ -1054,7 +1055,6 @@ export function Session() {
               flexGrow={1}
               scrollAcceleration={scrollAcceleration()}
             >
-              <box height={1} />
               <For each={messages()}>
                 {(message, index) => (
                   <Switch>
@@ -1158,6 +1158,9 @@ export function Session() {
               <Show when={permissions().length === 0 && questions().length > 0}>
                 <QuestionPrompt request={questions()[0]} />
               </Show>
+              <Show when={session()?.parentID}>
+                <SubagentFooter />
+              </Show>
               <Prompt
                 visible={!session()?.parentID && permissions().length === 0 && questions().length === 0}
                 ref={(r) => {
diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx
new file mode 100644
index 00000000000..315cd1e88cd
--- /dev/null
+++ b/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx
@@ -0,0 +1,109 @@
+import { createMemo, createSignal, Show } from "solid-js"
+import { useRouteData } from "@tui/context/route"
+import { useSync } from "@tui/context/sync"
+import { useTheme } from "@tui/context/theme"
+import { SplitBorder } from "@tui/component/border"
+import type { AssistantMessage } from "@opencode-ai/sdk/v2"
+import { useCommandDialog } from "@tui/component/dialog-command"
+import { useKeybind } from "../../context/keybind"
+import { Locale } from "@/util/locale"
+import { useTerminalDimensions } from "@opentui/solid"
+
+export function SubagentFooter() {
+  const route = useRouteData("session")
+  const sync = useSync()
+  const messages = createMemo(() => sync.data.message[route.sessionID] ?? [])
+
+  const usage = createMemo(() => {
+    const msg = messages()
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
+
+    const money = new Intl.NumberFormat("en-US", {
+      style: "currency",
+      currency: "USD",
+    })
+
+    return {
+      context: pct ? `${Locale.number(tokens)} (${pct})` : Locale.number(tokens),
+      cost: cost > 0 ? money.format(cost) : undefined,
+    }
+  })
+
+  const { theme } = useTheme()
+  const keybind = useKeybind()
+  const command = useCommandDialog()
+  const [hover, setHover] = createSignal<"parent" | "prev" | "next" | null>(null)
+  const dimensions = useTerminalDimensions()
+
+  return (
+    <box flexShrink={0}>
+      <box
+        paddingTop={1}
+        paddingBottom={1}
+        paddingLeft={2}
+        paddingRight={1}
+        {...SplitBorder}
+        border={["left"]}
+        borderColor={theme.border}
+        flexShrink={0}
+        backgroundColor={theme.backgroundPanel}
+      >
+        <box flexDirection="row" justifyContent="space-between" gap={1}>
+          <box flexDirection="row" gap={2}>
+            <text fg={theme.text}>
+              <b>Subagent session</b>
+            </text>
+            <Show when={usage()}>
+              {(item) => (
+                <text fg={theme.textMuted} wrapMode="none">
+                  {[item().context, item().cost].filter(Boolean).join(" · ")}
+                </text>
+              )}
+            </Show>
+          </box>
+          <box flexDirection="row" gap={2}>
+            <box
+              onMouseOver={() => setHover("parent")}
+              onMouseOut={() => setHover(null)}
+              onMouseUp={() => command.trigger("session.parent")}
+              backgroundColor={hover() === "parent" ? theme.backgroundElement : theme.backgroundPanel}
+            >
+              <text fg={theme.text}>
+                Parent <span style={{ fg: theme.textMuted }}>{keybind.print("session_parent")}</span>
+              </text>
+            </box>
+            <box
+              onMouseOver={() => setHover("prev")}
+              onMouseOut={() => setHover(null)}
+              onMouseUp={() => command.trigger("session.child.previous")}
+              backgroundColor={hover() === "prev" ? theme.backgroundElement : theme.backgroundPanel}
+            >
+              <text fg={theme.text}>
+                Prev <span style={{ fg: theme.textMuted }}>{keybind.print("session_child_cycle_reverse")}</span>
+              </text>
+            </box>
+            <box
+              onMouseOver={() => setHover("next")}
+              onMouseOut={() => setHover(null)}
+              onMouseUp={() => command.trigger("session.child.next")}
+              backgroundColor={hover() === "next" ? theme.backgroundElement : theme.backgroundPanel}
+            >
+              <text fg={theme.text}>
+                Next <span style={{ fg: theme.textMuted }}>{keybind.print("session_child_cycle")}</span>
+              </text>
+            </box>
+          </box>
+        </box>
+      </box>
+    </box>
+  )
+}

PATCH

echo "Fix applied successfully"
