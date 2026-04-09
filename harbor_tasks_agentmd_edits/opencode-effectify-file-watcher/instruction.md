# Refactor FileWatcher to Effect Service

## Problem

The `FileWatcher` in `packages/opencode/src/file/watcher.ts` currently uses the legacy `Instance.state()` pattern for lifecycle management. This approach has several issues:

1. No proper cleanup on instance disposal - subscriptions may leak
2. No ALS (AsyncLocalStorage) context preservation when native C++ callbacks fire from `@parcel/watcher`
3. Hard to test - requires mocking flags and modules
4. Doesn't follow the project's Effect patterns for services

The file watcher needs to be converted to an Effect `ServiceMap.Service` with proper scoped lifecycle management, similar to how `QuestionService`, `PermissionService`, and `ProviderAuthService` are implemented.

## What You Need to Do

1. **Refactor `FileWatcher` to `FileWatcherService`**:
   - Convert from namespace with `Instance.state()` to a `ServiceMap.Service` class with a `static readonly layer`
   - Use `Effect.gen` for composition
   - Use `Effect.addFinalizer` for cleanup (unsubscribe from watchers)
   - Read configuration via `Effect.promise()` wrappers
   - Update flags to use `Effect.Config` pattern (if they don't already)

2. **Add ALS context preservation**:
   - Use `Instance.bind()` for the native watcher callback to preserve AsyncLocalStorage context
   - This ensures `Bus.publish` and other instance-scoped operations work correctly when callbacks fire from C++

3. **Update service registration**:
   - Add `FileWatcherService` to `InstanceServices` union in `src/effect/instances.ts`
   - Add `Layer.fresh(FileWatcherService.layer)` to the `lookup()` function
   - Update `src/project/bootstrap.ts` to call the service via `runPromiseInstance()`

4. **Update documentation**:
   - The `packages/opencode/AGENTS.md` file documents Effect patterns used in this codebase
   - After making the changes, update AGENTS.md to document:
     - The Instance-scoped Effect services pattern
     - The `Instance.bind()` pattern for native callbacks
     - Any other relevant patterns you used (check the existing docs for structure)

## Key Files

- `packages/opencode/src/file/watcher.ts` - Main file to refactor (remove `Instance.state`, create `FileWatcherService`)
- `packages/opencode/src/effect/instances.ts` - Add service to union and layer
- `packages/opencode/src/project/bootstrap.ts` - Update initialization call
- `packages/opencode/src/project/instance.ts` - May need `Instance.bind()` method
- `packages/opencode/src/flag/flag.ts` - May need to convert flags to `Config.boolean()`
- `packages/opencode/AGENTS.md` - Document the patterns used

## Notes

- The `InstanceContext` service provides `directory` and `project` - use it instead of `Instance.*` globals inside the layer
- Look at `QuestionService`, `PermissionService`, or `ProviderAuthService` as reference implementations
- The native watcher callback needs `Instance.bind()` because it fires from C++ outside the normal JS async context
- Tests should be able to run the service with `ConfigProvider.layer` overrides instead of module mocking
