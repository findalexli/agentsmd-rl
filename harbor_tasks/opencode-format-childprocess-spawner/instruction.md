# Format service uses raw Process.spawn instead of Effect ChildProcessSpawner

## Problem

The `Format` service in `packages/opencode/src/format/index.ts` spawns child processes using the internal `Process` utility (`../util/process`) instead of the Effect-native child process service. This is inconsistent with the codebase's Effect migration strategy — effectified services should yield Effect services rather than dropping down to ad-hoc platform APIs.

Specifically:

1. `formatFile` is an `async function` returning a `Promise` instead of returning an `Effect`. Because of this, the caller in the `file` method has to wrap it with `Effect.promise()` rather than composing it natively.

2. `formatFile` uses `Process.spawn(...)` to run formatter commands. The project already has an effectified child process spawner (see `src/effect/cross-spawn-spawner.ts`) that should be used instead.

3. Error handling uses `try`/`catch` rather than Effect's error combinators.

4. The `defaultLayer` does not provide the spawner layer, so it can't be used even if the code were switched.

## Relevant files

- `packages/opencode/src/format/index.ts` — the Format service
- `packages/opencode/src/effect/cross-spawn-spawner.ts` — the existing effectified spawner
- `packages/opencode/test/format/format.test.ts` — the format test (will need layer updates)
- `packages/opencode/specs/effect-migration.md` — migration roadmap (update the checklist)
- `packages/opencode/AGENTS.md` — documents the preferred Effect patterns for this package
