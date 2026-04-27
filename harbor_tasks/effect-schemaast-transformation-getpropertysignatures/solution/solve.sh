#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency guard: a unique line from the patch.
if grep -q 'case "Transformation": return getPropertyKeyIndexedAccess(ast.to, name)' \
    packages/effect/src/SchemaAST.ts; then
    echo "[solve.sh] patch already applied; skipping"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/effect/src/SchemaAST.ts b/packages/effect/src/SchemaAST.ts
index 85f9ec8c42a..ab14a6df394 100644
--- a/packages/effect/src/SchemaAST.ts
+++ b/packages/effect/src/SchemaAST.ts
@@ -2328,6 +2328,8 @@ export const getPropertyKeyIndexedAccess = (ast: AST, name: PropertyKey): Proper
       return getPropertyKeyIndexedAccess(ast.f(), name)
     case "Refinement":
       return getPropertyKeyIndexedAccess(ast.from, name)
+    case "Transformation":
+      return getPropertyKeyIndexedAccess(ast.to, name)
   }
   throw new Error(errors_.getASTUnsupportedSchemaErrorMessage(ast))
 }
PATCH

echo "[solve.sh] patch applied"
