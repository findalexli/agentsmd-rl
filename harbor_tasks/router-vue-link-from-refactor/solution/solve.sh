#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/router-core/src/router.ts b/packages/router-core/src/router.ts
index 35ca8120b3d..05b76cd58d3 100644
--- a/packages/router-core/src/router.ts
+++ b/packages/router-core/src/router.ts
@@ -1703,7 +1703,7 @@ export class RouterCore<
     }

     // Determine params: reuse from state if possible, otherwise parse
-    const lastStateMatchId = this.stores.lastMatchId.state
+    const lastStateMatchId = last(this.stores.matchesId.state)
     const lastStateMatch =
       lastStateMatchId &&
       this.stores.activeMatchStoresById.get(lastStateMatchId)?.state
diff --git a/packages/router-core/src/stores.ts b/packages/router-core/src/stores.ts
index 3ba7644d6e7..c31bfb4ecbd 100644
--- a/packages/router-core/src/stores.ts
+++ b/packages/router-core/src/stores.ts
@@ -1,5 +1,5 @@
 import { createLRUCache } from './lru-cache'
-import { arraysEqual, last } from './utils'
+import { arraysEqual } from './utils'

 import type { AnyRoute } from './route'
 import type { RouterState } from './router'
@@ -88,8 +88,6 @@ export interface RouterStores<in out TRouteTree extends AnyRoute> {
   pendingMatchesSnapshot: ReadableStore<Array<AnyRouteMatch>>
   cachedMatchesSnapshot: ReadableStore<Array<AnyRouteMatch>>
   firstMatchId: ReadableStore<string | undefined>
-  /** could be react/vue only, the only use inside router-core/router could easily be removed */
-  lastMatchId: ReadableStore<string | undefined>
   hasPendingMatches: ReadableStore<boolean>
   matchRouteReactivity: ReadableStore<{
     locationHref: string
@@ -152,7 +150,6 @@ export function createRouterStores<TRouteTree extends AnyRoute>(
     readPoolMatches(cachedMatchStoresById, cachedMatchesId.state),
   )
   const firstMatchId = createReadonlyStore(() => matchesId.state[0])
-  const lastMatchId = createReadonlyStore(() => last(matchesId.state))
   const hasPendingMatches = createReadonlyStore(() =>
     matchesId.state.some((matchId) => {
       const store = activeMatchStoresById.get(matchId)
@@ -234,7 +231,6 @@ export function createRouterStores<TRouteTree extends AnyRoute>(
     pendingMatchesSnapshot,
     cachedMatchesSnapshot,
     firstMatchId,
-    lastMatchId,
     hasPendingMatches,
     matchRouteReactivity,

diff --git a/packages/vue-router/src/link.tsx b/packages/vue-router/src/link.tsx
index 0a197aac001..bb036b5a37c 100644
--- a/packages/vue-router/src/link.tsx
+++ b/packages/vue-router/src/link.tsx
@@ -168,8 +168,7 @@ export function useLinkProps<
   // During SSR we render exactly once and do not need reactivity.
   // Avoid store subscriptions, effects and observers on the server.
   if (isServer ?? router.isServer) {
-    const from = options.from ?? router.stores.lastMatchRouteFullPath.state
-    const next = router.buildLocation({ ...options, from } as any)
+    const next = router.buildLocation(options as any)
     const href = getHref({
       options: options as AnyLinkPropsOptions,
       router,
@@ -209,15 +208,6 @@ export function useLinkProps<
     ) as unknown as LinkHTMLAttributes
   }

-  const from = options.from
-    ? Vue.computed(() => options.from)
-    : useStore(router.stores.lastMatchRouteFullPath, (fullPath) => fullPath)
-
-  const _options = Vue.computed(() => ({
-    ...options,
-    from: from.value,
-  }))
-
   const currentLocation = useStore(router.stores.location, (l) => l, {
     equal: (prev, next) => prev.href === next.href,
   })
@@ -225,12 +215,12 @@ export function useLinkProps<
   const next = Vue.computed(() => {
     // Rebuild when inherited search/hash or the current route context changes.

-    const opts = { _fromLocation: currentLocation.value, ..._options.value }
+    const opts = { _fromLocation: currentLocation.value, ...options }
     return router.buildLocation(opts as any)
   })

   const preload = Vue.computed(() => {
-    if (_options.value.reloadDocument) {
+    if (options.reloadDocument) {
       return false
     }
     return options.preload ?? router.options.defaultPreload
@@ -251,7 +241,7 @@ export function useLinkProps<

   const doPreload = () =>
     router
-      .preloadRoute({ ..._options.value, _builtLocation: next.value } as any)
+      .preloadRoute({ ...options, _builtLocation: next.value } as any)
       .catch((err: any) => {
         console.warn(err)
         console.warn(preloadWarning)
@@ -299,7 +289,7 @@ export function useLinkProps<
       e.button === 0
     ) {
       // Don't prevent default or handle navigation if reloadDocument is true
-      if (_options.value.reloadDocument) {
+      if (options.reloadDocument) {
         return
       }

@@ -314,7 +304,7 @@ export function useLinkProps<

       // All is well? Navigate!
       router.navigate({
-        ..._options.value,
+        ...options,
         replace: options.replace,
         resetScroll: options.resetScroll,
         hashScrollIntoView: options.hashScrollIntoView,
diff --git a/packages/vue-router/src/routerStores.ts b/packages/vue-router/src/routerStores.ts
index b15a295ecee..129a910df60 100644
--- a/packages/vue-router/src/routerStores.ts
+++ b/packages/vue-router/src/routerStores.ts
@@ -9,7 +9,6 @@ import type { Readable } from '@tanstack/vue-store'
 declare module '@tanstack/router-core' {
   export interface RouterReadableStore<TValue> extends Readable<TValue> {}
   export interface RouterStores<in out TRouteTree extends AnyRoute> {
-    lastMatchRouteFullPath: RouterReadableStore<string | undefined>
     /** Maps each active routeId to the matchId of its child in the match tree. */
     childMatchIdByRouteId: RouterReadableStore<Record<string, string>>
     /** Maps each pending routeId to true for quick lookup. */
@@ -23,14 +22,6 @@ export const getStoreFactory: GetStoreConfig = (_opts) => {
     createReadonlyStore: createStore,
     batch,
     init: (stores: RouterStores<AnyRoute>) => {
-      stores.lastMatchRouteFullPath = createStore(() => {
-        const id = stores.lastMatchId.state
-        if (!id) {
-          return undefined
-        }
-        return stores.activeMatchStoresById.get(id)?.state.fullPath
-      })
-
       // Single derived store: one reactive node that maps every active
       // routeId to its child's matchId. Depends only on matchesId +
       // the pool's routeId tags (which are set during reconciliation)."
PATCH

# Idempotency check - verify the distinctive line from the patch
grep -q "last(this.stores.matchesId.state)" packages/router-core/src/router.ts && echo "Patch applied successfully" || exit 1
