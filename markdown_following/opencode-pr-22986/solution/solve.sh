#!/bin/bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: if the gold patch has already been applied, exit cleanly
if grep -q 'export \* as ConfigFormatter from "\./formatter"' \
   packages/opencode/src/config/formatter.ts 2>/dev/null; then
    echo "solve.sh: gold patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index a7895c831f12..44d08ae955eb 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -14,6 +14,7 @@
 - Use Bun APIs when possible, like `Bun.file()`
 - Rely on type inference when possible; avoid explicit type annotations or interfaces unless necessary for exports or clarity
 - Prefer functional array methods (flatMap, filter, map) over for loops; use type guards on filter to maintain type inference downstream
+- In `src/config`, follow the existing self-export pattern at the top of the file (for example `export * as ConfigAgent from "./agent"`) when adding a new config module.

 Reduce total variable count by inlining when a value is only used once.

diff --git a/packages/opencode/AGENTS.md b/packages/opencode/AGENTS.md
index f0f32fdd164a..761b9b5c5ecf 100644
--- a/packages/opencode/AGENTS.md
+++ b/packages/opencode/AGENTS.md
@@ -23,6 +23,10 @@ See `specs/effect/migration.md` for the compact pattern reference and examples.
 - Use `Effect.callback` for callback-based APIs.
 - Prefer `DateTime.nowAsDate` over `new Date(yield* Clock.currentTimeMillis)` when you need a `Date`.

+## Module conventions
+
+- In `src/config`, follow the existing self-export pattern at the top of the file (for example `export * as ConfigAgent from "./agent"`) when adding a new config module.
+
 ## Schemas and errors

 - Use `Schema.Class` for multi-field data.
diff --git a/packages/opencode/src/config/config.ts b/packages/opencode/src/config/config.ts
index adccb6353b7d..2edc455df32f 100644
--- a/packages/opencode/src/config/config.ts
+++ b/packages/opencode/src/config/config.ts
@@ -12,7 +12,6 @@ import { Auth } from "../auth"
 import { Env } from "../env"
 import { applyEdits, modify } from "jsonc-parser"
 import { Instance, type InstanceContext } from "../project/instance"
-import * as LSPServer from "../lsp/server"
 import { InstallationLocal, InstallationVersion } from "@/installation/version"
 import { existsSync } from "fs"
 import { GlobalBus } from "@/bus/global"
@@ -37,6 +36,8 @@ import { ConfigPermission } from "./permission"
 import { ConfigProvider } from "./provider"
 import { ConfigSkills } from "./skills"
 import { ConfigPaths } from "./paths"
+import { ConfigFormatter } from "./formatter"
+import { ConfigLSP } from "./lsp"

 const log = Log.create({ service: "config" })

@@ -186,56 +187,8 @@ export const Info = z
       )
       .optional()
       .describe("MCP (Model Context Protocol) server configurations"),
-    formatter: z
-      .union([
-        z.literal(false),
-        z.record(
-          z.string(),
-          z.object({
-            disabled: z.boolean().optional(),
-            command: z.array(z.string()).optional(),
-            environment: z.record(z.string(), z.string()).optional(),
-            extensions: z.array(z.string()).optional(),
-          }),
-        ),
-      ])
-      .optional(),
-    lsp: z
-      .union([
-        z.literal(false),
-        z.record(
-          z.string(),
-          z.union([
-            z.object({
-              disabled: z.literal(true),
-            }),
-            z.object({
-              command: z.array(z.string()),
-              extensions: z.array(z.string()).optional(),
-              disabled: z.boolean().optional(),
-              env: z.record(z.string(), z.string()).optional(),
-              initialization: z.record(z.string(), z.any()).optional(),
-            }),
-          ]),
-        ),
-      ])
-      .optional()
-      .refine(
-        (data) => {
-          if (!data) return true
-          if (typeof data === "boolean") return true
-          const serverIds = new Set(Object.values(LSPServer).map((s) => s.id))
-
-          return Object.entries(data).every(([id, config]) => {
-            if (config.disabled) return true
-            if (serverIds.has(id)) return true
-            return Boolean(config.extensions)
-          })
-        },
-        {
-          error: "For custom LSP servers, 'extensions' array is required.",
-        },
-      ),
+    formatter: ConfigFormatter.Info.optional(),
+    lsp: ConfigLSP.Info.optional(),
     instructions: z.array(z.string()).optional().describe("Additional instruction files or patterns to include"),
     layout: Layout.optional().describe("@deprecated Always uses stretch layout."),
     permission: ConfigPermission.Info.optional(),
diff --git a/packages/opencode/src/config/formatter.ts b/packages/opencode/src/config/formatter.ts
new file mode 100644
index 000000000000..7ac56214c912
--- /dev/null
+++ b/packages/opencode/src/config/formatter.ts
@@ -0,0 +1,13 @@
+export * as ConfigFormatter from "./formatter"
+
+import z from "zod"
+
+export const Entry = z.object({
+  disabled: z.boolean().optional(),
+  command: z.array(z.string()).optional(),
+  environment: z.record(z.string(), z.string()).optional(),
+  extensions: z.array(z.string()).optional(),
+})
+
+export const Info = z.union([z.literal(false), z.record(z.string(), Entry)])
+export type Info = z.infer<typeof Info>
diff --git a/packages/opencode/src/config/index.ts b/packages/opencode/src/config/index.ts
index c4a1c608b14b..a05c29d25ce9 100644
--- a/packages/opencode/src/config/index.ts
+++ b/packages/opencode/src/config/index.ts
@@ -2,6 +2,8 @@ export * as Config from "./config"
 export * as ConfigAgent from "./agent"
 export * as ConfigCommand from "./command"
 export * as ConfigError from "./error"
+export * as ConfigFormatter from "./formatter"
+export * as ConfigLSP from "./lsp"
 export * as ConfigVariable from "./variable"
 export { ConfigManaged } from "./managed"
 export * as ConfigMarkdown from "./markdown"
diff --git a/packages/opencode/src/config/lsp.ts b/packages/opencode/src/config/lsp.ts
new file mode 100644
index 000000000000..afb83908b9bf
--- /dev/null
+++ b/packages/opencode/src/config/lsp.ts
@@ -0,0 +1,39 @@
+export * as ConfigLSP from "./lsp"
+
+import z from "zod"
+import * as LSPServer from "../lsp/server"
+
+export const Disabled = z.object({
+  disabled: z.literal(true),
+})
+
+export const Entry = z.union([
+  Disabled,
+  z.object({
+    command: z.array(z.string()),
+    extensions: z.array(z.string()).optional(),
+    disabled: z.boolean().optional(),
+    env: z.record(z.string(), z.string()).optional(),
+    initialization: z.record(z.string(), z.any()).optional(),
+  }),
+])
+
+export const Info = z
+  .union([z.literal(false), z.record(z.string(), Entry)])
+  .refine(
+    (data) => {
+      if (typeof data === "boolean") return true
+      const serverIds = new Set(Object.values(LSPServer).map((server) => server.id))
+
+      return Object.entries(data).every(([id, config]) => {
+        if (config.disabled) return true
+        if (serverIds.has(id)) return true
+        return Boolean(config.extensions)
+      })
+    },
+    {
+      error: "For custom LSP servers, 'extensions' array is required.",
+    },
+  )
+
+export type Info = z.infer<typeof Info>
PATCH

echo "solve.sh: gold patch applied"
