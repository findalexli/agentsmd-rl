#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if infer_type_alias already calls infer_type_expression, skip
if grep -q 'infer_type_expression(&type_alias.value)' \
    crates/ty_python_semantic/src/types/infer/builder.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/generics/pep695/aliases.md b/crates/ty_python_semantic/resources/mdtest/generics/pep695/aliases.md
index 5c0cec90bb58e..db1f211f346e7 100644
--- a/crates/ty_python_semantic/resources/mdtest/generics/pep695/aliases.md
+++ b/crates/ty_python_semantic/resources/mdtest/generics/pep695/aliases.md
@@ -45,6 +45,17 @@ You cannot use the same typevar more than once.
 type RepeatedTypevar[T, T] = tuple[T, T]
 ```

+Legacy type variables cannot be used:
+
+```py
+from typing import TypeVar
+
+V = TypeVar("V")
+
+# error: [unbound-type-variable]
+type TA1[K] = dict[K, V]
+```
+
 ## Specializing type aliases explicitly

 The type parameter can be specified explicitly:
diff --git a/crates/ty_python_semantic/resources/mdtest/pep695_type_aliases.md b/crates/ty_python_semantic/resources/mdtest/pep695_type_aliases.md
index f191719989ed0..6cc94fca6d7d5 100644
--- a/crates/ty_python_semantic/resources/mdtest/pep695_type_aliases.md
+++ b/crates/ty_python_semantic/resources/mdtest/pep695_type_aliases.md
@@ -40,6 +40,36 @@ type OptionalInt = int | None
 x: OptionalInt = "1"
 ```

+## No type qualifiers
+
+The right-hand side of a type alias definition is a type expression, not an annotation expression.
+Type qualifiers like `ClassVar` and `Final` are only valid in annotation expressions, so they cannot
+appear at the top level of a PEP 695 alias definition:
+
+```py
+from typing_extensions import ClassVar, Final, Required, NotRequired, ReadOnly
+from dataclasses import InitVar
+
+# error: [invalid-type-form] "Type qualifier `typing.ClassVar` is not allowed in type expressions (only in annotation expressions)"
+type Bad1 = ClassVar[str]
+# error: [invalid-type-form] "Type qualifier `typing.ClassVar` is not allowed in type expressions (only in annotation expressions)"
+type Bad2 = ClassVar
+# error: [invalid-type-form] "Type qualifier `typing.Final` is not allowed in type expressions (only in annotation expressions)"
+type Bad3 = Final[int]
+# error: [invalid-type-form] "Type qualifier `typing.Final` is not allowed in type expressions (only in annotation expressions)"
+type Bad4 = Final
+# error: [invalid-type-form] "Type qualifier `typing.Required` is not allowed in type expressions (only in annotation expressions)"
+type Bad5 = Required[int]
+# error: [invalid-type-form] "Type qualifier `typing.NotRequired` is not allowed in type expressions (only in annotation expressions)"
+type Bad6 = NotRequired[int]
+# error: [invalid-type-form] "Type qualifier `typing.ReadOnly` is not allowed in type expressions (only in annotation expressions)"
+type Bad7 = ReadOnly[int]
+# error: [invalid-type-form] "Type qualifier `dataclasses.InitVar` is not allowed in type expressions (only in annotation expressions)"
+type Bad8 = InitVar[int]
+# error: [invalid-type-form] "Type qualifier `dataclasses.InitVar` is not allowed in type expressions (only in annotation expressions, and only with exactly one argument)"
+type Bad9 = InitVar
+```
+
 ## Type aliases in type aliases

 ```py
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index 1b2850ff519c2..7c4b4df370459 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -5019,6 +5019,12 @@ impl<'db> Type<'db> {
                 let ty = match class.known(db) {
                     Some(KnownClass::Complex) => KnownUnion::Complex.to_type(db),
                     Some(KnownClass::Float) => KnownUnion::Float.to_type(db),
+                    Some(KnownClass::InitVar) => {
+                        return Err(InvalidTypeExpressionError {
+                            invalid_expressions: smallvec_inline![InvalidTypeExpression::InitVar],
+                            fallback_type: Type::unknown(),
+                        });
+                    }
                     _ => Type::instance(db, class.default_specialization(db)),
                 };
                 Ok(ty)
@@ -6730,6 +6736,7 @@ enum InvalidTypeExpression<'db> {
     /// Type qualifiers that are invalid in type expressions,
     /// and which would require exactly one argument even if they appeared in an annotation expression
     TypeQualifierRequiresOneArgument(TypeQualifier),
+    InitVar,
     /// `typing.Self` cannot be used in `@staticmethod` definitions.
     TypingSelfInStaticMethod,
     /// `typing.Self` cannot be used in metaclass definitions.
@@ -6803,6 +6810,10 @@ impl<'db> InvalidTypeExpression<'db> {
                         "Type qualifier `{qualifier}` is not allowed in type expressions \
                         (only in annotation expressions, and only with exactly one argument)",
                     ),
+                    InvalidTypeExpression::InitVar => f.write_str(
+                        "Type qualifier `dataclasses.InitVar` is not allowed in type expressions \
+                        (only in annotation expressions, and only with exactly one argument)",
+                    ),
                     InvalidTypeExpression::TypingSelfInStaticMethod => {
                         f.write_str("`Self` cannot be used in a static method")
                     }
diff --git a/crates/ty_python_semantic/src/types/infer.rs b/crates/ty_python_semantic/src/types/infer.rs
index 5a2ee4441422a..75f741f334627 100644
--- a/crates/ty_python_semantic/src/types/infer.rs
+++ b/crates/ty_python_semantic/src/types/infer.rs
@@ -984,6 +984,7 @@ bitflags::bitflags! {
 }

 impl InferenceFlags {
+    #[must_use = "Inference flags should always be restored to the original value after being temporarily modified"]
     fn replace(&mut self, other: Self, set_to: bool) -> bool {
         let previously_contained_flag = self.contains(other);
         self.set(other, set_to);
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 773211ab774f3..52ba391e4ca07 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -1242,8 +1242,14 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
     }

     fn infer_type_alias(&mut self, type_alias: &ast::StmtTypeAlias) {
-        let value_ty =
-            self.infer_annotation_expression(&type_alias.value, DeferredExpressionState::None);
+        let previous_check_unbound_typevars = self
+            .inference_flags
+            .replace(InferenceFlags::CHECK_UNBOUND_TYPEVARS, true);
+        let value_ty = self.infer_type_expression(&type_alias.value);
+        self.inference_flags.set(
+            InferenceFlags::CHECK_UNBOUND_TYPEVARS,
+            previous_check_unbound_typevars,
+        );

         // A type alias where a value type points to itself, i.e. the expanded type is `Divergent` is meaningless
         // (but a type alias that expands to something like `list[Divergent]` may be a valid recursive type alias)
@@ -1259,7 +1265,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         // type IntOrStr = int | StrOrInt  # It's redundant, but OK
         // type StrOrInt = str | IntOrStr  # It's redundant, but OK
         // ```
-        let expanded = value_ty.inner_type().expand_eagerly(self.db());
+        let expanded = value_ty.expand_eagerly(self.db());
         if expanded.is_divergent() {
             if let Some(builder) = self
                 .context
diff --git a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
index e4a3399746bbc..24253a943fa3c 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
@@ -5,8 +5,9 @@ use super::{DeferredExpressionState, TypeInferenceBuilder};
 use crate::semantic_index::scope::ScopeKind;
 use crate::types::diagnostic::{
     self, INVALID_TYPE_FORM, NOT_SUBSCRIPTABLE, UNBOUND_TYPE_VARIABLE, UNSUPPORTED_OPERATOR,
-    note_py_version_too_old_for_pep_604, report_invalid_argument_number_to_special_form,
-    report_invalid_arguments_to_callable, report_invalid_concatenate_last_arg,
+    add_type_expression_reference_link, note_py_version_too_old_for_pep_604,
+    report_invalid_argument_number_to_special_form, report_invalid_arguments_to_callable,
+    report_invalid_concatenate_last_arg,
 };
 use crate::types::infer::InferenceFlags;
 use crate::types::signatures::{ConcatenateTail, Signature};
@@ -683,6 +684,17 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             Type::ClassLiteral(class_literal) => match class_literal.known(self.db()) {
                 Some(KnownClass::Tuple) => Type::tuple(self.infer_tuple_type_expression(subscript)),
                 Some(KnownClass::Type) => self.infer_subclass_of_type_expression(slice),
+                Some(KnownClass::InitVar) => {
+                    if let Some(builder) = self.context.report_lint(&INVALID_TYPE_FORM, subscript) {
+                        let diagnostic = builder.into_diagnostic(
+                            "Type qualifier `dataclasses.InitVar` is not allowed in type \
+                            expressions (only in annotation expressions)",
+                        );
+                        add_type_expression_reference_link(diagnostic);
+                    }
+                    self.infer_expression(slice, TypeContext::default());
+                    Type::unknown()
+                }
                 _ => self.infer_subscript_type_expression(subscript, value_ty),
             },
             _ => self.infer_subscript_type_expression(subscript, value_ty),

PATCH

echo "Patch applied successfully."
