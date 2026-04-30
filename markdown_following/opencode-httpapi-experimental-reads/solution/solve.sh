#!/usr/bin/env bash
# Gold patch for anomalyco/opencode#24365.
#
# Idempotency guard: bail if the new module already exists.
set -e

cd /workspace/opencode

if grep -q "^export const ExperimentalApi = HttpApi.make" \
        packages/opencode/src/server/routes/instance/httpapi/experimental.ts 2>/dev/null; then
    echo "Patch already applied — exiting."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/specs/effect/http-api.md b/packages/opencode/specs/effect/http-api.md
index 948389223bd..6d0381d2d86 100644
--- a/packages/opencode/specs/effect/http-api.md
+++ b/packages/opencode/specs/effect/http-api.md
@@ -30,6 +30,29 @@ Plan for replacing instance Hono route implementations with Effect `HttpApi` whi
 - Regenerate the SDK after schema or OpenAPI-affecting changes and verify the diff is expected.
 - Do not delete a Hono route until the SDK/OpenAPI pipeline no longer depends on its Hono `describeRoute` entry.
 
+## Route Slice Checklist
+
+Use this checklist for each small HttpApi migration PR:
+
+1. Read the legacy Hono route and copy behavior exactly, including default values, headers, operation IDs, response schemas, and status codes.
+2. Put the new `HttpApiGroup`, route paths, DTO schemas, and handlers in `src/server/routes/instance/httpapi/*`.
+3. Mount the new paths in `src/server/routes/instance/index.ts` only inside the `OPENCODE_EXPERIMENTAL_HTTPAPI` block.
+4. Use `InstanceState.context` / `InstanceState.directory` inside HttpApi handlers instead of `Instance.directory`, `Instance.worktree`, or `Instance.project` ALS globals.
+5. Reuse existing services directly. If a service returns plain objects, use `Schema.Struct`; use `Schema.Class` only when handlers return actual class instances.
+6. Keep legacy Hono routes and `.zod` compatibility in place for SDK/OpenAPI generation.
+7. Add tests that hit the Hono-mounted bridge via `InstanceRoutes`, not only the raw `HttpApi` web handler, when the route depends on auth or instance context.
+8. Run `bun typecheck` from `packages/opencode`, relevant `bun run test:ci ...` tests from `packages/opencode`, and `./packages/sdk/js/script/build.ts` from the repo root.
+
+## Experimental Read Slice Guidance
+
+For the experimental route group, port read-only JSON routes before mutations:
+
+- Good first batch: `GET /console`, `GET /console/orgs`, `GET /tool/ids`, `GET /resource`.
+- Consider `GET /worktree` only if the handler uses `InstanceState.context` instead of `Instance.project`.
+- Defer `POST /console/switch`, worktree create/remove/reset, and `GET /session` to separate PRs because they mutate state or have broader pagination/session behavior.
+- Preserve response headers such as pagination cursors if a route is ported.
+- If SDK generation changes, explain whether it is a semantic contract change or a generator-equivalent type normalization.
+
 ## Schema Notes
 
 - Use `Schema.Struct(...).annotate({ identifier })` for named OpenAPI refs when handlers return plain objects.
@@ -141,7 +164,7 @@ Use raw Effect HTTP routes where `HttpApi` does not fit. The goal is deleting Ho
 | `mcp`                    | `bridged` partial | status only                                            |
 | `workspace`              | `bridged`         | list, get, enter                                       |
 | top-level instance reads | `bridged`         | path, vcs, command, agent, skill, lsp, formatter       |
-| experimental JSON routes | `next/later`      | console, tool, worktree, resource, global session list |
+| experimental JSON routes | `bridged` partial | console reads, tool ids, resource list; worktree and global session list remain later |
 | `session`                | `later/special`   | large stateful surface plus streaming                  |
 | `sync`                   | `later`           | process/control side effects                           |
 | `event`                  | `special`         | SSE                                                    |
diff --git a/packages/opencode/src/mcp/index.ts b/packages/opencode/src/mcp/index.ts
index 23862db63ef..cfed592c4dd 100644
--- a/packages/opencode/src/mcp/index.ts
+++ b/packages/opencode/src/mcp/index.ts
@@ -36,16 +36,16 @@ import { withStatics } from "@/util/schema"
 const log = Log.create({ service: "mcp" })
 const DEFAULT_TIMEOUT = 30_000
 
-export const Resource = z
-  .object({
-    name: z.string(),
-    uri: z.string(),
-    description: z.string().optional(),
-    mimeType: z.string().optional(),
-    client: z.string(),
-  })
-  .meta({ ref: "McpResource" })
-export type Resource = z.infer<typeof Resource>
+export const Resource = Schema.Struct({
+  name: Schema.String,
+  uri: Schema.String,
+  description: Schema.optional(Schema.String),
+  mimeType: Schema.optional(Schema.String),
+  client: Schema.String,
+})
+  .annotate({ identifier: "McpResource" })
+  .pipe(withStatics((s) => ({ zod: effectZod(s) })))
+export type Resource = Schema.Schema.Type<typeof Resource>
 
 export const ToolsChanged = BusEvent.define(
   "mcp.tools.changed",
diff --git a/packages/opencode/src/server/routes/instance/experimental.ts b/packages/opencode/src/server/routes/instance/experimental.ts
index f13003cb4e5..0936f6252ce 100644
--- a/packages/opencode/src/server/routes/instance/experimental.ts
+++ b/packages/opencode/src/server/routes/instance/experimental.ts
@@ -394,7 +394,7 @@ export const ExperimentalRoutes = lazy(() =>
             description: "MCP resources",
             content: {
               "application/json": {
-                schema: resolver(z.record(z.string(), MCP.Resource)),
+                schema: resolver(z.record(z.string(), MCP.Resource.zod)),
               },
             },
           },
diff --git a/packages/opencode/src/server/routes/instance/httpapi/experimental.ts b/packages/opencode/src/server/routes/instance/httpapi/experimental.ts
new file mode 100644
index 00000000000..993971202f9
--- /dev/null
+++ b/packages/opencode/src/server/routes/instance/httpapi/experimental.ts
@@ -0,0 +1,159 @@
+import { Account } from "@/account/account"
+import { Config } from "@/config"
+import { MCP } from "@/mcp"
+import { ToolRegistry } from "@/tool"
+import { Effect, Layer, Option, Schema } from "effect"
+import { HttpApi, HttpApiBuilder, HttpApiEndpoint, HttpApiGroup, OpenApi } from "effect/unstable/httpapi"
+import { Authorization } from "./auth"
+
+const ConsoleStateResponse = Schema.Struct({
+  consoleManagedProviders: Schema.mutable(Schema.Array(Schema.String)),
+  activeOrgName: Schema.optionalKey(Schema.String),
+  switchableOrgCount: Schema.Number,
+}).annotate({ identifier: "ConsoleState" })
+
+const ConsoleOrgOption = Schema.Struct({
+  accountID: Schema.String,
+  accountEmail: Schema.String,
+  accountUrl: Schema.String,
+  orgID: Schema.String,
+  orgName: Schema.String,
+  active: Schema.Boolean,
+}).annotate({ identifier: "ConsoleOrgOption" })
+
+const ConsoleOrgList = Schema.Struct({
+  orgs: Schema.Array(ConsoleOrgOption),
+}).annotate({ identifier: "ConsoleOrgList" })
+
+const ToolIDs = Schema.Array(Schema.String).annotate({ identifier: "ToolIDs" })
+
+export const ExperimentalPaths = {
+  console: "/experimental/console",
+  consoleOrgs: "/experimental/console/orgs",
+  toolIDs: "/experimental/tool/ids",
+  resource: "/experimental/resource",
+} as const
+
+export const ExperimentalApi = HttpApi.make("experimental")
+  .add(
+    HttpApiGroup.make("experimental")
+      .add(
+        HttpApiEndpoint.get("console", ExperimentalPaths.console, {
+          success: ConsoleStateResponse,
+        }).annotateMerge(
+          OpenApi.annotations({
+            identifier: "experimental.console.get",
+            summary: "Get active Console provider metadata",
+            description: "Get the active Console org name and the set of provider IDs managed by that Console org.",
+          }),
+        ),
+        HttpApiEndpoint.get("consoleOrgs", ExperimentalPaths.consoleOrgs, {
+          success: ConsoleOrgList,
+        }).annotateMerge(
+          OpenApi.annotations({
+            identifier: "experimental.console.listOrgs",
+            summary: "List switchable Console orgs",
+            description: "Get the available Console orgs across logged-in accounts, including the current active org.",
+          }),
+        ),
+        HttpApiEndpoint.get("toolIDs", ExperimentalPaths.toolIDs, {
+          success: ToolIDs,
+        }).annotateMerge(
+          OpenApi.annotations({
+            identifier: "tool.ids",
+            summary: "List tool IDs",
+            description:
+              "Get a list of all available tool IDs, including both built-in tools and dynamically registered tools.",
+          }),
+        ),
+        HttpApiEndpoint.get("resource", ExperimentalPaths.resource, {
+          success: Schema.Record(Schema.String, MCP.Resource),
+        }).annotateMerge(
+          OpenApi.annotations({
+            identifier: "experimental.resource.list",
+            summary: "Get MCP resources",
+            description: "Get all available MCP resources from connected servers. Optionally filter by name.",
+          }),
+        ),
+      )
+      .annotateMerge(
+        OpenApi.annotations({
+          title: "experimental",
+          description: "Experimental HttpApi read-only routes.",
+        }),
+      )
+      .middleware(Authorization),
+  )
+  .annotateMerge(
+    OpenApi.annotations({
+      title: "opencode experimental HttpApi",
+      version: "0.0.1",
+      description: "Experimental HttpApi surface for selected instance routes.",
+    }),
+  )
+
+export const experimentalHandlers = Layer.unwrap(
+  Effect.gen(function* () {
+    const account = yield* Account.Service
+    const config = yield* Config.Service
+    const mcp = yield* MCP.Service
+    const registry = yield* ToolRegistry.Service
+
+    const getConsole = Effect.fn("ExperimentalHttpApi.console")(function* () {
+      const [state, groups] = yield* Effect.all(
+        [config.getConsoleState(), account.orgsByAccount().pipe(Effect.orDie)],
+        {
+          concurrency: "unbounded",
+        },
+      )
+      return {
+        consoleManagedProviders: state.consoleManagedProviders,
+        ...(state.activeOrgName ? { activeOrgName: state.activeOrgName } : {}),
+        switchableOrgCount: groups.reduce((count, group) => count + group.orgs.length, 0),
+      }
+    })
+
+    const listConsoleOrgs = Effect.fn("ExperimentalHttpApi.consoleOrgs")(function* () {
+      const [groups, active] = yield* Effect.all(
+        [account.orgsByAccount().pipe(Effect.orDie), account.active().pipe(Effect.orDie)],
+        {
+          concurrency: "unbounded",
+        },
+      )
+      const info = Option.getOrUndefined(active)
+      return {
+        orgs: groups.flatMap((group) =>
+          group.orgs.map((org) => ({
+            accountID: group.account.id,
+            accountEmail: group.account.email,
+            accountUrl: group.account.url,
+            orgID: org.id,
+            orgName: org.name,
+            active: !!info && info.id === group.account.id && info.active_org_id === org.id,
+          })),
+        ),
+      }
+    })
+
+    const toolIDs = Effect.fn("ExperimentalHttpApi.toolIDs")(function* () {
+      return yield* registry.ids()
+    })
+
+    const resource = Effect.fn("ExperimentalHttpApi.resource")(function* () {
+      return yield* mcp.resources()
+    })
+
+    return HttpApiBuilder.group(ExperimentalApi, "experimental", (handlers) =>
+      handlers
+        .handle("console", getConsole)
+        .handle("consoleOrgs", listConsoleOrgs)
+        .handle("toolIDs", toolIDs)
+        .handle("resource", resource),
+    )
+  }),
+).pipe(
+  Layer.provide(Account.defaultLayer),
+  Layer.provide(Config.defaultLayer),
+  Layer.provide(MCP.defaultLayer),
+  Layer.provide(ToolRegistry.defaultLayer),
+)
diff --git a/packages/opencode/src/server/routes/instance/httpapi/server.ts b/packages/opencode/src/server/routes/instance/httpapi/server.ts
index 17c3ba4b448..77a2832cefd 100644
--- a/packages/opencode/src/server/routes/instance/httpapi/server.ts
+++ b/packages/opencode/src/server/routes/instance/httpapi/server.ts
@@ -11,6 +11,7 @@ import { Filesystem } from "@/util"
 import { authorizationLayer } from "./auth"
 import { ConfigApi, configHandlers } from "./config"
 import { FileApi, fileHandlers } from "./file"
+import { ExperimentalApi, experimentalHandlers } from "./experimental"
 import { InstanceApi, instanceHandlers } from "./instance"
 import { McpApi, mcpHandlers } from "./mcp"
 import { PermissionApi, permissionHandlers } from "./permission"
@@ -63,6 +64,7 @@ const instance = HttpRouter.middleware()(
 
 export const routes = Layer.mergeAll(
   HttpApiBuilder.layer(ConfigApi).pipe(Layer.provide(configHandlers)),
+  HttpApiBuilder.layer(ExperimentalApi).pipe(Layer.provide(experimentalHandlers)),
   HttpApiBuilder.layer(FileApi).pipe(Layer.provide(fileHandlers)),
   HttpApiBuilder.layer(InstanceApi).pipe(Layer.provide(instanceHandlers)),
   HttpApiBuilder.layer(McpApi).pipe(Layer.provide(mcpHandlers)),
diff --git a/packages/opencode/src/server/routes/instance/index.ts b/packages/opencode/src/server/routes/instance/index.ts
index 488e4354227..65dd417051d 100644
--- a/packages/opencode/src/server/routes/instance/index.ts
+++ b/packages/opencode/src/server/routes/instance/index.ts
@@ -16,6 +16,7 @@ import { QuestionRoutes } from "./question"
 import { PermissionRoutes } from "./permission"
 import { Flag } from "@opencode-ai/core/flag/flag"
 import { ExperimentalHttpApiServer } from "./httpapi/server"
+import { ExperimentalPaths } from "./httpapi/experimental"
 import { FilePaths } from "./httpapi/file"
 import { InstancePaths } from "./httpapi/instance"
 import { McpPaths } from "./httpapi/mcp"
@@ -45,6 +46,10 @@ export const InstanceRoutes = (upgrade: UpgradeWebSocket): Hono => {
     app.post("/permission/:requestID/reply", (c) => handler(c.req.raw, context))
     app.get("/config", (c) => handler(c.req.raw, context))
     app.get("/config/providers", (c) => handler(c.req.raw, context))
+    app.get(ExperimentalPaths.console, (c) => handler(c.req.raw, context))
+    app.get(ExperimentalPaths.consoleOrgs, (c) => handler(c.req.raw, context))
+    app.get(ExperimentalPaths.toolIDs, (c) => handler(c.req.raw, context))
+    app.get(ExperimentalPaths.resource, (c) => handler(c.req.raw, context))
     app.get("/provider", (c) => handler(c.req.raw, context))
     app.get("/provider/auth", (c) => handler(c.req.raw, context))
     app.post("/provider/:providerID/oauth/authorize", (c) => handler(c.req.raw, context))
diff --git a/packages/opencode/src/tool/bash.ts b/packages/opencode/src/tool/bash.ts
index eeba5ebd659..a27d7c5ecb7 100644
--- a/packages/opencode/src/tool/bash.ts
+++ b/packages/opencode/src/tool/bash.ts
@@ -20,6 +20,7 @@ import { Plugin } from "@/plugin"
 import { Effect, Stream } from "effect"
 import { ChildProcess } from "effect/unstable/process"
 import { ChildProcessSpawner } from "effect/unstable/process/ChildProcessSpawner"
+import { InstanceState } from "@/effect"
 
 const MAX_METADATA_LENGTH = 30_000
 const DEFAULT_TIMEOUT = Flag.OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS || 2 * 60 * 1000
@@ -575,9 +576,10 @@ export const BashTool = Tool.define(
         log.info("bash tool using shell", { shell })
 
         const limits = yield* trunc.limits()
+        const instance = yield* InstanceState.context
 
         return {
-          description: DESCRIPTION.replaceAll("${directory}", Instance.directory)
+          description: DESCRIPTION.replaceAll("${directory}", instance.directory)
             .replaceAll("${os}", process.platform)
             .replaceAll("${shell}", name)
             .replaceAll("${chaining}", chain)
diff --git a/packages/opencode/test/server/httpapi-experimental.test.ts b/packages/opencode/test/server/httpapi-experimental.test.ts
new file mode 100644
index 00000000000..00d1fefb885
--- /dev/null
+++ b/packages/opencode/test/server/httpapi-experimental.test.ts
@@ -0,0 +1,66 @@
+import { afterEach, describe, expect, test } from "bun:test"
+import type { UpgradeWebSocket } from "hono/ws"
+import { Flag } from "@opencode-ai/core/flag/flag"
+import { Instance } from "../../src/project/instance"
+import { InstanceRoutes } from "../../src/server/routes/instance"
+import { ExperimentalPaths } from "../../src/server/routes/instance/httpapi/experimental"
+import { Log } from "../../src/util"
+import { resetDatabase } from "../fixture/db"
+import { tmpdir } from "../fixture/fixture"
+
+void Log.init({ print: false })
+
+const original = Flag.OPENCODE_EXPERIMENTAL_HTTPAPI
+const websocket = (() => () => new Response(null, { status: 501 })) as unknown as UpgradeWebSocket
+
+function app() {
+  Flag.OPENCODE_EXPERIMENTAL_HTTPAPI = true
+  return InstanceRoutes(websocket)
+}
+
+afterEach(async () => {
+  Flag.OPENCODE_EXPERIMENTAL_HTTPAPI = original
+  await Instance.disposeAll()
+  await resetDatabase()
+})
+
+describe("experimental HttpApi", () => {
+  test("serves read-only experimental endpoints through Hono bridge", async () => {
+    await using tmp = await tmpdir({
+      config: {
+        formatter: false,
+        lsp: false,
+        mcp: {
+          demo: {
+            type: "local",
+            command: ["echo", "demo"],
+            enabled: false,
+          },
+        },
+      },
+    })
+
+    const headers = { "x-opencode-directory": tmp.path }
+    const [consoleState, consoleOrgs, toolIDs, resources] = await Promise.all([
+      app().request(ExperimentalPaths.console, { headers }),
+      app().request(ExperimentalPaths.consoleOrgs, { headers }),
+      app().request(ExperimentalPaths.toolIDs, { headers }),
+      app().request(ExperimentalPaths.resource, { headers }),
+    ])
+
+    expect(consoleState.status).toBe(200)
+    expect(await consoleState.json()).toEqual({
+      consoleManagedProviders: [],
+      switchableOrgCount: 0,
+    })
+
+    expect(consoleOrgs.status).toBe(200)
+    expect(await consoleOrgs.json()).toEqual({ orgs: [] })
+
+    expect(toolIDs.status).toBe(200)
+    expect(await toolIDs.json()).toContain("bash")
+
+    expect(resources.status).toBe(200)
+    expect(await resources.json()).toEqual({})
+  })
+})
PATCH
echo "Gold patch applied."
