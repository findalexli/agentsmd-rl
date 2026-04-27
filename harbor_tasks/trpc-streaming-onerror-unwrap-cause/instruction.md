# tRPC: streaming server-side `onError` reports empty error messages

You are working in a clone of the [`trpc/trpc`](https://github.com/trpc/trpc) monorepo at `/workspace/trpc` (checked out at a specific base commit). Your task is to find and fix a bug in the server-side error-handling code path for **streaming responses**.

## Symptom

When a `query` (or any procedure) returns an **async iterable** (a generator) and that iterable later throws, the server-side `onError` callback configured on the HTTP adapter receives a `TRPCError` whose `.message` is the empty string `""`, instead of the original error's message.

Concretely, given a router like:

```ts
const t = initTRPC.create();

const router = t.router({
  failingIterable: t.procedure.query(async function* () {
    yield 1;
    throw new Error('stream broke');
  }),
});
```

…and the standard test harness `testServerAndClientResource(router)` (which uses an HTTP-streaming link by default), if a client iterates `failingIterable` and the iterable throws, the server's `onError` callback observes:

```ts
const serverErrorOpts = ctx.onErrorSpy.mock.calls[0]![0];
serverErrorOpts.error.message       // === ""             (BUG)
serverErrorOpts.error.cause         // === undefined or wrong wrapper
serverErrorOpts.error.cause.message // === "" or undefined
```

…whereas the **expected** behavior is:

```ts
serverErrorOpts.error                  // instanceof TRPCError
serverErrorOpts.error.message          // === 'stream broke'
serverErrorOpts.error.cause            // instanceof Error
serverErrorOpts.error.cause.message    // === 'stream broke'
```

The same bug surfaces for **streaming output-validation failures**: when an async-iterable procedure's output validator rejects a yielded value, the `serverError.message` observed by `onError` is `""` instead of a descriptive validation message.

The non-streaming `formatError` callback in the same area of the code already handles errors correctly — only the streaming `onError` path is broken. Look at how `formatError` is wired up and contrast it with the streaming `onError` callback.

## What to fix

Adjust the server's HTTP response code so that when an async iterable produced by a procedure throws (or its output is invalid), the `TRPCError` constructed for the server-side `onError` callback preserves:

1. The `message` of the underlying thrown `Error`.
2. A `.cause` that is an instance of `Error` whose `.message` matches.

Your fix must keep the existing non-streaming behavior unchanged, and must keep the existing public TypeScript types of all exported APIs unchanged.

## Acceptance criteria

A focused regression test (`packages/tests/server/_regression_streaming_onerror.test.ts`, written by the test harness) reproduces the streaming flow with `await using ctx = testServerAndClientResource(router)` and asserts:

- `error.message === 'stream broke'` on the client side
- `ctx.onErrorSpy.mock.calls.length === 1`
- The first call's `error` is an instance of `TRPCError`
- The first call's `error.message === 'stream broke'`
- The first call's `error.cause` is an instance of `Error` with `.message === 'stream broke'`

In addition, all of the following must remain green:

- The existing test file `packages/tests/server/errors.test.ts` (every test).
- The existing test file `packages/tests/server/TRPCError.test.ts`.
- `npx tsc --noEmit` inside `packages/server` (the server package must still type-check).

## Code Style Requirements

This repository enforces several rules from `.cursor/rules/coding-guidelines.mdc`. When editing TypeScript:

- Use `import type` for type-only imports (`@typescript-eslint/consistent-type-imports`).
- No non-null assertions (`!`) — prefer optional chaining or proper guards.
- No `console.log` calls inside `packages/*/src` (`no-console: error`).
- Prefer direct property access over destructuring for variables used only once or twice.
- Do **not** destructure inside function parameter declarations.
- Avoid sparse array destructuring.

Follow the repo's TypeScript style. Keep the change minimal and behavior-preserving.

## Test runner

Tests are executed with **vitest** at the repo root via `pnpm test -- --watch false <path>`. Use `pnpm` (never npm or yarn). The repo uses Node 24 and pnpm 9.12.2.
