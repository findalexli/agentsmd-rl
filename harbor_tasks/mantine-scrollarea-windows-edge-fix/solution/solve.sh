#!/bin/bash
set -e

cd /workspace/mantine

# Idempotency check - look for distinctive line from the fix
if grep -q "Allow horizontal scrolling even when vertical scroll is at boundaries" packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx b/packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx
index abc123..def456 100644
--- a/packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx
+++ b/packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx
@@ -6,14 +6,32 @@ import { useScrollAreaContext } from '../ScrollArea.context';
 export interface ScrollAreaViewportProps extends BoxProps, ElementProps<'div'> {}

 export const ScrollAreaViewport = forwardRef<HTMLDivElement, ScrollAreaViewportProps>(
-  ({ children, style, ...others }, ref) => {
+  ({ children, style, onWheel, ...others }, ref) => {
     const ctx = useScrollAreaContext();
     const rootRef = useMergedRef(ref, ctx.onViewportChange);

+    const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
+      onWheel?.(event);
+
+      // Fix for Windows: Allow horizontal scrolling even when vertical scroll is at boundaries
+      // When at vertical boundaries, Windows tries to scroll the parent/page instead of allowing horizontal scroll
+      if (ctx.scrollbarXEnabled && ctx.viewport && event.shiftKey) {
+        const { scrollTop, scrollHeight, clientHeight, scrollWidth, clientWidth } = ctx.viewport;
+        const isAtTop = scrollTop < 1;
+        const isAtBottom = scrollTop >= scrollHeight - clientHeight - 1;
+        const canScrollHorizontally = scrollWidth > clientWidth;
+
+        if (canScrollHorizontally && (isAtTop || isAtBottom)) {
+          event.stopPropagation();
+        }
+      }
+    };
+
     return (
       <Box
         {...others}
         ref={rootRef}
+        onWheel={handleWheel}
         style={{
           overflowX: ctx.scrollbarXEnabled ? 'scroll' : 'hidden',
           overflowY: ctx.scrollbarYEnabled ? 'scroll' : 'hidden',
PATCH

echo "Patch applied successfully."
