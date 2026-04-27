# Schema.omit drops index signatures on Struct with `optionalWith` + `Record`

## Symptom

In the `effect` library's Schema module, `Schema.omit` produces a structurally
wrong result when applied to a `Struct` whose property block contains
`Schema.optionalWith` (with `{ default: ... }` or `{ as: "Option" }`) and whose
index signatures come from `Schema.Record`.

Concretely, given:

```ts
import * as S from "effect/Schema"

const schema = S.Struct(
  { a: S.String, b: S.optionalWith(S.Number, { default: () => 0 }) },
  S.Record({ key: S.String, value: S.Boolean })
)

const omitted = schema.pipe(S.omit("a")).ast
```

`omitted._tag` is currently `"Transformation"`, but it should be `"TypeLiteral"`,
and the resulting AST should expose the original index signatures.

The structurally-equivalent plain struct (no `optionalWith`):

```ts
const plain = S.Struct(
  { a: S.String, b: S.Number },
  S.Record({ key: S.String, value: S.Boolean })
)
```

…produces the correct `TypeLiteral` AST with index signatures when `S.omit("a")`
is applied. The two omit results SHOULD be deep-equal — but currently are not.

The same problem affects `optionalWith(..., { as: "Option" })` and any other
`optionalWith` variant that wraps the struct in a `Transformation` AST node.

## Expected behavior

For ANY of the `optionalWith` variants that produce a `Transformation` AST,
`Schema.omit` should:

1. Return an AST whose `_tag` is `"TypeLiteral"` (not `"Transformation"`).
2. Preserve the index signatures from the underlying `Record` — i.e. the
   resulting `TypeLiteral.indexSignatures` array length must equal what the
   plain-struct equivalent produces (one entry per `Record(...)` argument).
3. Be deep-equal to the AST that would be produced by `S.omit("a")` on the
   equivalent struct constructed without `optionalWith` (i.e. with the bare
   field type).

The pre-existing `omit` test on a plain struct without index signatures must
continue to pass, as must the sibling `pick` tests.

## Where to look

The bug is internal to the schema-AST machinery in
`packages/effect/src/`. The fix is small (the project is the `effect`
monorepo; the repository is already cloned at `/workspace/effect` and
dependencies are installed). Investigate how `Schema.omit` decides between
returning a `TypeLiteral` (index-signature path) and delegating to property
selection — the AST traversal helper that drives that decision needs to handle
all AST node variants that wrap an underlying type, not only some of them.

## Verification

You can run the project's tests with `pnpm test run <path>` from the repo
root. The existing tests in
`packages/effect/test/Schema/Schema/Struct/omit.test.ts` and
`packages/effect/test/Schema/Schema/Struct/pick.test.ts` must keep passing.
The fix must not break TypeScript compilation (`pnpm exec tsc --noEmit -p
packages/effect/tsconfig.src.json`).

## Code Style Requirements

The repository's contributor guidelines apply:

- Match the existing style of the surrounding code; avoid adding comments
  unless they explain non-obvious logic.
- Keep changes minimal — do not refactor unrelated code.
- The fix should be consistent with how related AST-traversal helpers in the
  same file handle the same situation (look for the existing handling of
  similar wrapper-style AST nodes elsewhere in `SchemaAST.ts`).
- TypeScript code must continue to typecheck cleanly.
