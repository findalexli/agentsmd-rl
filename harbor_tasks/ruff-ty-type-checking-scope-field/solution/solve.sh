#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'ancestor_scopes(scope_id).any' crates/ty_python_semantic/src/semantic_index.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/semantic_index.rs b/crates/ty_python_semantic/src/semantic_index.rs
index a902cb6c69179f..0f3073de04aa0a 100644
--- a/crates/ty_python_semantic/src/semantic_index.rs
+++ b/crates/ty_python_semantic/src/semantic_index.rs
@@ -492,7 +492,7 @@ impl<'db> SemanticIndex<'db> {
     /// scope reachability and statement-level reachability within the scope.
     pub(crate) fn is_range_reachable(
         &self,
-        db: &'db dyn crate::Db,
+        db: &'db dyn Db,
         scope_id: FileScopeId,
         range: TextRange,
     ) -> bool {
@@ -505,14 +505,13 @@ impl<'db> SemanticIndex<'db> {
         scope_id: FileScopeId,
         range: TextRange,
     ) -> bool {
-        self.scope(scope_id).in_type_checking_block()
-            || self
-                .use_def_map(scope_id)
+        self.ancestor_scopes(scope_id).any(|(scope_id, _)| {
+            self.use_def_map(scope_id)
                 .is_range_in_type_checking_block(range)
+        })
     }

     /// Returns an iterator over the descendent scopes of `scope`.
-    #[allow(unused)]
     pub(crate) fn descendent_scopes(&self, scope: FileScopeId) -> DescendantsIter<'_> {
         DescendantsIter::new(&self.scopes, scope)
     }
diff --git a/crates/ty_python_semantic/src/semantic_index/builder.rs b/crates/ty_python_semantic/src/semantic_index/builder.rs
index ec11cf3ab045e6..ca8f3b1e8d4e16 100644
--- a/crates/ty_python_semantic/src/semantic_index/builder.rs
+++ b/crates/ty_python_semantic/src/semantic_index/builder.rs
@@ -324,7 +324,6 @@ impl<'db, 'ast> SemanticIndexBuilder<'db, 'ast> {
             node_with_kind,
             children_start..children_start,
             reachability,
-            self.in_type_checking_block,
         );
         let is_class_scope = scope.kind().is_class();
         self.try_node_context_stack_manager.enter_nested_scope();
diff --git a/crates/ty_python_semantic/src/semantic_index/scope.rs b/crates/ty_python_semantic/src/semantic_index/scope.rs
index d5ffb43f0a0e8f..585d1ec8973eb0 100644
--- a/crates/ty_python_semantic/src/semantic_index/scope.rs
+++ b/crates/ty_python_semantic/src/semantic_index/scope.rs
@@ -114,9 +114,6 @@ pub(crate) struct Scope {

     /// The constraint that determines the reachability of this scope.
     reachability: ScopedReachabilityConstraintId,
-
-    /// Whether this scope is defined inside an `if TYPE_CHECKING:` block.
-    in_type_checking_block: bool,
 }

 impl Scope {
@@ -125,14 +122,12 @@ impl Scope {
         node: NodeWithScopeKind,
         descendants: Range<FileScopeId>,
         reachability: ScopedReachabilityConstraintId,
-        in_type_checking_block: bool,
     ) -> Self {
         Scope {
             parent,
             node,
             descendants,
             reachability,
-            in_type_checking_block,
         }
     }

@@ -167,10 +162,6 @@ impl Scope {
     pub(crate) fn reachability(&self) -> ScopedReachabilityConstraintId {
         self.reachability
     }
-
-    pub(crate) fn in_type_checking_block(&self) -> bool {
-        self.in_type_checking_block
-    }
 }

 #[derive(Debug, PartialEq, Eq, Clone, Copy, Hash, get_size2::GetSize)]
diff --git a/crates/ty_python_semantic/src/types/infer/builder/function.rs b/crates/ty_python_semantic/src/types/infer/builder/function.rs
index 0b22120b297933..f4f445ba81f1c8 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/function.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/function.rs
@@ -65,7 +65,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                 if self.in_function_overload_or_abstractmethod() {
                     return;
                 }
-                if self.scope().scope(db).in_type_checking_block() {
+                if self.is_in_type_checking_block(self.scope(), function) {
                     return;
                 }
                 if let Some(class) = self.class_context_of_current_method() {
@@ -639,7 +639,7 @@ impl<'db, 'ast> TypeInferenceBuilder<'db, 'ast> {
                     && !suppress_invalid_default
                     && !((self.in_stub()
                         || self.in_function_overload_or_abstractmethod()
-                        || self.scope().scope(db).in_type_checking_block()
+                        || self.is_in_type_checking_block(self.scope(), default_expr)
                         || self
                             .class_context_of_current_method()
                             .is_some_and(|class| class.is_protocol(db)))
diff --git a/crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs b/crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs
index 11c043c5a24b5d..fe3593a5954e3c 100644
--- a/crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs
+++ b/crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs
@@ -1,4 +1,5 @@
 use ruff_db::diagnostic::Annotation;
+use ruff_text_size::Ranged;
 use rustc_hash::FxHashSet;

 use crate::{
@@ -100,10 +101,12 @@ pub(crate) fn check_overloaded_function<'db>(
     if implementation.is_none() && !context.in_stub() {
         let mut implementation_required = true;

-        if function
-            .iter_overloads_and_implementation(db)
-            .all(|f| f.body_scope(db).scope(db).in_type_checking_block())
-        {
+        if function.iter_overloads_and_implementation(db).all(|f| {
+            index.is_in_type_checking_block(
+                f.body_scope(db).file_scope_id(db),
+                f.node(db, context.file(), context.module()).range(),
+            )
+        }) {
             implementation_required = false;
         } else if let NodeWithScopeKind::Class(class_node_ref) = scope {
             let class = binding_type(

PATCH

echo "Patch applied successfully."
