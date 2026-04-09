#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for the new Naming Enforcement section)
if grep -q 'Naming Enforcement (Read This)' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full gold patch (code changes + AGENTS.md update)
git apply - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index 758714d10aaa..2158d73af1b4 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -20,6 +20,17 @@

 Prefer single word names for variables and functions. Only use multiple words if necessary.

+### Naming Enforcement (Read This)
+
+THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE.
+
+- Use single word names by default for new locals, params, and helper functions.
+- Multi-word names are allowed only when a single word would be unclear or ambiguous.
+- Do not introduce new camelCase compounds when a short single-word alternative is clear.
+- Before finishing edits, review touched lines and shorten newly introduced identifiers where possible.
+- Good short names to prefer: `pid`, `cfg`, `err`, `opts`, `dir`, `root`, `child`, `state`, `timeout`.
+- Examples to avoid unless truly required: `inputPID`, `existingClient`, `connectTimeout`, `workerPath`.
+
 ```ts
 // Good
 const foo = 1
diff --git a/packages/opencode/src/cli/cmd/tui/thread.ts b/packages/opencode/src/cli/cmd/tui/thread.ts
index 750347d9d636..f53cc3925523 100644
--- a/packages/opencode/src/cli/cmd/tui/thread.ts
+++ b/packages/opencode/src/cli/cmd/tui/thread.ts
@@ -5,8 +5,8 @@ import { type rpc } from "./worker"
 import path from "path"
 import { fileURLToPath } from "url"
 import { UI } from "@/cli/ui"
-import { iife } from "@/util/iife"
 import { Log } from "@/util/log"
+import { withTimeout } from "@/util/timeout"
 import { withNetworkOptions, resolveNetworkOptions } from "@/cli/network"
 import { Filesystem } from "@/util/filesystem"
 import type { Event } from "@opencode-ai/sdk/v2"
@@ -45,6 +45,20 @@ function createEventSource(client: RpcClient): EventSource {
   }
 }

+async function target() {
+  if (typeof OPENCODE_WORKER_PATH !== "undefined") return OPENCODE_WORKER_PATH
+  const dist = new URL("./cli/cmd/tui/worker.js", import.meta.url)
+  if (await Filesystem.exists(fileURLToPath(dist))) return dist
+  return new URL("./worker.ts", import.meta.url)
+}
+
+async function input(value?: string) {
+  const piped = process.stdin.isTTY ? undefined : await Bun.stdin.text()
+  if (!value) return piped
+  if (!piped) return value
+  return piped + "\n" + value
+}
+
 export const TuiThreadCommand = cmd({
   command: "$0 [project]",
   describe: "start opencode tui",
@@ -97,23 +111,17 @@ export const TuiThreadCommand = cmd({
       }

       // Resolve relative paths against PWD to preserve behavior when using --cwd flag
-      const baseCwd = process.env.PWD ?? process.cwd()
-      const cwd = args.project ? path.resolve(baseCwd, args.project) : process.cwd()
-      const localWorker = new URL("./worker.ts", import.meta.url)
-      const distWorker = new URL("./cli/cmd/tui/worker.js", import.meta.url)
-      const workerPath = await iife(async () => {
-        if (typeof OPENCODE_WORKER_PATH !== "undefined") return OPENCODE_WORKER_PATH
-        if (await Filesystem.exists(fileURLToPath(distWorker))) return distWorker
-        return localWorker
-      })
+      const root = process.env.PWD ?? process.cwd()
+      const cwd = args.project ? path.resolve(root, args.project) : process.cwd()
+      const file = await target()
       try {
         process.chdir(cwd)
-      } catch (e) {
+      } catch {
         UI.error("Failed to change directory to " + cwd)
         return
       }

-      const worker = new Worker(workerPath, {
+      const worker = new Worker(file, {
         env: Object.fromEntries(
           Object.entries(process.env).filter((entry): entry is [string, string] => entry[1] !== undefined),
         ),
@@ -121,76 +129,88 @@ export const TuiThreadCommand = cmd({
       worker.onerror = (e) => {
         Log.Default.error(e)
       }
+
       const client = Rpc.client<typeof rpc>(worker)
-      process.on("uncaughtException", (e) => {
-        Log.Default.error(e)
-      })
-      process.on("unhandledRejection", (e) => {
+      const error = (e: unknown) => {
         Log.Default.error(e)
-      })
-      process.on("SIGUSR2", async () => {
-        await client.call("reload", undefined)
-      })
+      }
+      const reload = () => {
+        client.call("reload", undefined).catch((err) => {
+          Log.Default.warn("worker reload failed", {
+            error: err instanceof Error ? err.message : String(err),
+          })
+        })
+      }
+      process.on("uncaughtException", error)
+      process.on("unhandledRejection", error)
+      process.on("SIGUSR2", reload)

-      const prompt = await iife(async () => {
-        const piped = !process.stdin.isTTY ? await Bun.stdin.text() : undefined
-        if (!args.prompt) return piped
-        return piped ? piped + "\n" + args.prompt : args.prompt
-      })
+      let stopped = false
+      const stop = async () => {
+        if (stopped) return
+        stopped = true
+        process.off("uncaughtException", error)
+        process.off("unhandledRejection", error)
+        process.off("SIGUSR2", reload)
+        await withTimeout(client.call("shutdown", undefined), 5000).catch((error) => {
+          Log.Default.warn("worker shutdown failed", {
+            error: error instanceof Error ? error.message : String(error),
+          })
+        })
+        worker.terminate()
+      }
+
+      const prompt = await input(args.prompt)
       const config = await Instance.provide({
         directory: cwd,
         fn: () => TuiConfig.get(),
       })

-      // Check if server should be started (port or hostname explicitly set in CLI or config)
-      const networkOpts = await resolveNetworkOptions(args)
-      const shouldStartServer =
+      const network = await resolveNetworkOptions(args)
+      const external =
         process.argv.includes("--port") ||
         process.argv.includes("--hostname") ||
         process.argv.includes("--mdns") ||
-        networkOpts.mdns ||
-        networkOpts.port !== 0 ||
-        networkOpts.hostname !== "127.0.0.1"
-
-      let url: string
-      let customFetch: typeof fetch | undefined
-      let events: EventSource | undefined
-
-      if (shouldStartServer) {
-        // Start HTTP server for external access
-        const server = await client.call("server", networkOpts)
-        url = server.url
-      } else {
-        // Use direct RPC communication (no HTTP)
-        url = "http://opencode.internal"
-        customFetch = createWorkerFetch(client)
-        events = createEventSource(client)
-      }
+        network.mdns ||
+        network.port !== 0 ||
+        network.hostname !== "127.0.0.1"

-      const tuiPromise = tui({
-        url,
-        config,
-        directory: cwd,
-        fetch: customFetch,
-        events,
-        args: {
-          continue: args.contue,
-          sessionID: args.session,
-          agent: args.agent,
-          model: args.model,
-          prompt,
-          fork: args.fork,
-        },
-        onExit: async () => {
-          await client.call("shutdown", undefined)
-        },
-      })
+      const transport = external
+        ? {
+            url: (await client.call("server", network)).url,
+            fetch: undefined,
+            events: undefined,
+          }
+        : {
+            url: "http://opencode.internal",
+            fetch: createWorkerFetch(client),
+            events: createEventSource(client),
+          }

       setTimeout(() => {
         client.call("checkUpgrade", { directory: cwd }).catch(() => {})
-      }, 1000)
+      }, 1000).unref?.()

-      await tuiPromise
+      try {
+        await tui({
+          url: transport.url,
+          config,
+          directory: cwd,
+          fetch: transport.fetch,
+          events: transport.events,
+          args: {
+            continue: args.continue,
+            sessionID: args.session,
+            agent: args.agent,
+            model: args.model,
+            prompt,
+            fork: args.fork,
+          },
+          onExit: stop,
+        })
+      } finally {
+        await stop()
+      }
     } finally {
       unguard?.()
     }
diff --git a/packages/opencode/src/cli/cmd/tui/worker.ts b/packages/opencode/src/cli/cmd/tui/worker.ts
index bb5495c48110..e63f10ba80c9 100644
--- a/packages/opencode/src/cli/cmd/tui/worker.ts
+++ b/packages/opencode/src/cli/cmd/tui/worker.ts
@@ -137,12 +137,7 @@ export const rpc = {
   async shutdown() {
     Log.Default.info("worker shutting down")
     if (eventStream.abort) eventStream.abort.abort()
-    await Promise.race([
-      Instance.disposeAll(),
-      new Promise((resolve) => {
-        setTimeout(resolve, 5000)
-      }),
-    ])
+    await Instance.disposeAll()
     if (server) server.stop(true)
   },
 }
PATCH

echo "Patch applied successfully."
