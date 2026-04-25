#!/bin/bash
set -e
cd /workspace/mantine_repo

# Gold patch for mantinedev/mantine#8777
cat <<'PATCH' | git apply -
diff --git a/packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts b/packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts
--- a/packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts
+++ b/packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts
@@ -6,6 +6,6 @@ interface GetHeatColorInput {

 export function getHeatColor({ value, min, max, colors }: GetHeatColorInput) {
-  const percent = (value - min) / (max - min);
+  const percent = max === min ? 1 : (value - min) / (max - min);
   const colorIndex = Math.round((colors.length - 1) * percent);
   return colors[colorIndex];
 }
PATCH

# Verify the patch applied
grep -q "max === min ? 1" packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts
