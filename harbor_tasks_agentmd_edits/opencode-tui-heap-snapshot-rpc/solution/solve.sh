#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for onSnapshot prop in app.tsx)
if grep -q 'onSnapshot' packages/opencode/src/cli/cmd/tui/app.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch with both code and config changes
git apply - <<'PATCH'
diff --git a/.opencode/command/changelog.md b/.opencode/command/changelog.md
index a8a57d1bf0d..7e066a20e82e 100644
--- a/.opencode/command/changelog.md
+++ b/.opencode/command/changelog.md
@@ -1,5 +1,17 @@
-go through each PR merged since the last tag
+create UPCOMING_CHANGELOG.md

-for each PR spawn a subagent to summarize what the PR was about. focus on user facing changes. if it was entirely internal or code related you can ignore it. also skip docs updates. each subagent should append its summary to UPCOMING_CHANGELOG.md
+it should have sections

-once that is done, read UPCOMING_CHANGELOG.md and group it into sections for better readability. make sure all PR references are preserved
+```
+# TUI
+
+# Desktop
+
+# Core
+
+# Misc
+```
+
+go through each PR merged since the last tag

+for each PR spawn a subagent to summarize what the PR was about. focus on user facing changes. if it was entirely internal or code related you can ignore it. also skip docs updates. each subagent should append its summary to UPCOMING_CHANGELOG.md into the appropriate section.

-once that is done, read UPCOMING_CHANGELOG.md and group it into sections for better readability. make sure all PR references are preserved
+once that is done, read UPCOMING_CHANGELOG.md and group it into sections for better readability. make sure all PR references are preserved
diff --git a/packages/opencode/src/cli/cmd/tui/app.tsx b/packages/opencode/src/cli/cmd/tui/app.tsx
index 549c7c34a7e0..8aabafd08020 100644
--- a/packages/opencode/src/cli/cmd/tui/app.tsx
+++ b/packages/opencode/src/cli/cmd/tui/app.tsx
@@ -110,6 +110,7 @@ export function tui(input: {
   url: string
   args: Args
   config: TuiConfig.Info
+  onSnapshot?: () => Promise<string[]>
   directory?: string
   fetch?: typeof fetch
   headers?: RequestInit["headers"]
@@ -160,7 +161,7 @@ export function tui(input: {
                                         <FrecencyProvider>
                                           <PromptHistoryProvider>
                                             <PromptRefProvider>
-                                              <App />
+                                              <App onSnapshot={input.onSnapshot} />
                                             </PromptRefProvider>
                                           </PromptHistoryProvider>
                                         </FrecencyProvider>
@@ -201,7 +202,7 @@ export function tui(input: {
   })
 }

-function App() {
+function App(props: { onSnapshot?: () => Promise<string[]> }) {
   const route = useRoute()
   const dimensions = useTerminalDimensions()
   const renderer = useRenderer()
@@ -627,11 +628,11 @@ function App() {
       title: "Write heap snapshot",
       category: "System",
       value: "app.heap_snapshot",
-      onSelect: (dialog) => {
-        const path = writeHeapSnapshot()
+      onSelect: async (dialog) => {
+        const files = await props.onSnapshot?.()
         toast.show({
           variant: "info",
-          message: `Heap snapshot written to ${path}`,
+          message: `Heap snapshot written to ${files?.join(", ")}`,
           duration: 5000,
         })
         dialog.clear()
diff --git a/packages/opencode/src/cli/cmd/tui/thread.ts b/packages/opencode/src/cli/cmd/tui/thread.ts
index 6e787c7afddd..d984dc6f3f01 100644
--- a/packages/opencode/src/cli/cmd/tui/thread.ts
+++ b/packages/opencode/src/cli/cmd/tui/thread.ts
@@ -14,6 +14,7 @@ import type { EventSource } from "./context/sdk"
 import { win32DisableProcessedInput, win32InstallCtrlCGuard } from "./win32"
 import { TuiConfig } from "@/config/tui"
 import { Instance } from "@/project/instance"
+import { writeHeapSnapshot } from "v8"

 declare global {
   const OPENCODE_WORKER_PATH: string
@@ -201,6 +202,11 @@ export const TuiThreadCommand = cmd({
       try {
         await tui({
           url: transport.url,
+          async onSnapshot() {
+            const tui = writeHeapSnapshot("tui.heapsnapshot")
+            const server = await client.call("snapshot", undefined)
+            return [tui, server]
+          },
           config,
           directory: cwd,
           fetch: transport.fetch,
diff --git a/packages/opencode/src/cli/cmd/tui/worker.ts b/packages/opencode/src/cli/cmd/tui/worker.ts
index 511182fe85df..06cb179e93af 100644
--- a/packages/opencode/src/cli/cmd/tui/worker.ts
+++ b/packages/opencode/src/cli/cmd/tui/worker.ts
@@ -10,6 +10,7 @@ import { GlobalBus } from "@/bus/global"
 import { createOpencodeClient, type Event } from "@opencode-ai/sdk/v2"
 import { Flag } from "@/flag/flag"
 import { setTimeout as sleep } from "node:timers/promises"
+import { writeHeapSnapshot } from "node:v8"

 await Log.init({
   print: process.argv.includes("--print-logs"),
@@ -117,6 +118,10 @@ export const rpc = {
       body,
     }
   },
+  snapshot() {
+    const result = writeHeapSnapshot("server.heapsnapshot")
+    return result
+  },
   async server(input: { port: number; hostname: string; mdns?: boolean; cors?: string[] }) {
     if (server) await server.stop(true)
     server = await Server.listen(input)

PATCH

echo "Patch applied successfully."
