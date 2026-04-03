#!/usr/bin/env bash
set -euo pipefail

cd /workspace/router

# Idempotent: skip if already applied
if grep -q 'publicHref: href,' packages/router-core/src/router.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/e2e/react-start/custom-basepath/tests/navigation.spec.ts b/e2e/react-start/custom-basepath/tests/navigation.spec.ts
index e238134d2ed..3e6a5bd1bea 100644
--- a/e2e/react-start/custom-basepath/tests/navigation.spec.ts
+++ b/e2e/react-start/custom-basepath/tests/navigation.spec.ts
@@ -61,14 +61,12 @@ test('server-side redirect', async ({ page, baseURL }) => {
   expect(page.url()).toBe(`${baseURL}/posts/1`)

   // do not follow redirects since we want to test the Location header
-  // Both requests (with or without basepath) should redirect directly to the final destination.
-  // The router is smart enough to skip the intermediate "add basepath" redirect and go
-  // straight to where the route's beforeLoad redirect points to.
+  // first go to the route WITHOUT the base path, this will just add the base path
   await page.request
     .get('/redirect/throw-it', { maxRedirects: 0 })
     .then((res) => {
       const headers = new Headers(res.headers())
-      expect(headers.get('location')).toBe('/custom/basepath/posts/1')
+      expect(headers.get('location')).toBe('/custom/basepath/redirect/throw-it')
     })
   await page.request
     .get('/custom/basepath/redirect/throw-it', { maxRedirects: 0 })
diff --git a/e2e/react-start/i18n-paraglide/src/server.ts b/e2e/react-start/i18n-paraglide/src/server.ts
index 9542b01d4ac..d4dc80a8de3 100644
--- a/e2e/react-start/i18n-paraglide/src/server.ts
+++ b/e2e/react-start/i18n-paraglide/src/server.ts
@@ -3,6 +3,6 @@ import handler from '@tanstack/react-start/server-entry'

 export default {
   fetch(req: Request): Promise<Response> {
-    return paraglideMiddleware(req, ({ request }) => handler.fetch(request))
+    return paraglideMiddleware(req, () => handler.fetch(req))
   },
 }
diff --git a/e2e/solid-start/custom-basepath/tests/navigation.spec.ts b/e2e/solid-start/custom-basepath/tests/navigation.spec.ts
index e238134d2ed..3e6a5bd1bea 100644
--- a/e2e/solid-start/custom-basepath/tests/navigation.spec.ts
+++ b/e2e/solid-start/custom-basepath/tests/navigation.spec.ts
@@ -61,14 +61,12 @@ test('server-side redirect', async ({ page, baseURL }) => {
   expect(page.url()).toBe(`${baseURL}/posts/1`)

   // do not follow redirects since we want to test the Location header
-  // Both requests (with or without basepath) should redirect directly to the final destination.
-  // The router is smart enough to skip the intermediate "add basepath" redirect and go
-  // straight to where the route's beforeLoad redirect points to.
+  // first go to the route WITHOUT the base path, this will just add the base path
   await page.request
     .get('/redirect/throw-it', { maxRedirects: 0 })
     .then((res) => {
       const headers = new Headers(res.headers())
-      expect(headers.get('location')).toBe('/custom/basepath/posts/1')
+      expect(headers.get('location')).toBe('/custom/basepath/redirect/throw-it')
     })
   await page.request
     .get('/custom/basepath/redirect/throw-it', { maxRedirects: 0 })
diff --git a/e2e/vue-start/custom-basepath/tests/navigation.spec.ts b/e2e/vue-start/custom-basepath/tests/navigation.spec.ts
index e238134d2ed..3e6a5bd1bea 100644
--- a/e2e/vue-start/custom-basepath/tests/navigation.spec.ts
+++ b/e2e/vue-start/custom-basepath/tests/navigation.spec.ts
@@ -61,14 +61,12 @@ test('server-side redirect', async ({ page, baseURL }) => {
   expect(page.url()).toBe(`${baseURL}/posts/1`)

   // do not follow redirects since we want to test the Location header
-  // Both requests (with or without basepath) should redirect directly to the final destination.
-  // The router is smart enough to skip the intermediate "add basepath" redirect and go
-  // straight to where the route's beforeLoad redirect points to.
+  // first go to the route WITHOUT the base path, this will just add the base path
   await page.request
     .get('/redirect/throw-it', { maxRedirects: 0 })
     .then((res) => {
       const headers = new Headers(res.headers())
-      expect(headers.get('location')).toBe('/custom/basepath/posts/1')
+      expect(headers.get('location')).toBe('/custom/basepath/redirect/throw-it')
     })
   await page.request
     .get('/custom/basepath/redirect/throw-it', { maxRedirects: 0 })
diff --git a/examples/react/i18n-paraglide/README.md b/examples/react/i18n-paraglide/README.md
index 4dac51934f4..98b25f6d0fe 100644
--- a/examples/react/i18n-paraglide/README.md
+++ b/examples/react/i18n-paraglide/README.md
@@ -1,6 +1,6 @@
 # TanStack Router - i18n with Paraglide Example

-This example shows how to use Paraglide with TanStack Router. The source code can be found [in the Paraglide monorepo](https://github.com/opral/monorepo/tree/main/inlang/packages/paraglide/paraglide-js/examples/tanstack-router).
+This example shows how to use Paraglide with TanStack Router.

 - [TanStack Router Docs](https://tanstack.com/router)
 - [Paraglide Documentation](https://inlang.com/m/gerre34r/library-inlang-paraglideJs)
diff --git a/examples/react/start-i18n-paraglide/README.md b/examples/react/start-i18n-paraglide/README.md
index f1aa91f5184..7f481e133c7 100644
--- a/examples/react/start-i18n-paraglide/README.md
+++ b/examples/react/start-i18n-paraglide/README.md
@@ -1,6 +1,6 @@
 # TanStack Start example with Paraglide

-This example shows how to use Paraglide with TanStack Start. The source code can be found [in the Paraglide monorepo](https://github.com/opral/monorepo/tree/main/inlang/packages/paraglide/paraglide-js/examples/tanstack-start).
+This example shows how to use Paraglide with TanStack Start.

 - [TanStack Router Docs](https://tanstack.com/router)
 - [Paraglide Documentation](https://inlang.com/m/gerre34r/library-inlang-paraglideJs)
@@ -81,7 +81,7 @@ import { paraglideMiddleware } from './paraglide/server.js'
 import handler from '@tanstack/react-start/server-entry'
 export default {
   fetch(req: Request): Promise<Response> {
-    return paraglideMiddleware(req, ({ request }) => handler.fetch(request))
+    return paraglideMiddleware(req, () => handler.fetch(req))
   },
 }
 ```
diff --git a/examples/solid/i18n-paraglide/README.md b/examples/solid/i18n-paraglide/README.md
index e9dd968ee86..d43951c8f11 100644
--- a/examples/solid/i18n-paraglide/README.md
+++ b/examples/solid/i18n-paraglide/README.md
@@ -1,6 +1,6 @@
 # TanStack Router example

-This example shows how to use Paraglide with TanStack Router. The source code can be found [here](https://github.com/opral/monorepo/tree/main/inlang/packages/paraglide/paraglide-js/examples/tanstack-router).
+This example shows how to use Paraglide with TanStack Router.

 ## Getting started

diff --git a/examples/solid/start-i18n-paraglide/README.md b/examples/solid/start-i18n-paraglide/README.md
index eee202e3a13..395c59fb956 100644
--- a/examples/solid/start-i18n-paraglide/README.md
+++ b/examples/solid/start-i18n-paraglide/README.md
@@ -1,6 +1,6 @@
 # TanStack Start example

-This example shows how to use Paraglide with TanStack Start. The source code can be found [here](https://github.com/opral/monorepo/tree/main/inlang/packages/paraglide/paraglide-js/examples/tanstack-start).
+This example shows how to use Paraglide with TanStack Start.

 ## Getting started

@@ -71,7 +71,7 @@ import handler from '@tanstack/solid-start/server-entry'

 export default {
   fetch(req: Request): Promise<Response> {
-    return paraglideMiddleware(req, ({ request }) => handler.fetch(request))
+    return paraglideMiddleware(req, () => handler.fetch(req))
   },
 }
 ```
diff --git a/packages/react-router/tests/router.test.tsx b/packages/react-router/tests/router.test.tsx
index 4708552d869..8d747c8e65b 100644
--- a/packages/react-router/tests/router.test.tsx
+++ b/packages/react-router/tests/router.test.tsx
@@ -3125,55 +3125,6 @@ describe('Router rewrite functionality', () => {
     expect(history.location.pathname).toBe('/user')
   })

-  it('should not cause redirect loops with i18n locale prefix rewriting', async () => {
-    // This test simulates an i18n middleware that:
-    // - Input: strips locale prefix (e.g., /en/home -> /home)
-    // - Output: adds locale prefix back (e.g., /home -> /en/home)
-
-    const rootRoute = createRootRoute({
-      component: () => <Outlet />,
-    })
-
-    const homeRoute = createRoute({
-      getParentRoute: () => rootRoute,
-      path: '/home',
-      component: () => <div data-testid="home">Home</div>,
-    })
-
-    const routeTree = rootRoute.addChildren([homeRoute])
-
-    // The history starts at the public-facing locale-prefixed URL.
-    // The input rewrite strips the locale prefix for internal routing.
-    const history = createMemoryHistory({ initialEntries: ['/en/home'] })
-
-    const router = createRouter({
-      routeTree,
-      history,
-      rewrite: {
-        input: ({ url }) => {
-          // Strip locale prefix: /en/home -> /home
-          if (url.pathname.startsWith('/en')) {
-            url.pathname = url.pathname.replace(/^\/en/, '')
-          }
-          return url
-        },
-      },
-    })
-
-    render(<RouterProvider router={router} />)
-
-    await waitFor(() => {
-      expect(screen.getByTestId('home')).toBeInTheDocument()
-    })
-
-    // The internal pathname should be /home (after input rewrite strips /en)
-    expect(router.state.location.pathname).toBe('/home')
-
-    // The publicHref should include the locale prefix (via output rewrite)
-    // Since we only have input rewrite here, publicHref equals the internal href
-    expect(router.state.location.publicHref).toBe('/home')
-  })
-
   it('should handle i18n rewriting with navigation between localized routes', async () => {
     // Tests navigation between routes with i18n locale prefix rewriting

diff --git a/packages/router-core/src/router.ts b/packages/router-core/src/router.ts
index 042af0abb17..d9d808a3185 100644
--- a/packages/router-core/src/router.ts
+++ b/packages/router-core/src/router.ts
@@ -1188,33 +1188,11 @@ export class RouterCore<

       const fullPath = url.href.replace(url.origin, '')

-      // Save the internal pathname for route matching (before output rewrite)
-      const internalPathname = url.pathname
-
-      // Compute publicHref by applying the output rewrite.
-      //
-      // The publicHref represents the URL as it should appear in the browser.
-      // This must match what buildLocation computes for the same logical route,
-      // otherwise the server-side redirect check will see a mismatch and trigger
-      // an infinite redirect loop.
-      //
-      // We always apply the output rewrite (not conditionally) because the
-      // incoming URL may have already been transformed by external middleware
-      // before reaching the router. In that case, the input rewrite has nothing
-      // to do, but we still need the output rewrite to reconstruct the correct
-      // public-facing URL.
-      //
-      // Clone the URL to avoid mutating the one used for route matching.
-      const urlForOutput = new URL(url.href)
-      const rewrittenUrl = executeRewriteOutput(this.rewrite, urlForOutput)
-      const publicHref =
-        rewrittenUrl.pathname + rewrittenUrl.search + rewrittenUrl.hash
-
       return {
         href: fullPath,
-        publicHref,
+        publicHref: href,
         url: url,
-        pathname: decodePath(internalPathname),
+        pathname: decodePath(url.pathname),
         searchStr,
         search: replaceEqualDeep(previousLocation?.search, parsedSearch) as any,
         hash: url.hash.split('#').reverse()[0] ?? '',

PATCH

echo "Patch applied successfully."
