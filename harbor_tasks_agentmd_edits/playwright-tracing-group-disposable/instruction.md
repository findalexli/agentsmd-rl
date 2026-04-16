## Task: Make Tracing.group() return Disposable and update CLAUDE.md

The `Tracing.group()` method in `packages/playwright-core/src/client/tracing.ts` currently returns `Promise<void>`. This method should be updated to return a `Disposable` that automatically calls `groupEnd()` when disposed, enabling the `await using` pattern for automatic cleanup.

### Code Changes Required

1. **Modify `packages/playwright-core/src/client/tracing.ts`:**
   - Import `DisposableStub` from `./disposable`
   - Make the `group()` method return `new DisposableStub(() => this.groupEnd())`

2. **Update type definitions:**
   - `packages/playwright-core/types/types.d.ts` - Change return type to `Promise<Disposable>`
   - `packages/playwright-client/types/types.d.ts` - Change return type to `Promise<Disposable>`

3. **Update API documentation:**
   - `docs/src/api/class-tracing.md` - Add `- returns: <[Disposable]>` to the group method documentation

### Config Update Required

The project uses `CLAUDE.md` as the agent instruction file. You must update it to include a pre-commit lint requirement:

- In the `## Commit Convention` section of `CLAUDE.md`, add a line stating that linting must be run before committing.

This follows the existing pattern in CLAUDE.md where development workflow instructions are documented alongside code conventions.

### Key Files

- `packages/playwright-core/src/client/tracing.ts` - Main implementation
- `packages/playwright-core/src/client/disposable.ts` - Contains `DisposableStub` class
- `packages/playwright-core/types/types.d.ts` - Type definitions (core)
- `packages/playwright-client/types/types.d.ts` - Type definitions (client)
- `docs/src/api/class-tracing.md` - API documentation
- `CLAUDE.md` - Agent instructions (must be updated)

### Notes

- The `DisposableStub` class already exists and is used by other parts of the codebase (e.g., screencast)
- A `Disposable` has a `dispose()` method that returns `Promise<void>` and implements `[Symbol.asyncDispose]`
- The change enables usage like: `await using group = await context.tracing.group("name")`
