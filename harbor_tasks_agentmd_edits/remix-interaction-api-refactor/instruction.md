# Refactor Interaction API to use `this` context pattern

## Problem

The `@remix-run/interaction` package's API for defining custom interactions currently requires passing `target` and `signal` as function arguments:

```ts
function MyInteraction(target: EventTarget, signal: AbortSignal) {
  on(target, signal, { ... })
}
```

This pattern is verbose and requires threading the signal through every `on()` call manually. The `on()` function also has an overload that accepts an `AbortSignal` as a second argument, adding API surface complexity.

Additionally, the `capture()` and `listenWith()` helper functions for creating event listener descriptors add unnecessary indirection. Descriptors should extend `AddEventListenerOptions` directly with a `listener` property instead.

Finally, there's no way to handle errors thrown by listeners centrally — each listener must handle its own errors.

## Expected Behavior

1. **Interaction setup functions** should use `this` context instead of arguments. A new `Interaction` interface should provide `this.target`, `this.signal`, `this.raise` (error handler), and `this.on()` (creates a container with automatic signal/error propagation).

2. **Remove `capture()` and `listenWith()`** helper functions. Descriptors should be plain objects extending `AddEventListenerOptions` with a `listener` property directly (e.g., `{ capture: true, listener(event) { ... } }`).

3. **Simplify `on()`** — remove the signal overload. `on(target, listeners)` should be a simple shortcut that returns a dispose function. For signal-based cleanup, use `createContainer` with options.

4. **`createContainer`** should accept an options object (`{ signal?, onError? }`) instead of a bare `AbortSignal`. The `onError` handler should catch both sync and async listener errors.

5. **Update all built-in interactions** (form, keys, popover, press) to use the new `this` context pattern.

6. After making the code changes, update the package's documentation (README.md, CHANGELOG.md) to reflect the new API. The README should show the updated usage patterns and the CHANGELOG should document the breaking changes.

## Files to Look At

- `packages/interaction/src/lib/interaction.ts` — core module with types, `on`, `createContainer`, descriptors, and interaction binding logic
- `packages/interaction/src/index.ts` — public exports
- `packages/interaction/src/lib/interactions/` — built-in interaction implementations (form, keys, popover, press)
- `packages/interaction/README.md` — package documentation with API examples
- `packages/interaction/CHANGELOG.md` — changelog for the package
