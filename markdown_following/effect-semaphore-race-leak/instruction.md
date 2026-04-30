# Fix Semaphore Race Condition

## Problem

The `Semaphore.take()` operation has a race condition where permits can be "leaked" — the internal `taken` counter is incremented but the calling fiber never actually receives the permit. This happens when a fiber waiting on `take()` is interrupted after a permit becomes available but before the fiber's continuation executes.

**Observable symptom**: After interrupting a fiber that was blocked on `sem.take(1)`, a subsequent `sem.withPermitsIfAvailable(1)` returns `None` (indicating no permits available) even though a permit was released and the interrupted fiber never consumed it. The permit is lost — `this.taken` was incremented but the fiber was interrupted before it could complete.

## How to Reproduce

Use `Scheduler.ControlledScheduler` from `effect/Scheduler` to deterministically control execution order:

1. Create a semaphore with 0 initial permits via `Effect.makeSemaphore(0)`
2. Fork a `sem.take(1)` using `Effect.withScheduler(scheduler)` to run on the controlled scheduler
3. Yield execution with `Effect.yieldNow()`
4. Release 1 permit via `sem.release(1).pipe(Effect.withScheduler(scheduler))` — this triggers the waiter's observer, but the controlled scheduler prevents the waiter from immediately resuming
5. Step the scheduler with `scheduler.step()` — the observer fires and the waiter should now have the permit
6. Interrupt the waiting fiber via `waiter.unsafeInterruptAsFork(FiberId.none)`
7. Step the scheduler again to process the interruption
8. Attempt to acquire a permit non-blockingly with `sem.withPermitsIfAvailable(1)(Effect.void)` — under correct behavior this returns `Some` (permit is available), but under the buggy behavior it returns `None` (permit was leaked)

## Expected Behavior

When a fiber blocked on `take()` is interrupted after a permit was released for it, the permit must remain available for other fibers. No permit should be silently consumed by an interrupted fiber. The test `"take interruption does not leak permits"` should pass — `withPermitsIfAvailable(1)` must return `Some` after the interruption.

## Code Style Requirements

- Run `pnpm lint-fix` after making changes to format code according to the project's style guidelines
- Use `pnpm test packages/effect/test/Effect/semaphore_race.test.ts` to verify the fix

## Existing Tests

All existing semaphore tests in `packages/effect/test/Effect/semaphore.test.ts` must continue to pass. Run them with `pnpm test packages/effect/test/Effect/semaphore.test.ts`.
