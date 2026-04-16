#!/bin/bash
set -e

cd /workspace/router

# Check idempotency - skip if already applied
if grep -q "isPromiseLike(a) || isPromiseLike(b)" packages/solid-router/src/useRouterState.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/solid-router/src/useRouterState.tsx b/packages/solid-router/src/useRouterState.tsx
index 809fd7f0374..b417cfed023 100644
--- a/packages/solid-router/src/useRouterState.tsx
+++ b/packages/solid-router/src/useRouterState.tsx
@@ -11,6 +11,8 @@ import type { Accessor } from 'solid-js'
 function deepEqual(a: any, b: any): boolean {
   if (Object.is(a, b)) return true

+  if (isPromiseLike(a) || isPromiseLike(b)) return false
+
   if (
     typeof a !== 'object' ||
     a === null ||
@@ -33,6 +35,14 @@ function deepEqual(a: any, b: any): boolean {
   return true
 }

+function isPromiseLike(value: unknown): value is PromiseLike<unknown> {
+  return (
+    !!value &&
+    (typeof value === 'object' || typeof value === 'function') &&
+    typeof (value as PromiseLike<unknown>).then === 'function'
+  )
+}
+
 export type UseRouterStateOptions<TRouter extends AnyRouter, TSelected> = {
   router?: TRouter
   select?: (state: RouterState<TRouter['routeTree']>) => TSelected
PATCH

echo "Patch applied successfully"
