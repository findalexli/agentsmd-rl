# Add staleReloadMode Feature to TanStack Router

## Problem Description

TanStack Router currently has a fixed stale-while-revalidate behavior: when a route with stale loader data is revisited, the router immediately renders with the stale data and reloads fresh data in the background. There is no way to configure the router to wait for the fresh data before rendering.

This causes issues when:
- You need to ensure users always see the latest data before interacting with a page
- Stale data could lead to incorrect decisions or confusion
- You want to show a loading state during revalidation instead of stale data

## Expected Behavior

Implement a `staleReloadMode` feature that allows configuring how stale successful loader data is revalidated:

1. **`'background'` (default)**: Current behavior - render immediately with stale data while reloading in the background
2. **`'blocking'`**: Wait for the stale loader reload to complete before resolving navigation and rendering

The feature should support two levels of configuration:

1. **Router-level** (`defaultStaleReloadMode`): Set the default for all routes
   ```ts
   const router = createRouter({
     routeTree,
     defaultStaleReloadMode: 'blocking', // or 'background'
   })
   ```

2. **Loader-level** (`loader.staleReloadMode`): Override the default for a specific route
   ```ts
   export const Route = createFileRoute('/posts')({
     loader: {
       handler: () => fetchPosts(),
       staleReloadMode: 'blocking', // overrides router default
     },
   })
   ```

## Type Requirements

The implementation requires the following types to be defined and exported:

- **LoaderStaleReloadMode**: A union type with values `'background'` and `'blocking'`, defined as:
  ```ts
  export type LoaderStaleReloadMode = 'background' | 'blocking'
  ```

- **RouteLoaderEntry**: A type that represents the loader configuration, supporting both function and object forms

- **RouteLoaderObject**: A type for object-form loaders with a `handler` property and optional `staleReloadMode` property:
  ```ts
  staleReloadMode?: LoaderStaleReloadMode
  ```

- **ResolveRouteLoaderFn**: A helper type for resolving loader functions

## Behavioral Requirements

When implementing the loader execution logic:

1. The loader must accept both a function form and an object form with a `handler` property. The object form must be handled using this exact pattern:
   ```ts
   typeof routeLoader === 'function' ? routeLoader : routeLoader?.handler
   ```

2. A flag named `shouldReloadInBackground` must be used to track whether to reload in background mode.

3. When checking for early return with stale data, the code must verify both `prevMatch.status === 'success'` AND `shouldReloadInBackground` together before returning early.

4. The `defaultStaleReloadMode` option must be added to `RouterOptions` interface.

## Framework Integration

The framework-specific `fileRoute.ts` files (in react-router, solid-router, and vue-router packages) must import and use `RouteLoaderEntry` instead of `RouteLoaderFn` for loader type definitions.

## Acceptance Criteria

- [ ] Types `LoaderStaleReloadMode` and `RouteLoaderEntry` are exported from `packages/router-core/src/index.ts`
- [ ] `RouteLoaderObject` type with `staleReloadMode` property is defined in `route.ts`
- [ ] `ResolveRouteLoaderFn` type helper is defined in `route.ts`
- [ ] `LoaderStaleReloadMode` type is defined as `'background' | 'blocking'` in `route.ts`
- [ ] `defaultStaleReloadMode` option is added to `RouterOptions`
- [ ] Object-form loader handler extraction pattern is implemented in `load-matches.ts`
- [ ] `shouldReloadInBackground` flag is used in `load-matches.ts`
- [ ] Stale reload mode is respected when returning early with stale data
- [ ] All framework `fileRoute.ts` files use `RouteLoaderEntry`
- [ ] All existing tests continue to pass
- [ ] TypeScript compilation succeeds
