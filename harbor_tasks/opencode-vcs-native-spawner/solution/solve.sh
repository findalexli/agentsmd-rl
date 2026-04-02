#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed
if grep -q 'ChildProcessSpawner' packages/opencode/src/project/vcs.ts 2>/dev/null; then
    echo "Already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/project/vcs.ts b/packages/opencode/src/project/vcs.ts
index 1c595f7f146..25f172b8a80 100644
--- a/packages/opencode/src/project/vcs.ts
+++ b/packages/opencode/src/project/vcs.ts
@@ -1,12 +1,12 @@
 import { Effect, Layer, ServiceMap, Stream } from "effect"
+import { ChildProcess, ChildProcessSpawner } from "effect/unstable/process"
 import { Bus } from "@/bus"
 import { BusEvent } from "@/bus/bus-event"
+import * as CrossSpawnSpawner from "@/effect/cross-spawn-spawner"
 import { InstanceState } from "@/effect/instance-state"
 import { makeRuntime } from "@/effect/run-service"
 import { FileWatcher } from "@/file/watcher"
 import { Log } from "@/util/log"
-import { git } from "@/util/git"
-import { Instance } from "./instance"
 import z from "zod"

 export namespace Vcs {
@@ -41,10 +41,25 @@ export namespace Vcs {

   export class Service extends ServiceMap.Service<Service, Interface>()("@opencode/Vcs") {}

-  export const layer: Layer.Layer<Service, never, Bus.Service> = Layer.effect(
+  export const layer: Layer.Layer<Service, never, Bus.Service | ChildProcessSpawner.ChildProcessSpawner> = Layer.effect(
     Service,
     Effect.gen(function* () {
       const bus = yield* Bus.Service
+      const spawner = yield* ChildProcessSpawner.ChildProcessSpawner
+
+      const git = Effect.fnUntraced(
+        function* (args: string[], opts: { cwd: string }) {
+          const handle = yield* spawner.spawn(
+            ChildProcess.make("git", args, { cwd: opts.cwd, extendEnv: true, stdin: "ignore" }),
+          )
+          const text = yield* Stream.mkString(Stream.decodeText(handle.stdout))
+          const code = yield* handle.exitCode
+          return { code, text }
+        },
+        Effect.scoped,
+        Effect.catch(() => Effect.succeed({ code: ChildProcessSpawner.ExitCode(1), text: "" })),
+      )
+
       const state = yield* InstanceState.make<State>(
         Effect.fn("Vcs.state")((ctx) =>
           Effect.gen(function* () {
@@ -52,17 +67,15 @@ export namespace Vcs {
               return { current: undefined }
             }

-            const get = async () => {
-              const result = await git(["rev-parse", "--abbrev-ref", "HEAD"], {
-                cwd: ctx.worktree,
-              })
-              if (result.exitCode !== 0) return undefined
-              const text = result.text().trim()
+            const getBranch = Effect.fnUntraced(function* () {
+              const result = yield* git(["rev-parse", "--abbrev-ref", "HEAD"], { cwd: ctx.worktree })
+              if (result.code !== 0) return undefined
+              const text = result.text.trim()
               return text || undefined
-            }
+            })

             const value = {
-              current: yield* Effect.promise(() => get()),
+              current: yield* getBranch(),
             }
             log.info("initialized", { branch: value.current })

@@ -70,7 +83,7 @@ export namespace Vcs {
               Stream.filter((evt) => evt.properties.file.endsWith("HEAD")),
               Stream.runForEach(() =>
                 Effect.gen(function* () {
-                  const next = yield* Effect.promise(() => get())
+                  const next = yield* getBranch()
                   if (next !== value.current) {
                     log.info("branch changed", { from: value.current, to: next })
                     value.current = next
@@ -97,7 +110,7 @@ export namespace Vcs {
     }),
   )

-  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer))
+  export const defaultLayer = layer.pipe(Layer.provide(Bus.layer), Layer.provide(CrossSpawnSpawner.defaultLayer))

   const { runPromise } = makeRuntime(Service, defaultLayer)

PATCH

echo "Patch applied successfully."
