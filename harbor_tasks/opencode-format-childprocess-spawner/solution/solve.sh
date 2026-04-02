#!/usr/bin/env bash
set -euo pipefail

REPO="/workspace/opencode"
FORMAT_TS="$REPO/packages/opencode/src/format/index.ts"

# Idempotency: check if already applied
if grep -q 'ChildProcessSpawner' "$FORMAT_TS" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd "$REPO"

git apply - <<'PATCH'
diff --git a/packages/opencode/specs/effect-migration.md b/packages/opencode/specs/effect-migration.md
index f4acc6e52e0..93b9cf8fb92 100644
--- a/packages/opencode/specs/effect-migration.md
+++ b/packages/opencode/specs/effect-migration.md
@@ -212,8 +212,81 @@ Fully migrated (single namespace, InstanceState where needed, flattened facade):

 Still open and likely worth migrating:

-- [ ] `Session`
-- [ ] `SessionProcessor`
-- [ ] `SessionPrompt`
-- [ ] `SessionCompaction`
-- [ ] `Provider`
+- [x] `Session` — `session/index.ts`
+- [ ] `SessionProcessor` — blocked by AI SDK v6 PR (#18433)
+- [ ] `SessionPrompt` — blocked by AI SDK v6 PR (#18433)
+- [ ] `SessionCompaction` — blocked by AI SDK v6 PR (#18433)
+- [ ] `Provider` — blocked by AI SDK v6 PR (#18433)
+
+Other services not yet migrated:
+
+- [ ] `SessionSummary` — `session/summary.ts`
+- [ ] `SessionTodo` — `session/todo.ts`
+- [ ] `SessionRevert` — `session/revert.ts`
+- [ ] `Instruction` — `session/instruction.ts`
+- [ ] `ShareNext` — `share/share-next.ts`
+- [ ] `SyncEvent` — `sync/index.ts`
+- [ ] `Storage` — `storage/storage.ts`
+- [ ] `Workspace` — `control-plane/workspace.ts`
+
+## Tool interface → Effect
+
+Once individual tools are effectified, change `Tool.Info` (`tool/tool.ts`) so `init` and `execute` return `Effect` instead of `Promise`. This lets tool implementations compose natively with the Effect pipeline rather than being wrapped in `Effect.promise()` at the call site. Requires:
+
+1. Migrate each tool to return Effects
+2. Update `Tool.define()` factory to work with Effects
+3. Update `SessionPrompt` to `yield*` tool results instead of `await`ing — blocked by AI SDK v6 PR (#18433)
+
+Individual tools, ordered by value:
+
+- [ ] `apply_patch.ts` — HIGH: multi-step orchestration, error accumulation, Bus events
+- [ ] `read.ts` — HIGH: streaming I/O, readline, binary detection → FileSystem + Stream
+- [ ] `edit.ts` — HIGH: multi-step diff/format/publish pipeline, FileWatcher lock
+- [ ] `grep.ts` — MEDIUM: spawns ripgrep → ChildProcessSpawner, timeout handling
+- [ ] `write.ts` — MEDIUM: permission checks, diagnostics polling, Bus events
+- [ ] `codesearch.ts` — MEDIUM: HTTP + SSE + manual timeout → HttpClient + Effect.timeout
+- [ ] `webfetch.ts` — MEDIUM: fetch with UA retry, size limits → HttpClient
+- [ ] `websearch.ts` — MEDIUM: MCP over HTTP → HttpClient
+- [ ] `batch.ts` — MEDIUM: parallel execution, per-call error recovery → Effect.all
+- [ ] `task.ts` — MEDIUM: task state management
+- [ ] `glob.ts` — LOW: simple async generator
+- [ ] `lsp.ts` — LOW: dispatch switch over LSP operations
+- [ ] `skill.ts` — LOW: skill tool adapter
+- [ ] `plan.ts` — LOW: plan file operations
+
+## Effect service adoption in already-migrated code
+
+Some services are effectified but still use raw `Filesystem.*` or `Process.spawn` instead of the Effect equivalents. These are low-hanging fruit — the layers already exist, they just need the dependency swap.
+
+### `Filesystem.*` → `AppFileSystem.Service` (yield in layer)
+
+- [ ] `file/index.ts` — 11 calls (the File service itself)
+- [ ] `config/config.ts` — 7 calls
+- [ ] `auth/index.ts` — 3 calls
+- [ ] `skill/index.ts` — 3 calls
+- [ ] `file/time.ts` — 1 call
+
+### `Process.spawn` → `ChildProcessSpawner` (yield in layer)
+
+- [ ] `format/index.ts` — 1 call
+
+## Filesystem consolidation
+
+`util/filesystem.ts` (raw fs wrapper) is used by **64 files**. The effectified `AppFileSystem` service (`filesystem/index.ts`) exists but only has **8 consumers**. As services and tools are effectified, they should switch from `Filesystem.*` to yielding `AppFileSystem.Service` — this happens naturally during each migration, not as a separate effort.
+
+Similarly, **28 files** still import raw `fs` or `fs/promises` directly. These should migrate to `AppFileSystem` or `Filesystem.*` as they're touched.
+
+Current raw fs users that will convert during tool migration:
+- `tool/read.ts` — fs.createReadStream, readline
+- `tool/apply_patch.ts` — fs/promises
+- `tool/bash.ts` — fs/promises
+- `file/ripgrep.ts` — fs/promises
+- `storage/storage.ts` — fs/promises
+- `patch/index.ts` — fs, fs/promises
+
+## Primitives & utilities
+
+- [ ] `util/lock.ts` — reader-writer lock → Effect Semaphore/Permit
+- [ ] `util/flock.ts` — file-based distributed lock with heartbeat → Effect.repeat + addFinalizer
+- [ ] `util/process.ts` — child process spawn wrapper → return Effect instead of Promise
+- [ ] `util/lazy.ts` — replace uses in Effect code with Effect.cached; keep for sync-only code
diff --git a/packages/opencode/src/format/index.ts b/packages/opencode/src/format/index.ts
index 314e8c6e71c..47b7d76b770 100644
--- a/packages/opencode/src/format/index.ts
+++ b/packages/opencode/src/format/index.ts
@@ -1,4 +1,6 @@
 import { Effect, Layer, ServiceMap } from "effect"
+import { ChildProcess, ChildProcessSpawner } from "effect/unstable/process"
+import * as CrossSpawnSpawner from "@/effect/cross-spawn-spawner"
 import { InstanceState } from "@/effect/instance-state"
 import { makeRuntime } from "@/effect/run-service"
 import path from "path"
@@ -6,7 +8,6 @@ import { mergeDeep } from "remeda"
 import z from "zod"
 import { Config } from "../config/config"
 import { Instance } from "../project/instance"
-import { Process } from "../util/process"
 import { Log } from "../util/log"
 import * as Formatter from "./formatter"

@@ -36,6 +37,7 @@ export namespace Format {
     Service,
     Effect.gen(function* () {
       const config = yield* Config.Service
+      const spawner = yield* ChildProcessSpawner.ChildProcessSpawner

       const state = yield* InstanceState.make(
         Effect.fn("Format.state")(function* (_ctx) {
@@ -98,38 +100,45 @@ export namespace Format {
             return checks.filter((x) => x.enabled).map((x) => x.item)
           }

-          async function formatFile(filepath: string) {
-            log.info("formatting", { file: filepath })
-            const ext = path.extname(filepath)
-
-            for (const item of await getFormatter(ext)) {
-              log.info("running", { command: item.command })
-              try {
-                const proc = Process.spawn(
-                  item.command.map((x) => x.replace("$FILE", filepath)),
-                  {
-                    cwd: Instance.directory,
-                    env: { ...process.env, ...item.environment },
-                    stdout: "ignore",
-                    stderr: "ignore",
-                  },
-                )
-                const exit = await proc.exited
-                if (exit !== 0) {
+          function formatFile(filepath: string) {
+            return Effect.gen(function* () {
+              log.info("formatting", { file: filepath })
+              const ext = path.extname(filepath)
+
+              for (const item of yield* Effect.promise(() => getFormatter(ext))) {
+                log.info("running", { command: item.command })
+                const cmd = item.command.map((x) => x.replace("$FILE", filepath))
+                const code = yield* spawner
+                  .spawn(
+                    ChildProcess.make(cmd[0]!, cmd.slice(1), {
+                      cwd: Instance.directory,
+                      env: item.environment,
+                      extendEnv: true,
+                    }),
+                  )
+                  .pipe(
+                    Effect.flatMap((handle) => handle.exitCode),
+                    Effect.scoped,
+                    Effect.catch(() =>
+                      Effect.sync(() => {
+                        log.error("failed to format file", {
+                          error: "spawn failed",
+                          command: item.command,
+                          ...item.environment,
+                          file: filepath,
+                        })
+                        return ChildProcessSpawner.ExitCode(1)
+                      }),
+                    ),
+                  )
+                if (code !== 0) {
                   log.error("failed", {
                     command: item.command,
                     ...item.environment,
                   })
                 }
-              } catch (error) {
-                log.error("failed to format file", {
-                  error,
-                  command: item.command,
-                  ...item.environment,
-                  file: filepath,
-                })
               }
-            }
+            })
           }

           log.info("init")
@@ -162,14 +171,14 @@ export namespace Format {

       const file = Effect.fn("Format.file")(function* (filepath: string) {
         const { formatFile } = yield* InstanceState.get(state)
-        yield* Effect.promise(() => formatFile(filepath))
+        yield* formatFile(filepath)
       })

       return Service.of({ init, status, file })
     }),
   )

-  export const defaultLayer = layer.pipe(Layer.provide(Config.defaultLayer))
+  export const defaultLayer = layer.pipe(Layer.provide(Config.defaultLayer), Layer.provide(CrossSpawnSpawner.defaultLayer))

   const { runPromise } = makeRuntime(Service, defaultLayer)

diff --git a/packages/opencode/test/format/format.test.ts b/packages/opencode/test/format/format.test.ts
index 6a9b4f5edac..74336e02a39 100644
--- a/packages/opencode/test/format/format.test.ts
+++ b/packages/opencode/test/format/format.test.ts
@@ -1,17 +1,13 @@
-import { NodeChildProcessSpawner, NodeFileSystem, NodePath } from "@effect/platform-node"
+import { NodeFileSystem } from "@effect/platform-node"
 import { describe, expect } from "bun:test"
 import { Effect, Layer } from "effect"
 import { provideTmpdirInstance } from "../fixture/fixture"
 import { testEffect } from "../lib/effect"
+import * as CrossSpawnSpawner from "../../src/effect/cross-spawn-spawner"
 import { Format } from "../../src/format"
-import { Config } from "../../src/config/config"
 import * as Formatter from "../../src/format/formatter"

-const node = NodeChildProcessSpawner.layer.pipe(
-  Layer.provideMerge(Layer.mergeAll(NodeFileSystem.layer, NodePath.layer)),
-)
-
-const it = testEffect(Layer.mergeAll(Format.layer, node).pipe(Layer.provide(Config.defaultLayer)))
+const it = testEffect(Layer.mergeAll(Format.defaultLayer, CrossSpawnSpawner.defaultLayer, NodeFileSystem.layer))

 describe("Format", () => {
   it.effect("status() returns built-in formatters when no config overrides", () =>

PATCH

echo "Patch applied successfully."
