#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'interpolated_element_expression_range' crates/ruff_python_formatter/src/other/interpolated_string_element.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.options.json b/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.options.json
new file mode 100644
index 0000000000000..0cd39ea2f5bc4
--- /dev/null
+++ b/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.options.json
@@ -0,0 +1,8 @@
+[
+  {
+    "target_version": "3.11"
+  },
+  {
+    "target_version": "3.12"
+  }
+]
diff --git a/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.py b/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.py
new file mode 100644
index 0000000000000..3354a910bf8fa
--- /dev/null
+++ b/crates/ruff_python_formatter/resources/test/fixtures/ruff/expression/fstring_multiline_replacement_field.py
@@ -0,0 +1,4 @@
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {
+    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
+}":
+    pass
diff --git a/crates/ruff_python_formatter/src/other/interpolated_string_element.rs b/crates/ruff_python_formatter/src/other/interpolated_string_element.rs
index 49495aa646999..4ee4243ea7e8e 100644
--- a/crates/ruff_python_formatter/src/other/interpolated_string_element.rs
+++ b/crates/ruff_python_formatter/src/other/interpolated_string_element.rs
@@ -3,9 +3,10 @@ use std::borrow::Cow;
 use ruff_formatter::{Buffer, FormatOptions as _, RemoveSoftLinesBuffer, format_args, write};
 use ruff_python_ast::{
     AnyStringFlags, ConversionFlag, Expr, InterpolatedElement, InterpolatedStringElement,
-    InterpolatedStringLiteralElement,
+    InterpolatedStringLiteralElement, StringFlags,
 };
-use ruff_text_size::{Ranged, TextSlice};
+use ruff_source_file::LineRanges;
+use ruff_text_size::{Ranged, TextRange, TextSlice};
 
 use crate::comments::dangling_open_parenthesis_comments;
 use crate::context::{
@@ -16,7 +17,7 @@ use crate::prelude::*;
 use crate::string::normalize_string;
 use crate::verbatim::verbatim_text;
 
-use super::interpolated_string::InterpolatedStringContext;
+use super::interpolated_string::{InterpolatedStringContext, InterpolatedStringLayout};
 
 /// Formats an f-string element which is either a literal or a formatted expression.
 ///
@@ -155,8 +156,23 @@ impl Format<PyFormatContext<'_>> for FormatInterpolatedElement<'_> {
         } else {
             let comments = f.context().comments().clone();
             let dangling_item_comments = comments.dangling(self.element);
-
-            let multiline = self.context.is_multiline();
+            let flags = self.context.flags();
+
+            // Before Python 3.12, non-triple-quoted f-strings cannot introduce new multiline
+            // replacement fields. Preserve existing multiline fields from unsupported syntax
+            // inputs, but keep originally flat fields flat.
+            let multiline = self.context.is_multiline()
+                && (f.options().target_version().supports_pep_701()
+                    || flags.is_triple_quoted()
+                    || f.context()
+                        .source()
+                        .contains_line_break(interpolated_element_expression_range(self.element)));
+
+            let context = if multiline {
+                self.context
+            } else {
+                InterpolatedStringContext::new(flags, InterpolatedStringLayout::Flat)
+            };
 
             // If an expression starts with a `{`, we need to add a space before the
             // curly brace to avoid turning it into a literal curly with `{{`.
@@ -184,10 +200,10 @@ impl Format<PyFormatContext<'_>> for FormatInterpolatedElement<'_> {
                 let state = match f.context().interpolated_string_state() {
                     InterpolatedStringState::InsideInterpolatedElement(_)
                     | InterpolatedStringState::NestedInterpolatedElement(_) => {
-                        InterpolatedStringState::NestedInterpolatedElement(self.context)
+                        InterpolatedStringState::NestedInterpolatedElement(context)
                     }
                     InterpolatedStringState::Outside => {
-                        InterpolatedStringState::InsideInterpolatedElement(self.context)
+                        InterpolatedStringState::InsideInterpolatedElement(context)
                     }
                 };
                 let f = &mut WithInterpolatedStringState::new(state, f);
@@ -216,7 +232,7 @@ impl Format<PyFormatContext<'_>> for FormatInterpolatedElement<'_> {
                     token(":").fmt(f)?;
 
                     for element in &format_spec.elements {
-                        FormatInterpolatedStringElement::new(element, self.context).fmt(f)?;
+                        FormatInterpolatedStringElement::new(element, context).fmt(f)?;
                     }
                 }
 
@@ -268,6 +284,14 @@ impl Format<PyFormatContext<'_>> for FormatInterpolatedElement<'_> {
     }
 }
 
+fn interpolated_element_expression_range(element: &InterpolatedElement) -> TextRange {
+    element
+        .format_spec
+        .as_deref()
+        .map(|format_spec| TextRange::new(element.start(), format_spec.start()))
+        .unwrap_or_else(|| element.range())
+}
+
 fn needs_bracket_spacing(expr: &Expr, context: &PyFormatContext) -> bool {
     // Ruff parenthesizes single element tuples, that's why we shouldn't insert
     // a space around the curly braces for those.
diff --git a/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring.py.snap b/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring.py.snap
index 421bf68c6ad1f..61dd90b33182a 100644
--- a/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring.py.snap
+++ b/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring.py.snap
@@ -1337,27 +1337,15 @@ if f"aaaaaaaaaaa {ttttteeeeeeeeest} more {  # comment
 }":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {
     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
 }":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {
     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
 }":
     pass
@@ -2169,27 +2157,15 @@ if f"aaaaaaaaaaa {ttttteeeeeeeeest} more {  # comment
 }":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {
     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
 }":
     pass
 
-if f"aaaaaaaaaaa {
-    [
-        ttttteeeeeeeeest,
-    ]
-} more {
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {
     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
 }":
     pass
@@ -2435,27 +2411,3 @@ error[invalid-syntax]: Cannot reuse outer quote character in f-strings on Python
 179 | f"foo {'"bar"'}"
     |
 warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.
-
-error[invalid-syntax]: Cannot use line breaks in non-triple-quoted f-string replacement fields on Python 3.10 (syntax was added in Python 3.12)
-   --> fstring.py:572:8
-    |
-570 |         ttttteeeeeeeeest,
-571 |     ]
-572 | } more {
-    |        ^
-573 |     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
-574 | }":
-    |
-warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.
-
-error[invalid-syntax]: Cannot use line breaks in non-triple-quoted f-string replacement fields on Python 3.10 (syntax was added in Python 3.12)
-   --> fstring.py:581:8
-    |
-579 |         ttttteeeeeeeeest,
-580 |     ]
-581 | } more {
-    |        ^
-582 |     aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
-583 | }":
-    |
-warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.
diff --git a/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring_multiline_replacement_field.py.snap b/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring_multiline_replacement_field.py.snap
new file mode 100644
index 0000000000000..d002931dea271
--- /dev/null
+++ b/crates/ruff_python_formatter/tests/snapshots/format@expression__fstring_multiline_replacement_field.py.snap
@@ -0,0 +1,62 @@
+---
+source: crates/ruff_python_formatter/tests/fixtures.rs
+---
+## Input
+```python
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest,]} more {
+    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
+}":
+    pass
+```
+
+## Outputs
+### Output 1
+```
+indent-style               = space
+line-width                 = 88
+indent-width               = 4
+quote-style                = Double
+line-ending                = LineFeed
+magic-trailing-comma       = Respect
+docstring-code             = Disabled
+docstring-code-line-width  = "dynamic"
+preview                    = Disabled
+target_version             = 3.11
+source_type                = Python
+nested-string-quote-style  = alternating
+```
+
+```python
+if f"aaaaaaaaaaa {[ttttteeeeeeeeest]} more {
+    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
+}":
+    pass
+```
+
+
+### Output 2
+```
+indent-style               = space
+line-width                 = 88
+indent-width               = 4
+quote-style                = Double
+line-ending                = LineFeed
+magic-trailing-comma       = Respect
+docstring-code             = Disabled
+docstring-code-line-width  = "dynamic"
+preview                    = Disabled
+target_version             = 3.12
+source_type                = Python
+nested-string-quote-style  = alternating
+```
+
+```python
+if f"aaaaaaaaaaa {
+    [
+        ttttteeeeeeeeest,
+    ]
+} more {
+    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
+}":
+    pass
+```

PATCH

echo "Patch applied successfully."
