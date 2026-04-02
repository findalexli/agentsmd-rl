#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if normalizeEncodedDynamicPlaceholder already exists, skip
if grep -q 'normalizeEncodedDynamicPlaceholder' packages/next/src/shared/lib/router/routes/app.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/shared/lib/router/routes/app.ts b/packages/next/src/shared/lib/router/routes/app.ts
index 0112713fa0fed9..fba29a29041b8a 100644
--- a/packages/next/src/shared/lib/router/routes/app.ts
+++ b/packages/next/src/shared/lib/router/routes/app.ts
@@ -60,6 +60,19 @@ export type NormalizedAppRouteSegment =
   | StaticAppRouteSegment
   | DynamicAppRouteSegment

+function normalizeEncodedDynamicPlaceholder(segment: string): string {
+  if (!/%5b|%5d/i.test(segment)) {
+    return segment
+  }
+
+  try {
+    const decodedSegment = decodeURIComponent(segment)
+    return getSegmentParam(decodedSegment) ? decodedSegment : segment
+  } catch {
+    return segment
+  }
+}
+
 export function parseAppRouteSegment(segment: string): AppRouteSegment | null {
   if (segment === '') {
     return null
@@ -180,8 +193,10 @@ export function parseAppRoute(
   let interceptedRoute: AppRoute | NormalizedAppRoute | undefined

   for (const segment of pathnameSegments) {
+    const normalizedSegment = normalizeEncodedDynamicPlaceholder(segment)
+
     // Parse the segment into an AppSegment.
-    const appSegment = parseAppRouteSegment(segment)
+    const appSegment = parseAppRouteSegment(normalizedSegment)
     if (!appSegment) {
       continue
     }

PATCH

echo "Patch applied successfully."
