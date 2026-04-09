# Route Handlers: Fix devRequestTiming attribution and Turbopack server HMR staleness

## Problem

Several issues exist in `AppRouteRouteModule` that interact with dev request timing and Turbopack server HMR:

1. **Incorrect timing attribution**: The app-route template statically imports the userland module at the top level (`import * as userland from 'VAR_USERLAND'`), which means the module's load time is included in the framework's startup overhead. The `devRequestTimingInternalsEnd` timestamp does not correctly capture the framework-to-application boundary.

2. **Stale route handlers after Turbopack server HMR**: After a Turbopack server HMR update, the route module's `getUserland` getter uses `import()` (async), which introduces latency that gets incorrectly attributed to application-code time in `devRequestTiming`. The async overhead should not be present since `require()` from `devModuleCache` is a synchronous lookup.

3. **Route handlers with top-level await break**: When a route file uses `top-level await`, `require()` returns a Promise instead of the module directly. The module must handle this case before the first request is processed, but currently there is no mechanism to await the pending module resolution.

4. **`output: export` validation deferred to request time**: With a lazy factory, validation errors (e.g. `dynamic = "force-dynamic"` on an exported route) would be deferred to request time, returning a 500 instead of surfacing as a Redbox in dev.

## Expected Behavior

- Userland should be loaded lazily so `devRequestTimingInternalsEnd` correctly attributes module load time to application code
- The HMR getter should be synchronous (`require()`) to avoid async overhead in timing
- Route files with top-level await should be handled gracefully before the first request
- For `output: export` routes, validation errors should still throw eagerly at module load time
- The base `RouteModule` class should support subclass overriding of userland access for lazy loading

## Files to Look At

- `packages/next/src/build/templates/app-route.ts` — Template that instantiates `AppRouteRouteModule` with userland
- `packages/next/src/server/route-modules/app-route/module.ts` — The `AppRouteRouteModule` class: options interface, constructor, handler resolution, request handling
- `packages/next/src/server/route-modules/route-module.ts` — Base `RouteModule` class that owns the `userland` property
- `packages/next/src/export/routes/app-route.ts` — Export route handler that accesses `module.userland`
