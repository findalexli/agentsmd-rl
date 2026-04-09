#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'from_str_radix' crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP012.py b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP012.py
index 94e5afbfea0a3..696858570d75d 100644
--- a/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP012.py
+++ b/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP012.py
@@ -129,3 +129,9 @@ def _match_ignore(line):

 "\
 " "\u0001".encode()
+
+# Regression https://github.com/astral-sh/ruff/issues/24389
+# (Should not panic)
+IMR_HEADER = "$IMURAW\0".encode("ascii")
+# No error
+"\000\N{DIGIT ONE}".encode()
diff --git a/crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs b/crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs
index 13451bdfc7035..e1cd6dbb38326 100644
--- a/crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs
+++ b/crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs
@@ -327,11 +327,13 @@ fn literal_contains_string_only_escapes(literal: &StringLiteral, locator: &Locat
                     (true, true) => format!("{escaped}{second}{third}"),
                 };

-                if octal_codepoint.parse::<u8>().is_err() {
+                if u8::from_str_radix(&octal_codepoint, 8).is_err() {
                     return true;
                 }

-                cursor.skip_bytes(octal_codepoint.len());
+                // Cursor is currently at first octal digit, so we just
+                // skip the remaining.
+                cursor.skip_bytes(octal_codepoint.len().saturating_sub(1));
             }
             _ => {}
         }

PATCH

echo "Patch applied successfully."
