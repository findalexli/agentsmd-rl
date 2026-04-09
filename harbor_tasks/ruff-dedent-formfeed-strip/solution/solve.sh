#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q "trim_start_matches.*0C" crates/ruff_python_trivia/src/textwrap.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/ruff/RUF072.py b/crates/ruff_linter/resources/test/fixtures/ruff/RUF072.py
index 7c422fb1c5d76c..0261718218dbd9 100644
--- a/crates/ruff_linter/resources/test/fixtures/ruff/RUF072.py
+++ b/crates/ruff_linter/resources/test/fixtures/ruff/RUF072.py
@@ -176,4 +176,12 @@
     1
     2
 finally:
-    pass
\ No newline at end of file
+    pass
+
+
+# Regression test for https://github.com/astral-sh/ruff/issues/24373
+# (`try` is preceded by a form feed below)
+try:
+    1
+finally:
+    pass
diff --git a/crates/ruff_linter/src/rules/ruff/snapshots/ruff_linter__rules__ruff__tests__preview__RUF072_RUF072.py.snap b/crates/ruff_linter/src/rules/ruff/snapshots/ruff_linter__rules__ruff__tests__preview__RUF072_RUF072.py.snap
index c46cec7598b757..2e420a0007e32a 100644
--- a/crates/ruff_linter/src/rules/ruff/snapshots/ruff_linter__rules__ruff__tests__preview__RUF072_RUF072.py.snap
+++ b/crates/ruff_linter/src/rules/ruff/snapshots/ruff_linter__rules__ruff__tests__preview__RUF072_RUF072.py.snap
@@ -349,3 +349,25 @@ help: Remove the `finally` clause
     -     pass
 175 + 1
 176 + 2
+177 |
+178 |
+179 | # Regression test for https://github.com/astral-sh/ruff/issues/24373
+
+RUF072 [*] Empty `finally` clause
+   --> RUF072.py:186:1
+    |
+184 |   try:
+185 |       1
+186 | / finally:
+187 | |     pass
+    | |________^
+    |
+help: Remove the `finally` clause
+181 |
+182 | # Regression test for https://github.com/astral-sh/ruff/issues/24373
+183 | # (`try` is preceded by a form feed below)
+    - try:
+    -     1
+    - finally:
+    -     pass
+184 + 1
diff --git a/crates/ruff_python_trivia/src/textwrap.rs b/crates/ruff_python_trivia/src/textwrap.rs
index 7ef766fbfd9197..df7b1618dea2f8 100644
--- a/crates/ruff_python_trivia/src/textwrap.rs
+++ b/crates/ruff_python_trivia/src/textwrap.rs
@@ -203,6 +203,11 @@ pub fn dedent(text: &str) -> Cow<'_, str> {
 /// # Panics
 /// If the first line is indented by less than the provided indent.
 pub fn dedent_to(text: &str, indent: &str) -> Option<String> {
+    // The caller may provide an `indent` from source code by taking
+    // a range of text beginning with the start of a line. In Python,
+    // while a line may begin with form feeds, these do not contribute
+    // to the indentation. So we strip those here.
+    let indent = indent.trim_start_matches('\x0C');
     // Look at the indentation of the first non-empty line, to determine the "baseline" indentation.
     let mut first_comment_indent = None;
     let existing_indent_len = text
@@ -753,4 +758,18 @@ mod tests {
         ].join("");
         assert_eq!(dedent_to(&x, ""), Some(y));
     }
+
+    #[test]
+    #[rustfmt::skip]
+    fn dedent_to_ignores_leading_form_feeds_in_provided_indentation() {
+        let x = [
+            "  1",
+            "  2",
+        ].join("\n");
+        let y = [
+            "1",
+            "2",
+        ].join("\n");
+        assert_eq!(dedent_to(&x, "\x0C\x0C"), Some(y));
+    }
 }

PATCH

echo "Patch applied successfully."
