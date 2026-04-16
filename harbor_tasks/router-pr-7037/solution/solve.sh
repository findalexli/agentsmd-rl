#!/bin/bash
set -e

cd /workspace/router

# Check if patch already applied (idempotency)
if grep -q "type ShouldBlockFnLocation<" packages/react-router/src/useBlocker.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/docs/router/api/router/useBlockerHook.md b/docs/router/api/router/useBlockerHook.md
index 98d4a06c3b2..3d9c00d6022 100644
--- a/docs/router/api/router/useBlockerHook.md
+++ b/docs/router/api/router/useBlockerHook.md
@@ -20,7 +20,7 @@ The `useBlocker` hook accepts a single _required_ argument, an option object:
 - Think of this function as telling the router if it should block the navigation, so returning `true` mean that it should block the navigation and `false` meaning that it should be allowed

 ```ts
-interface ShouldBlockFnLocation<...> {
+type ShouldBlockFnLocation<...> = {
   routeId: TRouteId
   fullPath: TFullPath
   pathname: string
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

echo "Patch applied successfully."
