#!/bin/bash
set -e

cd /workspace/superset

# Check if already patched (idempotency)
if grep -q "stackedTotalMax" superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat << 'PATCH' | git apply -
diff --git a/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts b/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
index 6966be78a3ef..114c374d659f 100644
--- a/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
+++ b/superset-frontend/plugins/plugin-chart-echarts/src/Timeseries/transformProps.ts
@@ -659,7 +659,10 @@ export default function transformProps(
     for (const s of series) {
       if (s.id) {
         const columnsArr = labelMap[s.id];
-        (s as any).stack = columnsArr[idxSelectedDimension];
+        const dimensionValue = columnsArr?.[idxSelectedDimension];
+        if (dimensionValue !== undefined) {
+          (s as any).stack = dimensionValue;
+        }
       }
     }
   }
@@ -682,9 +685,24 @@ export default function transformProps(

   // For horizontal bar charts, set max/min from calculated data bounds
   if (shouldCalculateDataBounds) {
-    // Set max to actual data max to avoid gaps and ensure labels are visible
-    if (dataMax !== undefined && yAxisMax === undefined) {
-      yAxisMax = dataMax;
+    // For stacked charts, clamp against the per-row stacked total to avoid
+    // clipping bars. Also keep dataMax so that mixed-sign stacks (where
+    // positive and negative values cancel in the algebraic row sum) cannot
+    // produce an axis max smaller than the largest individual positive segment.
+    const stackedTotalMax = Math.max(
+      ...sortedTotalValues.filter(
+        (v): v is number => typeof v === 'number' && !Number.isNaN(v),
+      ),
+    );
+    const effectiveDataMax = stack
+      ? Math.max(dataMax ?? Number.NEGATIVE_INFINITY, stackedTotalMax)
+      : dataMax;
+    if (
+      effectiveDataMax !== undefined &&
+      Number.isFinite(effectiveDataMax) &&
+      yAxisMax === undefined
+    ) {
+      yAxisMax = effectiveDataMax;
     }
     // Set min to actual data min for diverging bars
     if (dataMin !== undefined && yAxisMin === undefined && dataMin < 0) {
PATCH

echo "Patch applied successfully"
