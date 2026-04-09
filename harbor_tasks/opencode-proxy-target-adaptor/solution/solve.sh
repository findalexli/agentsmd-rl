#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'type Target =' packages/opencode/src/control-plane/types.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/control-plane/adaptors/worktree.ts b/packages/opencode/src/control-plane/adaptors/worktree.ts
index 719748e3a193..9fb6c7479365 100644
--- a/packages/opencode/src/control-plane/adaptors/worktree.ts
+++ b/packages/opencode/src/control-plane/adaptors/worktree.ts
@@ -32,7 +32,11 @@ export const WorktreeAdaptor: Adaptor = {
     const config = Config.parse(info)
     await Worktree.remove({ directory: config.directory })
   },
-  async fetch(_info, _input: RequestInfo | URL, _init?: RequestInit) {
-    throw new Error("fetch not implemented")
+  target(info) {
+    const config = Config.parse(info)
+    return {
+      type: "local",
+      directory: config.directory,
+    }
   },
 }
diff --git a/packages/opencode/src/control-plane/types.ts b/packages/opencode/src/control-plane/types.ts
index ab628a693814..dd17c56d93db 100644
--- a/packages/opencode/src/control-plane/types.ts
+++ b/packages/opencode/src/control-plane/types.ts
@@ -13,9 +13,20 @@ export const WorkspaceInfo = z.object({
 })
 export type WorkspaceInfo = z.infer<typeof WorkspaceInfo>

+export type Target =
+  | {
+      type: "local"
+      directory: string
+    }
+  | {
+      type: "remote"
+      url: string | URL
+      headers?: HeadersInit
+    }
+
 export type Adaptor = {
   configure(input: WorkspaceInfo): WorkspaceInfo | Promise<WorkspaceInfo>
-  create(input: WorkspaceInfo, from?: WorkspaceInfo): Promise<void>
+  create(config: WorkspaceInfo, from?: WorkspaceInfo): Promise<void>
   remove(config: WorkspaceInfo): Promise<void>
-  fetch(config: WorkspaceInfo, input: RequestInfo | URL, init?: RequestInit): Promise<Response>
+  target(config: WorkspaceInfo): Target | Promise<Target>
 }
diff --git a/packages/opencode/src/control-plane/workspace.ts b/packages/opencode/src/control-plane/workspace.ts
index e5294844b148..bb0fd60020bf 100644
--- a/packages/opencode/src/control-plane/workspace.ts
+++ b/packages/opencode/src/control-plane/workspace.ts
@@ -116,17 +116,31 @@ export namespace Workspace {
   async function workspaceEventLoop(space: Info, stop: AbortSignal) {
     while (!stop.aborted) {
       const adaptor = await getAdaptor(space.type)
-      const res = await adaptor.fetch(space, "/event", { method: "GET", signal: stop }).catch(() => undefined)
-      if (!res || !res.ok || !res.body) {
+      const target = await Promise.resolve(adaptor.target(space))
+
+      if (target.type === "local") {
+        return
+      }
+
+      const baseURL = String(target.url).replace(/\/?$/, "/")
+
+      const res = await fetch(new URL(baseURL + "/event"), {
+        method: "GET",
+        signal: stop,
+      })
+
+      if (!res.ok || !res.body) {
         await sleep(1000)
         continue
       }
+
       await parseSSE(res.body, stop, (event) => {
         GlobalBus.emit("event", {
           directory: space.id,
           payload: event,
         })
       })
+
       // Wait 250ms and retry if SSE connection fails
       await sleep(250)
     }
diff --git a/packages/opencode/src/server/proxy.ts b/packages/opencode/src/server/proxy.ts
new file mode 100644
index 000000000000..c489c6b42bf7
--- /dev/null
+++ b/packages/opencode/src/server/proxy.ts
@@ -0,0 +1,130 @@
+import type { Target } from "@/control-plane/types"
+import { lazy } from "@/util/lazy"
+import { Hono } from "hono"
+import { upgradeWebSocket } from "hono/bun"
+
+const hop = new Set([
+  "connection",
+  "keep-alive",
+  "proxy-authenticate",
+  "proxy-authorization",
+  "proxy-connection",
+  "te",
+  "trailer",
+  "transfer-encoding",
+  "upgrade",
+  "host",
+])
+
+type Msg = string | ArrayBuffer | Uint8Array
+
+function headers(req: Request, extra?: HeadersInit) {
+  const out = new Headers(req.headers)
+  for (const key of hop) out.delete(key)
+  out.delete("x-opencode-directory")
+  out.delete("x-opencode-workspace")
+  if (!extra) return out
+  for (const [key, value] of new Headers(extra).entries()) {
+    out.set(key, value)
+  }
+  return out
+}
+
+function protocols(req: Request) {
+  const value = req.headers.get("sec-websocket-protocol")
+  if (!value) return []
+  return value
+    .split(",")
+    .map((item) => item.trim())
+    .filter(Boolean)
+}
+
+function socket(url: string | URL) {
+  const next = new URL(url)
+  if (next.protocol === "http:") next.protocol = "ws:"
+  if (next.protocol === "https:") next.protocol = "wss:"
+  return next.toString()
+}
+
+function send(ws: { send(data: string | ArrayBuffer | Uint8Array): void }, data: any) {
+  if (data instanceof Blob) {
+    return data.arrayBuffer().then((x) => ws.send(x))
+  }
+  return ws.send(data)
+}
+
+const app = lazy(() =>
+  new Hono().get(
+    "/__workspace_ws",
+    upgradeWebSocket((c) => {
+      const url = c.req.header("x-opencode-proxy-url")
+      const queue: Msg[] = []
+      let remote: WebSocket | undefined
+      return {
+        onOpen(_, ws) {
+          if (!url) {
+            ws.close(1011, "missing proxy target")
+            return
+          }
+          remote = new WebSocket(url, protocols(c.req.raw))
+          remote.binaryType = "arraybuffer"
+          remote.onopen = () => {
+            for (const item of queue) remote?.send(item)
+            queue.length = 0
+          }
+          remote.onmessage = (event) => {
+            send(ws, event.data)
+          }
+          remote.onerror = () => {
+            ws.close(1011, "proxy error")
+          }
+          remote.onclose = (event) => {
+            ws.close(event.code, event.reason)
+          }
+        },
+        onMessage(event) {
+          const data = event.data
+          if (typeof data !== "string" && !(data instanceof Uint8Array) && !(data instanceof ArrayBuffer)) return
+          if (remote?.readyState === WebSocket.OPEN) {
+            remote.send(data)
+            return
+          }
+          queue.push(data)
+        },
+        onClose(event) {
+          remote?.close(event.code, event.reason)
+        },
+      }
+    }),
+  ),
+)
+
+export namespace ServerProxy {
+  export function http(target: Extract<Target, { type: "remote" }>, req: Request) {
+    return fetch(
+      new Request(target.url, {
+        method: req.method,
+        headers: headers(req, target.headers),
+        body: req.method === "GET" || req.method === "HEAD" ? undefined : req.body,
+        redirect: "manual",
+        signal: req.signal,
+      }),
+    )
+  }
+
+  export function websocket(target: Extract<Target, { type: "remote" }>, req: Request, env: unknown) {
+    const url = new URL(req.url)
+    url.pathname = "/__workspace_ws"
+    url.search = ""
+    const next = new Headers(req.headers)
+    next.set("x-opencode-proxy-url", socket(target.url))
+    return app().fetch(
+      new Request(url, {
+        method: req.method,
+        headers: next,
+        signal: req.signal,
+      }),
+      env as never,
+    )
+  }
+}
diff --git a/packages/opencode/src/server/router.ts b/packages/opencode/src/server/router.ts
index b239c6272847..b6f99ec73bd0 100644
--- a/packages/opencode/src/server/router.ts
+++ b/packages/opencode/src/server/router.ts
@@ -3,6 +3,7 @@ import type { UpgradeWebSocket } from "hono/ws"
 import { getAdaptor } from "@/control-plane/adaptors"
 import { WorkspaceID } from "@/control-plane/schema"
 import { Workspace } from "@/control-plane/workspace"
+import { ServerProxy } from "./proxy"
 import { lazy } from "@/util/lazy"
 import { Filesystem } from "@/util/filesystem"
 import { Instance } from "@/project/instance"
@@ -41,7 +42,7 @@ export function WorkspaceRouterMiddleware(upgrade: UpgradeWebSocket): Middleware
     )

     const url = new URL(c.req.url)
-    const workspaceParam = url.searchParams.get("workspace")
+    const workspaceParam = url.searchParams.get("workspace") || c.req.header("x-opencode-workspace")

     // TODO: If session is being routed, force it to lookup the
     // project/workspace
@@ -68,11 +69,12 @@ export function WorkspaceRouterMiddleware(upgrade: UpgradeWebSocket): Middleware
       })
     }

-    // Handle local workspaces directly so we can pass env to `fetch`,
-    // necessary for websocket upgrades
-    if (workspace.type === "worktree") {
+    const adaptor = await getAdaptor(workspace.type)
+    const target = await adaptor.target(workspace)
+
+    if (target.type === "local") {
       return Instance.provide({
-        directory: workspace.directory!,
+        directory: target.directory,
         init: InstanceBootstrap,
         async fn() {
           return routes().fetch(c.req.raw, c.env)
@@ -80,23 +82,24 @@ export function WorkspaceRouterMiddleware(upgrade: UpgradeWebSocket): Middleware
       })
     }

-    // Remote workspaces
-
     if (local(c.req.method, url.pathname)) {
       // No instance provided because we are serving cached data; there
       // is no instance to work with
       return routes().fetch(c.req.raw, c.env)
     }

-    const adaptor = await getAdaptor(workspace.type)
+    if (c.req.header("upgrade")?.toLowerCase() === "websocket") {
+      return ServerProxy.websocket(target, c.req.raw, c.env)
+    }
+
     const headers = new Headers(c.req.raw.headers)
     headers.delete("x-opencode-workspace")

-    return adaptor.fetch(workspace, `${url.pathname}${url.search}`, {
-      method: c.req.method,
-      body: c.req.method === "GET" || c.req.method === "HEAD" ? undefined : await c.req.raw.arrayBuffer(),
-      signal: c.req.raw.signal,
-      headers,
-    })
+    return ServerProxy.http(
+      target,
+      new Request(c.req.raw, {
+        headers,
+      }),
+    )
   }
 }

PATCH

echo "Patch applied successfully."
