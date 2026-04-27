# Fix a permit leak in `Effect.makeSemaphore`

You are working in the `Effect-TS/effect` monorepo (a TypeScript functional
programming library) at `/workspace/effect`. The semaphore primitive
exposed by `Effect.makeSemaphore(n)` has a race condition in which permits
can be permanently leaked.

## Symptom

Consider a semaphore created with `0` permits. A fiber calls `sem.take(1)`
and is added to the wait queue. Another fiber then calls `sem.release(1)`,
which schedules the waiter to be resumed with the granted permit.

If the waiter is **interrupted in the small window between being granted
the permit and actually consuming it**, the granted permit is lost: the
semaphore's internal `taken` counter remains incremented as if the permit
were in use, but no fiber actually holds it. Subsequent calls to
`sem.withPermitsIfAvailable(1)`, `sem.take(1)`, etc. observe `free === 0`
forever (until something matching `release` is called for the leaked
permits).

You can reproduce the leak deterministically with
`effect/Scheduler.ControlledScheduler`:

1. `sem = Effect.makeSemaphore(0)`
2. fork `sem.take(1)` against a `ControlledScheduler`
3. `sem.release(1)` against the same scheduler — the waiter is now resumable
4. `waiter.unsafeInterruptAsFork(FiberId.none)` and `scheduler.step()`
5. `sem.withPermitsIfAvailable(1)(Effect.void)` should return `Option.some(...)`
   because the permit released in step 3 was never actually consumed by the
   interrupted fiber. **On the broken implementation this returns
   `Option.none`**, demonstrating the leak.

## Expected behaviour

The expected contract is:

- A permit that has been granted to a waiter but **not yet consumed** must
  be returned to the available pool if that waiter is interrupted.
- `sem.withPermitsIfAvailable(1)(Effect.void)` after the interruption-and-
  release sequence above must return `Option.some(...)`.
- All existing semaphore behaviour (`sem.take`, `sem.release`,
  `sem.releaseAll`, `sem.resize`, `sem.withPermits`, `sem.withPermitsIfAvailable`)
  must keep working as before. The existing tests in
  `packages/effect/test/Effect/semaphore.test.ts` (`semaphore works`,
  `releaseAll`, `resize`) must continue to pass.

## Where to look

The semaphore implementation lives in the internal effect module. Search
the `packages/effect/src/internal/` tree for the `Semaphore` class — its
`take` method is the only place where granted permits are accounted for,
and it is the only place that needs to change. The fix should keep the
public `Semaphore` API surface unchanged.

## Code Style Requirements

This repository's `AGENTS.md` enforces several conventions you must follow:

- **Changesets**: every PR/change must include a markdown changeset file
  in the `.changeset/` directory describing the fix. The file's
  frontmatter must declare `"effect": patch` and the body should briefly
  describe the bug being fixed (e.g. mention "semaphore", "permit", or
  "leak").
- **Avoid comments**: the codebase prefers code without explanatory `//`
  line comments inside function bodies. Do not add narrative `//` comments
  inside the modified `take` method.
- **Conciseness**: keep the change minimal — only modify what is required
  to fix the leak.

## Verifying

Your fix is verified by running the package's vitest suite against the
modified file plus a deterministic regression test that exercises the
interruption race using `Scheduler.ControlledScheduler`. From
`packages/effect/`:

```
pnpm exec vitest run test/Effect/semaphore.test.ts
```

The repo uses `pnpm@10.17.1` and Node.js 23.7.0; dependencies are already
installed at `/workspace/effect`.
