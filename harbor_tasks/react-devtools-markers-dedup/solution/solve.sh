#!/usr/bin/env bash
# Gold patch for react-devtools-markers-dedup
set -euo pipefail

REPO_DIR="${1:-/workspace/react}"
cd "$REPO_DIR"

# Check if already applied (look for the distinctive fix - checking inside the suspender removal block)
if grep -q "suspenseNode.hasUniqueSuspenders" packages/react-devtools-shared/src/backend/fiber/renderer.js | head -1 | grep -q "suspenseNode.retiredSuspenders"; then
    echo "Patch appears to already be applied."
    exit 0
fi

# Apply the fix: move unblockSuspendedBy inside the check that ensures the suspender was actually removed
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 916d69823285..905524d0dd1b 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -3197,15 +3197,16 @@ export function attach(
                 environmentCounts.set(env, count - 1);
               }
             }
-          }
-          if (
-            suspenseNode.hasUniqueSuspenders &&
-            !ioExistsInSuspenseAncestor(suspenseNode, ioInfo)
-          ) {
-            // This entry wasn't in any ancestor and is no longer in this suspense boundary.
-            // This means that a child might now be the unique suspender for this IO.
-            // Search the child boundaries to see if we can reveal any of them.
-            unblockSuspendedBy(suspenseNode, ioInfo);
+
+            if (
+              suspenseNode.hasUniqueSuspenders &&
+              !ioExistsInSuspenseAncestor(suspenseNode, ioInfo)
+            ) {
+              // This entry wasn't in any ancestor and is no longer in this suspense boundary.
+              // This means that a child might now be the unique suspender for this IO.
+              // Search the child boundaries to see if we can reveal any of them.
+              unblockSuspendedBy(suspenseNode, ioInfo);
+            }
           }
         }
       }
PATCH

echo "Patch applied successfully."
