#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'is_annotated_assignment_redefinition_enabled' crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyflakes/F811_34.py b/crates/ruff_linter/resources/test/fixtures/pyflakes/F811_34.py
new file mode 100644
index 0000000000000..0578d14e5a409
--- /dev/null
+++ b/crates/ruff_linter/resources/test/fixtures/pyflakes/F811_34.py
@@ -0,0 +1,25 @@
+"""Regression test for: https://github.com/astral-sh/ruff/issues/23802"""
+
+# F811: both annotated assignments, first unused
+bar: int = 1
+bar: int = 2  # F811
+
+x: str = "hello"
+x: str = "world"  # F811
+
+# OK: plain reassignment (no annotation)
+y = 1
+y = 2
+
+# OK: first is plain, second is annotated
+z = 1
+z: int = 2
+
+# OK: first is annotated, second is plain
+w: int = 1
+w = 2
+
+# OK: used between assignments
+a: int = 1
+print(a)
+a: int = 2
diff --git a/crates/ruff_linter/src/preview.rs b/crates/ruff_linter/src/preview.rs
index fbb7cf0f6a3b6..7f539ab5431be 100644
--- a/crates/ruff_linter/src/preview.rs
+++ b/crates/ruff_linter/src/preview.rs
@@ -9,6 +9,13 @@ use crate::settings::{LinterSettings, types::PreviewMode};

 // Rule-specific behavior

+// https://github.com/astral-sh/ruff/issues/23802
+pub(crate) const fn is_annotated_assignment_redefinition_enabled(
+    settings: &LinterSettings,
+) -> bool {
+    settings.preview.is_enabled()
+}
+
 // https://github.com/astral-sh/ruff/pull/21382
 pub(crate) const fn is_custom_exception_checking_enabled(settings: &LinterSettings) -> bool {
     settings.preview.is_enabled()
diff --git a/crates/ruff_linter/src/rules/pyflakes/mod.rs b/crates/ruff_linter/src/rules/pyflakes/mod.rs
index ee48dd6580caf..273e2ffaae6d2 100644
--- a/crates/ruff_linter/src/rules/pyflakes/mod.rs
+++ b/crates/ruff_linter/src/rules/pyflakes/mod.rs
@@ -749,6 +749,19 @@ mod tests {
         Ok(())
     }

+    #[test]
+    fn f811_annotated_assignment_redefinition() -> Result<()> {
+        let diagnostics = test_path(
+            Path::new("pyflakes/F811_34.py"),
+            &LinterSettings {
+                preview: PreviewMode::Enabled,
+                ..LinterSettings::for_rule(Rule::RedefinedWhileUnused)
+            },
+        )?;
+        assert_diagnostics!(diagnostics);
+        Ok(())
+    }
+
     #[test]
     fn extend_generics() -> Result<()> {
         let snapshot = "extend_immutable_calls".to_string();
diff --git a/crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs b/crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs
index c93d0fc8c6029..593132b6f738c 100644
--- a/crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs
+++ b/crates/ruff_linter/src/rules/pyflakes/rules/redefined_while_unused.rs
@@ -1,11 +1,13 @@
 use ruff_macros::{ViolationMetadata, derive_message_formats};
+use ruff_python_ast::Stmt;
 use ruff_python_semantic::analyze::visibility;
-use ruff_python_semantic::{BindingKind, Imported, Scope, ScopeId};
+use ruff_python_semantic::{Binding, BindingKind, Imported, Scope, ScopeId, SemanticModel};
 use ruff_source_file::SourceRow;
 use ruff_text_size::Ranged;

 use crate::checkers::ast::Checker;
 use crate::fix::edits;
+use crate::preview::is_annotated_assignment_redefinition_enabled;
 use crate::{Fix, FixAvailability, Violation};

 use rustc_hash::FxHashMap;
@@ -31,6 +33,14 @@ use rustc_hash::FxHashMap;
 /// import bar
 /// ```
 ///
+/// ## Preview
+/// When [preview] is enabled, this rule also flags annotated variable
+/// redeclarations. For example, `bar: int = 1` followed by `bar: int = 2`
+/// will be flagged as a redefinition of an unused variable, whereas plain
+/// reassignments like `bar = 1` followed by `bar = 2` remain unflagged.
+///
+/// [preview]: https://docs.astral.sh/ruff/preview/
+///
 /// ## Options
 ///
 /// This rule ignores dummy variables, as determined by:
@@ -79,9 +89,15 @@ pub(crate) fn redefined_while_unused(checker: &Checker, scope_id: ScopeId, scope
             }

             // If the shadowing binding isn't considered a "redefinition" of the
-            // shadowed binding, abort.
+            // shadowed binding, abort — unless both are annotated assignments
+            // and preview mode is enabled (see #23802).
             if !binding.redefines(shadowed) {
-                continue;
+                if !(is_annotated_assignment_redefinition_enabled(checker.settings())
+                    && is_annotated_assignment(binding, checker.semantic())
+                    && is_annotated_assignment(shadowed, checker.semantic()))
+                {
+                    continue;
+                }
             }

             if shadow.same_scope() {
@@ -224,3 +240,9 @@ pub(crate) fn redefined_while_unused(checker: &Checker, scope_id: ScopeId, scope
         }
     }
 }
+
+fn is_annotated_assignment(binding: &Binding, semantic: &SemanticModel) -> bool {
+    binding
+        .statement(semantic)
+        .is_some_and(Stmt::is_ann_assign_stmt)
+}
diff --git a/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__f811_annotated_assignment_redefinition.snap b/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__f811_annotated_assignment_redefinition.snap
new file mode 100644
index 0000000000000..4f60b19931cf2
--- /dev/null
+++ b/crates/ruff_linter/src/rules/pyflakes/snapshots/ruff_linter__rules__pyflakes__tests__f811_annotated_assignment_redefinition.snap
@@ -0,0 +1,29 @@
+---
+source: crates/ruff_linter/src/rules/pyflakes/mod.rs
+---
+F811 Redefinition of unused `bar` from line 4
+ --> F811_34.py:4:1
+  |
+3 | # F811: both annotated assignments, first unused
+4 | bar: int = 1
+  | --- previous definition of `bar` here
+5 | bar: int = 2  # F811
+  | ^^^ `bar` redefined here
+6 |
+7 | x: str = "hello"
+  |
+help: Remove definition: `bar`
+
+F811 Redefinition of unused `x` from line 7
+  --> F811_34.py:7:1
+   |
+ 5 | bar: int = 2  # F811
+ 6 |
+ 7 | x: str = "hello"
+   | - previous definition of `x` here
+ 8 | x: str = "world"  # F811
+   | ^ `x` redefined here
+ 9 |
+10 | # OK: plain reassignment (no annotation)
+   |
+help: Remove definition: `x`

PATCH
