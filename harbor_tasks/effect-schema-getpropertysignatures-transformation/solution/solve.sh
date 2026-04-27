#!/bin/bash
set -euo pipefail

cd /workspace/effect

if grep -q 'case "Transformation":\s*$' packages/effect/src/SchemaAST.ts \
   && grep -A1 'case "Transformation":\s*$' packages/effect/src/SchemaAST.ts \
   | grep -q 'return getPropertyKeyIndexedAccess(ast.to, name)'; then
  echo "Patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-schema-ast-transformation.md b/.changeset/fix-schema-ast-transformation.md
new file mode 100644
index 00000000000..1ee1a1d1068
--- /dev/null
+++ b/.changeset/fix-schema-ast-transformation.md
@@ -0,0 +1,7 @@
+---
+"effect": patch
+---
+
+Schema: fix `getPropertySignatures` crash on Struct with `optionalWith({ default })` and other Transformation-producing variants
+
+`SchemaAST.getPropertyKeyIndexedAccess` now handles `Transformation` AST nodes by delegating to `ast.to`, matching the existing behavior of `getPropertyKeys`. Previously, calling `getPropertySignatures` on a `Schema.Struct` containing `Schema.optionalWith` with `{ default }`, `{ as: "Option" }`, `{ nullable: true }`, or similar options would throw `"Unsupported schema (Transformation)"`.
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
diff --git a/packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts b/packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts
index 173ee4fb6ed..8e659fb7368 100644
--- a/packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts
+++ b/packages/effect/test/Schema/SchemaAST/getPropertySignatures.test.ts
@@ -43,4 +43,30 @@ describe("getPropertySignatures", () => {
       new AST.PropertySignature("b", S.Number.ast, false, true)
     ])
   })
+
+  it("Transformation (Struct with optionalWith default)", () => {
+    const schema = S.Struct({
+      a: S.String,
+      b: S.optionalWith(S.Number, { default: () => 0 })
+    })
+    deepStrictEqual(AST.getPropertySignatures(schema.ast), [
+      new AST.PropertySignature("a", S.String.ast, false, true),
+      new AST.PropertySignature("b", S.Number.ast, false, true)
+    ])
+  })
+
+  it("Transformation (Struct with optionalWith as Option)", () => {
+    const schema = S.Struct({
+      a: S.String,
+      b: S.optionalWith(S.Number, { as: "Option" })
+    })
+    const signatures = AST.getPropertySignatures(schema.ast)
+    deepStrictEqual(signatures.length, 2)
+    deepStrictEqual(signatures[0], new AST.PropertySignature("a", S.String.ast, false, true))
+    deepStrictEqual(signatures[1].name, "b")
+    deepStrictEqual(signatures[1].isOptional, false)
+    deepStrictEqual(signatures[1].isReadonly, true)
+    // b's type on the decoded side is Option<number> (a Declaration AST)
+    deepStrictEqual(signatures[1].type._tag, "Declaration")
+  })
 })
PATCH

echo "Patch applied"
