# Make `Tracing.group()` Disposable

You are working in the Playwright monorepo at `/workspace/playwright`. The repo has been cloned at the appropriate base commit and dependencies are installed; the build artifacts under `packages/playwright-core/lib/` are also already produced for the unmodified source.

## Symptom

The `Tracing.group(name, options?)` API on the Playwright client currently resolves to `void`. There is no way to scope a group's lifetime: callers have to remember to call `tracing.groupEnd()` themselves, and they cannot use the modern explicit‑resource‑management pattern. In particular, this code does not compile and does not auto-close the group:

```ts
async function withGroup(tracing) {
  await using g = await tracing.group('outer');   // type error: void is not Disposable
  // ... do work; on scope exit, groupEnd() should run automatically ...
}
```

The same pattern is already used elsewhere in the Playwright client (e.g. screencasts and other resources), and a `DisposableStub` helper already exists in `packages/playwright-core/src/client/disposable.ts`. `DisposableStub` takes a single `() => Promise<void>` callback that is run on `dispose()`/`Symbol.asyncDispose`, with built-in idempotency.

## Required behavior after the fix

1. `await tracing.group(name, options?)` resolves to an object that:
   - has an async `dispose()` method, and
   - is usable with `await using` (i.e. it implements `Symbol.asyncDispose`).
2. Calling `dispose()` (whether directly or via `await using`) invokes the existing `groupEnd()` method **exactly once** even if `dispose()` is called multiple times.
3. The publicly generated TypeScript declaration files for the client must reflect the new return type — specifically, the `Tracing.group(...)` method signature in **both** of these generated files must end with `Promise<Disposable>` (not `Promise<void>`):
   - `packages/playwright-core/types/types.d.ts`
   - `packages/playwright-client/types/types.d.ts`
4. The pre-existing pre-condition behavior is unchanged: the underlying `tracingGroup` channel call must still happen (with the same `name` / `location` arguments), and `_additionalSources` must still be updated when `options.location` is provided. Only the return value changes.
5. The DEPS check (`node utils/check_deps.js`) and ESLint must continue to pass on any file you touch.

## Hints about the codebase (read these before editing)

- `packages/playwright-core/types/types.d.ts` and `packages/playwright-client/types/types.d.ts` are **generated** from the per-class API documentation under `docs/src/api/`. Hand-editing the generated `types.d.ts` files is not the right approach — they will be overwritten on the next build. Update the documentation source so the regenerated declarations are correct.
- The doc syntax for declaring a method's return type lives in `docs/src/api/`; look at how other methods in the same file declare return types (search for `- returns:`).
- The build pipeline that updates `lib/` and regenerates `types.d.ts` is `node utils/build/build.js --disable-install`. The grader runs this for you before tests, so you do not need to invoke it manually, but feel free to run it while iterating.

## What is being graded

Grading runs the build and then exercises the runtime behavior of the compiled client. The grader will:

- Construct a `Tracing` instance prototype with a mocked channel and call `group(...)` against it (no real browser needed).
- Verify the returned value has a callable `dispose()` and a `Symbol.asyncDispose` member.
- Verify that `dispose()` triggers exactly one `tracingGroupEnd` channel call, and that a second `dispose()` is a no-op.
- Verify `await using` semantics work end-to-end against the returned value.
- Inspect both generated `types.d.ts` files for the new return type.
- Re-run the repo's dependency boundary check and ESLint.

## Code Style Requirements

When iterating, run the repo's linters before considering the change complete. The grader runs `node utils/check_deps.js` and `npx eslint packages/playwright-core/src/client/tracing.ts` as part of testing; both must pass. Refer to `CLAUDE.md` in the repo root for the project's lint conventions.
