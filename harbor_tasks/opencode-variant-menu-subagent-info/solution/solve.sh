#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/workspace/opencode"
cd "$REPO_DIR"

# Idempotency check: if direction is already fixed, patch is applied
if grep -q '\- direction$' packages/opencode/src/cli/cmd/tui/routes/session/index.tsx 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
--- a/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
+++ b/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx
@@ -334,7 +334,7 @@ export function Session() {
     if (children().length === 1) return

     const sessions = children().filter((x) => !!x.parentID)
-    let next = sessions.findIndex((x) => x.id === session()?.id) + direction
+    let next = sessions.findIndex((x) => x.id === session()?.id) - direction

     if (next >= sessions.length) next = 0
     if (next < 0) next = sessions.length - 1
@@ -1228,7 +1228,6 @@ function UserMessage(props: {
   const local = useLocal()
   const text = createMemo(() => props.parts.flatMap((x) => (x.type === "text" && !x.synthetic ? [x] : []))[0])
   const files = createMemo(() => props.parts.flatMap((x) => (x.type === "file" ? [x] : [])))
-  const sync = useSync()
   const { theme } = useTheme()
   const [hover, setHover] = createSignal(false)
   const queued = createMemo(() => props.pending && props.message.id > props.pending)
@@ -1614,17 +1613,6 @@ function GenericTool(props: ToolProps<any>) {
   )
 }

-function ToolTitle(props: { fallback: string; when: any; icon: string; children: JSX.Element }) {
-  const { theme } = useTheme()
-  return (
-    <text paddingLeft={3} fg={props.when ? theme.textMuted : theme.text}>
-      <Show fallback={<>~ {props.fallback}</>} when={props.when}>
-        <span style={{ bold: true }}>{props.icon}</span> {props.children}
-      </Show>
-    </text>
-  )
-}
-
 function InlineTool(props: {
   icon: string
   iconColor?: RGBA
@@ -1962,10 +1950,7 @@ function WebSearch(props: ToolProps<any>) {
 }

 function Task(props: ToolProps<typeof TaskTool>) {
-  const { theme } = useTheme()
-  const keybind = useKeybind()
   const { navigate } = useRoute()
-  const local = useLocal()
   const sync = useSync()

   onMount(() => {
@@ -1996,7 +1981,7 @@ function Task(props: ToolProps<typeof TaskTool>) {

   const content = createMemo(() => {
     if (!props.input.description) return ""
-    let content = [`Task ${props.input.description}`]
+    let content = [`${Locale.titlecase(props.input.subagent_type ?? "General")} Task — ${props.input.description}`]

     if (isRunning() && tools().length > 0) {
       // content[0] += ` · ${tools().length} toolcalls`
diff --git a/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx b/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx
--- a/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx
+++ b/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx
@@ -13,6 +13,23 @@ export function SubagentFooter() {
   const route = useRouteData("session")
   const sync = useSync()
   const messages = createMemo(() => sync.data.message[route.sessionID] ?? [])
+  const session = createMemo(() => sync.session.get(route.sessionID))
+
+  const subagentInfo = createMemo(() => {
+    const s = session()
+    if (!s) return { label: "Subagent", index: 0, total: 0 }
+    const agentMatch = s.title.match(/@(\w+) subagent/)
+    const label = agentMatch ? Locale.titlecase(agentMatch[1]) : "Subagent"
+
+    if (!s.parentID) return { label, index: 0, total: 0 }
+
+    const siblings = sync.data.session
+      .filter((x) => x.parentID === s.parentID)
+      .toSorted((a, b) => a.time.created - b.time.created)
+    const index = siblings.findIndex((x) => x.id === s.id)
+
+    return { label, index: index + 1, total: siblings.length }
+  })

   const usage = createMemo(() => {
     const msg = messages()
@@ -58,10 +75,15 @@ export function SubagentFooter() {
         backgroundColor={theme.backgroundPanel}
       >
         <box flexDirection="row" justifyContent="space-between" gap={1}>
-          <box flexDirection="row" gap={2}>
+          <box flexDirection="row" gap={1}>
             <text fg={theme.text}>
-              <b>Subagent session</b>
+              <b>{subagentInfo().label}</b>
             </text>
+            <Show when={subagentInfo().total > 0}>
+              <text style={{ fg: theme.textMuted }}>
+                ({subagentInfo().index} of {subagentInfo().total})
+              </text>
+            </Show>
             <Show when={usage()}>
               {(item) => (
                 <text fg={theme.textMuted} wrapMode="none">

PATCH

echo "Patch applied successfully."
