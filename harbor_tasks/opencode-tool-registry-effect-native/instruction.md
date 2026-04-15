# ToolRegistry Service: Effect Dependency Graph Refactoring

## Context

The `ToolRegistry` service in `packages/opencode/src/tool/registry.ts` discovers, filters, and initializes tools for the AI agent. It uses the Effect library for structured concurrency and dependency injection.

The `Plugin` service in `packages/opencode/src/plugin/index.ts` manages plugin lifecycle and hooks.

## Problem

The ToolRegistry's layer definition bypasses Effect's dependency tracking by using async convenience facades instead of yielding services through the Effect protocol. This breaks structured concurrency, error channels, and dependency injection for `Config.Service` and `Plugin.Service`.

Symptoms include:
- Config and plugin services are obtained via module-level async calls instead of Effect dependency injection
- Concurrent tool initialization uses `Promise.all` instead of Effect concurrency primitives
- Helper functions that should be part of the Effect layer are plain async functions

## Requirements

The refactored code must satisfy all of the following:

1. **No async facades in state initialization**: The `InstanceState.make` closure must not call module-level async facades such as `Config.directories()`, `Config.waitForDependencies()`, or `Plugin.list()` directly.

2. **`all` helper must be Effectful**: Any function that assembles the tool list and calls `Config.get()` or equivalent must be defined as an Effect function (using `Effect.fn` or `Effect.gen`), not a plain `async function`.

3. **Effect concurrency for tool init**: Concurrent tool initialization must not use `Promise.all`. It must use Effect concurrency primitives (`Effect.forEach` or `Effect.all`).

4. **Services yielded via Effect protocol**: The layer generator must obtain `Config.Service` and `Plugin.Service` through the Effect dependency graph (using `yield*` on the service references), not through async facade calls.

5. **Effect.fn usage**: The registry code must use `Effect.fn` for named/traced effect operations at least 3 times.

6. **Effect.fnUntraced usage**: The registry code must use `Effect.fnUntraced` for internal or anonymous helper effects.

7. **Exported defaultLayer in Plugin**: The `Plugin` module must export a `defaultLayer` constant.

8. **Exported defaultLayer in ToolRegistry**: The `ToolRegistry` module must export a `defaultLayer` constant that composes `Config.defaultLayer` and `Plugin.defaultLayer`.

9. **Explicit return type on tools facade**: The public `tools()` async function must have an explicit return type annotation.

10. **Typecheck passes**: The repository's TypeScript typecheck (`bunx turbo typecheck`) must pass with no errors.

11. **Tool registry tests pass**: The test suite `bun test test/tool/registry.test.ts` must pass.

## Files to examine

- `packages/opencode/src/tool/registry.ts` — ToolRegistry service
- `packages/opencode/src/plugin/index.ts` — Plugin module
- `packages/opencode/AGENTS.md` — Project Effect conventions

## Guidance

Refer to `packages/opencode/AGENTS.md` for the project's Effect conventions. The rules about yielding Effect services versus using async facades are important for this refactoring.