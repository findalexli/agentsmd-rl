#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'sort_by_key.*error.*range' crates/ruff_python_formatter/tests/fixtures.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_python_formatter/tests/fixtures.rs b/crates/ruff_python_formatter/tests/fixtures.rs
index d3945a65ce3b2..bfd217022bf27 100644
--- a/crates/ruff_python_formatter/tests/fixtures.rs
+++ b/crates/ruff_python_formatter/tests/fixtures.rs
@@ -477,9 +477,16 @@ fn ensure_unchanged_ast(
     formatted_unsupported_syntax_errors
         .retain(|fingerprint, _| !unformatted_unsupported_syntax_errors.contains_key(fingerprint));

+    // Sort the errors by location to ensure the snapshot output is stable.
+    let mut formatted_unsupported_syntax_errors = formatted_unsupported_syntax_errors
+        .into_values()
+        .collect::<Vec<_>>();
+    formatted_unsupported_syntax_errors
+        .sort_by_key(|error| (error.range().start(), error.range().end()));
+
     let file = SourceFileBuilder::new(input_path.file_name().unwrap(), formatted_code).finish();
     let diagnostics = formatted_unsupported_syntax_errors
-        .values()
+        .iter()
         .map(|error| {
             let mut diag = Diagnostic::new(DiagnosticId::InvalidSyntax, Severity::Error, error);
             let span = Span::from(file.clone()).with_range(error.range());
diff --git a/crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap b/crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap
index 518d8170fbef5..4f956cd97de79 100644
--- a/crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap
+++ b/crates/ruff_python_formatter/tests/snapshots/format@expression__nested_string_quote_style.py.snap
@@ -392,26 +392,26 @@ t"{('implicit concatenation', ["'single'", '"double"'])}"

 ### Unsupported Syntax Errors
 error[invalid-syntax]: Cannot reuse outer quote character in f-strings on Python 3.11 (syntax was added in Python 3.12)
-  --> nested_string_quote_style.py:30:24
+  --> nested_string_quote_style.py:28:24
    |
+26 | f"'single' quotes and {'nested string'}"
+27 | t"'single' quotes and {'nested string'}"
 28 | f'"double" quotes and {'nested string with "double" quotes'}'  # syntax error pre-3.12
+   |                        ^
 29 | t'"double" quotes and {'nested string with "double" quotes'}'
 30 | f"'single' quotes and {"nested string with 'single' quotes"}'"  # syntax error pre-3.12
-   |                        ^
-31 | t"'single' quotes and {"nested string with 'single' quotes"}'"
-32 | f'"double" quotes and {"nested string with 'single' quotes"}'  # syntax error pre-3.12
    |
 warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.

 error[invalid-syntax]: Cannot reuse outer quote character in f-strings on Python 3.11 (syntax was added in Python 3.12)
-  --> nested_string_quote_style.py:28:24
+  --> nested_string_quote_style.py:30:24
    |
-26 | f"'single' quotes and {'nested string'}"
-27 | t"'single' quotes and {'nested string'}"
 28 | f'"double" quotes and {'nested string with "double" quotes'}'  # syntax error pre-3.12
-   |                        ^
 29 | t'"double" quotes and {'nested string with "double" quotes'}'
 30 | f"'single' quotes and {"nested string with 'single' quotes"}'"  # syntax error pre-3.12
+   |                        ^
+31 | t"'single' quotes and {"nested string with 'single' quotes"}'"
+32 | f'"double" quotes and {"nested string with 'single' quotes"}'  # syntax error pre-3.12
    |
 warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.

@@ -519,25 +519,25 @@ t"{('implicit concatenation', ["'single'", '"double"'])}"

 ### Unsupported Syntax Errors
 error[invalid-syntax]: Cannot reuse outer quote character in f-strings on Python 3.11 (syntax was added in Python 3.12)
-  --> nested_string_quote_style.py:30:24
+  --> nested_string_quote_style.py:28:24
    |
+26 | f"'single' quotes and {'nested string'}"
+27 | t"'single' quotes and {'nested string'}"
 28 | f'"double" quotes and {'nested string with "double" quotes'}'  # syntax error pre-3.12
+   |                        ^
 29 | t'"double" quotes and {'nested string with "double" quotes'}'
 30 | f"'single' quotes and {"nested string with 'single' quotes"}'"  # syntax error pre-3.12
-   |                        ^
-31 | t"'single' quotes and {"nested string with 'single' quotes"}'"
-32 | f'"double" quotes and {"nested string with 'single' quotes"}'  # syntax error pre-3.12
    |
 warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.

 error[invalid-syntax]: Cannot reuse outer quote character in f-strings on Python 3.11 (syntax was added in Python 3.12)
-  --> nested_string_quote_style.py:28:24
+  --> nested_string_quote_style.py:30:24
    |
-26 | f"'single' quotes and {'nested string'}"
-27 | t"'single' quotes and {'nested string'}"
 28 | f'"double" quotes and {'nested string with "double" quotes'}'  # syntax error pre-3.12
-   |                        ^
 29 | t'"double" quotes and {'nested string with "double" quotes'}'
 30 | f"'single' quotes and {"nested string with 'single' quotes"}'"  # syntax error pre-3.12
+   |                        ^
+31 | t"'single' quotes and {"nested string with 'single' quotes"}'"
+32 | f'"double" quotes and {"nested string with 'single' quotes"}'  # syntax error pre-3.12
    |
 warning: Only accept new syntax errors if they are also present in the input. The formatter should not introduce syntax errors.

PATCH

echo "Patch applied successfully."
