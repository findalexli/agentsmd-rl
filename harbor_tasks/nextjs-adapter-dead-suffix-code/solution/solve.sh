#!/usr/bin/env bash
set -euo pipefail

# Idempotency check: if shouldSkipSuffixes is already gone, patch was applied
if ! grep -q 'shouldSkipSuffixes' packages/next/src/build/adapter/build-complete.ts 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/build/adapter/build-complete.ts b/packages/next/src/build/adapter/build-complete.ts
index 0a801a8a69529..2b26b1b5e830b 100644
--- a/packages/next/src/build/adapter/build-complete.ts
+++ b/packages/next/src/build/adapter/build-complete.ts
@@ -1958,8 +1958,6 @@ export async function handleBuildComplete({
       const isFallbackFalse =
         prerenderManifest.dynamicRoutes[route.page]?.fallback === false

-      const { hasFallbackRootParams } = route
-
       const sourceRegex = routeRegex.namedRegex.replace(
         '^',
         `^${config.basePath && config.basePath !== '/' ? path.posix.join('/', config.basePath || '') : ''}[/]?${shouldLocalize ? '(?<nextLocale>[^/]{1,})' : ''}`
@@ -1973,23 +1971,11 @@ export async function handleBuildComplete({
         ) + getDestinationQuery(route.routeKeys)

       if (appPageKeys && appPageKeys.length > 0) {
-        // If we have fallback root params (implying we've already
-        // emitted a rewrite for the /_tree request), or if the route
-        // has PPR enabled and client param parsing is enabled, then
-        // we don't need to include any other suffixes.
-        const shouldSkipSuffixes = hasFallbackRootParams
-
         dynamicRoutes.push({
           source: route.page + '.rsc',
           sourceRegex: sourceRegex.replace(
             new RegExp(escapeStringRegexp('(?:/)?$')),
-            // Now than the upstream issues has been resolved, we can safely
-            // add the suffix back, this resolves a bug related to segment
-            // rewrites not capturing the correct suffix values when
-            // enabled.
-            shouldSkipSuffixes
-              ? '(?<rscSuffix>\\.rsc|\\.segments/.+\\.segment\\.rsc)(?:/)?$'
-              : '(?<rscSuffix>\\.rsc|\\.segments/.+\\.segment\\.rsc)(?:/)?$'
+            '(?<rscSuffix>\\.rsc|\\.segments/.+\\.segment\\.rsc)(?:/)?$'
           ),
           destination: destination?.replace(/($|\?)/, '$rscSuffix$1'),
           has:
diff --git a/packages/next/src/build/index.ts b/packages/next/src/build/index.ts
index bc24502bbef5c..76f1b14724e3c 100644
--- a/packages/next/src/build/index.ts
+++ b/packages/next/src/build/index.ts
@@ -401,12 +401,6 @@ export type ManifestRoute = ManifestBuiltRoute & {
   namedRegex: string
   routeKeys: { [key: string]: string }

-  /**
-   * If true, this indicates that the route has fallback root params. This is
-   * used to simplify the route regex for matching.
-   */
-  hasFallbackRootParams?: boolean
-
   /**
    * The prefetch segment data routes for this route. This is used to rewrite
    * the prefetch segment data routes (or the inverse) to the correct

PATCH

echo "Patch applied successfully."
