#!/bin/bash
set -e

cd /workspace/continue

# Apply the fix patch
git apply <<'PATCH'
diff --git a/core/tools/callTool.ts b/core/tools/callTool.ts
index dc1f16ade3c..22e83bb46ab 100644
--- a/core/tools/callTool.ts
+++ b/core/tools/callTool.ts
@@ -23,7 +23,7 @@ import { searchWebImpl } from "./implementations/searchWeb";
 import { viewDiffImpl } from "./implementations/viewDiff";
 import { viewRepoMapImpl } from "./implementations/viewRepoMap";
 import { viewSubdirectoryImpl } from "./implementations/viewSubdirectory";
-import { safeParseToolCallArgs } from "./parseArgs";
+import { coerceArgsToSchema, safeParseToolCallArgs } from "./parseArgs";

 async function callHttpTool(
   url: string,
@@ -95,10 +95,14 @@ async function callToolFromUri(
       if (!client) {
         throw new Error("MCP connection not found");
       }
+      const coercedArgs = coerceArgsToSchema(
+        args,
+        extras.tool?.function?.parameters,
+      );
       const response = await client.client.callTool(
         {
           name: toolName,
-          arguments: args,
+          arguments: coercedArgs,
         },
         CallToolResultSchema,
         { timeout: client.options.timeout },
diff --git a/core/tools/parseArgs.ts b/core/tools/parseArgs.ts
index 79f504d562b..4f4f67c9a 100644
--- a/core/tools/parseArgs.ts
+++ b/core/tools/parseArgs.ts
@@ -24,6 +24,44 @@ export function safeParseToolCallArgs(
   }
 }

+/**
+ * Coerce parsed args to match the tool's input schema types.
+ * JSON.parse() deeply parses all values, so string-typed parameters
+ * that contain valid JSON (e.g. file content for a .json file) get
+ * converted to objects. This checks the schema and re-stringifies
+ * any values that should be strings.
+ */
+export function coerceArgsToSchema(
+  args: Record<string, any>,
+  schema?: Record<string, any>,
+): Record<string, any> {
+  if (!schema?.properties) {
+    return args;
+  }
+
+  const coerced = { ...args };
+  for (const [key, value] of Object.entries(coerced)) {
+    const propSchema = schema.properties[key];
+    if (!propSchema) {
+      continue;
+    }
+
+    if (
+      propSchema.type === "string" &&
+      typeof value === "object" &&
+      value !== null
+    ) {
+      try {
+        coerced[key] = JSON.stringify(value);
+      } catch {
+        // leave as-is if stringify fails
+      }
+    }
+  }
+
+  return coerced;
+}
+
 export function getStringArg(
   args: any,
   argName: string,
PATCH

# Verify the distinctive line exists
grep -q "coerceArgsToSchema" core/tools/parseArgs.ts