#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
grep -q 'ScopeKind::Lambda' crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
index 50c4e45f57b5f7..e1096d53f2d9a6 100644
--- a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
+++ b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py
@@ -396,7 +396,6 @@ def f(self):


 class LambdaMethod(BaseClass):
-    # TODO(charlie): class-body lambda rewrite is still missed.
     f = lambda self: super(LambdaMethod, self).f()  # can use super()


diff --git a/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs b/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
index 813276376d6c28..c8cfbe8c7afd4b 100644
--- a/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
+++ b/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
@@ -2,7 +2,7 @@ use ruff_diagnostics::Applicability;
 use ruff_macros::{ViolationMetadata, derive_message_formats};
 use ruff_python_ast::visitor::{Visitor, walk_expr, walk_stmt};
 use ruff_python_ast::{self as ast, Expr, Stmt};
-use ruff_python_semantic::{ScopeKind, SemanticModel};
+use ruff_python_semantic::{Scope, ScopeKind, SemanticModel};
 use ruff_text_size::{Ranged, TextSize};

 use crate::checkers::ast::Checker;
@@ -75,12 +75,18 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
     if !is_super_call_with_arguments(call, checker) {
         return;
     }
-    let scope = checker.semantic().current_scope();
-
-    // Check: are we in a Function scope?
-    if !scope.kind.is_function() {
+    // Check: are we in a callable scope (function or lambda)?
+    let callable_scope = match &checker.semantic().current_scope().kind {
+        ScopeKind::Function(_) | ScopeKind::Lambda(_) => Some(checker.semantic().current_scope()),
+        ScopeKind::DunderClassCell => checker
+            .semantic()
+            .first_non_type_parent_scope(checker.semantic().current_scope())
+            .filter(|scope| matches!(scope.kind, ScopeKind::Function(_) | ScopeKind::Lambda(_))),
+        _ => None,
+    };
+    let Some(callable_scope) = callable_scope else {
         return;
-    }
+    };

     let mut parents = checker.semantic().current_statements();
     // For a `super` invocation to be unnecessary, the first argument needs to match
@@ -90,28 +96,53 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
         return;
     };

-    // Find the enclosing function definition (if any).
-    let Some(
-        func_stmt @ Stmt::FunctionDef(ast::StmtFunctionDef {
-            parameters: parent_parameters,
+    // Find the enclosing callable and extract the name of its first parameter.
+    let (parent_arg_name, has_local_dunder_class_var_ref) = match &callable_scope.kind {
+        ScopeKind::Function(_) => {
+            let Some(
+                func_stmt @ Stmt::FunctionDef(ast::StmtFunctionDef {
+                    parameters: parent_parameters,
+                    ..
+                }),
+            ) = parents.find(|stmt| stmt.is_function_def_stmt())
+            else {
+                return;
+            };
+
+            let Some(parent_arg) = parent_parameters.args.first() else {
+                return;
+            };
+
+            (
+                parent_arg.name().as_str(),
+                has_local_dunder_class_var_ref(callable_scope, |finder| {
+                    finder.visit_stmt(func_stmt);
+                }),
+            )
+        }
+        ScopeKind::Lambda(ast::ExprLambda {
+            parameters: Some(parent_parameters),
+            body,
             ..
-        }),
-    ) = parents.find(|stmt| stmt.is_function_def_stmt())
-    else {
-        return;
+        }) => {
+            let Some(parent_arg) = parent_parameters.args.first() else {
+                return;
+            };
+
+            (
+                parent_arg.name().as_str(),
+                has_local_dunder_class_var_ref(callable_scope, |finder| {
+                    finder.visit_expr(body);
+                }),
+            )
+        }
+        _ => return,
     };

-    if is_builtins_super(checker.semantic(), call)
-        && !has_local_dunder_class_var_ref(checker.semantic(), func_stmt)
-    {
+    if is_builtins_super(checker.semantic(), call) && !has_local_dunder_class_var_ref {
         return;
     }

-    // Extract the name of the first argument to the enclosing function.
-    let Some(parent_arg) = parent_parameters.args.first() else {
-        return;
-    };
-
     let mut enclosing_classes = checker.semantic().current_scopes().filter_map(|scope| {
         let ScopeKind::Class(class_def) = &scope.kind else {
             return None;
@@ -136,7 +167,7 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
         return;
     };

-    if second_arg_id != parent_arg.name().as_str() {
+    if second_arg_id != parent_arg_name {
         return;
     }

@@ -145,7 +176,7 @@ pub(crate) fn super_call_with_parameters(checker: &Checker, call: &ast::ExprCall
     // For `super(Outer.Inner, self)`, verify each segment matches the enclosing class nesting.
     match first_arg {
         Expr::Name(ast::ExprName { id, .. }) => {
-            if checker.semantic().current_scope().has(id) {
+            if callable_scope.has(id) {
                 return;
             }

@@ -263,18 +294,22 @@ fn is_super_call_with_arguments(call: &ast::ExprCall, checker: &Checker) -> bool
     checker.semantic().match_builtin_expr(&call.func, "super") && !call.arguments.is_empty()
 }

-/// Returns `true` if the function contains load references to `__class__` or `super` without
-/// local binding.
+/// Returns `true` if the callable body contains load references to `__class__` or `super` without
+/// a local binding.
 ///
-/// This indicates that the function relies on the implicit `__class__` cell variable created by
-/// Python when `super()` is called without arguments, making it unsafe to remove `super()` parameters.
-fn has_local_dunder_class_var_ref(semantic: &SemanticModel, func_stmt: &Stmt) -> bool {
-    if semantic.current_scope().has("__class__") {
+/// This indicates that the callable relies on the implicit `__class__` cell variable created by
+/// Python when `super()` is called without arguments, making it unsafe to remove `super()`
+/// parameters.
+fn has_local_dunder_class_var_ref(
+    callable_scope: &Scope,
+    visit: impl FnOnce(&mut ClassCellReferenceFinder),
+) -> bool {
+    if callable_scope.has("__class__") {
         return false;
     }

     let mut finder = ClassCellReferenceFinder::new();
-    finder.visit_stmt(func_stmt);
+    visit(&mut finder);

     finder.found()
 }

PATCH
