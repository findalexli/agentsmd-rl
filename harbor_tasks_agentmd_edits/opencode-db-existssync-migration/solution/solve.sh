#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (checking for existsSync import)
if grep -q 'existsSync' packages/opencode/src/storage/db.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/.opencode/skill/bun-file-io/SKILL.md b/.opencode/skill/bun-file-io/SKILL.md
deleted file mode 100644
index f78de330943e..000000000000
--- a/.opencode/skill/bun-file-io/SKILL.md
+++ /dev/null
@@ -1,42 +0,0 @@
----
-name: bun-file-io
description: Use this when you are working on file operations like reading, writing, scanning, or deleting files. It summarizes the preferred file APIs and patterns used in this repo. It also notes when to use filesystem helpers for directories.
----
-
-## Use this when
-
-- Editing file I/O or scans in `packages/opencode`
-- Handling directory operations or external tools
-
-## Bun file APIs (from Bun docs)
-
-- `Bun.file(path)` is lazy; call `text`, `json`, `stream`, `arrayBuffer`, `bytes`, `exists` to read.
-- Metadata: `file.size`, `file.type`, `file.name`.
-- `Bun.write(dest, input)` writes strings, buffers, Blobs, Responses, or files.
-- `Bun.file(...).delete()` deletes a file.
-- `file.writer()` returns a FileSink for incremental writes.
-- `Bun.Glob` + `Array.fromAsync(glob.scan({ cwd, absolute, onlyFiles, dot }))` for scans.
-- Use `Bun.which` to find a binary, then `Bun.spawn` to run it.
-- `Bun.readableStreamToText/Bytes/JSON` for stream output.
-
-## When to use node:fs
-
-- Use `node:fs/promises` for directories (`mkdir`, `readdir`, recursive operations).
-
-## Repo patterns
-
-- Prefer Bun APIs over Node `fs` for file access.
-- Check `Bun.file(...).exists()` before reading.
-- For binary/large files use `arrayBuffer()` and MIME checks via `file.type`.
-- Use `Bun.Glob` + `Array.fromAsync` for scans.
-- Decode tool stderr with `Bun.readableStreamToText`.
-- For large writes, use `Bun.write(Bun.file(path), text)`.
-
-NOTE: Bun.file(...).exists() will return `false` if the value is a directory.
-Use Filesystem.exists(...) instead if path can be file or directory
-
-## Quick checklist
-
-- Use Bun APIs first.
-- Use `path.join`/`path.resolve` for paths.
-- Prefer promise `.catch(...)` over `try/catch` when possible.
diff --git a/packages/opencode/src/storage/db.ts b/packages/opencode/src/storage/db.ts
index 0974cbe7be44..6d7bfd728102 100644
--- a/packages/opencode/src/storage/db.ts
+++ b/packages/opencode/src/storage/db.ts
@@ -10,7 +10,7 @@ import { Log } from "../util/log"
 import { NamedError } from "@opencode-ai/util/error"
 import z from "zod"
 import path from "path"
-import { readFileSync, readdirSync } from "fs"
+import { readFileSync, readdirSync, existsSync } from "fs"
 import * as schema from "./schema"

 declare const OPENCODE_MIGRATIONS: { sql: string; timestamp: number }[] | undefined
@@ -54,7 +54,7 @@ export namespace Database {
     const sql = dirs
       .map((name) => {
         const file = path.join(dir, name, "migration.sql")
-        if (!Bun.file(file).size) return
+        if (!existsSync(file)) return
         return {
           sql: readFileSync(file, "utf-8"),
           timestamp: time(name),

PATCH

echo "Patch applied successfully."
