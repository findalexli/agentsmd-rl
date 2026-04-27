#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency guard
if grep -q 'case "Transformation":\s*$' packages/effect/src/SchemaAST.ts \
   && grep -A1 'case "Transformation":' packages/effect/src/SchemaAST.ts \
        | grep -q 'return getIndexSignatures(ast.to)'; then
  echo "Already patched, skipping"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-schema-ast-getIndexSignatures.md b/.changeset/fix-schema-ast-getIndexSignatures.md
new file mode 100644
index 00000000000..890c5831f3f
--- /dev/null
+++ b/.changeset/fix-schema-ast-getIndexSignatures.md
@@ -0,0 +1,7 @@
+---
+"effect": patch
+---
+
+Schema: fix `Schema.omit` producing wrong result on Struct with `optionalWith({ default })` and index signatures
+
+`getIndexSignatures` now handles `Transformation` AST nodes by delegating to `ast.to`, matching the existing behavior of `getPropertyKeys` and `getPropertyKeyIndexedAccess`. Previously, `Schema.omit` on a struct combining `Schema.optionalWith` (with `{ default }`, `{ as: "Option" }`, etc.) and `Schema.Record` would silently take the wrong code path, returning a Transformation with property signatures instead of a TypeLiteral with index signatures.
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
diff --git a/packages/effect/test/Schema/Schema/Struct/omit.test.ts b/packages/effect/test/Schema/Schema/Struct/omit.test.ts
index 47059890948..da5f2b9c822 100644
--- a/packages/effect/test/Schema/Schema/Struct/omit.test.ts
+++ b/packages/effect/test/Schema/Schema/Struct/omit.test.ts
@@ -7,4 +7,16 @@ describe("omit", () => {
     const schema = S.Struct({ a: S.String, b: S.Number, c: S.Boolean }).omit("c")
     deepStrictEqual(schema.fields, { a: S.String, b: S.Number })
   })
+
+  it("should preserve index signatures on Struct with optionalWith default", () => {
+    const schema = S.Struct(
+      { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
+      S.Record({ key: S.String, value: S.Boolean })
+    )
+    const plain = S.Struct(
+      { a: S.String, b: S.Number },
+      S.Record({ key: S.String, value: S.Boolean })
+    )
+    deepStrictEqual(schema.pipe(S.omit("a")).ast, plain.pipe(S.omit("a")).ast)
+  })
 })
PATCH

echo "Patch applied successfully"
