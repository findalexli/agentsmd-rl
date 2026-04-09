#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'ALLOW_PARAMSPEC_TYPE_EXPR' crates/ty_python_semantic/src/types/infer/builder/typevar.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/infer/builder/subscript.rs b/crates/ty_python_semantic/src/types/infer/builder/subscript.rs
index af41ce019185f..8cb9dd336e447 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/subscript.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/subscript.rs
@@ -781,6 +781,9 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 // Whether to infer `Todo` for the parameters
                 let mut return_todo = false;

+                let previously_allowed_paramspec = self
+                    .inference_flags
+                    .replace(InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR, false);
                 for param in elts {
                     let param_type = self.infer_type_expression(param);
                     // This is similar to what we currently do for inferring tuple type expression.
@@ -791,6 +794,10 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                         && matches!(param, ast::Expr::Starred(_) | ast::Expr::Subscript(_));
                     parameter_types.push(param_type);
                 }
+                self.inference_flags.set(
+                    InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR,
+                    previously_allowed_paramspec,
+                );

                 let parameters = if return_todo {
                     // TODO: `Unpack`
diff --git a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
index 5a3e8a901195fe..31f803e129b8ff 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
@@ -2116,7 +2116,14 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                         // store without going through type-expression inference.
                         self.store_expression_type(argument, Type::unknown());
                     } else if i < arguments.len() - 1 {
+                        let previously_allowed_paramspec = self
+                            .inference_flags
+                            .replace(InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR, false);
                         self.infer_type_expression(argument);
+                        self.inference_flags.set(
+                            InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR,
+                            previously_allowed_paramspec,
+                        );
                     } else {
                         let previously_allowed_paramspec = self
                             .inference_flags
@@ -2523,6 +2530,9 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             }
         };

+        let previously_allowed_paramspec = self
+            .inference_flags
+            .replace(InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR, false);
         let prefix_params = prefix_args
             .iter()
             .map(|arg| {
@@ -2530,6 +2540,10 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                     .with_annotated_type(self.infer_type_expression(arg))
             })
             .collect();
+        self.inference_flags.set(
+            InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR,
+            previously_allowed_paramspec,
+        );

         let parameters = self
             .infer_concatenate_tail(last_arg)
diff --git a/crates/ty_python_semantic/src/types/infer/builder/typevar.rs b/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
index a0b0e1b20ce3d..9ae65dcaedb35 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
@@ -604,10 +604,17 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 return;
             }
             ast::Expr::List(ast::ExprList { elts, .. }) => {
+                let previously_allowed_paramspec = self
+                    .inference_flags
+                    .replace(InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR, false);
                 let types = elts
                     .iter()
                     .map(|elt| self.infer_type_expression(elt))
                     .collect::<Vec<_>>();
+                self.inference_flags.set(
+                    InferenceFlags::ALLOW_PARAMSPEC_TYPE_EXPR,
+                    previously_allowed_paramspec,
+                );
                 // N.B. We cannot represent a heterogeneous list of types in our type system, so we
                 // use a heterogeneous tuple type to represent the list of types instead.
                 self.store_expression_type(default_expr, Type::heterogeneous_tuple(db, types));

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

echo "Patch applied successfully."
