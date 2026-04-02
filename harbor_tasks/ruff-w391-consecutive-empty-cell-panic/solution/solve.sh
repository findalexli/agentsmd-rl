#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'content_ranges' crates/ruff_notebook/src/cell.rs 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_notebook/src/lib.rs b/crates/ruff_notebook/src/lib.rs
index e95c483a2f..6617560746 100644
--- a/crates/ruff_notebook/src/lib.rs
+++ b/crates/ruff_notebook/src/lib.rs
@@ -5,6 +5,8 @@ pub use index::*;
 pub use notebook::*;
 pub use schema::*;

+pub(crate) const SYNTHETIC_CELL_SEPARATOR: char = '\n';
+
 mod cell;
 mod index;
 mod notebook;
diff --git a/crates/ruff_notebook/src/cell.rs b/crates/ruff_notebook/src/cell.rs
index 315abe0ef0..1c7b749e05 100644
--- a/crates/ruff_notebook/src/cell.rs
+++ b/crates/ruff_notebook/src/cell.rs
@@ -5,8 +5,8 @@ use itertools::Itertools;

 use ruff_text_size::{TextRange, TextSize};

-use crate::CellMetadata;
 use crate::schema::{Cell, SourceValue};
+use crate::{CellMetadata, SYNTHETIC_CELL_SEPARATOR};

 impl fmt::Display for SourceValue {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
@@ -329,6 +329,18 @@ impl CellOffsets {
             .tuple_windows()
             .map(|(start, end)| TextRange::new(*start, *end))
     }
+
+    /// Returns an iterator over the concatenated source ranges covered by each cell's actual
+    /// contents, excluding Ruff's synthetic trailing newline separator.
+    pub fn content_ranges(&self) -> impl Iterator<Item = TextRange> {
+        self.ranges().map(|range| {
+            let end = range
+                .end()
+                .checked_sub(TextSize::of(SYNTHETIC_CELL_SEPARATOR))
+                .expect("cell ranges should include the synthetic separator newline");
+            TextRange::new(range.start(), end)
+        })
+    }
 }

 impl Deref for CellOffsets {
diff --git a/crates/ruff_notebook/src/notebook.rs b/crates/ruff_notebook/src/notebook.rs
index e0874b3f4a..fb9caf7c22 100644
--- a/crates/ruff_notebook/src/notebook.rs
+++ b/crates/ruff_notebook/src/notebook.rs
@@ -18,7 +18,7 @@ use ruff_text_size::{TextRange, TextSize};
 use crate::cell::CellOffsets;
 use crate::index::NotebookIndex;
 use crate::schema::{Cell, RawNotebook, SortAlphabetically, SourceValue};
-use crate::{CellMetadata, CellStart, RawNotebookMetadata, schema};
+use crate::{CellMetadata, CellStart, RawNotebookMetadata, SYNTHETIC_CELL_SEPARATOR, schema};

 /// Run round-trip source code generation on a given Jupyter notebook file path.
 pub fn round_trip(path: &Path) -> anyhow::Result<String> {
@@ -146,7 +146,7 @@ impl Notebook {
                 SourceValue::String(string) => string.clone(),
                 SourceValue::StringArray(string_array) => string_array.join(""),
             };
-            current_offset += TextSize::of(&cell_contents) + TextSize::new(1);
+            current_offset += TextSize::of(&cell_contents) + TextSize::of(SYNTHETIC_CELL_SEPARATOR);
             contents.push(cell_contents);
             cell_offsets.push(current_offset);
         }
@@ -199,7 +199,11 @@ impl Notebook {
             // The additional newline at the end is to maintain consistency for
             // all cells. These newlines will be removed before updating the
             // source code with the transformed content. Refer `update_cell_content`.
-            source_code: contents.join("\n") + "\n",
+            source_code: {
+                let mut source_code = contents.join("\n");
+                source_code.push(SYNTHETIC_CELL_SEPARATOR);
+                source_code
+            },
             cell_offsets,
             valid_code_cells,
             trailing_newline,
diff --git a/crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs b/crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs
index cd6b416e5a..ed4ddbfb42 100644
--- a/crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs
+++ b/crates/ruff_linter/src/rules/pycodestyle/rules/too_many_newlines_at_end_of_file.rs
@@ -1,6 +1,5 @@
 use std::iter::Peekable;

-use itertools::Itertools;
 use ruff_macros::{ViolationMetadata, derive_message_formats};
 use ruff_notebook::CellOffsets;
 use ruff_python_ast::token::{Token, TokenKind, Tokens};
@@ -64,32 +63,38 @@ pub(crate) fn too_many_newlines_at_end_of_file(
     tokens: &Tokens,
     cell_offsets: Option<&CellOffsets>,
 ) {
-    let mut tokens_iter = tokens.iter().rev().peekable();
-
     if let Some(cell_offsets) = cell_offsets {
-        notebook_newline_diagnostics(tokens_iter, cell_offsets, context);
+        notebook_newline_diagnostics(tokens, cell_offsets, context);
     } else {
+        let mut tokens_iter = tokens.iter().rev().peekable();
         newline_diagnostic(&mut tokens_iter, false, context);
     }
 }

 /// Collects trailing newline diagnostics for each cell
-fn notebook_newline_diagnostics<'a>(
-    mut tokens_iter: Peekable<impl Iterator<Item = &'a Token>>,
+fn notebook_newline_diagnostics(
+    tokens: &Tokens,
     cell_offsets: &CellOffsets,
     context: &LintContext,
 ) {
-    let offset_iter = cell_offsets.iter().rev();
-
-    // NB: When interpreting the below, recall that the iterators
-    // have been reversed.
-    for &offset in offset_iter {
-        // Advance to offset
-        tokens_iter
-            .peeking_take_while(|tok| tok.end() >= offset)
-            .for_each(drop);
-
+    let mut remaining_tokens = &tokens[..];
+
+    for range in cell_offsets.content_ranges() {
+        let start_index = remaining_tokens
+            .iter()
+            .position(|token| token.end() > range.start())
+            .unwrap_or(remaining_tokens.len());
+        remaining_tokens = &remaining_tokens[start_index..];
+
+        let end_index = remaining_tokens
+            .iter()
+            .position(|token| token.start() >= range.end())
+            .unwrap_or(remaining_tokens.len());
+        let (cell_tokens, rest) = remaining_tokens.split_at(end_index);
+
+        let mut tokens_iter = cell_tokens.iter().rev().peekable();
         newline_diagnostic(&mut tokens_iter, true, context);
+        remaining_tokens = rest;
     }
 }

PATCH

echo "Gold patch applied successfully."
