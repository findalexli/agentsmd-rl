# Stream.changes is emitting empty chunks downstream

You are working in the [Effect-TS/effect](https://github.com/Effect-TS/effect)
monorepo. Read `AGENTS.md` at the repo root for project conventions before
making changes.

## Symptom

`Stream.changes` (and the underlying `Stream.changesWith`) is intended to drop
consecutive duplicate elements from a stream. Internally it processes input
one chunk at a time, reducing each chunk to the elements that differ from the
previous "last seen" value, then writes the reduced chunk downstream.

When **every** element of an input chunk is filtered out as a duplicate, the
reduced chunk is `Chunk.empty`. The current implementation still writes that
empty chunk to the channel. Empty chunks should not be written downstream:
they add overhead to consumers, can break code that uses chunk boundaries
as a signal (e.g. `Stream.chunks` materialises them as zero-length chunks),
and are inconsistent with how the rest of the streaming primitives behave.

You can observe the bug like this:

```ts
import * as Chunk from "effect/Chunk"
import * as Effect from "effect/Effect"
import { pipe } from "effect/Function"
import * as Stream from "effect/Stream"

const program = pipe(
  Stream.fromChunks(Chunk.of(1), Chunk.make(1, 1), Chunk.of(2)),
  Stream.changes,
  Stream.chunks,
  Stream.runCollect
)

const chunks = Effect.runSync(program)
console.log(Array.from(chunks).map((c) => Array.from(c)))
// Current (buggy):  [[1], [], [2]]
// Expected:         [[1], [2]]
```

The middle chunk `Chunk.make(1, 1)` consists entirely of duplicates of the
previously-seen value `1`, so after deduplication it is empty — but it is
still written to the channel and shows up as `[]` in the materialised
chunks. The desired behaviour is for `Stream.changes` to skip writing
empty chunks entirely while still updating its internal "last seen"
tracking so later non-duplicate elements are emitted correctly.

## Expected behaviour

- For any input where one or more whole input chunks reduce to empty after
  deduplication, the downstream side of `Stream.changes` /
  `Stream.changesWith` must not observe any zero-length chunks.
- The flattened element sequence produced by `Stream.changes` must be
  unchanged — only the chunk-level shape of the output changes.
- The "last seen" element tracked across chunks must continue to advance
  through duplicate-only chunks so that, for example,
  `Stream.fromChunks(Chunk.of("a"), Chunk.make("A","a","A"), Chunk.of("b"))`
  piped through `Stream.changesWith` (with case-insensitive equality) still
  emits exactly `["a", "b"]`.
- The custom-equality variant `Stream.changesWith(f)` must behave the same
  way (the empty-chunk skip applies to it as well, since `changes` is just
  `changesWith(Equal.equals)`).

## Hints

The implementation of `Stream.changes` and `Stream.changesWith` is in the
`effect` package's internal stream module. Locate it by searching for the
`changesWith` export. It builds a recursive `writer` channel that reduces
each input chunk to the elements that differ from a tracked previous value
and writes the reduced chunk downstream. The bug is in that final write
step.

## Code Style Requirements

This task's checks include the repo's TypeScript typechecker (`pnpm check`,
which runs `tsc -b tsconfig.json` inside `packages/effect/`). Your patch
must type-check cleanly.

Per `AGENTS.md`:

- Keep the patch concise — clarity over cleverness.
- Do not add inline narrative comments.
- Do not hand-edit any `index.ts` barrel files (they are codegen-managed).
- Add a changeset under `.changeset/` describing the fix (the existing
  changesets in that directory are good templates — `effect: patch` is
  the right category here).

## Verification

Test the change with:

```bash
pnpm --filter effect exec vitest run test/Stream/changing.test.ts
pnpm --filter effect exec tsc -b tsconfig.json
```

Both must succeed. The first verifies the existing semantics of
`Stream.changes` are preserved; the second verifies the fix type-checks.
