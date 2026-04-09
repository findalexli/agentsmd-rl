#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch to fix CSS asset deduplication
patch -p1 <<'PATCH'
diff --git a/packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts b/packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts
index 7df4b450105..c08ae4ce3f2 100644
--- a/packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts
+++ b/packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts
@@ -31,8 +31,9 @@ interface ManifestAssetResolvers {
   getStylesheetAsset: (cssFile: string) => RouterManagedTag
 }

-type DedupePreloadRoute = {
+type DedupeRoute = {
   preloads?: Array<ManifestAssetLink>
+  assets?: Array<RouterManagedTag>
   children?: Array<string>
 }

@@ -158,7 +159,7 @@ export function buildStartManifest(options: {
     assetResolvers,
   })

-  dedupeNestedRoutePreloads(routes[rootRouteId]!, routes)
+  dedupeNestedRouteManifestEntries(rootRouteId, routes[rootRouteId]!, routes)

   // Prune routes with no assets or preloads from the manifest
   for (const routeId of Object.keys(routes)) {
@@ -418,6 +419,20 @@ export function createChunkCssAssetCollector(options: {
   const assetsByChunk = new Map<Rollup.OutputChunk, Array<RouterManagedTag>>()
   const stateByChunk = new Map<Rollup.OutputChunk, number>()

+  const appendAsset = (
+    assets: Array<RouterManagedTag>,
+    seenAssets: Set<string>,
+    asset: RouterManagedTag,
+  ) => {
+    const identity = getAssetIdentity(asset)
+    if (seenAssets.has(identity)) {
+      return
+    }
+
+    seenAssets.add(identity)
+    assets.push(asset)
+  }
+
   const getChunkCssAssets = (
     chunk: Rollup.OutputChunk,
   ): Array<RouterManagedTag> => {
@@ -432,9 +447,10 @@ export function createChunkCssAssetCollector(options: {
     stateByChunk.set(chunk, VISITING_CHUNK)

     const assets: Array<RouterManagedTag> = []
+    const seenAssets = new Set<string>()

     for (const cssFile of chunk.viteMetadata?.importedCss ?? []) {
-      assets.push(options.getStylesheetAsset(cssFile))
+      appendAsset(assets, seenAssets, options.getStylesheetAsset(cssFile))
     }

     for (let i = 0; i < chunk.imports.length; i++) {
@@ -445,7 +461,7 @@ export function createChunkCssAssetCollector(options: {

       const importedAssets = getChunkCssAssets(importedChunk)
       for (let j = 0; j < importedAssets.length; j++) {
-        assets.push(importedAssets[j]!)
+        appendAsset(assets, seenAssets, importedAssets[j]!)
       }
     }

@@ -510,12 +526,15 @@ export function buildRouteManifestRoutes(options: {
   return routes
 }

-export function dedupeNestedRoutePreloads(
-  route: DedupePreloadRoute,
-  routesById: Record<string, DedupePreloadRoute>,
+function dedupeNestedRouteManifestEntries(
+  routeId: string,
+  route: DedupeRoute,
+  routesById: Record<string, DedupeRoute>,
   seenPreloads = new Set<string>(),
+  seenAssets = new Set<string>(),
 ) {
   let routePreloads = route.preloads
+  let routeAssets = route.assets

   if (routePreloads && routePreloads.length > 0) {
     let dedupedPreloads: Array<ManifestAssetLink> | undefined
@@ -544,12 +563,49 @@ export function dedupeNestedRoutePreloads(
     }
   }

+  if (routeAssets && routeAssets.length > 0) {
+    let dedupedAssets: Array<RouterManagedTag> | undefined
+
+    for (let i = 0; i < routeAssets.length; i++) {
+      const asset = routeAssets[i]!
+      const identity = getAssetIdentity(asset)
+
+      if (seenAssets.has(identity)) {
+        if (dedupedAssets === undefined) {
+          dedupedAssets = routeAssets.slice(0, i)
+        }
+        continue
+      }
+
+      seenAssets.add(identity)
+
+      if (dedupedAssets) {
+        dedupedAssets.push(asset)
+      }
+    }
+
+    if (dedupedAssets) {
+      routeAssets = dedupedAssets
+      route.assets = dedupedAssets
+    }
+  }
+
   if (route.children) {
     for (const childRouteId of route.children) {
-      dedupeNestedRoutePreloads(
-        routesById[childRouteId]!,
+      const childRoute = routesById[childRouteId]
+
+      if (!childRoute) {
+        throw new Error(
+          `Route tree references child route ${childRouteId} from ${routeId}, but no route entry was found`,
+        )
+      }
+
+      dedupeNestedRouteManifestEntries(
+        childRouteId,
+        childRoute,
         routesById,
         seenPreloads,
+        seenAssets,
       )
     }
   }
@@ -559,4 +615,10 @@ export function dedupeNestedRoutePreloads(
       seenPreloads.delete(resolveManifestAssetLink(routePreloads[i]!).href)
     }
   }
+
+  if (routeAssets) {
+    for (let i = routeAssets.length - 1; i >= 0; i--) {
+      seenAssets.delete(getAssetIdentity(routeAssets[i]!))
+    }
+  }
 }
PATCH

# Idempotency check - verify a distinctive line from the patch
if ! grep -q "dedupeNestedRouteManifestEntries" packages/start-plugin-core/src/start-manifest-plugin/manifestBuilder.ts; then
    echo "Error: Patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
