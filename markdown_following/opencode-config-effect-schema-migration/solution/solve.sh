#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/opencode
cd "$REPO"

# Idempotency guard: a distinctive line that the gold patch introduces.
if grep -q 'static readonly zod = zod(this)' packages/opencode/src/config/console-state.ts 2>/dev/null; then
    echo "Gold patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/config/config.ts b/packages/opencode/src/config/config.ts
index 039b0598da86..261c5acab44f 100644
--- a/packages/opencode/src/config/config.ts
+++ b/packages/opencode/src/config/config.ts
@@ -100,7 +100,7 @@ export const Info = z
       .record(z.string(), ConfigCommand.Info)
       .optional()
       .describe("Command configuration, see https://opencode.ai/docs/commands"),
-    skills: ConfigSkills.Info.optional().describe("Additional skill folder paths"),
+    skills: ConfigSkills.Info.zod.optional().describe("Additional skill folder paths"),
     watcher: z
       .object({
         ignore: z.array(z.string()).optional(),
@@ -188,7 +188,7 @@ export const Info = z
       )
       .optional()
       .describe("MCP (Model Context Protocol) server configurations"),
-    formatter: ConfigFormatter.Info.optional(),
+    formatter: ConfigFormatter.Info.zod.optional(),
     lsp: ConfigLSP.Info.zod.optional(),
     instructions: z.array(z.string()).optional().describe("Additional instruction files or patterns to include"),
     layout: Layout.optional().describe("@deprecated Always uses stretch layout."),
diff --git a/packages/opencode/src/config/console-state.ts b/packages/opencode/src/config/console-state.ts
index cf96a4e305a3..08668afe4e8f 100644
--- a/packages/opencode/src/config/console-state.ts
+++ b/packages/opencode/src/config/console-state.ts
@@ -1,15 +1,16 @@
-import z from "zod"
+import { Schema } from "effect"
+import { zod } from "@/util/effect-zod"

-export const ConsoleState = z.object({
-  consoleManagedProviders: z.array(z.string()),
-  activeOrgName: z.string().optional(),
-  switchableOrgCount: z.number().int().nonnegative(),
-})
-
-export type ConsoleState = z.infer<typeof ConsoleState>
+export class ConsoleState extends Schema.Class<ConsoleState>("ConsoleState")({
+  consoleManagedProviders: Schema.mutable(Schema.Array(Schema.String)),
+  activeOrgName: Schema.optional(Schema.String),
+  switchableOrgCount: Schema.Number,
+}) {
+  static readonly zod = zod(this)
+}

-export const emptyConsoleState: ConsoleState = {
+export const emptyConsoleState: ConsoleState = ConsoleState.make({
   consoleManagedProviders: [],
   activeOrgName: undefined,
   switchableOrgCount: 0,
-}
+})
diff --git a/packages/opencode/src/config/formatter.ts b/packages/opencode/src/config/formatter.ts
index 93b87f02815c..8c1f09a2471d 100644
--- a/packages/opencode/src/config/formatter.ts
+++ b/packages/opencode/src/config/formatter.ts
@@ -1,13 +1,17 @@
 export * as ConfigFormatter from "./formatter"

-import z from "zod"
+import { Schema } from "effect"
+import { zod } from "@/util/effect-zod"
+import { withStatics } from "@/util/schema"

-export const Entry = z.object({
-  disabled: z.boolean().optional(),
-  command: z.array(z.string()).optional(),
-  environment: z.record(z.string(), z.string()).optional(),
-  extensions: z.array(z.string()).optional(),
-})
+export const Entry = Schema.Struct({
+  disabled: Schema.optional(Schema.Boolean),
+  command: Schema.optional(Schema.mutable(Schema.Array(Schema.String))),
+  environment: Schema.optional(Schema.Record(Schema.String, Schema.String)),
+  extensions: Schema.optional(Schema.mutable(Schema.Array(Schema.String))),
+}).pipe(withStatics((s) => ({ zod: zod(s) })))

-export const Info = z.union([z.boolean(), z.record(z.string(), Entry)])
-export type Info = z.infer<typeof Info>
+export const Info = Schema.Union([Schema.Boolean, Schema.Record(Schema.String, Entry)]).pipe(
+  withStatics((s) => ({ zod: zod(s) })),
+)
+export type Info = Schema.Schema.Type<typeof Info>
diff --git a/packages/opencode/src/config/skills.ts b/packages/opencode/src/config/skills.ts
index 38cbf99e7d75..f29d854f50a7 100644
--- a/packages/opencode/src/config/skills.ts
+++ b/packages/opencode/src/config/skills.ts
@@ -1,13 +1,16 @@
-import z from "zod"
+import { Schema } from "effect"
+import { zod } from "@/util/effect-zod"
+import { withStatics } from "@/util/schema"

-export const Info = z.object({
-  paths: z.array(z.string()).optional().describe("Additional paths to skill folders"),
-  urls: z
-    .array(z.string())
-    .optional()
-    .describe("URLs to fetch skills from (e.g., https://example.com/.well-known/skills/)"),
-})
+export const Info = Schema.Struct({
+  paths: Schema.optional(Schema.Array(Schema.String)).annotate({
+    description: "Additional paths to skill folders",
+  }),
+  urls: Schema.optional(Schema.Array(Schema.String)).annotate({
+    description: "URLs to fetch skills from (e.g., https://example.com/.well-known/skills/)",
+  }),
+}).pipe(withStatics((s) => ({ zod: zod(s) })))

-export type Info = z.infer<typeof Info>
+export type Info = Schema.Schema.Type<typeof Info>

 export * as ConfigSkills from "./skills"
diff --git a/packages/opencode/src/server/routes/instance/experimental.ts b/packages/opencode/src/server/routes/instance/experimental.ts
index f7ecc8255ba0..d5659346ef62 100644
--- a/packages/opencode/src/server/routes/instance/experimental.ts
+++ b/packages/opencode/src/server/routes/instance/experimental.ts
@@ -49,7 +49,7 @@ export const ExperimentalRoutes = lazy(() =>
             description: "Active Console provider metadata",
             content: {
               "application/json": {
-                schema: resolver(ConsoleState),
+                schema: resolver(ConsoleState.zod),
               },
             },
           },
PATCH

echo "Patch applied successfully."
