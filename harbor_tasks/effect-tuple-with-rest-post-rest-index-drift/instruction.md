# Fix `TupleWithRest` post-rest index drift in Effect's Schema decoder

You are working in the `Effect-TS/effect` monorepo. The Schema decoder in
`packages/effect/src/ParseResult.ts` mishandles tuples that have *both* a
rest element and a tail of fixed elements (the "post-rest" portion). When
the tail has more than one element, every position after the first is
either silently skipped or read from the wrong slot.

## Reproducer

Build a schema with a one-element head, a Boolean rest, and a three-element
tail of fixed types:

```ts
import * as S from "effect/Schema"
import * as Either from "effect/Either"

const schema = S.Tuple(
  [S.String],                 // head
  S.Boolean,                  // rest
  S.String, S.NumberFromString, S.NumberFromString  // tail
)
```

Then decode two inputs:

```ts
S.decodeUnknownEither(schema)(["a", true, "b", "1", "x"])
S.decodeUnknownEither(schema)(["a", true, "b", "1", "2"])
```

### Observed behavior (buggy)

Both calls return `Right` with the four-element output `["a", true, "b", 1]`:
the trailing element (whether the invalid `"x"` or the valid `"2"`) is
dropped without comment and never validated.

### Expected behavior

* `["a", true, "b", "1", "x"]` must produce a `Left` whose `ParseError`
  localises to index `[4]` and mentions the offending value `"x"`. The
  rendered message tree should look like:

  ```
  readonly [string, ...boolean[], string, NumberFromString, NumberFromString]
  └─ [4]
     └─ NumberFromString
        └─ Transformation process failure
           └─ Unable to decode "x" into a number
  ```

* `["a", true, "b", "1", "2"]` must produce a `Right` whose value contains
  every post-rest element: `["a", true, "b", 1, 2]`.

The same drift is observable for any other tuple shape with `tail.length ≥
2`. For a tuple `[NumberFromString] + ...String + [Number, Number, Number]`
decoding `["1", "a", "b", "2", "3", "4"]` must succeed and yield
`[1, "a", "b", 2, 3, 4]`; replacing the final `"4"` with `"z"` must fail
at index `[5]`.

## Where to look

The parser under `packages/effect/src/ParseResult.ts` builds element
parsers for tuples. Inside the per-tuple `Parser` that handles the
post-rest tail, each tail position must be validated against its own
absolute index inside `input`, not against an index that accumulates as
the loop iterates. Find that loop and make it check every tail position
sequentially and independently.

## What to deliver

* A behavioural fix in `packages/effect/src/ParseResult.ts` that makes the
  expected behaviours above hold for all tuple shapes with a rest element
  and a multi-element tail.
* A regression test in
  `packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts` covering at
  least the failing-decode case at index `[4]` and the all-valid case
  that must yield the full five-element output. Follow the existing
  patterns in that file (e.g. `Util.assertions.decoding.fail` /
  `Util.assertions.decoding.succeed`).
* A changeset file under `.changeset/` (any descriptive filename) marking
  this as a `patch` for the `effect` package, with a one-line summary.

## Code Style Requirements

The repository's automated checks must pass:

* `pnpm check` — TypeScript compiles cleanly (`tsc -b tsconfig.json` for
  the `effect` package).
* `pnpm vitest run packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts`
  — all tuple tests pass, including any regression test you add.
* Avoid adding comments unless the logic genuinely demands one; favour
  clarity over cleverness; keep wording concise (per `AGENTS.md`).

The repo is checked out at `/workspace/effect`. Use `pnpm` (already
installed) for any tooling. A `scratchpad/` directory is the conventional
place for ad-hoc verification scripts.
