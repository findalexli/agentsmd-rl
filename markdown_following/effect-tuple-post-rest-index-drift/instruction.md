# Fix post-rest tuple validation in `effect`

The `effect` schema parser in the `effect` package incorrectly validates the
**post-rest** elements of a tuple-with-rest schema. When a `Schema.Tuple` is
built with a leading rest element followed by two or more trailing tail
elements (`Schema.Tuple([head...], rest, tail0, tail1, ...)`), the parser
silently skips or misreports failures for some tail positions.

## Reproduction

Build a schema with a head, a rest element, and four trailing positions:

```ts
import * as S from "effect/Schema"

const schema = S.Tuple(
  [S.String],
  S.Boolean,
  S.String,
  S.NumberFromString,
  S.NumberFromString,
)
```

Now decode an input where the **last** element is not a valid number:

```ts
S.decodeUnknownEither(schema)(["a", true, "b", "1", "x"])
```

### Expected

The decode produces a `Left` whose error path is `[4]`, with a
`NumberFromString` / "Unable to decode" message, because `"x"` at index 4
cannot be transformed to a number.

### Actual (current behavior)

Depending on the schema shape, the parser either:

- skips validating the trailing tail position entirely (silently producing a
  `Right` for inputs that should be rejected), or
- reports the failure at the wrong index because the loop variable used to
  read the input element drifts away from the index expected by the
  caller-visible error path.

The same drift affects schemas with longer tails (e.g. tails of length 3 or
4): some post-rest positions are validated against the wrong input slot or
not validated at all.

## What you need to do

Make the post-rest validation correct: every tail position `j` must be
validated against the input element at the index `head.length + (rest_len) + j`
where `rest_len` is the number of input elements consumed by the rest
matcher, and any error pointer the parser produces must reference that same
index. Once fixed, decoding behaves as follows:

| Input to the schema above                       | Expected outcome                       |
|-------------------------------------------------|----------------------------------------|
| `["a", true, "b", "1", "x"]`                    | `Left`, error at `[4]`, NumberFromString failure |
| `["a", true, "b", "1", "2"]`                    | `Right` equal to `["a", true, "b", 1, 2]` |
| `["a", true, "b", "y", "2"]`                    | `Left`, error at `[3]`                  |
| `["a", true, 9, "1", "2"]`                      | `Left`, error at `[2]`                  |

The same correctness must hold for tuples with more rest matches and longer
tails:

| Input to `Tuple([], Number, String, String, String, NumberFromString)` | Expected outcome                       |
|------------------------------------------------------------------------|----------------------------------------|
| `[1, 2, 3, "x", "y", "z", "nope"]`                                    | `Left`, error at `[6]`, NumberFromString failure |
| `[1, 2, 3, "x", "y", "z", "42"]`                                       | `Right` equal to `[1, 2, 3, "x", "y", "z", 42]` |
| `[1, 2, 3, "x", "y", 7, "42"]`                                         | `Left`, error at `[5]`                  |

## Constraints

- Do **not** change the public API of `effect/Schema` or `effect/ParseResult`.
  The fix should be confined to the existing post-rest validation loop in
  the parser implementation.
- The repo's existing vitest suites for `Tuple` and `ParseResult` must
  continue to pass after your change.
- Follow the project's style guidelines from `AGENTS.md`: prefer clear,
  conventional code over clever tricks, and avoid adding new comments unless
  they explain something genuinely unusual.
- Add a changeset entry under `.changeset/` (a small markdown file with the
  `"effect": patch` frontmatter line and a one-sentence summary of the fix),
  as required for all PRs against this repo.
