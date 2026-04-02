# Bug: Vcs service uses Effect.promise bridge instead of native Effect spawner

## Context

The `packages/opencode/src/project/vcs.ts` file implements the Vcs service, which tracks the current git branch and publishes events when it changes.

Other services in the codebase (Snapshot, Worktree) have already been migrated to use Effect's native `ChildProcessSpawner` for running child processes. However, the Vcs service still uses an async `git()` utility from `@/util/git` and wraps calls to it with `Effect.promise`. This breaks the fully-native Effect pattern:

- `Effect.promise` bypasses Effect's scope and interruption model — if the scope is closed while git is running, the process isn't cleaned up.
- Tracing doesn't propagate through the `Effect.promise` boundary, so `git rev-parse` calls in Vcs don't appear in Effect traces the way they do in other services.
- The layer's dependency signature doesn't reflect that it spawns child processes, making it impossible to swap in a test spawner.

## What needs to change

Migrate the Vcs service to use `ChildProcessSpawner` from `effect/unstable/process` instead of the async `git()` utility, following the same pattern used by Snapshot and Worktree services. The `@/effect/cross-spawn-spawner` module provides the concrete implementation layer.

Relevant files:
- `packages/opencode/src/project/vcs.ts` — the service to migrate
- `packages/opencode/src/effect/cross-spawn-spawner.ts` — the concrete spawner implementation
- `packages/opencode/src/util/git.ts` — the old async utility (should no longer be imported by vcs.ts)

The service's public API (`init()`, `branch()`, events) must remain unchanged.
