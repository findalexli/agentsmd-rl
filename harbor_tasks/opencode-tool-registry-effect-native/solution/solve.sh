#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="/workspace/opencode"
cd "$REPO_ROOT"

# Idempotency check: if Config.Service is already yielded at top of generator, skip
if grep -q 'const config = yield\* Config\.Service' packages/opencode/src/tool/registry.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/plugin/index.ts b/packages/opencode/src/plugin/index.ts
index 9804169a463..df644c42a9f 100644
--- a/packages/opencode/src/plugin/index.ts
+++ b/packages/opencode/src/plugin/index.ts
@@ -194,7 +194,7 @@ export namespace Plugin {
     }),
   )

-  const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
+  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
   const { runPromise } = makeRuntime(Service, defaultLayer)

   export async function trigger<
diff --git a/packages/opencode/src/tool/registry.ts b/packages/opencode/src/tool/registry.ts
index ada761fd504..1e2b72ee289 100644
--- a/packages/opencode/src/tool/registry.ts
+++ b/packages/opencode/src/tool/registry.ts
@@ -54,6 +54,9 @@ export namespace ToolRegistry {
   export const layer = Layer.effect(
     Service,
     Effect.gen(function* () {
+      const config = yield* Config.Service
+      const plugin = yield* Plugin.Service
+
       const cache = yield* InstanceState.make<State>(
         Effect.fn("ToolRegistry.state")(function* (ctx) {
           const custom: Tool.Info[] = []
@@ -82,35 +85,34 @@ export namespace ToolRegistry {
             }
           }

-          yield* Effect.promise(async () => {
-            const matches = await Config.directories().then((dirs) =>
-              dirs.flatMap((dir) =>
-                Glob.scanSync("{tool,tools}/*.{js,ts}", { cwd: dir, absolute: true, dot: true, symlink: true }),
-              ),
+          const dirs = yield* config.directories()
+          const matches = dirs.flatMap((dir) =>
+            Glob.scanSync("{tool,tools}/*.{js,ts}", { cwd: dir, absolute: true, dot: true, symlink: true }),
+          )
+          if (matches.length) yield* config.waitForDependencies()
+          for (const match of matches) {
+            const namespace = path.basename(match, path.extname(match))
+            const mod = yield* Effect.promise(() =>
+              import(process.platform === "win32" ? match : pathToFileURL(match).href),
             )
-            if (matches.length) await Config.waitForDependencies()
-            for (const match of matches) {
-              const namespace = path.basename(match, path.extname(match))
-              const mod = await import(process.platform === "win32" ? match : pathToFileURL(match).href)
-              for (const [id, def] of Object.entries<ToolDefinition>(mod)) {
-                custom.push(fromPlugin(id === "default" ? namespace : `${namespace}_${id}`, def))
-              }
+            for (const [id, def] of Object.entries<ToolDefinition>(mod)) {
+              custom.push(fromPlugin(id === "default" ? namespace : `${namespace}_${id}`, def))
             }
+          }

-            const plugins = await Plugin.list()
-            for (const plugin of plugins) {
-              for (const [id, def] of Object.entries(plugin.tool ?? {})) {
-                custom.push(fromPlugin(id, def))
-              }
+          const plugins = yield* plugin.list()
+          for (const p of plugins) {
+            for (const [id, def] of Object.entries(p.tool ?? {})) {
+              custom.push(fromPlugin(id, def))
             }
-          })
+          }

           return { custom }
         }),
       )

-      async function all(custom: Tool.Info[]): Promise<Tool.Info[]> {
-        const cfg = await Config.get()
+      const all = Effect.fn("ToolRegistry.all")(function* (custom: Tool.Info[]) {
+        const cfg = yield* config.get()
         const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL

         return [
@@ -134,7 +136,7 @@ export namespace ToolRegistry {
           ...(Flag.OPENCODE_EXPERIMENTAL_PLAN_MODE && Flag.OPENCODE_CLIENT === "cli" ? [PlanExitTool] : []),
           ...custom,
         ]
-      }
+      })

       const register = Effect.fn("ToolRegistry.register")(function* (tool: Tool.Info) {
         const state = yield* InstanceState.get(cache)
@@ -148,7 +150,7 @@ export namespace ToolRegistry {

       const ids = Effect.fn("ToolRegistry.ids")(function* () {
         const state = yield* InstanceState.get(cache)
-        const tools = yield* Effect.promise(() => all(state.custom))
+        const tools = yield* all(state.custom)
         return tools.map((t) => t.id)
       })

@@ -157,40 +159,37 @@ export namespace ToolRegistry {
         agent?: Agent.Info,
       ) {
         const state = yield* InstanceState.get(cache)
-        const allTools = yield* Effect.promise(() => all(state.custom))
-        return yield* Effect.promise(() =>
-          Promise.all(
-            allTools
-              .filter((tool) => {
-                // Enable websearch/codesearch for zen users OR via enable flag
-                if (tool.id === "codesearch" || tool.id === "websearch") {
-                  return model.providerID === ProviderID.opencode || Flag.OPENCODE_ENABLE_EXA
-                }
-
-                // use apply tool in same format as codex
-                const usePatch =
-                  model.modelID.includes("gpt-") && !model.modelID.includes("oss") && !model.modelID.includes("gpt-4")
-                if (tool.id === "apply_patch") return usePatch
-                if (tool.id === "edit" || tool.id === "write") return !usePatch
-
-                return true
-              })
-              .map(async (tool) => {
-                using _ = log.time(tool.id)
-                const next = await tool.init({ agent })
-                const output = {
-                  description: next.description,
-                  parameters: next.parameters,
-                }
-                await Plugin.trigger("tool.definition", { toolID: tool.id }, output)
-                return {
-                  id: tool.id,
-                  ...next,
-                  description: output.description,
-                  parameters: output.parameters,
-                }
-              }),
-          ),
+        const allTools = yield* all(state.custom)
+        const filtered = allTools.filter((tool) => {
+          if (tool.id === "codesearch" || tool.id === "websearch") {
+            return model.providerID === ProviderID.opencode || Flag.OPENCODE_ENABLE_EXA
+          }
+
+          const usePatch =
+            model.modelID.includes("gpt-") && !model.modelID.includes("oss") && !model.modelID.includes("gpt-4")
+          if (tool.id === "apply_patch") return usePatch
+          if (tool.id === "edit" || tool.id === "write") return !usePatch
+
+          return true
+        })
+        return yield* Effect.forEach(
+          filtered,
+          Effect.fnUntraced(function* (tool) {
+            using _ = log.time(tool.id)
+            const next = yield* Effect.promise(() => tool.init({ agent }))
+            const output = {
+              description: next.description,
+              parameters: next.parameters,
+            }
+            yield* plugin.trigger("tool.definition", { toolID: tool.id }, output)
+            return {
+              id: tool.id,
+              ...next,
+              description: output.description,
+              parameters: output.parameters,
+            } as Awaited<ReturnType<Tool.Info["init"]>> & { id: string }
+          }),
+          { concurrency: "unbounded" },
         )
       })

@@ -198,7 +197,11 @@ export namespace ToolRegistry {
     }),
   )

-  const { runPromise } = makeRuntime(Service, layer)
+  export const defaultLayer = Layer.unwrap(
+    Effect.sync(() => layer.pipe(Layer.provide(Config.defaultLayer), Layer.provide(Plugin.defaultLayer))),
+  )
+
+  const { runPromise } = makeRuntime(Service, defaultLayer)

   export async function register(tool: Tool.Info) {
     return runPromise((svc) => svc.register(tool))
@@ -214,7 +217,7 @@ export namespace ToolRegistry {
       modelID: ModelID
     },
     agent?: Agent.Info,
-  ) {
+  ): Promise<(Awaited<ReturnType<Tool.Info["init"]>> & { id: string })[]> {
     return runPromise((svc) => svc.tools(model, agent))
   }
 }

PATCH
