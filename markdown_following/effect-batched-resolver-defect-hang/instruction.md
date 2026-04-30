# Batched RequestResolver defect leaves consumer fibers hanging

You are working in the [Effect-TS/effect](https://github.com/Effect-TS/effect)
monorepo, checked out at base commit `d4ed885bb94b45e315bd275a44a9e472ef6074f4`.
The repo lives at `/workspace/effect`.

## Bug

A `RequestResolver.makeBatched(...)` resolver that **dies with a defect**
(for example via `Effect.die(...)`) leaves every consumer of the batch
**hanging forever**. The request `Deferred`s belonging to entries in the
batch are never completed, so any fiber that issued an `Effect.request` and
is awaiting one of those deferreds blocks indefinitely.

### Reproduction

```ts
import { describe, it } from "@effect/vitest"
import { assertTrue } from "@effect/vitest/utils"
import * as Effect from "effect/Effect"
import * as Exit from "effect/Exit"
import * as Fiber from "effect/Fiber"
import * as Request from "effect/Request"
import * as RequestResolver from "effect/RequestResolver"

class GetValue extends Request.TaggedClass("GetValue")<string, never, { readonly id: number }> {}

it.live("resolver defect should not hang consumer", () =>
  Effect.gen(function*() {
    const resolver = RequestResolver.makeBatched(
      (_requests: Array<GetValue>) => Effect.die("boom")
    )

    const fiber = yield* Effect.request(new GetValue({ id: 1 }), resolver).pipe(Effect.fork)

    yield* Effect.sleep("500 millis")
    const poll = yield* Fiber.poll(fiber)

    // BUG: poll._tag is "None" forever — fiber is stuck on deferredAwait.
    // Expected: poll._tag === "Some" and Exit.isFailure(poll.value).
    assertTrue(poll._tag === "Some")
    if (poll._tag === "Some") {
      assertTrue(Exit.isFailure(poll.value))
    }
  })
)
```

The same hang occurs when several requests share a single defective batched
resolver via `Effect.forEach(..., { batching: true, concurrency: "unbounded" })`.

## Required behavior

After your fix:

- A consumer of a batched-resolver request whose batch effect dies with a
  defect must reach a completed state. Polling the consumer fiber (after
  giving it a brief tick of live-clock time) must return `Some(exit)` where
  `Exit.isFailure(exit) === true`. **It must not return `None`.**
- This must hold both for a single consumer and for multiple consumers
  batched together via `Effect.forEach(..., { batching: true })`.
- Existing happy-path behavior of batched resolvers must not regress:
  successful resolver runs must still complete request entries normally
  (the existing `packages/effect/test/Effect/query.test.ts` and
  `packages/effect/test/Effect/query-repro.test.ts` suites must continue
  to pass).
- The whole `effect` package must still type-check (`pnpm check`).

## Where to look

The bug is in the runtime support for batched request resolvers — the
machinery the `effect` package uses to fork a resolver, drive a batch of
request entries, and finally settle each entry's `Deferred` so consumers
can wake up. The relevant code lives somewhere under
`packages/effect/src/internal/`; you will need to localize it yourself.
Useful starting points: `RequestResolver.makeBatched`, and how the
runtime cleans up request entries that the resolver did not complete.

## Project conventions

This repo has an `AGENTS.md` at the root. Read it. In particular:

- Use **pnpm** (not npm, yarn, or bun) for everything.
- Run `pnpm lint-fix` after editing files.
- Run `pnpm test run <file>` to execute a specific test file (vitest).
- Run `pnpm check` to type-check.
- All pull-request-style changes must include a **changeset** under
  `.changeset/` (a new markdown file naming the affected packages and
  describing the fix).
- Avoid adding comments that merely restate what the code does. JSDoc
  is fine.
- `index.ts` barrel files are auto-generated — do not edit them by hand.
- If you add tests, use the `@effect/vitest` `it.effect` / `it.live`
  pattern and `assert*` helpers from `@effect/vitest/utils` (not vitest's
  `expect`).
- If you write throwaway code for debugging, put it in `scratchpad/` and
  delete it before you finish.

## Code Style Requirements

The verifier runs `pnpm check` (TypeScript compilation) on the `effect`
package. Your fix must compile cleanly with no new TS errors. Prefer
matching the surrounding code style — if you are unsure, run
`pnpm lint-fix` after editing.
