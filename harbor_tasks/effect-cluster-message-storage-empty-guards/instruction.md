# Task: Tighten `MessageStorage.makeEncoded` — guard empty id lists before delegation

You are working in the **`@effect/cluster`** package of the Effect-TS monorepo,
checked out under `/workspace/effect`. The relevant module is
`packages/cluster/src/MessageStorage.ts`.

## What is broken

`MessageStorage.makeEncoded(encoded)` adapts a low-level `Encoded` storage
implementation into the high-level `MessageStorage` service. Several of the
methods on the resulting service should treat an **empty input id list** as a
fast-path no-op — they must NOT call the underlying `encoded.*` method when
there is nothing to do, because some `encoded` SQL drivers cannot represent
an empty `IN ()` clause and would otherwise issue a malformed query.

Two such methods on the high-level service are currently **not** properly
guarded for empty inputs and forward straight to the encoded layer:

- `repliesForUnfiltered`
- `resetShards`

Concretely, when an empty array is passed to the high-level service:

- `storage.repliesForUnfiltered([])` should resolve to `[]` (an empty array of
  replies) **without** invoking `encoded.repliesForUnfiltered`.
- `storage.resetShards([])` should succeed as a no-op **without** invoking
  `encoded.resetShards`.

For non-empty inputs both methods must continue to delegate to the underlying
encoded layer with the (string-coerced) ids — no behavior change there.

## The contract this task expects

After your fix, the following must hold for `makeEncoded`:

1. **`repliesForUnfiltered`**
   - With an empty iterable: returns `Effect.succeed([])`, the encoded layer's
     `repliesForUnfiltered` is **never called**.
   - With a non-empty iterable: calls `encoded.repliesForUnfiltered(ids)` where
     `ids` is the input coerced to strings via `Array.from(ids, String)`.

2. **`resetShards`**
   - With an empty iterable: returns `Effect.void`, the encoded layer's
     `resetShards` is **never called**.
   - With a non-empty iterable: calls `encoded.resetShards(ids)` where `ids`
     is the input coerced to strings via
     `Array.from(shardIds, (id) => id.toString())`.

The existing guards already in `makeEncoded` for `repliesFor`,
`unprocessedMessages`, and `unprocessedMessagesById` (which currently use
`length === 0` style checks) should remain functionally equivalent — those
methods must continue to short-circuit on empty input and continue to delegate
on non-empty input.

The existing test file `packages/cluster/test/MessageStorage.test.ts` (and any
new tests there) must continue to pass.

## Constraints

- The package's existing public API surface for the high-level service should
  not change. In particular, callers may pass `[]`, `ReadonlyArray<string>`,
  `Iterable<string>`, etc. — your fix must not narrow the caller-facing input
  types of the high-level service in a way that breaks them.
- The underlying `Encoded` interface (the low-level driver-facing API) is
  *internal* to this module and may be tightened. In fact, consumers of this
  module (such as `packages/cluster/src/SqlMessageStorage.ts`) should be
  updated to match if you tighten that interface — the goal is to make
  accidental empty-id calls into the low-level layer impossible by
  construction.
- The module already imports a non-empty array helper from the `effect`
  library — use the established helper (the same one used by the surrounding
  code in this file) rather than adding a new ad-hoc check.

## Code Style Requirements

This repository enforces strict checks. Your change must pass:

- `pnpm check` (TypeScript build/type-check)
- `pnpm lint packages/cluster` (ESLint)

In addition, the repo's `AGENTS.md` requires:

- Run `pnpm lint-fix` after editing files to auto-format.
- Avoid adding comments unless they explain unusual logic; JSDoc on exported
  members is fine.
- Keep code concise — clarity over cleverness.
- Do not edit any auto-generated `index.ts` barrel files.

## How to validate locally

From `/workspace/effect/packages/cluster`:

```
pnpm vitest run test/MessageStorage.test.ts
pnpm check
```

From `/workspace/effect`:

```
pnpm lint packages/cluster
```

All three must succeed for your change to be considered correct.
