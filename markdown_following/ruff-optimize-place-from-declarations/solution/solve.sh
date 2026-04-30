#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'DeclarationsBoundnessEvaluator' crates/ty_python_semantic/src/place.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/place.rs b/crates/ty_python_semantic/src/place.rs
index ca08bf043ffc0..9146c6f32bdcc 100644
--- a/crates/ty_python_semantic/src/place.rs
+++ b/crates/ty_python_semantic/src/place.rs
@@ -1,4 +1,6 @@
+use itertools::Either;
 use ruff_db::files::File;
+use ruff_index::IndexVec;
 use ruff_python_ast::PythonVersion;
 use ty_module_resolver::{
     KnownModule, Module, ModuleName, file_to_module, resolve_module_confident,
@@ -8,10 +10,11 @@ use crate::dunder_all::dunder_all_names;
 use crate::semantic_index::definition::{Definition, DefinitionKind, DefinitionState};
 use crate::semantic_index::narrowing_constraints::ScopedNarrowingConstraint;
 use crate::semantic_index::place::{PlaceExprRef, ScopedPlaceId};
+use crate::semantic_index::predicate::{Predicate, ScopedPredicateId};
 use crate::semantic_index::scope::ScopeId;
 use crate::semantic_index::{
-    BindingWithConstraints, BindingWithConstraintsIterator, DeclarationsIterator, get_loop_header,
-    place_table,
+    BindingWithConstraints, BindingWithConstraintsIterator, DeclarationsIterator,
+    ReachabilityConstraints, get_loop_header, place_table,
 };
 use crate::semantic_index::{DeclarationWithConstraint, global_scope, use_def_map};
 use crate::types::{
@@ -1069,6 +1072,62 @@ pub(crate) fn place_by_id<'db>(
     // every path has either a binding or a declaration for it.)
 }

+enum DeclarationsBoundnessEvaluator<'map, 'db> {
+    AssumeBound,
+    BasedOnUnboundVisibility {
+        unbound_visibility: Option<DeclarationWithConstraint<'db>>,
+        reachability_constraints: &'map ReachabilityConstraints,
+        predicates: &'map IndexVec<ScopedPredicateId, Predicate<'db>>,
+        requires_explicit_reexport: RequiresExplicitReExport,
+    },
+}
+
+impl<'db> DeclarationsBoundnessEvaluator<'_, 'db> {
+    fn evaluate(self, db: &'db dyn Db, all_declarations_definitely_reachable: bool) -> Definedness {
+        match self {
+            DeclarationsBoundnessEvaluator::AssumeBound => {
+                if all_declarations_definitely_reachable {
+                    Definedness::AlwaysDefined
+                } else {
+                    // For declarations, it is important to consider the possibility that they might only
+                    // be bound in one control flow path, while the other path contains a binding. In order
+                    // to even consider the bindings as well in `place_by_id`, we return `PossiblyUndefined`
+                    // here.
+                    Definedness::PossiblyUndefined
+                }
+            }
+            DeclarationsBoundnessEvaluator::BasedOnUnboundVisibility {
+                reachability_constraints,
+                unbound_visibility,
+                predicates,
+                requires_explicit_reexport,
+            } => {
+                let undeclared_reachability = match unbound_visibility {
+                    Some(DeclarationWithConstraint {
+                        declaration,
+                        reachability_constraint,
+                    }) if declaration.is_undefined_or(|def| {
+                        is_non_exported(db, def, requires_explicit_reexport)
+                    }) =>
+                    {
+                        reachability_constraints.evaluate(db, predicates, reachability_constraint)
+                    }
+                    _ => Truthiness::AlwaysFalse,
+                };
+                match undeclared_reachability {
+                    Truthiness::AlwaysTrue => {
+                        unreachable!(
+                            "If we have at least one declaration, the implicit `unbound` binding should not be definitely visible"
+                        )
+                    }
+                    Truthiness::AlwaysFalse => Definedness::AlwaysDefined,
+                    Truthiness::Ambiguous => Definedness::PossiblyUndefined,
+                }
+            }
+        }
+    }
+}
+
 /// Implementation of [`symbol`].
 fn symbol_impl<'db>(
     db: &'db dyn Db,
@@ -1314,9 +1373,9 @@ fn place_from_bindings_impl<'db>(
                     return None;
                 }
                 DefinitionState::Deleted => {
-                    deleted_reachability = deleted_reachability.or(
+                    deleted_reachability = deleted_reachability.or_else(|| {
                         reachability_constraints.evaluate(db, predicates, reachability_constraint)
-                    );
+                    });
                     return None;
                 }
             };
@@ -1585,59 +1644,64 @@ impl<'db> DeclaredTypeBuilder<'db> {
 /// access any AST nodes from the file containing the declarations.
 fn place_from_declarations_impl<'db>(
     db: &'db dyn Db,
-    declarations: DeclarationsIterator<'_, 'db>,
+    declarations_iterator: DeclarationsIterator<'_, 'db>,
     requires_explicit_reexport: RequiresExplicitReExport,
 ) -> PlaceFromDeclarationsResult<'db> {
-    let predicates = declarations.predicates;
-    let reachability_constraints = declarations.reachability_constraints;
-    let boundness_analysis = declarations.boundness_analysis;
-    let mut declarations = declarations.peekable();
-    let mut first_declaration = None;
+    let predicates = declarations_iterator.predicates;
+    let reachability_constraints = declarations_iterator.reachability_constraints;
+    let boundness_analysis = declarations_iterator.boundness_analysis;

-    let is_non_exported = |declaration: Definition<'db>| {
-        requires_explicit_reexport.is_yes() && !is_reexported(db, declaration)
-    };
+    let declarations;

-    let undeclared_reachability = match declarations.peek() {
-        Some(DeclarationWithConstraint {
-            declaration,
-            reachability_constraint,
-        }) if declaration.is_undefined_or(is_non_exported) => {
-            reachability_constraints.evaluate(db, predicates, *reachability_constraint)
+    let boundness_evaluator = match boundness_analysis {
+        BoundnessAnalysis::AssumeBound => {
+            declarations = Either::Left(declarations_iterator);
+            DeclarationsBoundnessEvaluator::AssumeBound
+        }
+        BoundnessAnalysis::BasedOnUnboundVisibility => {
+            let mut declarations_iterator = declarations_iterator.peekable();
+            let unbound_visibility = declarations_iterator.peek().cloned();
+            declarations = Either::Right(declarations_iterator);
+            DeclarationsBoundnessEvaluator::BasedOnUnboundVisibility {
+                unbound_visibility,
+                predicates,
+                reachability_constraints,
+                requires_explicit_reexport,
+            }
         }
-        _ => Truthiness::AlwaysFalse,
     };

+    let mut first_declaration = None;
     let mut all_declarations_definitely_reachable = true;

-    let mut types = declarations.filter_map(
-        |DeclarationWithConstraint {
-             declaration,
-             reachability_constraint,
-         }| {
-            let DefinitionState::Defined(declaration) = declaration else {
-                return None;
-            };
+    let mut types = declarations.filter_map(|declaration_with_constraint| {
+        let DeclarationWithConstraint {
+            declaration,
+            reachability_constraint,
+        } = declaration_with_constraint;

-            if is_non_exported(declaration) {
-                return None;
-            }
+        let DefinitionState::Defined(declaration) = declaration else {
+            return None;
+        };

-            first_declaration.get_or_insert(declaration);
+        if is_non_exported(db, declaration, requires_explicit_reexport) {
+            return None;
+        }

-            let static_reachability =
-                reachability_constraints.evaluate(db, predicates, reachability_constraint);
+        first_declaration.get_or_insert(declaration);

-            if static_reachability.is_always_false() {
-                None
-            } else {
-                all_declarations_definitely_reachable =
-                    all_declarations_definitely_reachable && static_reachability.is_always_true();
+        let static_reachability =
+            reachability_constraints.evaluate(db, predicates, reachability_constraint);

-                Some(declaration_type(db, declaration))
-            }
-        },
-    );
+        if static_reachability.is_always_false() {
+            None
+        } else {
+            all_declarations_definitely_reachable =
+                all_declarations_definitely_reachable && static_reachability.is_always_true();
+
+            Some(declaration_type(db, declaration))
+        }
+    });

     if let Some(first) = types.next() {
         let (declared, conflicting) = if let Some(second) = types.next() {
@@ -1652,28 +1716,7 @@ fn place_from_declarations_impl<'db>(
             (first, None)
         };

-        let boundness = match boundness_analysis {
-            BoundnessAnalysis::AssumeBound => {
-                if all_declarations_definitely_reachable {
-                    Definedness::AlwaysDefined
-                } else {
-                    // For declarations, it is important to consider the possibility that they might only
-                    // be bound in one control flow path, while the other path contains a binding. In order
-                    // to even consider the bindings as well in `place_by_id`, we return `PossiblyUnbound`
-                    // here.
-                    Definedness::PossiblyUndefined
-                }
-            }
-            BoundnessAnalysis::BasedOnUnboundVisibility => match undeclared_reachability {
-                Truthiness::AlwaysTrue => {
-                    unreachable!(
-                        "If we have at least one declaration, the implicit `unbound` binding should not be definitely visible"
-                    )
-                }
-                Truthiness::AlwaysFalse => Definedness::AlwaysDefined,
-                Truthiness::Ambiguous => Definedness::PossiblyUndefined,
-            },
-        };
+        let boundness = boundness_evaluator.evaluate(db, all_declarations_definitely_reachable);

         let place_and_quals = Place::Defined(
             DefinedPlace::new(declared.inner_type())
@@ -1696,6 +1739,14 @@ fn place_from_declarations_impl<'db>(
     }
 }

+fn is_non_exported<'db>(
+    db: &'db dyn Db,
+    declaration: Definition<'db>,
+    requires_explicit_reexport: RequiresExplicitReExport,
+) -> bool {
+    requires_explicit_reexport.is_yes() && !is_reexported(db, declaration)
+}
+
 // Returns `true` if the `definition` is re-exported.
 //
 // This will first check if the definition is using the "redundant alias" pattern like `import foo
diff --git a/crates/ty_python_semantic/src/semantic_index.rs b/crates/ty_python_semantic/src/semantic_index.rs
index 777d2edeab59e..ac43b50c3c818 100644
--- a/crates/ty_python_semantic/src/semantic_index.rs
+++ b/crates/ty_python_semantic/src/semantic_index.rs
@@ -30,6 +30,7 @@ use crate::semantic_index::scope::{
 use crate::semantic_index::symbol::ScopedSymbolId;
 use crate::semantic_index::use_def::{EnclosingSnapshotKey, ScopedEnclosingSnapshotId, UseDefMap};
 use crate::semantic_model::HasTrackedScope;
+pub(crate) use reachability_constraints::ReachabilityConstraints;

 pub mod ast_ids;
 mod builder;
diff --git a/crates/ty_python_semantic/src/semantic_index/use_def.rs b/crates/ty_python_semantic/src/semantic_index/use_def.rs
index 8fe2324174ab5..6312e37d015b4 100644
--- a/crates/ty_python_semantic/src/semantic_index/use_def.rs
+++ b/crates/ty_python_semantic/src/semantic_index/use_def.rs
@@ -856,7 +856,7 @@ pub(crate) struct DeclarationsIterator<'map, 'db> {
     inner: LiveDeclarationsIterator<'map>,
 }

-#[derive(Debug)]
+#[derive(Debug, Clone)]
 pub(crate) struct DeclarationWithConstraint<'db> {
     pub(crate) declaration: DefinitionState<'db>,
     pub(crate) reachability_constraint: ScopedReachabilityConstraintId,
diff --git a/crates/ty_python_semantic/src/types.rs b/crates/ty_python_semantic/src/types.rs
index a9f0771dcb715..703f9fd32a387 100644
--- a/crates/ty_python_semantic/src/types.rs
+++ b/crates/ty_python_semantic/src/types.rs
@@ -7247,10 +7247,24 @@ impl Truthiness {
     }

     pub(crate) fn or(self, other: Self) -> Self {
-        match (self, other) {
-            (Truthiness::AlwaysFalse, Truthiness::AlwaysFalse) => Truthiness::AlwaysFalse,
-            (Truthiness::AlwaysTrue, _) | (_, Truthiness::AlwaysTrue) => Truthiness::AlwaysTrue,
-            _ => Truthiness::Ambiguous,
+        match self {
+            Truthiness::AlwaysTrue => self,
+            Truthiness::AlwaysFalse => other,
+            Truthiness::Ambiguous => match other {
+                Truthiness::AlwaysTrue => Truthiness::AlwaysTrue,
+                Truthiness::AlwaysFalse | Truthiness::Ambiguous => Truthiness::Ambiguous,
+            },
+        }
+    }
+
+    pub(crate) fn or_else(self, other: impl Fn() -> Self) -> Self {
+        match self {
+            Truthiness::AlwaysTrue => self,
+            Truthiness::AlwaysFalse => other(),
+            Truthiness::Ambiguous => match other() {
+                Truthiness::AlwaysTrue => Truthiness::AlwaysTrue,
+                Truthiness::AlwaysFalse | Truthiness::Ambiguous => Truthiness::Ambiguous,
+            },
         }
     }

PATCH

echo "Patch applied successfully."
