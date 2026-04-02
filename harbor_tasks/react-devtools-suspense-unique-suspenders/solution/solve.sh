#!/bin/bash
set -euo pipefail

# Gold patch for react-devtools-suspense-unique-suspenders
# Adds uniqueSuspenders field to Suspense tree snapshots in DevTools

# Check if already applied
if grep -q "hasUniqueSuspenders" packages/react-devtools-shared/src/devtools/utils.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/utils.js b/packages/react-devtools-shared/src/devtools/utils.js
index 640f0d19b579..b6438b47623c 100644
--- a/packages/react-devtools-shared/src/devtools/utils.js
+++ b/packages/react-devtools-shared/src/devtools/utils.js
@@ -64,9 +64,10 @@ function printRects(rects: SuspenseNode['rects']): string {

 function printSuspense(suspense: SuspenseNode): string {
   const name = ` name="${suspense.name || 'Unknown'}"`;
+  const hasUniqueSuspenders = ` uniqueSuspenders={${suspense.hasUniqueSuspenders ? 'true' : 'false'}}`;
   const printedRects = printRects(suspense.rects);

-  return `<Suspense${name}${printedRects}>`;
+  return `<Suspense${name}${hasUniqueSuspenders}${printedRects}>`;
 }

 function printSuspenseWithChildren(
PATCH

echo "Patch applied successfully"
