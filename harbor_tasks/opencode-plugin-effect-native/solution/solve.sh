#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/opencode"
FILE="$REPO/packages/opencode/src/plugin/index.ts"

# Idempotency: check if already applied
if grep -q 'const config = yield\* Config\.Service' "$FILE" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd "$REPO"
git apply - <<'PATCH'
diff --git a/packages/opencode/src/plugin/index.ts b/packages/opencode/src/plugin/index.ts
index e7bb2a91d0a..fe4be0372c8 100644
--- a/packages/opencode/src/plugin/index.ts
+++ b/packages/opencode/src/plugin/index.ts
@@ -176,76 +176,86 @@ export namespace Plugin {
     Service,
     Effect.gen(function* () {
       const bus = yield* Bus.Service
+      const config = yield* Config.Service

       const cache = yield* InstanceState.make<State>(
         Effect.fn("Plugin.state")(function* (ctx) {
           const hooks: Hooks[] = []

-          yield* Effect.promise(async () => {
-            const { Server } = await import("../server/server")
-
-            const client = createOpencodeClient({
-              baseUrl: "http://localhost:4096",
-              directory: ctx.directory,
-              headers: Flag.OPENCODE_SERVER_PASSWORD
-                ? {
-                    Authorization: `Basic ${Buffer.from(`${Flag.OPENCODE_SERVER_USERNAME ?? "opencode"}:${Flag.OPENCODE_SERVER_PASSWORD}`).toString("base64")}`,
-                  }
-                : undefined,
-              fetch: async (...args) => Server.Default().fetch(...args),
-            })
-            const cfg = await Config.get()
-            const input: PluginInput = {
-              client,
-              project: ctx.project,
-              worktree: ctx.worktree,
-              directory: ctx.directory,
-              get serverUrl(): URL {
-                return Server.url ?? new URL("http://localhost:4096")
-              },
-              $: Bun.$,
-            }
+          const { Server } = yield* Effect.promise(() => import("../server/server"))
+
+          const client = createOpencodeClient({
+            baseUrl: "http://localhost:4096",
+            directory: ctx.directory,
+            headers: Flag.OPENCODE_SERVER_PASSWORD
+              ? {
+                  Authorization: `Basic ${Buffer.from(`${Flag.OPENCODE_SERVER_USERNAME ?? "opencode"}:${Flag.OPENCODE_SERVER_PASSWORD}`).toString("base64")}`,
+                }
+              : undefined,
+            fetch: async (...args) => Server.Default().fetch(...args),
+          })
+          const cfg = yield* config.get()
+          const input: PluginInput = {
+            client,
+            project: ctx.project,
+            worktree: ctx.worktree,
+            directory: ctx.directory,
+            get serverUrl(): URL {
+              return Server.url ?? new URL("http://localhost:4096")
+            },
+            $: Bun.$,
+          }

-            for (const plugin of INTERNAL_PLUGINS) {
-              log.info("loading internal plugin", { name: plugin.name })
-              const init = await plugin(input).catch((err) => {
+          for (const plugin of INTERNAL_PLUGINS) {
+            log.info("loading internal plugin", { name: plugin.name })
+            const init = yield* Effect.tryPromise({
+              try: () => plugin(input),
+              catch: (err) => {
                 log.error("failed to load internal plugin", { name: plugin.name, error: err })
-              })
-              if (init) hooks.push(init)
-            }
-
-            const plugins = Flag.OPENCODE_PURE ? [] : (cfg.plugin ?? [])
-            if (Flag.OPENCODE_PURE && cfg.plugin?.length) {
-              log.info("skipping external plugins in pure mode", { count: cfg.plugin.length })
-            }
-            if (plugins.length) await Config.waitForDependencies()
-
-            const loaded = await Promise.all(plugins.map((item) => prepPlugin(item)))
-            for (const load of loaded) {
-              if (!load) continue
-
-              // Keep plugin execution sequential so hook registration and execution
-              // order remains deterministic across plugin runs.
-              await applyPlugin(load, input, hooks).catch((err) => {
+              },
+            }).pipe(Effect.option)
+            if (init._tag === "Some") hooks.push(init.value)
+          }
+
+          const plugins = Flag.OPENCODE_PURE ? [] : (cfg.plugin ?? [])
+          if (Flag.OPENCODE_PURE && cfg.plugin?.length) {
+            log.info("skipping external plugins in pure mode", { count: cfg.plugin.length })
+          }
+          if (plugins.length) yield* config.waitForDependencies()
+
+          const loaded = yield* Effect.promise(() => Promise.all(plugins.map((item) => prepPlugin(item))))
+          for (const load of loaded) {
+            if (!load) continue
+
+            // Keep plugin execution sequential so hook registration and execution
+            // order remains deterministic across plugin runs.
+            yield* Effect.tryPromise({
+              try: () => applyPlugin(load, input, hooks),
+              catch: (err) => {
                 const message = errorMessage(err)
                 log.error("failed to load plugin", { path: load.spec, error: message })
-                Bus.publish(Session.Event.Error, {
+                return message
+              },
+            }).pipe(
+              Effect.catch((message) =>
+                bus.publish(Session.Event.Error, {
                   error: new NamedError.Unknown({
                     message: `Failed to load plugin ${load.spec}: ${message}`,
                   }).toObject(),
-                })
-              })
-            }
-
-            // Notify plugins of current config
-            for (const hook of hooks) {
-              try {
-                await (hook as any).config?.(cfg)
-              } catch (err) {
+                }),
+              ),
+            )
+          }
+
+          // Notify plugins of current config
+          for (const hook of hooks) {
+            yield* Effect.tryPromise({
+              try: () => Promise.resolve((hook as any).config?.(cfg)),
+              catch: (err) => {
                 log.error("plugin config hook failed", { error: err })
-              }
-            }
-          })
+              },
+            }).pipe(Effect.ignore)
+          }

           // Subscribe to bus events, fiber interrupted when scope closes
           yield* bus.subscribeAll().pipe(
@@ -270,13 +280,11 @@ export namespace Plugin {
       >(name: Name, input: Input, output: Output) {
         if (!name) return output
         const state = yield* InstanceState.get(cache)
-        yield* Effect.promise(async () => {
-          for (const hook of state.hooks) {
-            const fn = hook[name] as any
-            if (!fn) continue
-            await fn(input, output)
-          }
-        })
+        for (const hook of state.hooks) {
+          const fn = hook[name] as any
+          if (!fn) continue
+          yield* Effect.promise(() => fn(input, output))
+        }
         return output
       })

@@ -293,7 +301,7 @@ export namespace Plugin {
     }),
   )

-  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
+  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer), Layer.provide(Config.defaultLayer))
   const { runPromise } = makeRuntime(Service, defaultLayer)

   export async function trigger<
diff --git a/packages/opencode/test/plugin/auth-override.test.ts b/packages/opencode/test/plugin/auth-override.test.ts
index c25984be6ff..6b77083828d 100644
--- a/packages/opencode/test/plugin/auth-override.test.ts
+++ b/packages/opencode/test/plugin/auth-override.test.ts
@@ -64,12 +64,11 @@ describe("plugin.config-hook-error-isolation", () => {
   test("config hooks are individually error-isolated in the layer factory", async () => {
     const src = await Bun.file(file).text()

-    // The config hook try/catch lives in the InstanceState factory (layer definition),
-    // not in init() which now just delegates to the Effect service.
+    // Each hook's config call is wrapped in Effect.tryPromise with error logging + Effect.ignore
     expect(src).toContain("plugin config hook failed")

     const pattern =
-      /for\s*\(const hook of hooks\)\s*\{[\s\S]*?try\s*\{[\s\S]*?\.config\?\.\([\s\S]*?\}\s*catch\s*\(err\)\s*\{[\s\S]*?plugin config hook failed[\s\S]*?\}/
+      /for\s*\(const hook of hooks\)\s*\{[\s\S]*?Effect\.tryPromise[\s\S]*?\.config\?\.\([\s\S]*?plugin config hook failed[\s\S]*?Effect\.ignore/
     expect(pattern.test(src)).toBe(true)
   })
 })

PATCH

echo "Patch applied successfully."
