#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/router-core/src/router.ts b/packages/router-core/src/router.ts
index 965fefda339..301648a80e3 100644
--- a/packages/router-core/src/router.ts
+++ b/packages/router-core/src/router.ts
@@ -1279,7 +1279,7 @@ export class RouterCore<

         return {
           href: pathname + searchStr + hash,
-          publicHref: href,
+          publicHref: pathname + searchStr + hash,
           pathname: decodePath(pathname).path,
           external: false,
           searchStr,
PATCH

echo "Patch applied successfully"
