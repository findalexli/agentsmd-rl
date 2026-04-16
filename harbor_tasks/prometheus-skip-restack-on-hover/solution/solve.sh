#!/bin/bash
set -e

# Change to the repository directory
cd /workspace/prometheus

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts b/web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts
index 1234567..abcdefg 100644
--- a/web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts
+++ b/web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts
@@ -85,14 +85,16 @@ export function setStackedOpts(opts: uPlot.Options, data: uPlot.AlignedData) {
     },
   };

-  // restack on toggle
+  // restack on toggle (but not on focus/hover)
   opts.hooks = opts.hooks || {};
   opts.hooks.setSeries = opts.hooks.setSeries || [];
-  opts.hooks.setSeries.push((u, _i) => {
-    const stacked = stack(data, (i) => !u.series[i].show);
-    u.delBand(null);
-    stacked.bands.forEach((b) => u.addBand(b));
-    u.setData(stacked.data);
+  opts.hooks.setSeries.push((u, _i, opts) => {
+    if (opts.show != null) {
+      const stacked = stack(data, (i) => !u.series[i].show);
+      u.delBand(null);
+      stacked.bands.forEach((b) => u.addBand(b));
+      u.setData(stacked.data);
+    }
   });

   return { opts, data: stacked.data };
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "restack on toggle (but not on focus/hover)" web/ui/mantine-ui/src/pages/query/uPlotStackHelpers.ts && echo "Patch applied successfully"
