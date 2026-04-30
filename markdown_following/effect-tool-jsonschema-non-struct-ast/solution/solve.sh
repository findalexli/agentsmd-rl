#!/bin/bash
set -euo pipefail

cd /workspace/effect

# Idempotency guard: if the defensive check is already gone, exit early.
if ! grep -q 'const props = AST.getPropertySignatures(ast)' packages/ai/ai/src/Tool.ts; then
  echo "Patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/rare-planets-lick.md b/.changeset/rare-planets-lick.md
new file mode 100644
index 00000000000..12aff13386e
--- /dev/null
+++ b/.changeset/rare-planets-lick.md
@@ -0,0 +1,5 @@
+---
+"@effect/ai": patch
+---
+
+Remove superfluous / defensive check from tool call json schema generation
diff --git a/packages/ai/ai/src/Tool.ts b/packages/ai/ai/src/Tool.ts
index 3dcb012d5cc..05128068f5d 100644
--- a/packages/ai/ai/src/Tool.ts
+++ b/packages/ai/ai/src/Tool.ts
@@ -1297,15 +1297,6 @@ export const getJsonSchema = <
 export const getJsonSchemaFromSchemaAst = (
   ast: AST.AST
 ): JsonSchema.JsonSchema7 => {
-  const props = AST.getPropertySignatures(ast)
-  if (props.length === 0) {
-    return {
-      type: "object",
-      properties: {},
-      required: [],
-      additionalProperties: false
-    }
-  }
   const $defs = {}
   const schema = JsonSchema.fromAST(ast, {
     definitions: $defs,
PATCH

echo "Patch applied"
