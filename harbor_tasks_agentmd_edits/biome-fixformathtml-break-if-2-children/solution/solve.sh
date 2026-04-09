#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q "css_display::CssDisplay" crates/biome_html_formatter/src/html/lists/element_list.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
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
diff --git a/.claude/skills/prettier-compare/SKILL.md b/.claude/skills/prettier-compare/SKILL.md
new file mode 100644
index 000000000000..9fc0ba044b12
--- /dev/null
+++ b/.claude/skills/prettier-compare/SKILL.md
@@ -0,0 +1,48 @@
+---
+name: prettier-compare
+description: Compares code formatting and formatting IR between Biome and Prettier to ensure that Biome's formatting is consistent and correct.
+---
+
+## Purpose
+
+Use `packages/prettier-compare/` to inspect any differences between Biome and Prettier formatting (including IR output) before shipping formatter changes.
+
+## Prerequisites
+
+1. Run every command from the repository root so relative paths resolve correctly.
+2. Use `bun` (the CLI is a Bun script) and ensure dependencies have been installed.
+3. Always pass `--rebuild` so the Biome WASM bundle matches your current Rust changes.
+
+## Common workflows
+
+Snippets passed as CLI args:
+
+```
+bun packages/prettier-compare/bin/prettier-compare.js --rebuild 'const x={a:1,b:2}'
+```
+
+Force a language (useful when the tool cannot infer it from a filename):
+
+```
+bun packages/prettier-compare/bin/prettier-compare.js --rebuild -l ts 'const x: number = 1'
+```
+
+Compare files on disk:
+
+```
+bun packages/prettier-compare/bin/prettier-compare.js --rebuild -f src/example.tsx
+```
+
+Read from stdin (great for piping editor selections):
+
+```
+echo 'const x = 1' | bun packages/prettier-compare/bin/prettier-compare.js --rebuild -l js
+```
+
+## Tips
+
+- Use `-l/--language` when formatting code without an extension so both formatters pick the correct parser.
+- Use `-f/--file` for large samples or snapshot tests so you can iterate directly on project fixtures.
+- Reference `packages/prettier-compare/README.md` for deeper CLI details; mirror any updates here, keeping the hard requirement that commands include `--rebuild`.
+- Use single quotes for code snippets passed as CLI arguments to avoid shell interpretation issues.
+- "\n" does not get escaped into a newline when passed as a CLI argument. You should write a literal newline or use a file instead.

PATCH

echo "Patch applied successfully."
