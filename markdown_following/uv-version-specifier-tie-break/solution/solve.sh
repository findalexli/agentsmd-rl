#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotency guard: if the canonical tie-break already exists, skip.
if grep -q "a.operator().cmp(b.operator())" crates/uv-pep440/src/version_specifier.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/uv-pep440/src/version_specifier.rs b/crates/uv-pep440/src/version_specifier.rs
index 17928b881218c..c86e8004c12d1 100644
--- a/crates/uv-pep440/src/version_specifier.rs
+++ b/crates/uv-pep440/src/version_specifier.rs
@@ -67,7 +67,14 @@ impl VersionSpecifiers {
     fn from_unsorted(mut specifiers: Vec<VersionSpecifier>) -> Self {
         // TODO(konsti): This seems better than sorting on insert and not getting the size hint,
         // but i haven't measured it.
-        specifiers.sort_by(|a, b| a.version().cmp(b.version()));
+        //
+        // Tie-break on the operator so semantically equivalent same-version intervals such as
+        // `>=1.4.4,<=1.4.4` and `<=1.4.4,>=1.4.4` normalize to the same representation.
+        specifiers.sort_by(|a, b| {
+            a.version()
+                .cmp(b.version())
+                .then_with(|| a.operator().cmp(b.operator()))
+        });
         Self(specifiers.into_boxed_slice())
     }

PATCH

echo "Patch applied."
