#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'end.saturating_sub(start)' crates/biome_markdown_parser/src/syntax/inline/emphasis.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/biome_markdown_parser/src/syntax/inline/emphasis.rs b/crates/biome_markdown_parser/src/syntax/inline/emphasis.rs
index 81ffef162965..bdd148e1be63 100644
--- a/crates/biome_markdown_parser/src/syntax/inline/emphasis.rs
+++ b/crates/biome_markdown_parser/src/syntax/inline/emphasis.rs
@@ -684,18 +684,16 @@ pub(crate) fn set_inline_emphasis_context_until(
 }

 fn inline_list_source_len_until(p: &mut MarkdownParser, stop: MarkdownSyntaxKind) -> usize {
+    let start: usize = p.cur_range().start().into();
     p.lookahead(|p| {
-        let mut len = 0usize;
-
         loop {
             if p.at(T![EOF]) || p.at(stop) || p.at_inline_end() {
                 break;
             }
-
-            len += p.cur_text().len();
             p.bump(p.cur());
         }

-        len
+        let end: usize = p.cur_range().start().into();
+        end.saturating_sub(start)
     })
 }

PATCH

echo "Patch applied successfully."
