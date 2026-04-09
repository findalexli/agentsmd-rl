#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q '@opencode/FileWatcher' packages/opencode/src/file/watcher.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/opencode/AGENTS.md b/packages/opencode/AGENTS.md
index 930297baa9f2..f281506220e0 100644
--- a/packages/opencode/AGENTS.md
+++ b/packages/opencode/AGENTS.md
@@ -34,6 +34,7 @@ Instructions to follow when writing Effect.
 - Use `Effect.gen(function* () { ... })` for composition.
 - Use `Effect.fn("ServiceName.method")` for named/traced effects and `Effect.fnUntraced` for internal helpers.
 - `Effect.fn` / `Effect.fnUntraced` accept pipeable operators as extra arguments, so avoid unnecessary `flow` or outer `.pipe()` wrappers.
+- **`Effect.callback`** (not `Effect.async`) for callback-based APIs. The classic `Effect.async` was renamed to `Effect.callback` in effect-smol/v4.

 ## Time

@@ -42,3 +43,37 @@ Instructions to follow when writing Effect.
 ## Errors

 - In `Effect.gen/fn`, prefer `yield* new MyError(...)` over `yield* Effect.fail(new MyError(...))` for direct early-failure branches.
+
+## Instance-scoped Effect services
+
+Services that need per-directory lifecycle (created/destroyed per instance) go through the `Instances` LayerMap:
+
+1. Define a `ServiceMap.Service` with a `static readonly layer` (see `FileWatcherService`, `QuestionService`, `PermissionService`, `ProviderAuthService`).
+2. Add it to `InstanceServices` union and `Layer.mergeAll(...)` in `src/effect/instances.ts`.
+3. Use `InstanceContext` inside the layer to read `directory` and `project` instead of `Instance.*` globals.
+4. Call from legacy code via `runPromiseInstance(MyService.use((s) => s.method()))`.
+
+### Instance.bind — ALS context for native callbacks
+
+`Instance.bind(fn)` captures the current Instance AsyncLocalStorage context and returns a wrapper that restores it synchronously when called.
+
+**Use it** when passing callbacks to native C/C++ addons (`@parcel/watcher`, `node-pty`, native `fs.watch`, etc.) that need to call `Bus.publish`, `Instance.state()`, or anything that reads `Instance.directory`.
+
+**Don't need it** for `setTimeout`, `Promise.then`, `EventEmitter.on`, or Effect fibers — Node.js ALS propagates through those automatically.
+
+```typescript
+// Native addon callback — needs Instance.bind
+const cb = Instance.bind((err, evts) => {
+  Bus.publish(MyEvent, { ... })
+})
+nativeAddon.subscribe(dir, cb)
+```
+
+## Flag → Effect.Config migration
+
+Flags in `src/flag/flag.ts` are being migrated from static `truthy(...)` reads to `Config.boolean(...).pipe(Config.withDefault(false))` as their consumers get effectified.
+
+- Effectful flags return `Config<boolean>` and are read with `yield*` inside `Effect.gen`.
+- The default `ConfigProvider` reads from `process.env`, so env vars keep working.
+- Tests can override via `ConfigProvider.layer(ConfigProvider.fromUnknown({ ... }))`.
+- Keep all flags in `flag.ts` as the single registry — just change the implementation from `truthy()` to `Config.boolean()` when the consumer moves to Effect.
diff --git a/packages/opencode/src/effect/instances.ts b/packages/opencode/src/effect/instances.ts
index 02d4bf48236f..d60d7935589a 100644
--- a/packages/opencode/src/effect/instances.ts
+++ b/packages/opencode/src/effect/instances.ts
@@ -3,6 +3,7 @@ import { registerDisposer } from "./instance-registry"
 import { ProviderAuthService } from "@/provider/auth-service"
 import { QuestionService } from "@/question/service"
 import { PermissionService } from "@/permission/service"
+import { FileWatcherService } from "@/file/watcher"
 import { Instance } from "@/project/instance"
 import type { Project } from "@/project/project"

@@ -17,7 +18,7 @@ export class InstanceContext extends ServiceMap.Service<InstanceContext, Instanc
   "opencode/InstanceContext",
 ) {}

-export type InstanceServices = QuestionService | PermissionService | ProviderAuthService
+export type InstanceServices = QuestionService | PermissionService | ProviderAuthService | FileWatcherService

 function lookup(directory: string) {
   const project = Instance.project
@@ -26,6 +27,7 @@ function lookup(directory: string) {
     Layer.fresh(QuestionService.layer),
     Layer.fresh(PermissionService.layer),
     Layer.fresh(ProviderAuthService.layer),
+    Layer.fresh(FileWatcherService.layer),
   ).pipe(Layer.provide(ctx))
 }

diff --git a/packages/opencode/src/file/watcher.ts b/packages/opencode/src/file/watcher.ts
index 3797c1627021..651f15f8403d 100644
--- a/packages/opencode/src/file/watcher.ts
+++ b/packages/opencode/src/file/watcher.ts
@@ -1,7 +1,8 @@
 import { BusEvent } from "@/bus/bus-event"
 import { Bus } from "@/bus"
+import { InstanceContext } from "@/effect/instances"
+import { Instance } from "@/project/instance"
 import z from "zod"
-import { Instance } from "../project/instance"
 import { Log } from "../util/log"
 import { FileIgnore } from "./ignore"
 import { Config } from "../config/config"
@@ -9,118 +10,139 @@ import path from "path"
 // @ts-ignore
 import { createWrapper } from "@parcel/watcher/wrapper"
 import { lazy } from "@/util/lazy"
-import { withTimeout } from "@/util/timeout"
 import type ParcelWatcher from "@parcel/watcher"
-import { Flag } from "@/flag/flag"
 import { readdir } from "fs/promises"
 import { git } from "@/util/git"
 import { Protected } from "./protected"
+import { Flag } from "@/flag/flag"
+import { Cause, Effect, Layer, ServiceMap } from "effect"

 const SUBSCRIBE_TIMEOUT_MS = 10_000

 declare const OPENCODE_LIBC: string | undefined

+const log = Log.create({ service: "file.watcher" })
+
+const event = {
+  Updated: BusEvent.define(
+    "file.watcher.updated",
+    z.object({
+      file: z.string(),
+      event: z.union([z.literal("add"), z.literal("change"), z.literal("unlink")]),
+    }),
+  ),
+}
+
+const watcher = lazy((): typeof import("@parcel/watcher") | undefined => {
+  try {
+    const binding = require(
+      `@parcel/watcher-${process.platform}-${process.arch}${process.platform === "linux" ? `-${OPENCODE_LIBC || "glibc"}` : ""}`,
+    )
+    return createWrapper(binding) as typeof import("@parcel/watcher")
+  } catch (error) {
+    log.error("failed to load watcher binding", { error })
+    return
+  }
+})
+
+function getBackend() {
+  if (process.platform === "win32") return "windows"
+  if (process.platform === "darwin") return "fs-events"
+  if (process.platform === "linux") return "inotify"
+}
+
 export namespace FileWatcher {
-  const log = Log.create({ service: "file.watcher" })
-
-  export const Event = {
-    Updated: BusEvent.define(
-      "file.watcher.updated",
-      z.object({
-        file: z.string(),
-        event: z.union([z.literal("add"), z.literal("change"), z.literal("unlink")]),
-      }),
-    ),
+  export const Event = event
+  /** Whether the native @parcel/watcher binding is available on this platform. */
+  export const hasNativeBinding = () => !!watcher()
+}
+
+const init = Effect.fn("FileWatcherService.init")(function* () {})
+
+export namespace FileWatcherService {
+  export interface Service {
+    readonly init: () => Effect.Effect<void>
   }
+}
+
+export class FileWatcherService extends ServiceMap.Service<FileWatcherService, FileWatcherService.Service>()(
+  "@opencode/FileWatcher",
+) {
+  static readonly layer = Layer.effect(
+    FileWatcherService,
+    Effect.gen(function* () {
+      const instance = yield* InstanceContext
+      if (yield* Flag.OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER) return FileWatcherService.of({ init })

-  const watcher = lazy((): typeof import("@parcel/watcher") | undefined => {
-    try {
-      const binding = require(
-        `@parcel/watcher-${process.platform}-${process.arch}${process.platform === "linux" ? `-${OPENCODE_LIBC || "glibc"}` : ""}`,
-      )
-      return createWrapper(binding) as typeof import("@parcel/watcher")
-    } catch (error) {
-      log.error("failed to load watcher binding", { error })
-      return
-    }
-  })
-
-  const state = Instance.state(
-    async () => {
-      log.info("init")
-      const cfg = await Config.get()
-      const backend = (() => {
-        if (process.platform === "win32") return "windows"
-        if (process.platform === "darwin") return "fs-events"
-        if (process.platform === "linux") return "inotify"
-      })()
+      log.info("init", { directory: instance.directory })
+
+      const backend = getBackend()
       if (!backend) {
-        log.error("watcher backend not supported", { platform: process.platform })
-        return {}
+        log.error("watcher backend not supported", { directory: instance.directory, platform: process.platform })
+        return FileWatcherService.of({ init })
       }
-      log.info("watcher backend", { platform: process.platform, backend })

       const w = watcher()
-      if (!w) return {}
+      if (!w) return FileWatcherService.of({ init })
+
+      log.info("watcher backend", { directory: instance.directory, platform: process.platform, backend })

-      const subscribe: ParcelWatcher.SubscribeCallback = (err, evts) => {
+      const subs: ParcelWatcher.AsyncSubscription[] = []
+      yield* Effect.addFinalizer(() => Effect.promise(() => Promise.allSettled(subs.map((sub) => sub.unsubscribe()))))
+
+      const cb: ParcelWatcher.SubscribeCallback = Instance.bind((err, evts) => {
         if (err) return
         for (const evt of evts) {
-          if (evt.type === "create") Bus.publish(Event.Updated, { file: evt.path, event: "add" })
-          if (evt.type === "update") Bus.publish(Event.Updated, { file: evt.path, event: "change" })
-          if (evt.type === "delete") Bus.publish(Event.Updated, { file: evt.path, event: "unlink" })
+          if (evt.type === "create") Bus.publish(event.Updated, { file: evt.path, event: "add" })
+          if (evt.type === "update") Bus.publish(event.Updated, { file: evt.path, event: "change" })
+          if (evt.type === "delete") Bus.publish(event.Updated, { file: evt.path, event: "unlink" })
         }
+      })
+
+      const subscribe = (dir: string, ignore: string[]) => {
+        const pending = w.subscribe(dir, cb, { ignore, backend })
+        return Effect.gen(function* () {
+          const sub = yield* Effect.promise(() => pending)
+          subs.push(sub)
+        }).pipe(
+          Effect.timeout(SUBSCRIBE_TIMEOUT_MS),
+          Effect.catchCause((cause) => {
+            log.error("failed to subscribe", { dir, cause: Cause.pretty(cause) })
+            // Clean up a subscription that resolves after timeout
+            pending.then((s) => s.unsubscribe()).catch(() => {})
+            return Effect.void
+          }),
+        )
       }

-      const subs: ParcelWatcher.AsyncSubscription[] = []
+      const cfg = yield* Effect.promise(() => Config.get())
       const cfgIgnores = cfg.watcher?.ignore ?? []

-      if (Flag.OPENCODE_EXPERIMENTAL_FILEWATCHER) {
-        const pending = w.subscribe(Instance.directory, subscribe, {
-          ignore: [...FileIgnore.PATTERNS, ...cfgIgnores, ...Protected.paths()],
-          backend,
-        })
-        const sub = await withTimeout(pending, SUBSCRIBE_TIMEOUT_MS).catch((err) => {
-          log.error("failed to subscribe to Instance.directory", { error: err })
-          pending.then((s) => s.unsubscribe()).catch(() => {})
-          return undefined
-        })
-        if (sub) subs.push(sub)
+      if (yield* Flag.OPENCODE_EXPERIMENTAL_FILEWATCHER) {
+        yield* subscribe(instance.directory, [...FileIgnore.PATTERNS, ...cfgIgnores, ...Protected.paths()])
       }

-      if (Instance.project.vcs === "git") {
-        const result = await git(["rev-parse", "--git-dir"], {
-          cwd: Instance.worktree,
-        })
-        const vcsDir = result.exitCode === 0 ? path.resolve(Instance.worktree, result.text().trim()) : undefined
+      if (instance.project.vcs === "git") {
+        const result = yield* Effect.promise(() =>
+          git(["rev-parse", "--git-dir"], {
+            cwd: instance.project.worktree,
+          }),
+        )
+        const vcsDir = result.exitCode === 0 ? path.resolve(instance.project.worktree, result.text().trim()) : undefined
         if (vcsDir && !cfgIgnores.includes(".git") && !cfgIgnores.includes(vcsDir)) {
-          const gitDirContents = await readdir(vcsDir).catch(() => [])
-          const ignoreList = gitDirContents.filter((entry) => entry !== "HEAD")
-          const pending = w.subscribe(vcsDir, subscribe, {
-            ignore: ignoreList,
-            backend,
-          })
-          const sub = await withTimeout(pending, SUBSCRIBE_TIMEOUT_MS).catch((err) => {
-            log.error("failed to subscribe to vcsDir", { error: err })
-            pending.then((s) => s.unsubscribe()).catch(() => {})
-            return undefined
-          })
-          if (sub) subs.push(sub)
+          const ignore = (yield* Effect.promise(() => readdir(vcsDir).catch(() => []))).filter(
+            (entry) => entry !== "HEAD",
+          )
+          yield* subscribe(vcsDir, ignore)
         }
       }

-      return { subs }
-    },
-    async (state) => {
-      if (!state.subs) return
-      await Promise.all(state.subs.map((sub) => sub?.unsubscribe()))
-    },
+      return FileWatcherService.of({ init })
+    }).pipe(
+      Effect.catchCause((cause) => {
+        log.error("failed to init watcher service", { cause: Cause.pretty(cause) })
+        return Effect.succeed(FileWatcherService.of({ init }))
+      }),
+    ),
   )
-
-  export function init() {
-    if (Flag.OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER) {
-      return
-    }
-    state()
-  }
 }
diff --git a/packages/opencode/src/flag/flag.ts b/packages/opencode/src/flag/flag.ts
index f1688a1b40a9..a1cfd862b7af 100644
--- a/packages/opencode/src/flag/flag.ts
+++ b/packages/opencode/src/flag/flag.ts
@@ -1,3 +1,5 @@
+import { Config } from "effect"
+
 function truthy(key: string) {
   const value = process.env[key]?.toLowerCase()
   return value === "true" || value === "1"
@@ -40,8 +42,12 @@ export namespace Flag {

   // Experimental
   export const OPENCODE_EXPERIMENTAL = truthy("OPENCODE_EXPERIMENTAL")
-  export const OPENCODE_EXPERIMENTAL_FILEWATCHER = truthy("OPENCODE_EXPERIMENTAL_FILEWATCHER")
-  export const OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER = truthy("OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER")
+  export const OPENCODE_EXPERIMENTAL_FILEWATCHER = Config.boolean("OPENCODE_EXPERIMENTAL_FILEWATCHER").pipe(
+    Config.withDefault(false),
+  )
+  export const OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER = Config.boolean(
+    "OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER",
+  ).pipe(Config.withDefault(false))
   export const OPENCODE_EXPERIMENTAL_ICON_DISCOVERY =
     OPENCODE_EXPERIMENTAL || truthy("OPENCODE_EXPERIMENTAL_ICON_DISCOVERY")

diff --git a/packages/opencode/src/project/bootstrap.ts b/packages/opencode/src/project/bootstrap.ts
index a2be3733f853..bd819dc280a1 100644
--- a/packages/opencode/src/project/bootstrap.ts
+++ b/packages/opencode/src/project/bootstrap.ts
@@ -1,7 +1,7 @@
 import { Plugin } from "../plugin"
 import { Format } from "../format"
 import { LSP } from "../lsp"
-import { FileWatcher } from "../file/watcher"
+import { FileWatcherService } from "../file/watcher"
 import { File } from "../file"
 import { Project } from "./project"
 import { Bus } from "../bus"
@@ -12,6 +12,7 @@ import { Log } from "@/util/log"
 import { ShareNext } from "@/share/share-next"
 import { Snapshot } from "../snapshot"
 import { Truncate } from "../tool/truncation"
+import { runPromiseInstance } from "@/effect/runtime"

 export async function InstanceBootstrap() {
   Log.Default.info("bootstrapping", { directory: Instance.directory })
@@ -19,7 +20,7 @@ export async function InstanceBootstrap() {
   ShareNext.init()
   Format.init()
   await LSP.init()
-  FileWatcher.init()
+  await runPromiseInstance(FileWatcherService.use((service) => service.init()))
   File.init()
   Vcs.init()
   Snapshot.init()
diff --git a/packages/opencode/src/project/instance.ts b/packages/opencode/src/project/instance.ts
index fd3cc640a337..c16801a7a120 100644
--- a/packages/opencode/src/project/instance.ts
+++ b/packages/opencode/src/project/instance.ts
@@ -101,6 +101,15 @@ export const Instance = {
     if (Instance.worktree === "/") return false
     return Filesystem.contains(Instance.worktree, filepath)
   },
+  /**
+   * Captures the current instance ALS context and returns a wrapper that
+   * restores it when called. Use this for callbacks that fire outside the
+   * instance async context (native addons, event emitters, timers, etc.).
+   */
+  bind<F extends (...args: any[]) => any>(fn: F): F {
+    const ctx = context.use()
+    return ((...args: any[]) => context.provide(ctx, () => fn(...args))) as F
+  },
   state<S>(init: () => S, dispose?: (state: Awaited<S>) => Promise<void>): () => S {
     return State.create(() => Instance.directory, init, dispose)
   },
diff --git a/packages/opencode/src/pty/index.ts b/packages/opencode/src/pty/index.ts
index d6bc4973a062..7436abec9f57 100644
--- a/packages/opencode/src/pty/index.ts
+++ b/packages/opencode/src/pty/index.ts
@@ -167,40 +167,44 @@ export namespace Pty {
       subscribers: new Map(),
     }
     state().set(id, session)
-    ptyProcess.onData((chunk) => {
-      session.cursor += chunk.length
+    ptyProcess.onData(
+      Instance.bind((chunk) => {
+        session.cursor += chunk.length

-      for (const [key, ws] of session.subscribers.entries()) {
-        if (ws.readyState !== 1) {
-          session.subscribers.delete(key)
-          continue
-        }
+        for (const [key, ws] of session.subscribers.entries()) {
+          if (ws.readyState !== 1) {
+            session.subscribers.delete(key)
+            continue
+          }

-        if (ws.data !== key) {
-          session.subscribers.delete(key)
-          continue
-        }
+          if (ws.data !== key) {
+            session.subscribers.delete(key)
+            continue
+          }

-        try {
-          ws.send(chunk)
-        } catch {
-          session.subscribers.delete(key)
+          try {
+            ws.send(chunk)
+          } catch {
+            session.subscribers.delete(key)
+          }
         }
-      }

-      session.buffer += chunk
-      if (session.buffer.length <= BUFFER_LIMIT) return
-      const excess = session.buffer.length - BUFFER_LIMIT
-      session.buffer = session.buffer.slice(excess)
-      session.bufferCursor += excess
-    })
-    ptyProcess.onExit(({ exitCode }) => {
-      if (session.info.status === "exited") return
-      log.info("session exited", { id, exitCode })
-      session.info.status = "exited"
-      Bus.publish(Event.Exited, { id, exitCode })
-      remove(id)
-    })
+        session.buffer += chunk
+        if (session.buffer.length <= BUFFER_LIMIT) return
+        const excess = session.buffer.length - BUFFER_LIMIT
+        session.buffer = session.buffer.slice(excess)
+        session.bufferCursor += excess
+      }),
+    )
+    ptyProcess.onExit(
+      Instance.bind(({ exitCode }) => {
+        if (session.info.status === "exited") return
+        log.info("session exited", { id, exitCode })
+        session.info.status = "exited"
+        Bus.publish(Event.Exited, { id, exitCode })
+        remove(id)
+      }),
+    )
     Bus.publish(Event.Created, { info })
     return info
   }

PATCH

echo "Patch applied successfully."
