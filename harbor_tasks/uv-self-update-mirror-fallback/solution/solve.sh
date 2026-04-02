#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

FILE="crates/uv-bin-install/src/lib.rs"

# Idempotency: check if already fixed (mirror URL in Uv arm)
if grep -A5 'Self::Uv =>' "$FILE" | grep -q 'VERSIONS_MANIFEST_MIRROR'; then
    echo "Already patched."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-bin-install/src/lib.rs b/crates/uv-bin-install/src/lib.rs
index aaa5d0f42b34e..6ab08251ff053 100644
--- a/crates/uv-bin-install/src/lib.rs
+++ b/crates/uv-bin-install/src/lib.rs
@@ -113,12 +113,11 @@ impl Binary {
                     .unwrap(),
                 DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson")).unwrap(),
             ],
-            Self::Uv => {
-                vec![
-                    DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson"))
-                        .unwrap(),
-                ]
-            }
+            Self::Uv => vec![
+                DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_MIRROR}/{name}.ndjson"))
+                    .unwrap(),
+                DisplaySafeUrl::parse(&format!("{VERSIONS_MANIFEST_URL}/{name}.ndjson")).unwrap(),
+            ],
         }
     }

@@ -393,11 +392,13 @@ impl RetriableError for Error {

     /// Returns `true` if trying an alternative URL makes sense after this error.
     ///
-    /// All errors arising from downloading (including streaming during extraction)
-    /// qualify.
+    /// Download and streaming failures qualify, as do malformed manifest responses.
     fn should_try_next_url(&self) -> bool {
         match self {
-            Self::Download { .. } | Self::ManifestFetch { .. } => true,
+            Self::Download { .. }
+            | Self::ManifestFetch { .. }
+            | Self::ManifestParse(..)
+            | Self::ManifestUtf8(..) => true,
             Self::Stream { .. } => true,
             Self::RetriedError { err, .. } => err.should_try_next_url(),
             err => {

PATCH

echo "Patch applied successfully."
