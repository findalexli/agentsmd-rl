#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: if patch already applied, skip
if ! grep -q "globalThis as any).createFileRoute" packages/react-router/src/router.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/react-router/src/router.ts b/packages/react-router/src/router.ts
index 2033bd1330b..178eace31bd 100644
--- a/packages/react-router/src/router.ts
+++ b/packages/react-router/src/router.ts
@@ -1,5 +1,4 @@
 import { RouterCore } from '@tanstack/router-core'
-import { createFileRoute, createLazyFileRoute } from './fileRoute'
 import { getStoreFactory } from './routerStores'
 import type { RouterHistory } from '@tanstack/history'
 import type {
@@ -118,11 +117,3 @@ export class Router<
     super(options, getStoreFactory)
   }
 }
-
-if (typeof globalThis !== 'undefined') {
-  ;(globalThis as any).createFileRoute = createFileRoute
-  ;(globalThis as any).createLazyFileRoute = createLazyFileRoute
-} else if (typeof window !== 'undefined') {
-  ;(window as any).createFileRoute = createFileRoute
-  ;(window as any).createLazyFileRoute = createLazyFileRoute
-}
diff --git a/packages/solid-router/src/router.ts b/packages/solid-router/src/router.ts
index 3b4928c0cd2..3fce7c9d75c 100644
--- a/packages/solid-router/src/router.ts
+++ b/packages/solid-router/src/router.ts
@@ -1,5 +1,4 @@
 import { RouterCore } from '@tanstack/router-core'
-import { createFileRoute, createLazyFileRoute } from './fileRoute'
 import { getStoreFactory } from './routerStores'
 import type { RouterHistory } from '@tanstack/history'
 import type {
@@ -103,11 +102,3 @@ export class Router<
     super(options, getStoreFactory)
   }
 }
-
-if (typeof globalThis !== 'undefined') {
-  ;(globalThis as any).createFileRoute = createFileRoute
-  ;(globalThis as any).createLazyFileRoute = createLazyFileRoute
-} else if (typeof window !== 'undefined') {
-  ;(window as any).createFileRoute = createFileRoute
-  ;(window as any).createLazyFileRoute = createLazyFileRoute
-}
PATCH

# Rebuild the affected packages after patch
pnpm nx run @tanstack/react-router:build --skipRemoteCache
pnpm nx run @tanstack/solid-router:build --skipRemoteCache

echo "Patch applied and packages rebuilt successfully."
