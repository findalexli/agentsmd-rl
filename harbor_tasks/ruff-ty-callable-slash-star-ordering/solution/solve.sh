#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q "parameter must appear before" crates/ty_python_semantic/src/types/display.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_python_semantic/src/types/display.rs b/crates/ty_python_semantic/src/types/display.rs
index 828c9e78590cac..7b5649e6a6413f 100644
--- a/crates/ty_python_semantic/src/types/display.rs
+++ b/crates/ty_python_semantic/src/types/display.rs
@@ -2166,14 +2166,6 @@ impl<'db> FmtDetailed<'db> for DisplayParameters<'_, 'db> {

             for parameter in parameters {
                 // Handle special separators
-                if !star_added && parameter.is_keyword_only() {
-                    if !first {
-                        f.write_str(arg_separator)?;
-                    }
-                    f.write_char('*')?;
-                    star_added = true;
-                    first = false;
-                }
                 if parameter.is_positional_only() {
                     needs_slash = true;
                 } else if needs_slash {
@@ -2184,6 +2176,14 @@ impl<'db> FmtDetailed<'db> for DisplayParameters<'_, 'db> {
                     needs_slash = false;
                     first = false;
                 }
+                if !star_added && parameter.is_keyword_only() {
+                    if !first {
+                        f.write_str(arg_separator)?;
+                    }
+                    f.write_char('*')?;
+                    star_added = true;
+                    first = false;
+                }

                 // Add comma before parameter if not first
                 if !first {
@@ -3254,6 +3254,20 @@ mod tests {
             @"(x, *, y) -> None"
         );

+        // '/' parameter must appear before '*' parameter
+        assert_snapshot!(
+            display_signature(
+                &db,
+                [
+                    Parameter::positional_only(Some(Name::new_static("a"))),
+                    Parameter::keyword_only(Name::new_static("x")),
+                    Parameter::keyword_only(Name::new_static("y")),
+                ],
+                Some(Type::none(&db))
+            ),
+            @"(a, /, *, x, y) -> None"
+        );
+
         // A mix of all parameter kinds.
         assert_snapshot!(
             display_signature(

PATCH

echo "Patch applied successfully."
