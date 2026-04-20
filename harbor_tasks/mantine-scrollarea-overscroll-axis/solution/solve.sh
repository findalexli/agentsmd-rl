#!/bin/bash
set -euo pipefail

cd /workspace/mantine

# Check if patch is already applied (idempotency)
if grep -q "overrideOverscrollBehavior" packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx b/packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx
index fd3ce5d5bcf..28d9f1a8594 100644
--- a/packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx
+++ b/packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx
@@ -105,12 +105,24 @@ const defaultProps = {
 } satisfies Partial<ScrollAreaProps>;

 const varsResolver = createVarsResolver<ScrollAreaFactory>(
-  (_, { scrollbarSize, overscrollBehavior }) => ({
-    root: {
-      '--scrollarea-scrollbar-size': rem(scrollbarSize),
-      '--scrollarea-over-scroll-behavior': overscrollBehavior,
-    },
-  })
+  (_, { scrollbarSize, overscrollBehavior, scrollbars }) => {
+    let overrideOverscrollBehavior = overscrollBehavior;
+
+    if (overscrollBehavior && scrollbars) {
+      if (scrollbars === 'x') {
+        overrideOverscrollBehavior = `${overscrollBehavior} auto`;
+      } else if (scrollbars === 'y') {
+        overrideOverscrollBehavior = `auto ${overscrollBehavior}`;
+      }
+    }
+
+    return {
+      root: {
+        '--scrollarea-scrollbar-size': rem(scrollbarSize),
+        '--scrollarea-over-scroll-behavior': overrideOverscrollBehavior,
+      },
+    };
+  }
 );

 export const ScrollArea = factory<ScrollAreaFactory>((_props, ref) => {
PATCH

echo "Patch applied successfully."
