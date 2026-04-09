#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'existsSync(file)' packages/opencode/src/storage/db.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix for packages/opencode/src/storage/db.ts
git apply - <<'PATCH'
diff --git a/packages/opencode/src/storage/db.ts b/packages/opencode/src/storage/db.ts
index 6fb4f2a7a..a8347c376 100644
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

# Remove the SKILL.md file
rm -f .opencode/skill/bun-file-io/SKILL.md

# Also remove the empty directory if it exists
rmdir .opencode/skill/bun-file-io 2>/dev/null || true

echo "Patch applied successfully."
