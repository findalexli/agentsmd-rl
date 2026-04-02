#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if annotate_final_declaration already exists, skip
if grep -q 'annotate_final_declaration' \
    crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md b/crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md
index afeddfc1fd725..24bd0cb4d034d 100644
--- a/crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md
+++ b/crates/ty_python_semantic/resources/mdtest/type_qualifiers/final.md
@@ -1138,6 +1138,29 @@ class E:
         self.x = 2  # Error: `self` is the second parameter, not the implicit receiver
 ```

+## Cross-module final attribute assignment
+
+Assigning to an inherited `Final` attribute where the base class is in a different module:
+
+`base.py`:
+
+```py
+from typing import Final
+
+class Base:
+    x: Final[int] = 1
+```
+
+`child.py`:
+
+```py
+from base import Base
+
+class Child(Base):
+    def f(self):
+        self.x = 2  # error: [invalid-assignment]
+```
+
 ## Full diagnostics

 <!-- snapshot-diagnostics -->
@@ -1186,6 +1209,55 @@ def __init__(c: C):
     c.x = 2  # error: [invalid-assignment]
 ```

+Class-body `Final` declaration without value:
+
+```py
+from typing import Final
+
+class C:
+    x: Final[int]  # error: [final-without-value]
+
+    def f(self):
+        self.x = 2  # error: [invalid-assignment]
+```
+
+`__init__` assignment after class-body value:
+
+```py
+from typing import Final
+
+class C:
+    x: Final[int] = 1
+
+    def __init__(self):
+        self.x = 2  # error: [invalid-assignment]
+```
+
+Inherited final attribute assignment:
+
+```py
+from typing import Final
+
+class Base:
+    x: Final[int] = 1
+
+class Child(Base):
+    def f(self):
+        self.x = 2  # error: [invalid-assignment]
+```
+
+Method-local `Final` annotation should not point at non-`Final` class annotation:
+
+```py
+from typing import Final
+
+class C:
+    x: int
+
+    def f(self):
+        self.x: Final[int] = 1  # error: [invalid-assignment]
+```
+
 `Final` declaration without value:

 ```py
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index 0656296c085b6..f7b70447e46df 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -1057,6 +1057,15 @@ impl<'db> Type<'db> {
             Type::NominalInstance(instance) => Some(instance.class(db)),
             Type::ProtocolInstance(instance) => instance.to_nominal_instance().map(|i| i.class(db)),
             Type::TypeAlias(alias) => alias.value_type(db).nominal_class(db),
+            Type::NewTypeInstance(newtype) => newtype.concrete_base_type(db).nominal_class(db),
+            Type::TypeVar(typevar) => {
+                let TypeVarBoundOrConstraints::UpperBound(bound) =
+                    typevar.typevar(db).bound_or_constraints(db)?
+                else {
+                    return None;
+                };
+                bound.nominal_class(db)
+            }
             _ => None,
         }
     }
diff --git a/crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs b/crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs
index ed812afe3964d..d5f7de9f24e8f 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs
@@ -1,13 +1,93 @@
+use ruff_db::diagnostic::{Annotation, Diagnostic, Span};
+use ruff_db::parsed::parsed_module;
 use ruff_python_ast as ast;
 use ruff_text_size::Ranged;

+use crate::place::place_from_declarations;
+use crate::semantic_index::definition::{Definition, DefinitionKind};
 use crate::semantic_index::place::{PlaceExpr, ScopedPlaceId};
+use crate::semantic_index::semantic_index;
 use crate::{
     TypeQualifiers,
     types::{Type, diagnostic::INVALID_ASSIGNMENT, infer::TypeInferenceBuilder},
 };

 impl<'db> TypeInferenceBuilder<'db, '_> {
+    /// Add a secondary annotation to a diagnostic pointing to the `Final` declaration site.
+    fn annotate_final_declaration(
+        &self,
+        diagnostic: &mut Diagnostic,
+        declaration: Definition<'db>,
+    ) {
+        let db = self.db();
+        let file = declaration.file(db);
+        let module = parsed_module(db, file).load(db);
+        let range = match declaration.kind(db) {
+            DefinitionKind::AnnotatedAssignment(assignment) => {
+                assignment.annotation(&module).range()
+            }
+            kind => kind.target_range(&module),
+        };
+
+        diagnostic.annotate(
+            Annotation::secondary(Span::from(file).with_range(range))
+                .message("Attribute declared as `Final` here"),
+        );
+    }
+
+    /// Try to find the unique `Final` declaration for `attribute` on `object_ty`.
+    ///
+    /// Returns `None` if the attribute is not `Final`, if there are multiple `Final`
+    /// declarations, or if the owning class cannot be determined.
+    fn precise_final_attribute_declaration(
+        &self,
+        object_ty: Type<'db>,
+        attribute: &str,
+    ) -> Option<Definition<'db>> {
+        let db = self.db();
+        let class_ty = object_ty
+            .nominal_class(db)
+            .or_else(|| object_ty.to_class_type(db))?;
+
+        for base in class_ty.iter_mro(db) {
+            let Some(class) = base.into_class() else {
+                continue;
+            };
+            let Some((class_literal, _)) = class.static_class_literal(db) else {
+                continue;
+            };
+
+            let class_body_scope = class_literal.body_scope(db);
+            let class_scope_id = class_body_scope.file_scope_id(db);
+            let class_index = semantic_index(db, class_body_scope.file(db));
+            let place_table = class_index.place_table(class_scope_id);
+            let Some(symbol_id) = place_table.symbol_id(attribute) else {
+                continue;
+            };
+
+            let use_def = class_index.use_def_map(class_scope_id);
+
+            let place_and_quals_result =
+                place_from_declarations(db, use_def.end_of_scope_symbol_declarations(symbol_id));
+
+            let Some(declaration) = place_and_quals_result.first_declaration else {
+                continue;
+            };
+
+            if !place_and_quals_result
+                .ignore_conflicting_declarations()
+                .qualifiers
+                .contains(TypeQualifiers::FINAL)
+            {
+                continue;
+            }
+
+            return Some(declaration);
+        }
+
+        None
+    }
+
     /// Check if the target attribute expression (e.g. `self.x`) is an instance attribute
     /// assignment, i.e. the object is the implicit `self`/`cls` receiver.
     ///
@@ -38,10 +118,7 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
         }

         let db = self.db();
-
-        // TODO: Point to the `Final` declaration once we can reliably resolve the owning
-        // declaration for this attribute, including inherited members and locally introduced
-        // `Final` annotations on assignments.
+        let final_declaration = self.precise_final_attribute_declaration(object_ty, attribute);

         // TODO: Use the full assignment statement range for these diagnostics instead of
         // just the attribute target range.
@@ -64,6 +141,9 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             diagnostic.set_primary_message(
                 "`Final` attributes can only be assigned in the class body or `__init__`",
             );
+            if let Some(final_declaration) = final_declaration {
+                self.annotate_final_declaration(&mut diagnostic, final_declaration);
+            }
         };

         if !is_in_init {
@@ -91,8 +171,10 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
         }

         if let Some((class_literal, _)) = class_ty.static_class_literal(db) {
-            let class_scope_id = class_literal.body_scope(db).file_scope_id(db);
-            let pt = self.index.place_table(class_scope_id);
+            let class_body_scope = class_literal.body_scope(db);
+            let class_scope_id = class_body_scope.file_scope_id(db);
+            let class_index = semantic_index(db, class_body_scope.file(db));
+            let pt = class_index.place_table(class_scope_id);

             if let Some(symbol) = pt.symbol_by_name(attribute)
                 && symbol.is_bound()
@@ -106,6 +188,9 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                     diagnostic.set_primary_message(format_args!(
                         "`{attribute}` already has a value in the class body"
                     ));
+                    if let Some(final_declaration) = final_declaration {
+                        self.annotate_final_declaration(&mut diagnostic, final_declaration);
+                    }
                 }

                 return true;

PATCH
