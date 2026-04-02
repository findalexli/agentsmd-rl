#!/usr/bin/env bash
set -euo pipefail

cd /repo 2>/dev/null || cd /workspace/ruff

# Idempotency check: if Cow is already imported in display_list.rs, patch is applied
if grep -q 'use std::borrow::Cow' crates/ruff_annotate_snippets/src/renderer/display_list.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_annotate_snippets/src/renderer/display_list.rs b/crates/ruff_annotate_snippets/src/renderer/display_list.rs
index 7507f88a22b20..75cbd3040ea0a 100644
--- a/crates/ruff_annotate_snippets/src/renderer/display_list.rs
+++ b/crates/ruff_annotate_snippets/src/renderer/display_list.rs
@@ -32,6 +32,7 @@
 //!
 //! The above snippet has been built out of the following structure:
 use crate::{Id, snippet};
+use std::borrow::Cow;
 use std::cmp::{Reverse, max, min};
 use std::collections::HashMap;
 use std::fmt::Display;
@@ -1863,12 +1864,21 @@ const OUTPUT_REPLACEMENTS: &[(char, &str)] = &[
     ('\u{2069}', ""),
 ];

-fn normalize_whitespace(str: &str) -> String {
+fn normalize_whitespace(str: &str) -> Cow<'_, str> {
+    // This is an optimization to avoid repeated `str::replace` calls in the typical case of no
+    // valid replacements. Note that this list needs to be kept in sync with `OUTPUT_REPLACEMENTS`.
+    if !str.contains([
+        '\t', '\u{200d}', '\u{202a}', '\u{202b}', '\u{202d}', '\u{202e}', '\u{2066}', '\u{2067}',
+        '\u{2068}', '\u{202c}', '\u{2069}',
+    ]) {
+        return Cow::Borrowed(str);
+    }
+
     let mut s = str.to_owned();
     for (c, replacement) in OUTPUT_REPLACEMENTS {
         s = s.replace(*c, replacement);
     }
-    s
+    Cow::Owned(s)
 }

 fn overlaps(
diff --git a/crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs b/crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs
index ec834e1bce915..73b30cefca10d 100644
--- a/crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs
+++ b/crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs
@@ -38,7 +38,8 @@ impl StyledBuffer {
     }

     pub(crate) fn render(&self, stylesheet: &Stylesheet) -> Result<String, fmt::Error> {
-        let mut str = String::new();
+        let capacity = self.lines.iter().map(|line| line.len()).sum();
+        let mut str = String::with_capacity(capacity);
         for (i, line) in self.lines.iter().enumerate() {
             let mut current_style = stylesheet.none;
             for ch in line {
@@ -49,11 +50,11 @@ impl StyledBuffer {
                     current_style = ch.style;
                     write!(str, "{}", current_style.render())?;
                 }
-                write!(str, "{}", ch.ch)?;
+                str.push(ch.ch);
             }
             write!(str, "{}", current_style.render_reset())?;
             if i != self.lines.len() - 1 {
-                writeln!(str)?;
+                str.push('\n');
             }
         }
         Ok(str)
@@ -74,10 +75,18 @@ impl StyledBuffer {
     /// If `line` does not exist in our buffer, adds empty lines up to the given
     /// and fills the last line with unstyled whitespace.
     pub(crate) fn puts(&mut self, line: usize, col: usize, string: &str, style: Style) {
-        let mut n = col;
-        for c in string.chars() {
-            self.putc(line, n, c, style);
-            n += 1;
+        if string.is_empty() {
+            return;
+        }
+        self.ensure_lines(line);
+        let char_count = string.chars().count();
+        let needed = col + char_count;
+        if needed > self.lines[line].len() {
+            self.lines[line].resize(needed, StyledChar::SPACE);
+        }
+        let line = &mut self.lines[line];
+        for (i, c) in string.chars().enumerate() {
+            line[col + i] = StyledChar::new(c, style);
         }
     }
     /// For given `line` inserts `string` with `style` after old content of that line,

PATCH

echo "Patch applied successfully."
