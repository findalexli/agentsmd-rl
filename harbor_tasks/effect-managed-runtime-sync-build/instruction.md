# build ManagedRuntime synchronously if possible

You are working in the [`Effect-TS/effect`](https://github.com/Effect-TS/effect) monorepo (a TypeScript functional-programming library). The repository is checked out at `/workspace/effect` on commit `dd4cf4b119592e670ad9347091bdec8a9c6c3422`. `pnpm` is preinstalled and `pnpm install` has already been run.

## The bug

`ManagedRuntime` is meant to let callers run effects against a pre-configured runtime. When the wrapped `Layer` is *synchronously* buildable (for example `Layer.empty` or `Layer.succeed(tag, value)`), the runtime should also become available *synchronously* — i.e. immediately after the first call that triggers a build.

Today this isn't the case. The build is always deferred to async fiber processing, even when the layer doesn't require any async work. As a consequence the following sequence (which a user would reasonably expect to work for a synchronous layer) crashes:

```ts
import { Effect, Layer, ManagedRuntime } from "effect"

const runtime = ManagedRuntime.make(Layer.empty)
runtime.runFork(Effect.void)   // kicks off the build
runtime.runSync(Effect.void)   // throws — the runtime hasn't been built yet
```

`runSync` aborts because the underlying build fiber has not finished yet — it has only been queued for asynchronous processing — so the `ManagedRuntime`'s cached `Runtime` is still `undefined` and the caller is forced to await asynchronously. Users have no way to run a synchronous effect through a `ManagedRuntime` without first awaiting the build, even when no asynchrony is logically required.

## Your task

Change the implementation so that, when the supplied `Layer` is synchronously buildable, the `ManagedRuntime`'s runtime is fully built and cached **before** the first triggering call returns. The motivating success criterion is:

```ts
const runtime = ManagedRuntime.make(Layer.empty)
runtime.runFork(Effect.void)
runtime.runSync(Effect.void)   // must succeed
```

More generally, after the first `runFork`/`runSync`/`runPromise` call on a `ManagedRuntime` whose layer requires no asynchronous step, the cached runtime should be observable immediately on the same tick. Layers that genuinely need async work must continue to function as before.

You may need to revisit how the build fiber is scheduled (so that its execution is synchronous when possible) and how the build fiber is awaited (so that an already-resolved fiber does not force callers onto the async path). All of `effect`'s public API and existing test suite must continue to behave identically.

## Repository conventions

This repo's `AGENTS.md` includes rules that apply to every PR. The most relevant for this task:

- **Add a changeset.** Every pull request must include a new file under `.changeset/` describing the change. Use the standard frontmatter format, e.g.:
  ```md
  ---
  "effect": patch
  ---

  build ManagedRuntime synchronously if possible
  ```
  Write one changeset per logical change. The changeset *body* is what ships in the changelog — keep it concise.
- **Conciseness over verbosity.** Both code and any prose you write should be short and to the point.
- **Reduce comments.** Don't add comments unless they explain genuinely unusual or complex logic.
- **Follow existing patterns.** Look at neighbouring code for style and naming before introducing new constructs.
- **Don't hand-edit barrel files.** `index.ts` files in this repo are generated; if you find yourself editing one, you're going about it the wrong way.

## Verifying your work

Vitest is available via `pnpm`. The relevant suite for this change is:

```
pnpm --filter effect vitest run test/ManagedRuntime.test.ts
```

It must continue to pass. The behaviour described above must also work for both `Layer.empty` and `Layer.succeed(...)` — varying the inner layer should not change the outcome.
