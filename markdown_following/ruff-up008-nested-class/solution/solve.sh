#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
grep -q 'enclosing_classes.next().is_some()' crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
index 877e952cd2fa16..50c4e45f57b5f7 100644
--- a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
+++ b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
@@ -347,7 +347,6 @@ def __init__(self, foo):
 class CommonNesting:
     class C(Base):
         def __init__(self, foo):
-            # TODO(charlie): false positive until nested class matching is fixed.
             super(C, self).__init__(foo)  # Should NOT trigger UP008


@@ -355,7 +354,6 @@ class HigherLevelsOfNesting:
     class Inner:
         class C(Base):
             def __init__(self, foo):
-                # TODO(charlie): false positive until nested class matching is fixed.
                 super(Inner.C, self).__init__(foo)  # Should NOT trigger UP008


diff --git a/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs b/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
index 54315ea2cdebf7..813276376d6c28 100644
--- a/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
+++ b/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
@@ -2,7 +2,7 @@ use ruff_diagnostics::Applicability;
 use ruff_macros::{ViolationMetadata, derive_message_formats};
 use ruff_python_ast::visitor::{Visitor, walk_expr, walk_stmt};
 use ruff_python_ast::{self as ast, Expr, Stmt};
-use ruff_python_semantic::SemanticModel;
+use ruff_python_semantic::{ScopeKind, SemanticModel};
 use ruff_text_size::{Ranged, TextSize};

 use crate::checkers::ast::Checker;
@@ -112,12 +112,19 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
         return;
     };

+    let mut enclosing_classes = checker.semantic().current_scopes().filter_map(|scope| {
+        let ScopeKind::Class(class_def) = &scope.kind else {
+            return None;
+        };
+        Some(*class_def)
+    });
+
     // Find the enclosing class definition (if any).
-    let Some(Stmt::ClassDef(ast::StmtClassDef {
+    let Some(ast::StmtClassDef {
         name: parent_name,
         decorator_list,
         ..
-    })) = parents.find(|stmt| stmt.is_class_def_stmt())
+    }) = enclosing_classes.next()
     else {
         return;
     };
@@ -138,9 +145,15 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
     // For `super(Outer.Inner, self)`, verify each segment matches the enclosing class nesting.
     match first_arg {
         Expr::Name(ast::ExprName { id, .. }) => {
-            if !((id == "__class__" || id == parent_name.as_str())
-                && !checker.semantic().current_scope().has(id))
-            {
+            if checker.semantic().current_scope().has(id) {
+                return;
+            }
+
+            if id != "__class__" && id == parent_name.as_str() {
+                if enclosing_classes.next().is_some() {
+                    return;
+                }
+            } else if id != "__class__" {
                 return;
             }
         }
@@ -152,10 +165,10 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
             }
             // Each preceding name must match the next enclosing class.
             for name in chain.iter().rev().skip(1) {
-                let Some(Stmt::ClassDef(ast::StmtClassDef {
+                let Some(ast::StmtClassDef {
                     name: enclosing_name,
                     ..
-                })) = parents.find(|stmt| stmt.is_class_def_stmt())
+                }) = enclosing_classes.next()
                 else {
                     return;
                 };
@@ -163,6 +176,9 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
                     return;
                 }
             }
+            if enclosing_classes.next().is_some() {
+                return;
+            }
         }
         _ => return,
     }

PATCH

# Copy the updated snapshot file
cp /solution/UP008.py.snap /workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/snapshots/ruff_linter__rules__pyupgrade__tests__UP008.py.snap
