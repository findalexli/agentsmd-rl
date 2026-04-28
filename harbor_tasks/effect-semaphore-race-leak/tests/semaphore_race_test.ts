import { assert, describe, it } from "@effect/vitest"
import * as Effect from "effect/Effect"
import * as FiberId from "effect/FiberId"
import * as Option from "effect/Option"
import * as Scheduler from "effect/Scheduler"

describe("Semaphore Race", () => {
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
