# Effectify FileWatcherService

## Problem

The current `FileWatcher` in `src/file/watcher.ts` uses the legacy `Instance.state()` pattern for per-directory lifecycle management. This pattern:
- Uses async/await instead of Effect composition
- Relies on static `Flag.truthy()` reads that can't be overridden in tests
- Doesn't properly capture AsyncLocalStorage context for native addon callbacks
- Isn't integrated with the `Instances` LayerMap for proper resource cleanup

Additionally, native callbacks from `@parcel/watcher` fire outside the instance async context, causing `Bus.publish` and `Instance.state()` calls to fail silently or read incorrect values.

## Expected Behavior

Convert `FileWatcher` to a proper Effect service:

1. **Service Definition**: Define `FileWatcherService` as a `ServiceMap.Service` with a static `layer` property
2. **Layer Registration**: Add it to `InstanceServices` union in `src/effect/instances.ts` and include in `Layer.mergeAll()`
3. **Instance.bind**: Add `Instance.bind(fn)` method that captures the current ALS context for native callbacks
4. **Effect.Config Flags**: Migrate `OPENCODE_EXPERIMENTAL_FILEWATCHER` and `OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER` from `truthy()` to `Config.boolean().pipe(Config.withDefault(false))`
5. **Bootstrap Update**: Change `bootstrap.ts` to use `runPromiseInstance(FileWatcherService.use((s) => s.init()))`
6. **AGENTS.md Documentation**: Add sections documenting:
   - Instance-scoped Effect services pattern
   - `Instance.bind` for ALS context in native callbacks
   - Flag → Effect.Config migration pattern

## Files to Look At

- `src/file/watcher.ts` — Main FileWatcher implementation to convert
- `src/effect/instances.ts` — Add to InstanceServices and LayerMap
- `src/project/instance.ts` — Add Instance.bind method
- `src/flag/flag.ts` — Convert flags to Effect.Config
- `src/project/bootstrap.ts` — Update initialization pattern
- `packages/opencode/AGENTS.md` — Add documentation for new patterns

## Key Patterns

### Service Definition
```typescript
export class FileWatcherService extends ServiceMap.Service<FileWatcherService, FileWatcherService.Service>()(
  "@opencode/FileWatcher",
) {
  static readonly layer = Layer.effect(FileWatcherService, Effect.gen(function* () {
    // implementation
  }))
}
```

### Instance.bind
```typescript
const cb = Instance.bind((err, evts) => {
  Bus.publish(MyEvent, { ... })
})
nativeAddon.subscribe(dir, cb)
```

### Effect.Config Flags
```typescript
export const OPENCODE_EXPERIMENTAL_FILEWATCHER = Config.boolean("OPENCODE_EXPERIMENTAL_FILEWATCHER").pipe(
  Config.withDefault(false),
)
```
