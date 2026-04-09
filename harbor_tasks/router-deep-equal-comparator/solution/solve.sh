#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch for deepEqual comparator addition
cat << 'PATCH' | git apply -
diff --git a/packages/react-router/src/Scripts.tsx b/packages/react-router/src/Scripts.tsx
index b4ef9474496..d2110b68be0 100644
--- a/packages/react-router/src/Scripts.tsx
+++ b/packages/react-router/src/Scripts.tsx
@@ -1,4 +1,5 @@
 import { useStore } from '@tanstack/react-store'
+import { deepEqual } from '@tanstack/router-core'
 import { isServer } from '@tanstack/router-core/isServer'
 import { Asset } from './Asset'
 import { useRouter } from './useRouter'
@@ -68,9 +69,14 @@ export const Scripts = () => {
   const assetScripts = useStore(
     router.stores.activeMatchesSnapshot,
     getAssetScripts,
+    deepEqual,
   )
   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
-  const scripts = useStore(router.stores.activeMatchesSnapshot, getScripts)
+  const scripts = useStore(
+    router.stores.activeMatchesSnapshot,
+    getScripts,
+    deepEqual,
+  )

   return renderScripts(router, scripts, assetScripts)
 }
diff --git a/packages/react-router/src/headContentUtils.tsx b/packages/react-router/src/headContentUtils.tsx
index ea426a6dd6d..5340d8aa19e 100644
--- a/packages/react-router/src/headContentUtils.tsx
+++ b/packages/react-router/src/headContentUtils.tsx
@@ -1,6 +1,6 @@
 import * as React from 'react'
 import { useStore } from '@tanstack/react-store'
-import { escapeHtml } from '@tanstack/router-core'
+import { deepEqual, escapeHtml } from '@tanstack/router-core'
 import { isServer } from '@tanstack/router-core/isServer'
 import { useRouter } from './useRouter'
 import type { RouterManagedTag } from '@tanstack/router-core'
@@ -183,9 +183,13 @@ export const useTags = () => {
   }

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
-  const routeMeta = useStore(router.stores.activeMatchesSnapshot, (matches) => {
-    return matches.map((match) => match.meta!).filter(Boolean)
-  })
+  const routeMeta = useStore(
+    router.stores.activeMatchesSnapshot,
+    (matches) => {
+      return matches.map((match) => match.meta!).filter(Boolean)
+    },
+    deepEqual,
+  )

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
   const meta: Array<RouterManagedTag> = React.useMemo(() => {
@@ -260,42 +264,46 @@ export const useTags = () => {
   }, [routeMeta, nonce])

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
-  const links = useStore(router.stores.activeMatchesSnapshot, (matches) => {
-    const constructed = matches
-      .map((match) => match.links!)
-      .filter(Boolean)
-      .flat(1)
-      .map((link) => ({
-        tag: 'link',
-        attrs: {
-          ...link,
-          nonce,
-        },
-      })) satisfies Array<RouterManagedTag>
+  const links = useStore(
+    router.stores.activeMatchesSnapshot,
+    (matches) => {
+      const constructed = matches
+        .map((match) => match.links!)
+        .filter(Boolean)
+        .flat(1)
+        .map((link) => ({
+          tag: 'link',
+          attrs: {
+            ...link,
+            nonce,
+          },
+        })) satisfies Array<RouterManagedTag>

-    const manifest = router.ssr?.manifest
+      const manifest = router.ssr?.manifest

-    // These are the assets extracted from the ViteManifest
-    // using the `startManifestPlugin`
-    const assets = matches
-      .map((match) => manifest?.routes[match.routeId]?.assets ?? [])
-      .filter(Boolean)
-      .flat(1)
-      .filter((asset) => asset.tag === 'link')
-      .map(
-        (asset) =>
-          ({
-            tag: 'link',
-            attrs: {
-              ...asset.attrs,
-              suppressHydrationWarning: true,
-              nonce,
-            },
-          }) satisfies RouterManagedTag,
-      )
+      // These are the assets extracted from the ViteManifest
+      // using the `startManifestPlugin`
+      const assets = matches
+        .map((match) => manifest?.routes[match.routeId]?.assets ?? [])
+        .filter(Boolean)
+        .flat(1)
+        .filter((asset) => asset.tag === 'link')
+        .map(
+          (asset) =>
+            ({
+              tag: 'link',
+              attrs: {
+                ...asset.attrs,
+                suppressHydrationWarning: true,
+                nonce,
+              },
+            }) satisfies RouterManagedTag,
+        )

-    return [...constructed, ...assets]
-  })
+      return [...constructed, ...assets]
+    },
+    deepEqual,
+  )

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
   const preloadLinks = useStore(
@@ -322,23 +330,27 @@ export const useTags = () => {

       return preloadLinks
     },
+    deepEqual,
   )

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
-  const styles = useStore(router.stores.activeMatchesSnapshot, (matches) =>
-    (
-      matches
-        .map((match) => match.styles!)
-        .flat(1)
-        .filter(Boolean) as Array<RouterManagedTag>
-    ).map(({ children, ...attrs }) => ({
-      tag: 'style',
-      attrs: {
-        ...attrs,
-        nonce,
-      },
-      children,
-    })),
+  const styles = useStore(
+    router.stores.activeMatchesSnapshot,
+    (matches) =>
+      (
+        matches
+          .map((match) => match.styles!)
+          .flat(1)
+          .filter(Boolean) as Array<RouterManagedTag>
+      ).map(({ children, ...attrs }) => ({
+        tag: 'style',
+        attrs: {
+          ...attrs,
+          nonce,
+        },
+        children,
+      })),
+    deepEqual,
   )

   // eslint-disable-next-line react-hooks/rules-of-hooks -- condition is static
@@ -358,6 +370,7 @@ export const useTags = () => {
         },
         children,
       })),
+    deepEqual,
   )

   return uniqBy(
PATCH

echo "Gold patch applied successfully"
