#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied (run method is gone)
if ! grep -q 'router\.run()' packages/fetch-router/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/demos/bookstore/README.md b/demos/bookstore/README.md
index 5b7a08e7e6f..790e1305f2c 100644
--- a/demos/bookstore/README.md
+++ b/demos/bookstore/README.md
@@ -21,7 +21,6 @@ Then visit http://localhost:44100

 - [`app/routes.ts`](app/routes.ts) shows declarative route definitions using `route()`, `form()`, and `resources()` helpers. All route URLs are generated with full type safety, so `routes.admin.books.edit.href({ bookId: '123' })` ensures you never have broken links.
 - [`app/router.ts`](app/router.ts) demonstrates how to compose middleware for cross-cutting concerns: static file serving, form data parsing, method override, sessions, and async context. Each middleware is independent and reusable.
-- Tests can use [`router.run()`](../../packages/fetch-router/README.md#running-code-in-request-context) to execute request-scoped code inside the same middleware stack without creating test-only routes.
 - [`app/middleware/database.ts`](app/middleware/database.ts) shows a request-scoped database pattern. It "checks out" a database handle at the start of each request, stores it in request context, and releases it in a `finally` block.
 - [`app/middleware/auth.ts`](app/middleware/auth.ts) provides two patterns:
   - **`loadAuth()`** - Optionally loads the current user without requiring authentication
diff --git a/packages/fetch-router/.changes/minor.router-run.md b/packages/fetch-router/.changes/minor.router-run.md
deleted file mode 100644
index b0acee254ec..00000000000
--- a/packages/fetch-router/.changes/minor.router-run.md
+++ /dev/null
@@ -1,16 +0,0 @@
-Added a new `router.run(...)` API to `@remix-run/fetch-router`
-
-`router.run()` executes a callback inside the router's middleware and request context without dispatching to a route action. This is useful in tests and utilities that need request-scoped values such as authenticated users, checked-out database handles, correlation IDs, or feature flags.
-
-Supported signatures:
-
-```ts
-router.run(input, callback)
-router.run(input, init, callback)
-```
-
-Example:
-
-```ts
-let value = await router.run('https://remix.run', ({ storage }) => storage.get(myStorageKey))
-```
diff --git a/packages/fetch-router/README.md b/packages/fetch-router/README.md
index 94fe81e110a..a3bb7936283 100644
--- a/packages/fetch-router/README.md
+++ b/packages/fetch-router/README.md
@@ -68,37 +68,6 @@ let response = await router.fetch('https://remix.run/blog/hello-remix')
 console.log(await response.text()) // "Post hello-remix"
 ```

-### Running Code In Request Context
-
-Use `router.run()` when you need to execute code inside the router's middleware/request context
-without mapping a test-only route.
-
-```ts
-import { asyncContext } from 'remix/async-context-middleware'
-import { createRouter, createStorageKey } from 'remix/fetch-router'
-
-let key = createStorageKey<string>()
-let router = createRouter({
-  middleware: [
-    asyncContext(),
-    (context, next) => {
-      context.storage.set(key, 'from middleware')
-      return next()
-    },
-  ],
-})
-
-let value = await router.run('https://remix.run', ({ storage }) => storage.get(key))
-console.log(value) // "from middleware"
-
-// You can also provide RequestInit, similar to router.fetch(input, init)
-let method = await router.run('https://remix.run', { method: 'POST' }, ({ method }) => method)
-console.log(method) // "POST"
-```
-
-This is especially useful in tests for request-scoped services like authenticated users, database
-handles, correlation IDs, and per-request feature flags.
-
 The route map is an object of the same shape as the object pass into `route()`, including nested objects. The leaves of the map are `Route` objects, which you can see if you inspect the type of the `routes` variable in your IDE.

 ```ts
diff --git a/packages/fetch-router/src/lib/router.test.ts b/packages/fetch-router/src/lib/router.test.ts
index dcf643d9acf..8afd507fd81 100644
--- a/packages/fetch-router/src/lib/router.test.ts
+++ b/packages/fetch-router/src/lib/router.test.ts
@@ -2,7 +2,6 @@ import * as assert from 'node:assert/strict'
 import { describe, it } from 'node:test'
 import { ArrayMatcher, RoutePattern } from '@remix-run/route-pattern'

-import { createStorageKey } from './app-storage.ts'
 import type { RequestContext } from './request-context.ts'
 import { createRoutes as route } from './route-map.ts'
 import type { MatchData } from './router.ts'
@@ -159,71 +158,6 @@ describe('router.fetch()', () => {
   })
 })

-describe('router.run()', () => {
-  it('runs a callback and returns its value', async () => {
-    let router = createRouter()
-    let result = await router.run(
-      'https://remix.run/posts?sort=asc',
-      ({ url }) => `${url.pathname}:${url.searchParams.get('sort')}`,
-    )
-
-    assert.equal(result, '/posts:asc')
-  })
-
-  it('runs middleware before invoking the callback', async () => {
-    let key = createStorageKey('unset')
-    let requestLog: string[] = []
-
-    let router = createRouter({
-      middleware: [
-        (context, next) => {
-          requestLog.push('middleware')
-          context.storage.set(key, 'ready')
-          return next()
-        },
-      ],
-    })
-
-    let value = await router.run('https://remix.run', ({ storage }) => {
-      requestLog.push('callback')
-      return storage.get(key)
-    })
-
-    assert.equal(value, 'ready')
-    assert.deepEqual(requestLog, ['middleware', 'callback'])
-  })
-
-  it('throws when middleware short-circuits before invoking the callback', async () => {
-    let router = createRouter({
-      middleware: [() => new Response('Unauthorized', { status: 401 })],
-    })
-
-    await assert.rejects(
-      () => router.run('https://remix.run', () => 'ok'),
-      /router.run\(\) callback was not invoked/,
-    )
-  })
-
-  it('propagates callback errors', async () => {
-    let router = createRouter()
-
-    await assert.rejects(
-      () =>
-        router.run('https://remix.run', () => {
-          throw new Error('boom')
-        }),
-      /boom/,
-    )
-  })
-
-  it('accepts RequestInit options', async () => {
-    let router = createRouter()
-    let method = await router.run('https://remix.run', { method: 'POST' }, ({ method }) => method)
-
-    assert.equal(method, 'POST')
-  })
-})
-
 describe('router.map() with single routes', () => {
   it('maps a single route to a request handler', async () => {
     let routes = route({
diff --git a/packages/fetch-router/src/lib/router.ts b/packages/fetch-router/src/lib/router.ts
index 30e5fa3424c..480425b6d92 100644
--- a/packages/fetch-router/src/lib/router.ts
+++ b/packages/fetch-router/src/lib/router.ts
@@ -74,34 +74,6 @@ export interface Router {
    * @returns The response from the route that matched the request
    */
   fetch(input: string | URL | Request, init?: RequestInit): Promise<Response>
-  /**
-   * Run a callback with a request context and middleware.
-   *
-   * This is useful in tests and utility code where you need access to request-scoped context
-   * (such as async-local storage, sessions, or other middleware-provided values) without
-   * dispatching to a route action.
-   *
-   * @param input The request input used to create the request context
-   * @param callback The callback to run
-   * @returns The callback result
-   */
-  run<result>(
-    input: string | URL | Request,
-    callback: (context: RequestContext) => Promise<result> | result,
-  ): Promise<result>
-  /**
-   * Run a callback with a request context and middleware.
-   *
-   * @param input The request input used to create the request context
-   * @param init The request init options
-   * @param callback The callback to run
-   * @returns The callback result
-   */
-  run<result>(
-    input: string | URL | Request,
-    init: RequestInit,
-    callback: (context: RequestContext) => Promise<result> | result,
-  ): Promise<result>
   /**
    * Add a route to the router.
    *
@@ -340,54 +312,6 @@ export function createRouter(options?: RouterOptions): Router {

       return dispatch(context)
     },
-    async run<result>(
-      input: string | URL | Request,
-      initOrCallback: RequestInit | ((context: RequestContext) => Promise<result> | result),
-      maybeCallback?: (context: RequestContext) => Promise<result> | result,
-    ): Promise<result> {
-      let init = typeof initOrCallback === 'function' ? undefined : initOrCallback
-      let callback = typeof initOrCallback === 'function' ? initOrCallback : maybeCallback
-      if (callback == null) {
-        throw new TypeError('router.run() requires a callback function')
-      }
-
-      let context = createRequestContext(input, init)
-      let callbackRan = false
-      let callbackThrew = false
-      let callbackError: unknown = undefined
-      let callbackResult: result | undefined = undefined
-
-      let runCallback = async (): Promise<Response> => {
-        callbackRan = true
-
-        try {
-          callbackResult = await callback(context)
-        } catch (error) {
-          callbackThrew = true
-          callbackError = error
-        }
-
-        return new Response(null, { status: 204 })
-      }
-
-      if (globalMiddleware) {
-        await runMiddleware(globalMiddleware, context, runCallback)
-      } else {
-        await runCallback()
-      }
-
-      if (!callbackRan) {
-        throw new Error(
-          'router.run() callback was not invoked. Ensure all middleware at this URL calls next() and does not return a Response directly.',
-        )
-      }
-
-      if (callbackThrew) {
-        throw callbackError
-      }
-
-      return callbackResult as result
-    },
     route: addRoute,
     map: mapRoutes,
     get<pattern extends string>(

PATCH

echo "Patch applied successfully."
