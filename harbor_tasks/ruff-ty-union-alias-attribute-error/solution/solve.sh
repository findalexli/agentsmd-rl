#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff 2>/dev/null || cd /repo

TARGET="crates/ty_python_semantic/src/types/infer/builder.rs"

# Idempotency: check if the recursive helper already exists
if grep -q 'fn union_elements_missing_attribute' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 8997c25fe3b11..85b5b92fad3bd 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -8347,6 +8347,21 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             }
         }

+        fn union_elements_missing_attribute<'db>(
+            db: &'db dyn Db,
+            ty: Type<'db>,
+            attr_name: &str,
+            missing_types: &mut FxIndexSet<Type<'db>>,
+        ) {
+            if let Some(union) = ty.as_union_like(db) {
+                for element in union.elements(db) {
+                    union_elements_missing_attribute(db, *element, attr_name, missing_types);
+                }
+            } else if ty.member(db, attr_name).place.is_undefined() {
+                missing_types.insert(ty);
+            }
+        }
+
         let ast::ExprAttribute { value, attr, .. } = attribute;

         let mut value_type = self.infer_maybe_standalone_expression(value, TypeContext::default());
@@ -8587,11 +8602,16 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                     // we want it to be an error. Use `as_union_like` here to handle type aliases
                     // of unions and `NewType`s of float/complex in addition to explicit unions.
                     if let Some(union) = value_type.as_union_like(db) {
-                        let elements_missing_the_attribute: Vec<_> = union
-                            .elements(db)
-                            .iter()
-                            .filter(|element| element.member(db, attr_name).place.is_undefined())
-                            .collect();
+                        let mut elements_missing_the_attribute = FxIndexSet::default();
+                        for element in union.elements(db) {
+                            union_elements_missing_attribute(
+                                db,
+                                *element,
+                                attr_name,
+                                &mut elements_missing_the_attribute,
+                            );
+                        }
+
                         if !elements_missing_the_attribute.is_empty() {
                             if let Some(builder) =
                                 self.context.report_lint(&UNRESOLVED_ATTRIBUTE, attribute)

PATCH

echo "Patch applied successfully."
