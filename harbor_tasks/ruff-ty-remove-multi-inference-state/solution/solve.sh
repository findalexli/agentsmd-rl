#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if defuse() method already exists on InferContext, patch is applied
if grep -q 'pub(crate) fn defuse' crates/ty_python_semantic/src/types/context.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/context.rs b/crates/ty_python_semantic/src/types/context.rs
index a0f688981e98bc..a0b2de9ae07016 100644
--- a/crates/ty_python_semantic/src/types/context.rs
+++ b/crates/ty_python_semantic/src/types/context.rs
@@ -41,7 +41,6 @@ pub(crate) struct InferContext<'db, 'ast> {
     module: &'ast ParsedModuleRef,
     diagnostics: std::cell::RefCell<TypeCheckDiagnostics>,
     no_type_check: InNoTypeCheck,
-    multi_inference: bool,
     bomb: DebugDropBomb,
 }
 
@@ -52,7 +51,6 @@ impl<'db, 'ast> InferContext<'db, 'ast> {
             scope,
             module,
             file: scope.file(db),
-            multi_inference: false,
             diagnostics: std::cell::RefCell::new(TypeCheckDiagnostics::default()),
             no_type_check: InNoTypeCheck::default(),
             bomb: DebugDropBomb::new(
@@ -98,9 +96,7 @@ impl<'db, 'ast> InferContext<'db, 'ast> {
     }
 
     pub(crate) fn extend(&mut self, other: &TypeCheckDiagnostics) {
-        if !self.is_in_multi_inference() {
-            self.diagnostics.get_mut().extend(other);
-        }
+        self.diagnostics.get_mut().extend(other);
     }
 
     pub(super) fn is_lint_enabled(&self, lint: &'static LintMetadata) -> bool {
@@ -165,18 +161,6 @@ impl<'db, 'ast> InferContext<'db, 'ast> {
         DiagnosticGuardBuilder::new(self, id, severity)
     }
 
-    /// Returns `true` if the current expression is being inferred for a second
-    /// (or subsequent) time, with a potentially different bidirectional type
-    /// context.
-    pub(super) fn is_in_multi_inference(&self) -> bool {
-        self.multi_inference
-    }
-
-    /// Set the multi-inference state, returning the previous value.
-    pub(super) fn set_multi_inference(&mut self, multi_inference: bool) -> bool {
-        std::mem::replace(&mut self.multi_inference, multi_inference)
-    }
-
     pub(super) fn set_in_no_type_check(&mut self, no_type_check: InNoTypeCheck) -> InNoTypeCheck {
         std::mem::replace(&mut self.no_type_check, no_type_check)
     }
@@ -216,6 +200,10 @@ impl<'db, 'ast> InferContext<'db, 'ast> {
         self.file.is_stub(self.db())
     }
 
+    pub(crate) fn defuse(&mut self) {
+        self.bomb.defuse();
+    }
+
     #[must_use]
     pub(crate) fn finish(mut self) -> TypeCheckDiagnostics {
         self.bomb.defuse();
@@ -437,11 +425,6 @@ impl<'db, 'ctx> LintDiagnosticGuardBuilder<'db, 'ctx> {
         if ctx.is_in_no_type_check() {
             return None;
         }
-        // If this lint is being reported as part of multi-inference of a given expression,
-        // silence it to avoid duplicated diagnostics.
-        if ctx.is_in_multi_inference() {
-            return None;
-        }
 
         Some((severity, source))
     }
@@ -524,11 +507,6 @@ impl<'db, 'ctx> DiagnosticGuardBuilder<'db, 'ctx> {
         if !ctx.db.should_check_file(ctx.file) {
             return None;
         }
-        // If this lint is being reported as part of multi-inference of a given expression,
-        // silence it to avoid duplicated diagnostics.
-        if ctx.is_in_multi_inference() {
-            return None;
-        }
         Some(DiagnosticGuardBuilder { ctx, id, severity })
     }
 
diff --git a/crates/ty_python_semantic/src/types/infer/builder.rs b/crates/ty_python_semantic/src/types/infer/builder.rs
index d7940755c9258c..ebd1aa25f0a03b 100644
--- a/crates/ty_python_semantic/src/types/infer/builder.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder.rs
@@ -288,13 +288,6 @@ pub(super) struct TypeInferenceBuilder<'db, 'ast> {
     /// is a stub file but we're still in a non-deferred region.
     deferred_state: DeferredExpressionState,
 
-    multi_inference_state: MultiInferenceState,
-
-    /// If you cannot avoid the possibility of calling `infer(_type)_expression` multiple times for a given expression,
-    /// set this to `Get` after the expression has been inferred for the first time.
-    /// While this is `Get`, any expressions will be considered to have already been inferred.
-    inner_expression_inference_state: InnerExpressionInferenceState,
-
     inferring_vararg_annotation: bool,
 
     /// For function definitions, the undecorated type of the function.
@@ -336,8 +329,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             called_functions: FxIndexSet::default(),
             deferred_state: DeferredExpressionState::None,
             inferring_vararg_annotation: false,
-            multi_inference_state: MultiInferenceState::Panic,
-            inner_expression_inference_state: InnerExpressionInferenceState::Infer,
             expressions: FxHashMap::default(),
             string_annotations: FxHashSet::default(),
             bindings: VecMap::default(),
@@ -375,12 +366,10 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         assert_eq!(self.scope, inference.scope);
 
         self.expressions.extend(inference.expressions.iter());
-        self.declarations
-            .extend(inference.declarations(), self.multi_inference_state);
+        self.declarations.extend(inference.declarations());
 
         if !matches!(self.region, InferenceRegion::Scope(..)) {
-            self.bindings
-                .extend(inference.bindings(), self.multi_inference_state);
+            self.bindings.extend(inference.bindings());
         }
 
         if let Some(extra) = &inference.extra {
@@ -388,8 +377,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 .extend(extra.called_functions.iter().copied());
             self.extend_cycle_recovery(extra.cycle_recovery);
             self.context.extend(&extra.diagnostics);
-            self.deferred
-                .extend(extra.deferred.iter().copied(), self.multi_inference_state);
+            self.deferred.extend(extra.deferred.iter().copied());
             self.string_annotations
                 .extend(extra.string_annotations.iter().copied());
         }
@@ -412,8 +400,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 .extend(extra.string_annotations.iter().copied());
 
             if !matches!(self.region, InferenceRegion::Scope(..)) {
-                self.bindings
-                    .extend(extra.bindings.iter().copied(), self.multi_inference_state);
+                self.bindings.extend(extra.bindings.iter().copied());
             }
         }
     }
@@ -486,11 +473,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         }
     }
 
-    /// Set the multi-inference state, returning the previous value.
-    fn set_multi_inference_state(&mut self, state: MultiInferenceState) -> MultiInferenceState {
-        std::mem::replace(&mut self.multi_inference_state, state)
-    }
-
     /// Are we currently inferring types in file with deferred types?
     /// This is true for stub files, for files with `__future__.annotations`, and
     /// by default for all source files in Python 3.14 and later.
@@ -1137,8 +1119,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             }
             TypeAndQualifiers::declared(Type::unknown())
         };
-        self.declarations
-            .insert(declaration, ty, self.multi_inference_state);
+        self.declarations.insert(declaration, ty);
     }
 
     fn add_declaration_with_binding(
@@ -1213,10 +1194,8 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             }
         };
 
-        self.declarations
-            .insert(definition, declared_ty, self.multi_inference_state);
-        self.bindings
-            .insert(definition, inferred_ty, self.multi_inference_state);
+        self.declarations.insert(definition, declared_ty);
+        self.bindings.insert(definition, inferred_ty);
     }
 
     fn add_unknown_declaration_with_binding(
@@ -1781,8 +1760,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             union.add_in_place(narrowed_ty);
         }
 
-        self.bindings
-            .insert(definition, union.build(), self.multi_inference_state);
+        self.bindings.insert(definition, union.build());
     }
 
     fn infer_match_statement(&mut self, match_statement: &ast::StmtMatch) {
@@ -3037,7 +3015,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         }
 
         // Inference of `tp` must be deferred, to avoid cycles.
-        self.deferred.insert(definition, self.multi_inference_state);
+        self.deferred.insert(definition);
 
         Type::KnownInstance(KnownInstanceType::NewType(NewType::new(
             db,
@@ -3273,7 +3251,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         }
 
         // Inference of the value argument must be deferred, to avoid cycles.
-        self.deferred.insert(definition, self.multi_inference_state);
+        self.deferred.insert(definition);
 
         Type::KnownInstance(KnownInstanceType::TypeAliasType(
             TypeAliasType::ManualPEP695(ManualPEP695TypeAliasType::new(
@@ -3557,7 +3535,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         //   and store the explicit bases directly (since they were inferred eagerly).
         let anchor = if let Some(def) = definition {
             // Register for deferred inference to infer bases and validate later.
-            self.deferred.insert(def, self.multi_inference_state);
+            self.deferred.insert(def);
             DynamicClassAnchor::Definition(def)
         } else {
             let call_node_index = call_expr.node_index().load();
@@ -5074,7 +5052,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 )
                 .is_err()
             {
-                speculative_builder.discard();
                 return None;
             }
 
@@ -5087,7 +5064,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 .return_type(db)
                 .is_assignable_to(db, narrowed_ty)
             {
-                speculative_builder.discard();
                 return None;
             }
 
@@ -5326,13 +5302,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                     infer_argument_ty(self, (argument_index, ast_argument, TypeContext::default())),
                 );
 
-                // We then silence any diagnostics emitted during multi-inference, as the type context is only
-                // used as a hint to infer a more assignable argument type, and should not lead to diagnostics
-                // for non-matching overloads.
-                let was_in_multi_inference = self.context.set_multi_inference(true);
-                let prev_multi_inference_state =
-                    self.set_multi_inference_state(MultiInferenceState::Ignore);
-
                 // Infer the type of each argument once with each distinct parameter type as type context.
                 let parameter_types = overloads_with_binding
                     .iter()
@@ -5345,14 +5314,15 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                         continue;
                     }
 
-                    let inferred_ty =
-                        infer_argument_ty(self, (argument_index, ast_argument, parameter_tcx));
+                    // We use a speculative builder to silence any diagnostics emitted during multi-inference, as the
+                    // type context is only used as a hint to infer a more assignable argument type, and should not lead
+                    // to diagnostics for non-matching overloads.
+                    let inferred_ty = infer_argument_ty(
+                        &mut self.speculate(),
+                        (argument_index, ast_argument, parameter_tcx),
+                    );
                     argument_types.insert(parameter.annotated_type(), inferred_ty);
                 }
-
-                // Re-enable diagnostics.
-                self.context.set_multi_inference(was_in_multi_inference);
-                self.set_multi_inference_state(prev_multi_inference_state);
             }
         }
     }
@@ -5443,9 +5413,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         expression: &ast::Expr,
         tcx: TypeContext<'db>,
     ) -> Type<'db> {
-        if self.inner_expression_inference_state.is_get() {
-            return self.expression_type(expression);
-        }
         let mut ty = match expression {
             ast::Expr::NoneLiteral(ast::ExprNoneLiteral {
                 range: _,
@@ -5487,16 +5454,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             ast::Expr::Yield(yield_expression) => self.infer_yield_expression(yield_expression),
             ast::Expr::YieldFrom(yield_from) => self.infer_yield_from_expression(yield_from),
             ast::Expr::Await(await_expression) => self.infer_await_expression(await_expression),
-            ast::Expr::Named(named) => {
-                // Definitions must be unique, so we bypass multi-inference for named expressions.
-                if !self.multi_inference_state.is_panic()
-                    && let Some(ty) = self.expressions.get(&expression.into())
-                {
-                    return *ty;
-                }
-
-                self.infer_named_expression(named)
-            }
+            ast::Expr::Named(named) => self.infer_named_expression(named),
             ast::Expr::IpyEscapeCommand(_) => {
                 todo_type!("Ipy escape command support")
             }
@@ -5520,19 +5478,8 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
 
     #[track_caller]
     fn store_expression_type(&mut self, expression: &ast::Expr, ty: Type<'db>) {
-        if self.inner_expression_inference_state.is_get() {
-            // If `inner_expression_inference_state` is `Get`, the expression type has already been stored.
-            return;
-        }
-
-        match self.multi_inference_state {
-            MultiInferenceState::Ignore => {}
-
-            MultiInferenceState::Panic => {
-                let previous = self.expressions.insert(expression.into(), ty);
-                assert_eq!(previous, None);
-            }
-        }
+        let previous = self.expressions.insert(expression.into(), ty);
+        assert_eq!(previous, None);
     }
 
     fn infer_number_literal_expression(&self, literal: &ast::ExprNumberLiteral) -> Type<'db> {
@@ -5910,29 +5857,24 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                         item_types.insert(item.value.node_index().load(), value_ty);
                     }
 
-                    // Disable diagnostics as we attempt to narrow to specific `TypedDict`
-                    // elements of the union. Mixed unions like `TypedDict | dict[str, Any]`
-                    // should not emit `TypedDict` diagnostics if a non-`TypedDict` arm accepts
-                    // the literal.
-                    let old_multi_inference = self.context.set_multi_inference(true);
-                    let old_multi_inference_state =
-                        self.set_multi_inference_state(MultiInferenceState::Ignore);
-
                     let mut narrowed_tys = Vec::new();
                     let mut item_types = FxHashMap::default();
                     for typed_dict in typed_dicts {
-                        if let Some(inferred_ty) =
-                            self.infer_typed_dict_expression(dict, typed_dict, &mut item_types)
-                        {
+                        // Disable diagnostics as we attempt to narrow to specific `TypedDict`
+                        // elements of the union. Mixed unions like `TypedDict | dict[str, Any]`
+                        // should not emit `TypedDict` diagnostics if a non-`TypedDict` arm accepts
+                        // the literal.
+                        if let Some(inferred_ty) = self.speculate().infer_typed_dict_expression(
+                            dict,
+                            typed_dict,
+                            &mut item_types,
+                        ) {
                             narrowed_tys.push(inferred_ty);
                         }
 
                         item_types.clear();
                     }
 
-                    self.context.set_multi_inference(old_multi_inference);
-                    self.set_multi_inference_state(old_multi_inference_state);
-
                     // Successfully narrowed to a subset of typed dicts.
                     if !narrowed_tys.is_empty() {
                         return UnionType::from_elements(self.db(), narrowed_tys);
@@ -6041,7 +5983,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
 
             // Ensure the inferred return type is assignable to the narrowed declared type.
             if !inferred_ty.is_assignable_to(db, narrowed_ty) {
-                speculative_builder.discard();
                 return None;
             }
 
@@ -9001,8 +8942,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
-            multi_inference_state: _,
-            inner_expression_inference_state: _,
             inferring_vararg_annotation: _,
             called_functions: _,
             index: _,
@@ -9088,8 +9027,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
-            multi_inference_state: _,
-            inner_expression_inference_state: _,
             inferring_vararg_annotation: _,
             index: _,
             region: _,
@@ -9131,8 +9068,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             inference_flags: _,
             deferred_state: _,
             inferring_vararg_annotation: _,
-            multi_inference_state: _,
-            inner_expression_inference_state: _,
             index: _,
             region: _,
             return_types_and_ranges: _,
@@ -9213,8 +9148,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
-            multi_inference_state: _,
-            inner_expression_inference_state: _,
             inferring_vararg_annotation: _,
             called_functions: _,
             index: _,
@@ -9244,9 +9177,52 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
     /// to speculatively infer expressions during multi-inference.
     ///
     /// The inference results can be merged into the current inference region using
-    /// [`TypeInferenceBuilder::extend`], or ignored using [`TypeInferenceBuilder::discard`].
+    /// [`TypeInferenceBuilder::extend`].
     fn speculate(&mut self) -> Self {
-        TypeInferenceBuilder::new(self.db(), self.region, self.index, self.module())
+        let Self {
+            region,
+            index,
+            cycle_recovery,
+            deferred_state,
+            inference_flags,
+            typevar_binding_context,
+            inferring_vararg_annotation,
+            ref return_types_and_ranges,
+            ref dataclass_field_specifiers,
+
+            // These fields are type inference results, but do not affect the inference of a given
+            // expression.
+            context: _,
+            expressions: _,
+            string_annotations: _,
+            scope: _,
+            bindings: _,
+            declarations: _,
+            deferred: _,
+            called_functions: _,
+            undecorated_type: _,
+            all_definitely_bound: _,
+        } = *self;
+
+        let mut builder = TypeInferenceBuilder::new(self.db(), region, index, self.module());
+
+        // Speculated builders are often discarded immediately.
+        builder.context.defuse();
+
+        // Ensure the speculative builder has the same inference context as the current one.
+        builder.cycle_recovery = cycle_recovery;
+        builder.deferred_state = deferred_state;
+        builder.typevar_binding_context = typevar_binding_context;
+        builder.inference_flags = inference_flags;
+        builder.inferring_vararg_annotation = inferring_vararg_annotation;
+        builder
+            .return_types_and_ranges
+            .clone_from(return_types_and_ranges);
+        builder
+            .dataclass_field_specifiers
+            .clone_from(dataclass_field_specifiers);
+
+        builder
     }
 
     /// Extend the current region with the results of a speculative [`TypeInferenceBuilder`].
@@ -9270,8 +9246,6 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             typevar_binding_context: _,
             inference_flags: _,
             deferred_state: _,
-            multi_inference_state: _,
-            inner_expression_inference_state: _,
             inferring_vararg_annotation: _,
             called_functions: _,
             index: _,
@@ -9298,20 +9272,10 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             .extend(string_annotations.iter().copied());
 
         if !matches!(self.region, InferenceRegion::Scope(..)) {
-            self.bindings.extend(
-                bindings.iter().map(|(def, ty)| (*def, *ty)),
-                self.multi_inference_state,
-            );
+            self.bindings
+                .extend(bindings.iter().map(|(def, ty)| (*def, *ty)));
         }
     }
-
-    /// Ignore the results of this [`TypeInferenceBuilder`].
-    ///
-    /// Note that dropping a [`TypeInferenceBuilder`] without calling this method will result
-    /// in a panic.
-    fn discard(self) {
-        let _ = self.context.finish();
-    }
 }
 
 /// Manages the inference of a given expression.
@@ -9362,18 +9326,8 @@ impl<'db, 'ast, 'infer> MultiInferenceGuard<'db, 'ast, 'infer> {
         builder: &mut TypeInferenceBuilder<'db, 'ast>,
         tcx: TypeContext<'db>,
     ) -> Type<'db> {
-        let prev_multi_inference_state =
-            builder.set_multi_inference_state(MultiInferenceState::Ignore);
-        let was_in_multi_inference = builder.context.set_multi_inference(true);
-
-        let value_ty = (self.infer_expr)(builder, tcx);
         self.last_tcx = Some(tcx);
-
-        // Reset the multi-inference state.
-        builder.set_multi_inference_state(prev_multi_inference_state);
-        builder.context.set_multi_inference(was_in_multi_inference);
-
-        value_ty
+        (self.infer_expr)(&mut builder.speculate(), tcx)
     }
 
     fn last_tcx(&self) -> TypeContext<'db> {
@@ -9422,36 +9376,6 @@ impl<'a> Iterator for ArgumentsIter<'a> {
     }
 }
 
-/// Dictates the behavior when an expression is inferred multiple times.
-#[derive(Default, Debug, Clone, Copy)]
-enum MultiInferenceState {
-    /// Panic if the expression has already been inferred.
-    #[default]
-    Panic,
-
-    /// Ignore the newly inferred value.
-    Ignore,
-}
-
-impl MultiInferenceState {
-    const fn is_panic(self) -> bool {
-        matches!(self, MultiInferenceState::Panic)
-    }
-}
-
-#[derive(Default, Debug, Clone, Copy)]
-enum InnerExpressionInferenceState {
-    #[default]
-    Infer,
-    Get,
-}
-
-impl InnerExpressionInferenceState {
-    const fn is_get(self) -> bool {
-        matches!(self, InnerExpressionInferenceState::Get)
-    }
-}
-
 /// The deferred state of a specific expression in an inference region.
 #[derive(Default, Debug, Clone, Copy)]
 enum DeferredExpressionState {
@@ -9608,11 +9532,7 @@ where
     K: std::fmt::Debug,
     V: std::fmt::Debug,
 {
-    fn insert(&mut self, key: K, value: V, multi_inference_state: MultiInferenceState) {
-        if matches!(multi_inference_state, MultiInferenceState::Ignore) {
-            return;
-        }
-
+    fn insert(&mut self, key: K, value: V) {
         debug_assert!(
             !self.0.iter().any(|(existing, _)| existing == &key),
             "An existing entry already exists for key {key:?}",
@@ -9622,14 +9542,10 @@ where
     }
 
     #[inline]
-    fn extend<T: IntoIterator<Item = (K, V)>>(
-        &mut self,
-        iter: T,
-        multi_inference_state: MultiInferenceState,
-    ) {
+    fn extend<T: IntoIterator<Item = (K, V)>>(&mut self, iter: T) {
         if cfg!(debug_assertions) {
             for (key, value) in iter {
-                self.insert(key, value, multi_inference_state);
+                self.insert(key, value);
             }
         } else {
             self.0.extend(iter);
@@ -9696,11 +9612,7 @@ where
     V: Eq,
     V: std::fmt::Debug,
 {
-    fn insert(&mut self, value: V, multi_inference_state: MultiInferenceState) {
-        if matches!(multi_inference_state, MultiInferenceState::Ignore) {
-            return;
-        }
-
+    fn insert(&mut self, value: V) {
         debug_assert!(
             !self.0.iter().any(|existing| existing == &value),
             "An existing entry already exists for {value:?}",
@@ -9716,14 +9628,10 @@ where
     V: std::fmt::Debug,
 {
     #[inline]
-    fn extend<T: IntoIterator<Item = V>>(
-        &mut self,
-        iter: T,
-        multi_inference_state: MultiInferenceState,
-    ) {
+    fn extend<T: IntoIterator<Item = V>>(&mut self, iter: T) {
         if cfg!(debug_assertions) {
             for value in iter {
-                self.insert(value, multi_inference_state);
+                self.insert(value);
             }
         } else {
             self.0.extend(iter);
@@ -9861,9 +9769,7 @@ impl<'db, 'ast> AddBinding<'db, 'ast> {
             }
         }
 
-        builder
-            .bindings
-            .insert(self.binding, bound_ty, builder.multi_inference_state);
+        builder.bindings.insert(self.binding, bound_ty);
 
         inferred_ty
     }
diff --git a/crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs b/crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs
index bf05e80d713356..bd36a0649da657 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs
@@ -1,6 +1,6 @@
 use ruff_python_ast::{self as ast, AnyNodeRef};
 
-use super::{MultiInferenceState, TypeInferenceBuilder};
+use super::TypeInferenceBuilder;
 use crate::Db;
 use crate::types::call::CallArguments;
 use crate::types::constraints::ConstraintSetBuilder;
@@ -162,17 +162,11 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
     ) -> Option<Type<'db>> {
         let db = self.db();
 
-        let old_multi_inference = self.context.set_multi_inference(true);
-        let old_multi_inference_state = self.set_multi_inference_state(MultiInferenceState::Ignore);
-
-        let update_ty = self.infer_expression(
+        let update_ty = self.speculate().infer_expression(
             update,
             TypeContext::new(Some(Type::TypedDict(update_context_typed_dict))),
         );
 
-        self.context.set_multi_inference(old_multi_inference);
-        self.set_multi_inference_state(old_multi_inference_state);
-
         Type::TypedDict(result_typed_dict)
             .try_call_dunder(
                 db,
diff --git a/crates/ty_python_semantic/src/types/infer/builder/class.rs b/crates/ty_python_semantic/src/types/infer/builder/class.rs
index dcc28a41cba178..49932f7d0c748b 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/class.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/class.rs
@@ -225,7 +225,7 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                     .iter()
                     .any(|expr| any_over_expr(expr, &ast::Expr::is_string_literal_expr))
             {
-                self.deferred.insert(definition, self.multi_inference_state);
+                self.deferred.insert(definition);
             } else {
                 let previous_typevar_binding_context =
                     self.typevar_binding_context.replace(definition);
diff --git a/crates/ty_python_semantic/src/types/infer/builder/function.rs b/crates/ty_python_semantic/src/types/infer/builder/function.rs
index 841a4dc23dca25..824f69e12e0cc3 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/function.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/function.rs
@@ -228,8 +228,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 .iter()
                 .map(|(expression, ty)| (*expression, *ty)),
         );
-        self.bindings
-            .extend(decorator_inference.bindings(), self.multi_inference_state);
+        self.bindings.extend(decorator_inference.bindings());
         self.called_functions
             .extend(decorator_inference.called_functions().iter().copied());
 
@@ -305,7 +304,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         // (lazily) inferring the parameter and return types.) If defaults exist, we also defer so
         // they can be inferred once with type context in the enclosing scope.
         if type_params.is_none() || has_defaults {
-            self.deferred.insert(definition, self.multi_inference_state);
+            self.deferred.insert(definition);
         }
 
         let known_function = KnownFunction::try_from_definition_and_name(db, definition, name);
diff --git a/crates/ty_python_semantic/src/types/infer/builder/named_tuple.rs b/crates/ty_python_semantic/src/types/infer/builder/named_tuple.rs
index c503461f8423ff..350b1ce65b8e5f 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/named_tuple.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/named_tuple.rs
@@ -367,7 +367,7 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                     // The `fields` argument to `typing.NamedTuple` cannot be inferred
                     // eagerly if it's not a dangling call, as it may contain forward references
                     // or recursive references.
-                    self.deferred.insert(definition, self.multi_inference_state);
+                    self.deferred.insert(definition);
                     DynamicNamedTupleAnchor::TypingDefinition(definition)
                 }
             },
diff --git a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
index 8af0b0dbd5a43d..14a96467aad2a1 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/type_expression.rs
@@ -9,7 +9,6 @@ use crate::types::diagnostic::{
     report_invalid_arguments_to_callable, report_invalid_concatenate_last_arg,
 };
 use crate::types::infer::InferenceFlags;
-use crate::types::infer::builder::{InnerExpressionInferenceState, MultiInferenceState};
 use crate::types::signatures::{ConcatenateTail, Signature};
 use crate::types::special_form::{AliasSpec, LegacyStdlibAlias};
 use crate::types::string_annotation::parse_string_annotation;
@@ -27,9 +26,6 @@ use crate::{FxOrderSet, Program, add_inferred_python_version_hint_to_diagnostic}
 impl<'db> TypeInferenceBuilder<'db, '_> {
     /// Infer the type of a type expression.
     pub(super) fn infer_type_expression(&mut self, expression: &ast::Expr) -> Type<'db> {
-        if self.inner_expression_inference_state.is_get() {
-            return self.expression_type(expression);
-        }
         let previous_deferred_state = self.deferred_state;
 
         // `DeferredExpressionState::InStringAnnotation` takes precedence over other states.
@@ -78,9 +74,6 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
 
     /// Infer the type of a type expression without storing the result.
     pub(super) fn infer_type_expression_no_store(&mut self, expression: &ast::Expr) -> Type<'db> {
-        if self.inner_expression_inference_state.is_get() {
-            return self.expression_type(expression);
-        }
         // https://typing.python.org/en/latest/spec/annotations.html#grammar-token-expression-grammar-type_expression
         match expression {
             ast::Expr::Name(name) => match name.ctx {
@@ -162,20 +155,16 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
                         if !self.deferred_state.is_deferred()
                             && !self.scope.scope(self.db()).in_type_checking_block()
                         {
-                            let previous_state =
-                                self.set_multi_inference_state(MultiInferenceState::Ignore);
-                            let was_in_multi_inference = self.context.set_multi_inference(true);
+                            let mut speculative_builder = self.speculate();
                             // If the left-hand side of the union is itself a PEP-604 union,
                             // we'll already have checked whether it can be used with `|` in a previous inference step
                             // and emitted a diagnostic if it was appropriate. We should skip inferring it here to
                             // avoid duplicate diagnostics; just assume that the l.h.s. is a `UnionType` instance
                             // in that case.
-                            let left_type_value =
-                                self.infer_expression(&binary.left, TypeContext::default());
-                            let right_type_value =
-                                self.infer_expression(&binary.right, TypeContext::default());
-                            self.multi_inference_state = previous_state;
-                            self.context.set_multi_inference(was_in_multi_inference);
+                            let left_type_value = speculative_builder
+                                .infer_expression(&binary.left, TypeContext::default());
+                            let right_type_value = speculative_builder
+                                .infer_expression(&binary.right, TypeContext::default());
 
                             let dunder_fails = Type::try_call_bin_op(
                                 self.db(),
@@ -1405,15 +1394,13 @@ impl<'db> TypeInferenceBuilder<'db, '_> {
             }
             Type::Union(union) => {
                 self.infer_type_expression(slice);
-                let previous_slice_inference_state = std::mem::replace(
-                    &mut self.inner_expression_inference_state,
-                    InnerExpressionInferenceState::Get,
-                );
-                let union = union.map(self.db(), |element| {
-                    self.infer_subscript_type_expression(subscript, *element)
-                });
-                self.inner_expression_inference_state = previous_slice_inference_state;
-                union
+                union.map(self.db(), |element| {
+                    let mut speculative_builder = self.speculate();
+                    let subscript_ty =
+                        speculative_builder.infer_subscript_type_expression(subscript, *element);
+                    self.context.extend(&speculative_builder.context.finish());
+                    subscript_ty
+                })
             }
             _ => {
                 self.infer_type_expression(slice);
diff --git a/crates/ty_python_semantic/src/types/infer/builder/typevar.rs b/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
index 06d908365e6b2d..a0b0e1b20ce3dc 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/typevar.rs
@@ -62,7 +62,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
             None => None,
         };
         if bound_or_constraint.is_some() || default.is_some() {
-            self.deferred.insert(definition, self.multi_inference_state);
+            self.deferred.insert(definition);
         }
         let identity = TypeVarIdentity::new(db, &name.id, Some(definition), TypeVarKind::Pep695);
         let ty = Type::KnownInstance(KnownInstanceType::TypeVar(TypeVarInstance::new(
@@ -541,7 +541,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         let db = self.db();
 
         if default.is_some() {
-            self.deferred.insert(definition, self.multi_inference_state);
+            self.deferred.insert(definition);
         }
         let identity =
             TypeVarIdentity::new(db, &name.id, Some(definition), TypeVarKind::Pep695ParamSpec);
@@ -807,7 +807,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         }
 
         if default.is_some() {
-            self.deferred.insert(definition, self.multi_inference_state);
+            self.deferred.insert(definition);
         }
 
         let identity =
@@ -1049,7 +1049,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
         };
 
         if bound_or_constraints.is_some() || default.is_some() {
-            self.deferred.insert(definition, self.multi_inference_state);
+            self.deferred.insert(definition);
         }
 
         let identity = TypeVarIdentity::new(db, target_name, Some(definition), TypeVarKind::Legacy);

PATCH
