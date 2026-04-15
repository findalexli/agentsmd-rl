# Effectify TodoWriteTool with Todo.Service

## Problem

The `TodoWriteTool` in `packages/opencode/src/tool/todo.ts` is currently built using `Tool.define(...)`, which creates a plain static tool definition. It calls `Todo.update(...)` directly as a namespace function, bypassing the Effect dependency injection system.

This means `TodoWriteTool` does not declare `Todo.Service` as a dependency — it reaches into the `Todo` namespace and calls the convenience wrapper directly. This breaks the effectification pattern used by other tools and makes the tool harder to test in isolation.

## Required Changes

Convert `TodoWriteTool` to use the Effect-based pattern with these specific requirements:

1. **Use `Tool.defineEffect(...)`** instead of `Tool.define(...)` to declare `Todo.Service` as a dependency

2. **Use `Effect.gen(function* () { ... })`** for composition inside the tool implementation

3. **Yield the service with `yield* Todo.Service`** to obtain the Todo service instance inside the Effect generator

4. **Export `defaultLayer`** from `packages/opencode/src/session/todo.ts` — the instruction must contain `export const defaultLayer`

5. **Provide `Todo.defaultLayer`** in `packages/opencode/src/tool/registry.ts` so the `ToolRegistry` layer makes the service available to the tool

6. All existing type checks and tests must continue to pass

## Files to Look At

- `packages/opencode/src/tool/todo.ts` — the tool definition
- `packages/opencode/src/tool/tool.ts` — contains `Tool.define` and `Tool.defineEffect` APIs
- `packages/opencode/src/tool/registry.ts` — wires up all tools
- `packages/opencode/src/session/todo.ts` — the `Todo` service
- Test files in `packages/opencode/test/` that verify layer setup
