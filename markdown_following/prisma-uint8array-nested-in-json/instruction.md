# Nested `Uint8Array` values in `Json` fields lose their base64 encoding

## Bug

When the Prisma client parameterizes a query argument bound to a `Json` field, the JSON encoding step uses JavaScript's native `JSON.stringify`. Because `JSON.stringify` cannot natively serialize typed arrays, any `Uint8Array` reachable only through property or index lookup inside the `Json` value is encoded as a numeric-keyed object (e.g. `{"0":72,"1":101,"2":108,"3":108,"4":111}`) instead of a base64 string.

A top-level `Uint8Array` argument (when the field is bound directly to a `Uint8Array`, not nested inside an object/array) is unaffected: it is correctly converted to base64 by an earlier value-classification step. The bug appears only when the typed array is nested.

## Expected behaviour

After parameterization, the JSON-encoded placeholder value passed to the database layer must contain base64 strings everywhere the input contained a `Uint8Array`, regardless of how deeply nested the typed array is and regardless of whether the immediate container is an object or an array.

The encoding must be the standard, `padding`-included base64 representation of the underlying bytes. Examples (these are the encodings asserted by the regression tests):

| input bytes | base64 |
| --- | --- |
| `[72, 101, 108, 108, 111]` (ASCII codes for `"Hello"`) | `SGVsbG8=` |
| `[1, 2, 3]` | `AQID` |

Concrete cases the parameterizer must round-trip correctly when the input is supplied to a `Json` argument:

- Nested in an object — input `{ payload: new Uint8Array([72, 101, 108, 108, 111]), label: 'test' }` must serialize to `{"payload":"SGVsbG8=","label":"test"}`.
- Nested in an array — input `[new Uint8Array([72, 101, 108, 108, 111]), 'world']` must serialize to `["SGVsbG8=","world"]`.
- Deeply nested — input `{ outer: { inner: new Uint8Array([1, 2, 3]) } }` must serialize to `{"outer":{"inner":"AQID"}}`.

## Scope and constraints

- The change must preserve the parameterizer's existing behavior for every other type. Placeholder names, cache-key generation, scalar parameterization, list-scalar parameterization, tagged values (`DateTime`, `Decimal`, `Bytes`, `BigInt`), enum parameterization, and selection-set rendering must all be unchanged.
- Both the array-valued and object-valued `Json` argument paths must be fixed: the same input shape inside an array must produce the same base64 encoding as inside an object. The fix cannot be one-sided.
- No new dependencies are required. Consider whether the surrounding workspace already exposes a JSON-serialization helper that handles `JSON.stringify`-unsupported types (typed arrays, `BigInt`) the same way the rest of the runtime already serializes `Json` values for non-parameterized paths.

## Code Style Requirements

This repository's `AGENTS.md` (also surfaced as `CLAUDE.md`) is authoritative for style. The rules most likely to apply here:

- Use `kebab-case` for any new file names.
- Do not create barrel `index.ts` files; import from the source module directly.
- Use native JavaScript private members (`#field`) rather than the TypeScript `private` keyword on classes.
- Do not write inline comments that merely restate what the code does; reserve inline comments for explaining *why*.
- Keep changes ASCII unless the file already uses Unicode.

The fix is expected to be small. The repository already has a unit-test harness for the parameterizer; the regression tests for this issue exercise the `parameterizeQuery` entry point with a minimal `ParamGraph` that has a single `Json` scalar field, so the only behavior under test is the JSON-encoding step inside the parameterizer itself.
