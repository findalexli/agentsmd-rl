# Fix a `Semaphore` race that leaks permits when a waiting fiber is interrupted

You are working in the [Effect-TS/effect](https://github.com/Effect-TS/effect) monorepo at `/workspace/effect`. The relevant package is `packages/effect` (the core `effect` library). The bug is somewhere in the internal semaphore implementation that backs `Effect.makeSemaphore`.

## Symptom

The `Semaphore` returned by `Effect.makeSemaphore` exposes a `take(n)` method that asynchronously waits until `n` permits are free, then claims them. When a fiber is currently blocked inside `take(n)` waiting for permits to become available, two things can happen, in order:

1. Another fiber calls `release(n)`, which schedules the waiter to be woken up.
2. The waiter is interrupted *before* it actually resumes and runs.

Today, this combination **leaks the permits**: the semaphore's internal `taken` counter is incremented as part of the wakeup path, but the interrupted fiber never gets a chance to register a finalizer that releases what it took. Subsequent calls to `withPermitsIfAvailable(n)` therefore see zero free permits and return `Option.none`, even though no fiber actually holds them.

A correct semaphore must satisfy the following invariant: **if a fiber waiting inside `take(n)` is interrupted, no permits are consumed.** A subsequent `withPermitsIfAvailable(n)` (with the same `n` that was just released) must observe the permits as available and return `Option.some(...)`.

## Reproducer

The following test (already placed in your workspace at `packages/effect/test/Effect/leak_regression.test.ts`) demonstrates the bug. It uses `Scheduler.ControlledScheduler` to deterministically interleave the release and the interrupt:

```ts
import { assert, describe, it } from "@effect/vitest"
import * as Effect from "effect/Effect"
import * as FiberId from "effect/FiberId"
import * as Option from "effect/Option"
import * as Scheduler from "effect/Scheduler"

describe("Semaphore regression", () => {
  it.effect("take interruption does not leak permits", () =>
    Effect.gen(function*() {
      const scheduler = new Scheduler.ControlledScheduler()
      const sem = yield* Effect.makeSemaphore(0)
      const waiter = yield* sem.take(1).pipe(
        Effect.withScheduler(scheduler),
        Effect.fork
      )

      yield* Effect.yieldNow()
      yield* sem.release(1).pipe(Effect.withScheduler(scheduler))
      assert.isNull(waiter.unsafePoll())

      scheduler.step()
      assert.isNull(waiter.unsafePoll())

      waiter.unsafeInterruptAsFork(FiberId.none)
      scheduler.step()

      const result = yield* sem.withPermitsIfAvailable(1)(Effect.void)
      assert.isTrue(Option.isSome(result))
    }))
})
```

On the unfixed code this test fails on the final assertion: `withPermitsIfAvailable(1)` returns `Option.none` because the interrupted waiter has already debited the permit count.

You can run it with:

```
cd /workspace/effect/packages/effect
pnpm exec vitest run --no-coverage test/Effect/leak_regression.test.ts
```

You may **not** edit `leak_regression.test.ts`; it is the regression contract.

## Task

Fix the bug so that the regression test passes and the existing tests in `packages/effect/test/Effect/semaphore.test.ts` (`semaphore works`, `releaseAll`, `resize`) continue to pass. You will need to make the permit-claim observable to interrupts: it must not be considered "taken" until the waiting fiber has actually been allowed to resume.

The fix lives entirely inside the core `effect` package's internal semaphore implementation. You do not need to change any public API.

## Code Style Requirements

Per the repository's `AGENTS.md`:

- The change must type-check: `pnpm exec tsc --noEmit -p tsconfig.src.json` (run from `packages/effect`) must succeed.
- The change must pass `pnpm lint` (eslint) without modifications from `lint-fix`.
- All PRs add a changeset under `.changeset/`. Add one short markdown file describing the fix as a `patch` to the `effect` package.
- Avoid comments unless absolutely required to explain unusual or complex logic.
- Do not edit any auto-generated `index.ts` barrel files.

## Verification

```
cd /workspace/effect/packages/effect
pnpm exec vitest run --no-coverage test/Effect/leak_regression.test.ts        # must pass
pnpm exec vitest run --no-coverage test/Effect/semaphore.test.ts              # must still pass
pnpm exec tsc --noEmit -p tsconfig.src.json                                   # must succeed
```
