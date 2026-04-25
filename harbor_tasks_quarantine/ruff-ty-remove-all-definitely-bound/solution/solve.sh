#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: if all_definitely_bound is gone from infer.rs, patch already applied
if ! grep -q 'all_definitely_bound' crates/ty_python_semantic/src/types/infer.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix for trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/infer.rs b/crates/ty_python_semantic/src/types/infer.rs
index bb78a9e7216dc7..36669743123ced 100644
--- a/crates/ty_python_semantic/src/types/infer.rs
+++ b/crates/ty_python_semantic/src/types/infer.rs
@@ -908,9 +908,6 @@ struct ExpressionInferenceExtra<'db> {

     /// The fallback type for missing expressions/bindings/declarations or recursive type inference.
     cycle_recovery: Option<Type<'db>>,
-
-    /// `true` if all places in this expression are definitely bound
-    all_definitely_bound: bool,
 }

 impl<'db> ExpressionInference<'db> {
@@ -919,7 +916,6 @@ impl<'db> ExpressionInference<'db> {
         Self {
             extra: Some(Box::new(ExpressionInferenceExtra {
                 cycle_recovery: Some(cycle_recovery),
-                all_definitely_bound: true,
                 ..ExpressionInferenceExtra::default()
             })),
             expressions: FxHashMap::default(),

diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index 74bb3c7d394028..76486311c1e2fd 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -303,9 +303,6 @@ pub(super) struct TypeInferenceBuilder<'db, 'ast> {
     /// The fallback type for missing expressions/bindings/declarations or recursive type inference.
     cycle_recovery: Option<Type<'db>>,

-    /// `true` if all places in this expression are definitely bound
-    all_definitely_bound: bool,
-
     /// A list of `dataclass_transform` field specifiers that are "active" (when inferring
     /// the right hand side of an annotated assignment in a class that is a dataclass).
     dataclass_field_specifiers: SmallVec<[Type<'db>; NUM_FIELD_SPECIFIERS_INLINE]>,
@@ -349,7 +346,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             deferred: VecSet::default(),
             undecorated_type: None,
             cycle_recovery: None,
-            all_definitely_bound: true,
             dataclass_field_specifiers: SmallVec::new(),
         }
     }
@@ -7339,10 +7335,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 }
             });

-        if !resolved_after_fallback.place.is_definitely_bound() {
-            self.all_definitely_bound = false;
-        }
-
         let ty =
             resolved_after_fallback.unwrap_with_diagnostic(db, |lookup_error| match lookup_error {
                 LookupError::Undefined(qualifiers) => {
@@ -7900,19 +7892,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 assigned_type = Some(ty);
             }
         }
-        let mut fallback_place = value_type.member(db, &attr.id);
-        // Exclude non-definitely-bound places for purposes of reachability
-        // analysis. We currently do not perform boundness analysis for implicit
-        // instance attributes, so we exclude them here as well.
-        if !fallback_place.place.is_definitely_bound()
-            || fallback_place
-                .qualifiers
-                .contains(TypeQualifiers::IMPLICIT_INSTANCE_ATTRIBUTE)
-        {
-            self.all_definitely_bound = false;
-        }
-
-        fallback_place = fallback_place.map_type(|ty| {
+        let fallback_place = value_type.member(db, &attr.id).map_type(|ty| {
             self.narrow_expr_with_applicable_constraints(attribute, ty, &constraint_keys)
         });

@@ -8574,7 +8554,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             declarations,
             deferred,
             cycle_recovery,
-            all_definitely_bound,
             dataclass_field_specifiers: _,

             // Ignored; only relevant to definition regions
@@ -8604,7 +8583,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         );

         let extra =
-            (!string_annotations.is_empty() || cycle_recovery.is_some() || !bindings.is_empty() || !diagnostics.is_empty() || !all_definitely_bound).then(|| {
+            (!string_annotations.is_empty() || cycle_recovery.is_some() || !bindings.is_empty() || !diagnostics.is_empty()).then(|| {
                 if bindings.len() > 20 {
                     tracing::debug!(
                         "Inferred expression region `{:?}` contains {} bindings. Lookups by linear scan might be slow.",
@@ -8618,7 +8597,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                     bindings: bindings.into_boxed_slice(),
                     diagnostics,
                     cycle_recovery,
-                    all_definitely_bound,
                 })
             });

@@ -8673,7 +8651,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             index: _,
             region: _,
             cycle_recovery: _,
-            all_definitely_bound: _,
             qualifiers: _,
         } = self;
         let diagnostics = context.finish();
@@ -8709,7 +8686,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             // builder only state
             expression_cache: _,
             dataclass_field_specifiers: _,
-            all_definitely_bound: _,
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
@@ -8794,7 +8770,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             // Builder only state
             expression_cache: _,
             dataclass_field_specifiers: _,
-            all_definitely_bound: _,
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
@@ -8850,7 +8825,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             deferred: _,
             called_functions: _,
             undecorated_type: _,
-            all_definitely_bound: _,
             qualifiers: _,
         } = *self;

@@ -8893,7 +8867,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {

             // builder only state
             expression_cache: _,
-            all_definitely_bound: _,
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,

PATCH

echo "Patch applied successfully."
