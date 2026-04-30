# Bug: Skill service has incorrect runtime behavior

## Context

The `Skill` service in `packages/opencode/src/skill/index.ts` manages loading and discovery of skill definitions (SKILL.md files) from various directories. It composes with `Discovery`, `Config`, and `Bus` services.

## Symptom

When the Effect runtime manages the Skill service layer, the following runtime issues occur:

1. **Helpers use async/await**: The `add` and `scan` helper functions are declared as `async` functions instead of native Effect generators. This means `Config.get()`, `Config.directories()`, and `Bus.publish(...)` are called through async facades at runtime, rather than being yielded from the Effect context. When the layer is torn down, the runtime cannot correctly manage the lifecycle of these dependencies.

2. **Error handling via Promise chains**: The `scan` helper uses `.then()` / `.catch()` chains instead of Effect's error channel, so errors propagate inconsistently with the rest of the codebase's Effect patterns.

3. **Effect.runPromise bridge**: `discovery.pull()` results are consumed via `Effect.runPromise` inside the loading routine rather than being yielded natively as Effect values.

4. **Monolithic Effect.promise wrapper**: `InstanceState.make` wraps the entire loading routine in a single `Effect.promise`, preventing granular resource tracking and error isolation.

## Observed Failures

- `Effect.fn`, `Effect.fnUntraced`, or `Effect.gen` (any of these) is not used for `add`, `scan`, or `loadSkills` helpers
- `Config.get()` or `Config.directories()` static calls are still present in the code
- `Effect.runPromise` is still used to bridge discovery results
- A monolithic `Effect.promise(() => loadSkills(...))` wrapper is present
- `.then()` promise chains exist in the code
- `Promise.all` is used instead of `Effect.forEach` or `Effect.all`
- `yield* Config.Service` and `yield* Bus.Service` are not used
- `Layer.provide(Config.` and `Layer.provide(Bus.` are not present in `defaultLayer`
- The layer type does not include `Config.Service` or `Bus.Service` in its dependency list

## Expected Runtime Behavior

- Helper functions (`add`, `scan`, `loadSkills`) run as native Effect generators
- `Config.Service` and `Bus.Service` are yielded from the Effect context and threaded through as parameters
- `discovery.pull()` results are yielded natively
- `defaultLayer` provides layers for `Discovery`, `Config`, and `Bus` alongside each other
- Error reporting still publishes `Session.Event.Error` events to the bus
- Core patterns like `Skill.state` (the InstanceState accessor) remain intact

## Codebase Standards (from AGENTS.md)

- No `try/catch` blocks — use `Effect.tryPromise` or `Effect.catch` instead
- No `any` type annotations — use specific types
- No `fs/promises` imports — use `FileSystem.FileSystem` instead
- No raw `fetch()` calls — use `HttpClient.HttpClient` instead

## Files to Inspect

- `packages/opencode/src/skill/index.ts`
- Related: `packages/opencode/src/skill/discovery.ts`, `packages/opencode/test/skill/discovery.test.ts`, `packages/opencode/test/skill/skill.test.ts`, `packages/opencode/test/tool/skill.test.ts`