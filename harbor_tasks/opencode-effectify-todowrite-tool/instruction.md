# Effectify TodoWriteTool with Todo.Service

## Problem

The `TodoWriteTool` in `packages/opencode/src/tool/todo.ts` is currently built using `Tool.define(...)`, which creates a plain static tool definition. It calls `Todo.update(...)` directly as a namespace function, bypassing the Effect dependency injection system.

This means `TodoWriteTool` does not declare `Todo.Service` as a dependency — it reaches into the `Todo` namespace and calls the convenience wrapper directly. This breaks the effectification pattern used by other tools and makes the tool harder to test in isolation.

## Expected Behavior

`TodoWriteTool` should be converted to use `Tool.defineEffect(...)` so that:

1. It declares `Todo.Service` as an Effect requirement
2. It yields the service inside `Effect.gen` and calls methods on the yielded instance
3. The `ToolRegistry` layer correctly provides `Todo.Service` (and its default layer) to the tool
4. All existing type checks and tests continue to pass

## Files to Look At

- `packages/opencode/src/tool/todo.ts` — the tool definition to convert
- `packages/opencode/src/tool/tool.ts` — contains both `Tool.define` and `Tool.defineEffect` APIs
- `packages/opencode/src/tool/registry.ts` — wires up all tools; needs to provide the new dependency
- `packages/opencode/src/session/todo.ts` — the `Todo` service whose `defaultLayer` may need to be exported
- `packages/opencode/test/session/prompt-effect.test.ts` — test layer setup that may need updating
- `packages/opencode/test/session/snapshot-tool-race.test.ts` — test layer setup that may need updating
