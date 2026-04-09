#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'FnMut.*TypeContext' crates/ty_python_semantic/src/types/typed_dict.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/resources/mdtest/typed_dict.md b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
index 1aa8fb330321f..169cd41bd0316 100644
--- a/crates/ty_python_semantic/resources/mdtest/typed_dict.md
+++ b/crates/ty_python_semantic/resources/mdtest/typed_dict.md
@@ -408,6 +408,21 @@ accepts_person({"name": "Alice", "age": 30})
 house.owner = {"name": "Alice", "age": 30}
 ```

+Known issue: speculative `TypedDict` constructor validation currently duplicates diagnostics that
+were already emitted by the initial inference pass:
+
+```py
+from typing import TypedDict
+
+class TD(TypedDict):
+    x: int
+
+# TODO: This should only emit a single `unresolved-reference` diagnostic.
+# error: [unresolved-reference] "Name `missing` used when not defined"
+# error: [unresolved-reference] "Name `missing` used when not defined"
+TD(x=missing)
+```
+
 All of these are missing the required `age` field:

 ```py
@@ -2398,6 +2413,32 @@ def _(node: Node, person: Person):
 _: Node = Person(name="Alice", parent=Node(name="Bob", parent=Person(name="Charlie", parent=None)))
 ```

+TypedDict constructor calls should also use field type context when inferring nested values:
+
+```py
+from typing import TypedDict
+
+class Comparison(TypedDict):
+    field: str
+    value: object
+
+class Logical(TypedDict):
+    primary: Comparison
+    conditions: list[Comparison]
+
+logical_from_literal = Logical(
+    primary=Comparison(field="a", value="b"),
+    conditions=[Comparison(field="c", value="d")],
+)
+logical_from_dict_call = Logical(dict(primary=dict(field="a", value="b"), conditions=[dict(field="c", value="d")]))
+
+# error: [missing-typed-dict-key]
+missing_primary_from_dict_call = Logical(primary=dict(field="a"), conditions=[dict(field="c", value="d")])
+
+# error: [missing-typed-dict-key]
+missing_primary_from_literal = Logical(primary={"field": "a"}, conditions=[dict(field="c", value="d")])
+```
+
 ## Function/assignment syntax

 TypedDicts can be created using the functional syntax:
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 74bb3c7d39402..3c428ad59e79f 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -6892,13 +6892,18 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         if let Some(class) = class
             && class.is_typed_dict(self.db())
         {
+            let mut speculative = self.speculate();
             validate_typed_dict_constructor(
                 &self.context,
                 TypedDictType::new(class),
                 arguments,
                 func.as_ref().into(),
-                |expr| self.expression_type(expr),
+                |expr, tcx| speculative.infer_expression(expr, tcx),
             );
+            // TODO: Merging speculative inference preserves TypedDict-specific diagnostics, but it
+            // can also duplicate diagnostics that were already emitted during the initial
+            // type-context-free argument inference.
+            self.extend(speculative);
         }

         let mut bindings = match bindings_result {
diff --git a/crates/ty_python_semantic/src/types/infer/builder/dict.rs b/crates/ty_python_semantic/src/types/infer/builder/dict.rs
index 85690464f91e2..77cdf711b2943 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/dict.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/dict.rs
@@ -45,7 +45,7 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                 typed_dict,
                 arguments,
                 func.into(),
-                |expr| self.expression_type(expr),
+                |expr, _| self.expression_type(expr),
             );

             return Some(Type::TypedDict(typed_dict));
diff --git a/crates/ty_python_semantic/src/types/typed_dict.rs b/crates/ty_python_semantic/src/types/typed_dict.rs
index acae24520966b..0d0dcefc6fa94 100644
--- a/crates/ty_python_semantic/src/types/typed_dict.rs
+++ b/crates/ty_python_semantic/src/types/typed_dict.rs
@@ -922,7 +922,7 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
     typed_dict: TypedDictType<'db>,
     arguments: &'ast Arguments,
     error_node: AnyNodeRef<'ast>,
-    expression_type_fn: impl Fn(&ast::Expr) -> Type<'db>,
+    mut expression_type_fn: impl FnMut(&ast::Expr, TypeContext<'db>) -> Type<'db>,
 ) {
     let db = context.db();

@@ -939,7 +939,7 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
             typed_dict,
             arguments,
             error_node,
-            &expression_type_fn,
+            &mut expression_type_fn,
         );
         validate_typed_dict_required_keys(context, typed_dict, &provided_keys, error_node);
     } else if is_single_positional_arg {
@@ -948,8 +948,8 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
         // Assignability already checks for required keys and type compatibility,
         // so we don't need separate validation.
         let arg = &arguments.args[0];
-        let arg_ty = expression_type_fn(arg);
         let target_ty = Type::TypedDict(typed_dict);
+        let arg_ty = expression_type_fn(arg, TypeContext::new(Some(target_ty)));

         if !arg_ty.is_assignable_to(db, target_ty) {
             if let Some(builder) = context.report_lint(&INVALID_ARGUMENT_TYPE, arg) {
@@ -966,7 +966,7 @@ pub(super) fn validate_typed_dict_constructor<'db, 'ast>(
             typed_dict,
             arguments,
             error_node,
-            &expression_type_fn,
+            &mut expression_type_fn,
         );
         validate_typed_dict_required_keys(context, typed_dict, &provided_keys, error_node);
     }
@@ -979,9 +979,10 @@ fn validate_from_dict_literal<'db, 'ast>(
     typed_dict: TypedDictType<'db>,
     arguments: &'ast Arguments,
     typed_dict_node: AnyNodeRef<'ast>,
-    expression_type_fn: &impl Fn(&ast::Expr) -> Type<'db>,
+    expression_type_fn: &mut impl FnMut(&ast::Expr, TypeContext<'db>) -> Type<'db>,
 ) -> OrderSet<Name> {
     let mut provided_keys = OrderSet::new();
+    let items = typed_dict.items(context.db());

     if let ast::Expr::Dict(dict_expr) = &arguments.args[0] {
         // Validate dict entries
@@ -994,8 +995,11 @@ fn validate_from_dict_literal<'db, 'ast>(
                 let key = key_value.to_str();
                 provided_keys.insert(Name::new(key));

-                // Get the already-inferred argument type
-                let value_ty = expression_type_fn(&dict_item.value);
+                let value_tcx = items
+                    .get(key)
+                    .map(|field| TypeContext::new(Some(field.declared_ty)))
+                    .unwrap_or_default();
+                let value_ty = expression_type_fn(&dict_item.value, value_tcx);
                 TypedDictKeyAssignment {
                     context,
                     typed_dict,
@@ -1023,9 +1027,10 @@ fn validate_from_keywords<'db, 'ast>(
     typed_dict: TypedDictType<'db>,
     arguments: &'ast Arguments,
     typed_dict_node: AnyNodeRef<'ast>,
-    expression_type_fn: &impl Fn(&ast::Expr) -> Type<'db>,
+    expression_type_fn: &mut impl FnMut(&ast::Expr, TypeContext<'db>) -> Type<'db>,
 ) -> OrderSet<Name> {
     let db = context.db();
+    let items = typed_dict.items(db);

     // Collect keys from explicit keyword arguments
     let mut provided_keys: OrderSet<Name> = arguments
@@ -1038,7 +1043,11 @@ fn validate_from_keywords<'db, 'ast>(
     for keyword in &arguments.keywords {
         if let Some(arg_name) = &keyword.arg {
             // Explicit keyword argument: e.g., `name="Alice"`
-            let value_ty = expression_type_fn(&keyword.value);
+            let value_tcx = items
+                .get(arg_name.id.as_str())
+                .map(|field| TypeContext::new(Some(field.declared_ty)))
+                .unwrap_or_default();
+            let value_ty = expression_type_fn(&keyword.value, value_tcx);
             TypedDictKeyAssignment {
                 context,
                 typed_dict,
@@ -1057,7 +1066,7 @@ fn validate_from_keywords<'db, 'ast>(
             // Unlike positional TypedDict arguments, unpacking passes all keys as explicit
             // keyword arguments, so extra keys should be flagged as errors (consistent with
             // explicitly providing those keys).
-            let unpacked_type = expression_type_fn(&keyword.value);
+            let unpacked_type = expression_type_fn(&keyword.value, TypeContext::default());

             // Never and Dynamic types are special: they can have any keys, so we skip
             // validation and mark all required keys as provided.

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
