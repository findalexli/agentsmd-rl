#!/bin/bash
set -e

cd /workspace/mantine

# Apply the fix for ScrollArea overscroll-behavior issue
cat <<'PATCH' | git apply -
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

# Verify the patch was applied by checking for the distinctive line
grep -q "overrideOverscrollBehavior = \`\${overscrollBehavior} auto\`" packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx
echo "Patch applied successfully"
