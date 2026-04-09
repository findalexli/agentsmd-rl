#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'token.string_flags().is_some()' crates/ruff_python_index/src/indexer.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pycodestyle/E502.py b/crates/ruff_linter/resources/test/fixtures/pycodestyle/E502.py
index aa7348768566e..920f50807ef92 100644
--- a/crates/ruff_linter/resources/test/fixtures/pycodestyle/E502.py
+++ b/crates/ruff_linter/resources/test/fixtures/pycodestyle/E502.py
@@ -82,6 +82,14 @@
 x = ("abc" \
     "xyz")

+x = [
+    "a" + \
+f"""
+b
+""" + \
+    "c"
+]
+

 def foo():
     x = (a + \
diff --git a/crates/ruff_python_index/src/indexer.rs b/crates/ruff_python_index/src/indexer.rs
index 80c0e00e209d0..c0cd2ebb3ff0b 100644
--- a/crates/ruff_python_index/src/indexer.rs
+++ b/crates/ruff_python_index/src/indexer.rs
@@ -68,14 +68,14 @@ impl Indexer {
                 TokenKind::Newline | TokenKind::NonLogicalNewline => {
                     line_start = token.end();
                 }
-                TokenKind::String => {
-                    // If the previous token was a string, find the start of the line that contains
-                    // the closing delimiter, since the token itself can span multiple lines.
-                    line_start = source.line_start(token.end());
-                }
                 TokenKind::Comment => {
                     comment_ranges.push(token.range());
                 }
+                _ if token.string_flags().is_some() => {
+                    // String-like tokens, including f/t-string start, middle, and end tokens, can
+                    // span multiple lines.
+                    line_start = source.line_start(token.end());
+                }
                 _ => {}
             }

@@ -346,6 +346,24 @@ x = (
                 TextSize::new(31),
             ]
         );
+
+        let contents = r#"
+x = [
+    "a" + \
+f"""
+b
+""" + \
+    "c"
+]
+"#
+        .trim();
+        assert_eq!(
+            new_indexer(contents).continuation_line_starts(),
+            [
+                TextSize::try_from(contents.find(r#"    "a" + \"#).unwrap()).unwrap(),
+                TextSize::try_from(contents.find("\"\"\" + \\").unwrap()).unwrap(),
+            ]
+        );
     }

     #[test]

PATCH

echo "Patch applied successfully."
