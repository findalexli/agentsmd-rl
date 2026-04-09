#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: if is_scope_reachable is gone from semantic_index.rs, patch already applied
if ! grep -q 'is_scope_reachable' crates/ty_python_semantic/src/semantic_index.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix for trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/semantic_index.rs b/crates/ty_python_semantic/src/semantic_index.rs
index 0f3073de04aa0a..f7b4732edd0eba 100644
--- a/crates/ty_python_semantic/src/semantic_index.rs
+++ b/crates/ty_python_semantic/src/semantic_index.rs
@@ -474,20 +474,6 @@ impl<'db> SemanticIndex<'db> {
             .map(|node_ref| self.expect_single_definition(node_ref))
     }

-    pub(crate) fn is_scope_reachable(&self, db: &'db dyn Db, scope_id: FileScopeId) -> bool {
-        self.parent_scope_id(scope_id)
-            .is_none_or(|parent_scope_id| {
-                if !self.is_scope_reachable(db, parent_scope_id) {
-                    return false;
-                }
-
-                let parent_use_def = self.use_def_map(parent_scope_id);
-                let reachability = self.scope(scope_id).reachability();
-
-                parent_use_def.is_reachable(db, reachability)
-            })
-    }
-
     /// Check whether a diagnostic emitted at `range` is in reachable code, considering both
     /// scope reachability and statement-level reachability within the scope.
     pub(crate) fn is_range_reachable(
@@ -496,8 +482,8 @@ impl<'db> SemanticIndex<'db> {
         scope_id: FileScopeId,
         range: TextRange,
     ) -> bool {
-        self.is_scope_reachable(db, scope_id)
-            && self.use_def_map(scope_id).is_range_reachable(db, range)
+        self.ancestor_scopes(scope_id)
+            .all(|(scope_id, _)| self.use_def_map(scope_id).is_range_reachable(db, range))
     }

     pub(crate) fn is_in_type_checking_block(
diff --git a/crates/ty_python_semantic/src/semantic_index/builder.rs b/crates/ty_python_semantic/src/semantic_index/builder.rs
index ca8f3b1e8d4e16..4afd5c07e30f68 100644
--- a/crates/ty_python_semantic/src/semantic_index/builder.rs
+++ b/crates/ty_python_semantic/src/semantic_index/builder.rs
@@ -180,12 +180,7 @@ impl<'db, 'ast> SemanticIndexBuilder<'db, 'ast> {
             semantic_syntax_errors: RefCell::default(),
         };

-        builder.push_scope_with_parent(
-            NodeWithScopeRef::Module,
-            None,
-            ScopedReachabilityConstraintId::ALWAYS_TRUE,
-        );
-
+        builder.push_scope_with_parent(NodeWithScopeRef::Module, None);
         builder
     }
@@ -303,28 +298,16 @@ impl<'db, 'ast> SemanticIndexBuilder<'db, 'ast> {
     }

     fn push_scope(&mut self, node: NodeWithScopeRef) {
-        let parent = self.current_scope();
-        let reachability = self.current_use_def_map().reachability;
-        self.push_scope_with_parent(node, Some(parent), reachability);
+        self.push_scope_with_parent(node, Some(self.current_scope()));
     }

-    fn push_scope_with_parent(
-        &mut self,
-        node: NodeWithScopeRef,
-        parent: Option<FileScopeId>,
-        reachability: ScopedReachabilityConstraintId,
-    ) {
+    fn push_scope_with_parent(&mut self, node: NodeWithScopeRef, parent: Option<FileScopeId>) {
         let children_start = self.scopes.next_index() + 1;

         // Note `node` is guaranteed to be a child of `self.module`
         let node_with_kind = node.to_kind(self.module);

-        let scope = Scope::new(
-            parent,
-            node_with_kind,
-            children_start..children_start,
-            reachability,
-        );
+        let scope = Scope::new(parent, node_with_kind, children_start..children_start);
         let is_class_scope = scope.kind().is_class();
         self.try_node_context_stack_manager.enter_nested_scope();
@@ -1742,14 +1725,6 @@ impl<'db, 'ast> SemanticIndexBuilder<'db, 'ast> {

         assert_eq!(&self.current_assignments, &[]);

-        for scope in &self.scopes {
-            if let Some(parent) = scope.parent() {
-                self.use_def_maps[parent]
-                    .reachability_constraints
-                    .mark_used(scope.reachability());
-            }
-        }
-
         let mut place_tables: IndexVec<_, _> = self
             .place_tables
             .into_iter()
diff --git a/crates/ty_python_semantic/src/semantic_index/scope.rs b/crates/ty_python_semantic/src/semantic_index/scope.rs
index 585d1ec8973eb0..3077075e902f46 100644
--- a/crates/ty_python_semantic/src/semantic_index/scope.rs
+++ b/crates/ty_python_semantic/src/semantic_index/scope.rs
@@ -8,9 +8,7 @@ use crate::{
     Db,
     ast_node_ref::AstNodeRef,
     node_key::NodeKey,
-    semantic_index::{
-        SemanticIndex, reachability_constraints::ScopedReachabilityConstraintId, semantic_index,
-    },
+    semantic_index::{SemanticIndex, semantic_index},
     types::{GenericContext, binding_type, infer_definition_types},
 };
@@ -111,9 +109,6 @@ pub(crate) struct Scope {

     /// The range of [`FileScopeId`]s that are descendants of this scope.
     descendants: Range<FileScopeId>,
-
-    /// The constraint that determines the reachability of this scope.
-    reachability: ScopedReachabilityConstraintId,
 }

 impl Scope {
@@ -121,13 +116,11 @@ impl Scope {
         parent: Option<FileScopeId>,
         node: NodeWithScopeKind,
         descendants: Range<FileScopeId>,
-        reachability: ScopedReachabilityConstraintId,
     ) -> Self {
         Scope {
             parent,
             node,
             descendants,
-            reachability,
         }
     }
@@ -158,10 +151,6 @@ impl Scope {
     pub(crate) fn is_eager(&self) -> bool {
         self.kind().is_eager()
     }
-
-    pub(crate) fn reachability(&self) -> ScopedReachabilityConstraintId {
-        self.reachability
-    }
 }

 #[derive(Debug, PartialEq, Eq, Clone, Copy, Hash, get_size2::GetSize)]
diff --git a/crates/ty_python_semantic/src/types/ide_support.rs b/crates/ty_python_semantic/src/types/ide_support.rs
index 0e31b106fa225d..7d684a248ac7b5 100644
--- a/crates/ty_python_semantic/src/types/ide_support.rs
+++ b/crates/ty_python_semantic/src/types/ide_support.rs
@@ -1728,7 +1728,8 @@ pub fn type_hierarchy_subtypes(db: &dyn Db, ty: Type<'_>) -> Vec<TypeHierarchyCl
             }

             let file_scope_id = scope_id.file_scope_id(db);
-            if !index.is_scope_reachable(db, file_scope_id) {
+            let parsed = parsed_module(db, file).load(db);
+            if !index.is_range_reachable(db, file_scope_id, class_node.node(&parsed).range()) {
                 continue;
             }

PATCH

echo "Patch applied successfully."
