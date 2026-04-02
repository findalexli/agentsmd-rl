#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check: if router.ts already exists with Instance.provide, patch is applied
if grep -q 'Instance.provide' packages/opencode/src/server/router.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/control-plane/adaptors/worktree.ts b/packages/opencode/src/control-plane/adaptors/worktree.ts
index 2a96034d787..719748e3a19 100644
--- a/packages/opencode/src/control-plane/adaptors/worktree.ts
+++ b/packages/opencode/src/control-plane/adaptors/worktree.ts
@@ -32,15 +32,7 @@ export const WorktreeAdaptor: Adaptor = {
     const config = Config.parse(info)
     await Worktree.remove({ directory: config.directory })
   },
-  async fetch(info, input: RequestInfo | URL, init?: RequestInit) {
-    const { Server } = await import("../../server/server")
-
-    const config = Config.parse(info)
-    const url = input instanceof Request || input instanceof URL ? input : new URL(input, "http://opencode.internal")
-    const headers = new Headers(init?.headers ?? (input instanceof Request ? input.headers : undefined))
-    headers.set("x-opencode-directory", config.directory)
-
-    const request = new Request(url, { ...init, headers })
-    return Server.Default().fetch(request)
+  async fetch(_info, _input: RequestInfo | URL, _init?: RequestInit) {
+    throw new Error("fetch not implemented")
   },
 }
diff --git a/packages/opencode/src/control-plane/workspace-router-middleware.ts b/packages/opencode/src/control-plane/workspace-router-middleware.ts
deleted file mode 100644
index 1fc19a22b1a..00000000000
--- a/packages/opencode/src/control-plane/workspace-router-middleware.ts
+++ /dev/null
@@ -1,64 +0,0 @@
-import type { MiddlewareHandler } from "hono"
-import { Flag } from "../flag/flag"
-import { getAdaptor } from "./adaptors"
-import { WorkspaceID } from "./schema"
-import { Workspace } from "./workspace"
-import { InstanceRoutes } from "../server/instance"
-import { lazy } from "../util/lazy"
-
-type Rule = { method?: string; path: string; exact?: boolean; action: "local" | "forward" }
-
-const RULES: Array<Rule> = [
-  { path: "/session/status", action: "forward" },
-  { method: "GET", path: "/session", action: "local" },
-]
-
-function local(method: string, path: string) {
-  for (const rule of RULES) {
-    if (rule.method && rule.method !== method) continue
-    const match = rule.exact ? path === rule.path : path === rule.path || path.startsWith(rule.path + "/")
-    if (match) return rule.action === "local"
-  }
-  return false
-}
-
-const routes = lazy(() => InstanceRoutes())
-
-export const WorkspaceRouterMiddleware: MiddlewareHandler = async (c) => {
-  if (!Flag.OPENCODE_EXPERIMENTAL_WORKSPACES) {
-    return routes().fetch(c.req.raw, c.env)
-  }
-
-  const url = new URL(c.req.url)
-  const raw = url.searchParams.get("workspace")
-
-  if (!raw) {
-    return routes().fetch(c.req.raw, c.env)
-  }
-
-  if (local(c.req.method, url.pathname)) {
-    return routes().fetch(c.req.raw, c.env)
-  }
-
-  const workspaceID = WorkspaceID.make(raw)
-  const workspace = await Workspace.get(workspaceID)
-  if (!workspace) {
-    return new Response(`Workspace not found: ${workspaceID}`, {
-      status: 500,
-      headers: {
-        "content-type": "text/plain; charset=utf-8",
-      },
-    })
-  }
-
-  const adaptor = await getAdaptor(workspace.type)
-  const headers = new Headers(c.req.raw.headers)
-  headers.delete("x-opencode-workspace")
-
-  return adaptor.fetch(workspace, `${url.pathname}${url.search}`, {
-    method: c.req.method,
-    body: c.req.method === "GET" || c.req.method === "HEAD" ? undefined : await c.req.raw.arrayBuffer(),
-    signal: c.req.raw.signal,
-    headers,
-  })
-}
diff --git a/packages/opencode/src/server/instance.ts b/packages/opencode/src/server/instance.ts
index b99cf3d99f9..4bb6efaf9b0 100644
--- a/packages/opencode/src/server/instance.ts
+++ b/packages/opencode/src/server/instance.ts
@@ -14,7 +14,6 @@ import { Global } from "../global"
 import { LSP } from "../lsp"
 import { Command } from "../command"
 import { Flag } from "../flag/flag"
-import { Filesystem } from "@/util/filesystem"
 import { QuestionRoutes } from "./routes/question"
 import { PermissionRoutes } from "./routes/permission"
 import { ProjectRoutes } from "./routes/project"
@@ -26,7 +25,6 @@ import { ConfigRoutes } from "./routes/config"
 import { ExperimentalRoutes } from "./routes/experimental"
 import { ProviderRoutes } from "./routes/provider"
 import { EventRoutes } from "./routes/event"
-import { InstanceBootstrap } from "../project/bootstrap"
 import { errorHandler } from "./middleware"

 const log = Log.create({ service: "server" })
@@ -45,26 +43,6 @@ const csp = (hash = "") =>
 export const InstanceRoutes = (app?: Hono) =>
   (app ?? new Hono())
     .onError(errorHandler(log))
-    .use(async (c, next) => {
-      const raw = c.req.query("directory") || c.req.header("x-opencode-directory") || process.cwd()
-      const directory = Filesystem.resolve(
-        (() => {
-          try {
-            return decodeURIComponent(raw)
-          } catch {
-            return raw
-          }
-        })(),
-      )
-
-      return Instance.provide({
-        directory,
-        init: InstanceBootstrap,
-        async fn() {
-          return next()
-        },
-      })
-    })
     .route("/project", ProjectRoutes())
     .route("/pty", PtyRoutes())
     .route("/config", ConfigRoutes())
diff --git a/packages/opencode/src/server/router.ts b/packages/opencode/src/server/router.ts
new file mode 100644
index 00000000000..f64180892ee
--- /dev/null
+++ b/packages/opencode/src/server/router.ts
@@ -0,0 +1,99 @@
+import type { MiddlewareHandler } from "hono"
+import { getAdaptor } from "@/control-plane/adaptors"
+import { WorkspaceID } from "@/control-plane/schema"
+import { Workspace } from "@/control-plane/workspace"
+import { lazy } from "@/util/lazy"
+import { Filesystem } from "@/util/filesystem"
+import { Instance } from "@/project/instance"
+import { InstanceBootstrap } from "@/project/bootstrap"
+import { InstanceRoutes } from "./instance"
+
+type Rule = { method?: string; path: string; exact?: boolean; action: "local" | "forward" }
+
+const RULES: Array<Rule> = [
+  { path: "/session/status", action: "forward" },
+  { method: "GET", path: "/session", action: "local" },
+]
+
+function local(method: string, path: string) {
+  for (const rule of RULES) {
+    if (rule.method && rule.method !== method) continue
+    const match = rule.exact ? path === rule.path : path === rule.path || path.startsWith(rule.path + "/")
+    if (match) return rule.action === "local"
+  }
+  return false
+}
+
+const routes = lazy(() => InstanceRoutes())
+
+export const WorkspaceRouterMiddleware: MiddlewareHandler = async (c) => {
+  const raw = c.req.query("directory") || c.req.header("x-opencode-directory") || process.cwd()
+  const directory = Filesystem.resolve(
+    (() => {
+      try {
+        return decodeURIComponent(raw)
+      } catch {
+        return raw
+      }
+    })(),
+  )
+
+  const url = new URL(c.req.url)
+  const workspaceParam = url.searchParams.get("workspace")
+
+  // TODO: If session is being routed, force it to lookup the
+  // project/workspace
+
+  // If no workspace is provided we use the "project" workspace
+  if (!workspaceParam) {
+    return Instance.provide({
+      directory,
+      init: InstanceBootstrap,
+      async fn() {
+        return routes().fetch(c.req.raw, c.env)
+      },
+    })
+  }
+
+  const workspaceID = WorkspaceID.make(workspaceParam)
+  const workspace = await Workspace.get(workspaceID)
+  if (!workspace) {
+    return new Response(`Workspace not found: ${workspaceID}`, {
+      status: 500,
+      headers: {
+        "content-type": "text/plain; charset=utf-8",
+      },
+    })
+  }
+
+  // Handle local workspaces directly so we can pass env to `fetch`,
+  // necessary for websocket upgrades
+  if (workspace.type === "worktree") {
+    return Instance.provide({
+      directory: workspace.directory!,
+      init: InstanceBootstrap,
+      async fn() {
+        return routes().fetch(c.req.raw, c.env)
+      },
+    })
+  }
+
+  // Remote workspaces
+
+  if (local(c.req.method, url.pathname)) {
+    // No instance provided because we are serving cached data; there
+    // is no instance to work with
+    return routes().fetch(c.req.raw, c.env)
+  }
+
+  const adaptor = await getAdaptor(workspace.type)
+  const headers = new Headers(c.req.raw.headers)
+  headers.delete("x-opencode-workspace")
+
+  return adaptor.fetch(workspace, `${url.pathname}${url.search}`, {
+    method: c.req.method,
+    body: c.req.method === "GET" || c.req.method === "HEAD" ? undefined : await c.req.raw.arrayBuffer(),
+    signal: c.req.raw.signal,
+    headers,
+  })
+}
diff --git a/packages/opencode/src/server/server.ts b/packages/opencode/src/server/server.ts
index cfb22929bcd..ec245ed59f2 100644
--- a/packages/opencode/src/server/server.ts
+++ b/packages/opencode/src/server/server.ts
@@ -8,7 +8,7 @@ import z from "zod"
 import { Auth } from "../auth"
 import { Flag } from "../flag/flag"
 import { ProviderID } from "../provider/schema"
-import { WorkspaceRouterMiddleware } from "../control-plane/workspace-router-middleware"
+import { WorkspaceRouterMiddleware } from "./router"
 import { websocket } from "hono/bun"
 import { errors } from "./error"
 import { GlobalRoutes } from "./routes/global"

PATCH
