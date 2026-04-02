#!/usr/bin/env bash
set -euo pipefail

# Gold patch for react-devtools-resizeobserver-overflow
# PR: facebook/react#35694

HOOKS_FILE="packages/react-devtools-shared/src/devtools/views/hooks.js"

# Check if already applied (look for ResizeObserver usage)
if grep -q "ResizeObserver" "$HOOKS_FILE" 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/views/hooks.js b/packages/react-devtools-shared/src/devtools/views/hooks.js
index 2984c2fbfcda..c5e426e7a622 100644
--- a/packages/react-devtools-shared/src/devtools/views/hooks.js
+++ b/packages/react-devtools-shared/src/devtools/views/hooks.js
@@ -112,30 +112,38 @@ export function useEditableValue(
 }

 export function useIsOverflowing(
-  containerRef: {current: HTMLDivElement | null, ...},
+  containerRef: {current: HTMLDivElement | null},
   totalChildWidth: number,
 ): boolean {
   const [isOverflowing, setIsOverflowing] = useState<boolean>(false);

   // It's important to use a layout effect, so that we avoid showing a flash of overflowed content.
   useLayoutEffect(() => {
-    if (containerRef.current === null) {
-      return () => {};
+    const container = containerRef.current;
+    if (container === null) {
+      return;
     }

-    const container = ((containerRef.current: any): HTMLDivElement);
-
-    const handleResize = () =>
-      setIsOverflowing(container.clientWidth <= totalChildWidth);
+    // ResizeObserver on the global did not fire for the extension.
+    // We need to grab the ResizeObserver from the container's window.
+    const ResizeObserver = container.ownerDocument.defaultView.ResizeObserver;
+    const observer = new ResizeObserver(entries => {
+      const entry = entries[0];
+      const contentWidth = entry.contentRect.width;
+      setIsOverflowing(
+        contentWidth <=
+          // We need to treat the box as overflowing when you're just
+          // about to overflow.
+          // Otherwise you won't be able to resize panes with custom resize handles.
+          // Previously we were relying on clientWidth which is already rounded.
+          // We don't want to read that again since that would trigger another layout.
+          totalChildWidth + 1,
+      );
+    });

-    handleResize();
+    observer.observe(container);

-    // It's important to listen to the ownerDocument.defaultView to support the browser extension.
-    // Here we use portals to render individual tabs (e.g. Profiler),
-    // and the root document might belong to a different window.
-    const ownerWindow = container.ownerDocument.defaultView;
-    ownerWindow.addEventListener('resize', handleResize);
-    return () => ownerWindow.removeEventListener('resize', handleResize);
+    return observer.disconnect.bind(observer);
   }, [containerRef, totalChildWidth]);

   return isOverflowing;
PATCH

echo "Patch applied successfully"
