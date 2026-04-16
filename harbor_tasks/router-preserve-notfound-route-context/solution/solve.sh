#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: if already patched, exit early
if grep -q "error.routeId ??= matchState.routeId as any" packages/react-router/src/Match.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch using heredoc
cat <<'PATCH' | git apply -
diff --git a/packages/react-router/src/Match.tsx b/packages/react-router/src/Match.tsx
index 910d1ef2243..ae30f4b7ec4 100644
--- a/packages/react-router/src/Match.tsx
+++ b/packages/react-router/src/Match.tsx
@@ -167,7 +167,10 @@ function MatchView({
             errorComponent={routeErrorComponent || ErrorComponent}
             onCatch={(error, errorInfo) => {
               // Forward not found errors (we don't want to show the error component for these)
-              if (isNotFound(error)) throw error
+              if (isNotFound(error)) {
+                error.routeId ??= matchState.routeId as any
+                throw error
+              }
               if (process.env.NODE_ENV !== 'production') {
                 console.warn(`Warning: Error in route match: ${matchId}`)
               }
@@ -176,6 +179,8 @@ function MatchView({
           >
             <ResolvedNotFoundBoundary
               fallback={(error) => {
+                error.routeId ??= matchState.routeId as any
+
                 // If the current not found handler doesn't exist or it has a
                 // route ID which doesn't match the current route, rethrow the error
                 if (
diff --git a/packages/solid-router/src/Match.tsx b/packages/solid-router/src/Match.tsx
index b02d07513da..b1f1c2b824f 100644
--- a/packages/solid-router/src/Match.tsx
+++ b/packages/solid-router/src/Match.tsx
@@ -11,7 +11,7 @@ import { isServer } from '@tanstack/router-core/isServer'
 import { Dynamic } from 'solid-js/web'
 import { CatchBoundary, ErrorComponent } from './CatchBoundary'
 import { useRouter } from './useRouter'
-import { CatchNotFound } from './not-found'
+import { CatchNotFound, getNotFound } from './not-found'
 import { nearestMatchContext } from './matchContext'
 import { SafeFragment } from './SafeFragment'
 import { renderRouteNotFound } from './renderRouteNotFound'
@@ -117,7 +117,12 @@ export const Match = (props: { matchId: string }) => {
                   errorComponent={routeErrorComponent() || ErrorComponent}
                   onCatch={(error: Error) => {
                     // Forward not found errors (we don't want to show the error component for these)
-                    if (isNotFound(error)) throw error
+                    const notFoundError = getNotFound(error)
+                    if (notFoundError) {
+                      notFoundError.routeId ??= currentMatchState()
+                        .routeId as any
+                      throw notFoundError
+                    }
                     if (process.env.NODE_ENV !== 'production') {
                       console.warn(
                         `Warning: Error in route match: ${currentMatchState().routeId}`,
@@ -129,20 +134,26 @@ export const Match = (props: { matchId: string }) => {
                   <Dynamic
                     component={ResolvedNotFoundBoundary()}
                     fallback={(error: any) => {
+                      const notFoundError = getNotFound(error) ?? error
+
+                      notFoundError.routeId ??= currentMatchState()
+                        .routeId as any
+
                       // If the current not found handler doesn't exist or it has a
                       // route ID which doesn't match the current route, rethrow the error
                       if (
                         !routeNotFoundComponent() ||
-                        (error.routeId &&
-                          error.routeId !== currentMatchState().routeId) ||
-                        (!error.routeId && !route().isRoot)
+                        (notFoundError.routeId &&
+                          notFoundError.routeId !==
+                            currentMatchState().routeId) ||
+                        (!notFoundError.routeId && !route().isRoot)
                       )
-                        throw error
+                        throw notFoundError

                       return (
                         <Dynamic
                           component={routeNotFoundComponent()}
-                          {...error}
+                          {...notFoundError}
                         />
                       )
                     }}
diff --git a/packages/solid-router/src/not-found.tsx b/packages/solid-router/src/not-found.tsx
index cc73adc53c0..19fe0a28f2a 100644
--- a/packages/solid-router/src/not-found.tsx
+++ b/packages/solid-router/src/not-found.tsx
@@ -4,9 +4,25 @@ import { CatchBoundary } from './CatchBoundary'
 import { useRouter } from './useRouter'
 import type { NotFoundError } from '@tanstack/router-core'

+// Solid wraps non-Error throws in an Error and stores the original thrown value
+// on `cause`, so component-thrown `notFound()` needs one extra unwrapping step.
+export function getNotFound(
+  error: unknown,
+): (NotFoundError & { isNotFound: true }) | undefined {
+  if (isNotFound(error)) {
+    return error as NotFoundError & { isNotFound: true }
+  }
+
+  if (isNotFound((error as any)?.cause)) {
+    return (error as any).cause as NotFoundError & { isNotFound: true }
+  }
+
+  return undefined
+}
+
 export function CatchNotFound(props: {
   fallback?: (error: NotFoundError) => Solid.JSX.Element
-  onCatch?: (error: Error) => void
+  onCatch?: (error: NotFoundError) => void
   children: Solid.JSX.Element
 }) {
   const router = useRouter()
@@ -18,15 +34,19 @@ export function CatchNotFound(props: {
     <CatchBoundary
       getResetKey={() => `not-found-${pathname()}-${status()}`}
       onCatch={(error) => {
-        if (isNotFound(error)) {
-          props.onCatch?.(error)
+        const notFoundError = getNotFound(error)
+
+        if (notFoundError) {
+          props.onCatch?.(notFoundError)
         } else {
           throw error
         }
       }}
       errorComponent={({ error }) => {
-        if (isNotFound(error)) {
-          return props.fallback?.(error)
+        const notFoundError = getNotFound(error)
+
+        if (notFoundError) {
+          return props.fallback?.(notFoundError)
         } else {
           throw error
         }
diff --git a/packages/vue-router/src/Match.tsx b/packages/vue-router/src/Match.tsx
index 380ff00843e..f078986be70 100644
--- a/packages/vue-router/src/Match.tsx
+++ b/packages/vue-router/src/Match.tsx
@@ -168,6 +168,8 @@ export const Match = Vue.defineComponent({
         if (routeNotFoundComponent.value) {
           content = Vue.h(CatchNotFound, {
             fallback: (error: any) => {
+              error.routeId ??= matchData.value?.routeId as any
+
               // If the current not found handler doesn't exist or it has a
               // route ID which doesn't match the current route, rethrow the error
               if (
@@ -190,7 +192,10 @@ export const Match = Vue.defineComponent({
             errorComponent: routeErrorComponent.value || ErrorComponent,
             onCatch: (error: Error) => {
               // Forward not found errors (we don't want to show the error component for these)
-              if (isNotFound(error)) throw error
+              if (isNotFound(error)) {
+                error.routeId ??= matchData.value?.routeId as any
+                throw error
+              }
               if (process.env.NODE_ENV !== 'production') {
                 console.warn(`Warning: Error in route match: ${actualMatchId}`)
               }
PATCH

echo "Gold patch applied successfully."
