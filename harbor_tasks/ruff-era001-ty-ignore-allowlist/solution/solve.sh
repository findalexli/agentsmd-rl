#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q 'ty:\\s\*ignore' crates/ruff_linter/src/rules/eradicate/detection.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/eradicate/ERA001.py b/crates/ruff_linter/resources/test/fixtures/eradicate/ERA001.py
index e33577e5689bcf..868f06ebdcafd8 100644
--- a/crates/ruff_linter/resources/test/fixtures/eradicate/ERA001.py
+++ b/crates/ruff_linter/resources/test/fixtures/eradicate/ERA001.py
@@ -91,7 +91,10 @@ class A():
 # Foobar


-# Regression tests for https://github.com/astral-sh/ruff/issues/19713
+# Regression tests for https://github.com/astral-sh/ruff/issues/19713,
+# https://github.com/astral-sh/ruff/issues/24186
+
+# ty: ignore

 # mypy: ignore-errors
 # pyright: ignore-errors
diff --git a/crates/ruff_linter/src/rules/eradicate/detection.rs b/crates/ruff_linter/src/rules/eradicate/detection.rs
index c4a0b9f5858233..94ea58592a89c7 100644
--- a/crates/ruff_linter/src/rules/eradicate/detection.rs
+++ b/crates/ruff_linter/src/rules/eradicate/detection.rs
@@ -25,6 +25,7 @@ static ALLOWLIST_REGEX: LazyLock<Regex> = LazyLock::new(|| {
         |   ruff\s*:\s*(disable|enable)
         |   mypy:
         |   type:\s*ignore
+        |   ty:\s*ignore
         |   SPDX-License-Identifier:
         |   fmt:\s*(on|off|skip)
         |   region|endregion
@@ -322,6 +323,15 @@ mod tests {
         assert!(!comment_contains_code("# type:ignore", &[]));
         assert!(!comment_contains_code("# type: ignore[import]", &[]));
         assert!(!comment_contains_code("# type:ignore[import]", &[]));
+        assert!(!comment_contains_code("# ty: ignore", &[]));
+        assert!(!comment_contains_code("# ty:ignore", &[]));
+        assert!(!comment_contains_code("# ty: ignore[import]", &[]));
+        assert!(!comment_contains_code("# ty:ignore[import]", &[]));
+        assert!(!comment_contains_code(
+            "# ty: ignore[missing-argument, invalid-argument-type]",
+            &[]
+        ));
+        assert!(!comment_contains_code("# ty: ignore[]", &[]));
         assert!(!comment_contains_code(
             "# TODO: Do that",
             &["TODO".to_string()]

PATCH

echo "Patch applied successfully."
