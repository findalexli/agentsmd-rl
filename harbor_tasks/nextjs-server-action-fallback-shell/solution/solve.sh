#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Check if already applied
if grep -q 'isPossibleServerAction' packages/next/src/build/templates/app-page.ts 2>/dev/null | grep -q 'staticPathKey' 2>/dev/null; then
    # More precise check: is isPossibleServerAction referenced near staticPathKey assignment?
    if awk '/let staticPathKey/,/staticPathKey = resolvedPathname/' packages/next/src/build/templates/app-page.ts | grep -q 'isPossibleServerAction'; then
        echo "Patch already applied"
        exit 0
    fi
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/build/templates/app-page.ts b/packages/next/src/build/templates/app-page.ts
index bafdc15973fe91..7cc442885bb29b 100644
--- a/packages/next/src/build/templates/app-page.ts
+++ b/packages/next/src/build/templates/app-page.ts
@@ -621,7 +621,14 @@ export async function handler(
   if (
     !staticPathKey &&
     (routeModule.isDev ||
-      (isSSG && pageIsDynamic && prerenderInfo?.fallbackRouteParams))
+      (isSSG &&
+        pageIsDynamic &&
+        prerenderInfo?.fallbackRouteParams &&
+        // Server action requests must not get a staticPathKey, otherwise they
+        // enter the fallback rendering block below and return the cached HTML
+        // shell with the action result appended, instead of responding with
+        // just the RSC action result.
+        !isPossibleServerAction))
   ) {
     staticPathKey = resolvedPathname
   }

PATCH

echo "Patch applied successfully"
