#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if patch already applied
if grep -q "escapeRegExp(stripSegment)" packages/router-generator/src/filesystem/physical/getRouteNodes.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/router-generator/src/filesystem/physical/getRouteNodes.ts b/packages/router-generator/src/filesystem/physical/getRouteNodes.ts
index 172e5bbf50f..8d25e7b71a7 100644
--- a/packages/router-generator/src/filesystem/physical/getRouteNodes.ts
+++ b/packages/router-generator/src/filesystem/physical/getRouteNodes.ts
@@ -2,6 +2,7 @@ import path from 'node:path'
 import * as fsp from 'node:fs/promises'
 import {
   determineInitialRoutePath,
+  escapeRegExp,
   hasEscapedLeadingUnderscore,
   removeExt,
   replaceBackslash,
@@ -265,9 +266,12 @@ export async function getRouteNodes(

           if (suffixToStrip || shouldStripRouteToken) {
             const stripSegment = suffixToStrip ?? lastRouteSegment
-            routePath = routePath.replace(new RegExp(`/${stripSegment}$`), '')
+            routePath = routePath.replace(
+              new RegExp(`/${escapeRegExp(stripSegment)}$`),
+              '',
+            )
             originalRoutePath = originalRoutePath.replace(
-              new RegExp(`/${stripSegment}$`),
+              new RegExp(`/${escapeRegExp(stripSegment)}$`),
               '',
             )
           }
@@ -305,13 +309,13 @@ export async function getRouteNodes(

               routePath =
                 routePath.replace(
-                  new RegExp(`/${updatedLastRouteSegment}$`),
+                  new RegExp(`/${escapeRegExp(updatedLastRouteSegment)}$`),
                   '/',
                 ) || (isLayoutRoute ? '' : '/')

               originalRoutePath =
                 originalRoutePath.replace(
-                  new RegExp(`/${indexTokenCandidate}$`),
+                  new RegExp(`/${escapeRegExp(indexTokenCandidate)}$`),
                   '/',
                 ) || (isLayoutRoute ? '' : '/')
             }
diff --git a/packages/router-generator/src/utils.ts b/packages/router-generator/src/utils.ts
index 7dc74d7f8e2..251753a6336 100644
--- a/packages/router-generator/src/utils.ts
+++ b/packages/router-generator/src/utils.ts
@@ -414,7 +414,7 @@ export function isSegmentPathless(
   return !hasEscapedLeadingUnderscore(originalSegment)
 }

-function escapeRegExp(s: string): string {
+export function escapeRegExp(s: string): string {
   return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
 }

PATCH

echo "Patch applied successfully."

# Rebuild the router-generator package
pnpm nx run @tanstack/router-generator:build
