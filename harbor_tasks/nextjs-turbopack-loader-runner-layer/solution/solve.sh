#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency: check if the fix is already applied
if grep -q 'Layer::new(rcstr!("webpack_loaders"))' turbopack/crates/turbopack/src/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack/src/lib.rs b/turbopack/crates/turbopack/src/lib.rs
index d7660f3bcd3a5..8e815936e7f88 100644
--- a/turbopack/crates/turbopack/src/lib.rs
+++ b/turbopack/crates/turbopack/src/lib.rs
@@ -716,7 +716,7 @@ async fn process_default_internal(
             *execution_context,
             Some(import_map),
             None,
-            Layer::new(rcstr!("turbopack_use_loaders")),
+            Layer::new(rcstr!("webpack_loaders")),
             false,
         )
         .to_resolved()

PATCH

echo "Patch applied successfully."
