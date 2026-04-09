#!/bin/bash
set -e

cd /workspace/router

# Check if already patched (idempotency)
if grep -q "Mark the current location as resolved so that later load cycles" packages/router-core/src/ssr/ssr-client.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
patch -p1 << 'PATCH'
diff --git a/packages/router-core/src/ssr/ssr-client.ts b/packages/router-core/src/ssr/ssr-client.ts
index b2ea33e92bf..678aa869a99 100644
--- a/packages/router-core/src/ssr/ssr-client.ts
+++ b/packages/router-core/src/ssr/ssr-client.ts
@@ -254,6 +254,11 @@ export async function hydrate(router: AnyRouter): Promise<any> {
       // remove the dehydrated flag since we won't run router.load() which would remove it
       match._nonReactive.dehydrated = undefined
     })
+    // Mark the current location as resolved so that later load cycles
+    // (e.g. preloads, invalidations) don't mistakenly detect a href change
+    // (resolvedLocation defaults to undefined and router.load() is skipped
+    // in the normal SSR hydration path).
+    router.stores.resolvedLocation.setState(() => router.stores.location.state)
     return routeChunkPromise
   }
PATCH

echo "Patch applied successfully"
