#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'infer_extra_items_kwarg' crates/ty_python_semantic/src/types/infer/builder/class.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index ae9e2480eeeb70..ca2871f127b7c0 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -4264,7 +4264,8 @@ e: MovieFunctional = {"name": "Blade Runner", "year": 1982}  # error: [invalid-k
 always implicitly non-required.

 ```py
-from typing_extensions import TypedDict, ReadOnly, Required, NotRequired
+from typing_extensions import TypedDict, ReadOnly, Required, NotRequired, ClassVar, Final
+from dataclasses import InitVar

 # OK
 class A(TypedDict, extra_items=int):
@@ -4274,13 +4275,25 @@ class A(TypedDict, extra_items=int):
 class B(TypedDict, extra_items=ReadOnly[int]):
     name: str

-# TODO: should be error: [invalid-typed-dict-header]
+# error: [invalid-type-form] "Type qualifier `typing.Required` is not valid in a TypedDict `extra_items` argument"
 class C(TypedDict, extra_items=Required[int]):
     name: str

-# TODO: should be error: [invalid-typed-dict-header]
+# error: [invalid-type-form] "Type qualifier `typing.NotRequired` is not valid in a TypedDict `extra_items` argument"
 class D(TypedDict, extra_items=NotRequired[int]):
     name: str
+
+# error: [invalid-type-form] "Type qualifier `typing.ClassVar` is not valid in a TypedDict `extra_items` argument"
+class D(TypedDict, extra_items=ClassVar[int]):
+    name: str
+
+# error: [invalid-type-form] "Type qualifier `typing.Final` is not valid in a TypedDict `extra_items` argument"
+class D(TypedDict, extra_items=Final[int]):
+    name: str
+
+# error: [invalid-type-form] "Type qualifier `dataclasses.InitVar` is not valid in a TypedDict `extra_items` argument"
+class D(TypedDict, extra_items=InitVar[int]):
+    name: str
 ```

 It is an error to specify both `closed` and `extra_items`:
@@ -4291,6 +4304,62 @@ class E(TypedDict, closed=True, extra_items=int):
     name: str
 ```

+### Forward references in `extra_items`
+
+Stringified forward references are understood:
+
+`a.py`:
+
+```py
+from typing import TypedDict
+
+class F(TypedDict, extra_items="F | None"): ...
+```
+
+While invalid syntax in forward annotations is rejected:
+
+`b.py`:
+
+```py
+from typing import TypedDict
+
+# error: [invalid-syntax-in-forward-annotation]
+class G(TypedDict, extra_items="not a type expression"): ...
+```
+
+In non-stub files, forward references in `extra_items` must be stringified:
+
+`c.py`:
+
+```py
+from typing import TypedDict
+
+# error: [unresolved-reference] "Name `H` used when not defined"
+class H(TypedDict, extra_items=H | None): ...
+```
+
+but stringification is unnecessary in stubs:
+
+`stub.pyi`:
+
+```pyi
+from typing import TypedDict
+
+class I(TypedDict, extra_items=I | None): ...
+```
+
+The `extra_items` keyword is not parsed as an annotation expression for non-TypedDict classes:
+
+`d.py`:
+
+```py
+class TypedDict:  # not typing.TypedDict!
+    def __init_subclass__(cls, extra_items: int): ...
+
+class Foo(TypedDict, extra_items=42): ...  # fine
+class Bar(TypedDict, extra_items=int): ...  # error: [invalid-argument-type]
+```
+
 ### Writing to an undeclared literal key of an `extra_items` TypedDict is allowed, if the type is assignable

 ```py
diff --git a/crates/ty_python_semantic/src/types/infer/builder/class.rs b/crates/ty_python_semantic/src/types/infer/builder/class.rs
index a5563ddda4a035..0d524f65c8a131 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/class.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/class.rs
@@ -9,6 +9,7 @@ use crate::{
             TypeInferenceBuilder,
             builder::{DeclaredAndInferredType, DeferredExpressionState},
         },
+        infer_definition_types,
         signatures::ParameterForm,
         special_form::TypeQualifier,
     },
@@ -219,7 +220,9 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             let previous_deferred_state =
                 std::mem::replace(&mut self.deferred_state, in_stub.into());
             for keyword in class_node.keywords() {
-                self.infer_expression(&keyword.value, TypeContext::default());
+                if keyword.arg.as_deref() != Some("extra_items") {
+                    self.infer_expression(&keyword.value, TypeContext::default());
+                }
             }
             self.deferred_state = previous_deferred_state;

@@ -229,6 +232,11 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                     .bases()
                     .iter()
                     .any(|expr| any_over_expr(expr, &ast::Expr::is_string_literal_expr))
+                || class_node
+                    .arguments
+                    .as_deref()
+                    .and_then(|args| args.find_keyword("extra_items"))
+                    .is_some()
             {
                 self.deferred.insert(definition);
             } else {
@@ -260,5 +268,24 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             }
         }
         self.typevar_binding_context = previous_typevar_binding_context;
+
+        if let Some(arguments) = class.arguments.as_deref()
+            && let Some(extra_items_keyword) = arguments.find_keyword("extra_items")
+        {
+            let class_type = infer_definition_types(self.db(), definition).binding_type(definition);
+            if let Type::ClassLiteral(class_literal) = class_type
+                && class_literal.is_typed_dict(self.db())
+            {
+                self.infer_extra_items_kwarg(&extra_items_keyword.value);
+            } else if self.in_stub() {
+                self.infer_expression_with_state(
+                    &extra_items_keyword.value,
+                    TypeContext::default(),
+                    DeferredExpressionState::Deferred,
+                );
+            } else {
+                self.infer_expression(&extra_items_keyword.value, TypeContext::default());
+            }
+        }
     }
 }
diff --git a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
index ab90b41acfd1f3..70e1007fa658b6 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
@@ -11,6 +11,7 @@ use crate::types::diagnostic::{
     INVALID_ARGUMENT_TYPE, INVALID_TYPE_FORM, MISSING_ARGUMENT, TOO_MANY_POSITIONAL_ARGUMENTS,
     UNKNOWN_ARGUMENT,
 };
+use crate::types::infer::builder::DeferredExpressionState;
 use crate::types::special_form::TypeQualifier;
 use crate::types::typed_dict::{TypedDictSchema, functional_typed_dict_field};
 use crate::types::{IntersectionType, KnownClass, Type, TypeAndQualifiers, TypeContext};
@@ -355,8 +356,13 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
         annotation
     }

-    fn infer_extra_items_kwarg(&mut self, value: &ast::Expr) -> TypeAndQualifiers<'db> {
-        let annotation = self.infer_annotation_expression(value, self.deferred_state);
+    pub(super) fn infer_extra_items_kwarg(&mut self, value: &ast::Expr) -> TypeAndQualifiers<'db> {
+        let state = if self.in_stub() {
+            DeferredExpressionState::Deferred
+        } else {
+            self.deferred_state
+        };
+        let annotation = self.infer_annotation_expression(value, state);
         for qualifier in TypeQualifier::iter() {
             if qualifier != TypeQualifier::ReadOnly
                 && annotation

PATCH

echo "Patch applied successfully."
