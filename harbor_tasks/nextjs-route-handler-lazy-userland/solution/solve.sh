#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'ensureUserland' packages/next/src/server/route-modules/app-route/module.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/build/templates/app-route.ts b/packages/next/src/build/templates/app-route.ts
index 10ba66d57847a..7991b066b9364 100644
--- a/packages/next/src/build/templates/app-route.ts
+++ b/packages/next/src/build/templates/app-route.ts
@@ -2,7 +2,6 @@ import {
   AppRouteRouteModule,
   type AppRouteRouteHandlerContext,
   type AppRouteRouteModuleOptions,
-  type AppRouteUserlandModule,
 } from '../../server/route-modules/app-route/module.compiled'
 import { RouteKind } from '../../server/route-kind'
 import { patchFetch as _patchFetch } from '../../server/lib/patch-fetch'
@@ -36,7 +35,6 @@ import {
   type ResponseCacheEntry,
   type ResponseGenerator,
 } from '../../server/response-cache'
-import * as userland from 'VAR_USERLAND'

 // These are injected by the loader afterwards. This is injected as a variable
 // instead of a replacement because this could also be `undefined` instead of
@@ -59,15 +57,24 @@ const routeModule = new AppRouteRouteModule({
   relativeProjectDir: process.env.__NEXT_RELATIVE_PROJECT_DIR || '',
   resolvedPagePath: 'VAR_RESOLVED_PAGE_PATH',
   nextConfigOutput,
-  // The static import is used for initialization (methods, dynamic, etc.).
-  userland: userland as AppRouteUserlandModule,
-  // In Turbopack dev mode, also provide a getter that calls require() on every
-  // request. This re-reads from devModuleCache so HMR updates are picked up,
-  // and the async wrapper unwraps async-module Promises (ESM-only
-  // serverExternalPackages) automatically.
+  // Always use a lazy require factory so that:
+  // - In dev: devRequestTimingInternalsEnd is set before userland executes,
+  //   correctly attributing module load time to application-code rather than
+  //   framework internals.
+  // - In all modes: async modules (route files with top-level await) are
+  //   handled correctly — require() returns a Promise for such modules, which
+  //   ensureUserland() awaits before the first request is handled. Eagerly
+  //   calling require() would pass that Promise directly to the constructor
+  //   and break _initFromUserland().
+  userland: () => require('VAR_USERLAND') as typeof import('VAR_USERLAND'),
+  // In Turbopack dev mode, also provide a synchronous per-request getter so
+  // server HMR updates are picked up without re-executing the entry chunk.
+  // Using require() (synchronous) avoids adding async overhead that would be
+  // incorrectly attributed to application-code time in devRequestTiming.
   ...(process.env.TURBOPACK && process.env.__NEXT_DEV_SERVER
     ? {
-        getUserland: () => import('VAR_USERLAND'),
+        getUserland: () =>
+          require('VAR_USERLAND') as typeof import('VAR_USERLAND'),
       }
     : {}),
 })
diff --git a/packages/next/src/export/routes/app-route.ts b/packages/next/src/export/routes/app-route.ts
index 6d1545e0bb279..8fa5eb93c243b 100644
--- a/packages/next/src/export/routes/app-route.ts
+++ b/packages/next/src/export/routes/app-route.ts
@@ -88,6 +88,11 @@ export async function exportAppRoute(
   }

   try {
+    // Ensure the userland module is fully loaded before accessing it. This is
+    // required for route files that use top-level await: require() returns a
+    // Promise for async modules, so module.userland would be undefined until
+    // the Promise resolves.
+    await module.ensureUserland()
     const userland = module.userland
     // we don't bail from the static optimization for
     // metadata routes, since it's app-route we can always append /route suffix.
diff --git a/packages/next/src/server/route-modules/app-route/module.ts b/packages/next/src/server/route-modules/app-route/module.ts
index df095e5a8a3fa..f095d2481c3c2 100644
--- a/packages/next/src/server/route-modules/app-route/module.ts
+++ b/packages/next/src/server/route-modules/app-route/module.ts
@@ -173,15 +173,23 @@ export type AppRouteUserlandModule = AppRouteHandlers &
  * module from the bundled code.
  */
 export interface AppRouteRouteModuleOptions
-  extends RouteModuleOptions<AppRouteRouteDefinition, AppRouteUserlandModule> {
+  extends Omit<
+    RouteModuleOptions<AppRouteRouteDefinition, AppRouteUserlandModule>,
+    'userland'
+  > {
+  readonly userland:
+    | AppRouteUserlandModule
+    | (() => AppRouteUserlandModule | Promise<AppRouteUserlandModule>)
   readonly resolvedPagePath: string
   readonly nextConfigOutput: NextConfig['output']
   /**
-   * Optional getter that returns the live userland module. When provided (in
-   * Turbopack dev mode), it is called on every request so that server HMR
-   * updates are picked up without re-executing the entry chunk.
+   * Optional synchronous getter that returns the live userland module. When
+   * provided (Turbopack dev mode), it is called on every request so that
+   * server HMR updates are picked up without re-executing the entry chunk.
+   * Using require() instead of import() keeps this synchronous so the time
+   * spent here is not incorrectly attributed to application-code in timing.
    */
-  readonly getUserland?: () => Promise<AppRouteUserlandModule>
+  readonly getUserland?: () => AppRouteUserlandModule
 }

 /**
@@ -218,10 +226,55 @@ export class AppRouteRouteModule extends RouteModule<
   public readonly resolvedPagePath: string
   public readonly nextConfigOutput: NextConfig['output'] | undefined

-  private readonly _getUserland?: () => Promise<AppRouteUserlandModule>
-  private methods: Record<HTTP_METHOD, AppRouteHandlerFn>
-  private hasNonStaticMethods: boolean
-  private dynamic: AppRouteUserlandModule['dynamic']
+  // Set in the constructor when userland is provided as a factory. Cleared
+  // after the first access so userland is only loaded once.
+  private _userlandFactory:
+    | (() => AppRouteUserlandModule | Promise<AppRouteUserlandModule>)
+    | null
+  // Non-null while an async userland module (top-level await) is loading.
+  // ensureUserland() awaits this before the first request is handled.
+  private _pendingUserland: Promise<void> | null = null
+  // Synchronous per-request userland getter for Turbopack dev mode.
+  // Called on every request to pick up server HMR updates.
+  private readonly _getUserland?: () => AppRouteUserlandModule
+  private _methods!: Record<HTTP_METHOD, AppRouteHandlerFn>
+  private _hasNonStaticMethods!: boolean
+  private _dynamic!: AppRouteUserlandModule['dynamic']
+
+  override get userland(): AppRouteUserlandModule {
+    if (this._userlandFactory) {
+      const result = this._userlandFactory()
+      this._userlandFactory = null
+      if (result instanceof Promise) {
+        // The route file uses top-level await (async module). Store the
+        // promise so ensureUserland() can await it before the first request.
+        this._pendingUserland = result.then((mod) => {
+          this._userland = mod
+          this._pendingUserland = null
+          this._initFromUserland()
+        })
+      } else {
+        this._userland = result
+        this._initFromUserland()
+      }
+    }
+    return this._userland as AppRouteUserlandModule
+  }
+
+  /**
+   * Ensures the userland module is fully loaded before a request is handled.
+   * Required for route files that use top-level await, where require() returns
+   * a Promise instead of the module directly. Must be called before accessing
+   * `userland` in contexts where the module may not yet be resolved (e.g. the
+   * export/static-generation worker).
+   */
+  async ensureUserland(): Promise<void> {
+    // Trigger lazy loading if not yet started.
+    void this.userland
+    if (this._pendingUserland) {
+      await this._pendingUserland
+    }
+  }

   constructor({
     userland,
@@ -232,8 +285,9 @@ export class AppRouteRouteModule extends RouteModule<
     resolvedPagePath,
     nextConfigOutput,
   }: AppRouteRouteModuleOptions) {
+    const isLazy = typeof userland === 'function'
     super({
-      userland: userland!,
+      userland: (isLazy ? undefined! : userland) as AppRouteUserlandModule,
       definition,
       distDir,
       relativeProjectDir,
@@ -243,26 +297,54 @@ export class AppRouteRouteModule extends RouteModule<
     this.nextConfigOutput = nextConfigOutput
     this._getUserland = getUserland

+    if (!isLazy) {
+      this._userlandFactory = null
+      this._initFromUserland()
+    } else if (nextConfigOutput === 'export') {
+      // For output:export routes, validate constraints eagerly at module load
+      // time so that the error surfaces as a Redbox in dev (module load error)
+      // rather than being silently swallowed as a 500 response at request time.
+      this._userlandFactory = null
+      const result = userland()
+      if (result instanceof Promise) {
+        // Async module (top-level await) — defer via pending promise.
+        this._pendingUserland = result.then((mod) => {
+          this._userland = mod
+          this._pendingUserland = null
+          this._initFromUserland()
+        })
+      } else {
+        this._userland = result
+        this._initFromUserland() // throws for invalid output:export routes
+      }
+    } else {
+      this._userlandFactory = userland
+    }
+  }
+
+  private _initFromUserland(): void {
+    const userland = this._userland as AppRouteUserlandModule
+
     // Automatically implement some methods if they aren't implemented by the
     // userland module.
-    this.methods = autoImplementMethods(userland!)
+    this._methods = autoImplementMethods(userland)

     // Get the non-static methods for this route.
-    this.hasNonStaticMethods = hasNonStaticMethods(userland!)
+    this._hasNonStaticMethods = hasNonStaticMethods(userland)

     // Get the dynamic property from the userland module.
-    this.dynamic = userland!.dynamic
+    this._dynamic = userland.dynamic
     if (this.nextConfigOutput === 'export') {
-      if (this.dynamic === 'force-dynamic') {
+      if (this._dynamic === 'force-dynamic') {
         throw new Error(
-          `export const dynamic = "force-dynamic" on page "${definition.pathname}" cannot be used with "output: export". See more info here: https://nextjs.org/docs/advanced-features/static-html-export`
+          `export const dynamic = "force-dynamic" on page "${this.definition.pathname}" cannot be used with "output: export". See more info here: https://nextjs.org/docs/advanced-features/static-html-export`
         )
-      } else if (!isStaticGenEnabled(this.userland) && this.userland['GET']) {
+      } else if (!isStaticGenEnabled(userland) && userland['GET']) {
         throw new Error(
-          `export const dynamic = "force-static"/export const revalidate not configured on route "${definition.pathname}" with "output: export". See more info here: https://nextjs.org/docs/advanced-features/static-html-export`
+          `export const dynamic = "force-static"/export const revalidate not configured on route "${this.definition.pathname}" with "output: export". See more info here: https://nextjs.org/docs/advanced-features/static-html-export`
         )
       } else {
-        this.dynamic = 'error'
+        this._dynamic = 'error'
       }
     }

@@ -273,7 +355,7 @@ export class AppRouteRouteModule extends RouteModule<
       // uppercase handlers are supported.
       const lowercased = HTTP_METHODS.map((method) => method.toLowerCase())
       for (const method of lowercased) {
-        if (method in this.userland) {
+        if (method in userland) {
           Log.error(
             `Detected lowercase method '${method}' in '${
               this.resolvedPagePath
@@ -284,7 +366,7 @@ export class AppRouteRouteModule extends RouteModule<

       // Print error if the module exports a default handler, they must use named
       // exports for each HTTP method.
-      if ('default' in this.userland) {
+      if ('default' in userland) {
         Log.error(
           `Detected default export in '${this.resolvedPagePath}'. Export a named export for each HTTP method instead.`
         )
@@ -292,7 +374,7 @@ export class AppRouteRouteModule extends RouteModule<

       // If there is no methods exported by this module, then return a not found
       // response.
-      if (!HTTP_METHODS.some((method) => method in this.userland)) {
+      if (!HTTP_METHODS.some((method) => method in userland)) {
         Log.error(
           `No HTTP methods exported in '${this.resolvedPagePath}'. Export a named export for each HTTP method.`
         )
@@ -301,30 +383,27 @@ export class AppRouteRouteModule extends RouteModule<
   }

   /**
-   * Resolves the handler function for the given method.
-   *
-   * @param method the requested method
-   * @returns the handler function for the given method
+   * Returns the handler function for the given HTTP method.
+   * Must be called after ensureUserland() has resolved so that _methods is
+   * populated.
    */
-  private resolve(method: string): AppRouteHandlerFn {
-    // Ensure that the requested method is a valid method (to prevent RCE's).
+  private resolveHandler(method: string): AppRouteHandlerFn {
+    // Prevent RCE: only allow recognized HTTP methods.
     if (!isHTTPMethod(method)) return () => new Response(null, { status: 400 })

-    return autoImplementMethods(this.userland as AppRouteUserlandModule)[method]
+    return this._methods[method]
   }

   /**
-   * Like resolve(), but re-fetches the userland module on every call via the
-   * async getter. Only used in Turbopack dev mode, where server HMR disposes
-   * modules between requests. The async wrapper also unwraps async-module
-   * Promises produced by ESM-only serverExternalPackages.
+   * Returns the handler for the given method using a live userland snapshot.
+   * Used in Turbopack dev mode to pick up server HMR updates. The userland
+   * is fetched synchronously via require() so no async overhead is added.
    */
-  private async resolveWithGetter(
+  private resolveHandlerFromUserland(
     method: string,
-    getUserland: () => Promise<AppRouteUserlandModule>
-  ): Promise<AppRouteHandlerFn> {
+    userland: AppRouteUserlandModule
+  ): AppRouteHandlerFn {
     if (!isHTTPMethod(method)) return () => new Response(null, { status: 400 })
-    const userland = await getUserland()
     return autoImplementMethods(userland)[method]
   }

@@ -720,12 +799,25 @@ export class AppRouteRouteModule extends RouteModule<
     req: NextRequest,
     context: AppRouteRouteHandlerContext
   ): Promise<Response> {
-    // Get the handler function for the given method. In Turbopack dev mode,
-    // use resolveWithGetter() to re-fetch the live userland on every request
-    // In all other modes, resolve() is synchronous.
-    const handler = this._getUserland
-      ? await this.resolveWithGetter(req.method, this._getUserland)
-      : this.resolve(req.method)
+    // Ensure userland is fully loaded (handles async modules with top-level
+    // await, where require() returns a Promise instead of the module).
+    await this.ensureUserland()
+
+    // In Turbopack dev mode, fetch the live userland module on every request
+    // via the synchronous require() getter so server HMR updates are reflected
+    // immediately. This is cheap — it is just a devModuleCache lookup.
+    // For routes with top-level await, require() may still return a Promise
+    // (async module); in that case fall back to the already-resolved
+    // _userland from ensureUserland() above.
+    const rawLiveUserland = this._getUserland?.()
+    const liveUserland =
+      rawLiveUserland instanceof Promise
+        ? undefined
+        : (rawLiveUserland as AppRouteUserlandModule | undefined)
+
+    const handler = liveUserland
+      ? this.resolveHandlerFromUserland(req.method, liveUserland)
+      : this.resolveHandler(req.method)

     // Get the context for the static generation.
     const staticGenerationContext: WorkStoreContext = {
@@ -735,8 +827,12 @@ export class AppRouteRouteModule extends RouteModule<
       previouslyRevalidatedTags: [],
     }

+    // Use the live userland (if available) for per-request values so HMR
+    // changes to fetchCache, dynamic, etc. are also picked up.
+    const userland = liveUserland ?? (this._userland as AppRouteUserlandModule)
+
     // Add the fetchCache option to the renderOpts.
-    staticGenerationContext.renderOpts.fetchCache = this.userland.fetchCache
+    staticGenerationContext.renderOpts.fetchCache = userland.fetchCache

     const actionStore: ActionStore = {
       isAppRoute: true,
@@ -769,8 +865,12 @@ export class AppRouteRouteModule extends RouteModule<
         this.workUnitAsyncStorage.run(requestStore, () =>
           this.workAsyncStorage.run(workStore, async () => {
             // Check to see if we should bail out of static generation based on
-            // having non-static methods.
-            if (hasNonStaticMethods(this.userland)) {
+            // having non-static methods. Use live userland when available so
+            // HMR changes to exported HTTP methods are reflected immediately.
+            const hasNonStatic = liveUserland
+              ? hasNonStaticMethods(liveUserland)
+              : this._hasNonStaticMethods
+            if (hasNonStatic) {
               if (workStore.isStaticGeneration) {
                 const err = new DynamicServerError(
                   'Route is configured with methods that cannot be statically generated.'
@@ -785,8 +885,11 @@ export class AppRouteRouteModule extends RouteModule<
             // proxying it in certain circumstances based on execution type and configuration
             let request = req

+            // Use the live dynamic value when available so HMR changes to
+            // `export const dynamic` are reflected immediately.
+            const dynamic = liveUserland?.dynamic ?? this._dynamic
+
             // Update the static generation store based on the dynamic property.
-            const { dynamic } = this.userland
             switch (dynamic) {
               case 'force-dynamic': {
                 // Routes of generated paths should be dynamic
diff --git a/packages/next/src/server/route-modules/route-module.ts b/packages/next/src/server/route-modules/route-module.ts
index 006231c1408a6..57cbd00a6d678 100644
--- a/packages/next/src/server/route-modules/route-module.ts
+++ b/packages/next/src/server/route-modules/route-module.ts
@@ -108,10 +108,13 @@ export abstract class RouteModule<
 > {
   /**
    * The userland module. This is the module that is exported from the user's
-   * code. This is marked as readonly to ensure that the module is not mutated
-   * because the module (when compiled) only provides getters.
+   * code. Exposed as a getter so subclasses can override with lazy loading.
    */
-  public readonly userland: Readonly<U>
+  protected _userland: Readonly<U>
+
+  get userland(): Readonly<U> {
+    return this._userland
+  }

   /**
    * The definition of the route.
@@ -135,7 +138,7 @@ export abstract class RouteModule<
     distDir,
     relativeProjectDir,
   }: RouteModuleOptions<D, U>) {
-    this.userland = userland
+    this._userland = userland
     this.definition = definition
     this.isDev = !!process.env.__NEXT_DEV_SERVER
     this.distDir = distDir

PATCH

echo "Patch applied successfully."
