#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'fn any_reachable' crates/ty_python_semantic/src/semantic_index/use_def.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/semantic_index/use_def.rs b/crates/ty_python_semantic/src/semantic_index/use_def.rs
index af9a7dad7c0e1..d2b2f68426ad0 100644
--- a/crates/ty_python_semantic/src/semantic_index/use_def.rs
+++ b/crates/ty_python_semantic/src/semantic_index/use_def.rs
@@ -863,27 +863,27 @@ pub(crate) struct DeclarationWithConstraint<'db> {
 }

 impl<'db> DeclarationsIterator<'_, 'db> {
-    /// Returns `true` if `predicate` holds for every declaration whose
+    /// Returns `true` if `predicate` holds for at least one declaration whose
     /// reachability constraint is not statically false.
-    pub(crate) fn all_reachable(
-        self,
+    pub(crate) fn any_reachable(
+        mut self,
         db: &'db dyn crate::Db,
         mut predicate: impl FnMut(DefinitionState<'db>) -> bool,
     ) -> bool {
         let predicates = self.predicates;
         let reachability_constraints = self.reachability_constraints;

-        self.filter(
+        self.any(
             |DeclarationWithConstraint {
+                 declaration,
                  reachability_constraint,
-                 ..
              }| {
-                !reachability_constraints
-                    .evaluate(db, predicates, *reachability_constraint)
-                    .is_always_false()
+                predicate(declaration)
+                    && !reachability_constraints
+                        .evaluate(db, predicates, reachability_constraint)
+                        .is_always_false()
             },
         )
-        .all(|DeclarationWithConstraint { declaration, .. }| predicate(declaration))
     }
 }

diff --git a/crates/ty_python_semantic/src/types/class/static_literal.rs b/crates/ty_python_semantic/src/types/class/static_literal.rs
index 4418a7048f84c..ce740c9e763db 100644
--- a/crates/ty_python_semantic/src/types/class/static_literal.rs
+++ b/crates/ty_python_semantic/src/types/class/static_literal.rs
@@ -1751,9 +1751,9 @@ impl<'db> StaticClassLiteral<'db> {
             // want to improve this, we could instead pass a definition-kind filter to the use-def map
             // query, or to the `symbol_from_declarations` call below. Doing so would potentially require
             // us to generate a union of `__init__` methods.
-            if !declarations.clone().all_reachable(db, |declaration| {
-                declaration.is_undefined_or(|declaration| {
-                    matches!(
+            if declarations.clone().any_reachable(db, |declaration| {
+                declaration.is_defined_and(|declaration| {
+                    !matches!(
                         declaration.kind(db),
                         DefinitionKind::AnnotatedAssignment(..)
                     )
diff --git a/crates/ty_python_semantic/src/types/enums.rs b/crates/ty_python_semantic/src/types/enums.rs
index 8f771a1294cf3..f483f09831626 100644
--- a/crates/ty_python_semantic/src/types/enums.rs
+++ b/crates/ty_python_semantic/src/types/enums.rs
@@ -349,9 +349,9 @@ pub(crate) fn enum_metadata<'db>(
             let declarations = use_def_map.end_of_scope_symbol_declarations(symbol_id);

             if !explicit_member_wrapper
-                && !declarations.clone().all_reachable(db, |declaration| {
-                    declaration.is_undefined_or(|declaration| {
-                        matches!(
+                && declarations.clone().any_reachable(db, |declaration| {
+                    declaration.is_defined_and(|declaration| {
+                        !matches!(
                             declaration.kind(db),
                             DefinitionKind::AnnotatedAssignment(assignment)
                                 if assignment

PATCH

echo "Patch applied successfully."
