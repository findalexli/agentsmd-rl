#!/bin/bash
set -e

cd /workspace/superset

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/superset-frontend/src/explore/components/ExploreChartPanel/index.tsx b/superset-frontend/src/explore/components/ExploreChartPanel/index.tsx
index 82aee5bdcb58..d7393a0f99e5 100644
--- a/superset-frontend/src/explore/components/ExploreChartPanel/index.tsx
+++ b/superset-frontend/src/explore/components/ExploreChartPanel/index.tsx
@@ -204,7 +204,6 @@ const ExploreChartPanel = ({

   const {
     ref: chartPanelRef,
-    observerRef: resizeObserverRef,
     width: chartPanelWidth,
     height: chartPanelHeight,
   } = useResizeDetectorByObserver();
@@ -378,7 +377,6 @@ const ExploreChartPanel = ({
           flex-direction: column;
           padding-top: ${theme.sizeUnit * 2}px;
         `}
-        ref={resizeObserverRef}
       >
         {vizTypeNeedsDataset && (
           <Alert
@@ -481,7 +479,6 @@ const ExploreChartPanel = ({
       </div>
     ),
     [
-      resizeObserverRef,
       showAlertBanner,
       errorMessage,
       onQuery,
@@ -533,7 +530,7 @@ const ExploreChartPanel = ({
       document.body.className += ` ${standaloneClass}`;
     }
     return (
-      <div id="app" data-test="standalone-app" ref={resizeObserverRef}>
+      <div id="app" data-test="standalone-app">
         {standaloneChartBody}
       </div>
     );
diff --git a/superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts b/superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts
index 04ae6c1a2f49..908fec4c4dc9 100644
--- a/superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts
+++ b/superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts
@@ -31,15 +31,16 @@ export default function useResizeDetectorByObserver() {
       setChartPanelSize({ width, height });
     }
   }, []);
-  const { ref: observerRef } = useResizeDetector({
+  // Use targetRef to observe the same element we measure
+  useResizeDetector({
     refreshMode: 'debounce',
     refreshRate: 300,
     onResize,
+    targetRef: ref,
   });

   return {
     ref,
-    observerRef,
     width,
     height,
   };
PATCH

echo "Patch applied successfully"

# Verify the patch was applied
grep -q "targetRef: ref," superset-frontend/src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts && echo "Fix verified: targetRef is used"
