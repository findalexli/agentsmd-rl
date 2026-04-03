#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'css_display::CssDisplay' crates/biome_html_formatter/src/html/lists/element_list.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.changeset/odd-schools-behave.md b/.changeset/odd-schools-behave.md
new file mode 100644
index 000000000000..49a21ba42bb0
--- /dev/null
+++ b/.changeset/odd-schools-behave.md
@@ -0,0 +1,14 @@
+---
+"@biomejs/biome": patch
+---
+
+Fixed [#4927](https://github.com/biomejs/biome/issues/4927), [#6407](https://github.com/biomejs/biome/issues/6407): The HTML formatter will now correctly break a block-like element if it has more than 2 children, and at least one of them is another block-like element.
+
+```diff
+-<div>a<div>b</div> c</div>
++<div>
++  a
++  <div>b</div>
++  c
++</div>
+```
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
diff --git a/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html b/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html
new file mode 100644
index 000000000000..5f55ad19fb2f
--- /dev/null
+++ b/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html
@@ -0,0 +1 @@
+<div>a<div>b</div> c</div>
diff --git a/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html.snap b/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html.snap
new file mode 100644
index 000000000000..c97479689f70
--- /dev/null
+++ b/crates/biome_html_formatter/tests/specs/html/whitespace/force-break-nontext-and-non-sensitive-sibling.html.snap
@@ -0,0 +1,39 @@
+---
+source: crates/biome_formatter_test/src/snapshot_builder.rs
+info: whitespace/force-break-nontext-and-non-sensitive-sibling.html
+---
+# Input
+
+```html
+<div>a<div>b</div> c</div>
+
+```
+
+
+=============================
+
+# Outputs
+
+## Output 1
+
+-----
+Indent style: Tab
+Indent width: 2
+Line ending: LF
+Line width: 80
+Attribute Position: Auto
+Bracket same line: false
+Whitespace sensitivity: css
+Indent script and style: false
+Self close void elements: never
+Trailing newline: true
+-----
+
+```html
+<div>
+	a
+	<div>b</div>
+	c
+</div>
+
+```
diff --git a/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html b/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html
new file mode 100644
index 000000000000..f0012d0730a8
--- /dev/null
+++ b/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html
@@ -0,0 +1 @@
+<div>123<meta attr />456</div>
diff --git a/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html.snap b/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html.snap
new file mode 100644
index 000000000000..41a73c16e63a
--- /dev/null
+++ b/crates/biome_html_formatter/tests/specs/html/whitespace/no-break-display-none.html.snap
@@ -0,0 +1,35 @@
+---
+source: crates/biome_formatter_test/src/snapshot_builder.rs
+info: whitespace/no-break-display-none.html
+---
+# Input
+
+```html
+<div>123<meta attr />456</div>
+
+```
+
+
+=============================
+
+# Outputs
+
+## Output 1
+
+-----
+Indent style: Tab
+Indent width: 2
+Line ending: LF
+Line width: 80
+Attribute Position: Auto
+Bracket same line: false
+Whitespace sensitivity: css
+Indent script and style: false
+Self close void elements: never
+Trailing newline: true
+-----
+
+```html
+<div>123<meta attr>456</div>
+
+```
diff --git a/crates/biome_html_formatter/tests/specs/prettier/html/tags/tags2.html.snap b/crates/biome_html_formatter/tests/specs/prettier/html/tags/tags2.html.snap
index 2364249ccf5d..f876130207f8 100644
--- a/crates/biome_html_formatter/tests/specs/prettier/html/tags/tags2.html.snap
+++ b/crates/biome_html_formatter/tests/specs/prettier/html/tags/tags2.html.snap
@@ -25,26 +25,16 @@ info: html/tags/tags2.html
 ```diff
 --- Prettier
 +++ Biome
-@@ -1,14 +1,12 @@
+@@ -1,6 +1,6 @@
  <div>
 -  before<noscript>noscript long long long long long long long long</noscript
 -  >after
-+  before
-+  <noscript>noscript long long long long long long long long</noscript>
++  before<noscript>noscript long long long long long long long long</noscript>
 +  after
  </div>

  <div>
-   before
--  <details>
--    <summary>summary long long long long</summary>
--    details
--  </details>
-+  <details><summary>summary long long long long</summary>details</details>
-   after
- </div>
-
-@@ -21,8 +19,8 @@
+@@ -21,8 +21,8 @@
  <div>
    before<object data="horse.wav">
      <param name="autoplay" value="true" />
@@ -55,7 +45,7 @@ info: html/tags/tags2.html
  </div>

  <div>
-@@ -33,8 +31,7 @@
+@@ -33,8 +33,7 @@
      high=".7"
      optimum=".5"
      value=".2"
@@ -71,14 +61,16 @@ info: html/tags/tags2.html

 ```html
 <div>
-  before
-  <noscript>noscript long long long long long long long long</noscript>
+  before<noscript>noscript long long long long long long long long</noscript>
   after
 </div>

 <div>
   before
-  <details><summary>summary long long long long</summary>details</details>
+  <details>
+    <summary>summary long long long long</summary>
+    details
+  </details>
   after
 </div>

PATCH

echo "Patch applied successfully."
