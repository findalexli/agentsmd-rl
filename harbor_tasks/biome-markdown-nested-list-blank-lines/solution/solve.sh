#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'tracking the indent of the last line visited' crates/biome_markdown_parser/src/syntax/list.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/biome_markdown_parser/src/syntax/list.rs b/crates/biome_markdown_parser/src/syntax/list.rs
index 9bfbfcf485ee..a5117f681dcf 100644
--- a/crates/biome_markdown_parser/src/syntax/list.rs
+++ b/crates/biome_markdown_parser/src/syntax/list.rs
@@ -2569,11 +2569,21 @@ where
     F: Fn(&mut MarkdownParser) -> bool,
 {
     p.lookahead(|p| {
-        // Skip all blank lines
+        // Skip all blank lines, tracking the indent of the last line visited.
+        // The loop consumes whitespace on each line to check if it's blank
+        // (only whitespace + newline). When we hit a non-blank line, the
+        // whitespace was already consumed, so we must track the indent here
+        // rather than counting it separately afterwards.
+        let mut indent;
         loop {
+            indent = 0;
             while p.at(MD_TEXTUAL_LITERAL) {
                 let text = p.cur_text();
-                if text == " " || text == "\t" {
+                if text == " " {
+                    indent += 1;
+                    p.bump(MD_TEXTUAL_LITERAL);
+                } else if text == "\t" {
+                    indent += TAB_STOP_SPACES - (indent % TAB_STOP_SPACES);
                     p.bump(MD_TEXTUAL_LITERAL);
                 } else {
                     break;
@@ -2586,20 +2596,6 @@ where
             break;
         }
 
-        let mut indent = 0;
-        while p.at(MD_TEXTUAL_LITERAL) {
-            let text = p.cur_text();
-            if text == " " {
-                indent += 1;
-                p.bump(MD_TEXTUAL_LITERAL);
-            } else if text == "\t" {
-                indent += TAB_STOP_SPACES - (indent % TAB_STOP_SPACES);
-                p.bump(MD_TEXTUAL_LITERAL);
-            } else {
-                break;
-            }
-        }
-
         // Check indent matches the list's marker indent range
         if expected_indent == 0 {
             if indent > MAX_BLOCK_PREFIX_INDENT {

PATCH

echo "Patch applied successfully."
