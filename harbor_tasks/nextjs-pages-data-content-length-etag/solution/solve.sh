#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

TARGET="packages/next/src/server/route-modules/pages/pages-handler.ts"

# Idempotency check: if Buffer.from is already removed from the data response construction, skip
if ! grep -q 'Buffer\.from(JSON\.stringify(result\.value\.pageData))' "$TARGET" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/route-modules/pages/pages-handler.ts b/packages/next/src/server/route-modules/pages/pages-handler.ts
index 83af0ec60ef018..a0dd5016e24f84 100644
--- a/packages/next/src/server/route-modules/pages/pages-handler.ts
+++ b/packages/next/src/server/route-modules/pages/pages-handler.ts
@@ -502,16 +502,13 @@ export const getHandler = ({
             return {
               value: {
                 kind: CachedRouteKind.PAGES,
-                html: new RenderResult(
-                  Buffer.from(previousCacheEntry.value.html),
-                  {
-                    contentType: HTML_CONTENT_TYPE_HEADER,
-                    metadata: {
-                      statusCode: previousCacheEntry.value.status,
-                      headers: previousCacheEntry.value.headers,
-                    },
-                  }
-                ),
+                html: new RenderResult(previousCacheEntry.value.html, {
+                  contentType: HTML_CONTENT_TYPE_HEADER,
+                  metadata: {
+                    statusCode: previousCacheEntry.value.status,
+                    headers: previousCacheEntry.value.headers,
+                  },
+                }),
                 pageData: {},
                 status: previousCacheEntry.value.status,
                 headers: previousCacheEntry.value.headers,
@@ -710,13 +707,10 @@ export const getHandler = ({
           // anymore
           result:
             isNextDataRequest && !isErrorPage && !is500Page
-              ? new RenderResult(
-                  Buffer.from(JSON.stringify(result.value.pageData)),
-                  {
-                    contentType: JSON_CONTENT_TYPE_HEADER,
-                    metadata: result.value.html.metadata,
-                  }
-                )
+              ? new RenderResult(JSON.stringify(result.value.pageData), {
+                  contentType: JSON_CONTENT_TYPE_HEADER,
+                  metadata: result.value.html.metadata,
+                })
               : result.value.html,
           generateEtags: nextConfig.generateEtags,
           poweredByHeader: nextConfig.poweredByHeader,

PATCH

echo "Fix applied successfully."
