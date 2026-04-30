#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency: skip if already applied
if grep -q 'case "Transformation":\s*$' packages/effect/src/SchemaAST.ts \
   && grep -q 'return getIndexSignatures(ast.to)' packages/effect/src/SchemaAST.ts; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/effect/src/SchemaAST.ts b/packages/effect/src/SchemaAST.ts
--- a/packages/effect/src/SchemaAST.ts
+++ b/packages/effect/src/SchemaAST.ts
@@ -2231,6 +2231,8 @@ const getIndexSignatures = (ast: AST): Array<IndexSignature> => {
       return getIndexSignatures(ast.f())
     case "Refinement":
       return getIndexSignatures(ast.from)
+    case "Transformation":
+      return getIndexSignatures(ast.to)
   }
   return []
 }
PATCH

echo "Gold patch applied."
