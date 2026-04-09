#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch - convert ShouldBlockFnLocation from interface to type
patch -p1 <<'PATCH'
diff --git a/packages/react-router/src/useBlocker.tsx b/packages/react-router/src/useBlocker.tsx
index 209af19501a..a40fe19b50d 100644
--- a/packages/react-router/src/useBlocker.tsx
+++ b/packages/react-router/src/useBlocker.tsx
@@ -12,12 +12,12 @@ import type {
   RegisteredRouter,
 } from '@tanstack/router-core'

-interface ShouldBlockFnLocation<
+type ShouldBlockFnLocation<
   out TRouteId,
   out TFullPath,
   out TAllParams,
   out TFullSearchSchema,
-> {
+> = {
   routeId: TRouteId
   fullPath: TFullPath
   pathname: string
diff --git a/packages/solid-router/src/useBlocker.tsx b/packages/solid-router/src/useBlocker.tsx
index f07c7bf7b55..2e87ed0673e 100644
--- a/packages/solid-router/src/useBlocker.tsx
+++ b/packages/solid-router/src/useBlocker.tsx
@@ -13,12 +13,12 @@ import type {
   RegisteredRouter,
 } from '@tanstack/router-core'

-interface ShouldBlockFnLocation<
+type ShouldBlockFnLocation<
   out TRouteId,
   out TFullPath,
   out TAllParams,
   out TFullSearchSchema,
-> {
+> = {
   routeId: TRouteId
   fullPath: TFullPath
   pathname: string
diff --git a/packages/vue-router/src/useBlocker.tsx b/packages/vue-router/src/useBlocker.tsx
index 082c8de0409..71c6e60e509 100644
--- a/packages/vue-router/src/useBlocker.tsx
+++ b/packages/vue-router/src/useBlocker.tsx
@@ -12,12 +12,12 @@ import type {
   RegisteredRouter,
 } from '@tanstack/router-core'

-interface ShouldBlockFnLocation<
+type ShouldBlockFnLocation<
   out TRouteId,
   out TFullPath,
   out TAllParams,
   out TFullSearchSchema,
-> {
+> = {
   routeId: TRouteId
   fullPath: TFullPath
   pathname: string
PATCH

# Idempotency check - verify the distinctive line from the patch
if grep -q "type ShouldBlockFnLocation<" packages/react-router/src/useBlocker.tsx; then
    echo "Patch already applied (idempotency check passed)"
else
    echo "Failed to apply patch"
    exit 1
fi
