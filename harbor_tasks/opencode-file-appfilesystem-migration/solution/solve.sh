#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check: if AppFileSystem is already imported in file/index.ts, skip
if grep -q 'import { AppFileSystem }' packages/opencode/src/file/index.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/file/index.ts b/packages/opencode/src/file/index.ts
index e70141e8dcc..fec1b4bc935 100644
--- a/packages/opencode/src/file/index.ts
+++ b/packages/opencode/src/file/index.ts
@@ -1,6 +1,7 @@
 import { BusEvent } from "@/bus/bus-event"
 import { InstanceState } from "@/effect/instance-state"
 import { makeRuntime } from "@/effect/run-service"
+import { AppFileSystem } from "@/filesystem"
 import { git } from "@/util/git"
 import { Effect, Layer, ServiceMap } from "effect"
 import { formatPatch, structuredPatch } from "diff"
@@ -343,6 +344,8 @@ export namespace File {
   export const layer = Layer.effect(
     Service,
     Effect.gen(function* () {
+      const appFs = yield* AppFileSystem.Service
+
       const state = yield* InstanceState.make<State>(
         Effect.fn("File.state")(() =>
           Effect.succeed({
@@ -512,57 +515,54 @@ export namespace File {
       })

       const read = Effect.fn("File.read")(function* (file: string) {
-        return yield* Effect.promise(async (): Promise<File.Content> => {
-          using _ = log.time("read", { file })
-          const full = path.join(Instance.directory, file)
+        using _ = log.time("read", { file })
+        const full = path.join(Instance.directory, file)

-          if (!Instance.containsPath(full)) {
-            throw new Error("Access denied: path escapes project directory")
-          }
+        if (!Instance.containsPath(full)) throw new Error("Access denied: path escapes project directory")

-          if (isImageByExtension(file)) {
-            if (await Filesystem.exists(full)) {
-              const buffer = await Filesystem.readBytes(full).catch(() => Buffer.from([]))
-              return {
-                type: "text",
-                content: buffer.toString("base64"),
-                mimeType: getImageMimeType(file),
-                encoding: "base64",
-              }
+        if (isImageByExtension(file)) {
+          const exists = yield* appFs.existsSafe(full)
+          if (exists) {
+            const bytes = yield* appFs.readFile(full).pipe(Effect.catch(() => Effect.succeed(new Uint8Array())))
+            return {
+              type: "text" as const,
+              content: Buffer.from(bytes).toString("base64"),
+              mimeType: getImageMimeType(file),
+              encoding: "base64" as const,
             }
-            return { type: "text", content: "" }
           }
+          return { type: "text" as const, content: "" }
+        }

-          const knownText = isTextByExtension(file) || isTextByName(file)
+        const knownText = isTextByExtension(file) || isTextByName(file)

-          if (isBinaryByExtension(file) && !knownText) {
-            return { type: "binary", content: "" }
-          }
+        if (isBinaryByExtension(file) && !knownText) return { type: "binary" as const, content: "" }

-          if (!(await Filesystem.exists(full))) {
-            return { type: "text", content: "" }
-          }
+        const exists = yield* appFs.existsSafe(full)
+        if (!exists) return { type: "text" as const, content: "" }

-          const mimeType = Filesystem.mimeType(full)
-          const encode = knownText ? false : shouldEncode(mimeType)
+        const mimeType = Filesystem.mimeType(full)
+        const encode = knownText ? false : shouldEncode(mimeType)

-          if (encode && !isImage(mimeType)) {
-            return { type: "binary", content: "", mimeType }
-          }
+        if (encode && !isImage(mimeType)) return { type: "binary" as const, content: "", mimeType }

-          if (encode) {
-            const buffer = await Filesystem.readBytes(full).catch(() => Buffer.from([]))
-            return {
-              type: "text",
-              content: buffer.toString("base64"),
-              mimeType,
-              encoding: "base64",
-            }
+        if (encode) {
+          const bytes = yield* appFs.readFile(full).pipe(Effect.catch(() => Effect.succeed(new Uint8Array())))
+          return {
+            type: "text" as const,
+            content: Buffer.from(bytes).toString("base64"),
+            mimeType,
+            encoding: "base64" as const,
           }
+        }

-          const content = (await Filesystem.readText(full).catch(() => "")).trim()
+        const content = yield* appFs.readFileString(full).pipe(
+          Effect.map((s) => s.trim()),
+          Effect.catch(() => Effect.succeed("")),
+        )

-          if (Instance.project.vcs === "git") {
+        if (Instance.project.vcs === "git") {
+          return yield* Effect.promise(async (): Promise<File.Content> => {
             let diff = (
               await git(["-c", "core.fsmonitor=false", "diff", "--", file], { cwd: Instance.directory })
             ).text()
@@ -579,60 +579,51 @@ export namespace File {
                 context: Infinity,
                 ignoreWhitespace: true,
               })
-              return {
-                type: "text",
-                content,
-                patch,
-                diff: formatPatch(patch),
-              }
+              return { type: "text", content, patch, diff: formatPatch(patch) }
             }
-          }
+            return { type: "text", content }
+          })
+        }

-          return { type: "text", content }
-        })
+        return { type: "text" as const, content }
       })

       const list = Effect.fn("File.list")(function* (dir?: string) {
-        return yield* Effect.promise(async () => {
-          const exclude = [".git", ".DS_Store"]
-          let ignored = (_: string) => false
-          if (Instance.project.vcs === "git") {
-            const ig = ignore()
-            const gitignore = path.join(Instance.project.worktree, ".gitignore")
-            if (await Filesystem.exists(gitignore)) {
-              ig.add(await Filesystem.readText(gitignore))
-            }
-            const ignoreFile = path.join(Instance.project.worktree, ".ignore")
-            if (await Filesystem.exists(ignoreFile)) {
-              ig.add(await Filesystem.readText(ignoreFile))
-            }
-            ignored = ig.ignores.bind(ig)
-          }
-
-          const resolved = dir ? path.join(Instance.directory, dir) : Instance.directory
-          if (!Instance.containsPath(resolved)) {
-            throw new Error("Access denied: path escapes project directory")
-          }
-
-          const nodes: File.Node[] = []
-          for (const entry of await fs.promises.readdir(resolved, { withFileTypes: true }).catch(() => [])) {
-            if (exclude.includes(entry.name)) continue
-            const absolute = path.join(resolved, entry.name)
-            const file = path.relative(Instance.directory, absolute)
-            const type = entry.isDirectory() ? "directory" : "file"
-            nodes.push({
-              name: entry.name,
-              path: file,
-              absolute,
-              type,
-              ignored: ignored(type === "directory" ? file + "/" : file),
-            })
-          }
-
-          return nodes.sort((a, b) => {
-            if (a.type !== b.type) return a.type === "directory" ? -1 : 1
-            return a.name.localeCompare(b.name)
+        const exclude = [".git", ".DS_Store"]
+        let ignored = (_: string) => false
+        if (Instance.project.vcs === "git") {
+          const ig = ignore()
+          const gitignore = path.join(Instance.project.worktree, ".gitignore")
+          const gitignoreText = yield* appFs.readFileString(gitignore).pipe(Effect.catch(() => Effect.succeed("")))
+          if (gitignoreText) ig.add(gitignoreText)
+          const ignoreFile = path.join(Instance.project.worktree, ".ignore")
+          const ignoreText = yield* appFs.readFileString(ignoreFile).pipe(Effect.catch(() => Effect.succeed("")))
+          if (ignoreText) ig.add(ignoreText)
+          ignored = ig.ignores.bind(ig)
+        }
+
+        const resolved = dir ? path.join(Instance.directory, dir) : Instance.directory
+        if (!Instance.containsPath(resolved)) throw new Error("Access denied: path escapes project directory")
+
+        const entries = yield* appFs.readDirectoryEntries(resolved).pipe(Effect.orElseSucceed(() => []))
+
+        const nodes: File.Node[] = []
+        for (const entry of entries) {
+          if (exclude.includes(entry.name)) continue
+          const absolute = path.join(resolved, entry.name)
+          const file = path.relative(Instance.directory, absolute)
+          const type = entry.type === "directory" ? "directory" : "file"
+          nodes.push({
+            name: entry.name,
+            path: file,
+            absolute,
+            type,
+            ignored: ignored(type === "directory" ? file + "/" : file),
           })
+        }
+        return nodes.sort((a, b) => {
+          if (a.type !== b.type) return a.type === "directory" ? -1 : 1
+          return a.name.localeCompare(b.name)
         })
       })

@@ -676,7 +667,9 @@ export namespace File {
     }),
   )

-  const { runPromise } = makeRuntime(Service, layer)
+  export const defaultLayer = layer.pipe(Layer.provide(AppFileSystem.defaultLayer))
+
+  const { runPromise } = makeRuntime(Service, defaultLayer)

   export function init() {
     return runPromise((svc) => svc.init())
diff --git a/packages/opencode/src/filesystem/index.ts b/packages/opencode/src/filesystem/index.ts
index d8f7d6053e7..6bc02ccce3a 100644
--- a/packages/opencode/src/filesystem/index.ts
+++ b/packages/opencode/src/filesystem/index.ts
@@ -1,6 +1,7 @@
 import { NodeFileSystem } from "@effect/platform-node"
 import { dirname, join, relative, resolve as pathResolve } from "path"
 import { realpathSync } from "fs"
+import * as NFS from "fs/promises"
 import { lookup } from "mime-types"
 import { Effect, FileSystem, Layer, Schema, ServiceMap } from "effect"
 import type { PlatformError } from "effect/PlatformError"
@@ -14,13 +15,20 @@ export namespace AppFileSystem {

   export type Error = PlatformError | FileSystemError

+  export interface DirEntry {
+    readonly name: string
+    readonly type: "file" | "directory" | "symlink" | "other"
+  }
+
   export interface Interface extends FileSystem.FileSystem {
-    readonly isDir: (path: string) => Effect.Effect<boolean, Error>
-    readonly isFile: (path: string) => Effect.Effect<boolean, Error>
+    readonly isDir: (path: string) => Effect.Effect<boolean>
+    readonly isFile: (path: string) => Effect.Effect<boolean>
+    readonly existsSafe: (path: string) => Effect.Effect<boolean>
     readonly readJson: (path: string) => Effect.Effect<unknown, Error>
     readonly writeJson: (path: string, data: unknown, mode?: number) => Effect.Effect<void, Error>
     readonly ensureDir: (path: string) => Effect.Effect<void, Error>
     readonly writeWithDirs: (path: string, content: string | Uint8Array, mode?: number) => Effect.Effect<void, Error>
+    readonly readDirectoryEntries: (path: string) => Effect.Effect<DirEntry[], Error>
     readonly findUp: (target: string, start: string, stop?: string) => Effect.Effect<string[], Error>
     readonly up: (options: { targets: string[]; start: string; stop?: string }) => Effect.Effect<string[], Error>
     readonly globUp: (pattern: string, start: string, stop?: string) => Effect.Effect<string[], Error>
@@ -35,6 +43,10 @@ export namespace AppFileSystem {
     Effect.gen(function* () {
       const fs = yield* FileSystem.FileSystem

+      const existsSafe = Effect.fn("FileSystem.existsSafe")(function* (path: string) {
+        return yield* fs.exists(path).pipe(Effect.orElseSucceed(() => false))
+      })
+
       const isDir = Effect.fn("FileSystem.isDir")(function* (path: string) {
         const info = yield* fs.stat(path).pipe(Effect.catch(() => Effect.void))
         return info?.type === "Directory"
@@ -45,6 +57,19 @@ export namespace AppFileSystem {
         return info?.type === "File"
       })

+      const readDirectoryEntries = Effect.fn("FileSystem.readDirectoryEntries")(function* (dirPath: string) {
+        return yield* Effect.tryPromise({
+          try: async () => {
+            const entries = await NFS.readdir(dirPath, { withFileTypes: true })
+            return entries.map((e): DirEntry => ({
+              name: e.name,
+              type: e.isDirectory() ? "directory" : e.isSymbolicLink() ? "symlink" : e.isFile() ? "file" : "other",
+            }))
+          },
+          catch: (cause) => new FileSystemError({ method: "readDirectoryEntries", cause }),
+        })
+      })
+
       const readJson = Effect.fn("FileSystem.readJson")(function* (path: string) {
         const text = yield* fs.readFileString(path)
         return JSON.parse(text)
@@ -135,8 +160,10 @@ export namespace AppFileSystem {

       return Service.of({
         ...fs,
+        existsSafe,
         isDir,
         isFile,
+        readDirectoryEntries,
         readJson,
         writeJson,
         ensureDir,
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
