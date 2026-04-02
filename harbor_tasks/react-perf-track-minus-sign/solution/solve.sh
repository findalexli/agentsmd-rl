#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
if grep -q "^const REMOVED = '-\\u00a0';" packages/shared/ReactPerformanceTrackProperties.js 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js b/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
index 703a69469c60..faaadb9cb617 100644
--- a/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
@@ -231,7 +231,7 @@ describe('ReactPerformanceTracks', () => {
               properties: [
                 ['Changed Props', ''],
                 ['  data', ''],
-                ['–   buffer', 'null'],
+                ['-   buffer', 'null'],
                 ['+   buffer', 'Uint8Array'],
                 ['+     0', '0'],
                 ['+     1', '0'],
@@ -422,7 +422,7 @@ describe('ReactPerformanceTracks', () => {
               color: 'error',
               properties: [
                 ['Changed Props', ''],
-                ['– value', '1'],
+                ['- value', '1'],
                 ['+ value', '2'],
               ],
               tooltipText: 'Left',
@@ -510,7 +510,7 @@ describe('ReactPerformanceTracks', () => {
                 ['  data', ''],
                 ['    deeply', ''],
                 ['      nested', ''],
-                ['–       numbers', 'Array'],
+                ['-       numbers', 'Array'],
                 ['+       numbers', 'Array'],
               ],
               tooltipText: 'App',
diff --git a/packages/shared/ReactPerformanceTrackProperties.js b/packages/shared/ReactPerformanceTrackProperties.js
index f088d51025b5..a2063584bdf0 100644
--- a/packages/shared/ReactPerformanceTrackProperties.js
+++ b/packages/shared/ReactPerformanceTrackProperties.js
@@ -279,7 +279,7 @@ export function addValueToProperties(
   properties.push([prefix + '\xa0\xa0'.repeat(indent) + propertyName, desc]);
 }

-const REMOVED = '\u2013\xa0';
+const REMOVED = '-\xa0';
 const ADDED = '+\xa0';
 const UNCHANGED = '\u2007\xa0';

PATCH

echo "Fix applied successfully"
