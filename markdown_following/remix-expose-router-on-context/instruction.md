# Expose Router on Request Context

The `@remix-run/fetch-router` package's `RequestContext` class has no built-in way to access the owning `Router` instance. Framework helpers that need router state (e.g., for internal frame resolution) currently require app-level middleware to store the router manually in `context.storage`.

## Symptom

In the bookstore demo, the `render()` helper retrieves the router using:

```ts
let router = context.storage.get(routerStorageKey)
```

This requires a separate `router-storage.ts` utility file that creates a typed storage key, plus middleware that stores the router on every request:

```ts
middleware.unshift((context, next) => {
  context.storage.set(routerStorageKey, router)
  return next()
})
```

This is boilerplate that every consumer of fetch-router would need to replicate. The `RequestContext` should expose the router directly.

## Desired Behavior

1. **`context.router` getter**: The `RequestContext` class should have a `router` property. During a `router.fetch()` call, the context should provide access to the `Router` instance that is handling the request. Accessing `context.router` when no router has been assigned should throw an error containing the phrase "No router found" so the failure mode is clear.

2. **Router assignment during fetch**: When `createRouter()` dispatches a request via its `fetch()` method, it should assign the router to the newly created request context before the request is handled.

3. **Bookstore demo cleanup**: The bookstore demo should use the new `context.router` API instead of the storage-key workaround. The `router-storage.ts` file and the middleware that stores the router should be removed.

## Constraints

- Follow the monorepo's established code conventions documented in `AGENTS.md` at the repository root.
- Existing tests in the `@remix-run/fetch-router` package must continue to pass.
- TypeScript type checking (`pnpm --filter @remix-run/fetch-router run typecheck`) must pass.
- The `RequestContext` class uses `#private` fields for internal state — follow this pattern.

## Code Style Requirements

This repository uses Prettier for code formatting and ESLint (`pnpm lint`) for static analysis. Prettier settings: printWidth 100, no semicolons, single quotes, spaces not tabs. Run `pnpm run format` before finishing.
