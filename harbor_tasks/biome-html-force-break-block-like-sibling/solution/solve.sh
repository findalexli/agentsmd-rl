#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotency: skip if already applied (distinctive line from the patch).
if grep -q "Block-like elements followed by text should break before the text" \
        crates/biome_html_formatter/src/html/lists/element_list.rs; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/biome_html_formatter/src/html/lists/element_list.rs b/crates/biome_html_formatter/src/html/lists/element_list.rs
index 76dd1128eb48..d57bf75a286f 100644
--- a/crates/biome_html_formatter/src/html/lists/element_list.rs
+++ b/crates/biome_html_formatter/src/html/lists/element_list.rs
@@ -186,6 +186,7 @@ use crate::{
     prelude::*,
     utils::{
         children::{HtmlChild, HtmlChildrenIterator, html_split_children},
+        css_display::CssDisplay,
         metadata::get_element_css_display,
     },
 };
@@ -507,8 +508,23 @@ impl FormatHtmlElementList {
                                     // Prettier's behavior where the line break happens BEFORE the
                                     // element rather than after the text.
                                     if !css_display.is_inline_like() {
-                                        // add a line break after the word for non-inline elements
-                                        if force_multiline {
+                                        if css_display.is_block_like()
+                                            && css_display != CssDisplay::None
+                                        {
+                                            // A visible block-like element adjacent to text.
+                                            //
+                                            // Prettier always breaks in cases like:
+                                            // `<div>a<div>b</div> c</div>`.
+                                            child_breaks = true;
+                                            force_multiline = true;
+                                            write!(f, [hard_line_break()])?;
+                                        } else if css_display == CssDisplay::None {
+                                            // Avoid introducing whitespace around `display: none` elements if they are adjacent to whitespace sensitive children.
+                                            //
+                                            // ```html
+                                            // <div>123<meta attr />456</div>
+                                            // ```
+                                        } else if force_multiline {
                                             write!(f, [hard_line_break()])?;
                                         } else {
                                             write!(f, [soft_line_break()])?;
@@ -565,6 +581,14 @@ impl FormatHtmlElementList {
                             if last_nontext_had_trailing_line {
                                 // The outer group pattern already added the trailing space
                                 // Don't add another one
+                            } else if force_multiline
+                                && matches!(children_iter.peek(), Some(HtmlChild::Word(_)))
+                                && last_css_display.is_block_like()
+                                && last_css_display != CssDisplay::None
+                            {
+                                // If we're already multiline, keep words after block-like elements on their own line.
+                                child_breaks = true;
+                                write!(f, [hard_line_break()])?;
                             } else if last_css_display.is_externally_whitespace_sensitive(f) {
                                 // For whitespace-sensitive elements, use soft_line_break_or_space
                                 // so the space is preserved in flat mode
@@ -660,6 +684,13 @@ impl FormatHtmlElementList {
                                     // <a>link</a>more text
                                     // ```
                                     None
+                                } else if css_display.is_block_like()
+                                    && css_display != CssDisplay::None
+                                {
+                                    // Block-like elements followed by text should break before the text.
+                                    // This matches Prettier for cases like:
+                                    // `<div>a<div>b</div> c</div>` and `<details><summary>...</summary>details</details>`.
+                                    Some(LineMode::Hard)
                                 } else {
                                     Some(LineMode::Soft)
                                 }
diff --git a/crates/biome_html_formatter/src/utils/css_display.rs b/crates/biome_html_formatter/src/utils/css_display.rs
index 6da5e882bc9c..325a5ce6c594 100644
--- a/crates/biome_html_formatter/src/utils/css_display.rs
+++ b/crates/biome_html_formatter/src/utils/css_display.rs
@@ -62,6 +62,8 @@ impl CssDisplay {
     /// **Note: For formatting purposes, you MUST use [`Self::is_internally_whitespace_sensitive`] or
     /// [`Self::is_externally_whitespace_sensitive`] to determine if an element is whitespace-sensitive.**
     pub fn is_block_like(self) -> bool {
+        // FIXME: Prettier treats `display: none` as whitespace sensitive. So technically, this should not be included here.
+        // However, including it here simplifies some logic elsewhere.
         matches!(
             self,
             Self::Block
PATCH

echo "Gold patch applied."
