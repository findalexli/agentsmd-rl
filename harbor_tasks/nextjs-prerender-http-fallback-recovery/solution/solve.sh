#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'findPrerenderHTTPErrorBoundaryTree' packages/next/src/server/app-render/app-render.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/next/src/server/app-render/app-render.tsx b/packages/next/src/server/app-render/app-render.tsx
index ac46b83128ecb0..6013e3539e4516 100644
--- a/packages/next/src/server/app-render/app-render.tsx
+++ b/packages/next/src/server/app-render/app-render.tsx
@@ -113,7 +113,11 @@ import {
   walkTreeWithFlightRouterState,
   createFullTreeFlightDataForNavigation,
 } from './walk-tree-with-flight-router-state'
-import { createComponentTree, getRootParams } from './create-component-tree'
+import {
+  createComponentTree,
+  getRootParams,
+  type PrerenderHTTPErrorState,
+} from './create-component-tree'
 import { getAssetQueryString } from './get-asset-query-string'
 import {
   getClientReferenceManifest,
@@ -506,6 +510,54 @@ function createNotFoundLoaderTree(loaderTree: LoaderTree): LoaderTree {
   ]
 }

+type HTTPAccessErrorStatusCode = 404 | 403 | 401
+
+function hasPrerenderHTTPErrorBoundary(
+  loaderTree: LoaderTree,
+  triggeredStatus: HTTPAccessErrorStatusCode,
+  authInterrupts: boolean
+): boolean {
+  switch (triggeredStatus) {
+    case 404:
+      return !!loaderTree[2]['not-found']
+    case 403:
+      return authInterrupts && !!loaderTree[2].forbidden
+    case 401:
+      return authInterrupts && !!loaderTree[2].unauthorized
+    default:
+      return false
+  }
+}
+
+function findPrerenderHTTPErrorBoundaryTree(
+  loaderTree: LoaderTree,
+  triggeredStatus: HTTPAccessErrorStatusCode,
+  authInterrupts: boolean
+): LoaderTree | null {
+  let boundaryTree: LoaderTree | null = hasPrerenderHTTPErrorBoundary(
+    loaderTree,
+    triggeredStatus,
+    authInterrupts
+  )
+    ? loaderTree
+    : null
+
+  const childrenTree = loaderTree[1].children
+  if (childrenTree) {
+    const deeperBoundaryTree = findPrerenderHTTPErrorBoundaryTree(
+      childrenTree,
+      triggeredStatus,
+      authInterrupts
+    )
+
+    if (deeperBoundaryTree) {
+      boundaryTree = deeperBoundaryTree
+    }
+  }
+
+  return boundaryTree
+}
+
 /**
  * Returns a function that parses the dynamic segment and return the associated value.
  */
@@ -1709,6 +1761,9 @@ async function getRSCPayload(
   ctx: AppRenderContext,
   options: {
     is404: boolean
+    // When set, rerender a segment-scoped HTTP fallback inside the normal app
+    // router tree instead of falling back to the generic error shell payload.
+    prerenderHTTPError?: PrerenderHTTPErrorState
     staleTimeIterable?: AsyncIterable<number>
     staticStageByteLengthPromise?: Promise<number>
     runtimePrefetchStream?: ReadableStream<Uint8Array>
@@ -1716,6 +1771,7 @@ async function getRSCPayload(
 ): Promise<InitialRSCPayload & { P: ReactNode }> {
   const {
     is404,
+    prerenderHTTPError,
     staleTimeIterable,
     staticStageByteLengthPromise,
     runtimePrefetchStream,
@@ -1789,6 +1845,7 @@ async function getRSCPayload(
     preloadCallbacks,
     authInterrupts: ctx.renderOpts.experimental.authInterrupts,
     MetadataOutlet,
+    prerenderHTTPError,
   })

   // When the `vary` response header is present with `Next-URL`, that means there's a chance
@@ -7117,16 +7174,46 @@ async function prerenderToStream(
           : INFINITE_CACHE,
       tags: [...(prerenderStore?.tags || implicitTags.tags)],
     })
-    const errorRSCPayload = await workUnitAsyncStorage.run(
-      prerenderLegacyStore,
-      getErrorRSCPayload,
-      tree,
-      ctx,
-      reactServerErrorsByDigest.has((err as any).digest) ? undefined : err,
-      errorType
-    )
+    let prerenderHTTPError: PrerenderHTTPErrorState | undefined
+    if (cacheComponents && isHTTPAccessFallbackError(err)) {
+      const triggeredStatus = getAccessFallbackHTTPStatus(
+        err
+      ) as HTTPAccessErrorStatusCode
+      const boundaryTree = findPrerenderHTTPErrorBoundaryTree(
+        tree,
+        triggeredStatus,
+        ctx.renderOpts.experimental.authInterrupts
+      )
+
+      if (boundaryTree) {
+        prerenderHTTPError = {
+          boundaryTree,
+          triggeredStatus,
+        }
+      }
+    }

-    const errorServerStream = workUnitAsyncStorage.run(
+    const errorRSCPayload = prerenderHTTPError
+      ? await workUnitAsyncStorage.run(
+          prerenderLegacyStore,
+          getRSCPayload,
+          tree,
+          ctx,
+          {
+            is404: errorType === 'not-found',
+            prerenderHTTPError,
+          }
+        )
+      : await workUnitAsyncStorage.run(
+          prerenderLegacyStore,
+          getErrorRSCPayload,
+          tree,
+          ctx,
+          reactServerErrorsByDigest.has((err as any).digest) ? undefined : err,
+          errorType
+        )
+
+    const errorServerStreamRaw = workUnitAsyncStorage.run(
       prerenderLegacyStore,
       renderToFlightStream,
       ComponentMod,
@@ -7138,6 +7225,19 @@ async function prerenderToStream(
       }
     )

+    let errorServerStream = errorServerStreamRaw
+    const errorFlightResultPromise = prerenderHTTPError
+      ? (() => {
+          // Fizz still needs to read the Flight stream to render ErrorApp, but
+          // the prerender path also needs a buffered Flight result for the HTML
+          // prelude and segment data collectors. Tee the stream so each consumer
+          // gets its own copy.
+          const [appStream, flightStream] = teeStream(errorServerStreamRaw)
+          errorServerStream = appStream
+          return createReactServerPrerenderResultFromRender(flightStream)
+        })()
+      : null
+
     try {
       const { stream: errorHtmlStream } = await workUnitAsyncStorage.run(
         prerenderLegacyStore,
@@ -7157,10 +7257,15 @@ async function prerenderToStream(
         }
       )

+      const resolvedFlightResult = errorFlightResultPromise
+        ? await errorFlightResultPromise
+        : reactServerPrerenderResult
+      if (errorFlightResultPromise) {
+        reactServerPrerenderResult.consume()
+      }
+
       if (shouldGenerateStaticFlightData(workStore)) {
-        const flightData = await streamToBuffer(
-          reactServerPrerenderResult.asStream()
-        )
+        const flightData = await streamToBuffer(resolvedFlightResult.asStream())
         metadata.flightData = flightData
         await collectSegmentData(
           flightData,
@@ -7172,9 +7277,7 @@ async function prerenderToStream(
         )
       }

-      // This is intentionally using the readable datastream from the main
-      // render rather than the flight data from the error page render
-      const flightStream = reactServerPrerenderResult.consumeAsStream()
+      const flightStream = resolvedFlightResult.consumeAsStream()

       return {
         digestErrorsMap: reactServerErrorsByDigest,
diff --git a/packages/next/src/server/app-render/create-component-tree.tsx b/packages/next/src/server/app-render/create-component-tree.tsx
index 3b9ff10615f46d..5d27d62eeded65 100644
--- a/packages/next/src/server/app-render/create-component-tree.tsx
+++ b/packages/next/src/server/app-render/create-component-tree.tsx
@@ -44,6 +44,13 @@ import {
 import type { AppSegmentConfig } from '../../build/segment-config/app/app-segment-config'
 import { RenderStage, type StagedRenderingController } from './staged-rendering'

+type HTTPAccessErrorStatusCode = 404 | 403 | 401
+
+export type PrerenderHTTPErrorState = {
+  boundaryTree: LoaderTree
+  triggeredStatus: HTTPAccessErrorStatusCode
+}
+
 /**
  * Use the provided loader tree to create the React Component tree.
  */
@@ -62,6 +69,7 @@ export function createComponentTree(props: {
   preloadCallbacks: PreloadCallbacks
   authInterrupts: boolean
   MetadataOutlet: ComponentType
+  prerenderHTTPError?: PrerenderHTTPErrorState
 }): Promise<CacheNodeSeedData> {
   return getTracer().trace(
     NextNodeServerSpan.createComponentTree,
@@ -99,6 +107,7 @@ async function createComponentTreeInternal(
     preloadCallbacks,
     authInterrupts,
     MetadataOutlet,
+    prerenderHTTPError,
   }: {
     loaderTree: LoaderTree
     parentParams: Params
@@ -113,6 +122,7 @@ async function createComponentTreeInternal(
     preloadCallbacks: PreloadCallbacks
     authInterrupts: boolean
     MetadataOutlet: ComponentType | null
+    prerenderHTTPError?: PrerenderHTTPErrorState
   },
   isRoot: boolean
 ): Promise<CacheNodeSeedData> {
@@ -595,28 +605,72 @@ async function createComponentTreeInternal(
             }
           }

-          const seedData = await createComponentTreeInternal(
-            {
-              loaderTree: parallelRoute,
-              parentParams: currentParams,
-              parentOptionalCatchAllParamName: optionalCatchAllParamName,
-              parentRuntimePrefetchable: isRuntimePrefetchable,
-              rootLayoutIncluded: rootLayoutIncludedAtThisLevelOrAbove,
-              injectedCSS: injectedCSSWithCurrentLayout,
-              injectedJS: injectedJSWithCurrentLayout,
-              injectedFontPreloadTags: injectedFontPreloadTagsWithCurrentLayout,
-              ctx,
-              missingSlots,
-              preloadCallbacks,
-              authInterrupts,
-              // `StreamingMetadataOutlet` is used to conditionally throw. In the case of parallel routes we will have more than one page
-              // but we only want to throw on the first one.
-              MetadataOutlet: isChildrenRouteKey ? MetadataOutlet : null,
-            },
-            false
-          )
+          // The outer prerender catch already found the deepest segment whose
+          // HTTP fallback should replace the throwing page. When we reach that
+          // segment's `children` slot, render the fallback directly instead of
+          // descending back into the subtree that threw during deserialization.
+
+          // Like the other segment-level boundary props below, HTTP access
+          // fallbacks are attached to the default `children` slot, not to named
+          // parallel routes.
+          const shouldRenderPrerenderHTTPFallback =
+            prerenderHTTPError?.boundaryTree === tree && isChildrenRouteKey
+
+          if (shouldRenderPrerenderHTTPFallback) {
+            let fallbackElement: React.ReactNode | undefined
+            switch (prerenderHTTPError.triggeredStatus) {
+              case 404:
+                fallbackElement = notFoundElement
+                break
+              case 403:
+                fallbackElement = forbiddenElement
+                break
+              case 401:
+                fallbackElement = unauthorizedElement
+                break
+              default:
+                break
+            }

-          childCacheNodeSeedData = seedData
+            if (fallbackElement) {
+              childCacheNodeSeedData = createSeedData(
+                ctx,
+                fallbackElement,
+                {},
+                null,
+                isPossiblyPartialResponse,
+                false,
+                emptyVaryParamsAccumulator
+              )
+            }
+          }
+
+          if (childCacheNodeSeedData === null) {
+            const seedData = await createComponentTreeInternal(
+              {
+                loaderTree: parallelRoute,
+                parentParams: currentParams,
+                parentOptionalCatchAllParamName: optionalCatchAllParamName,
+                parentRuntimePrefetchable: isRuntimePrefetchable,
+                rootLayoutIncluded: rootLayoutIncludedAtThisLevelOrAbove,
+                injectedCSS: injectedCSSWithCurrentLayout,
+                injectedJS: injectedJSWithCurrentLayout,
+                injectedFontPreloadTags:
+                  injectedFontPreloadTagsWithCurrentLayout,
+                ctx,
+                missingSlots,
+                preloadCallbacks,
+                authInterrupts,
+                // `StreamingMetadataOutlet` is used to conditionally throw. In the case of parallel routes we will have more than one page
+                // but we only want to throw on the first one.
+                MetadataOutlet: isChildrenRouteKey ? MetadataOutlet : null,
+                prerenderHTTPError,
+              },
+              false
+            )
+
+            childCacheNodeSeedData = seedData
+          }
         }

         const templateNode = createElement(

PATCH

echo "Patch applied successfully."
