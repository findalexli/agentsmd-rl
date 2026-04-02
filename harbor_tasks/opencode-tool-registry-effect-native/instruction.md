# ToolRegistry service bypasses Effect dependency graph via async facades

## Context

The `ToolRegistry` service in `packages/opencode/src/tool/registry.ts` is responsible for discovering, filtering, and initializing tools for the AI agent. It uses Effect for structured concurrency and dependency injection.

The `Plugin` service in `packages/opencode/src/plugin/index.ts` manages plugin lifecycle and hooks.

## Problem

The ToolRegistry's `layer` definition has several issues related to improper Effect usage:

1. **Async facade leakage in state init**: Inside the `InstanceState.make` closure, the code wraps config directory scanning and plugin listing in a single `Effect.promise(async () => { ... })` block. Within that block, it calls `Config.directories()`, `Config.waitForDependencies()`, and `Plugin.list()` — all async convenience facades. Since this code is already inside an `Effect.gen` generator, it should yield the `Config.Service` and `Plugin.Service` directly and call their methods through the Effect protocol. This breaks Effect's dependency tracking and error channels.

2. **`all()` helper is async instead of effectful**: The `all()` function that assembles the tool list is defined as a plain `async function` that calls `Config.get()` (the async facade). It should be an Effect function that yields the config service.

3. **`tools()` uses Promise.all instead of Effect.forEach**: The `tools` method wraps `Promise.all(allTools.filter(...).map(async ...))` inside `Effect.promise`. Each tool init and plugin trigger call should be structured as Effect operations using `Effect.forEach` with concurrency, not a promise-based map.

4. **Missing layer composition**: Because the ToolRegistry should yield `Config.Service` and `Plugin.Service` directly in its generators, the layer needs proper composition that provides these dependencies. The `Plugin` module's layer also needs its `defaultLayer` to be accessible for this composition.

5. **Missing return type on tools facade**: The public `tools()` async function lacks an explicit return type annotation, which causes circular type inference issues with some tool types.

## Files to modify

- `packages/opencode/src/tool/registry.ts` — the main ToolRegistry service
- `packages/opencode/src/plugin/index.ts` — the Plugin module (layer export visibility)

## Guidance

- Refer to `packages/opencode/AGENTS.md` for the project's Effect conventions, especially the rules about yielding Effect services vs using async facades.
- The `InstanceState.make` closure is an Effect generator — use `yield*` to call service methods.
- For concurrent tool initialization, use `Effect.forEach` with `{ concurrency: "unbounded" }`.
- The layer graph needs `Config.defaultLayer` and `Plugin.defaultLayer` provided to the ToolRegistry layer.
