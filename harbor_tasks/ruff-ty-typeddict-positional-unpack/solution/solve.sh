#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'validate_from_typed_dict_argument' crates/ty_python_semantic/src/types/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index c93e5da4adaddf..b5699554d1feeb 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -496,6 +496,54 @@ def _(
     ChildKwargs(**maybe_name, count=1)
 ```

+TypedDict positional arguments in mixed constructors should validate their declared keys:
+
+```py
+from typing import TypedDict
+
+class Target(TypedDict):
+    a: int
+    b: int
+
+class Source(TypedDict):
+    a: int
+
+class BadSource(TypedDict):
+    a: str
+
+class MaybeSource(TypedDict, total=False):
+    a: int
+
+class WiderSource(TypedDict):
+    a: int
+    extra: str
+
+class WiderBadSource(TypedDict):
+    a: str
+    extra: str
+
+def _(
+    source: Source,
+    bad: BadSource,
+    maybe: MaybeSource,
+    wide: WiderSource,
+    wide_bad: WiderBadSource,
+    cond: bool,
+):
+    Target(source, b=2)
+    Target(source if cond else {"a": 1}, b=2)
+    Target(wide, b=2)
+
+    # error: [invalid-argument-type] "Invalid argument to key "a" with declared type `int` on TypedDict `Target`: value of type `str`"
+    Target(bad, b=2)
+
+    # error: [invalid-argument-type] "Invalid argument to key "a" with declared type `int` on TypedDict `Target`: value of type `str`"
+    Target(wide_bad, b=2)
+
+    # error: [missing-typed-dict-key] "Missing required key 'a' in TypedDict `Target` constructor"
+    Target(maybe, b=2)
+```
+
 All of these are missing the required `age` field:

 ```py
diff --git a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
index eff31551b47c8f..57a16e774961c0 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs
@@ -15,7 +15,8 @@ use crate::types::diagnostic::{
 use crate::types::infer::builder::DeferredExpressionState;
 use crate::types::special_form::TypeQualifier;
 use crate::types::typed_dict::{
-    TypedDictSchema, functional_typed_dict_field, validate_typed_dict_constructor,
+    TypedDictSchema, collect_guaranteed_keyword_keys, functional_typed_dict_field,
+    infer_unpacked_keyword_types, typed_dict_without_keys, validate_typed_dict_constructor,
     validate_typed_dict_dict_literal,
 };
 use crate::types::{
@@ -367,11 +368,26 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                 let target_ty = Type::TypedDict(typed_dict);
                 self.get_or_infer_expression(argument, TypeContext::new(Some(target_ty)));
             }
+            TypedDictConstructorForm::MixedPositionalAndKeywords => {
+                // Infer the positional argument against the schema left after removing keys that
+                // are guaranteed by keywords. For `Target(source if cond else {"a": 1}, b=2)`,
+                // the conditional must be prepared against `{"a": int}` rather than the full
+                // `Target`; otherwise the cached type spuriously requires `b` before validation.
+                let unpacked_keyword_types =
+                    infer_unpacked_keyword_types(arguments, &mut |expr, tcx| {
+                        self.get_or_infer_expression(expr, tcx)
+                    });
+                let keyword_keys =
+                    collect_guaranteed_keyword_keys(self.db(), arguments, &unpacked_keyword_types);
+                let positional_target =
+                    typed_dict_without_keys(self.db(), typed_dict, &keyword_keys);
+                let target_ty = Type::TypedDict(positional_target);
+                self.get_or_infer_expression(&arguments.args[0], TypeContext::new(Some(target_ty)));
+            }
             TypedDictConstructorForm::MixedLiteralAndKeywords(dict_expr) => {
                 self.infer_typed_dict_constructor_dict_literal_values(typed_dict, dict_expr);
             }
-            TypedDictConstructorForm::MixedPositionalAndKeywords
-            | TypedDictConstructorForm::KeywordOnly => {}
+            TypedDictConstructorForm::KeywordOnly => {}
         }

         if !arguments.keywords.is_empty() {
diff --git a/crates/ty_python_semantic/src/types/typed_dict.rs b/crates/ty_python_semantic/src/types/typed_dict.rs
index 2ec873a948d00b..d9048e260096d2 100644
--- a/crates/ty_python_semantic/src/types/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/typed_dict.rs
@@ -962,7 +962,7 @@ fn extract_unpacked_typed_dict_keys<'db>(
 ///
 /// Mixed positional-and-keyword `TypedDict` construction needs to inspect unpacked keyword types
 /// in multiple validation passes. Precomputing them avoids re-inference in speculative builders.
-fn infer_unpacked_keyword_types<'db>(
+pub(super) fn infer_unpacked_keyword_types<'db>(
     arguments: &Arguments,
     expression_type_fn: &mut impl FnMut(&ast::Expr, TypeContext<'db>) -> Type<'db>,
 ) -> Vec<Option<Type<'db>>> {
@@ -983,7 +983,7 @@ fn infer_unpacked_keyword_types<'db>(
 /// Explicit keyword arguments always provide their key. For `**kwargs`, only required keys are
 /// guaranteed to be present; optional keys may be omitted at runtime and cannot suppress missing
 /// key diagnostics for the positional mapping.
-fn collect_guaranteed_keyword_keys<'db>(
+pub(super) fn collect_guaranteed_keyword_keys<'db>(
     db: &'db dyn Db,
     arguments: &Arguments,
     unpacked_keyword_types: &[Option<Type<'db>>],
@@ -1013,7 +1013,7 @@ fn collect_guaranteed_keyword_keys<'db>(
 ///
 /// This is used for mixed positional-and-keyword constructor calls, where guaranteed keyword
 /// arguments override any same-named keys from the positional mapping.
-fn typed_dict_without_keys<'db>(
+pub(super) fn typed_dict_without_keys<'db>(
     db: &'db dyn Db,
     typed_dict: TypedDictType<'db>,
     excluded_keys: &OrderSet<Name>,
@@ -1032,6 +1032,108 @@ fn typed_dict_without_keys<'db>(
     TypedDictType::from_schema_items(db, filtered_items)
 }

+fn full_object_ty_annotation(ty: Type<'_>) -> Option<Type<'_>> {
+    (ty.is_union() || ty.is_intersection()).then_some(ty)
+}
+
+/// AST nodes attached to a `TypedDict` key assignment diagnostic.
+///
+/// Example: for `Target(source, b=2)`, this bundles the full constructor call together with the
+/// expression nodes that should be highlighted for the key and value being validated.
+#[derive(Clone, Copy)]
+struct TypedDictAssignmentNodes<'ast> {
+    /// The outer `TypedDict` constructor or unpacking site.
+    ///
+    /// Example: this is the `Target(source, b=2)` call when validating a mixed constructor.
+    typed_dict: AnyNodeRef<'ast>,
+    /// The syntax node used to label the key location in diagnostics.
+    ///
+    /// Example: this is the `b=2` keyword for an explicit key, or the `source` expression when a
+    /// positional `TypedDict` supplies the key.
+    key: AnyNodeRef<'ast>,
+    /// The syntax node used to label the value location in diagnostics.
+    ///
+    /// Example: this is the `2` in `Target(source, b=2)`, or the `source` expression when the
+    /// positional argument provides both the key and value type information.
+    value: AnyNodeRef<'ast>,
+}
+
+/// Validates a set of extracted `TypedDict`-like keys against a constructor target.
+///
+/// This is shared by `**kwargs` validation and mixed constructor calls where the first positional
+/// argument is itself `TypedDict`-shaped. It reports per-key diagnostics using the supplied
+/// nodes and returns the subset of keys that are guaranteed to be present.
+fn validate_extracted_typed_dict_keys<'db, 'ast>(
+    context: &InferContext<'db, 'ast>,
+    typed_dict: TypedDictType<'db>,
+    unpacked_keys: &BTreeMap<Name, UnpackedTypedDictKey<'db>>,
+    nodes: TypedDictAssignmentNodes<'ast>,
+    full_object_ty: Option<Type<'db>>,
+    ignored_keys: &OrderSet<Name>,
+) -> OrderSet<Name> {
+    let mut provided_keys = OrderSet::new();
+
+    for (key_name, unpacked_key) in unpacked_keys {
+        if ignored_keys.contains(key_name) {
+            continue;
+        }
+        if unpacked_key.is_required {
+            provided_keys.insert(key_name.clone());
+        }
+        TypedDictKeyAssignment {
+            context,
+            typed_dict,
+            full_object_ty,
+            key: key_name.as_str(),
+            value_ty: unpacked_key.value_ty,
+            typed_dict_node: nodes.typed_dict,
+            key_node: nodes.key,
+            value_node: nodes.value,
+            assignment_kind: TypedDictAssignmentKind::Constructor,
+            emit_diagnostic: true,
+        }
+        .validate();
+    }
+
+    provided_keys
+}
+
+/// Validates a mixed-constructor positional argument when its type can be viewed as a `TypedDict`.
+///
+/// If `arg_ty` exposes concrete `TypedDict` keys, only keys that overlap the constructor target
+/// are validated directly. This preserves the structural leniency of positional `TypedDict`
+/// arguments while still checking declared keys precisely in mixed calls. Returns `None` when the
+/// argument is not `TypedDict`-shaped and the caller should fall back to ordinary assignability
+/// checks.
+fn validate_from_typed_dict_argument<'db, 'ast>(
+    context: &InferContext<'db, 'ast>,
+    typed_dict: TypedDictType<'db>,
+    arg: &'ast ast::Expr,
+    arg_ty: Type<'db>,
+    typed_dict_node: AnyNodeRef<'ast>,
+    ignored_keys: &OrderSet<Name>,
+) -> Option<OrderSet<Name>> {
+    let db = context.db();
+    let typed_dict_items = typed_dict.items(db);
+    let unpacked_keys = extract_unpacked_typed_dict_keys(db, arg_ty)?
+        .into_iter()
+        .filter(|(key_name, _)| typed_dict_items.contains_key(key_name))
+        .collect();
+
+    Some(validate_extracted_typed_dict_keys(
+        context,
+        typed_dict,
+        &unpacked_keys,
+        TypedDictAssignmentNodes {
+            typed_dict: typed_dict_node,
+            key: arg.into(),
+            value: arg.into(),
+        },
+        full_object_ty_annotation(arg_ty),
+        ignored_keys,
+    ))
+}
+
 /// Validates a `TypedDict` constructor call.
 ///
 /// This handles keyword-only construction, a single positional mapping argument, and mixed
@@ -1072,21 +1174,32 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
             let positional_target_ty = Type::TypedDict(positional_target);
             let arg_ty = expression_type_fn(arg, TypeContext::new(Some(positional_target_ty)));

-            if !arg_ty.is_assignable_to(db, positional_target_ty) {
-                if let Some(builder) = context.report_lint(&INVALID_ARGUMENT_TYPE, arg) {
-                    builder.into_diagnostic(format_args!(
-                        "Argument of type `{}` is not assignable to `{}`",
-                        arg_ty.display(db),
-                        positional_target_ty.display(db),
-                    ));
+            if let Some(provided_keys) = validate_from_typed_dict_argument(
+                context,
+                typed_dict,
+                arg,
+                arg_ty,
+                error_node,
+                &keyword_keys,
+            ) {
+                provided_keys
+            } else {
+                if !arg_ty.is_assignable_to(db, positional_target_ty) {
+                    if let Some(builder) = context.report_lint(&INVALID_ARGUMENT_TYPE, arg) {
+                        builder.into_diagnostic(format_args!(
+                            "Argument of type `{}` is not assignable to `{}`",
+                            arg_ty.display(db),
+                            positional_target_ty.display(db),
+                        ));
+                    }
                 }
-            }

-            positional_target
-                .items(db)
-                .iter()
-                .filter_map(|(key_name, field)| field.is_required().then_some(key_name.clone()))
-                .collect()
+                positional_target
+                    .items(db)
+                    .iter()
+                    .filter_map(|(key_name, field)| field.is_required().then_some(key_name.clone()))
+                    .collect()
+            }
         };

         provided_keys.extend(validate_from_keywords(
@@ -1260,24 +1373,18 @@ fn validate_from_keywords<'db, 'ast>(
                 }
             } else if let Some(unpacked_keys) = extract_unpacked_typed_dict_keys(db, unpacked_type)
             {
-                for (key_name, unpacked_key) in &unpacked_keys {
-                    if unpacked_key.is_required {
-                        provided_keys.insert(key_name.clone());
-                    }
-                    TypedDictKeyAssignment {
-                        context,
-                        typed_dict,
-                        full_object_ty: None,
-                        key: key_name.as_str(),
-                        value_ty: unpacked_key.value_ty,
-                        typed_dict_node,
-                        key_node: keyword.into(),
-                        value_node: (&keyword.value).into(),
-                        assignment_kind: TypedDictAssignmentKind::Constructor,
-                        emit_diagnostic: true,
-                    }
-                    .validate();
-                }
+                provided_keys.extend(validate_extracted_typed_dict_keys(
+                    context,
+                    typed_dict,
+                    &unpacked_keys,
+                    TypedDictAssignmentNodes {
+                        typed_dict: typed_dict_node,
+                        key: keyword.into(),
+                        value: (&keyword.value).into(),
+                    },
+                    full_object_ty_annotation(unpacked_type),
+                    &OrderSet::new(),
+                ));
             }
         }
     }

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
