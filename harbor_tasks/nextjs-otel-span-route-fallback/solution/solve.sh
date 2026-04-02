#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotency check: if the fix is already applied, the route assignment
# in app-page.ts will use a fallback (|| normalizedSrcPage) instead of
# a bare rootSpanAttributes.get('next.route') inside a conditional.
if grep -q "rootSpanAttributes.get('next.route') || normalizedSrcPage" \
    packages/next/src/build/templates/app-page.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/build/templates/app-page.ts b/packages/next/src/build/templates/app-page.ts
index 96a4ddf81c7501..fc621e81ba66ec 100644
--- a/packages/next/src/build/templates/app-page.ts
+++ b/packages/next/src/build/templates/app-page.ts
@@ -713,25 +713,21 @@ export async function handler(
           return
         }

-        const route = rootSpanAttributes.get('next.route')
-        if (route) {
-          const name = `${method} ${route}`
-
-          span.setAttributes({
-            'next.route': route,
-            'http.route': route,
-            'next.span_name': name,
-          })
-          span.updateName(name)
+        const route = rootSpanAttributes.get('next.route') || normalizedSrcPage
+        const name = `${method} ${route}`

-          // Propagate http.route to the parent span if one exists (e.g.
-          // a platform-created HTTP span in adapter deployments).
-          if (parentSpan && parentSpan !== span) {
-            parentSpan.setAttribute('http.route', route)
-            parentSpan.updateName(name)
-          }
-        } else {
-          span.updateName(`${method} ${srcPage}`)
+        span.setAttributes({
+          'next.route': route,
+          'http.route': route,
+          'next.span_name': name,
+        })
+        span.updateName(name)
+
+        // Propagate http.route to the parent span if one exists (e.g.
+        // a platform-created HTTP span in adapter deployments).
+        if (parentSpan && parentSpan !== span) {
+          parentSpan.setAttribute('http.route', route)
+          parentSpan.updateName(name)
         }
       })
     }
diff --git a/packages/next/src/build/templates/app-route.ts b/packages/next/src/build/templates/app-route.ts
index 4817c5883e9bff..10ba66d57847ab 100644
--- a/packages/next/src/build/templates/app-route.ts
+++ b/packages/next/src/build/templates/app-route.ts
@@ -301,25 +301,21 @@ export async function handler(
           return
         }

-        const route = rootSpanAttributes.get('next.route')
-        if (route) {
-          const name = `${method} ${route}`
-
-          span.setAttributes({
-            'next.route': route,
-            'http.route': route,
-            'next.span_name': name,
-          })
-          span.updateName(name)
-
-          // Propagate http.route to the parent span if one exists (e.g.
-          // a platform-created HTTP span in adapter deployments).
-          if (parentSpan && parentSpan !== span) {
-            parentSpan.setAttribute('http.route', route)
-            parentSpan.updateName(name)
-          }
-        } else {
-          span.updateName(`${method} ${srcPage}`)
+        const route = rootSpanAttributes.get('next.route') || normalizedSrcPage
+        const name = `${method} ${route}`
+
+        span.setAttributes({
+          'next.route': route,
+          'http.route': route,
+          'next.span_name': name,
+        })
+        span.updateName(name)
+
+        // Propagate http.route to the parent span if one exists (e.g.
+        // a platform-created HTTP span in adapter deployments).
+        if (parentSpan && parentSpan !== span) {
+          parentSpan.setAttribute('http.route', route)
+          parentSpan.updateName(name)
         }
       })
     }
diff --git a/packages/next/src/build/templates/pages-api.ts b/packages/next/src/build/templates/pages-api.ts
index ef1a983a68d4fd..8e0b2dbd0b6ff4 100644
--- a/packages/next/src/build/templates/pages-api.ts
+++ b/packages/next/src/build/templates/pages-api.ts
@@ -138,25 +138,21 @@ export async function handler(
             return
           }

-          const route = rootSpanAttributes.get('next.route')
-          if (route) {
-            const name = `${method} ${route}`
-
-            span.setAttributes({
-              'next.route': route,
-              'http.route': route,
-              'next.span_name': name,
-            })
-            span.updateName(name)
-
-            // Propagate http.route to the parent span if one exists (e.g.
-            // a platform-created HTTP span in adapter deployments).
-            if (parentSpan && parentSpan !== span) {
-              parentSpan.setAttribute('http.route', route)
-              parentSpan.updateName(name)
-            }
-          } else {
-            span.updateName(`${method} ${srcPage}`)
+          const route = rootSpanAttributes.get('next.route') || srcPage
+          const name = `${method} ${route}`
+
+          span.setAttributes({
+            'next.route': route,
+            'http.route': route,
+            'next.span_name': name,
+          })
+          span.updateName(name)
+
+          // Propagate http.route to the parent span if one exists (e.g.
+          // a platform-created HTTP span in adapter deployments).
+          if (parentSpan && parentSpan !== span) {
+            parentSpan.setAttribute('http.route', route)
+            parentSpan.updateName(name)
           }
         })

diff --git a/packages/next/src/server/route-modules/pages/pages-handler.ts b/packages/next/src/server/route-modules/pages/pages-handler.ts
index 4534c1d7978bbf..2c6b62c1a80fbf 100644
--- a/packages/next/src/server/route-modules/pages/pages-handler.ts
+++ b/packages/next/src/server/route-modules/pages/pages-handler.ts
@@ -224,6 +224,9 @@ export const getHandler = ({

     const tracer = getTracer()
     const activeSpan = tracer.getActiveScopeSpan()
+    const isWrappedByNextServer = Boolean(
+      routerServerContext?.isWrappedByNextServer
+    )

     try {
       const method = req.method || 'GET'
@@ -413,26 +416,22 @@ export const getHandler = ({
                     return
                   }

-                  const route = rootSpanAttributes.get('next.route')
-                  if (route) {
-                    const name = `${method} ${route}`
-
-                    span.setAttributes({
-                      'next.route': route,
-                      'http.route': route,
-                      'next.span_name': name,
-                    })
-                    span.updateName(name)
-
-                    // Propagate http.route to the parent span if one exists
-                    // (e.g. a platform-created HTTP span in adapter
-                    // deployments).
-                    if (parentSpan && parentSpan !== span) {
-                      parentSpan.setAttribute('http.route', route)
-                      parentSpan.updateName(name)
-                    }
-                  } else {
-                    span.updateName(`${method} ${srcPage}`)
+                  const route = rootSpanAttributes.get('next.route') || srcPage
+                  const name = `${method} ${route}`
+
+                  span.setAttributes({
+                    'next.route': route,
+                    'http.route': route,
+                    'next.span_name': name,
+                  })
+                  span.updateName(name)
+
+                  // Propagate http.route to the parent span if one exists
+                  // (e.g. a platform-created HTTP span in adapter
+                  // deployments).
+                  if (parentSpan && parentSpan !== span) {
+                    parentSpan.setAttribute('http.route', route)
+                    parentSpan.updateName(name)
                   }
                 })
             } catch (err: unknown) {
@@ -750,23 +749,27 @@ export const getHandler = ({

       // TODO: activeSpan code path is for when wrapped by
       // next-server can be removed when this is no longer used
-      if (activeSpan) {
-        await handleResponse()
+      if (isWrappedByNextServer && activeSpan) {
+        await handleResponse(activeSpan)
       } else {
         parentSpan = tracer.getActiveScopeSpan()
-        await tracer.withPropagatedContext(req.headers, () =>
-          tracer.trace(
-            BaseServerSpan.handleRequest,
-            {
-              spanName: `${method} ${srcPage}`,
-              kind: SpanKind.SERVER,
-              attributes: {
-                'http.method': method,
-                'http.target': req.url,
+        await tracer.withPropagatedContext(
+          req.headers,
+          () =>
+            tracer.trace(
+              BaseServerSpan.handleRequest,
+              {
+                spanName: `${method} ${srcPage}`,
+                kind: SpanKind.SERVER,
+                attributes: {
+                  'http.method': method,
+                  'http.target': req.url,
+                },
               },
-            },
-            handleResponse
-          )
+              handleResponse
+            ),
+          undefined,
+          !isWrappedByNextServer
         )
       }
     } catch (err) {

PATCH

echo "Patch applied successfully."
