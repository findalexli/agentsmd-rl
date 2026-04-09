#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'Emit `abi3t` everywhere' crates/uv-platform-tags/src/tags.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-platform-tags/src/tags.rs b/crates/uv-platform-tags/src/tags.rs
index 2f063ecfe0972..b0679a8eb15ae 100644
--- a/crates/uv-platform-tags/src/tags.rs
+++ b/crates/uv-platform-tags/src/tags.rs
@@ -180,13 +180,8 @@ impl Tags {
         }
         // 2. abi3/abi3t and no abi (e.g. executable binary)
         if let Implementation::CPython { variant } = implementation {
-            // `abi3` starts at Python 3.2, while `abi3t` starts at Python 3.15.
-            let stable_abi_minor = if variant.contains(CPythonAbiVariants::Freethreading) {
-                15
-            } else {
-                2
-            };
-            for minor in (stable_abi_minor..=python_version.1).rev() {
+            // Emit `abi3t` everywhere we'd emit `abi3` for non-free-threaded builds.
+            for minor in (2..=python_version.1).rev() {
                 if variant.contains(CPythonAbiVariants::Freethreading) {
                     for platform_tag in &platform_tags {
                         tags.push((
@@ -2730,6 +2725,19 @@ mod tests {
         cp315-cp315t-linux_x86_64
         cp315-abi3t-linux_x86_64
         cp315-none-linux_x86_64
+        cp314-abi3t-linux_x86_64
+        cp313-abi3t-linux_x86_64
+        cp312-abi3t-linux_x86_64
+        cp311-abi3t-linux_x86_64
+        cp310-abi3t-linux_x86_64
+        cp39-abi3t-linux_x86_64
+        cp38-abi3t-linux_x86_64
+        cp37-abi3t-linux_x86_64
+        cp36-abi3t-linux_x86_64
+        cp35-abi3t-linux_x86_64
+        cp34-abi3t-linux_x86_64
+        cp33-abi3t-linux_x86_64
+        cp32-abi3t-linux_x86_64
         py315-none-linux_x86_64
         py3-none-linux_x86_64
         py314-none-linux_x86_64

PATCH

echo "Patch applied successfully."
