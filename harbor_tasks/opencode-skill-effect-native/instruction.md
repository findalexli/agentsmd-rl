# Bug: Skill service bypasses Effect dependency injection

## Context

The `Skill` service in `packages/opencode/src/skill/index.ts` manages loading and discovery of skill definitions (SKILL.md files) from various directories. It composes with `Discovery`, `Config`, and `Bus` services.

## Problem

The internal helper functions (`add`, `scan`, and the main skill-loading routine) are written as plain `async` functions that bridge to Effect only through `Effect.promise`. This means:

1. **Config and Bus are accessed through async facades** (`Config.get()`, `Config.directories()`, `Bus.publish(...)`) rather than being yielded from the Effect context. The service's layer type does not declare them as dependencies, so the Effect runtime cannot manage their lifecycle correctly.

2. **The `scan` helper uses `.then()` / `.catch()` chains** instead of Effect's error channel, making error handling inconsistent with the rest of the codebase's Effect patterns.

3. **`discovery.pull()` results are consumed via `Effect.runPromise`** inside the loading routine rather than being yielded as native Effect values.

4. **The layer's `InstanceState.make` closure wraps the entire loading routine in a single `Effect.promise`**, preventing granular resource tracking and error isolation.

## Expected Behavior

- The helper functions should be native Effect generators (using `Effect.fnUntraced`).
- `Config.Service` and `Bus.Service` should be yielded directly in the layer and threaded through as parameters.
- The layer type should explicitly declare `Config.Service` and `Bus.Service` as dependencies.
- `defaultLayer` should provide the corresponding default layers for these services.

## Files to Modify

- `packages/opencode/src/skill/index.ts`
