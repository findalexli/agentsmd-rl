# Fix Schema.omit on Struct with optionalWith and index signatures

When `Schema.omit("key")` is called on a `Schema.Struct` that uses both
`Schema.optionalWith` (with options that wrap the property in a
Transformation AST node, such as `{ default: () => value }` or
`{ as: "Option" }`) and an index signature via `Schema.Record`, the
resulting schema has the wrong structure.

## Symptoms

The returned schema is a Transformation wrapping property signatures,
instead of a TypeLiteral with index signatures. This means the omitted
schema silently loses its index signature behavior — it behaves as
though the `Schema.Record` argument was never provided.

To see the problem, compare the AST of these two expressions:

```typescript
const schema = S.Struct(
  { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
  S.Record({ key: S.String, value: S.Boolean })
)
schema.pipe(S.omit("a")).ast

const plain = S.Struct(
  { a: S.String, b: S.Number },
  S.Record({ key: S.String, value: S.Boolean })
)
plain.pipe(S.omit("a")).ast
```

The first AST should match the second but does not: omit takes the wrong
internal code path because index signature detection does not follow
through Transformation AST nodes to reach the underlying TypeLiteral.

## What to fix

Fix the root cause so that `Schema.omit` returns the correct AST shape
(TypeLiteral with index signatures) when the struct is built with
`optionalWith` and `Schema.Record` together.

The internal function responsible for detecting index signatures must
handle the Transformation AST node type by continuing to inspect the
underlying ("to") AST, consistent with how other internal functions
(`getPropertyKeys`, `getPropertyKeyIndexedAccess`) already handle
Transformation.

## Verification

- `Schema.omit` on a struct with `optionalWith({ default: () => <value> })`
  and `Schema.Record` must produce the same AST as omitting from an
  equivalent plain struct (one using the unwrapped property type without
  `optionalWith`).
- This must work when omitting any field, not just the optional one.
- Existing tests in `omit.test.ts` must still pass.

## Code Style Requirements

- Run `pnpm lint-fix` after editing files to format code automatically.
- Follow the existing pattern of adjacent switch cases — no extra comments
  or abstractions beyond what the surrounding code uses.
