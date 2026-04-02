#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
grep -q 'Expr::Generator' crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py b/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py
index cd39b2f9831c0..45acc2345239c 100644
--- a/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py
+++ b/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py
@@ -99,3 +99,11 @@ def g():

 for x in (1,) if True else (2,):
     s.add(x)
+
+# https://github.com/astral-sh/ruff/issues/21098
+for x in ("abc", "def"):
+    s.add(c for c in x)
+
+# don't add extra parens for already parenthesized generators
+for x in ("abc", "def"):
+    s.add((c for c in x))
diff --git a/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs b/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs
index 202f5095578e7..e55aca2d5e248 100644
--- a/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs
+++ b/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs
@@ -111,13 +111,21 @@ pub(crate) fn for_loop_set_mutations(checker: &Checker, for_stmt: &StmtFor) {
                 parenthesize_loop_iter_if_necessary(for_stmt, checker, IterLocation::Call),
             )
         }
-        (for_target, arg) => format!(
-            "{}.{batch_method_name}({} for {} in {})",
-            set.id,
-            locator.slice(arg),
-            locator.slice(for_target),
-            parenthesize_loop_iter_if_necessary(for_stmt, checker, IterLocation::Comprehension),
-        ),
+        (for_target, arg) => {
+            let arg_content = match arg {
+                Expr::Generator(generator) if !generator.parenthesized => {
+                    format!("({})", locator.slice(arg))
+                }
+                _ => locator.slice(arg).to_string(),
+            };
+            format!(
+                "{}.{batch_method_name}({} for {} in {})",
+                set.id,
+                arg_content,
+                locator.slice(for_target),
+                parenthesize_loop_iter_if_necessary(for_stmt, checker, IterLocation::Comprehension),
+            )
+        }
     };

     let applicability = if checker.comment_ranges().intersects(for_stmt.range) {

PATCH
