#!/usr/bin/env bash
set -euo pipefail

cd /repo

FILE="crates/uv-resolver/src/lock/export/mod.rs"

# Idempotency check: if the fix is already applied, skip
if grep -q 'Track the activated package in the list of known conflicts' "$FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-resolver/src/lock/export/mod.rs b/crates/uv-resolver/src/lock/export/mod.rs
--- a/crates/uv-resolver/src/lock/export/mod.rs
+++ b/crates/uv-resolver/src/lock/export/mod.rs
@@ -84,6 +84,11 @@
                     name: root_name.clone(),
                 })?;

+            // Track the activated package in the list of known conflicts.
+            if let Some(conflicts) = conflicts.as_mut() {
+                conflicts.insert(ConflictItem::from(dist.id.name.clone()), MarkerTree::TRUE);
+            }
+
             if groups.prod() {

PATCH

echo "Patch applied successfully."
