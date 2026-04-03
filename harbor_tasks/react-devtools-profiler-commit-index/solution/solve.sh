#!/bin/bash
set -euo pipefail

# Check if fix is already applied
FILE="packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js"

if grep -q "Reset commit index when commitData changes" "$FILE"; then
    echo "Fix already applied"
    exit 0
fi

echo "Applying profiler commit index fix..."

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js b/packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js
index e309e6a3cf39..d3369b4f9538 100644
--- a/packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js
+++ b/packages/react-devtools-shared/src/devtools/views/Profiler/useCommitFilteringAndNavigation.js
@@ -45,6 +45,14 @@ export function useCommitFilteringAndNavigation(
     null,
   );

+  // Reset commit index when commitData changes (e.g., when switching roots).
+  const [previousCommitData, setPreviousCommitData] =
+    useState<Array<CommitDataFrontend>>(commitData);
+  if (previousCommitData !== commitData) {
+    setPreviousCommitData(commitData);
+    selectCommitIndex(commitData.length > 0 ? 0 : null);
+  }
+
   const calculateFilteredIndices = useCallback(
     (enabled: boolean, minDuration: number): Array<number> => {
       return commitData.reduce((reduced: Array<number>, commitDatum, index) => {
PATCH

echo "Fix applied successfully"
