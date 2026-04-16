#!/bin/bash
set -e

cd /workspace/electric

# Apply the gold patch for fixing handle -next suffix accumulation on repeated 409s
patch -p1 << 'PATCH'
diff --git a/packages/typescript-client/src/client.ts b/packages/typescript-client/src/client.ts
index edb1991b3a..29675a692b 100644
--- a/packages/typescript-client/src/client.ts
+++ b/packages/typescript-client/src/client.ts
@@ -96,6 +96,10 @@ const RESERVED_PARAMS: Set<ReservedParamKeys> = new Set([

 const TROUBLESHOOTING_URL = `https://electric-sql.com/docs/guides/troubleshooting`

+function createCacheBuster(): string {
+  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
+}
+
 type Replica = `full` | `default`
 export type LogMode = `changes_only` | `full`

@@ -617,6 +621,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
   #fastLoopBackoffMaxMs = 5_000
   #fastLoopConsecutiveCount = 0
   #fastLoopMaxCount = 5
+  #refetchCacheBuster?: string

   constructor(options: ShapeStreamOptions<GetExtensions<T>>) {
     this.options = { subscribe: true, ...options }
@@ -875,10 +880,10 @@ export class ShapeStream<T extends Row<unknown> = Row>
       if (!(e instanceof FetchError)) throw e // should never happen

       if (e.status == 409) {
-        // Upon receiving a 409, we should start from scratch
-        // with the newly provided shape handle, or a fallback
-        // pseudo-handle based on the current one to act as a
-        // consistent cache buster
+        // Upon receiving a 409, start from scratch with the newly
+        // provided shape handle. If the header is missing (e.g. proxy
+        // stripped it), reset without a handle and use a random
+        // cache-buster query param to ensure the retry URL is unique.

         // Store the current shape URL as expired to avoid future 409s
         if (this.#syncState.handle) {
@@ -886,8 +891,14 @@ export class ShapeStream<T extends Row<unknown> = Row>
           expiredShapesCache.markExpired(shapeKey, this.#syncState.handle)
         }

-        const newShapeHandle =
-          e.headers[SHAPE_HANDLE_HEADER] || `${this.#syncState.handle!}-next`
+        const newShapeHandle = e.headers[SHAPE_HANDLE_HEADER]
+        if (!newShapeHandle) {
+          console.warn(
+            `[Electric] Received 409 response without a shape handle header. ` +
+              `This likely indicates a proxy or CDN stripping required headers.`
+          )
+          this.#refetchCacheBuster = createCacheBuster()
+        }
         this.#reset(newShapeHandle)

         // must refetch control message might be in a list or not depending
@@ -1144,6 +1155,16 @@ export class ShapeStream<T extends Row<unknown> = Row>
       fetchUrl.searchParams.set(EXPIRED_HANDLE_QUERY_PARAM, expiredHandle)
     }

+    // Add one-shot cache buster when a 409 response lacked a handle header
+    // (e.g. proxy stripped it). Ensures each retry has a unique URL.
+    if (this.#refetchCacheBuster) {
+      fetchUrl.searchParams.set(
+        CACHE_BUSTER_QUERY_PARAM,
+        this.#refetchCacheBuster
+      )
+      this.#refetchCacheBuster = undefined
+    }
+
     // sort query params in-place for stable URLs and improved cache hits
     fetchUrl.searchParams.sort()

@@ -1199,8 +1220,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
       expiredHandle,
       now: Date.now(),
       maxStaleCacheRetries: this.#maxStaleCacheRetries,
-      createCacheBuster: () =>
-        `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
+      createCacheBuster,
     })

     this.#syncState = transition.state
@@ -1786,8 +1806,7 @@ export class ShapeStream<T extends Row<unknown> = Row>
           expiredHandle: null,
           now: Date.now(),
           maxStaleCacheRetries: this.#maxStaleCacheRetries,
-          createCacheBuster: () =>
-            `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
+          createCacheBuster,
         })
         if (transition.action === `accepted`) {
           this.#syncState = transition.state
@@ -1869,9 +1888,16 @@ export class ShapeStream<T extends Row<unknown> = Row>

         // For snapshot 409s, only update the handle — don't reset offset/schema/etc.
         // The main stream is paused and should not be disturbed.
-        const nextHandle =
-          e.headers[SHAPE_HANDLE_HEADER] || `${usedHandle ?? `handle`}-next`
-        this.#syncState = this.#syncState.withHandle(nextHandle)
+        const nextHandle = e.headers[SHAPE_HANDLE_HEADER]
+        if (nextHandle) {
+          this.#syncState = this.#syncState.withHandle(nextHandle)
+        } else {
+          console.warn(
+            `[Electric] Received 409 response without a shape handle header. ` +
+              `This likely indicates a proxy or CDN stripping required headers.`
+          )
+          this.#refetchCacheBuster = createCacheBuster()
+        }

         return this.fetchSnapshot(opts)
       }
PATCH

echo "Patch applied successfully"
