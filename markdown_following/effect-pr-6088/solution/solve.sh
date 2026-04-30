#!/bin/bash
set -euo pipefail
cd /workspace/effect

if grep -q 'getIndexSignatures(ast.to)' packages/effect/src/SchemaAST.ts; then
    echo "Patch already applied (idempotency check passed)"
    exit 0
fi

git apply <<'PATCH'
diff --git a/packages/effect/src/SchemaAST.ts b/packages/effect/src/SchemaAST.ts
index ab14a6df394..1f9efb8a2d0 100644
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
