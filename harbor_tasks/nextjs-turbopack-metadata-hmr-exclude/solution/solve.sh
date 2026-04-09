#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'isMetadataRoute(entryPage)' packages/next/src/server/dev/hot-reloader-turbopack.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/dev/hot-reloader-turbopack.ts b/packages/next/src/server/dev/hot-reloader-turbopack.ts
index a3194c5e880c9..271d8ab51696b 100644
--- a/packages/next/src/server/dev/hot-reloader-turbopack.ts
+++ b/packages/next/src/server/dev/hot-reloader-turbopack.ts
@@ -82,7 +82,10 @@ import { isAppPageRouteDefinition } from '../route-definitions/app-page-route-de
 import { normalizeAppPath } from '../../shared/lib/router/utils/app-paths'
 import type { ModernSourceMapPayload } from '../lib/source-maps'
 import { isDeferredEntry } from '../../build/entries'
-import { isMetadataRouteFile } from '../../lib/metadata/is-metadata-route'
+import {
+  isMetadataRoute,
+  isMetadataRouteFile,
+} from '../../lib/metadata/is-metadata-route'
 import { setBundlerFindSourceMapImplementation } from '../patch-error-inspect'
 import { getNextErrorFeedbackMiddleware } from '../../next-devtools/server/get-next-error-feedback-middleware'
 import {
@@ -602,16 +605,20 @@ export async function createHotReloaderTurbopack(
       join(distDir, p)
     )

-    const { type: entryType } = splitEntryKey(key)
+    const { type: entryType, page: entryPage } = splitEntryKey(key)

-    // Server HMR applies to all App Router entries built with the Turbopack
-    // Node.js runtime: both app pages and route handlers. Edge routes,
-    // Pages Router pages, and middleware/instrumentation do not use the
-    // Turbopack Node.js dev runtime and are excluded.
+    // Server HMR applies to App Router entries built with the Turbopack Node.js
+    // runtime: app pages and regular route handlers. Edge routes, Pages Router
+    // pages, middleware/instrumentation, and metadata routes (manifest.ts,
+    // robots.ts, sitemap.ts, icon.tsx, etc.) are excluded. Metadata routes are
+    // excluded because they serve HTTP responses directly and must re-execute
+    // on every request to pick up file changes; the in-place module update
+    // model of Server HMR does not apply to them.
     const usesServerHmr =
       serverFastRefresh &&
       entryType === 'app' &&
-      writtenEndpoint.type !== 'edge'
+      writtenEndpoint.type !== 'edge' &&
+      !isMetadataRoute(entryPage)

     const filesToDelete: string[] = []
     for (const file of serverPaths) {

PATCH

echo "Patch applied successfully."
