#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if patch already applied
if ! grep -q "const shouldClearCache" packages/router-core/src/scroll-restoration.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
git apply --verbose <<'PATCH'
diff --git a/packages/router-core/src/scroll-restoration.ts b/packages/router-core/src/scroll-restoration.ts
index 6091a4560aa..828fc8e8686 100644
--- a/packages/router-core/src/scroll-restoration.ts
+++ b/packages/router-core/src/scroll-restoration.ts
@@ -258,24 +258,6 @@ export function setupScrollRestoration(router: AnyRouter, force?: boolean) {
       return
     }

-    const fromIndex = event.fromLocation?.state.__TSR_index
-    const toIndex = event.toLocation.state.__TSR_index
-    // Clear on forward navigations, and on same-entry replace navigations where
-    // the href changed. Preserve back/restore entries so they can be restored.
-    const shouldClearCache =
-      typeof fromIndex === 'number' && typeof toIndex === 'number'
-        ? toIndex > fromIndex ||
-          (toIndex === fromIndex &&
-            event.fromLocation?.href !== event.toLocation.href)
-        : true
-
-    if (shouldClearCache) {
-      cache.set((state) => {
-        delete state[cacheKey]
-        return state
-      })
-    }
-
     ignoreScroll = true

     try {
PATCH

echo "Patch applied successfully"

# Rebuild the router-core package after the fix
cd /workspace/router
pnpm nx run @tanstack/router-core:build --skip-nx-cache
