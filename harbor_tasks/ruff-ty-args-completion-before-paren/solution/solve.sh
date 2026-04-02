#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency check: if in_arguments variable already exists in the function, skip
if grep -q 'let mut in_arguments' crates/ty_ide/src/completion.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_ide/src/completion.rs b/crates/ty_ide/src/completion.rs
index 40ef8c47da5efe..1c8761df82ca07 100644
--- a/crates/ty_ide/src/completion.rs
+++ b/crates/ty_ide/src/completion.rs
@@ -1397,10 +1397,14 @@ fn add_argument_completions<'db>(
     cursor: &ContextCursor<'_>,
     completions: &mut Completions<'db>,
 ) {
+    let mut in_arguments = false;
     for node in cursor.covering_node.ancestors() {
         match node {
-            ast::AnyNodeRef::ExprCall(call) => {
-                if call.arguments.range().contains_range(cursor.range) {
+            ast::AnyNodeRef::Arguments(_) => {
+                in_arguments = true;
+            }
+            ast::AnyNodeRef::ExprCall(_) => {
+                if in_arguments {
                     add_function_arg_completions(db, model.file(), cursor, completions);
                 }
                 return;
@@ -5465,6 +5469,21 @@ def test_point(p2: Point):
         builder.build().contains("orthogonal_direction");
     }

+    // https://github.com/astral-sh/ty/issues/3087
+    #[test]
+    fn no_panic_argument_completion_before_paren() {
+        let builder = completion_test_builder(
+            r#"
+list[int]<CURSOR>()
+"#,
+        );
+
+        assert_snapshot!(
+            builder.skip_keywords().skip_builtins().skip_auto_import().build().snapshot(),
+            @"<No completions found after filtering out completions>",
+        );
+    }
+
     #[test]
     fn from_import1() {
         let builder = completion_test_builder(

PATCH

echo "Patch applied successfully."
