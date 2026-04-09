#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'After whitespace following destination content, only a title' crates/biome_markdown_parser/src/syntax/link_block.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/biome_markdown_parser/src/syntax/link_block.rs b/crates/biome_markdown_parser/src/syntax/link_block.rs
index 00bd7b36b398..b8ffe716fa53 100644
--- a/crates/biome_markdown_parser/src/syntax/link_block.rs
+++ b/crates/biome_markdown_parser/src/syntax/link_block.rs
@@ -305,8 +305,10 @@ fn skip_destination_tokens(p: &mut MarkdownParser) -> DestinationResult {
                 continue;
             }

-            if at_title_start(p) && has_content && saw_separator {
-                // Break here - we've found separator before title
+            if has_content && saw_separator {
+                // After whitespace following destination content, only a title
+                // starter is valid. Any other text means the destination ended
+                // at the whitespace boundary.
                 break;
             }

diff --git a/crates/biome_markdown_parser/tests/md_test_suite/ok/link_definition_edge_cases.md.snap b/crates/biome_markdown_parser/tests/md_test_suite/ok/link_definition_edge_cases.md.snap
index 2eb68ddaaf2b..3bedbd664b72 100644
--- a/crates/biome_markdown_parser/tests/md_test_suite/ok/link_definition_edge_cases.md.snap
+++ b/crates/biome_markdown_parser/tests/md_test_suite/ok/link_definition_edge_cases.md.snap
@@ -581,43 +581,28 @@ MdDocument {
         MdNewline {
             value_token: NEWLINE@439..440 "\n" [] [],
         },
-        MdLinkReferenceDefinition {
-            indent: MdIndentTokenList [],
-            l_brack_token: L_BRACK@440..441 "[" [] [],
-            label: MdLinkLabel {
-                content: MdInlineItemList [
-                    MdTextual {
-                        value_token: MD_TEXTUAL_LITERAL@441..448 "invalid" [] [],
-                    },
-                    MdTextual {
-                        value_token: MD_TEXTUAL_LITERAL@448..449 "-" [] [],
-                    },
-                    MdTextual {
-                        value_token: MD_TEXTUAL_LITERAL@449..457 "trailing" [] [],
-                    },
-                ],
-            },
-            r_brack_token: R_BRACK@457..458 "]" [] [],
-            colon_token: COLON@458..459 ":" [] [],
-            destination: MdLinkDestination {
-                content: MdInlineItemList [
-                    MdTextual {
-                        value_token: MD_TEXTUAL_LITERAL@459..460 " " [] [],
-                    },
-                    MdTextual {
-                        value_token: MD_TEXTUAL_LITERAL@460..464 "/url" [] [],
-                    },
-                ],
-            },
-            title: missing (optional),
-        },
         MdParagraph {
             list: MdInlineItemList [
                 MdTextual {
-                    value_token: MD_TEXTUAL_LITERAL@464..465 " " [] [],
+                    value_token: MD_TEXTUAL_LITERAL@440..441 "[" [] [],
+                },
+                MdTextual {
+                    value_token: MD_TEXTUAL_LITERAL@441..448 "invalid" [] [],
+                },
+                MdTextual {
+                    value_token: MD_TEXTUAL_LITERAL@448..449 "-" [] [],
+                },
+                MdTextual {
+                    value_token: MD_TEXTUAL_LITERAL@449..457 "trailing" [] [],
+                },
+                MdTextual {
+                    value_token: MD_TEXTUAL_LITERAL@457..458 "]" [] [],
+                },
+                MdTextual {
+                    value_token: MD_TEXTUAL_LITERAL@458..459 ":" [] [],
                 },
                 MdTextual {
-                    value_token: MD_TEXTUAL_LITERAL@465..472 "invalid" [] [],
+                    value_token: MD_TEXTUAL_LITERAL@459..472 " /url invalid" [] [],
                 },
                 MdTextual {
                     value_token: MD_TEXTUAL_LITERAL@472..473 "\n" [] [],
@@ -1033,38 +1018,28 @@ MdDocument {
       1: (empty)
     36: MD_NEWLINE@439..440
       0: NEWLINE@439..440 "\n" [] []
-    37: MD_LINK_REFERENCE_DEFINITION@440..464
-      0: MD_INDENT_TOKEN_LIST@440..440
-      1: L_BRACK@440..441 "[" [] []
-      2: MD_LINK_LABEL@441..457
-        0: MD_INLINE_ITEM_LIST@441..457
-          0: MD_TEXTUAL@441..448
-            0: MD_TEXTUAL_LITERAL@441..448 "invalid" [] []
-          1: MD_TEXTUAL@448..449
-            0: MD_TEXTUAL_LITERAL@448..449 "-" [] []
-          2: MD_TEXTUAL@449..457
-            0: MD_TEXTUAL_LITERAL@449..457 "trailing" [] []
-      3: R_BRACK@457..458 "]" [] []
-      4: COLON@458..459 ":" [] []
-      5: MD_LINK_DESTINATION@459..464
-        0: MD_INLINE_ITEM_LIST@459..464
-          0: MD_TEXTUAL@459..460
-            0: MD_TEXTUAL_LITERAL@459..460 " " [] []
-          1: MD_TEXTUAL@460..464
-            0: MD_TEXTUAL_LITERAL@460..464 "/url" [] []
-      6: (empty)
-    38: MD_PARAGRAPH@464..473
-      0: MD_INLINE_ITEM_LIST@464..473
-        0: MD_TEXTUAL@464..465
-          0: MD_TEXTUAL_LITERAL@464..465 " " [] []
-        1: MD_TEXTUAL@465..472
-          0: MD_TEXTUAL_LITERAL@465..472 "invalid" [] []
-        2: MD_TEXTUAL@472..473
+    37: MD_PARAGRAPH@440..473
+      0: MD_INLINE_ITEM_LIST@440..473
+        0: MD_TEXTUAL@440..441
+          0: MD_TEXTUAL_LITERAL@440..441 "[" [] []
+        1: MD_TEXTUAL@441..448
+          0: MD_TEXTUAL_LITERAL@441..448 "invalid" [] []
+        2: MD_TEXTUAL@448..449
+          0: MD_TEXTUAL_LITERAL@448..449 "-" [] []
+        3: MD_TEXTUAL@449..457
+          0: MD_TEXTUAL_LITERAL@449..457 "trailing" [] []
+        4: MD_TEXTUAL@457..458
+          0: MD_TEXTUAL_LITERAL@457..458 "]" [] []
+        5: MD_TEXTUAL@458..459
+          0: MD_TEXTUAL_LITERAL@458..459 ":" [] []
+        6: MD_TEXTUAL@459..472
+          0: MD_TEXTUAL_LITERAL@459..472 " /url invalid" [] []
+        7: MD_TEXTUAL@472..473
           0: MD_TEXTUAL_LITERAL@472..473 "\n" [] []
       1: (empty)
-    39: MD_NEWLINE@473..474
+    38: MD_NEWLINE@473..474
       0: NEWLINE@473..474 "\n" [] []
-    40: MD_PARAGRAPH@474..507
+    39: MD_PARAGRAPH@474..507
       0: MD_INLINE_ITEM_LIST@474..507
         0: MD_TEXTUAL@474..475
           0: MD_TEXTUAL_LITERAL@474..475 "[" [] []

PATCH

echo "Patch applied successfully."
