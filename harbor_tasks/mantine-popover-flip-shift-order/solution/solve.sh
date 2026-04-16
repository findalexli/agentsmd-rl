#!/bin/bash
set -e

REPO="/workspace/mantine"
cd "$REPO"

# Check if already patched
if grep -q "middlewaresOptions.flip" packages/@mantine/core/src/components/Popover/use-popover.ts | grep -q "middlewaresOptions.shift"; then
    echo "Patch may already be applied, checking..."
    # More specific check: if flip block appears BEFORE shift block
    FLIP_LINE=$(grep -n "if (middlewaresOptions.flip)" packages/@mantine/core/src/components/Popover/use-popover.ts | head -1 | cut -d: -f1)
    SHIFT_LINE=$(grep -n "if (middlewaresOptions.shift)" packages/@mantine/core/src/components/Popover/use-popover.ts | head -1 | cut -d: -f1)

    if [ -n "$FLIP_LINE" ] && [ -n "$SHIFT_LINE" ] && [ "$FLIP_LINE" -lt "$SHIFT_LINE" ]; then
        echo "Patch already applied (flip comes before shift)"
        exit 0
    fi
fi

# Apply the patch to reorder middlewares: flip before shift
cat <<'PATCH' | patch -p1
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

echo "Patch applied successfully!"
