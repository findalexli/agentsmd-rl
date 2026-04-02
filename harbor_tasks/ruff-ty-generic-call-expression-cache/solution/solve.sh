#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if fix is already applied (look for expression_cache field)
if grep -q 'expression_cache:' crates/ty_python_semantic/src/types/infer/builder.rs; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 520b2e8f7841e..4022a254d137a 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -1,4 +1,6 @@
 use std::borrow::Cow;
+use std::cell::RefCell;
+use std::rc::Rc;

 use itertools::{Either, Itertools};
 use ruff_db::diagnostic::{Annotation, DiagnosticId, Severity};
@@ -222,6 +224,9 @@ pub(super) struct TypeInferenceBuilder<'db, 'ast> {
     /// The types of every expression in this region.
     expressions: FxHashMap<ExpressionNodeKey, Type<'db>>,

+    /// An expression cache shared across builders during multi-inference.
+    expression_cache: Option<Rc<RefCell<ExpressionCache<'db>>>>,
+
     /// Expressions that are string annotations
     string_annotations: FxHashSet<ExpressionNodeKey>,

@@ -306,6 +311,9 @@ pub(super) struct TypeInferenceBuilder<'db, 'ast> {
     dataclass_field_specifiers: SmallVec<[Type<'db>; NUM_FIELD_SPECIFIERS_INLINE]>,
 }

+/// An expression cache shared across builders during multi-inference.
+type ExpressionCache<'db> = FxHashMap<(ExpressionNodeKey, TypeContext<'db>), Type<'db>>;
+
 impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
     /// How big a string do we build before bailing?
     ///
@@ -332,6 +340,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             deferred_state: DeferredExpressionState::None,
             inferring_vararg_annotation: false,
             expressions: FxHashMap::default(),
+            expression_cache: None,
             string_annotations: FxHashSet::default(),
             bindings: VecMap::default(),
             declarations: VecMap::default(),
@@ -475,6 +484,22 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         }
     }

+    /// Setup a shared expression cache for multi-inference.
+    ///
+    /// Returns `false` if the expression cache was already initialized.
+    fn setup_expression_cache(&mut self) -> bool {
+        if self.expression_cache.is_some() {
+            false
+        } else {
+            self.expression_cache = Some(Rc::new(RefCell::new(FxHashMap::default())));
+            true
+        }
+    }
+
+    fn teardown_expression_cache(&mut self) {
+        self.expression_cache = None;
+    }
+
     /// Are we currently inferring types in file with deferred types?
     /// This is true for stub files, for files with `__future__.annotations`, and
     /// by default for all source files in Python 3.14 and later.
@@ -5329,6 +5354,12 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

                 let mut seen = FxHashSet::default();

+                // Cache expressions inferred across speculative inference attempts.
+                //
+                // This is important to avoid exponential blowup for deeply nested generic calls,
+                // as inner expressions are repeatedly inferred with the same type context.
+                let teardown = self.setup_expression_cache();
+
                 for (parameter, parameter_tcx) in parameter_types {
                     if !seen.insert(parameter.annotated_type()) {
                         continue;
@@ -5343,6 +5374,10 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                     );
                     argument_types.insert(parameter.annotated_type(), inferred_ty);
                 }
+
+                if teardown {
+                    self.teardown_expression_cache();
+                }
             }
         }
     }
@@ -5433,6 +5468,16 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         expression: &ast::Expr,
         tcx: TypeContext<'db>,
     ) -> Type<'db> {
+        if let Some(ty) = self.expression_cache.as_ref().and_then(|expression_cache| {
+            expression_cache
+                .borrow()
+                .get(&(expression.into(), tcx))
+                .copied()
+        }) {
+            self.store_expression_type(expression, ty);
+            return ty;
+        }
+
         let mut ty = match expression {
             ast::Expr::NoneLiteral(ast::ExprNoneLiteral {
                 range: _,
@@ -5493,6 +5538,12 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

         self.store_expression_type(expression, ty);

+        if let Some(expression_cache) = &self.expression_cache {
+            expression_cache
+                .borrow_mut()
+                .insert((expression.into(), tcx), ty);
+        }
+
         ty
     }

@@ -8921,6 +8972,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             undecorated_type: _,

             // builder only state
+            expression_cache: _,
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
@@ -8999,6 +9051,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             expressions,
             bindings,
             called_functions,
+            expression_cache: _,
             declarations: _,
             deferred: _,
             scope: _,
@@ -9043,7 +9096,9 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             cycle_recovery,
             undecorated_type,
             called_functions,
+
             // builder only state
+            expression_cache: _,
             dataclass_field_specifiers: _,
             all_definitely_bound: _,
             typevar_binding_context: _,
@@ -9125,6 +9180,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             undecorated_type: _,

             // Builder only state
+            expression_cache: _,
             dataclass_field_specifiers: _,
             all_definitely_bound: _,
             typevar_binding_context: _,
@@ -9169,6 +9225,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             inference_flags,
             typevar_binding_context,
             inferring_vararg_annotation,
+            ref expression_cache,
             ref return_types_and_ranges,
             ref dataclass_field_specifiers,

@@ -9197,6 +9254,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         builder.typevar_binding_context = typevar_binding_context;
         builder.inference_flags = inference_flags;
         builder.inferring_vararg_annotation = inferring_vararg_annotation;
+        builder.expression_cache.clone_from(expression_cache);
         builder
             .return_types_and_ranges
             .clone_from(return_types_and_ranges);
@@ -9224,6 +9282,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             undecorated_type: _,

             // builder only state
+            expression_cache: _,
             all_definitely_bound: _,
             typevar_binding_context: _,
             inference_flags: _,

PATCH

echo "Patch applied successfully."

# Rebuild ty
CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1 | tail -5
echo "Build complete."
