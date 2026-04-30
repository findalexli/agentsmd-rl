#!/usr/bin/env bash
set -euo pipefail

WORKER="packages/opencode/src/cli/cmd/tui/worker.ts"

# Idempotency: check if fix already applied
if grep -q 'Bus.subscribeAll' "$WORKER" 2>/dev/null; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/cli/cmd/tui/worker.ts b/packages/opencode/src/cli/cmd/tui/worker.ts
index 06cb179e93a..3d8c00cc520 100644
--- a/packages/opencode/src/cli/cmd/tui/worker.ts
+++ b/packages/opencode/src/cli/cmd/tui/worker.ts
@@ -6,11 +6,14 @@ import { InstanceBootstrap } from "@/project/bootstrap"
 import { Rpc } from "@/util/rpc"
 import { upgrade } from "@/cli/upgrade"
 import { Config } from "@/config/config"
+import { Bus } from "@/bus"
 import { GlobalBus } from "@/bus/global"
-import { createOpencodeClient, type Event } from "@opencode-ai/sdk/v2"
+import type { Event } from "@opencode-ai/sdk/v2"
 import { Flag } from "@/flag/flag"
 import { setTimeout as sleep } from "node:timers/promises"
 import { writeHeapSnapshot } from "node:v8"
+import { WorkspaceContext } from "@/control-plane/workspace-context"
+import { WorkspaceID } from "@/control-plane/schema"

 await Log.init({
   print: process.argv.includes("--print-logs"),
@@ -50,39 +53,55 @@ const startEventStream = (input: { directory: string; workspaceID?: string }) =>
   eventStream.abort = abort
   const signal = abort.signal

-  const fetchFn = (async (input: RequestInfo | URL, init?: RequestInit) => {
-    const request = new Request(input, init)
-    const auth = getAuthorizationHeader()
-    if (auth) request.headers.set("Authorization", auth)
-    return Server.Default().fetch(request)
-  }) as typeof globalThis.fetch
-
-  const sdk = createOpencodeClient({
-    baseUrl: "http://opencode.internal",
-    directory: input.directory,
-    experimental_workspaceID: input.workspaceID,
-    fetch: fetchFn,
-    signal,
-  })
+  const workspaceID = input.workspaceID ? WorkspaceID.make(input.workspaceID) : undefined

   ;(async () => {
     while (!signal.aborted) {
-      const events = await Promise.resolve(
-        sdk.event.subscribe(
-          {},
-          {
-            signal,
-          },
-        ),
-      ).catch(() => undefined)
-
-      if (!events) {
-        await sleep(250)
-        continue
-      }
-
-      for await (const event of events.stream) {
-        Rpc.emit("event", event as Event)
+      const shouldReconnect = await WorkspaceContext.provide({
+        workspaceID,
+        fn: () =>
+          Instance.provide({
+            directory: input.directory,
+            init: InstanceBootstrap,
+            fn: () =>
+              new Promise<boolean>((resolve) => {
+                Rpc.emit("event", {
+                  type: "server.connected",
+                  properties: {},
+                } satisfies Event)
+
+                let settled = false
+                const settle = (value: boolean) => {
+                  if (settled) return
+                  settled = true
+                  signal.removeEventListener("abort", onAbort)
+                  unsub()
+                  resolve(value)
+                }
+
+                const unsub = Bus.subscribeAll((event) => {
+                  Rpc.emit("event", event as Event)
+                  if (event.type === Bus.InstanceDisposed.type) {
+                    settle(true)
+                  }
+                })
+
+                const onAbort = () => {
+                  settle(false)
+                }
+
+                signal.addEventListener("abort", onAbort, { once: true })
+              }),
+          }),
+      }).catch((error) => {
+        Log.Default.error("event stream subscribe error", {
+          error: error instanceof Error ? error.message : error,
+        })
+        return false
+      })
+
+      if (!shouldReconnect || signal.aborted) {
+        break
       }

       if (!signal.aborted) {

PATCH

echo "Applied: bypass SSE event streaming in TUI worker"
