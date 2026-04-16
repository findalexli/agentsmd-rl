#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch for MatchRoute reactivity fix
patch -p1 << 'PATCH'
diff --git a/packages/solid-router/src/Matches.tsx b/packages/solid-router/src/Matches.tsx
index abc123..def456 100644
--- a/packages/solid-router/src/Matches.tsx
+++ b/packages/solid-router/src/Matches.tsx
@@ -144,9 +144,9 @@ export function useMatchRoute<TRouter extends AnyRouter = RegisteredRouter>() {
   ): Solid.Accessor<
     false | Expand<ResolveRoute<TRouter, TFrom, TTo>['types']['allParams']>
   > => {
-    const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
-
     return Solid.createMemo(() => {
+      const { pending, caseSensitive, fuzzy, includeSearch, ...rest } = opts
+
       router.stores.matchRouteReactivity.state
       return router.matchRoute(rest as any, {
         pending,
@@ -185,19 +185,19 @@ export function MatchRoute<
 >(props: MakeMatchRouteOptions<TRouter, TFrom, TTo, TMaskFrom, TMaskTo>): any {
   const matchRoute = useMatchRoute()
   const params = matchRoute(props as any)
-  const child = props.children

-  const renderedChild = () => {
+  const renderedChild = Solid.createMemo(() => {
     const matchedParams = params()
+    const child = props.children

     if (typeof child === 'function') {
       return (child as any)(matchedParams)
     }

     return matchedParams ? child : null
-  }
+  })

-  return renderedChild()
+  return <>{renderedChild()}</>
 }
PATCH

# Idempotency check: verify the distinctive line is now inside createMemo
if ! grep -A 2 "return Solid.createMemo" packages/solid-router/src/Matches.tsx | grep -q "const { pending, caseSensitive, fuzzy, includeSearch"; then
    echo "ERROR: Patch may not have been applied correctly"
    exit 1
fi

echo "Gold patch applied successfully"
