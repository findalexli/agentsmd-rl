#!/bin/bash
set -euo pipefail

cd /workspace/remix

# Idempotency check
if grep -q 'context.router = router' packages/fetch-router/src/lib/router.ts; then
  echo "Patch already applied, exiting."
  exit 0
fi

git apply <<'PATCH'
diff --git a/demos/bookstore/app/router.ts b/demos/bookstore/app/router.ts
index 9b4851f91c9..d3899b1631e 100644
--- a/demos/bookstore/app/router.ts
+++ b/demos/bookstore/app/router.ts
@@ -22,7 +22,6 @@ import checkoutController from './checkout.tsx'
 import * as marketingController from './marketing.tsx'
 import { uploadsAction } from './uploads.tsx'
 import fragmentsController from './fragments.tsx'
-import { routerStorageKey } from './utils/router-storage.ts'
 import { loadDatabase } from './middleware/database.ts'

 let middleware = []
@@ -49,12 +48,6 @@ await initializeBookstoreDatabase()

 export let router = createRouter({ middleware })

-// Make router available to render() for internal frame resolution (no network).
-middleware.unshift((context: any, next: any) => {
-  context.storage.set(routerStorageKey, router)
-  return next()
-})
-
 router.get(routes.uploads, uploadsAction)
 router.map(routes.fragments, fragmentsController)
 router.post(routes.api.cartToggle, toggleCart)
diff --git a/demos/bookstore/app/utils/render.ts b/demos/bookstore/app/utils/render.ts
index a74a7b64308..abf96d7a796 100644
--- a/demos/bookstore/app/utils/render.ts
+++ b/demos/bookstore/app/utils/render.ts
@@ -3,12 +3,10 @@ import { renderToStream } from 'remix/component/server'
 import { getContext } from 'remix/async-context-middleware'
 import type { Router } from 'remix/fetch-router'

-import { routerStorageKey } from './router-storage.ts'
-
 export function render(node: RemixNode, init?: ResponseInit) {
   let context = getContext()
   let request = context.request
-  let router = context.storage.get(routerStorageKey)
+  let router = context.router

   let stream = renderToStream(node, {
     resolveFrame: (src) => resolveFrame(router, request, src),
diff --git a/demos/bookstore/app/utils/router-storage.ts b/demos/bookstore/app/utils/router-storage.ts
deleted file mode 100644
index dc097be71be..00000000000
--- a/demos/bookstore/app/utils/router-storage.ts
+++ /dev/null
@@ -1,4 +0,0 @@
-import { createStorageKey } from 'remix/fetch-router'
-import type { Router } from 'remix/fetch-router'
-
-export let routerStorageKey = createStorageKey<Router>()
diff --git a/packages/fetch-router/.changes/minor.router-on-context.md b/packages/fetch-router/.changes/minor.router-on-context.md
new file mode 100644
index 00000000000..931b222c59d
--- /dev/null
+++ b/packages/fetch-router/.changes/minor.router-on-context.md
@@ -0,0 +1,3 @@
+Expose `context.router` on request context
+
+Each router request context now gets the owning `Router` assigned as `context.router` by `createRouter()` when `fetch()` is called. This lets framework helpers read router state directly from `RequestContext` instead of requiring app-level middleware to store the router in `context.storage`.
diff --git a/packages/fetch-router/src/lib/request-context.ts b/packages/fetch-router/src/lib/request-context.ts
index 6111f5a501f..ad88566ef8f 100644
--- a/packages/fetch-router/src/lib/request-context.ts
+++ b/packages/fetch-router/src/lib/request-context.ts
@@ -1,4 +1,5 @@
 import { createSession, type Session } from '@remix-run/session'
+import type { Router } from './router.ts'

 import { AppStorage } from './app-storage.ts'
 import {
@@ -118,6 +119,23 @@ export class RequestContext<

   #session?: Session

+  #router?: Router
+
+  /**
+   * The router handling this request.
+   */
+  get router(): Router {
+    if (this.#router == null) {
+      throw new Error('No router found in request context.')
+    }
+
+    return this.#router
+  }
+
+  set router(router: Router) {
+    this.#router = router
+  }
+
   /**
    * Whether the session has been started.
    */
diff --git a/packages/fetch-router/src/lib/router.ts b/packages/fetch-router/src/lib/router.ts
index 480425b6d92..0c560c083cc 100644
--- a/packages/fetch-router/src/lib/router.ts
+++ b/packages/fetch-router/src/lib/router.ts
@@ -302,9 +302,10 @@ export function createRouter(options?: RouterOptions): Router {
     }
   }

-  return {
+  let router: Router = {
     fetch(input: string | URL | Request, init?: RequestInit): Promise<Response> {
       let context = createRequestContext(input, init)
+      context.router = router

       if (globalMiddleware) {
         return runMiddleware(globalMiddleware, context, dispatch)
@@ -353,8 +354,10 @@ export function createRouter(options?: RouterOptions): Router {
     options<pattern extends string>(
       route: pattern | RoutePattern<pattern> | Route<'OPTIONS' | 'ANY', pattern>,
       action: Action<'OPTIONS', pattern>,
-    ): void {
-      addRoute('OPTIONS', route, action)
-    },
+      ): void {
+        addRoute('OPTIONS', route, action)
+      },
   }
+
+  return router
 }
PATCH

echo "Patch applied successfully."
