#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'initial_binding_start' crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/flake8_simplify/SIM113.py b/crates/ruff_linter/resources/test/fixtures/flake8_simplify/SIM113.py
index 00771b5f701703..fadb95a9ac6953 100644
--- a/crates/ruff_linter/resources/test/fixtures/flake8_simplify/SIM113.py
+++ b/crates/ruff_linter/resources/test/fixtures/flake8_simplify/SIM113.py
@@ -195,6 +195,31 @@ def inner():
             g(x, idx)
             idx += 1

+
+def func():
+    # SIM113 x2 (same variable name reused in sibling loops)
+    i = 0
+    for val in [1, 2, 3]:
+        print(f"{i}: {val}")
+        i += 1
+
+    i = 0
+    for val in [1, 2, 3]:
+        print(f"{i}: {val}")
+        i += 1
+
+
+def func():
+    # SIM113 (same variable name reused after an `enumerate` loop)
+    for i, val in enumerate([1, 2, 3]):
+        print(f"{i}: {val}")
+
+    i = 0
+    for val in [1, 2, 3]:
+        print(f"{i}: {val}")
+        i += 1
+
+
 async def func():
     # OK (for loop is async)
     idx = 0
diff --git a/crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs b/crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs
index a35513de856f64..400b5d87bbd700 100644
--- a/crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs
+++ b/crates/ruff_linter/src/rules/flake8_simplify/rules/enumerate_for_loop.rs
@@ -79,18 +79,19 @@ pub(crate) fn enumerate_for_loop(checker: &Checker, for_stmt: &ast::StmtFor) {
             };

             // If it's not an assignment (e.g., it's a function argument), ignore it.
-            let binding = checker.semantic().binding(id);
-            if !binding.kind.is_assignment() {
+            let initial_binding = checker.semantic().binding(id);
+            if !initial_binding.kind.is_assignment() {
                 continue;
             }

             // If the variable is global or nonlocal, ignore it.
-            if binding.is_global() || binding.is_nonlocal() {
+            if initial_binding.is_global() || initial_binding.is_nonlocal() {
                 continue;
             }

             // Ensure that the index variable was initialized to 0 (or instance of `int` if preview is enabled).
-            let Some(value) = typing::find_binding_value(binding, checker.semantic()) else {
+            let Some(value) = typing::find_binding_value(initial_binding, checker.semantic())
+            else {
                 continue;
             };
             if !(matches!(
@@ -112,7 +113,7 @@ pub(crate) fn enumerate_for_loop(checker: &Checker, for_stmt: &ast::StmtFor) {
             let Some(for_loop_id) = checker.semantic().current_statement_id() else {
                 continue;
             };
-            let Some(assignment_id) = binding.source else {
+            let Some(assignment_id) = initial_binding.source else {
                 continue;
             };
             if checker.semantic().parent_statement_id(for_loop_id)
@@ -124,7 +125,7 @@ pub(crate) fn enumerate_for_loop(checker: &Checker, for_stmt: &ast::StmtFor) {
             // Identify the binding created by the augmented assignment.
             // TODO(charlie): There should be a way to go from `ExprName` to `BindingId` (like
             // `resolve_name`, but for bindings rather than references).
-            let binding = {
+            let increment_binding = {
                 let mut bindings = checker
                     .semantic()
                     .current_scope()
@@ -144,10 +145,13 @@ pub(crate) fn enumerate_for_loop(checker: &Checker, for_stmt: &ast::StmtFor) {
                 binding
             };

-            // If the variable is used outside the loop, ignore it.
-            if binding.references.iter().any(|id| {
-                let reference = checker.semantic().reference(*id);
-                !for_stmt.range().contains_range(reference.range())
+            // Reassignments in the same scope inherit older references. Ignore anything that
+            // predates the counter's initialization and only consider uses in its current lifetime.
+            let initial_binding_start = initial_binding.range.start();
+            if increment_binding.references().any(|id| {
+                let reference = checker.semantic().reference(id);
+                reference.start() >= initial_binding_start
+                    && !for_stmt.range().contains_range(reference.range())
             }) {
                 continue;
             }
diff --git a/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__SIM113_SIM113.py.snap b/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__SIM113_SIM113.py.snap
index 3015682026c5a4..1e4771fe56b927 100644
--- a/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__SIM113_SIM113.py.snap
+++ b/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__SIM113_SIM113.py.snap
@@ -48,3 +48,32 @@ SIM113 Use `enumerate()` for index variable `idx` in `for` loop
    |         ^^^^^^^^
 45 |         h(x)
    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:204:9
+    |
+202 |     for val in [1, 2, 3]:
+203 |         print(f"{i}: {val}")
+204 |         i += 1
+    |         ^^^^^^
+205 |
+206 |     i = 0
+    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:209:9
+    |
+207 |     for val in [1, 2, 3]:
+208 |         print(f"{i}: {val}")
+209 |         i += 1
+    |         ^^^^^^
+    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:220:9
+    |
+218 |     for val in [1, 2, 3]:
+219 |         print(f"{i}: {val}")
+220 |         i += 1
+    |         ^^^^^^
+    |
diff --git a/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__preview__SIM113_SIM113.py.snap b/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__preview__SIM113_SIM113.py.snap
index 065ed20bb9a3d9..5af873a570caad 100644
--- a/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__preview__SIM113_SIM113.py.snap
+++ b/crates/ruff_linter/src/rules/flake8_simplify/snapshots/ruff_linter__rules__flake8_simplify__tests__preview__SIM113_SIM113.py.snap
@@ -58,3 +58,32 @@ SIM113 Use `enumerate()` for index variable `idx` in `for` loop
    |         ^^^^^^^^
 55 |         h(x)
    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:204:9
+    |
+202 |     for val in [1, 2, 3]:
+203 |         print(f"{i}: {val}")
+204 |         i += 1
+    |         ^^^^^^
+205 |
+206 |     i = 0
+    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:209:9
+    |
+207 |     for val in [1, 2, 3]:
+208 |         print(f"{i}: {val}")
+209 |         i += 1
+    |         ^^^^^^
+    |
+
+SIM113 Use `enumerate()` for index variable `i` in `for` loop
+   --> SIM113.py:220:9
+    |
+218 |     for val in [1, 2, 3]:
+219 |         print(f"{i}: {val}")
+220 |         i += 1
+    |         ^^^^^^
+    |

PATCH
