# Refactor @remix-run/interaction to use `this` context for Interactions

## Problem

The `@remix-run/interaction` package's Interaction setup API is cumbersome. Each interaction function receives `(target: EventTarget, signal: AbortSignal)` as separate parameters, leading to awkward patterns where interactions must call `on(target, signal, {...})` to forward both the target and signal. The helper functions `capture()` and `listenWith()` add unnecessary API surface for simple event listener options. The `on()` function has an overloaded signature that accepts an optional `AbortSignal` as its second argument, adding complexity.

Additionally, there is no centralized error handling for listener errors — each consumer must individually wrap listeners with try/catch.

## Expected Behavior

1. **Interaction context via `this`**: Interaction setup functions should receive context through `this` (using TypeScript's `this` parameter syntax). The context should provide `this.target`, `this.signal`, `this.raise` (error handler), and `this.on()` (a helper to create containers that automatically propagate signal and error handling).

2. **Inline descriptor objects**: Remove `capture()` and `listenWith()` helper functions. Consumers should use inline descriptor objects that extend `AddEventListenerOptions` directly (e.g., `{ capture: true, listener(event) { ... } }`).

3. **Simplified `on()` function**: Remove the `AbortSignal` overload from `on()`. It should be a simple shorthand for `createContainer` without options.

4. **Container error handling**: `createContainer` should accept an options object (`{ signal?, onError? }`) instead of a bare `AbortSignal`. The `onError` callback handles both synchronous and asynchronous listener errors.

5. **Update all interaction submodules** (`form.ts`, `keys.ts`, `popover.ts`, `press.ts`) to use the new `this` context pattern.

6. After making the code changes, update the package's README and CHANGELOG to reflect the new API. The documentation should show the new descriptor syntax, the `this` context pattern for custom interactions, and the updated `createContainer` options.

## Files to Look At

- `packages/interaction/src/lib/interaction.ts` — core library with `on`, `createContainer`, `defineInteraction`, and type definitions
- `packages/interaction/src/index.ts` — package exports
- `packages/interaction/src/lib/interactions/form.ts` — form reset interaction
- `packages/interaction/src/lib/interactions/keys.ts` — keyboard interactions
- `packages/interaction/src/lib/interactions/popover.ts` — popover interaction
- `packages/interaction/src/lib/interactions/press.ts` — press/long-press interaction
- `packages/interaction/README.md` — package documentation
- `packages/interaction/CHANGELOG.md` — changelog
