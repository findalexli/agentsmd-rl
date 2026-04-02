#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if eq_ignore_ascii_case is already used for Version check, skip
if grep -q 'eq_ignore_ascii_case("Version")' crates/uv-pypi-types/src/metadata/metadata_resolver.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-pypi-types/src/metadata/metadata_resolver.rs b/crates/uv-pypi-types/src/metadata/metadata_resolver.rs
index daebbda6b82b4..912008e6c7a6f 100644
--- a/crates/uv-pypi-types/src/metadata/metadata_resolver.rs
+++ b/crates/uv-pypi-types/src/metadata/metadata_resolver.rs
@@ -79,7 +79,7 @@ impl ResolutionMetadata {
             .collect::<Box<_>>();
         let dynamic = headers
             .get_all_values("Dynamic")
-            .any(|field| field == "Version");
+            .any(|field| field.eq_ignore_ascii_case("Version"));

         Ok(Self {
             name,
@@ -112,12 +112,15 @@ impl ResolutionMetadata {
         // If any of the fields we need are marked as dynamic, we can't use the `PKG-INFO` file.
         let mut dynamic = false;
         for field in headers.get_all_values("Dynamic") {
-            match field.as_str() {
-                "Requires-Python" => return Err(MetadataError::DynamicField("Requires-Python")),
-                "Requires-Dist" => return Err(MetadataError::DynamicField("Requires-Dist")),
-                "Provides-Extra" => return Err(MetadataError::DynamicField("Provides-Extra")),
-                "Version" => dynamic = true,
-                _ => (),
+            let field = field.as_str();
+            if field.eq_ignore_ascii_case("Requires-Python") {
+                return Err(MetadataError::DynamicField("Requires-Python"));
+            } else if field.eq_ignore_ascii_case("Requires-Dist") {
+                return Err(MetadataError::DynamicField("Requires-Dist"));
+            } else if field.eq_ignore_ascii_case("Provides-Extra") {
+                return Err(MetadataError::DynamicField("Provides-Extra"));
+            } else if field.eq_ignore_ascii_case("Version") {
+                dynamic = true;
             }
         }

PATCH

echo "Patch applied successfully."
