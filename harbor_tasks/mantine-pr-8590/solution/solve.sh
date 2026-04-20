#!/bin/bash
set -e
cd /workspace/mantine

# Apply the gold patch
git apply <<'PATCH'
diff --git a/packages/@mantine/core/src/components/Popover/use-popover.ts b/packages/@mantine/core/src/components/Popover/use-popover.ts
index c04db29008..567fca8288 100644
--- a/packages/@mantine/core/src/components/Popover/use-popover.ts
+++ b/packages/@mantine/core/src/components/Popover/use-popover.ts
@@ -71,6 +71,12 @@ function getPopoverMiddlewares(
     middlewaresOptions.flip = false;
   }

+  if (middlewaresOptions.flip) {
+    middlewares.push(
+      typeof middlewaresOptions.flip === 'boolean' ? flip() : flip(middlewaresOptions.flip)
+    );
+  }
+
   if (middlewaresOptions.shift) {
     middlewares.push(
       shift(
@@ -81,12 +87,6 @@ function getPopoverMiddlewares(
     );
   }

-  if (middlewaresOptions.flip) {
-    middlewares.push(
-      typeof middlewaresOptions.flip === 'boolean' ? flip() : flip(middlewaresOptions.flip)
-    );
-  }
-
   if (middlewaresOptions.inline) {
     middlewares.push(
       typeof middlewaresOptions.inline === 'boolean' ? inline() : inline(middlewaresOptions.inline)
PATCH

# Verify the patch was applied (idempotency check)
grep -q "typeof middlewaresOptions.flip === 'boolean' ? flip() : flip(middlewaresOptions.flip)" packages/@mantine/core/src/components/Popover/use-popover.ts
