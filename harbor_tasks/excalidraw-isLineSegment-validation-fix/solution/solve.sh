#!/bin/bash
set -e

cd /workspace/excalidraw

# Apply the gold patch for isLineSegment fix
cat <<'PATCH' | git apply -
--- a/packages/math/src/segment.ts
+++ b/packages/math/src/segment.ts
@@ -40,7 +40,7 @@ export const isLineSegment = <Point extends GlobalPoint | LocalPoint>(
   Array.isArray(segment) &&
   segment.length === 2 &&
   isPoint(segment[0]) &&
-  isPoint(segment[0]);
+  isPoint(segment[1]);

 /**
  * Return the coordinates resulting from rotating the given line about an origin by an angle in radians
PATCH

# Verify the patch was applied (distinctive line from patch)
grep -q "isPoint(segment\[1\])" packages/math/src/segment.ts || {
    echo "ERROR: Patch was not applied correctly"
    exit 1
}

echo "Gold patch applied successfully"
