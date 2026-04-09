#!/bin/bash
set -e

cd /workspace/sui

# Apply the fix for Display v2 scoping issue
patch -p1 <<'PATCH'
diff --git a/crates/sui-indexer-alt-graphql/src/api/types/display.rs b/crates/sui-indexer-alt-graphql/src/api/types/display.rs
index 78a10711ce6e..4c8020c48a34 100644
--- a/crates/sui-indexer-alt-graphql/src/api/types/display.rs
+++ b/crates/sui-indexer-alt-graphql/src/api/types/display.rs
@@ -58,6 +58,11 @@ pub(crate) async fn display_v2(
     let object_id = display_registry::display_object_id(type_.into())
         .context("Failed to derive Display V2 object ID")?;

+    // Display registry objects are global objects, not children of the value being rendered.
+    // Ignore any root-version bound inherited from the value so a newer Display v2 object can
+    // still be resolved for older objects.
+    let scope = scope.without_root_bound();
+
     let Some(object) = Object::latest(ctx, scope, object_id.into()).await? else {
         return Ok(None);
     };
PATCH

# Verify the patch was applied
grep -q "without_root_bound" crates/sui-indexer-alt-graphql/src/api/types/display.rs && echo "Patch applied successfully"
